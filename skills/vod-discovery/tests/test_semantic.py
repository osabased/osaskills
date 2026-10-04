from pathlib import Path
import hashlib
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import semantic
from evidence import input_signature
from vod import read, write


class FakeModel:
    def __init__(self):
        self.batches = []

    def passage_embed(self, texts, **kwargs):
        self.batches.append(list(texts))
        return [[1.] * 384 for _ in texts]

    def query_embed(self, text):
        yield [1.] * 384


def row(start, end, value, stream=1):
    return {'start': start, 'end': end, 'text': value, 'occurrences': [
        {'start_sec': start, 'end_sec': end, 'audio_stream': stream, 'segment_index': 0,
         'transcript_file': 'raw.json', 'evidence_file': 'evidence.json'}]}


class SemanticPassages(unittest.TestCase):
    def test_context_keeps_source_clocks_streams_and_gaps(self):
        source = {'source_id': 'a', 'source': 'a.mp4'}
        rows = [row(310, 314, 'first'), row(314, 317, 'second'), row(311, 319, 'other', 2), row(370, 374, 'later')]
        docs = semantic.passages([(source, rows)], len)
        context = next(d for d in docs if d['passage_kind'] == 'context')
        self.assertEqual((context['start_sec'], context['end_sec'], context['text']), (310, 317, 'first\nsecond'))
        self.assertEqual({o['audio_stream'] for s in context['segments'] for o in s['occurrences']}, {1})
        self.assertTrue(any(d['text'] == 'later' for d in docs))
        self.assertFalse(any('other' in d['text'] and 'first' in d['text'] for d in docs))

    def test_long_text_keeps_every_character_without_inventing_word_times(self):
        value = 'This is a long transcript. ' * 80
        pieces = semantic.split_text(value, len)
        self.assertEqual(''.join(x[0] for x in pieces), value)
        self.assertTrue(all(len(x[0]) <= 384 and value[x[1]:x[2]] == x[0] for x in pieces))
        docs = semantic.passages([({'source_id': 'a', 'source': 'a.mp4'}, [row(30, 40, value)])], len)
        self.assertTrue(all(d['start_sec'] == 30 and d['end_sec'] == 40 for d in docs))

    def test_overlap_grouping_preserves_other_povs_streams_and_repeated_events(self):
        docs = [{'source_id': sid, 'audio_stream': stream, 'start_sec': a, 'end_sec': b}
                for sid, stream, a, b in [('a', 1, 10, 20), ('a', 1, 11, 22), ('b', 1, 11, 22),
                                         ('a', 2, 11, 22), ('a', 1, 110, 120)]]
        hits, info = semantic.rank(docs, [.9, .8, .7, .6, .5], 3)
        self.assertEqual(len(hits), 3)
        self.assertEqual(info['distinct_results'], 4)
        self.assertTrue(info['more_available'])
        self.assertEqual(info['overlapping_results_grouped'], 1)
        self.assertEqual(semantic.rank([], [], 10)[0], [])


class SemanticSnapshots(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name); self.prepared = self.root / 'prepared'; self.index = self.root / 'literal'
        self.out = self.root / 'semantic'
        write(self.prepared / 'source.json', {'id': 'a', 'path': 'a.mp4', 'duration_sec': 600, 'settings': {'window': 300}})
        attempt = self.prepared / 'packet-0000/attempt-a'
        write(attempt / 'packet.json', {'source_id': 'a', 'start_sec': 0, 'end_sec': 300})
        write(attempt / 'frames.json', {'frames': []}); write(attempt / 'transcript.json', {'segments': []})
        write(attempt.parent / 'complete.json', {'attempt': 'attempt-a'})
        self.aggregate = self.index / 'build-a/source-000/transcript.json'
        write(self.aggregate, {'segments': [row(10, 20, 'Let us make peace.')]})
        write(self.index / 'index.json', {'schema': 'vod-search/v1', 'build': 'build-a',
              'inputs': {str(self.prepared): input_signature(self.prepared)},
              'sources': [{'source_id': 'a', 'source': 'a.mp4', 'aggregate': 'source-000'}],
              'summary': {'invalid_transcript_segments': 0}})

    def tearDown(self):
        self.temp.cleanup()

    def test_raw_changes_are_stale_but_review_notes_are_not(self):
        before = semantic.snapshot(self.index)[1]
        write(self.prepared / 'packet-0000/review.json', {'human_note': 'Keep'})
        self.assertEqual(semantic.snapshot(self.index)[1], before)
        write(self.prepared / 'packet-0000/attempt-a/transcript.json', {'segments': ['changed']})
        with self.assertRaisesRegex(ValueError, 'stale'):
            semantic.snapshot(self.index)

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_reuse_and_failed_rebuild_preserve_published_snapshot(self, loader, identity):
        class FakeModel:
            def passage_embed(self, texts, **kwargs):
                return [[1.] * 384 for _ in texts]
        loader.return_value = (FakeModel(), len)
        self.assertFalse(semantic.build(self.index, self.out, 'unused')['reused'])
        published = (self.out / 'semantic.json').read_bytes()
        self.assertTrue(semantic.build(self.index, self.out, 'unused')['reused'])
        self.assertEqual(loader.call_count, 1)
        write(self.aggregate, {'segments': [row(10, 20, 'Different evidence')]})
        loader.side_effect = RuntimeError('Inference failed')
        with self.assertRaises(RuntimeError): semantic.build(self.index, self.out, 'unused')
        self.assertEqual((self.out / 'semantic.json').read_bytes(), published)
        with self.assertRaisesRegex(ValueError, 'stale'):
            semantic.search(self.out, 'unused', 'peace')

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_changed_vectors_are_rejected_before_query_inference(self, loader, identity):
        loader.return_value = (type('FakeModel', (), {'passage_embed': lambda self, docs, **kw: [[1.] * 384 for _ in docs]})(), len)
        semantic.build(self.index, self.out, 'unused')
        manifest = read(self.out / 'semantic.json')
        (self.out / manifest['build'] / 'vectors.npy').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'artifacts changed'):
            semantic.search(self.out, 'unused', 'peace')
        self.assertEqual(loader.call_count, 1)

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_shared_cache_reuses_text_when_references_change_and_inputs_expand(self, loader, identity):
        model = FakeModel(); loader.return_value = (model, len)
        cache = self.root / 'shared-cache'
        first = semantic.build(self.index, self.out, 'unused', cache)
        self.assertEqual((first['embeddings_computed'], first['embeddings_reused']), (1, 0))
        changed = row(60, 70, 'Let us make peace.')
        changed['occurrences'][0]['transcript_file'] = 'new-exact-reference.json'
        write(self.aggregate, {'segments': [changed, row(110, 120, 'A new passage')]})
        second_out = self.root / 'new-semantic'
        second = semantic.build(self.index, second_out, 'unused', cache)
        self.assertEqual((second['embeddings_computed'], second['embeddings_reused']), (1, 1))
        self.assertEqual(model.batches, [['Let us make peace.'], ['A new passage']])
        manifest = read(second_out / 'semantic.json')
        docs = read(second_out / manifest['build'] / 'passages.json')
        self.assertEqual(docs[0]['start_sec'], 60)
        self.assertEqual(docs[0]['segments'][0]['occurrences'][0]['transcript_file'], 'new-exact-reference.json')

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_recipe_and_model_changes_do_not_reuse_embeddings(self, loader, identity):
        model = FakeModel(); loader.return_value = (model, len)
        semantic.build(self.index, self.out, 'unused')
        with patch.dict(semantic.CACHE_RECIPE, {'normalization': 'l2/next'}):
            with self.assertRaisesRegex(ValueError, 'recipe changed'):
                semantic.search(self.out, 'unused', 'peace')
            self.assertEqual(semantic.build(self.index, self.out, 'unused')['embeddings_computed'], 1)
        identity.return_value = {'test': 'other-model'}
        self.assertEqual(semantic.build(self.index, self.out, 'unused')['embeddings_computed'], 1)
        with patch.dict(semantic.POLICY, {'version': 3}):
            self.assertEqual(semantic.build(self.index, self.out, 'unused')['embeddings_computed'], 1)
        self.assertEqual(len(model.batches), 4)

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_legacy_manifest_remains_searchable_then_rebuilds_with_recipe(self, loader, identity):
        model = FakeModel(); loader.return_value = (model, len)
        semantic.build(self.index, self.out, 'unused')
        manifest = read(self.out / 'semantic.json'); del manifest['embedding_recipe']
        write(self.out / 'semantic.json', manifest)
        self.assertEqual(len(semantic.search(self.out, 'unused', 'peace')['hits']), 1)
        rebuilt = semantic.build(self.index, self.out, 'unused')
        self.assertFalse(rebuilt['reused'])
        self.assertEqual(rebuilt['embeddings_reused'], 1)
        self.assertEqual(read(self.out / 'semantic.json')['embedding_recipe'], semantic.CACHE_RECIPE)

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_warm_search_initializes_once_and_matches_fresh_queries(self, loader, identity):
        loader.return_value = (FakeModel(), len)
        semantic.build(self.index, self.out, 'unused')
        loader.reset_mock()
        session = semantic.SearchSession(self.out, 'unused')
        session.start()
        first = session.search('peace')
        session.search('a different query')
        self.assertEqual(session.search('peace'), first)
        self.assertEqual(loader.call_count, 1)
        self.assertEqual(semantic.search(self.out, 'unused', 'peace'), first)

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_warm_search_rejects_raw_and_vector_changes_after_success(self, loader, identity):
        model = FakeModel(); loader.return_value = (model, len)
        semantic.build(self.index, self.out, 'unused')
        session = semantic.SearchSession(self.out, 'unused')
        session.search('peace')
        raw = self.prepared / 'packet-0000/attempt-a/transcript.json'
        original = raw.read_bytes()
        write(raw, {'segments': ['changed']})
        with self.assertRaisesRegex(ValueError, 'stale'): session.search('peace')
        raw.write_bytes(original)
        manifest = read(self.out / 'semantic.json')
        (self.out / manifest['build'] / 'vectors.npy').write_bytes(b'damaged')
        with self.assertRaisesRegex(ValueError, 'artifacts changed'): session.search('peace')

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_warm_search_refreshes_published_evidence_references(self, loader, identity):
        loader.return_value = (FakeModel(), len)
        semantic.build(self.index, self.out, 'unused')
        session = semantic.SearchSession(self.out, 'unused')
        session.search('peace')
        changed = row(70, 80, 'Let us make peace.')
        changed['occurrences'][0]['transcript_file'] = 'new-source.json'
        write(self.aggregate, {'segments': [changed]})
        semantic.build(self.index, self.out, 'unused')
        before = loader.call_count
        result = session.search('peace')['hits'][0]
        self.assertEqual(loader.call_count, before)
        self.assertEqual((result['start_sec'], result['end_sec']), (70, 80))
        self.assertEqual(result['segments'][0]['occurrences'][0]['transcript_file'], 'new-source.json')

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_warm_search_cannot_mix_a_new_index_model_with_resident_old_model(self, loader, identity):
        loader.return_value = (FakeModel(), len)
        semantic.build(self.index, self.out, 'unused')
        session = semantic.SearchSession(self.out, 'unused'); session.search('peace')
        identity.return_value = {'test': 'replacement-model'}
        semantic.build(self.index, self.out, 'unused')
        with self.assertRaisesRegex(ValueError, 'restart the worker'): session.search('peace')

    @patch.object(semantic, 'model_identity', return_value={'test': 'model'})
    @patch.object(semantic, 'load_model')
    def test_worker_errors_do_not_replay_previous_results_or_stop_valid_requests(self, loader, identity):
        loader.return_value = (FakeModel(), len)
        semantic.build(self.index, self.out, 'unused')
        requests = io.StringIO('\n'.join(['not json', json.dumps({'id':'bad', 'query':'peace','limit':False}),
            json.dumps({'id':'empty','query':' '}),json.dumps({'id':'long','query':'a'*385}),
            json.dumps({'id':'ok','query':'peace','limit':1})])+'\n')
        target = io.StringIO()
        semantic.worker(semantic.SearchSession(self.out,'unused'), requests, target)
        replies = [json.loads(line) for line in target.getvalue().splitlines()]
        self.assertTrue(replies[0]['ready'])
        self.assertTrue(all('error' in r and 'result' not in r for r in replies[1:5]))
        self.assertEqual(replies[5]['id'], 'ok')
        self.assertEqual(len(replies[5]['result']['hits']), 1)

    def test_worker_stops_on_oversized_input(self):
        class Session:
            def start(self): pass
            def search(self, *a, **k): raise AssertionError('Oversized request must not infer')
        target = io.StringIO()
        semantic.worker(Session(), io.StringIO('x'*17000+'\n'), target)
        self.assertIn('worker stopped', target.getvalue())


class SemanticEmbeddingCache(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.cache = Path(self.temp.name)
        self.identity = {'test': 'model'}

    def tearDown(self):
        self.temp.cleanup()

    def entries(self):
        return list(self.cache.glob('*/*.json'))

    def test_duplicate_text_is_embedded_once_and_returned_in_original_order(self):
        import numpy as np
        model = FakeModel()
        docs = [{'text': 'same'}, {'text': 'other'}, {'text': 'same'}]
        vectors, info = semantic.passage_embeddings(model, docs, self.cache, self.identity)
        self.assertEqual(model.batches, [['same', 'other']])
        self.assertEqual(info, {'embeddings_computed': 2, 'embeddings_reused': 0})
        self.assertEqual(vectors.shape, (3, 384))
        self.assertTrue(np.array_equal(vectors[0], vectors[2]))
        second, info = semantic.passage_embeddings(model, docs, self.cache, self.identity)
        self.assertEqual(len(model.batches), 1)
        self.assertEqual(info, {'embeddings_computed': 0, 'embeddings_reused': 2})
        self.assertTrue(np.array_equal(vectors, second))

    def test_failed_later_batch_keeps_only_completed_batches_for_retry(self):
        model = FakeModel()
        docs = [{'text': f'passage-{i}'} for i in range(35)]
        good_embed = model.passage_embed

        def fail_second(texts, **kwargs):
            if texts[0] == 'passage-32':
                yield [1.] * 384
                raise RuntimeError('Interrupted inference')
            yield from good_embed(texts, **kwargs)

        model.passage_embed = fail_second
        with self.assertRaisesRegex(RuntimeError, 'Interrupted'):
            semantic.passage_embeddings(model, docs, self.cache, self.identity)
        self.assertEqual(len(self.entries()), 32)
        self.assertFalse(list(self.cache.rglob('*.tmp')))
        retry = FakeModel()
        _, info = semantic.passage_embeddings(retry, docs, self.cache, self.identity)
        self.assertEqual(info, {'embeddings_reused': 32, 'embeddings_computed': 3})
        self.assertEqual(retry.batches, [[f'passage-{i}' for i in range(32, 35)]])

    def test_invalid_batch_never_publishes_any_entry(self):
        bad_outputs = [([[1.] * 384, [1.] * 383]),
                       ([[1.] * 384, [float('nan')] * 384]),
                       ([[1.] * 384, [float('inf')] * 384]),
                       ([[1.] * 384, [0.] * 384]),
                       ([[1.] * 384])]
        docs = [{'text': 'first'}, {'text': 'second'}]
        for output in bad_outputs:
            with self.subTest(output_length=len(output)):
                model = FakeModel(); model.passage_embed = lambda *a, **kw: output
                with self.assertRaises(ValueError):
                    semantic.passage_embeddings(model, docs, self.cache, self.identity)
                self.assertEqual(self.entries(), [])

    def test_corrupted_entries_are_recomputed(self):
        import numpy as np
        docs = [{'text': 'same'}]
        model = FakeModel()
        semantic.passage_embeddings(model, docs, self.cache, self.identity)
        path = self.entries()[0]
        good = read(path)
        invalid = [dict(good, vector=[0.] * 384), dict(good, vector=[1.] * 383),
                   dict(good, vector=[float('nan')] * 384), dict(good, scope='wrong'),
                   dict(good, text_sha256='wrong'), dict(good, vector_sha256='wrong')]
        # A checksum-matching vector must also have unit norm and valid dimensions.
        unnormalized = [1.] * 384
        invalid.append(dict(good, vector=unnormalized,
                            vector_sha256=hashlib.sha256(np.asarray(unnormalized, dtype='<f4').tobytes()).hexdigest()))
        for entry in invalid:
            write(path, entry)
            _, info = semantic.passage_embeddings(model, docs, self.cache, self.identity)
            self.assertEqual(info['embeddings_computed'], 1)
        path.write_text('unfinished json', encoding='utf-8')
        _, info = semantic.passage_embeddings(model, docs, self.cache, self.identity)
        self.assertEqual(info['embeddings_computed'], 1)

    def test_failed_atomic_save_leaves_existing_entry_and_no_temp(self):
        import numpy as np
        scope = semantic.embedding_scope(self.identity)
        key = hashlib.sha256(b'same').hexdigest()
        path = self.cache / scope / (key + '.json')
        vector = np.ones(384, dtype=np.float32); vector /= np.linalg.norm(vector)
        semantic.save_cached_vector(path, scope, key, vector)
        before = path.read_bytes()
        with patch.object(Path, 'replace', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                semantic.save_cached_vector(path, scope, key, vector)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(self.cache.rglob('*.tmp')))

    def test_empty_passages_do_not_infer_or_create_cache(self):
        model = FakeModel()
        vectors, info = semantic.passage_embeddings(model, [], self.cache / 'empty', self.identity)
        self.assertEqual(vectors.shape, (0, 384))
        self.assertEqual(model.batches, [])
        self.assertEqual(info, {'embeddings_computed': 0, 'embeddings_reused': 0})
        self.assertFalse((self.cache / 'empty').exists())


if __name__ == '__main__':
    unittest.main()
