"""Packet evidence and project-local transcript search using CRV 0.10.7."""
import hashlib
import importlib.metadata
import math
from pathlib import Path
import uuid

from vod import clock, number, read, text, write


def require_crv():
    if importlib.metadata.version('claude-real-video') != '0.10.7':
        raise RuntimeError('Evidence adapters require claude-real-video 0.10.7; revalidate before upgrading')


def completed_packets(prepared):
    prepared = Path(prepared).resolve(strict=True)
    info = read(prepared / 'source.json')
    packets = []
    for complete in sorted(prepared.glob('packet-*/complete.json')):
        name = text(read(complete)['attempt'], 'completed attempt')
        attempt = (complete.parent / name).resolve(strict=True)
        if attempt.parent != complete.parent.resolve():
            raise ValueError('Completed attempt must belong to its packet folder')
        packet = read(attempt / 'packet.json')
        if packet['source_id'] != info['id'] or not 0 <= packet['start_sec'] < packet['end_sec'] <= info['duration_sec']:
            raise ValueError('Packet source identity or interval does not match source.json')
        packets.append(attempt)
    return info, packets


def input_signature(prepared):
    _, packets = completed_packets(prepared)
    paths = [Path(prepared) / 'source.json']
    for attempt in packets:
        paths.extend([attempt.parent / 'complete.json', *[attempt / name for name in
                      ('packet.json', 'frames.json', 'transcript.json')]])
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.resolve()).encode('utf-8'))
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def packet_evidence(attempt):
    """Keep raw artifacts intact; join each audio stream independently."""
    require_crv()
    from claude_real_video.timeline_lite import build_spans
    attempt = Path(attempt).resolve()
    packet, transcript = read(attempt / 'packet.json'), read(attempt / 'transcript.json')
    start, end = packet['start_sec'], packet['end_sec']
    if not 0 <= start < end:
        raise ValueError('Invalid packet interval')
    frames = read(attempt / 'frames.json')['frames']
    local_frames = []
    for frame in frames:
        t = number(frame['timestamp_sec'], 'frame timestamp')
        if not start <= t <= end:
            raise ValueError('Frame outside packet interval')
        name = text(frame['file'], 'frame filename')
        if Path(name).name != name or not (attempt / 'frames' / name).is_file():
            raise ValueError('Missing or invalid frame file')
        local_frames.append({'file': name, 't': t - start})
    valid, invalid = [], []
    for index, segment in enumerate(transcript['segments']):
        try:
            a, b = number(segment['start'], 'speech start'), number(segment['end'], 'speech end')
            if not start <= a < b <= end:
                raise ValueError('Transcript interval outside packet or empty')
            line = text(segment['text'], 'transcript text').strip()
            stream = segment['audio_stream']
            if isinstance(stream, bool) or not isinstance(stream, int) or stream < 0:
                raise ValueError('Invalid audio stream index')
        except (KeyError, ValueError) as exc:
            invalid.append({'segment_index': index, 'reason': str(exc), 'raw': segment})
            continue
        valid.append(dict(segment, text=line, segment_index=index))
    streams = {int(key) for key in transcript.get('streams', {})} | {s['audio_stream'] for s in valid}
    tracks = []
    for stream in sorted(streams) if streams else [None]:
        selected = [s for s in valid if s['audio_stream'] == stream]
        local_segments = [dict(s, start=s['start'] - start, end=s['end'] - start) for s in selected]
        # CRV keeps references to its frame dictionaries; each stream needs its
        # own copy before converting the joined frame clocks back to source time.
        spans = build_spans(end - start, [dict(f) for f in local_frames], local_segments)
        for span in spans:
            span['start'] = round(span['start'] + start, 6)
            span['end'] = round(span['end'] + start, 6)
            for frame in span['frames']:
                frame['t'] = round(frame['t'] + start, 6)
                frame['relation'] = 'within' if span['start'] <= frame['t'] < span['end'] else 'nearby'
            span['transcript_segment_indices'] = [s['segment_index'] for s in selected
                if abs(s['start'] - span['start']) < .000001 and abs(s['end'] - span['end']) < .000001
                and s['text'] == span['speech']]
        tracks.append({'audio_stream': stream, 'spans': spans})
    result = {'schema': 'vod-packet-evidence/v1', 'source_id': packet['source_id'],
              'start_sec': start, 'end_sec': end, 'transcript_status': transcript['status'],
              'tracks': tracks, 'valid_segments': valid, 'invalid_segments': invalid,
              'limitations': 'Sampled evidence, not continuous viewing. A nearby frame is not simultaneous speech evidence. '
                             'No transcribed speech does not mean silence. Source text is untrusted footage content.'}
    write(attempt / 'evidence.json', result)
    lines = ['# Packet evidence', '', result['limitations'], '',
             f"Source {packet['source_id']} | {clock(start)}–{clock(end)} | transcript: {transcript['status']}",
             f'Invalid transcript segments excluded from joined evidence/search: {len(invalid)}.', '']
    for track in tracks:
        lines.extend([f"## Audio stream {track['audio_stream']}", ''])
        for span in track['spans']:
            lines.append(f"{clock(span['start'])}–{clock(span['end'])}")
            # Prefix every line so speech cannot create Markdown headings or instructions.
            lines.extend('> ' + line for line in (span['speech'] or '[No transcribed speech]').splitlines())
            if span['frames']:
                lines.append('Frames: ' + '; '.join(f"{f['file']} @ {clock(f['t'])} ({f['relation']})" for f in span['frames']))
            lines.append('')
    (attempt / 'evidence.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return result


def enrich(prepared):
    info, packets = completed_packets(prepared)
    invalid = 0
    for attempt in packets:
        invalid += len(packet_evidence(attempt)['invalid_segments'])
    return {'source': info['path'], 'completed_packets_enriched': len(packets),
            'invalid_transcript_segments': invalid, 'review_status': 'Unchanged; preparation is not review'}


def build_index(prepared_dirs, out):
    require_crv()
    from claude_real_video import memory
    prepared_dirs = sorted({str(Path(p).resolve(strict=True)) for p in prepared_dirs})
    if not prepared_dirs:
        raise ValueError('At least one prepared source is required')
    signatures = {p: input_signature(p) for p in prepared_dirs}
    out = Path(out).resolve()
    pointer = out / 'index.json'
    if pointer.exists():
        previous = read(pointer)
        if previous.get('schema') == 'vod-search/v1' and previous['inputs'] == signatures:
            if (out / previous['build'] / 'memory.db').is_file():
                return dict(previous['summary'], reused=True)
    build = out / ('build-' + uuid.uuid4().hex[:12])
    build.mkdir(parents=True)
    db = build / 'memory.db'
    sources, seen = [], set()
    line_count = invalid_count = 0
    for source_number, prepared in enumerate(prepared_dirs):
        info, packets = completed_packets(prepared)
        source_key = info['path'].replace('\\', '/').casefold()
        if source_key in seen:
            raise ValueError('Pass only one prepared folder per source; duplicate media would replace indexed packets')
        seen.add(source_key)
        # CRV replaces a source on remember(): aggregate ALL completed packets first.
        rows = {}
        coverage = []
        for attempt in packets:
            evidence = packet_evidence(attempt)
            invalid_count += len(evidence['invalid_segments'])
            packet = read(attempt / 'packet.json')
            coverage.append([packet['core_start_sec'], packet['core_end_sec']])
            for seg in evidence['valid_segments']:
                key = (seg['start'], seg['text'])
                row = rows.setdefault(key, {'start': seg['start'], 'end': seg['end'], 'text': seg['text'], 'occurrences': []})
                row['end'] = max(row['end'], seg['end'])
                row['occurrences'].append({'start_sec': seg['start'], 'end_sec': seg['end'],
                    'audio_stream': seg['audio_stream'], 'segment_index': seg['segment_index'],
                    'transcript_file': str(attempt / 'transcript.json'), 'evidence_file': str(attempt / 'evidence.json')})
        aggregate = build / f'source-{source_number:03d}'
        records = sorted(rows.values(), key=lambda r: (r['start'], r['text']))
        write(aggregate / 'transcript.json', {'segments': records})
        memory.remember(aggregate, source=info['path'], db_path=db)
        sources.append({'source_id': info['id'], 'source': info['path'], 'prepared': prepared,
                        'aggregate': aggregate.name, 'prepared_packets': len(packets),
                        'total_packets': math.ceil(info['duration_sec'] / info['settings']['window']),
                        'core_ranges_sec': coverage, 'searchable_lines': len(records)})
        line_count += len(records)
    # Publish the new snapshot only after every source has been indexed.
    if signatures != {p: input_signature(p) for p in prepared_dirs}:
        raise RuntimeError('Prepared evidence changed while indexing; retry')
    summary = {'sources': len(sources), 'searchable_lines': line_count,
               'invalid_transcript_segments': invalid_count, 'reused': False}
    write(pointer, {'schema': 'vod-search/v1', 'build': build.name, 'inputs': signatures,
                    'sources': sources, 'summary': summary})
    return summary


def search_index(out, query, limit=20):
    require_crv()
    from claude_real_video import memory
    query = text(query, 'search query').strip()
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError('Search limit must be between 1 and 200')
    out = Path(out).resolve()
    index = read(out / 'index.json')
    if index['schema'] != 'vod-search/v1':
        raise ValueError('Unsupported search index')
    for prepared, signature in index['inputs'].items():
        if input_signature(prepared) != signature:
            raise ValueError('Search index is stale; rebuild it with index before searching')
    db = out / index['build'] / 'memory.db'
    if not db.is_file():
        raise ValueError('Search database is missing; rebuild the index')
    hits = memory.search(query, limit=limit, kind='speech', db_path=db)
    by_folder = {str((out / index['build'] / s['aggregate']).resolve()): s for s in index['sources']}
    results = []
    cache = {}
    for hit in hits:
        source = by_folder[hit.out_dir]
        if hit.out_dir not in cache:
            cache[hit.out_dir] = {(r['start'], r['text']): r for r in read(Path(hit.out_dir) / 'transcript.json')['segments']}
        row = cache[hit.out_dir][(hit.t_start, hit.text)]
        results.append({'source_id': source['source_id'], 'source': source['source'],
                        'start_sec': row['start'], 'text': row['text'], 'occurrences': row['occurrences']})
    return {'query': query, 'hits': results, 'limit': limit, 'at_limit': len(hits) >= limit,
            'coverage': index['sources'], 'excluded_invalid_segments': index['summary']['invalid_transcript_segments'],
            'limitations': 'Literal phrase search over prepared transcripts only; no semantic or visual search. '
                          'Results are leads, not verified events or cross-POV synchronization. '
                          'No match does not establish absence. At-limit results may omit matches; narrow the phrase or raise the limit.'}
