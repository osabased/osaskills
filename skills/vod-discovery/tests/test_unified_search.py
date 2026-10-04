from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evidence import build_index
from semantic import passages, snapshot
from unified_search import SearchSession, build, digest, search
from vod import read, write


class UnifiedSearch(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.literal = self.root / 'literal'
        self.out = self.root / 'unified'
        self.sources, self.attempts = {}, {}
        self.source('alice', [(10, 12, 'Josh offers a truce', 1),
                              (10, 12, 'Josh offers a truce', 2),
                              (20, 22, 'Josh offers a truce', 1),
                              (24, 26, '  Let us stop fighting  ', 1)])
        self.source('bob', [(90, 92, 'Josh offers a truce', 1)])
        build_index(list(self.sources.values()), self.literal)

    def tearDown(self):
        self.temp.cleanup()

    def source(self, name, segments):
        source = self.root / name
        write(source / 'source.json', {'id': name, 'path': str(self.root / (name + '.mp4')),
              'duration_sec': 300, 'settings': {'window': 300}})
        attempt = source / 'packet-0000' / 'attempt-test'
        write(attempt / 'packet.json', {'source_id': name, 'start_sec': 0, 'end_sec': 300,
              'core_start_sec': 0, 'core_end_sec': 300})
        write(attempt / 'transcript.json', {'status': 'transcribed', 'streams': {'1': 'transcribed', '2': 'transcribed'},
              'segments': [{'start': a, 'end': b, 'text': line, 'audio_stream': stream} for a, b, line, stream in segments]})
        image = attempt / 'frames' / 'raw_00000.jpg'; image.parent.mkdir(parents=True)
        image.write_bytes(b'image fixture ' + name.encode())
        write(attempt / 'frames.json', {'frames': [{'file': image.name, 'timestamp_sec': 10}]})
        write(attempt.parent / 'complete.json', {'attempt': attempt.name})
        self.sources[name], self.attempts[name] = source, attempt

    def ocr(self, source_id='alice', timestamp=10, image=None, label='Josh: truce?', empty=False):
        image = image or self.attempts['alice'] / 'frames' / 'raw_00000.jpg'
        manifest = self.root / 'ocr-input.json'
        item = {'source_id': source_id, 'timestamp_sec': timestamp, 'file': str(image.resolve())}
        write(manifest, [item])
        report = self.root / 'ocr-report.json'
        write(report, {'schema': 'vod-frame-ocr/v1', 'engine': 'fixture', 'language': 'en-US',
              'manifest': str(manifest), 'manifest_sha256': digest(manifest),
              'frames': [{**item, 'image_sha256': digest(image), 'text': '' if empty else label,
                          'width': 100, 'height': 100, 'lines': []}]})
        return report

    def semantic(self):
        folder = self.root / 'semantic'; data = folder / 'build-fixture'
        index, hashes, aggregates = snapshot(self.literal)
        docs = passages(aggregates, lambda value: len(value.split()))
        write(data / 'passages.json', docs)
        (data / 'vectors.npy').write_bytes(b'fake matrix; mocked search does not load it')
        write(folder / 'semantic.json', {'schema': 'vod-semantic/v1', 'literal_index': str(self.literal),
              'inputs': hashes, 'build': data.name, 'artifacts': {name: digest(data / name)
              for name in ('passages.json', 'vectors.npy')}})
        hit = next(d for d in docs if d['text'] == 'Let us stop fighting')
        return folder, hit

    def test_speech_ocr_and_exact_rank_without_merging_sources_streams_or_repeats(self):
        report = self.ocr()
        self.assertEqual(build(self.literal, self.out, [report])['documents'], 6)
        result = search(self.out, 'truce')
        self.assertEqual(len(result['hits']), 5)
        speech = [h for h in result['hits'] if h['evidence_type'] == 'speech']
        self.assertEqual({(h['source_id'], h['audio_stream'], h['start_sec']) for h in speech},
                         {('alice', 1, 10), ('alice', 2, 10), ('alice', 1, 20), ('bob', 1, 90)})
        visible = next(h for h in result['hits'] if h['evidence_type'] == 'visible_text')
        self.assertEqual(visible['text'], 'Josh: truce?')
        self.assertEqual(visible['timestamp_sec'], 10)
        self.assertEqual(visible['ocr_refs'][0]['report_file'], str(report))
        self.assertIn('ocr', visible['channels']); self.assertNotIn('speech', visible['channels'])
        self.assertEqual(visible['image_sha256'], digest(visible['file']))
        for hit in speech:
            self.assertEqual(set(hit['channels']), {'exact', 'speech'})
            self.assertAlmostEqual(hit['rrf_score'], sum(1 / (60 + v['rank']) for v in hit['channels'].values()))
            self.assertEqual(hit['occurrences'][0]['transcript_sha256'], digest(hit['occurrences'][0]['transcript_file']))

    def test_exact_phrase_punctuation_and_unicode_are_literal_not_fts_syntax(self):
        line = 'JÖSH 100% boss_ "down" OR NEAR(x)'
        report = self.ocr(label=line)
        build(self.literal, self.out, [report])
        for query in ('jösh 100%', '"down" OR', 'NEAR(x)'):
            result = search(self.out, query, channels=['exact'])
            self.assertEqual([h['text'] for h in result['hits']], [line])
        self.assertEqual(search(self.out, '" OR *', channels=['exact'])['hits'], [])

    def test_keyword_ranking_supports_noncontiguous_words_with_transparent_scores(self):
        build(self.literal, self.out)
        result = search(self.out, 'Josh truce')
        self.assertEqual(len(result['hits']), 4)
        self.assertTrue(all(set(h['channels']) == {'speech'} for h in result['hits']))
        self.assertTrue(all('bm25' in h['channels']['speech'] for h in result['hits']))

    def test_raw_transcript_text_and_read_only_inputs_preserved(self):
        inputs = [self.attempts['alice'] / n for n in ('transcript.json', 'packet.json', 'frames.json')]
        inputs += [self.sources['alice'] / 'packet-0000' / 'complete.json']
        originals = {p: p.read_bytes() for p in inputs}
        build(self.literal, self.out)
        hit = search(self.out, 'stop fighting')['hits'][0]
        self.assertEqual(hit['text'], 'Let us stop fighting')
        self.assertEqual(hit['occurrences'][0]['raw_text'], '  Let us stop fighting  ')
        for p, content in originals.items(): self.assertEqual(p.read_bytes(), content)

    def test_overlap_packet_provenance_combines_only_exact_identity(self):
        old = self.attempts['alice']
        attempt = self.sources['alice'] / 'packet-0001' / 'attempt-copy'
        shutil.copytree(old, attempt)
        transcript = read(attempt / 'transcript.json')
        for segment in transcript['segments']:
            segment['start'], segment['end'] = float(segment['start']), float(segment['end'])
        write(attempt / 'transcript.json', transcript)
        write(attempt.parent / 'complete.json', {'attempt': attempt.name})
        build_index(list(self.sources.values()), self.literal)
        build(self.literal, self.out)
        self.assertEqual(len(search(self.out, 'truce')['hits']), 4)
        hit = next(h for h in search(self.out, 'truce')['hits']
                   if h['source_id'] == 'alice' and h['start_sec'] == 10 and h['audio_stream'] == 1)
        self.assertEqual(len(hit['occurrences']), 2)
        self.assertEqual({o['transcript_file'] for o in hit['occurrences']},
                         {str(old / 'transcript.json'), str(attempt / 'transcript.json')})

    def test_wrong_source_evidence_reference_and_fabricated_joined_segment_rejected(self):
        index = read(self.literal / 'index.json')
        source = next(s for s in index['sources'] if s['source_id'] == 'alice')
        aggregate = self.literal / index['build'] / source['aggregate'] / 'transcript.json'
        rows = read(aggregate)
        rows['segments'][0]['occurrences'][0]['evidence_file'] = str(self.attempts['bob'] / 'evidence.json')
        write(aggregate, rows)
        with self.assertRaisesRegex(ValueError, 'accompany its exact raw transcript'):
            build(self.literal, self.out)
        rows['segments'][0]['occurrences'][0]['evidence_file'] = str(self.attempts['alice'] / 'evidence.json')
        write(aggregate, rows)
        evidence = read(self.attempts['alice'] / 'evidence.json')
        evidence['valid_segments'][0]['text'] = 'fabricated'
        write(self.attempts['alice'] / 'evidence.json', evidence)
        with self.assertRaisesRegex(ValueError, 'Joined speech evidence'):
            build(self.literal, self.out)

    def test_empty_ocr_text_is_coverage_and_not_an_invented_document(self):
        report = self.ocr(empty=True)
        result = build(self.literal, self.out, [report])
        self.assertEqual(result['ocr_documents'], 0)
        result = search(self.out, 'truce')
        self.assertEqual(result['coverage']['ocr'][0]['frames_processed'], 1)
        self.assertEqual(result['coverage']['ocr'][0]['nonempty_text_frames'], 0)
        self.assertEqual(result['channels']['ocr']['status'], 'searched')

    def test_requested_missing_channel_explicit_and_default_coverage_reports_omissions(self):
        build(self.literal, self.out)
        result = search(self.out, 'truce')
        self.assertEqual(result['channels']['ocr']['status'], 'not_indexed')
        self.assertEqual(result['channels']['semantic']['status'], 'not_indexed')
        for channel in ('ocr', 'semantic'):
            with self.assertRaisesRegex(ValueError, 'not indexed'):
                search(self.out, 'truce', channels=[channel])

    def test_limits_and_candidate_truncation_are_explicit(self):
        build(self.literal, self.out)
        result = search(self.out, 'truce', limit=1, candidate_limit=1)
        self.assertEqual(len(result['hits']), 1)
        self.assertTrue(result['at_limit']); self.assertTrue(result['more_available'])
        self.assertEqual(result['channels']['speech']['matches'], 4)
        self.assertTrue(result['channels']['speech']['more_available'])
        for kwargs in ({'limit': True}, {'candidate_limit': 201}, {'limit': 10, 'candidate_limit': 9},
                       {'channels': []}, {'channels': ['speech', 'speech']}):
            with self.assertRaises(ValueError): search(self.out, 'truce', **kwargs)

    def test_source_alias_requires_exact_path_and_detail_map_authorizes_clock(self):
        detail = self.root / 'detail'
        write(detail / 'packet.json', {'source': str(self.root / 'alice.mp4'), 'start_sec': 40, 'end_sec': 45})
        image = detail / 'frames' / 'raw_00001.jpg'; image.parent.mkdir(parents=True); image.write_bytes(b'detail')
        write(detail / 'frames.json', {'frames': [{'file': image.name, 'timestamp_sec': 42}]})
        report = self.ocr(source_id='ALIAS', timestamp=42, image=image)
        mapping = self.root / 'source-map.json'
        write(mapping, {'schema': 'vod-ocr-source-map/v1', 'sources': [
              {'ocr_source_id': 'ALIAS', 'source_id': 'alice', 'source': str(self.root / 'alice.mp4')}]})
        with self.assertRaisesRegex(ValueError, 'Unknown OCR source'):
            build(self.literal, self.out, [report], [detail])
        build(self.literal, self.out, [report], [detail], mapping)
        visible = next(h for h in search(self.out, 'truce')['hits'] if h['evidence_type'] == 'visible_text')
        self.assertEqual((visible['source_id'], visible['timestamp_sec']), ('alice', 42))
        self.assertEqual(visible['ocr_refs'][0]['ocr_source_id'], 'ALIAS')
        self.assertEqual(visible['frame_refs'][0]['frame_map'], str(detail / 'frames.json'))
        bad = read(mapping); bad['sources'][0]['source'] = str(self.root / 'bob.mp4'); write(mapping, bad)
        with self.assertRaisesRegex(ValueError, 'exact indexed source'):
            build(self.literal, self.out, [report], [detail], mapping)

    def test_ocr_wrong_clock_source_hash_and_manifest_rejected(self):
        for change, error in (('timestamp', 'frame map'), ('source', 'frame map'),
                              ('hash', 'image changed'), ('manifest', 'manifest changed')):
            with self.subTest(change=change):
                report = self.ocr()
                data = read(report)
                if change == 'timestamp':
                    data['frames'][0]['timestamp_sec'] = 11
                    manifest = read(data['manifest']); manifest[0]['timestamp_sec'] = 11
                    write(data['manifest'], manifest); data['manifest_sha256'] = digest(data['manifest'])
                elif change == 'source':
                    data['frames'][0]['source_id'] = 'bob'
                    manifest = read(data['manifest']); manifest[0]['source_id'] = 'bob'
                    write(data['manifest'], manifest); data['manifest_sha256'] = digest(data['manifest'])
                elif change == 'hash': data['frames'][0]['image_sha256'] = '0' * 64
                else: Path(data['manifest']).write_text('[]', encoding='utf-8')
                write(report, data)
                with self.assertRaisesRegex(ValueError, error): build(self.literal, self.out, [report])

    def test_ocr_report_must_include_all_manifest_frames_once(self):
        report = self.ocr(); data = read(report); data['frames'] = []; write(report, data)
        with self.assertRaisesRegex(ValueError, 'match its input manifest'):
            build(self.literal, self.out, [report])
        report = self.ocr(); data = read(report); data['frames'].append(deepcopy(data['frames'][0])); write(report, data)
        with self.assertRaisesRegex(ValueError, 'match its input manifest'):
            build(self.literal, self.out, [report])

    def test_stale_report_image_manifest_and_raw_evidence_refuse_search(self):
        report = self.ocr()
        for path in (report, Path(read(report)['manifest']), Path(read(report)['frames'][0]['file']),
                     self.attempts['alice'] / 'transcript.json', self.attempts['alice'] / 'frames.json'):
            with self.subTest(path=path):
                build(self.literal, self.out, [report])
                old = path.read_bytes(); path.write_bytes(old + b' ')
                with self.assertRaisesRegex(ValueError, 'stale'):
                    search(self.out, 'truce')
                path.write_bytes(old)

    def test_reuse_and_database_corruption_repair(self):
        build(self.literal, self.out)
        pointer = (self.out / 'unified.json').read_bytes()
        self.assertTrue(build(self.literal, self.out)['reused'])
        self.assertEqual((self.out / 'unified.json').read_bytes(), pointer)
        manifest = read(self.out / 'unified.json'); database = self.out / manifest['build'] / 'evidence.db'
        database.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'database changed'): search(self.out, 'truce')
        self.assertFalse(build(self.literal, self.out)['reused'])
        self.assertEqual(len(search(self.out, 'truce')['hits']), 4)

    def test_failed_rebuild_preserves_previous_published_index(self):
        build(self.literal, self.out); pointer = (self.out / 'unified.json').read_bytes()
        report = self.ocr(timestamp=11)
        with self.assertRaises(ValueError): build(self.literal, self.out, [report])
        self.assertEqual((self.out / 'unified.json').read_bytes(), pointer)
        self.assertEqual(len(search(self.out, 'truce')['hits']), 4)

    def test_semantic_rank_expands_to_exact_raw_evidence_and_one_model_session(self):
        folder, hit = self.semantic(); build(self.literal, self.out, semantic_folder=folder)
        calls = []
        class FakeSession:
            def __init__(self, out, model): calls.append(('initialize', out, model))
            def search(self, query, limit):
                calls.append(('query', query))
                return {'hits': [{**hit, 'similarity': .75}], 'distinct_results': 1,
                        'overlapping_results_grouped': 0, 'more_available': False, 'indexed_passages': 5}
        session = SearchSession(self.out, 'local-model', FakeSession)
        for query in ('truce', 'peace offering'):
            result = session.search(query)
            semantic = next(h for h in result['hits'] if 'semantic' in h['channels'])
            self.assertEqual(semantic['text'], 'Let us stop fighting')
            self.assertEqual(semantic['occurrences'][0]['raw_text'], '  Let us stop fighting  ')
            self.assertEqual(semantic['channels']['semantic']['similarity'], .75)
            self.assertEqual(semantic['rrf_score'], 1 / 61)
        self.assertEqual(len([c for c in calls if c[0] == 'initialize']), 1)
        with self.assertRaisesRegex(ValueError, '--model-dir'):
            search(self.out, 'truce')
        self.assertEqual(search(self.out, 'truce', channels=['speech'])['channels']['semantic']['status'], 'not_requested')

    def test_semantic_hits_merge_channels_only_for_exact_same_evidence(self):
        folder, _ = self.semantic(); data = read(folder / 'build-fixture' / 'passages.json')
        hit = next(d for d in data if d['source_id'] == 'alice' and d['audio_stream'] == 1
                   and d['start_sec'] == 10 and d['passage_kind'] == 'segment')
        build(self.literal, self.out, semantic_folder=folder)
        class FakeSession:
            def __init__(self, *args): pass
            def search(self, *args):
                return {'hits': [{**hit, 'similarity': .99}], 'distinct_results': 1,
                        'overlapping_results_grouped': 0, 'more_available': False, 'indexed_passages': 5}
        result = SearchSession(self.out, 'local-model', FakeSession).search('truce')
        merged = [h for h in result['hits'] if 'semantic' in h['channels']]
        self.assertEqual(len(merged), 1)
        self.assertEqual(set(merged[0]['channels']), {'exact', 'speech', 'semantic'})
        self.assertEqual(len(result['hits']), 4)

    def test_unrelated_semantic_index_and_changed_artifacts_rejected(self):
        folder, _ = self.semantic(); manifest = read(folder / 'semantic.json')
        manifest['literal_index'] = str(self.root / 'different-index'); write(folder / 'semantic.json', manifest)
        with self.assertRaisesRegex(ValueError, 'exact current literal'):
            build(self.literal, self.out, semantic_folder=folder)
        folder, _ = self.semantic(); (folder / 'build-fixture' / 'vectors.npy').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'artifacts changed'):
            build(self.literal, self.out, semantic_folder=folder)

    def test_semantic_unmapped_occurrence_and_requested_failure_propagate(self):
        folder, hit = self.semantic(); build(self.literal, self.out, semantic_folder=folder)
        hit['segments'][0]['occurrences'][0]['segment_index'] = 999
        class BadSession:
            def __init__(self, *args): pass
            def search(self, *args):
                return {'hits': [{**hit, 'similarity': .99}], 'distinct_results': 1,
                        'overlapping_results_grouped': 0, 'more_available': False, 'indexed_passages': 5}
        with self.assertRaisesRegex(ValueError, 'exact current transcript'):
            SearchSession(self.out, 'model', BadSession).search('truce')
        class FailedSession(BadSession):
            def search(self, *args): raise RuntimeError('model failure')
        with self.assertRaisesRegex(RuntimeError, 'model failure'):
            SearchSession(self.out, 'model', FailedSession).search('truce')

    def test_captured_snapshot_revalidated_after_semantic_work(self):
        folder, hit = self.semantic(); build(self.literal, self.out, semantic_folder=folder)
        initial = read(self.out / 'unified.json')
        class MutatingSession:
            def __init__(self, *args): pass
            def search(other, *args):
                literal = read(self.literal / 'index.json')
                aggregate = self.literal / literal['build'] / literal['sources'][0]['aggregate'] / 'transcript.json'
                aggregate.write_bytes(aggregate.read_bytes() + b' ')
                newer = deepcopy(initial); newer['dependencies'][str(aggregate)] = digest(aggregate)
                write(self.out / 'unified.json', newer)
                return {'hits': [{**hit, 'similarity': .99}], 'distinct_results': 1,
                        'overlapping_results_grouped': 0, 'more_available': False, 'indexed_passages': 5}
        with self.assertRaisesRegex(ValueError, 'stale'):
            SearchSession(self.out, 'model', MutatingSession).search('truce')

    def test_pointer_replacement_during_search_refused_even_if_old_evidence_valid(self):
        folder, hit = self.semantic(); build(self.literal, self.out, semantic_folder=folder)
        class RebuildingSession:
            def __init__(self, *args): pass
            def search(other, *args):
                build(self.literal, self.out)  # Publish a lexical-only snapshot.
                return {'hits': [{**hit, 'similarity': .99}], 'distinct_results': 1,
                        'overlapping_results_grouped': 0, 'more_available': False, 'indexed_passages': 5}
        with self.assertRaisesRegex(ValueError, 'changed during search'):
            SearchSession(self.out, 'model', RebuildingSession).search('truce')


if __name__ == '__main__':
    unittest.main()
