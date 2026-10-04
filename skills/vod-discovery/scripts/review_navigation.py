"""Small, cached navigation assets from registered previews, using local FFmpeg."""
from array import array
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

from vod import probe, read

SCHEMA = 'vod-review-navigation/v1'
VERSION = 1


def related_groups(cards):
    """Connected components of authored links; no inferred relation or shared clock."""
    from review_queue import digest
    by_id = {c['id']: c for c in cards}
    neighbors = {eid: set() for eid in by_id}
    links = []
    for card in cards:
        for relation in card.get('related', []):
            other = relation['event_id']
            if other == card['id'] or other not in by_id:
                continue
            neighbors[card['id']].add(other)
            neighbors[other].add(card['id'])
            links.append(dict(event_id=card['id'], related_event_id=other,
                              source_id=relation['source_id'], relationship=relation['relationship']))
    groups, visited = [], set()
    for card in cards:
        eid = card['id']
        if eid in visited or not neighbors[eid]:
            continue
        pending, component = [eid], set()
        while pending:
            node = pending.pop()
            if node in component:
                continue
            component.add(node)
            pending.extend(neighbors[node] - component)
        visited.update(component)
        ids = [c['id'] for c in cards if c['id'] in component]
        groups.append(dict(id=digest(sorted(ids)), title=by_id[ids[0]]['title'], event_ids=ids,
                           links=[l for l in links if l['event_id'] in component]))
    return dict(groups=groups, ungrouped_ids=[c['id'] for c in cards if c['id'] not in visited])


def waveform(path, duration, work):
    """Max absolute amplitude of either channel, capped at 6,000 source-time bins."""
    metadata, _ = probe(path)
    if not any(s['codec_type'] == 'audio' for s in metadata['streams']):
        return dict(status='no_audio', peaks=[], step_sec=0)
    bins = min(6000, max(1, math.ceil(duration * 20)))
    frames_per_bin = max(1, math.ceil(duration * 8000 / bins))
    peaks, cursor = [0] * bins, 0
    with work.open('wb') as output:
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-threads', '2',
            '-i', str(path), '-map', '0:a:0', '-vn', '-filter_threads', '1', '-ac', '2', '-ar', '8000', '-f', 's16le', 'pipe:1'],
            stdout=output, stderr=subprocess.PIPE, check=True, timeout=max(120, duration * 3))
    with work.open('rb') as stream:
        while block := stream.read(65536):
            samples = array('h', block)
            if sys.byteorder != 'little':
                samples.byteswap()
            for i in range(0, len(samples), 2):
                index = min(bins - 1, cursor // frames_per_bin)
                peaks[index] = max(peaks[index], abs(samples[i]), abs(samples[i + 1]))
                cursor += 1
    return dict(status='ready', peaks=[round(p / 32768, 4) for p in peaks], step_sec=frames_per_bin / 8000)


def render_aids(preview, path, out, key):
    from review_queue import file_hash
    duration = preview['preview_end_sec'] - preview['preview_start_sec']
    work = out / ('.' + key + '.' + uuid.uuid4().hex + '.pcm')
    temp = out / ('.' + key + '.' + uuid.uuid4().hex + '.jpg')
    dest = out / ('aids-' + key + '.jpg')
    interval = max(5, duration / 119)
    columns, width, height = 8, 160, 90
    rows = max(1, math.ceil(min(120, math.ceil(duration / interval) + 1) / columns))
    try:
        peaks = waveform(path, duration, work)
        filters = (f"select='isnan(prev_selected_t)+gte(t-prev_selected_t,{interval})',"
                   f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
                   f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,showinfo,tile={columns}x{rows}')
        result = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'info', '-nostdin', '-n',
            '-threads', '2', '-i', str(path), '-map', '0:v:0', '-an', '-filter_threads', '1',
            '-vf', filters, '-frames:v', '1', '-q:v', '5', '-threads', '1', str(temp)],
            capture_output=True, check=True, timeout=max(120, duration * 3))
        times = [float(t) for t in re.findall(r'\bpts_time:([\d.eE+-]+)', result.stderr.decode('utf-8', 'replace'))]
        if not times or len(times) > columns * rows or not temp.is_file():
            raise ValueError('Could not verify the thumbnail frame map')
        os.replace(temp, dest)
        frames = [dict(source_sec=preview['preview_start_sec'] + time, x=(i % columns) * width,
                       y=(i // columns) * height) for i, time in enumerate(times)]
        return dict(source_id=preview['source_id'], preview_start_sec=preview['preview_start_sec'],
                    preview_end_sec=preview['preview_end_sec'], waveform=peaks,
                    thumbnails=dict(file=dest.name, sha256=file_hash(dest), width=width, height=height,
                                    columns=columns, rows=rows, frames=frames))
    finally:
        work.unlink(missing_ok=True)
        temp.unlink(missing_ok=True)


class NavigationAssets:
    def __init__(self, store):
        self.store = store
        self.path = store.folder / 'navigation.json'
        self.folder = store.folder / 'navigation'
        try:
            record = read(self.path) if self.path.exists() else None
        except (ValueError, OSError):
            record = None
        # These are expendable derived caches. Bad caches must never block choices.
        self.record = record if (isinstance(record, dict) and record.get('schema') == SCHEMA and
            record.get('queue_hash') == store.queue_hash and isinstance(record.get('aids'), dict) and
            isinstance(record.get('excerpts'), dict)) else dict(schema=SCHEMA, queue_hash=store.queue_hash, aids={}, excerpts={})
        self.executor = None
        self.jobs, self.pending = {}, {}

    def submit(self, key, kind, target, task):
        from review_queue import Conflict
        with self.store.lock:
            if key in self.pending:
                return self.status(self.pending[key])
            if len(self.pending) >= 8:
                raise Conflict('Preview preparation is busy. Retry shortly.')
            self.store.validate_inputs()
            self.folder.mkdir(exist_ok=True)
            job = dict(id=uuid.uuid4().hex, status='pending', kind=kind, target=target)
            self.jobs[job['id']] = job
            self.pending[key] = job['id']
            if len(self.jobs) > 64:
                for old in list(self.jobs):
                    if self.jobs[old]['status'] != 'pending':
                        del self.jobs[old]
                        if len(self.jobs) <= 64:
                            break
            if self.executor is None:
                self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='vod-navigation')
            self.executor.submit(self.complete, key, job, task)
            return self.status(job['id'])

    def complete(self, key, job, task):
        from review_queue import atomic_json
        try:
            result = task()
            with self.store.lock:
                self.store.validate_inputs()
                candidate = deepcopy(self.record)
                candidate[job['kind']][key] = result
                atomic_json(self.path, candidate)
                self.record = candidate
                job.update(status='ready', result=result)
        except Exception as exc:
            with self.store.lock:
                job.update(status='error', error=str(exc))
        finally:
            with self.store.lock:
                self.pending.pop(key, None)

    def status(self, jobid):
        with self.store.lock:
            if jobid not in self.jobs:
                raise ValueError('Preview request expired; retry')
            job = self.jobs[jobid]
            return {k: deepcopy(v) for k, v in job.items() if k != 'target'}

    def valid(self, entry, excerpt=False):
        from review_queue import file_hash
        if not isinstance(entry, dict):
            return False
        sid, start, end = (entry.get(k) for k in ('source_id', 'preview_start_sec', 'preview_end_sec'))
        if (sid not in self.store.sources or type(start) not in (int, float) or type(end) not in (int, float) or
                not 0 <= start < end <= self.store.sources[sid]['duration_sec']):
            return False
        if excerpt:
            name, sha, root = entry.get('file', ''), entry.get('sha256'), self.store.folder / 'previews'
            pattern = r'speech-[0-9a-f]{64}\.mp4'
        else:
            thumbnail = entry.get('thumbnails', {})
            wave = entry.get('waveform', {})
            if not isinstance(thumbnail, dict) or not isinstance(wave, dict):
                return False
            peaks, frames = wave.get('peaks'), thumbnail.get('frames')
            if (wave.get('status') not in ('ready', 'no_audio') or not isinstance(peaks, list) or len(peaks) > 6000 or
                    any(type(p) not in (int, float) or not 0 <= p <= 1 for p in peaks) or
                    type(wave.get('step_sec')) not in (int, float) or
                    (wave['status'] == 'ready' and (not peaks or not wave['step_sec'] > 0)) or
                    not isinstance(frames, list) or not 1 <= len(frames) <= 120):
                return False
            previous = start - .25
            for frame in frames:
                if (not isinstance(frame, dict) or type(frame.get('source_sec')) not in (int, float) or
                        not previous <= frame['source_sec'] < end + .25 or
                        type(frame.get('x')) is not int or frame['x'] < 0 or type(frame.get('y')) is not int or frame['y'] < 0):
                    return False
                previous = frame['source_sec']
            name, sha, root = thumbnail.get('file', ''), thumbnail.get('sha256'), self.folder
            pattern = r'aids-[0-9a-f]{64}\.jpg'
        return bool(re.fullmatch(pattern, name)) and (root / name).is_file() and file_hash(root / name) == sha

    def aids(self, patch):
        from review_queue import digest, file_hash
        with self.store.lock:
            if 'excerpt_id' in patch:
                preview = self.record['excerpts'].get(patch['excerpt_id'])
                if not self.valid(preview, excerpt=True):
                    raise ValueError('Transcript excerpt is no longer available; click the line again')
                preview = deepcopy(preview)
            else:
                eid, index = patch.get('event_id'), patch.get('view')
                if eid not in self.store.cards or type(index) is not int or not 0 <= index < len(self.store.cards[eid]['views']):
                    raise ValueError('Unknown preview moment or POV')
                preview = self.store.context.view(eid, index)
            path = self.store.folder / 'previews' / preview['file']
            sha = file_hash(path)
            key = digest([VERSION, self.store.queue_hash, preview['source_id'], preview['preview_start_sec'],
                          preview['preview_end_sec'], sha])
            entry = self.record['aids'].get(key)
            if self.valid(entry):
                return dict(status='ready', kind='aids', result=deepcopy(entry))
            def prepare():
                result = render_aids(preview, path, self.folder, key)
                if file_hash(path) != sha:
                    raise ValueError('Preview changed during navigation preparation')
                return result
            return self.submit(key, 'aids', preview, prepare)

    def excerpt(self, patch):
        from review_queue import digest, render_preview
        with self.store.lock:
            line = self.store.transcript.by_id.get(patch.get('line_id'))
            if line is None:
                raise ValueError('Unknown attached transcript line')
            source = self.store.sources[line['source_id']]
            start = max(0, line['start_sec'] - 3)
            end = min(source['duration_sec'], start + 30)
            key = digest([VERSION, self.store.queue_hash, source['id'], start, end])
            entry = self.record['excerpts'].get(key)
            if self.valid(entry, excerpt=True):
                return dict(status='ready', kind='excerpts', result=deepcopy(entry))
            preview = dict(source_id=source['id'], label=source.get('label', source['id']), file='speech-' + key + '.mp4',
                           preview_start_sec=start, preview_end_sec=end, excerpt_id=key)
            def prepare():
                result = render_preview(source, self.store.probes[source['id']], preview,
                                        self.store.folder / 'previews' / preview['file'])
                return dict(preview, **result)
            return self.submit(key, 'excerpts', preview, prepare)

    def registered(self, name, excerpt=False):
        if not re.fullmatch(r'speech-[0-9a-f]{64}\.mp4' if excerpt else r'aids-[0-9a-f]{64}\.jpg', name):
            return False
        with self.store.lock:
            entries = self.record['excerpts' if excerpt else 'aids'].values()
            return any(isinstance(e, dict) and isinstance(e if excerpt else e.get('thumbnails'), dict) and
                       (e if excerpt else e['thumbnails']).get('file') == name for e in entries)

    def close(self):
        if self.executor is not None:
            self.executor.shutdown(wait=True, cancel_futures=True)
            self.executor = None
