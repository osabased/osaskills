from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evidence import build_index, enrich, packet_evidence, search_index
from vod import read, write


class EvidenceSearch(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.out = self.root / 'search'

    def tearDown(self):
        self.temp.cleanup()

    def source(self, name):
        folder = self.root / name
        write(folder / 'source.json', {'id': name, 'path': str(self.root / (name + '.mp4')),
              'duration_sec': 900, 'settings': {'window': 300}})
        return folder

    def packet(self, source, index, start, end, segments, times=None):
        folder = source / f'packet-{index:04d}'
        attempt = folder / 'attempt-test'
        write(attempt / 'packet.json', {'source_id': source.name, 'start_sec': start, 'end_sec': end,
              'core_start_sec': index * 300, 'core_end_sec': (index + 1) * 300})
        write(attempt / 'transcript.json', {'status': 'transcribed' if segments else 'no_speech_detected',
              'streams': {'1': 'transcribed'}, 'segments': segments})
        frames = []
        for i, t in enumerate(times if times is not None else [start, (start + end) / 2]):
            name = f'raw_{i:05d}.jpg'
            (attempt / 'frames').mkdir(exist_ok=True)
            (attempt / 'frames' / name).write_bytes(b'fixture')
            frames.append({'file': name, 'timestamp_sec': t})
        write(attempt / 'frames.json', {'frames': frames})
        write(folder / 'review.json', {'status': 'partial', 'event_ids': ['human-note']})
        write(folder / 'complete.json', {'attempt': attempt.name})
        return attempt

    def seg(self, start, end, text, stream=1):
        return {'start': start, 'end': end, 'text': text, 'audio_stream': stream}

    def test_nonzero_packet_clocks_and_overlapping_audio_streams(self):
        source = self.source('alice')
        attempt = self.packet(source, 1, 300, 330,
            [self.seg(310, 315, 'First voice'), self.seg(310, 315, 'Second voice', 2)],
            [300, 311, 325, 330])
        result = packet_evidence(attempt)
        self.assertEqual([t['audio_stream'] for t in result['tracks']], [1, 2])
        for track in result['tracks']:
            spans = track['spans']
            self.assertEqual([f['t'] for sp in spans for f in sp['frames']], [300, 311, 325, 330])
            speech = next(sp for sp in spans if sp['speech'])
            self.assertEqual((speech['start'], speech['end']), (310, 315))
            self.assertEqual(speech['frames'][0]['t'], 311)
            self.assertEqual(speech['frames'][0]['relation'], 'within')

    def test_small_gap_frame_is_nearby_not_assigned_to_spoken_instant(self):
        source = self.source('alice')
        attempt = self.packet(source, 0, 0, 12,
            [self.seg(0, 5, 'one'), self.seg(6, 12, 'two')], [5.5])
        result = packet_evidence(attempt)
        frames = [f for sp in result['tracks'][0]['spans'] for f in sp['frames']]
        self.assertEqual(frames[0]['relation'], 'nearby')
        self.assertEqual(frames[0]['t'], 5.5)

    def test_invalid_transcript_excluded_without_altering_raw_or_review(self):
        source = self.source('alice')
        attempt = self.packet(source, 1, 300, 330,
            [self.seg(299, 310, 'before'), self.seg(328, 338, 'past'), self.seg(320, 319, 'backwards')])
        originals = {p: p.read_bytes() for p in [attempt / 'transcript.json', attempt.parent / 'review.json']}
        self.assertEqual(enrich(source)['invalid_transcript_segments'], 3)
        evidence = read(attempt / 'evidence.json')
        self.assertEqual(evidence['valid_segments'], [])
        self.assertEqual(len(evidence['tracks'][0]['spans'][0]['frames']), 2)
        self.assertIsNone(evidence['tracks'][0]['spans'][0]['speech'])
        for path, content in originals.items():
            self.assertEqual(path.read_bytes(), content)
        self.assertEqual(build_index([source], self.out)['invalid_transcript_segments'], 3)
        self.assertEqual(search_index(self.out, 'past')['hits'], [])

    def test_search_retains_all_packets_and_independent_pov_clocks(self):
        a, b = self.source('alice'), self.source('bob')
        self.packet(a, 0, 0, 315, [self.seg(10, 12, 'boss defeated')])
        self.packet(a, 1, 285, 615, [self.seg(310, 312, 'boss defeated again')])
        self.packet(b, 0, 0, 315, [self.seg(92, 94, 'boss defeated')])
        self.assertEqual(build_index([a, b], self.out)['searchable_lines'], 3)
        result = search_index(self.out, 'boss defeated')
        self.assertEqual({(h['source_id'], h['start_sec']) for h in result['hits']},
                         {('alice', 10), ('alice', 310), ('bob', 92)})
        self.assertEqual([s['prepared_packets'] for s in result['coverage']], [2, 1])
        self.assertEqual([s['total_packets'] for s in result['coverage']], [3, 3])
        for hit in result['hits']:
            self.assertEqual(hit['occurrences'][0]['audio_stream'], 1)
            self.assertTrue(Path(hit['occurrences'][0]['evidence_file']).is_file())
        first = read(self.out / 'index.json')['build']
        self.assertTrue(build_index([a, b], self.out)['reused'])
        self.assertEqual(read(self.out / 'index.json')['build'], first)

    def test_exact_overlap_groups_provenance_but_repeated_lines_survive(self):
        a = self.source('alice')
        phrase = '100% boss_ "down"'
        self.packet(a, 0, 0, 315, [self.seg(290, 292, phrase), self.seg(294, 296, phrase)])
        self.packet(a, 1, 285, 615, [self.seg(290, 292, phrase)])
        build_index([a], self.out)
        hits = search_index(self.out, phrase)['hits']
        self.assertEqual(len(hits), 2)
        repeated = next(h for h in hits if h['start_sec'] == 290)
        self.assertEqual(len(repeated['occurrences']), 2)
        self.assertNotEqual(repeated['occurrences'][0]['transcript_file'], repeated['occurrences'][1]['transcript_file'])

    def test_stale_index_rejected_and_rebuild_replaces_previous_text(self):
        a = self.source('alice')
        attempt = self.packet(a, 0, 0, 315, [self.seg(10, 12, 'oldword')])
        build_index([a], self.out)
        transcript = read(attempt / 'transcript.json')
        transcript['segments'][0]['text'] = 'newword'
        write(attempt / 'transcript.json', transcript)
        with self.assertRaisesRegex(ValueError, 'stale'):
            search_index(self.out, 'oldword')
        self.assertFalse(build_index([a], self.out)['reused'])
        self.assertEqual(search_index(self.out, 'oldword')['hits'], [])
        self.assertEqual(len(search_index(self.out, 'newword')['hits']), 1)
        self.packet(a, 1, 285, 615, [self.seg(400, 401, 'newword')])
        with self.assertRaisesRegex(ValueError, 'stale'):
            search_index(self.out, 'newword')
        build_index([a], self.out)
        self.assertEqual(len(search_index(self.out, 'newword')['hits']), 2)

    def test_failed_rebuild_leaves_published_index_intact(self):
        a, b = self.source('alice'), self.source('bob')
        self.packet(a, 0, 0, 315, [self.seg(10, 12, 'hello')])
        info = read(b / 'source.json')
        info['path'] = read(a / 'source.json')['path']
        write(b / 'source.json', info)
        build_index([a], self.out)
        previous = (self.out / 'index.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'duplicate media'):
            build_index([a, b], self.out)
        self.assertEqual((self.out / 'index.json').read_bytes(), previous)
        self.assertEqual(len(search_index(self.out, 'hello')['hits']), 1)

    def test_limit_and_stream_provenance_are_explicit(self):
        a = self.source('alice')
        self.packet(a, 0, 0, 315, [self.seg(10, 12, 'hello', 1), self.seg(10, 12, 'hello', 2),
                    self.seg(20, 22, 'hello again')])
        build_index([a], self.out)
        result = search_index(self.out, 'hello', limit=1)
        self.assertTrue(result['at_limit'])
        self.assertEqual(len(result['hits']), 1)
        hits = search_index(self.out, 'hello')['hits']
        first = next(h for h in hits if h['start_sec'] == 10)
        self.assertEqual({o['audio_stream'] for o in first['occurrences']}, {1, 2})
        with self.assertRaises(ValueError):
            search_index(self.out, 'hello', limit=201)


if __name__ == '__main__':
    unittest.main()
