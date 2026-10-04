"""Snapshot and search existing timestamped speech; never run inference."""
from copy import deepcopy
import math
from pathlib import Path
import re

from vod import read

SCHEMA = 'vod-review-transcript/v1'


def media_key(path):
    return str(Path(path).resolve()).replace('\\', '/').casefold()


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def inside(root, *parts):
    path = root.joinpath(*parts).resolve(strict=True)
    if root not in path.parents:
        raise ValueError('Transcript index files must stay within the index folder')
    return path


def import_transcripts(store, index_path, source_map=None):
    """Use the literal search index's validated occurrences, preserving each stream."""
    from evidence import input_signature
    from review_queue import atomic_json, digest, file_hash
    from unified_search import speech_documents
    store.validate_inputs()
    path = Path(index_path).resolve(strict=True)
    if path.is_dir():
        path /= 'index.json'
    index = read(path)
    if index.get('schema') != 'vod-search/v1':
        raise ValueError('Supply the existing vod.py index folder or its index.json')
    for prepared, signature in index['inputs'].items():
        if input_signature(prepared) != signature:
            raise ValueError('Transcript index is stale; rebuild the existing index before attaching it')
    mappings = {}
    if source_map:
        value = read(source_map)
        if value.get('schema') != 'vod-review-transcript-map/v1':
            raise ValueError('Expected a vod-review-transcript-map/v1 source mapping')
        for entry in value['sources']:
            sid, target, offset = entry['indexed_source_id'], entry['source_id'], entry.get('offset_sec', 0)
            if sid in mappings or target not in store.sources or not finite(offset):
                raise ValueError('Transcript source mapping must be unique, finite and refer to a queue source')
            if not isinstance(entry.get('evidence'), str) or not entry['evidence'].strip():
                raise ValueError('An explicit transcript mapping needs evidence for its source clock')
            mappings[sid] = deepcopy(entry)
    by_path = {media_key(s['path']): s['id'] for s in store.sources.values()}
    rows, coverage, unmapped, rejected = {}, [], [], 0
    input_files = {str(path): file_hash(path)}
    for info in index['sources']:
        prepared_source = read(Path(info['prepared']) / 'source.json')
        if (prepared_source['id'] != info['source_id'] or
                media_key(prepared_source['path']) != media_key(info['source'])):
            raise ValueError('Transcript index source does not match its prepared metadata')
        stat = Path(info['source']).stat()
        if stat.st_size != prepared_source['size'] or stat.st_mtime_ns != prepared_source['mtime_ns']:
            raise ValueError('Transcript source media changed since preparation')
        mapping = mappings.get(info['source_id'])
        sid = mapping['source_id'] if mapping else by_path.get(media_key(info['source']))
        if sid is None:
            unmapped.append(dict(source_id=info['source_id'], source=info['source']))
            continue
        offset = mapping.get('offset_sec', 0) if mapping else 0
        duration = store.sources[sid]['duration_sec']
        ranges = []
        for a, b in info['core_ranges_sec']:
            if not finite(a) or not finite(b) or not 0 <= a + offset < b + offset <= duration + .1:
                raise ValueError('Mapped transcript coverage exceeds its queue source')
            ranges.append([a + offset, min(duration, b + offset)])
        coverage.append(dict(source_id=sid, indexed_source_id=info['source_id'], source=info['source'],
            prepared=info['prepared'], core_ranges_sec=ranges, prepared_packets=info['prepared_packets'],
            total_packets=info['total_packets'], mapping=mapping))
        aggregate = inside(path.parent, index['build'], info['aggregate'], 'transcript.json')
        input_files[str(aggregate)] = file_hash(aggregate)
        valid_segments = []
        for segment in read(aggregate)['segments']:
            text = segment.get('text')
            if not isinstance(text, str) or not text.strip():
                rejected += 1
                continue
            occurrences = []
            for occurrence in segment.get('occurrences', []):
                start, end, stream = (occurrence.get(k) for k in ('start_sec', 'end_sec', 'audio_stream'))
                if (not finite(start) or not finite(end) or type(stream) is not int or stream < 0 or
                        not 0 <= start < end <= prepared_source['duration_sec'] or
                        not 0 <= start + offset < end + offset <= duration):
                    rejected += 1
                    continue
                occurrences.append(occurrence)
            if occurrences:
                valid_segments.append(dict(segment, occurrences=occurrences))
        # Reuse the existing cross-source search adapter's exact raw/stream/reference checks.
        for document in speech_documents([(info, valid_segments)], input_files):
            start, end, stream, text = (document[k] for k in ('start_sec', 'end_sec', 'audio_stream', 'text'))
            start, end = start + offset, end + offset
            key = (sid, stream, start, end, text)
            row = rows.setdefault(key, dict(id=digest(key), source_id=sid, audio_stream=stream,
                start_sec=start, end_sec=end, text=text, refs=[]))
            for occurrence in document['occurrences']:
                ref = dict(occurrence, indexed_source_id=info['source_id'], indexed_source=info['source'], mapping=mapping)
                if ref not in row['refs']:
                    row['refs'].append(ref)
    if set(mappings) - {s['source_id'] for s in index['sources']}:
        raise ValueError('Transcript mapping contains a source absent from the supplied index')
    store.validate_inputs()
    if any(file_hash(p) != sha for p, sha in input_files.items()):
        raise ValueError('Transcript evidence changed during import; retry')
    if any(input_signature(prepared) != signature for prepared, signature in index['inputs'].items()):
        raise ValueError('Prepared transcript evidence changed during import; retry')
    snapshot = dict(schema=SCHEMA, queue_hash=store.queue_hash,
        rows=sorted(rows.values(), key=lambda r: (list(store.sources).index(r['source_id']), r['start_sec'],
                                                r['audio_stream'], r['end_sec'], r['id'])),
        coverage=coverage, unmapped_sources=unmapped,
        excluded_invalid_segments=index['summary'].get('invalid_transcript_segments', 0) + rejected,
        inputs=input_files,
        limitations='Rough recognized speech over prepared coverage only. A missing line does not establish silence; '
                     'search results are leads, not event or synchronization confidence.')
    TranscriptEvidence(store, snapshot)  # Validate before replacing a previous attachment.
    atomic_json(store.folder / 'transcript.json', snapshot)
    store.transcript = TranscriptEvidence(store, snapshot)
    return dict(lines=len(snapshot['rows']), sources=len(coverage), unmapped_sources=unmapped,
                excluded_invalid_segments=snapshot['excluded_invalid_segments'])


class TranscriptEvidence:
    def __init__(self, store, snapshot=None, load=True):
        self.store = store
        self.error = None
        path = store.folder / 'transcript.json'
        self.snapshot = snapshot if snapshot is not None else (read(path) if load and path.exists() else None)
        self.rows, self.by_id = [], {}
        self.searchable = []
        if self.snapshot is None:
            return
        if self.snapshot.get('schema') != SCHEMA or self.snapshot.get('queue_hash') != store.queue_hash:
            raise ValueError('Attached transcript belongs to a different queue')
        if (not isinstance(self.snapshot.get('rows'), list) or not isinstance(self.snapshot.get('coverage'), list) or
                not isinstance(self.snapshot.get('unmapped_sources'), list) or
                type(self.snapshot.get('excluded_invalid_segments')) is not int or self.snapshot['excluded_invalid_segments'] < 0 or
                not isinstance(self.snapshot.get('limitations'), str)):
            raise ValueError('Invalid attached transcript summary')
        for row in self.snapshot['rows']:
            sid, start, end, stream = (row.get(k) for k in ('source_id', 'start_sec', 'end_sec', 'audio_stream'))
            if (sid not in store.sources or not finite(start) or not finite(end) or
                    not 0 <= start < end <= store.sources[sid]['duration_sec'] or
                    type(stream) is not int or stream < 0 or not isinstance(row.get('text'), str) or
                    not isinstance(row.get('refs'), list) or any(not isinstance(ref, dict) for ref in row['refs']) or
                    not re.fullmatch(r'[0-9a-f]{64}', row.get('id', '')) or row['id'] in self.by_id):
                raise ValueError('Invalid attached transcript line')
            self.rows.append(row)
            self.by_id[row['id']] = row
        self.searchable = [' '.join(r['text'].casefold().split()) for r in self.rows]

    def summary(self):
        if self.error:
            return dict(status='error', error=self.error, coverage=[], lines=0)
        if self.snapshot is None:
            return dict(status='missing', coverage=[], lines=0,
                        limitations='No transcript attached. Reuse an existing literal speech index; no transcription runs here.')
        return {**{k: deepcopy(self.snapshot[k]) for k in
                   ('coverage', 'unmapped_sources', 'excluded_invalid_segments', 'limitations')},
                'status': 'ready', 'lines': len(self.rows)}

    def resolve(self, row, current_id=None):
        candidates = []
        for card in self.store.cards.values():
            for index, base in enumerate(card['views']):
                if base['source_id'] != row['source_id']:
                    continue
                view = self.store.context.view(card['id'], index)
                if view['preview_start_sec'] <= row['start_sec'] < view['preview_end_sec']:
                    candidates.append(dict(event_id=card['id'], view=index, source_sec=row['start_sec']))
        return next((c for c in candidates if c['event_id'] == current_id), candidates[0] if candidates else None)

    def search(self, query='', source_id=None, start=None, end=None, offset=0, limit=100, current_id=None):
        if not isinstance(query, str) or len(query) > 300:
            raise ValueError('Transcript query must be at most 300 characters')
        if source_id is not None and source_id not in self.store.sources:
            raise ValueError('Unknown transcript POV')
        if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 200:
            raise ValueError('Invalid transcript page')
        if (start is not None or end is not None) and (
                source_id is None or not finite(start) or not finite(end) or not 0 <= start < end):
            raise ValueError('Transcript window needs a source and valid bounds')
        query = ' '.join(query.casefold().split())
        matches = [r for r, text in zip(self.rows, self.searchable)
                   if (not query or query in text) and (source_id is None or r['source_id'] == source_id) and
                   (start is None or r['end_sec'] > start and r['start_sec'] < end)]
        hits = []
        for row in matches[offset:offset + limit]:
            source = self.store.sources[row['source_id']]
            hits.append(dict(row, label=source.get('label', source['id']), source=source['path'],
                             target=self.resolve(row, current_id)))
        return dict(hits=hits, total=len(matches), offset=offset, limit=limit,
                    more=offset + limit < len(matches), **self.summary())
