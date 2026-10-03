"""Local, persistent moment review. Python standard library + FFmpeg only."""
import argparse
from copy import deepcopy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import threading
from urllib.parse import urlsplit
import uuid
import webbrowser

from vod import export_events, number, probe, read
from review_timeline import build_review

SCHEMA = 'vod-review-queue/v1'
DECISIONS = ('unreviewed', 'keep', 'later', 'skip')
ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'review-queue'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temp.open('w', encoding='utf-8', newline='\n') as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def identity(source):
    path = Path(source['path']).resolve(strict=True)
    stat = path.stat()
    return dict(path=str(path), size=stat.st_size, mtime_ns=stat.st_mtime_ns)


def selected_xml(data, plan, probes, decisions, mode='keep'):
    if mode not in ('keep', 'all'):
        raise ValueError('Unknown export mode')
    selected = {e['id'] for e in data['events']
                if mode == 'all' or decisions[e['id']]['decision'] == 'keep'}
    if not selected:
        raise ValueError('Keep at least one moment before exporting your selection.')
    # Resolve relationships before filtering: an earlier, unselected event can
    # remain a useful source-time reference without becoming a selected marker.
    markers = export_events(data)
    for source in markers['sources']:
        source['markers'] = [m for m in source['markers'] if m['key'] in selected]
    markers['sources'] = [s for s in markers['sources'] if s['markers'] or s['id'] in plan['main_sources']]
    present = {s['id'] for s in markers['sources']}
    for source in data['sources']:
        if source['id'] in plan['main_sources'] and source['id'] not in present:
            markers['sources'].append(dict(source, markers=[]))
    filtered = deepcopy(plan)
    filtered['title'] = plan['title'] + (' - Kept moments' if mode == 'keep' else ' - All moments')
    filtered['alternates'] = [a for a in plan.get('alternates', []) if a['event_id'] in selected]
    filtered['coverage_note'] = (plan.get('coverage_note', '') +
        '\nFull main chronology retained. Review choices filter markers and alternate excerpts only.')
    return build_review(markers, probes, filtered), sorted(selected)


def cards_for(data, plan, padding):
    number(padding, 'preview padding')
    sources = {s['id']: s for s in data['sources']}
    order = plan['main_sources'] + [s for s in sources if s not in plan['main_sources']]
    cards = []
    for event in data['events']:
        views = sorted(event['perspectives'], key=lambda v: order.index(v['source_id']))
        card = dict(id=event['id'], title=event['marker_title'], summary=event['marker_summary'],
                    check=event.get('review_note', ''), related=event.get('related_events', []), views=[])
        for view in views:
            source = sources[view['source_id']]
            start = max(0, view['start_sec'] - padding)
            end = min(source['duration_sec'], view['end_sec'] + padding)
            card['views'].append(dict(source_id=source['id'], label=source.get('label', source['id']),
                title=view.get('marker_title', event['marker_title']),
                summary=view.get('marker_summary', event['marker_summary']), role=view.get('marker_role', view['role']),
                start_sec=view['start_sec'], end_sec=view['end_sec'], preview_start_sec=start,
                preview_end_sec=end, uncertainty_sec=view['uncertainty_sec'], alignment=view['alignment']))
        cards.append(card)
    # Main chronology first, then independent secondary moments in their own
    # source order. Never imply a common clock by interleaving unsynced POVs.
    return sorted(cards, key=lambda c: (order.index(c['views'][0]['source_id']), c['views'][0]['start_sec'], c['id']))


def initialize(events_path, plan_path, out, padding=3):
    out = Path(out).resolve()
    data, plan = read(events_path), read(plan_path)
    export_events(data)
    if not data['events']:
        raise ValueError('No moments to review')
    event_map = {e['id']: e for e in data['events']}
    for alt in plan.get('alternates', []):
        event = event_map.get(alt.get('event_id'))
        if not event or not {alt['source_id'], alt['main_source_id']} <= {v['source_id'] for v in event['perspectives']}:
            raise ValueError('Every alternate needs an event_id with both referenced perspectives')
    probes, identities = {}, {}
    for source in data['sources']:
        identities[source['id']] = identity(source)
        metadata, duration = probe(Path(source['path']))
        if abs(duration - source['duration_sec']) > .1:
            raise ValueError('Media duration changed; review source mapping')
        probes[source['id']] = metadata
    cards = cards_for(data, plan, padding)
    decisions = {c['id']: dict(decision='unreviewed', note='', view=0, positions={}) for c in cards}
    selected_xml(data, plan, probes, decisions, 'all')  # Validate exporter/layout before rendering.
    out.mkdir(parents=True, exist_ok=False)
    (out / 'previews').mkdir()
    atomic_json(out / 'events.json', data)
    atomic_json(out / 'plan.json', plan)
    atomic_json(out / 'probes.json', probes)
    sources = {s['id']: s for s in data['sources']}
    for i, card in enumerate(cards):
        for j, view in enumerate(card['views']):
            name = f'{i:04d}-{j:02d}.mp4'
            dest = out / 'previews' / name
            source = sources[view['source_id']]
            video = next(s for s in probes[source['id']]['streams'] if s['codec_type'] == 'video')
            audio = [s for s in probes[source['id']]['streams'] if s['codec_type'] == 'audio']
            command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
                '-ss', str(view['preview_start_sec']), '-i', source['path'],
                '-t', str(view['preview_end_sec'] - view['preview_start_sec']), '-map', f"0:{video['index']}"]
            if audio:
                command += ['-map', f"0:{audio[0]['index']}", '-c:a', 'aac', '-b:a', '128k']
            else:
                command += ['-an']
            command += ['-vf', 'scale=960:-2,fps=24', '-c:v', 'libx264', '-preset', 'veryfast',
                        '-crf', '25', '-pix_fmt', 'yuv420p', '-threads', '2', '-movflags', '+faststart', str(dest)]
            subprocess.run(command, check=True, capture_output=True)
            _, duration = probe(dest)
            expected = view['preview_end_sec'] - view['preview_start_sec']
            if abs(duration - expected) > .25:
                raise ValueError(f'Preview duration differs from requested source interval: {name}')
            view['file'] = name
        print(f"Prepared {i + 1}/{len(cards)}: {card['title']}", flush=True)
    # Publish only after every preview succeeds. A failed build is never served.
    manifest = dict(schema=SCHEMA, title='Moment review', cards=cards, identities=identities,
        coverage=plan.get('coverage_note', 'Review coverage not supplied.'),
        snapshots={n: file_hash(out / n) for n in ('events.json', 'plan.json', 'probes.json')},
        inputs=[dict(path=str(Path(p).resolve()), sha256=file_hash(p)) for p in (events_path, plan_path)])
    atomic_json(out / 'queue.json', manifest)
    atomic_json(out / 'state.json', dict(schema=SCHEMA, queue_hash=digest(manifest), revision=0,
        current_id=cards[0]['id'], decisions=decisions, history=[]))
    return out


class Conflict(ValueError):
    pass


class Store:
    def __init__(self, folder):
        self.folder = Path(folder).resolve(strict=True)
        self.queue = read(self.folder / 'queue.json')
        if self.queue['schema'] != SCHEMA:
            raise ValueError('Unknown queue schema')
        self.lock = threading.RLock()
        self.cards = {c['id']: c for c in self.queue['cards']}
        self.playback_plan = read(self.folder / 'plan.json')
        self.validate_inputs()
        self.state()

    def validate_inputs(self):
        for name, expected in self.queue['snapshots'].items():
            if name not in ('events.json', 'plan.json', 'probes.json') or file_hash(self.folder / name) != expected:
                raise ValueError('Queue snapshot changed. Preserve this queue and create a new one.')
        for item in self.queue['inputs']:
            if file_hash(item['path']) != item['sha256']:
                raise ValueError('Discovery inputs changed. Preserve choices; build a new queue for revised discoveries.')
        for source in read(self.folder / 'events.json')['sources']:
            if identity(source) != self.queue['identities'][source['id']]:
                raise ValueError('Source media changed. Review mapping before exporting.')

    def state(self):
        state = read(self.folder / 'state.json')
        if state['schema'] != SCHEMA or state['queue_hash'] != digest(self.queue) or set(state['decisions']) != set(self.cards):
            raise ValueError('Decisions belong to a different queue')
        if state['current_id'] not in self.cards or type(state['revision']) is not int or state['revision'] < 0:
            raise ValueError('Invalid review state')
        for eid, item in state['decisions'].items():
            if item['decision'] not in DECISIONS or not isinstance(item['note'], str):
                raise ValueError('Invalid saved choice')
            if type(item['view']) is not int or not 0 <= item['view'] < len(self.cards[eid]['views']):
                raise ValueError('Invalid saved view')
            for key, position in item['positions'].items():
                if not key.isdecimal() or not 0 <= int(key) < len(self.cards[eid]['views']):
                    raise ValueError('Invalid saved playback view')
                view = self.cards[eid]['views'][int(key)]
                if number(position, 'saved position') > view['preview_end_sec'] - view['preview_start_sec'] + .25:
                    raise ValueError('Invalid saved playback position')
        return state

    def playback_queue(self):
        # Derive from the validated immutable plan; preserve manifest/state hashes.
        queue = deepcopy(self.queue)
        plan = self.playback_plan
        for card in queue['cards']:
            card['sync_links'] = [dict(
                main_source_id=a['main_source_id'], source_id=a['source_id'],
                offset_sec=a['source_anchor_sec'] - a['main_anchor_sec'],
                source_start_sec=a['source_start_sec'], source_end_sec=a['source_end_sec'],
                uncertainty_sec=a['uncertainty_sec'])
                for a in plan.get('alternates', []) if a['event_id'] == card['id']]
        return queue

    def mutate(self, patch, undo=False):
        with self.lock:
            state = self.state()
            if type(patch.get('revision')) is not int or patch['revision'] != state['revision']:
                raise Conflict('Another tab saved changes. Reload this page before continuing.')
            if undo:
                if state['history']:
                    entry = state['history'].pop()
                    state['decisions'][entry['id']]['decision'] = entry['decision']
                    state['current_id'] = entry['id']
            else:
                eid = patch.get('event_id')
                if eid not in self.cards:
                    raise ValueError('Unknown moment')
                item = state['decisions'][eid]
                decision = patch.get('decision', item['decision'])
                note = patch.get('note', item['note'])
                view = patch.get('view', item['view'])
                if decision not in DECISIONS or not isinstance(note, str) or len(note) > 4000:
                    raise ValueError('Invalid decision or note (maximum 4,000 characters)')
                if type(view) is not int or not 0 <= view < len(self.cards[eid]['views']):
                    raise ValueError('Unknown view')
                if decision != item['decision']:
                    state['history'].append(dict(id=eid, decision=item['decision']))
                item.update(decision=decision, note=note, view=view)
                if 'position_sec' in patch:
                    position = number(patch['position_sec'], 'playback position')
                    v = self.cards[eid]['views'][view]
                    if position > v['preview_end_sec'] - v['preview_start_sec'] + .25:
                        raise ValueError('Playback position outside preview')
                    item['positions'][str(view)] = position
                state['current_id'] = eid
            state['revision'] += 1
            atomic_json(self.folder / 'state.json', state)
            return state

    def export(self, patch):
        with self.lock:
            state = self.state()
            if patch.get('revision') != state['revision']:
                raise Conflict('Choices changed; reload before export.')
            self.validate_inputs()
            mode = patch.get('mode', 'keep')
            xml, selected = selected_xml(read(self.folder / 'events.json'), read(self.folder / 'plan.json'),
                                        read(self.folder / 'probes.json'), state['decisions'], mode)
            name = f'review-r{state["revision"]}-{uuid.uuid4().hex[:8]}'
            folder = self.folder / 'exports' / name
            folder.mkdir(parents=True)
            (folder / 'review.xml').write_text(xml, encoding='utf-8')
            atomic_json(folder / 'decisions.json', state)
            atomic_json(folder / 'selection.json', dict(mode=mode, selected_event_ids=selected,
                        queue_hash=state['queue_hash'], revision=state['revision']))
            return dict(url=f'/exports/{name}/review.xml', path=str(folder / 'review.xml'), count=len(selected))


def make_server(store, port=0):
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def allowed(self):
            return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

        def send_headers(self, status, content_type, length, extra=None):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(length))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()

        def json_response(self, data, status=200):
            raw = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_headers(status, 'application/json; charset=utf-8', len(raw))
            if self.command != 'HEAD':
                self.wfile.write(raw)

        def do_HEAD(self):
            self.do_GET()

        def do_GET(self):
            if not self.allowed():
                return self.json_response({'error': 'Use the provided loopback URL'}, 403)
            path = urlsplit(self.path).path
            try:
                if path == '/api/queue':
                    return self.json_response(dict(queue=store.playback_queue(), state=store.state(), token=token))
                assets = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css',
                          '/playback.js': 'playback.js'}
                if path in assets:
                    target = ASSETS / assets[path]
                elif path.startswith('/previews/') and path.removeprefix('/previews/') in {
                    v['file'] for c in store.queue['cards'] for v in c['views']}:
                    target = store.folder / path.lstrip('/')
                elif re.fullmatch(r'/exports/review-r\d+-[0-9a-f]{8}/review\.xml', path):
                    target = store.folder / path.lstrip('/')
                else:
                    return self.json_response({'error': 'Not found'}, 404)
                size = target.stat().st_size
                start, end, status = 0, size - 1, 200
                extra = {'Accept-Ranges': 'bytes'}
                if target.suffix == '.xml':
                    extra['Content-Disposition'] = 'attachment; filename="Moment-Review.xml"'
                range_header = self.headers.get('Range')
                if range_header:
                    match = re.fullmatch(r'bytes=(\d*)-(\d*)', range_header)
                    if not match or not any(match.groups()):
                        self.send_headers(416, 'text/plain', 0, {'Content-Range': f'bytes */{size}'})
                        return
                    a, b = match.groups()
                    start = int(a) if a else max(0, size - int(b))
                    end = min(size - 1, int(b)) if a and b else size - 1
                    if start > end or start >= size:
                        self.send_headers(416, 'text/plain', 0, {'Content-Range': f'bytes */{size}'})
                        return
                    status = 206
                    extra['Content-Range'] = f'bytes {start}-{end}/{size}'
                self.send_headers(status, mimetypes.guess_type(target)[0] or 'application/octet-stream', end - start + 1, extra)
                if self.command != 'HEAD':
                    with target.open('rb') as f:
                        f.seek(start)
                        remaining = end - start + 1
                        while remaining:
                            block = f.read(min(262144, remaining))
                            if not block:
                                break
                            self.wfile.write(block)
                            remaining -= len(block)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
            except (ValueError, KeyError, OSError) as exc:
                self.json_response({'error': str(exc)}, 400)

        def do_POST(self):
            origin = f'http://127.0.0.1:{self.server.server_port}'
            if (not self.allowed() or self.headers.get('Origin') != origin or
                    self.headers.get('X-Review-Token') != token or
                    self.headers.get('Content-Type') != 'application/json'):
                return self.json_response({'error': 'Request rejected'}, 403)
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 32768:
                    raise ValueError('Invalid request size')
                patch = json.loads(self.rfile.read(length))
                if not isinstance(patch, dict):
                    raise ValueError('Expected an object')
                if self.path in ('/api/save', '/api/undo'):
                    return self.json_response(store.mutate(patch, undo=self.path == '/api/undo'))
                if self.path == '/api/export':
                    return self.json_response(store.export(patch))
                return self.json_response({'error': 'Not found'}, 404)
            except Conflict as exc:
                self.json_response({'error': str(exc)}, 409)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                self.json_response({'error': str(exc)}, 400)

    class LoopbackServer(ThreadingHTTPServer):
        # HTTPServer's default SO_REUSEADDR can let two Windows servers bind
        # the same port and send the browser to the wrong process.
        allow_reuse_address = os.name != 'nt'

        def server_bind(self):
            if os.name == 'nt':
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            super().server_bind()

    return LoopbackServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--events', required=True)
    init.add_argument('--plan', required=True)
    init.add_argument('--out', required=True)
    init.add_argument('--padding', type=float, default=3)
    serve = sub.add_parser('serve')
    serve.add_argument('--queue', required=True)
    serve.add_argument('--port', type=int, default=8765)
    serve.add_argument('--open', action='store_true')
    args = parser.parse_args()
    if args.command == 'init':
        print(initialize(args.events, args.plan, args.out, args.padding))
        return
    store = Store(args.queue)
    # Hold an OS lock so a second server cannot race writes to the same state.
    with (store.folder / '.server.lock').open('a+b') as lock:
        if lock.tell() == 0:
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise SystemExit('This queue is already open in another server. Use its URL.')
        with make_server(store, args.port) as server:
            url = f'http://127.0.0.1:{server.server_port}'
            print(url, flush=True)
            if args.open:
                webbrowser.open(url)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == '__main__':
    main()
