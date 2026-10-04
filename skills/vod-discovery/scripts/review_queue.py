"""Local, persistent moment review. Python standard library + FFmpeg only."""
import argparse
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from fractions import Fraction
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
from urllib.parse import parse_qs, urlsplit
import uuid
import webbrowser

from vod import export_events, number, probe, read
from review_timeline import build_review
from premiere_xml import frame_rate
from review_navigation import NavigationAssets, related_groups
from review_transcript import TranscriptEvidence, import_transcripts

SCHEMA = 'vod-review-queue/v1'
BUILD_SCHEMA = 'vod-review-build/v1'
PREVIEW_VERSION = 1
CONTEXT_SCHEMA = 'vod-review-context/v1'
CONTEXT_STEP = 15
DECISIONS = ('unreviewed', 'keep', 'later', 'skip')
ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'review-queue'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


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


def atomic_snapshot(path, text):
    """Keep old snapshot bytes, including the hashes recorded in its manifest."""
    path = Path(path)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temp.open('wb') as stream:
            stream.write(text.encode('utf-8')); stream.flush(); os.fsync(stream.fileno())
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
        '\nFull main chronology retained. Selected main moments have boundary cuts and Mango labels; '
        'surrounding footage has Iris labels. Review choices select these moments, source markers '
        'and alternate excerpts; no main footage is removed.')
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


@contextmanager
def build_lock(folder, name='.build.lock', message='This queue is already being prepared by another process.'):
    with (folder / name).open('a+b') as lock:
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
        except OSError as exc:
            raise Conflict(message) from exc
        try:
            yield
        finally:
            lock.seek(0)
            if os.name == 'nt':
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)


def render_preview(source, metadata, view, dest):
    # Publish only a validated file. Interrupted encodes cannot replace a good preview.
    temp = dest.with_name(dest.stem + '.' + uuid.uuid4().hex + '.tmp.mp4')
    video = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
    audio = [s for s in metadata['streams'] if s['codec_type'] == 'audio']
    expected = view['preview_end_sec'] - view['preview_start_sec']
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
               '-ss', str(view['preview_start_sec']), '-threads', '2', '-i', source['path'],
               '-t', str(expected), '-map', f"0:{video['index']}"]
    if audio:
        command += ['-map', f"0:{audio[0]['index']}", '-c:a', 'aac', '-b:a', '128k']
    else:
        command += ['-an']
    command += ['-filter_threads', '1', '-vf', 'scale=960:-2,fps=24', '-c:v', 'libx264',
                '-preset', 'veryfast', '-crf', '25', '-pix_fmt', 'yuv420p', '-threads', '2',
                '-movflags', '+faststart', str(temp)]
    try:
        subprocess.run(command, check=True, capture_output=True, timeout=max(120, expected * 5))
        _, duration = probe(temp)
        if abs(duration - expected) > .25:
            raise ValueError(f'Preview duration differs from requested source interval: {dest.name}')
        checksum = file_hash(temp)
        os.replace(temp, dest)
        return dict(sha256=checksum, duration_sec=duration)
    finally:
        temp.unlink(missing_ok=True)


def prepare_previews(cards, sources, probes, out, record, jobs):
    pending = []
    total = sum(len(c['views']) for c in cards)
    reused = 0
    for i, card in enumerate(cards):
        for j, view in enumerate(card['views']):
            name = f'{i:04d}-{j:02d}.mp4'
            view['file'] = name
            dest = out / 'previews' / name
            cached = record['completed'].get(name, {})
            expected = view['preview_end_sec'] - view['preview_start_sec']
            if (dest.is_file() and cached.get('sha256') == file_hash(dest) and
                    isinstance(cached.get('duration_sec'), (int, float)) and
                    abs(cached['duration_sec'] - expected) <= .25):
                reused += 1
            else:
                record['completed'].pop(name, None)
                pending.append((name, view, dest))
    atomic_json(out / 'build.json', record)
    if reused:
        print(f'Reusing {reused}/{total} verified previews.', flush=True)
    error = None
    executor = ThreadPoolExecutor(max_workers=jobs)
    try:
        futures = {executor.submit(render_preview, sources[v['source_id']], probes[v['source_id']], v, dest): name
                   for name, v, dest in pending}
        for future in as_completed(futures):
            if future.cancelled():
                continue
            name = futures[future]
            try:
                record['completed'][name] = future.result()
                atomic_json(out / 'build.json', record)
                print(f"Prepared {len(record['completed'])}/{total} previews.", flush=True)
            except Exception as exc:
                if error is None:
                    error = exc
                    for other in futures:
                        other.cancel()
    finally:
        # Ctrl+C must not wait for every queued encode to run. Finish active jobs only.
        executor.shutdown(wait=True, cancel_futures=True)
    if error is not None:
        raise error


def initialize(events_path, plan_path, out, padding=3, jobs=2, resume=False, migration=None):
    out = Path(out).resolve()
    if type(jobs) is not int or jobs < 1:
        raise ValueError('Preview jobs must be a positive integer')
    data, plan = read(events_path), read(plan_path)
    export_events(data)
    if not data['events']:
        raise ValueError('No moments to review')
    event_map = {e['id']: e for e in data['events']}
    for alt in plan.get('alternates', []):
        event = event_map.get(alt.get('event_id'))
        if not event or not {alt['source_id'], alt['main_source_id']} <= {v['source_id'] for v in event['perspectives']}:
            raise ValueError('Every alternate needs an event_id with both referenced perspectives')
    identities = {s['id']: identity(s) for s in data['sources']}
    inputs = [dict(path=str(Path(p).resolve()), sha256=file_hash(p)) for p in (events_path, plan_path)]
    request = dict(schema=BUILD_SCHEMA, identities=identities, inputs=inputs,
                   settings=dict(padding=padding, preview_version=PREVIEW_VERSION))
    cards = cards_for(data, plan, padding)
    if migration is not None:
        from review_migration import prepare_migration
        report = prepare_migration(migration, data, plan, probes=None, identities=identities)
        request['migration'] = digest(migration)
        # Retain already requested context and source positions on unchanged views.
        for card in cards:
            if report['moments'][card['id']]['status'] == 'unchanged':
                old = migration['cards'][report['moments'][card['id']]['previous_id']]
                for view in card['views']:
                    prior = next(v for v in old['views'] if v['source_id'] == view['source_id'])
                    view['preview_start_sec'] = min(view['preview_start_sec'], prior['preview_start_sec'])
                    view['preview_end_sec'] = max(view['preview_end_sec'], prior['preview_end_sec'])
    decisions = {c['id']: dict(decision='unreviewed', note='', view=0, positions={}) for c in cards}
    if resume:
        if not out.is_dir():
            raise ValueError('No incomplete build to resume in this folder')
        probes = None
    else:
        probes = {}
        for source in data['sources']:
            metadata, duration = probe(Path(source['path']))
            if abs(duration - source['duration_sec']) > .1:
                raise ValueError('Media duration changed; review source mapping')
            probes[source['id']] = metadata
        selected_xml(data, plan, probes, decisions, 'all')  # Validate layout before rendering.
        out.mkdir(parents=True, exist_ok=False)
    with build_lock(out):
        if resume:
            if (out / 'queue.json').exists():
                raise ValueError('This queue is complete. Run serve to resume reviewing it.')
            if not (out / 'build.json').is_file():
                raise ValueError('No resumable build record. Use a new output folder.')
            record = read(out / 'build.json')
            if any(record.get(key) != value for key, value in request.items()):
                raise ValueError('Build inputs, media or preview settings changed. Use a new output folder.')
            for name in ('events.json', 'plan.json', 'probes.json'):
                if file_hash(out / name) != record['snapshots'].get(name):
                    raise ValueError('Build snapshot changed. Use a new output folder.')
            probes = read(out / 'probes.json')
            selected_xml(data, plan, probes, decisions, 'all')
        else:
            (out / 'previews').mkdir()
            atomic_json(out / 'events.json', data)
            atomic_json(out / 'plan.json', plan)
            atomic_json(out / 'probes.json', probes)
            record = dict(request, completed={}, snapshots={n: file_hash(out / n)
                          for n in ('events.json', 'plan.json', 'probes.json')})
            atomic_json(out / 'build.json', record)
        if migration is not None:
            atomic_json(out / 'migration-input.json', migration)
        prepare_previews(cards, {s['id']: s for s in data['sources']}, probes, out, record, jobs)
        # Recheck inputs after a long encode; never publish previews for changed originals.
        if ({s['id']: identity(s) for s in data['sources']} != identities or
                any(file_hash(item['path']) != item['sha256'] for item in inputs)):
            raise ValueError('Build inputs or media changed during preparation. Use a new output folder.')
        manifest = dict(schema=SCHEMA, title='Moment review', cards=cards, identities=identities,
            coverage=plan.get('coverage_note', 'Review coverage not supplied.'),
            snapshots=record['snapshots'], inputs=inputs)
        initial_state = dict(schema=SCHEMA, queue_hash=digest(manifest), revision=0,
            current_id=cards[0]['id'], decisions=decisions, history=[])
        if migration is not None:
            from review_migration import prepare_migration, migrated_state
            report = prepare_migration(migration, data, plan, probes=probes, identities=identities)
            manifest['migration'] = report
            initial_state = migrated_state(manifest, migration)
            archive = out / 'migration' / 'previous'
            archive.mkdir(parents=True, exist_ok=True)
            for name, value in migration['snapshots'].items():
                atomic_snapshot(archive / name, migration['raw_snapshots'][name])
            for name, text in migration.get('ancestor_snapshots', {}).items():
                target = out / 'migration' / name
                target.parent.mkdir(parents=True, exist_ok=True)
                atomic_snapshot(target, text)
            atomic_json(out / 'migration.json', report)
        # queue.json is the completion record; publish it after the initial state.
        atomic_json(out / 'state.json', initial_state)
        atomic_json(out / 'queue.json', manifest)
        if migration is not None and 'transcript.json' in migration['snapshots']:
            # Speech belongs to original source clocks, independently of moment choices.
            previous = migration['snapshots']['transcript.json']
            unchanged = {sid for sid, value in identities.items()
                         if migration['snapshots']['queue.json']['identities'].get(sid) == value}
            if previous.get('schema') == 'vod-review-transcript/v1':
                attached = deepcopy(previous)
                attached['queue_hash'] = digest(manifest)
                attached['rows'] = [r for r in attached['rows'] if r['source_id'] in unchanged]
                attached['coverage'] = [c for c in attached['coverage'] if c['source_id'] in unchanged]
                atomic_json(out / 'transcript.json', attached)
        return out


class Conflict(ValueError):
    pass


DEFAULT_KEYS = dict(previous='ArrowLeft', next='ArrowRight', pov='KeyP', povBack='Shift+KeyP',
                    play='Space', back='Shift+ArrowLeft', forward='Shift+ArrowRight',
                    keep='Digit1', later='Digit2', skip='Digit3', undo='KeyU',
                    extendBack='BracketLeft', extendForward='BracketRight')
LEGACY_KEYS = set(DEFAULT_KEYS) - {'extendBack', 'extendForward'}
KEY_CODES = ([f'Key{c}' for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'] + [f'Digit{n}' for n in range(10)] +
             ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Space', 'Enter', 'Backspace',
              'Delete', 'Home', 'End', 'PageUp', 'PageDown', 'Comma', 'Period', 'Slash',
              'Semicolon', 'Quote', 'BracketLeft', 'BracketRight', 'Backslash', 'Minus', 'Equal'])


class Preferences:
    """One keyboard profile for all queues/ports; independent of review decisions."""
    def __init__(self, path=None):
        base = Path(os.environ.get('LOCALAPPDATA') or os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
        self.path = Path(path) if path else base / 'vod-discovery' / 'keybinds.json'
        self.lock = threading.Lock()

    @staticmethod
    def validate(keys):
        if not isinstance(keys, dict) or set(keys) != set(DEFAULT_KEYS):
            raise ValueError('Provide every keyboard action')
        allowed = set(KEY_CODES) | {'Shift+' + code for code in KEY_CODES}
        if any(not isinstance(v, str) or v not in allowed for v in keys.values()):
            raise ValueError('Use a letter, number, navigation or punctuation key, optionally with Shift')
        if len(set(keys.values())) != len(keys):
            raise ValueError('Each shortcut must be unique')

    def read(self):
        if not self.path.exists():
            return dict(schema=1, revision=0, keys=deepcopy(DEFAULT_KEYS))
        value = read(self.path)
        if value.get('schema') != 1 or type(value.get('revision')) is not int or value['revision'] < 0:
            raise ValueError('Invalid saved keyboard profile')
        if isinstance(value.get('keys'), dict) and set(value['keys']) == LEGACY_KEYS:
            # Preserve customized old bindings, even if they occupy the new defaults.
            keys = dict(value['keys'])
            for action in ('extendBack', 'extendForward'):
                options = [DEFAULT_KEYS[action], 'Shift+' + DEFAULT_KEYS[action]] + KEY_CODES
                keys[action] = next(key for key in options if key not in keys.values())
            value['keys'] = keys
        self.validate(value.get('keys'))
        return value

    @contextmanager
    def exclusive(self):
        # Separate lock file stays stable across atomic profile replacements.
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.with_suffix('.lock').open('a+b') as lock:
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
                except OSError as exc:
                    raise Conflict('Keyboard settings are being saved by another project. Try again.') from exc
                try:
                    yield
                finally:
                    lock.seek(0)
                    if os.name == 'nt':
                        msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(lock, fcntl.LOCK_UN)

    def save(self, patch):
        self.validate(patch.get('keys'))
        with self.exclusive():
            current = self.read()
            if type(patch.get('revision')) is not int or patch['revision'] != current['revision']:
                raise Conflict('Keyboard settings changed in another project. Reopen Keys and try again.')
            value = dict(schema=1, revision=current['revision'] + 1, keys=deepcopy(patch['keys']))
            atomic_json(self.path, value)
            return value


class ContextPreviews:
    """On-demand encodes; completion is separate from decisions and discovery."""
    def __init__(self, store, repair=True):
        self.store = store
        self.path = store.folder / 'context.json'
        self.record = (read(self.path) if self.path.exists() else
                       dict(schema=CONTEXT_SCHEMA, queue_hash=store.queue_hash, completed={}, cached={}))
        if self.record.get('schema') != CONTEXT_SCHEMA or self.record.get('queue_hash') != store.queue_hash:
            raise ValueError('Context previews belong to a different queue')
        if not isinstance(self.record.get('completed'), dict) or not isinstance(self.record.get('cached', {}), dict):
            raise ValueError('Invalid saved context registry')
        self.jobs, self.pending = {}, {}
        self.record.setdefault('cached', {e['file']: e for e in self.record['completed'].values()})
        for key, entry in self.record['completed'].items():
            if (key != self.key(entry['event_id'], entry['view']) or
                    self.record['cached'].get(entry['file']) != entry):
                raise ValueError('Invalid context moment/cache binding')
        self.executor = None
        for name, entry in self.record['cached'].items():
            if name != entry['file'] or not re.fullmatch(r'context-[0-9a-f]{64}\.mp4', name):
                raise ValueError('Invalid registered context preview')
        for entry in list(self.record['completed'].values()) + list(self.record['cached'].values()):
            if (entry['event_id'] not in store.cards or type(entry['view']) is not int or
                    not 0 <= entry['view'] < len(store.cards[entry['event_id']]['views'])):
                raise ValueError('Invalid context moment or POV')
            base = store.cards[entry['event_id']]['views'][entry['view']]
            duration = store.sources[base['source_id']]['duration_sec']
            if (entry['source_id'] != base['source_id'] or
                    not 0 <= entry['preview_start_sec'] <= base['preview_start_sec'] or
                    not base['preview_end_sec'] <= entry['preview_end_sec'] <= duration or
                    not re.fullmatch(r'context-[0-9a-f]{64}\.mp4', entry['file']) or
                    not re.fullmatch(r'[0-9a-f]{64}', entry['sha256']) or
                    abs(entry['duration_sec'] - (entry['preview_end_sec'] - entry['preview_start_sec'])) > .25):
                raise ValueError('Invalid saved context preview')
        if repair:
            # A saved source position may lie outside the base preview. Repair
            # damaged/missing current context before serving it rather than
            # loading a shorter file and overwriting that source position.
            for key, entry in list(self.record['completed'].items()):
                if self.valid(entry):
                    continue
                store.validate_inputs()
                view = self.view(entry['event_id'], entry['view'])
                source = store.sources[view['source_id']]
                result = render_preview(source, store.probes[source['id']], view,
                                        store.folder / 'previews' / view['file'])
                store.validate_inputs()
                candidate = deepcopy(self.record)
                candidate['completed'][key] = {**entry, **result}
                candidate['cached'][entry['file']] = candidate['completed'][key]
                atomic_json(self.path, candidate)
                self.record = candidate

    @staticmethod
    def key(eid, index):
        return digest([eid, index])

    def view(self, eid, index):
        with self.store.lock:
            base = deepcopy(self.store.cards[eid]['views'][index])
            base['base_preview_start_sec'] = base['preview_start_sec']
            base['source_duration_sec'] = self.store.sources[base['source_id']]['duration_sec']
            entry = self.record['completed'].get(self.key(eid, index))
            if entry:
                base.update({k: entry[k] for k in ('preview_start_sec', 'preview_end_sec', 'file')})
            return base

    def registered(self, name):
        with self.store.lock:
            return name in self.record['cached']

    def request(self, patch):
        eid, index, direction = patch.get('event_id'), patch.get('view'), patch.get('direction')
        if eid not in self.store.cards or type(index) is not int or not 0 <= index < len(self.store.cards[eid]['views']):
            raise ValueError('Unknown context moment or view')
        if direction not in ('before', 'after'):
            raise ValueError('Context direction must be before or after')
        # Bounds from the caller make network retries idempotent. A stale tab's
        # request unions with newer context instead of adding another 15 seconds.
        start = number(patch.get('preview_start_sec'), 'context start')
        end = number(patch.get('preview_end_sec'), 'context end')
        with self.store.lock:
            base = self.store.cards[eid]['views'][index]
            current = self.view(eid, index)
            duration = current['source_duration_sec']
            if not 0 <= start <= base['preview_start_sec'] < base['preview_end_sec'] <= end <= duration:
                raise ValueError('Context request must contain the original preview within media bounds')
            requested_start = max(0, start - CONTEXT_STEP) if direction == 'before' else start
            requested_end = min(duration, end + CONTEXT_STEP) if direction == 'after' else end
            if (requested_start < current['preview_start_sec'] - CONTEXT_STEP or
                    requested_end > current['preview_end_sec'] + CONTEXT_STEP):
                raise ValueError('Request at most 15 seconds of additional context per side')
            target = dict(current, preview_start_sec=min(current['preview_start_sec'], requested_start),
                          preview_end_sec=max(current['preview_end_sec'], requested_end))
            key = self.key(eid, index)
            if key in self.pending:
                job = self.jobs[self.pending[key]]
                if (job['target']['preview_start_sec'] <= target['preview_start_sec'] and
                        job['target']['preview_end_sec'] >= target['preview_end_sec']):
                    return self.status(job['id'])
                raise Conflict('Context for this POV is already preparing. Try again when it is ready.')
            entry = self.record['completed'].get(key)
            if (target['preview_start_sec'] == current['preview_start_sec'] and
                    target['preview_end_sec'] == current['preview_end_sec'] and
                    (not entry or self.valid(entry))):
                return dict(status='ready', event_id=eid, view=index, preview=current)
            if len(self.pending) >= 8:
                raise Conflict('Context preparation is busy. Try again shortly.')
            self.store.validate_inputs()
            name = 'context-' + digest([self.store.queue_hash, eid, index, target['preview_start_sec'],
                                       target['preview_end_sec'], PREVIEW_VERSION]) + '.mp4'
            target['file'] = name
            jobid = uuid.uuid4().hex
            job = dict(id=jobid, status='pending', event_id=eid, view=index, target=target)
            self.jobs[jobid] = job; self.pending[key] = jobid
            if self.executor is None:
                self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='vod-context')
            self.executor.submit(self.encode, key, job)
            return self.status(jobid)

    def valid(self, entry):
        target = self.store.folder / 'previews' / entry['file']
        return target.is_file() and file_hash(target) == entry['sha256']

    def encode(self, key, job):
        try:
            source = self.store.sources[job['target']['source_id']]
            result = render_preview(source, self.store.probes[source['id']], job['target'],
                                    self.store.folder / 'previews' / job['target']['file'])
            with self.store.lock:
                self.store.validate_inputs()
                entry = dict(event_id=job['event_id'], view=job['view'], source_id=source['id'],
                             **{k: job['target'][k] for k in ('preview_start_sec', 'preview_end_sec', 'file')}, **result)
                candidate = deepcopy(self.record)
                candidate['completed'][key] = entry
                candidate['cached'][entry['file']] = entry
                atomic_json(self.path, candidate)
                self.record = candidate
                job['status'] = 'ready'
        except Exception as exc:
            with self.store.lock:
                job.update(status='error', error=str(exc))
        finally:
            with self.store.lock:
                self.pending.pop(key, None)

    def status(self, jobid):
        with self.store.lock:
            if jobid not in self.jobs:
                raise ValueError('Context request expired. Retry the same request.')
            job = self.jobs[jobid]
            result = {k: job[k] for k in ('id', 'status', 'event_id', 'view')}
            if job['status'] == 'ready':
                result['preview'] = self.view(job['event_id'], job['view'])
            if job['status'] == 'error':
                result['error'] = job['error']
            return result

    def close(self):
        if self.executor is not None:
            self.executor.shutdown(wait=True, cancel_futures=True)
            self.executor = None


class Store:
    def __init__(self, folder, allow_stale=False):
        self.folder = Path(folder).resolve(strict=True)
        self.queue = read(self.folder / 'queue.json')
        if self.queue['schema'] != SCHEMA:
            raise ValueError('Unknown queue schema')
        self.queue_hash = digest(self.queue)
        self.lock = threading.RLock()
        self.cards = {c['id']: c for c in self.queue['cards']}
        self.sources = {s['id']: s for s in read(self.folder / 'events.json')['sources']}
        self.probes = read(self.folder / 'probes.json')
        self.playback_plan = read(self.folder / 'plan.json')
        self.validate_snapshots()
        if not allow_stale:
            self.validate_inputs()
        self.context = ContextPreviews(self, repair=not allow_stale)
        self.navigation = NavigationAssets(self)
        try:
            self.transcript = TranscriptEvidence(self)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            # A damaged optional transcript must not strand confirmed choices.
            self.transcript = TranscriptEvidence(self, load=False)
            self.transcript.error = str(exc)
        self.timeline = self.timeline_data()
        self.state()

    def timeline_data(self):
        sources = {s['id']: s for s in read(self.folder / 'events.json')['sources']}
        probes = read(self.folder / 'probes.json')
        mains = self.playback_plan['main_sources']
        fps = frame_rate(next(s for s in probes[mains[0]]['streams'] if s['codec_type'] == 'video'))[2]
        parts, cursor = [], 0
        for sid in mains:
            source = sources[sid]
            frames = round(Fraction(str(source['duration_sec'])) * fps)
            parts.append(dict(id=sid, label=source.get('label', sid), start=float(cursor / fps),
                              end=float((cursor + frames) / fps)))
            cursor += frames
        origins = {p['id']: p['start'] for p in parts}
        segments = []
        for card in self.cards.values():
            for index, view in enumerate(card['views']):
                if view['source_id'] in origins:
                    origin = origins[view['source_id']]
                    segments.append(dict(eid=card['id'], view=index, lane='main', origin=origin, offset=0,
                        start=origin+view['start_sec'], end=origin+view['end_sec'], label=view['title'], uncertainty=0))
        lanes = []
        for alt in self.playback_plan.get('alternates', []):
            card = self.cards[alt['event_id']]
            index = next(i for i, v in enumerate(card['views']) if v['source_id'] == alt['source_id'])
            sid = alt['source_id']
            if sid not in [lane['id'] for lane in lanes]:
                lanes.append(dict(id=sid, label=sources[sid].get('label', sid)))
            origin = origins[alt['main_source_id']]
            offset = alt['source_anchor_sec'] - alt['main_anchor_sec']
            segments.append(dict(eid=card['id'], view=index, lane=sid, origin=origin, offset=offset,
                start=origin+alt['source_start_sec']-offset, end=origin+alt['source_end_sec']-offset,
                label=card['views'][index]['title'], uncertainty=alt['uncertainty_sec']))
        return dict(parts=parts, segments=segments, total=float(cursor / fps),
                    lanes=lanes + [dict(id='main', label=sources[mains[0]].get('pov', 'Main'))])

    def validate_snapshots(self):
        for name, expected in self.queue['snapshots'].items():
            if name not in ('events.json', 'plan.json', 'probes.json') or file_hash(self.folder / name) != expected:
                raise ValueError('Queue snapshot changed. Preserve this queue and create a new one.')

    def validate_inputs(self):
        self.validate_snapshots()
        for item in self.queue['inputs']:
            if file_hash(item['path']) != item['sha256']:
                raise ValueError('Discovery inputs changed. Preserve choices; build a new queue for revised discoveries.')
        for source in read(self.folder / 'events.json')['sources']:
            if identity(source) != self.queue['identities'][source['id']]:
                raise ValueError('Source media changed. Review mapping before exporting.')

    def state(self, state=None):
        state = read(self.folder / 'state.json') if state is None else state
        if state['schema'] != SCHEMA or state['queue_hash'] != self.queue_hash or set(state['decisions']) != set(self.cards):
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
            for key, position in item.get('source_positions', {}).items():
                if not key.isdecimal() or not 0 <= int(key) < len(self.cards[eid]['views']):
                    raise ValueError('Invalid saved source view')
                sid = self.cards[eid]['views'][int(key)]['source_id']
                if number(position, 'saved source position') > self.sources[sid]['duration_sec']:
                    raise ValueError('Invalid saved source position')
        return state

    def playback_queue(self):
        # Derive from the validated immutable plan; preserve manifest/state hashes.
        queue = deepcopy(self.queue)
        queue['timeline'] = self.timeline
        links = {}
        for a in self.playback_plan.get('alternates', []):
            links.setdefault(a['event_id'], []).append(dict(
                main_source_id=a['main_source_id'], source_id=a['source_id'],
                offset_sec=a['source_anchor_sec'] - a['main_anchor_sec'],
                source_start_sec=a['source_start_sec'], source_end_sec=a['source_end_sec'],
                uncertainty_sec=a['uncertainty_sec']))
        for card in queue['cards']:
            card['sync_links'] = links.get(card['id'], [])
            for index, view in enumerate(card['views']):
                view.update(self.context.view(card['id'], index))
            card['migration'] = queue.get('migration', {}).get('moments', {}).get(card['id'])
        queue['context_step_sec'] = CONTEXT_STEP
        queue['related_groups'] = related_groups(queue['cards'])
        queue['transcript'] = self.transcript.summary()
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
                    item.setdefault('source_positions', {})[str(view)] = min(v['preview_end_sec'], v['preview_start_sec'] + position)
                if 'source_position_sec' in patch:
                    position = number(patch['source_position_sec'], 'source playback position')
                    effective = self.context.view(eid, view)
                    if not effective['preview_start_sec'] <= position <= effective['preview_end_sec'] + .25:
                        raise ValueError('Source playback position outside preview')
                    item.setdefault('source_positions', {})[str(view)] = min(position, effective['preview_end_sec'])
                    original = self.cards[eid]['views'][view]
                    if original['preview_start_sec'] <= position <= original['preview_end_sec']:
                        item['positions'][str(view)] = position - original['preview_start_sec']
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


def update_queue(previous, events_path, plan_path, out, padding=3, jobs=2, resume=False, event_map=None):
    previous, out = Path(previous).resolve(strict=True), Path(out).resolve()
    if previous == out or previous in out.parents or out in previous.parents:
        raise ValueError('Update into a new, separate folder; preserve the previous queue')
    mapping = {}
    if event_map is not None:
        supplied = read(event_map)
        if supplied.get('schema') != 'vod-review-event-map/v1' or not isinstance(supplied.get('matches'), list):
            raise ValueError('Use a vod-review-event-map/v1 mapping with explicit matches')
        for match in supplied['matches']:
            eid, old = match.get('event_id'), match.get('previous_id')
            if not isinstance(eid, str) or not isinstance(old, str) or eid in mapping:
                raise ValueError('Each explicit event match must be unique')
            mapping[eid] = old
    # Changed external inputs/media are allowed here, but never changed queue
    # snapshots or an active server that could save decisions during migration.
    with build_lock(previous, '.server.lock', 'Stop the previous queue server before updating; its choices remain saved.'):
        store = Store(previous, allow_stale=True)
        snapshot_names = ('queue.json', 'state.json', 'events.json', 'plan.json', 'probes.json', 'context.json', 'build.json', 'migration.json', 'transcript.json')
        raw = {name: (previous / name).read_bytes().decode('utf-8')
               for name in snapshot_names if (previous / name).is_file()}
        ancestors = {}
        ancestor_folders = []
        prior = previous / 'migration' / 'previous'
        if (prior / 'queue.json').is_file():
            ancestor_folders.append((digest(read(prior / 'queue.json')), prior))
        old_ancestors = previous / 'migration' / 'ancestors'
        if old_ancestors.is_dir():
            ancestor_folders.extend((folder.name, folder) for folder in old_ancestors.iterdir() if folder.is_dir())
        for key, folder in ancestor_folders:
            if (not re.fullmatch(r'[0-9a-f]{64}', key) or folder.is_symlink() or
                    previous not in folder.resolve().parents):
                raise ValueError('Invalid previous history archive')
            for name in snapshot_names:
                path = folder / name
                if path.is_file():
                    if path.is_symlink():
                        raise ValueError('History snapshot must stay inside the previous queue')
                    text = path.read_bytes().decode('utf-8')
                    relative = 'ancestors/' + key + '/' + name
                    if relative in ancestors and ancestors[relative] != text:
                        raise ValueError('Conflicting previous history snapshots')
                    ancestors[relative] = text
        migration = dict(folder=str(previous), event_map=mapping,
                         raw_snapshots=raw, ancestor_snapshots=ancestors,
                         snapshots={name: json.loads(text) for name, text in raw.items()},
                         cards={card['id']: card for card in store.playback_queue()['cards']})
        try:
            if digest(migration['snapshots']['queue.json']) != store.queue_hash:
                raise ValueError('Previous queue changed during migration snapshot')
            for name, expected in store.queue['snapshots'].items():
                if hashlib.sha256(raw[name].encode('utf-8')).hexdigest() != expected:
                    raise ValueError('Previous snapshot changed during migration capture')
            store.state(migration['snapshots']['state.json'])
            return initialize(events_path, plan_path, out, padding, jobs, resume, migration)
        finally:
            store.context.close()
            store.navigation.close()


def make_server(store, port=0, preferences=None):
    token = secrets.token_urlsafe(32)
    preferences = preferences or Preferences()
    preview_files = frozenset(v['file'] for c in store.queue['cards'] for v in c['views'])

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            # Bound abandoned requests and paused range downloads.
            self.connection.settimeout(15)

        def log_message(self, *args):
            pass

        def allowed(self):
            return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

        def send_headers(self, status, content_type, length, extra=None):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(length))
            self.send_header('Connection', 'close')
            self.close_connection = True
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
                if path == '/api/keys':
                    return self.json_response(dict(profile=preferences.read(), defaults=DEFAULT_KEYS, codes=KEY_CODES))
                if path == '/api/transcript':
                    query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
                    def arg(name, default=None):
                        values = query.get(name, [default])
                        if len(values) != 1:
                            raise ValueError('Duplicate transcript parameter')
                        return values[0]
                    return self.json_response(store.transcript.search(query=arg('q', ''), source_id=arg('source_id'),
                        start=float(arg('start')) if arg('start') is not None else None,
                        end=float(arg('end')) if arg('end') is not None else None,
                        offset=int(arg('offset', 0)), limit=int(arg('limit', 100)), current_id=arg('current_id')))
                if re.fullmatch(r'/api/navigation/[0-9a-f]{32}', path):
                    return self.json_response(store.navigation.status(path.rsplit('/', 1)[-1]))
                if re.fullmatch(r'/api/context/[0-9a-f]{32}', path):
                    return self.json_response(store.context.status(path.rsplit('/', 1)[-1]))
                assets = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css',
                          '/playback.js': 'playback.js', '/timeline.js': 'timeline.js', '/keys.js': 'keys.js',
                          '/aids.js': 'aids.js'}
                if path in assets:
                    target = ASSETS / assets[path]
                elif path.startswith('/previews/') and (path.removeprefix('/previews/') in preview_files or
                        store.context.registered(path.removeprefix('/previews/')) or
                        store.navigation.registered(path.removeprefix('/previews/'), excerpt=True)):
                    target = store.folder / path.lstrip('/')
                elif path.startswith('/navigation/') and store.navigation.registered(path.removeprefix('/navigation/')):
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
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, TimeoutError):
                self.close_connection = True
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
                if self.path == '/api/keys':
                    return self.json_response(preferences.save(patch))
                if self.path == '/api/context':
                    return self.json_response(store.context.request(patch))
                if self.path == '/api/aids':
                    return self.json_response(store.navigation.aids(patch))
                if self.path == '/api/transcript-preview':
                    return self.json_response(store.navigation.excerpt(patch))
                return self.json_response({'error': 'Not found'}, 404)
            except Conflict as exc:
                self.json_response({'error': str(exc)}, 409)
            except (ValueError, KeyError, TypeError, OSError) as exc:
                self.json_response({'error': str(exc)}, 400)

    class LoopbackServer(ThreadingHTTPServer):
        # HTTPServer's default SO_REUSEADDR can let two Windows servers bind
        # the same port and send the browser to the wrong process.
        allow_reuse_address = os.name != 'nt'

        def server_close(self):
            super().server_close()
            store.context.close()
            store.navigation.close()

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
    init.add_argument('--jobs', type=int, default=2, help='Maximum concurrent preview encodes (default: 2; use 1 for serial)')
    init.add_argument('--resume', action='store_true', help='Resume an incomplete build with unchanged inputs and settings')
    update = sub.add_parser('update', help='Create a revised queue and conservatively preserve prior review choices')
    update.add_argument('--from-queue', required=True)
    update.add_argument('--events', required=True)
    update.add_argument('--plan', required=True)
    update.add_argument('--out', required=True)
    update.add_argument('--padding', type=float, default=3)
    update.add_argument('--jobs', type=int, default=2)
    update.add_argument('--resume', action='store_true')
    update.add_argument('--event-map', help='Explicit one-to-one stable-ID mapping for renamed moments')
    transcript = sub.add_parser('transcripts', help='Attach an existing literal speech index without new transcription')
    transcript.add_argument('--queue', required=True)
    transcript.add_argument('--index', required=True)
    transcript.add_argument('--source-map', help='Explicit source and clock mapping for verified excerpt media')
    serve = sub.add_parser('serve')
    serve.add_argument('--queue', required=True)
    serve.add_argument('--port', type=int, default=8765)
    serve.add_argument('--open', action='store_true')
    serve.add_argument('--preferences', help='Override the shared keyboard-profile path (for isolated testing)')
    args = parser.parse_args()
    if args.command == 'init':
        print(initialize(args.events, args.plan, args.out, args.padding, args.jobs, args.resume))
        return
    if args.command == 'update':
        print(update_queue(args.from_queue, args.events, args.plan, args.out, args.padding,
                           args.jobs, args.resume, args.event_map))
        return
    folder = Path(args.queue).resolve(strict=True)
    if args.command == 'transcripts':
        with build_lock(folder, '.server.lock', 'Stop this queue server before attaching transcript evidence.'):
            store = Store(folder)
            try:
                print(json.dumps(import_transcripts(store, args.index, args.source_map), indent=2))
            finally:
                store.context.close()
                store.navigation.close()
        return
    # Lock before Store can repair context, not just before serving choices.
    with (folder / '.server.lock').open('a+b') as lock:
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
        store = Store(folder)
        with make_server(store, args.port, Preferences(args.preferences)) as server:
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
