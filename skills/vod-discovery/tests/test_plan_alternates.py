import contextlib
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from plan_alternates import parse_accept, parse_covered, place
from review_timeline import main as build_timeline
from vod import write


def event(eid, status, start, end, source='main'):
    return {'id': eid, 'title': eid, 'marker_title': eid.title(), 'marker_summary': 'Something happens.', 'status': status,
            'why': 'Because.', 'perspectives': [{'source_id': source, 'start_sec': start, 'end_sec': end, 'role': 'action',
                                                 'alignment': 'observed', 'uncertainty_sec': 0, 'evidence': 'frames'}]}


def span(offset, first, last, gaps=()):
    return {'alt_equals_main_plus_sec': offset, 'offset_spread_sec': 2, 'tolerance_sec': 3,
            'first_support_main_sec': first, 'last_support_main_sec': last, 'supporting_utterances': 20,
            'supporting_by_kind': {'speech': 5, 'screen': 15},
            'quiet_gaps': [{'from_main_sec': a, 'to_main_sec': b} for a, b in gaps]}


class Placement(unittest.TestCase):
    def setUp(self):
        self.data = {'sources': [{'id': 'main', 'duration_sec': 600, 'label': 'Main'},
                                 {'id': 'alt', 'duration_sec': 400, 'label': 'Alt'}],
                     'events': [event('a', 'candidate', 100, 130), event('b', 'candidate', 135, 160),
                                event('c', 'context', 200, 230), event('d', 'candidate', 300, 330)]}
        self.alignment = {'main_source_id': 'main', 'alternates': [{'source_id': 'alt', 'spans': [span(50, 90, 340)]}]}

    def run_place(self, covered=None, spans=None):
        if spans:
            self.alignment['alternates'][0]['spans'] = spans
        return place(self.data, self.alignment, [('alt', 0)], covered or {}, ('candidate',), 10, 'sheets in work/pairs')

    def test_nearby_candidates_share_one_excerpt_translated_by_the_offset(self):
        placed, unchecked, skipped = self.run_place()
        first = placed[0]
        self.assertEqual((first['source_start_sec'], first['source_end_sec']), (150, 210))
        self.assertEqual((first['main_anchor_sec'], first['source_anchor_sec']), (130, 180))
        self.assertEqual(first['event_id'], 'a')
        self.assertEqual(first['uncertainty_sec'], 3)
        self.assertIn('sheets in work/pairs', first['evidence'])
        self.assertEqual([p['event_id'] for p in placed], ['a', 'd'])
        self.assertEqual((unchecked, skipped), ([], []))

    def test_blocks_in_quiet_gaps_wait_for_a_visual_check_unless_confirmed(self):
        spans = [span(50, 90, 340, gaps=[(160, 320)])]
        placed, unchecked, _ = self.run_place(spans=spans)
        self.assertEqual([p['event_id'] for p in placed], ['a'])
        self.assertEqual(len(unchecked), 1)
        self.assertEqual((unchecked[0]['main_from_sec'], unchecked[0]['main_to_sec']), (300, 330))
        placed, unchecked, _ = self.run_place(covered={'alt': [(290, 340)]}, spans=spans)
        self.assertEqual([p['event_id'] for p in placed], ['a', 'd'])
        self.assertEqual(unchecked, [])

    def test_blocks_the_alternate_does_not_reach_are_skipped_and_partial_ones_clipped(self):
        placed, _, skipped = self.run_place(spans=[span(-335, 90, 340)])
        self.assertEqual(placed, [])
        self.assertEqual(len(skipped), 2)
        placed, _, skipped = self.run_place(spans=[span(-310, 90, 340)])
        self.assertEqual([(p['event_id'], p['source_start_sec'], p['source_end_sec']) for p in placed], [('d', 0, 20)])
        self.assertEqual(len(skipped), 1)

    def test_accept_and_covered_arguments(self):
        self.assertEqual(parse_accept('abc123:2'), ('abc123', 2))
        self.assertEqual(parse_covered(['alt=10-20.5', 'alt=30-40']), {'alt': [(10.0, 20.5), (30.0, 40.0)]})
        for bad in ('alt', 'alt:x'):
            with self.assertRaises(ValueError):
                parse_accept(bad)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'needs ffmpeg')
class TimelineWithPlacedAlternates(unittest.TestCase):
    def test_alternates_without_markers_build_into_a_timeline_with_merged_cuts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, seconds in (('main', 12), ('alt', 10)):
                subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', f'testsrc=duration={seconds}:size=320x180:rate=30',
                                '-f', 'lavfi', '-i', f'sine=duration={seconds}', '-c:v', 'mpeg4', '-c:a', 'aac',
                                str(root / f'{name}.mp4')], check=True)
            data = {'schema_version': 1, 'sources': [
                {'id': 'main', 'path': str(root / 'main.mp4'), 'duration_sec': 12, 'label': 'Main'},
                {'id': 'alt', 'path': str(root / 'alt.mp4'), 'duration_sec': 10, 'label': 'Alt'}],
                'events': [event('a', 'candidate', 2, 4), event('b', 'candidate', 6, 8), event('c', 'context', 10, 11)]}
            alignment = {'main_source_id': 'main', 'alternates': [{'source_id': 'alt', 'spans': [span(1, 0, 12)]}]}
            placed, _, _ = place(data, alignment, [('alt', 0)], {}, ('candidate',), 5, '')
            write(root / 'events.json', data)
            write(root / 'plan.json', {'title': 'Test', 'main_sources': ['main'], 'alternates': placed})
            with contextlib.redirect_stdout(io.StringIO()):
                build_timeline(['--events', str(root / 'events.json'), '--plan', str(root / 'plan.json'),
                                '--out', str(root / 'out.xml'), '--close-gaps-sec', '5'])
            sequence = ET.parse(root / 'out.xml').getroot().find('.//sequence')
            main, alt = sequence.findall('./media/video/track')
            labels = [c.findtext('labels/label2') for c in main.findall('clipitem')]
            self.assertEqual(labels, [None, 'Mango', None])
            self.assertEqual([(c.findtext('start'), c.findtext('end')) for c in main.findall('clipitem')],
                             [('0', '60'), ('60', '240'), ('240', '360')])
            clip = alt.find('clipitem')
            self.assertEqual((clip.findtext('start'), clip.findtext('end'), clip.findtext('enabled')), ('60', '240', 'FALSE'))


if __name__ == '__main__':
    unittest.main()
