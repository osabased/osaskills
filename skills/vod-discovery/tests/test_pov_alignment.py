from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from pov_alignment import align, evidence_lines
from vod import write


def code(number):
    return ''.join(chr(97 + int(digit)) for digit in str(number))


def sentence(tag, number):
    return f'x{tag}{code(number)} y{tag}{code(number)} z{tag}{code(number)}'


class Alignment(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def prepared(self, name, segments, region=None, duration=1200):
        folder = self.root / name
        write(folder / 'source.json', {'id': name, 'path': str(self.root / (name + '.mp4')), 'duration_sec': duration})
        attempt = folder / 'packet-0000' / 'attempt-test'
        write(attempt / 'packet.json', {'source_id': name, 'start_sec': 0, 'end_sec': duration,
                                        'core_start_sec': 0, 'core_end_sec': duration})
        write(attempt / 'transcript.json', {'status': 'transcribed', 'streams': {'1': 'transcribed'}, 'segments': [
            {'start': t - 1, 'end': t + 1, 'text': text, 'audio_stream': 1} for t, text in segments]})
        write(folder / 'packet-0000' / 'complete.json', {'attempt': attempt.name})
        if region:
            write(folder / 'region-text' / 'chat.json', {'schema': 'vod-region-text/v1', 'source_id': name, 'lines': [
                {'first_sec': t, 'last_sec': t + 3, 'text': text} for t, text in region]})
        return folder

    def shared_scene(self, offset, times, tag='s'):
        main = [(t, sentence(tag, i)) for i, t in enumerate(times)]
        alt = [(t + offset, text) for t, text in main]
        return main, alt

    def test_shared_speech_gives_the_offset_and_quiet_gaps(self):
        main, alt = self.shared_scene(30.2, [10 * i for i in range(1, 8)] + [800 + 10 * i for i in range(7)])
        main += [(100 + 7 * i, sentence('m', i)) for i in range(20)]
        alt += [(400 + 9 * i, sentence('a', i)) for i in range(20)]
        report = align(self.prepared('main', main), [self.prepared('alt', alt)])
        entry = report['alternates'][0]
        self.assertEqual(entry['status'], 'candidates')
        span = entry['spans'][0]
        self.assertAlmostEqual(span['alt_equals_main_plus_sec'], 30.2, delta=1)
        self.assertEqual(span['status'], 'candidate_needs_review')
        self.assertGreater(span['score'], span['strongest_chance_score'])
        self.assertEqual(span['supporting_by_kind'], {'speech': 14, 'screen': 0})
        self.assertEqual(len(span['quiet_gaps']), 1)
        self.assertAlmostEqual(span['quiet_gaps'][0]['from_main_sec'], 70, delta=1)

    def test_unrelated_speech_is_unresolved(self):
        main = [(10 * i, sentence('m', i)) for i in range(1, 30)]
        alt = [(10 * i + 3, sentence('a', i)) for i in range(1, 30)]
        report = align(self.prepared('main', main), [self.prepared('alt', alt)])
        self.assertEqual(report['alternates'][0]['status'], 'unresolved')
        self.assertEqual(report['alternates'][0]['spans'], [])

    def test_screen_text_aligns_when_nobody_shares_speech(self):
        times = [20 + 15 * i for i in range(12)]
        main_region = [(t, 'chat ' + sentence('c', i)) for i, t in enumerate(times)]
        alt_region = [(t - 12, text) for t, text in main_region]
        report = align(self.prepared('main', [], main_region), [self.prepared('alt', [], alt_region)])
        span = report['alternates'][0]['spans'][0]
        self.assertAlmostEqual(span['alt_equals_main_plus_sec'], -12, delta=1)
        self.assertEqual(span['supporting_by_kind'], {'speech': 0, 'screen': 12})

    def test_region_text_from_another_source_is_rejected(self):
        folder = self.prepared('main', [])
        write(folder / 'region-text' / 'chat.json', {'schema': 'vod-region-text/v1', 'source_id': 'other', 'lines': []})
        with self.assertRaisesRegex(ValueError, 'does not belong'):
            evidence_lines(folder)


if __name__ == '__main__':
    unittest.main()
