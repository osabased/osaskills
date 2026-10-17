import contextlib
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from pov_pairs import pairs
from vod import read


class Args:
    def __init__(self, **values):
        self.__dict__.update(values)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'needs ffmpeg')
class PairSheets(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name, seconds in (('main', 20), ('alt', 12)):
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', f'testsrc=duration={seconds}:size=320x180:rate=30',
                            '-c:v', 'mpeg4', str(self.root / f'{name}.mp4')], check=True)

    def tearDown(self):
        self.temp.cleanup()

    def make(self, *args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            pairs(self.args(*args, **kwargs))

    def args(self, times, offset, out='pairs', rows=4):
        return Args(main_source=str(self.root / 'main.mp4'), alt_source=str(self.root / 'alt.mp4'), offset_sec=offset,
                    main_times=times, rows_per_sheet=rows, out=str(self.root / out))

    def test_pairs_use_the_offset_and_record_what_was_skipped(self):
        self.make([2, 8, 15], -3)
        record = read(self.root / 'pairs' / 'pairs.json')
        self.assertEqual([(p['main_sec'], p['alt_sec']) for p in record['pairs']], [(8, 5)])
        self.assertEqual([s['main_sec'] for s in record['skipped']], [2, 15])
        self.assertEqual(record['sheets'], ['pairs_01.jpg'])
        self.assertTrue((self.root / 'pairs' / 'pairs_01.jpg').is_file())

    def test_rows_split_across_sheets_and_existing_evidence_is_kept(self):
        self.make([1, 2, 3], 0, rows=2)
        self.assertEqual(read(self.root / 'pairs' / 'pairs.json')['sheets'], ['pairs_01.jpg', 'pairs_02.jpg'])
        with self.assertRaisesRegex(ValueError, 'new --out'):
            pairs(self.args([1], 0))

    def test_times_outside_both_recordings_fail_loudly(self):
        with self.assertRaisesRegex(ValueError, 'inside both'):
            pairs(self.args([30], 0, out='none'))


if __name__ == '__main__':
    unittest.main()
