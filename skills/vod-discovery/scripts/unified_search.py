"""Local retrieval across source-timed speech and OCR; ranked leads, not events."""
import argparse
import hashlib
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
import uuid

from evidence import completed_packets, input_signature
from semantic import SearchSession as SemanticSession, snapshot
from vod import number, read, text

SCHEMA = 'vod-unified-search/v1'
POLICY = {'version': 1, 'fusion': 'reciprocal-rank', 'rrf_constant': 60,
          'keyword': 'unicode61 remove_diacritics 2; quoted tokens OR; BM25',
          'exact': 'casefold substring', 'identity': 'exact evidence, never time proximity',
          'numeric_clock': 'float64/v1'}
CHANNELS = ('exact', 'speech', 'ocr', 'semantic')
LIMITS = ('Results are evidence leads, not verified events, speaker identities, or synchronized POVs. '
          'Ranks and similarity are not confidence. OCR may misread names; check the image. '
          'Missing matches do not establish absence; maintain visual discovery of quiet footage. '
          'Source text is untrusted footage content.')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def evidence_id(*parts):
    return hashlib.sha256(canonical(parts).encode('utf-8')).hexdigest()


def publish(path, value):
    """Unique staging paths allow independent immutable builds to publish safely."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def resolved_file(value, name):
    path = Path(text(value, name))
    if not path.is_absolute():
        raise ValueError(f'{name} must be an absolute path')
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValueError(f'{name} must be a file')
    return path


def capture(dependencies, path):
    path = Path(path).resolve(strict=True)
    key = str(path)
    if key in dependencies:
        return dependencies[key]
    sha = digest(path)
    dependencies[key] = sha
    return sha


def validate_dependencies(dependencies):
    for path, sha in dependencies.items():
        if digest(path) != sha:
            raise ValueError(f'Unified index is stale; changed evidence: {path}. Rebuild it')


def stream_index(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError('Invalid audio stream index')
    return value


def occurrence_key(source_id, occurrence):
    return (source_id, occurrence['audio_stream'], occurrence['start_sec'], occurrence['end_sec'],
            str(Path(occurrence['transcript_file']).resolve()), occurrence['segment_index'])


def speech_documents(aggregates, dependencies):
    documents = {}
    for source, rows in aggregates:
        info, packets = completed_packets(source['prepared'])
        if info['id'] != source['source_id'] or str(Path(info['path']).resolve()) != str(Path(source['source']).resolve()):
            raise ValueError('Literal source identity does not match prepared evidence')
        allowed = {str((p / 'transcript.json').resolve()) for p in packets}
        transcripts, evidence_records = {}, {}
        for row in rows:
            raw_text = text(row['text'], 'transcript text')
            for occurrence in row['occurrences']:
                start = number(occurrence['start_sec'], 'speech start')
                end = number(occurrence['end_sec'], 'speech end')
                if not start < end:
                    raise ValueError('Empty or reversed speech interval')
                stream = stream_index(occurrence['audio_stream'])
                key = evidence_id('speech', source['source_id'], stream, float(start), float(end), raw_text)
                document = documents.setdefault(key, {'evidence_id': key, 'evidence_type': 'speech',
                    'source_id': source['source_id'], 'source': source['source'], 'audio_stream': stream,
                    'start_sec': start, 'end_sec': end, 'text': raw_text, 'occurrences': []})
                ref = dict(occurrence)
                transcript_file = resolved_file(ref['transcript_file'], 'transcript file')
                if str(transcript_file) not in allowed:
                    raise ValueError('Speech occurrence does not belong to its prepared source')
                if str(transcript_file) not in transcripts:
                    transcripts[str(transcript_file)] = read(transcript_file)['segments']
                index = ref['segment_index']
                if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(transcripts[str(transcript_file)]):
                    raise ValueError('Invalid raw transcript segment reference')
                segment = transcripts[str(transcript_file)][index]
                if (segment['start'] != start or segment['end'] != end or segment['audio_stream'] != stream
                        or text(segment['text'], 'raw transcript text').strip() != raw_text):
                    raise ValueError('Speech occurrence does not match its exact raw transcript segment')
                ref['raw_text'] = segment['text']
                ref['transcript_sha256'] = capture(dependencies, transcript_file)
                evidence_file = resolved_file(ref['evidence_file'], 'evidence file')
                if evidence_file != transcript_file.parent / 'evidence.json':
                    raise ValueError('Speech evidence file must accompany its exact raw transcript')
                if str(evidence_file) not in evidence_records:
                    evidence_records[str(evidence_file)] = read(evidence_file)
                evidence = evidence_records[str(evidence_file)]
                matched = [s for s in evidence['valid_segments'] if s['segment_index'] == index]
                if (evidence['source_id'] != source['source_id'] or len(matched) != 1
                        or any(matched[0][k] != v for k, v in
                               (('start', start), ('end', end), ('audio_stream', stream), ('text', raw_text)))):
                    raise ValueError('Joined speech evidence does not match its exact raw transcript segment')
                ref['evidence_sha256'] = capture(dependencies, evidence_file)
                if ref not in document['occurrences']:
                    document['occurrences'].append(ref)
    return list(documents.values())


def mapped_frames(folder, source_id, source, duration, dependencies, detail=False):
    folder = Path(folder).resolve(strict=True)
    packet_path, map_path = folder / 'packet.json', folder / 'frames.json'
    capture(dependencies, packet_path); capture(dependencies, map_path)
    packet = read(packet_path)
    if detail:
        if str(Path(packet['source']).resolve()) != str(Path(source).resolve()):
            raise ValueError('Detail source path does not match an indexed source')
    elif packet['source_id'] != source_id:
        raise ValueError('Frame map source identity does not match the indexed source')
    start, end = number(packet['start_sec'], 'packet start'), number(packet['end_sec'], 'packet end')
    if not 0 <= start < end <= duration:
        raise ValueError('Frame map interval outside indexed source')
    frames = read(map_path)['frames']
    result = []
    for i, frame in enumerate(frames):
        timestamp = number(frame['timestamp_sec'], 'frame timestamp')
        name = text(frame['file'], 'frame filename')
        if Path(name).name != name or not start <= timestamp <= end:
            raise ValueError('Invalid frame filename or source timestamp')
        image = (folder / 'frames' / name).resolve(strict=True)
        if image.parent != (folder / 'frames').resolve() or not image.is_file():
            raise ValueError('Frame image must belong to its mapped frame folder')
        result.append(((source_id, str(image), timestamp),
                       {'frame_map': str(map_path), 'frame_index': i, 'packet_file': str(packet_path)}))
    return result


def ocr_documents(index, reports, detail_folders, source_map, dependencies):
    if not reports:
        if detail_folders or source_map:
            raise ValueError('OCR source/detail mappings require an OCR report')
        return [], []
    sources = {s['source_id']: s for s in index['sources']}
    if len(sources) != len(index['sources']):
        raise ValueError('Duplicate indexed source IDs')
    aliases = {}
    if source_map:
        capture(dependencies, source_map)
        mapping = read(source_map)
        if mapping.get('schema') != 'vod-ocr-source-map/v1':
            raise ValueError('Unsupported OCR source map')
        for entry in mapping['sources']:
            alias, sid = text(entry['ocr_source_id'], 'OCR alias'), text(entry['source_id'], 'source ID')
            if not Path(text(entry['source'], 'OCR mapped source path')).is_absolute():
                raise ValueError('OCR mapped source must be an absolute indexed source path')
            if alias in aliases or sid not in sources or str(Path(entry['source']).resolve()) != str(Path(sources[sid]['source']).resolve()):
                raise ValueError('OCR source alias must identify one exact indexed source path')
            if alias in sources and alias != sid:
                raise ValueError('OCR source alias cannot override another indexed source ID')
            aliases[alias] = sid
    maps, coverage = {}, []
    durations = {}
    for sid, source in sources.items():
        info, packets = completed_packets(source['prepared'])
        durations[sid] = number(info['duration_sec'], 'source duration', .001)
        for attempt in packets:
            for key, reference in mapped_frames(attempt, sid, source['source'], durations[sid], dependencies):
                maps.setdefault(key, []).append(reference)
    for folder in detail_folders:
        packet = read(Path(folder) / 'packet.json')
        matched = [s for s in sources.values() if str(Path(packet['source']).resolve()) == str(Path(s['source']).resolve())]
        if len(matched) != 1:
            raise ValueError('Detail folder must match exactly one indexed source path')
        source = matched[0]
        for key, reference in mapped_frames(folder, source['source_id'], source['source'], durations[source['source_id']], dependencies, True):
            maps.setdefault(key, []).append(reference)
    documents = {}
    for report_file in reports:
        report_file = Path(report_file).resolve(strict=True)
        report_sha = capture(dependencies, report_file)
        report = read(report_file)
        if report.get('schema') != 'vod-frame-ocr/v1':
            raise ValueError('Unsupported OCR report; expected vod-frame-ocr/v1')
        manifest_file = resolved_file(report['manifest'], 'OCR input manifest')
        if capture(dependencies, manifest_file) != report['manifest_sha256']:
            raise ValueError('OCR input manifest changed; regenerate OCR evidence')
        manifest = read(manifest_file)
        if not isinstance(manifest, list) or not manifest:
            raise ValueError('OCR input manifest must contain source-timed frames')
        def frame_key(frame):
            alias = text(frame['source_id'], 'OCR source ID')
            sid = aliases.get(alias, alias)
            if sid not in sources:
                raise ValueError(f'Unknown OCR source ID: {alias}; supply an explicit --source-map')
            image = resolved_file(frame['file'], 'OCR image')
            timestamp = number(frame['timestamp_sec'], 'OCR source timestamp')
            key = (sid, str(image), timestamp)
            if key not in maps:
                raise ValueError('OCR image/source timestamp is not in a prepared or explicit detail frame map')
            return key
        manifest_keys = [frame_key(frame) for frame in manifest]
        report_keys = [frame_key(frame) for frame in report['frames']]
        if (len(set(manifest_keys)) != len(manifest_keys) or len(set(report_keys)) != len(report_keys)
                or set(manifest_keys) != set(report_keys)):
            raise ValueError('OCR report frames do not match its input manifest exactly')
        indexed = 0
        for position, (frame, key) in enumerate(zip(report['frames'], report_keys)):
            sid, image, timestamp = key
            sha = capture(dependencies, image)
            if sha != frame['image_sha256']:
                raise ValueError('OCR image changed; regenerate OCR evidence')
            raw_text = frame['text']
            if not isinstance(raw_text, str):
                raise ValueError('OCR text must be a string')
            if not raw_text.strip():
                continue
            indexed += 1
            identity = evidence_id('visible_text', sid, image, float(timestamp), raw_text)
            document = documents.setdefault(identity, {'evidence_id': identity, 'evidence_type': 'visible_text',
                'source_id': sid, 'source': sources[sid]['source'], 'timestamp_sec': timestamp,
                'start_sec': timestamp, 'end_sec': timestamp, 'text': raw_text, 'file': image,
                'image_sha256': sha, 'frame_refs': maps[key], 'ocr_refs': []})
            reference = {'report_file': str(report_file), 'report_sha256': report_sha, 'frame_index': position,
                         'manifest_file': str(manifest_file), 'ocr_source_id': frame['source_id'],
                         'engine': report.get('engine'), 'language': report.get('language')}
            if frame['source_id'] in aliases:
                reference['source_map_file'] = str(Path(source_map).resolve())
                reference['source_map_sha256'] = dependencies[reference['source_map_file']]
            if reference not in document['ocr_refs']:
                document['ocr_refs'].append(reference)
        coverage.append({'report_file': str(report_file), 'frames_processed': len(report_keys),
                         'nonempty_text_frames': indexed, 'source_ids': sorted({k[0] for k in report_keys})})
    return list(documents.values()), coverage


def semantic_binding(folder, literal_folder, literal_hashes, dependencies):
    folder = Path(folder).resolve(strict=True)
    pointer = folder / 'semantic.json'
    capture(dependencies, pointer)
    manifest = read(pointer)
    if (manifest.get('schema') != 'vod-semantic/v1'
            or Path(manifest['literal_index']).resolve() != Path(literal_folder).resolve()
            or manifest['inputs'] != literal_hashes):
        raise ValueError('Semantic index must reference this exact current literal index')
    build = (folder / manifest['build']).resolve(strict=True)
    if build.parent != folder or set(manifest['artifacts']) != {'passages.json', 'vectors.npy'}:
        raise ValueError('Invalid semantic artifact snapshot')
    for name, sha in manifest['artifacts'].items():
        if capture(dependencies, build / name) != sha:
            raise ValueError('Semantic artifacts changed; rebuild semantic index')
    return str(folder)


def build(literal_folder, out, ocr_reports=(), detail_folders=(), source_map=None, semantic_folder=None):
    literal_folder, out = Path(literal_folder).resolve(strict=True), Path(out).resolve()
    index, hashes, aggregates = snapshot(literal_folder)
    dependencies = {}
    for name in hashes:
        capture(dependencies, literal_folder / name)
    documents = speech_documents(aggregates, dependencies)
    ocr, ocr_coverage = ocr_documents(index, ocr_reports, detail_folders, source_map, dependencies)
    documents.extend(ocr)
    semantic_folder = semantic_binding(semantic_folder, literal_folder, hashes, dependencies) if semantic_folder else None
    manifest = {'schema': SCHEMA, 'policy': POLICY, 'literal_index': str(literal_folder),
                'prepared_inputs': index['inputs'], 'dependencies': dependencies, 'semantic_index': semantic_folder,
                'coverage': {'speech': index['sources'], 'ocr': ocr_coverage,
                             'semantic': {'status': 'available' if semantic_folder else 'not_indexed'}},
                'excluded_invalid_segments': index['summary']['invalid_transcript_segments'],
                'documents': len(documents)}
    pointer = out / 'unified.json'
    if pointer.exists():
        old = read(pointer)
        if all(old.get(k) == v for k, v in manifest.items()):
            try:
                database = checked_database(out, old)
            except (OSError, ValueError):
                pass  # A corrupt generated snapshot can be rebuilt from evidence.
            else:
                return {'documents': len(documents), 'reused': True, 'database': str(database)}
    folder = out / ('build-' + uuid.uuid4().hex[:12]); folder.mkdir(parents=True)
    database = folder / 'evidence.db'
    with closing(sqlite3.connect(database)) as connection:
        connection.execute('CREATE TABLE documents (id INTEGER PRIMARY KEY, evidence_id TEXT UNIQUE, evidence_type TEXT, body TEXT)')
        try:
            connection.execute("CREATE VIRTUAL TABLE terms USING fts5(text, tokenize='unicode61 remove_diacritics 2')")
        except sqlite3.OperationalError as exc:
            raise RuntimeError('This Python SQLite build lacks FTS5; use an FTS5-enabled local Python') from exc
        for i, document in enumerate(sorted(documents, key=lambda d: d['evidence_id']), 1):
            connection.execute('INSERT INTO documents VALUES (?, ?, ?, ?)', (i, document['evidence_id'], document['evidence_type'], canonical(document)))
            connection.execute('INSERT INTO terms (rowid, text) VALUES (?, ?)', (i, document['text']))
        connection.commit()
    validate_dependencies(dependencies)
    if snapshot(literal_folder)[1] != hashes:
        raise ValueError('Literal evidence changed during indexing; previous snapshot preserved')
    manifest.update(build=folder.name, database_sha256=digest(database))
    publish(pointer, manifest)
    return {'documents': len(documents), 'speech_documents': len(documents) - len(ocr),
            'ocr_documents': len(ocr), 'reused': False, 'database': str(database)}


def checked_database(out, manifest):
    folder = (Path(out) / manifest['build']).resolve(strict=True)
    if folder.parent != Path(out).resolve():
        raise ValueError('Invalid unified build folder')
    database = folder / 'evidence.db'
    if digest(database) != manifest['database_sha256']:
        raise ValueError('Unified database changed; rebuild the index')
    return database


def validate_snapshot(out):
    out = Path(out).resolve(strict=True)
    manifest = read(out / 'unified.json')
    if manifest.get('schema') != SCHEMA or manifest.get('policy') != POLICY:
        raise ValueError('Unsupported unified index or retrieval policy; rebuild it')
    validate_manifest(out, manifest)
    return manifest, checked_database(out, manifest)


def validate_manifest(out, manifest):
    """Validate the captured snapshot, including after a long semantic query."""
    for prepared, signature in manifest['prepared_inputs'].items():
        if input_signature(prepared) != signature:
            raise ValueError('Unified index is stale; prepared evidence changed. Rebuild it')
    validate_dependencies(manifest['dependencies'])
    checked_database(out, manifest)


def bounded_limit(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 200:
        raise ValueError(f'{name} must be between 1 and 200')
    return value


def lexical(connection, query, channel, candidate_limit):
    kind = {'speech': 'speech', 'ocr': 'visible_text'}.get(channel)
    if channel == 'exact':
        connection.create_function('contains_casefold', 2, lambda body, q: q.casefold() in json.loads(body)['text'].casefold())
        predicate, parameters = 'contains_casefold(body, ?)', (query,)
        count = connection.execute(f'SELECT count(*) FROM documents WHERE {predicate}', parameters).fetchone()[0]
        rows = connection.execute(f'SELECT body FROM documents WHERE {predicate} ORDER BY evidence_id LIMIT ?', (*parameters, candidate_limit)).fetchall()
        hits = [(json.loads(row[0]), {}) for row in rows]
    else:
        tokens = list(dict.fromkeys(re.findall(r'\w+', query, flags=re.UNICODE)))
        if not tokens:
            return [], {'matches': 0, 'more_available': False, 'at_limit': False, 'candidate_limit': candidate_limit}
        expression = ' OR '.join('"' + token.replace('"', '""') + '"' for token in tokens)
        predicate = 'terms MATCH ? AND documents.evidence_type = ?'
        parameters = (expression, kind)
        count = connection.execute(f'SELECT count(*) FROM terms JOIN documents ON documents.id=terms.rowid WHERE {predicate}', parameters).fetchone()[0]
        rows = connection.execute(f'SELECT documents.body, bm25(terms) AS score FROM terms JOIN documents ON documents.id=terms.rowid WHERE {predicate} ORDER BY score, documents.evidence_id LIMIT ?', (*parameters, candidate_limit)).fetchall()
        hits = [(json.loads(row[0]), {'bm25': row[1]}) for row in rows]
    return hits, {'matches': count, 'more_available': count > candidate_limit,
                  'at_limit': count >= candidate_limit, 'candidate_limit': candidate_limit}


class SearchSession:
    """Reuse one optional semantic model; validate evidence on every query."""
    def __init__(self, out, model_folder=None, semantic_session_factory=SemanticSession):
        self.out, self.model_folder = Path(out).resolve(), model_folder
        self.semantic_session_factory = semantic_session_factory
        self.semantic_session, self.semantic_index = None, None

    def search(self, query, limit=20, candidate_limit=100, channels=None):
        query = text(query, 'search query').strip()
        if len(query) > 16384:
            raise ValueError('Search query exceeds 16384 characters')
        bounded_limit(limit, 'Search limit'); bounded_limit(candidate_limit, 'Candidate limit')
        if candidate_limit < limit:
            raise ValueError('Candidate limit must be at least the search limit')
        manifest, database = validate_snapshot(self.out)
        available = {'exact', 'speech'}
        if manifest['coverage']['ocr']: available.add('ocr')
        if manifest['semantic_index']: available.add('semantic')
        requested = list(channels) if channels is not None else [c for c in CHANNELS if c in available]
        if not requested or len(set(requested)) != len(requested) or set(requested) - set(CHANNELS):
            raise ValueError('Choose distinct channels from exact, speech, ocr, semantic')
        missing = set(requested) - available
        if missing:
            raise ValueError('Requested channels are not indexed: ' + ', '.join(sorted(missing)))
        if 'semantic' in requested and not self.model_folder:
            raise ValueError('The indexed semantic channel requires --model-dir; choose lexical channels explicitly to omit it')
        rankings, summaries = {}, {}
        with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)) as connection:
            connection.execute('PRAGMA query_only=ON')
            for channel in requested:
                if channel != 'semantic':
                    rankings[channel], summaries[channel] = lexical(connection, query, channel, candidate_limit)
            if 'semantic' in requested:
                if self.semantic_session is None:
                    self.semantic_index = manifest['semantic_index']
                    self.semantic_session = self.semantic_session_factory(self.semantic_index, self.model_folder)
                elif self.semantic_index != manifest['semantic_index']:
                    raise ValueError('Semantic index changed while search session was running; restart it')
                result = self.semantic_session.search(query, candidate_limit)
                exact_occurrences = {}
                for row, in connection.execute("SELECT body FROM documents WHERE evidence_type='speech'"):
                    doc = json.loads(row)
                    for occurrence in doc['occurrences']:
                        key = occurrence_key(doc['source_id'], occurrence)
                        previous = exact_occurrences.get(key)
                        if previous is not None and previous['evidence_id'] != doc['evidence_id']:
                            raise ValueError('Ambiguous exact transcript occurrence')
                        exact_occurrences[key] = doc
                hits, seen = [], set()
                for passage_rank, hit in enumerate(result['hits'], 1):
                    for segment in hit['segments']:
                        for occurrence in segment['occurrences']:
                            key = occurrence_key(hit['source_id'], occurrence)
                            if key not in exact_occurrences:
                                raise ValueError('Semantic result lacks an exact current transcript occurrence')
                            doc = exact_occurrences[key]
                            if doc['evidence_id'] not in seen:
                                seen.add(doc['evidence_id'])
                                hits.append((doc, {'similarity': hit['similarity'], 'passage_rank': passage_rank,
                                    'passage_kind': hit['passage_kind'], 'passage_start_sec': hit['start_sec'],
                                    'passage_end_sec': hit['end_sec'], 'matched_text': segment['text']}))
                rankings['semantic'] = hits
                summaries['semantic'] = {k: result[k] for k in ('distinct_results', 'overlapping_results_grouped', 'more_available', 'indexed_passages')}
                summaries['semantic'].update(candidate_limit=candidate_limit, returned_passages=len(result['hits']),
                                             expanded_evidence=len(hits), at_limit=len(result['hits']) >= candidate_limit)
        combined = {}
        for channel, hits in rankings.items():
            for position, (doc, scores) in enumerate(hits, 1):
                # Context passages may expand to several exact segments. Their
                # semantic rank remains the passage rank; no time grouping occurs.
                rank = scores.get('passage_rank', position)
                result = combined.setdefault(doc['evidence_id'], {**doc, 'channels': {}, 'rrf_score': 0.})
                result['channels'][channel] = {'rank': rank, **scores}
                result['rrf_score'] += 1 / (POLICY['rrf_constant'] + rank)
        hits = sorted(combined.values(), key=lambda h: (-h['rrf_score'], h['evidence_id']))
        validate_manifest(self.out, manifest)
        if read(self.out / 'unified.json') != manifest:
            raise ValueError('Unified index changed during search; retry against the current snapshot')
        return {'schema': 'vod-unified-results/v1', 'query': query, 'hits': hits[:limit], 'limit': limit,
                'candidate_limit': candidate_limit, 'distinct_retrieved_evidence': len(hits),
                'more_available': len(hits) > limit or any(s['more_available'] for s in summaries.values()),
                'at_limit': len(hits) >= limit, 'channels': {c: {'status': 'searched' if c in requested else
                    ('not_requested' if c in available else 'not_indexed'), **summaries.get(c, {})} for c in CHANNELS},
                'coverage': manifest['coverage'], 'excluded_invalid_segments': manifest['excluded_invalid_segments'],
                'fusion': POLICY, 'limitations': LIMITS}


def search(out, query, limit=20, candidate_limit=100, model_folder=None, channels=None):
    return SearchSession(out, model_folder).search(query, limit, candidate_limit, channels)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('index')
    p.add_argument('--literal-index', required=True); p.add_argument('--out', required=True)
    p.add_argument('--ocr-report', action='append', default=[])
    p.add_argument('--detail-folder', action='append', default=[])
    p.add_argument('--source-map', help='Explicit vod-ocr-source-map/v1 aliases tied to exact source paths')
    p.add_argument('--semantic-index')
    for command in ('search', 'search-many'):
        p = commands.add_parser(command); p.add_argument('--index', required=True)
        p.add_argument('--model-dir'); p.add_argument('--limit', type=int, default=20)
        p.add_argument('--candidate-limit', type=int, default=100)
        p.add_argument('--channels', nargs='+', choices=CHANNELS)
        if command == 'search': p.add_argument('--query', required=True); p.add_argument('--out')
        else: p.add_argument('--queries', required=True); p.add_argument('--out', required=True)
    args = parser.parse_args()
    if args.command == 'index':
        result = build(args.literal_index, args.out, args.ocr_report, args.detail_folder, args.source_map, args.semantic_index)
    else:
        if args.out and Path(args.out).exists(): raise ValueError('Use a fresh output file')
        session = SearchSession(args.index, args.model_dir)
        if args.command == 'search-many':
            queries = read(args.queries)
            if not isinstance(queries, list) or not queries or any(not isinstance(q, str) or not q.strip() for q in queries):
                raise ValueError('Queries must be a nonempty JSON array of nonempty strings')
            result = {'schema': 'vod-unified-batch/v1', 'results': [session.search(q, args.limit, args.candidate_limit, args.channels) for q in queries]}
        else:
            result = session.search(args.query, args.limit, args.candidate_limit, args.channels)
        if args.out: publish(args.out, result)
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
