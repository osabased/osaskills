from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audio_match import assess


def result(offsets, strengths, rank=10):
    return {'match_info': {'b.wav': {'offset_seconds': offsets, 'confidence': strengths}},
            'rankings': {'match_info': {'b.wav': rank}}}


class LocalAudioCandidates(unittest.TestCase):
    def test_known_delay_sign_and_independent_source_origins(self):
        fp = result([1.99692, 2.04336, 3.29723], [102171, 60, 39])
        corr = result([2, 1.997, 2.003, 7], [1, .16, .16, .1])
        report = assess(fp, corr, 100, 180)
        self.assertEqual(report['status'], 'candidate_needs_review')
        self.assertAlmostEqual(report['candidate_offset_b_minus_a_sec'], 82)
        self.assertAlmostEqual(assess(fp, corr, 0, 0)['candidate_offset_b_minus_a_sec'], 2)

    def test_high_rank_and_normalized_peak_are_not_proof(self):
        report = assess(result([0, 4], [11, 11], rank=10), result([0, 4], [1, .95], rank=10), 0, 0)
        self.assertEqual(report['status'], 'unresolved')
        self.assertIsNone(report['candidate_offset_b_minus_a_sec'])
        self.assertGreaterEqual(len(report['reasons']), 2)

    def test_disagreement_and_missing_match_remain_unresolved(self):
        for fp, corr in [(result([18.2, 1.06], [170, 8]), result([-2.01, 24], [1, .2])),
                         (None, result([2], [1]))]:
            report = assess(fp, corr, 145, 225)
            self.assertEqual(report['status'], 'unresolved')
            self.assertIsNone(report['candidate_offset_b_minus_a_sec'])

    def test_neighboring_peaks_do_not_masquerade_as_independent_offsets(self):
        fp = result([2.04336, 2.0898, -16.1], [282, 250, 13])
        corr = result([2.04175, 2.043625, 22.27875], [1, .544, .374])
        report = assess(fp, corr, 100, 180)
        self.assertEqual(report['status'], 'candidate_needs_review')
        self.assertAlmostEqual(report['candidate_offset_b_minus_a_sec'], 82.04175)


if __name__ == '__main__':
    unittest.main()
