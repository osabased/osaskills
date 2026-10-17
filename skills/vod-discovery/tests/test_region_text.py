from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from region_text import extract, merge_lines


def frame(t, *lines):
    return {'timestamp_sec': t, 'lines': [{'text': text} for text in lines]}


class MergeLines(unittest.TestCase):
    def test_a_line_seen_in_consecutive_samples_is_one_interval_despite_ocr_noise(self):
        found = merge_lines([frame(0, 'alice: hi lit or rat can i get some assistance'),
                             frame(3, 'alice: hi lit or rat can i get some assitånce', 'bob: lol'),
                             frame(6, 'bob: lol')], 3)
        self.assertEqual([(l['first_sec'], l['last_sec']) for l in found], [(0, 3), (3, 6)])
        self.assertEqual(found[0]['text'], 'alice: hi lit or rat can i get some assistance')

    def test_the_same_words_much_later_are_a_new_line(self):
        found = merge_lines([frame(0, 'carol has made the advancement'), frame(60, 'carol has made the advancement')], 3)
        self.assertEqual([l['first_sec'] for l in found], [0, 60])

    def test_fragments_without_two_real_words_are_dropped(self):
        self.assertEqual(merge_lines([frame(0, 'a 1 ,', 'ok', 'real words here')], 3)[0]['text'], 'real words here')
        self.assertEqual(len(merge_lines([frame(0, 'a 1 ,', 'ok')], 3)), 0)


@unittest.skipUnless(shutil.which('ffmpeg'), 'needs ffmpeg')
class Extraction(unittest.TestCase):
    def test_samples_carry_their_own_source_times_inside_the_window(self):
        import subprocess
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc=duration=20:size=320x180:rate=30',
                            '-c:v', 'mpeg4', str(root / 'v.mp4')], check=True)
            scratch = root / 'crops'
            scratch.mkdir()
            sampled = extract(root / 'v.mp4', 5, 17, '160:90:0:0', 3, 2, scratch)
            times = [t for t, _ in sampled]
            self.assertEqual(len(times), 4)
            self.assertAlmostEqual(times[0], 5, delta=.1)
            self.assertTrue(all(b - a >= 2.9 for a, b in zip(times, times[1:])))
            self.assertTrue(all(5 <= t <= 17 for t in times))


if __name__ == '__main__':
    unittest.main()
