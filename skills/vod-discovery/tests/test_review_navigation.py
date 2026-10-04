import copy
import http.client
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch

import test_review_queue as fixtures
from review_queue import Store, atomic_json, digest, file_hash, make_server, Preferences, selected_xml
from review_navigation import related_groups
from review_transcript import SCHEMA, TranscriptEvidence, import_transcripts


class ReviewNavigationTests(unittest.TestCase):
    def setUp(self):
        fixtures.ReviewQueueTests.setUp(self)
        self.addCleanup(self.store.context.close)
        self.addCleanup(self.store.navigation.close)

    def snapshot(self):
        def row(sid, stream, start, end, text):
            return dict(id=digest([sid, stream, start, end, text]), source_id=sid, audio_stream=stream,
                        start_sec=start, end_sec=end, text=text, refs=[dict(transcript_file='speech.json', segment_index=0)])
        return dict(schema=SCHEMA, queue_hash=self.store.queue_hash, rows=[
            row('a', 1, 110, 114, 'Remember this attempt'), row('b', 1, 195, 198, 'Remember this attempt'),
            row('b', 2, 195, 198, 'Remember this attempt'), row('a', 1, 400, 405, 'A later payoff'),
            row('b', 1, 898, 899.9, 'End of recording')],
            coverage=[dict(source_id='a', core_ranges_sec=[[0, 600]]), dict(source_id='b', core_ranges_sec=[[0, 900]])],
            unmapped_sources=[], excluded_invalid_segments=1, inputs={}, limitations='Rough recognized speech only')

    def attach(self):
        value = self.snapshot()
        atomic_json(self.root / 'transcript.json', value)
        self.store.transcript = TranscriptEvidence(self.store)
        return value

    def completed(self, navigation, patch_value, method='aids'):
        job = getattr(navigation, method)(patch_value)
        navigation.close()
        return navigation.status(job['id']) if 'id' in job else job

    def fake_aids(self, view, path, out, key):
        name = 'aids-' + key + '.jpg'
        (out / name).write_bytes(b'thumbnail')
        return dict(source_id=view['source_id'], preview_start_sec=view['preview_start_sec'],
                    preview_end_sec=view['preview_end_sec'], waveform=dict(status='ready', peaks=[.3, .8], step_sec=1),
                    thumbnails=dict(file=name, sha256=file_hash(out / name), width=160, height=90,
                                    columns=8, rows=1, frames=[dict(source_sec=view['preview_start_sec'], x=0, y=0)]))

    def test_groups_use_authored_links_only_preserving_order_choices_and_unconnected_moments(self):
        before = copy.deepcopy(self.cards)
        data = related_groups(self.cards)
        self.assertEqual(data['groups'][0]['event_ids'], ['fight', 'later'])
        self.assertEqual(data['ungrouped_ids'], ['social'])
        self.assertEqual(data['groups'][0]['links'], [dict(event_id='later', related_event_id='fight', source_id='b', relationship='earlier')])
        self.assertEqual(self.cards, before)
        originals = {n:(self.root / n).read_bytes() for n in ('queue.json', 'state.json', 'events.json', 'plan.json')}
        self.assertEqual(self.store.playback_queue()['related_groups'], data)
        for n, raw in originals.items():
            self.assertEqual((self.root / n).read_bytes(), raw)

    def test_bidirectional_cycles_do_not_merge_independent_repeated_attempts(self):
        cards = copy.deepcopy(self.cards)
        cards[0]['related'] = [dict(event_id='later', source_id='a', relationship='later')]
        cards.append(dict(cards[0], id='another-attempt', related=[]))
        groups = related_groups(cards)
        self.assertEqual(len(groups['groups']), 1)
        self.assertEqual(groups['ungrouped_ids'], ['social', 'another-attempt'])

    def test_old_queue_and_missing_transcript_search_leave_saved_state_unchanged(self):
        before = (self.root / 'state.json').read_bytes()
        result = self.store.transcript.search('anything')
        self.assertEqual(result['status'], 'missing')
        self.assertEqual(result['hits'], [])
        self.assertEqual((self.root / 'state.json').read_bytes(), before)

    def test_literal_search_preserves_duplicate_speech_on_separate_streams_and_source_clocks(self):
        self.attach()
        result = self.store.transcript.search('REMEMBER  this')
        self.assertEqual(result['total'], 3)
        self.assertEqual([(r['source_id'], r['audio_stream'], r['start_sec']) for r in result['hits']],
                         [('a', 1, 110), ('b', 1, 195), ('b', 2, 195)])
        self.assertEqual(result['hits'][1]['target'], dict(event_id='fight', view=1, source_sec=195))
        self.assertEqual(result['hits'][0]['refs'][0]['transcript_file'], 'speech.json')

    def test_transcript_scope_paging_empty_search_and_unprepared_targets_are_explicit(self):
        self.attach()
        result = self.store.transcript.search('', source_id='a', start=105, end=122)
        self.assertEqual([r['start_sec'] for r in result['hits']], [110])
        result = self.store.transcript.search('', limit=2, offset=2)
        self.assertTrue(result['more'])
        self.assertIsNone(result['hits'][1]['target'])
        self.assertEqual(self.store.transcript.search('not spoken')['total'], 0)
        for kwargs in [dict(limit=0), dict(offset=-1), dict(source_id='nope'), dict(start=0, end=1), dict(query='x'*301)]:
            with self.assertRaises(ValueError):
                self.store.transcript.search(**kwargs)

    def test_bad_transcript_does_not_block_confirmed_review_choices(self):
        value = self.attach()
        value['rows'][0]['start_sec'] = -1
        atomic_json(self.root / 'transcript.json', value)
        loaded = Store(self.root)
        self.assertEqual(loaded.playback_queue()['transcript']['status'], 'error')
        self.assertEqual(loaded.state(), self.store.state())
        value['queue_hash'] = 'different'
        atomic_json(self.root / 'transcript.json', value)
        self.assertEqual(Store(self.root).transcript.summary()['status'], 'error')
        value = self.snapshot(); del value['coverage']; atomic_json(self.root / 'transcript.json', value)
        self.assertEqual(Store(self.root).transcript.summary()['status'], 'error')

    def test_visual_cache_reuses_and_repairs_assets_without_modifying_queue_or_decisions(self):
        originals = {n:(self.root / n).read_bytes() for n in ('queue.json', 'state.json', 'events.json', 'plan.json')}
        with patch('review_navigation.render_aids', side_effect=self.fake_aids) as renderer:
            result = self.completed(self.store.navigation, dict(event_id='fight', view=1))
            self.assertEqual(result['status'], 'ready')
            self.assertEqual(renderer.call_count, 1)
            reloaded = Store(self.root)
            same = self.completed(reloaded.navigation, dict(event_id='fight', view=1))
            self.assertEqual(same['result'], result['result'])
            self.assertEqual(renderer.call_count, 1)
            (self.root / 'navigation' / result['result']['thumbnails']['file']).unlink()
            repaired = self.completed(reloaded.navigation, dict(event_id='fight', view=1))
            self.assertEqual(repaired['status'], 'ready')
            self.assertEqual(renderer.call_count, 2)
        for n, raw in originals.items():
            self.assertEqual((self.root / n).read_bytes(), raw)

    def test_failed_visual_preparation_retains_choices_and_is_retryable(self):
        before = (self.root / 'state.json').read_bytes()
        with patch('review_navigation.render_aids', side_effect=RuntimeError('encoder failed')):
            result = self.completed(self.store.navigation, dict(event_id='fight', view=0))
        self.assertEqual(result['status'], 'error')
        with patch('review_navigation.render_aids', side_effect=self.fake_aids):
            self.assertEqual(self.completed(self.store.navigation, dict(event_id='fight', view=0))['status'], 'ready')
        self.assertEqual((self.root / 'state.json').read_bytes(), before)

    def test_corrupt_optional_navigation_registry_does_not_block_review(self):
        (self.root / 'navigation.json').write_text('{invalid', encoding='utf-8')
        reloaded = Store(self.root)
        self.assertEqual(reloaded.state(), self.store.state())
        with patch('review_navigation.render_aids', side_effect=self.fake_aids):
            self.assertEqual(self.completed(reloaded.navigation, dict(event_id='fight', view=0))['status'], 'ready')

    def test_context_change_gets_new_peaks_and_frame_source_start(self):
        with patch('review_navigation.render_aids', side_effect=self.fake_aids) as renderer:
            first = self.completed(self.store.navigation, dict(event_id='fight', view=0))
            with patch('review_queue.render_preview', side_effect=fixtures.ReviewQueueTests.fake_preview):
                view = self.store.context.view('fight', 0)
                job = self.store.context.request(dict(event_id='fight', view=0, direction='before',
                    preview_start_sec=view['preview_start_sec'], preview_end_sec=view['preview_end_sec']))
                self.store.context.close()
                self.assertEqual(self.store.context.status(job['id'])['status'], 'ready')
            second = self.completed(self.store.navigation, dict(event_id='fight', view=0))
            self.assertEqual(renderer.call_count, 2)
            self.assertEqual(second['result']['thumbnails']['frames'][0]['source_sec'], 90)
            self.assertNotEqual(first['result']['thumbnails']['file'], second['result']['thumbnails']['file'])
            self.assertTrue(self.store.navigation.registered(first['result']['thumbnails']['file']))

    def test_transcript_excerpt_is_bounded_source_specific_cached_and_never_changes_export(self):
        self.attach()
        before = {n:(self.root / n).read_bytes() for n in ('queue.json', 'state.json', 'events.json', 'plan.json')}
        xml, _ = selected_xml(self.data, self.plan, self.probes, self.state['decisions'], 'all')
        row = self.store.transcript.search('payoff')['hits'][0]
        with patch('review_queue.render_preview', side_effect=fixtures.ReviewQueueTests.fake_preview) as renderer:
            result = self.completed(self.store.navigation, dict(line_id=row['id']), 'excerpt')
            view = result['result']
            self.assertEqual((view['source_id'], view['preview_start_sec'], view['preview_end_sec']), ('a', 397, 427))
            self.assertEqual(self.completed(self.store.navigation, dict(line_id=row['id']), 'excerpt')['result'], view)
            self.assertEqual(renderer.call_count, 1)
            row = self.store.transcript.search('End of recording')['hits'][0]
            result = self.completed(self.store.navigation, dict(line_id=row['id']), 'excerpt')
            self.assertEqual(result['result']['preview_end_sec'], 900)
        for n, raw in before.items():
            self.assertEqual((self.root / n).read_bytes(), raw)
        self.assertEqual(selected_xml(self.data, self.plan, self.probes, self.state['decisions'], 'all')[0], xml)
        with self.assertRaises(ValueError):
            self.store.navigation.excerpt(dict(line_id='not a line'))

    def fake_index(self, other_path=False):
        path = self.root / 'speech-index'
        prepared = path / 'prepared'
        prepared.mkdir(parents=True)
        source = self.data['sources'][0]
        media = self.root / 'different-excerpt.mp4' if other_path else Path(source['path'])
        if other_path: media.write_bytes(b'excerpt')
        stat = media.stat()
        atomic_json(prepared / 'source.json', dict(id='indexed-a', path=str(media), size=stat.st_size, mtime_ns=stat.st_mtime_ns, duration_sec=600))
        attempt = prepared / 'packet-0000' / 'attempt-one'; attempt.mkdir(parents=True)
        atomic_json(attempt.parent / 'complete.json', dict(attempt='attempt-one'))
        atomic_json(attempt / 'packet.json', dict(source_id='indexed-a', start_sec=0, end_sec=600))
        raw = [dict(start=110, end=114, text='Recognized words', audio_stream=stream) for stream in (1, 2)]
        atomic_json(attempt / 'transcript.json', dict(segments=raw))
        atomic_json(attempt / 'evidence.json', dict(source_id='indexed-a', valid_segments=[dict(row, segment_index=i) for i, row in enumerate(raw)]))
        aggregate = path / 'build-one' / 'source-000'
        aggregate.mkdir(parents=True)
        occurrence = dict(start_sec=110, end_sec=114, audio_stream=1, transcript_file=str(attempt / 'transcript.json'),
                          evidence_file=str(attempt / 'evidence.json'), segment_index=0)
        atomic_json(aggregate / 'transcript.json', dict(segments=[dict(start=110, end=114, text='Recognized words',
            occurrences=[occurrence, dict(occurrence, audio_stream=2, segment_index=1), dict(occurrence, end_sec=9999)])]))
        atomic_json(path / 'index.json', dict(schema='vod-search/v1', build='build-one', inputs={str(prepared):'signature'},
            sources=[dict(source_id='indexed-a', source=str(media), prepared=str(prepared), aggregate='source-000',
                          core_ranges_sec=[[0, 600]], prepared_packets=1, total_packets=1)],
            summary=dict(invalid_transcript_segments=1)))
        return path

    def test_import_reuses_index_and_retains_streams_provenance_invalid_exclusions_and_choices(self):
        index = self.fake_index()
        before = (self.root / 'state.json').read_bytes()
        with patch('evidence.input_signature', return_value='signature'):
            summary = import_transcripts(self.store, index)
        self.assertEqual(summary['lines'], 2)
        self.assertEqual(summary['excluded_invalid_segments'], 2)
        self.assertEqual([r['audio_stream'] for r in self.store.transcript.rows], [1, 2])
        self.assertEqual(self.store.transcript.rows[0]['refs'][0]['indexed_source_id'], 'indexed-a')
        self.assertEqual((self.root / 'state.json').read_bytes(), before)

    def test_unmapped_excerpt_needs_explicit_evidenced_clock_mapping(self):
        index = self.fake_index(other_path=True)
        with patch('evidence.input_signature', return_value='signature'):
            self.assertEqual(import_transcripts(self.store, index)['lines'], 0)
            mapping = self.root / 'map.json'
            atomic_json(mapping, dict(schema='vod-review-transcript-map/v1', sources=[
                dict(indexed_source_id='indexed-a', source_id='a', offset_sec=0, evidence='Verified source excerpt at zero')]))
            self.assertEqual(import_transcripts(self.store, index, mapping)['lines'], 2)
        self.assertEqual(self.store.transcript.rows[0]['refs'][0]['mapping']['evidence'], 'Verified source excerpt at zero')

    def test_stale_index_or_changed_speech_media_rejects_without_overwriting_existing_snapshot(self):
        self.attach()
        original = (self.root / 'transcript.json').read_bytes()
        index = self.fake_index()
        with patch('evidence.input_signature', return_value='wrong'):
            with self.assertRaises(ValueError): import_transcripts(self.store, index)
        self.assertEqual((self.root / 'transcript.json').read_bytes(), original)

    def test_import_rejects_reference_to_other_source_or_changed_raw_segment(self):
        self.attach()
        original = (self.root / 'transcript.json').read_bytes()
        index = self.fake_index()
        raw = index / 'prepared' / 'packet-0000' / 'attempt-one' / 'transcript.json'
        value = json.loads(raw.read_text()); value['segments'][0]['text'] = 'Different raw speech'; atomic_json(raw, value)
        with patch('evidence.input_signature', return_value='signature'):
            with self.assertRaises(ValueError): import_transcripts(self.store, index)
        self.assertEqual((self.root / 'transcript.json').read_bytes(), original)
        source_json = index / 'prepared' / 'source.json'
        value = json.loads(source_json.read_text()); value['size'] += 1; atomic_json(source_json, value)
        with patch('evidence.input_signature', return_value='signature'):
            with self.assertRaises(ValueError): import_transcripts(self.store, index)
        self.assertEqual((self.root / 'transcript.json').read_bytes(), original)

    def test_navigation_http_is_authenticated_and_only_registered_assets_are_exposed(self):
        self.attach()
        with patch('review_navigation.render_aids', side_effect=self.fake_aids):
            aids = self.completed(self.store.navigation, dict(event_id='fight', view=0))['result']
        server = make_server(self.store, preferences=Preferences(self.root / 'keys.json'))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        def request(method, path, body=None, headers=None):
            c = http.client.HTTPConnection('127.0.0.1', server.server_port)
            c.request(method, path, body=body, headers=headers or {})
            r = c.getresponse(); result=(r.status,r.read()); c.close(); return result
        status, raw = request('GET', '/api/queue'); self.assertEqual(status, 200)
        token = json.loads(raw)['token']
        status, raw = request('GET', '/api/transcript?q=remember&source_id=b')
        self.assertEqual(status, 200); self.assertEqual(json.loads(raw)['total'], 2)
        self.assertEqual(request('GET', '/navigation/'+aids['thumbnails']['file']), (200, b'thumbnail'))
        self.assertEqual(request('GET', '/navigation/../state.json')[0], 404)
        self.assertEqual(request('GET', '/previews/speech-'+'0'*64+'.mp4')[0], 404)
        body = json.dumps(dict(event_id='fight', view=0))
        self.assertEqual(request('POST', '/api/aids', body, {'Content-Type':'application/json'})[0], 403)
        headers = {'Content-Type':'application/json', 'X-Review-Token':token, 'Origin':f'http://127.0.0.1:{server.server_port}'}
        self.assertEqual(request('POST', '/api/aids', body, headers)[0], 200)
        self.assertEqual(request('GET', '/api/transcript?offset=-1')[0], 400)


if __name__ == '__main__':
    unittest.main()
