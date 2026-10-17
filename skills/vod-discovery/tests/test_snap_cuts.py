from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from snap_cuts import pauses, snap, snap_events, snap_view, SILENCE_DB, SILENCE_MIN_SEC
from vod import export_events, write


def line(start, end):
    return {'start': start, 'end': end}


class SnapCuts(unittest.TestCase):
    def test_pauses_join_speech_gaps_and_audio_silences(self):
        found = pauses([line(0, 2), line(2.1, 5), line(9, 12)], [(5.5, 5.9), (10, 10.4)], 20)
        self.assertEqual(found, [(0, 0), (5, 9), (10, 10.4), (12, 20)])
        self.assertEqual(pauses([line(0, 2)], [(9.0, 9.4)], 20), [(0, 0), (2, 20)])

    def test_cut_lands_in_the_pause_nearest_the_lead_in(self):
        found = [(0, 0), (5, 9), (30, 31)]
        self.assertEqual(snap(8, 10, found, -1), 8)
        self.assertEqual(snap(12, 14, found, -1), 8.75)
        self.assertEqual(snap(33, 31, found, 1), None)

    def test_cut_never_enters_the_moment(self):
        found = [(0, 0), (9.8, 10.4), (40, 45)]
        self.assertIsNone(snap(9, 10, found, -1))
        self.assertIsNone(snap(11, 10.2, found, 1))

    def test_unreachable_pauses_fall_back_to_lead_in_and_tail_with_a_note(self):
        view = {'start_sec': 100, 'end_sec': 120}
        result = snap_view(view, [(0, 0), (500, 510)], 600)
        self.assertEqual((result['cut_start_sec'], result['cut_end_sec']), (98, 121.5))
        self.assertEqual(len(result['cut_notes']), 2)

    def test_snapped_cuts_always_contain_the_marker(self):
        found = [(0, 0), (92, 93), (126, 127)]
        result = snap_view({'start_sec': 100, 'end_sec': 120}, found, 600)
        self.assertEqual((result['cut_start_sec'], result['cut_end_sec']), (92.75, 126.25))
        self.assertEqual(result['cut_notes'], [])


class EventsFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.media = self.root / 'main.mp4'
        self.folder = self.root / 'prepared'
        write(self.folder / 'source.json', {'id': 'main', 'path': str(self.media), 'duration_sec': 600})
        attempt = self.folder / 'packet-0000' / 'attempt-test'
        write(attempt / 'packet.json', {'source_id': 'main', 'start_sec': 0, 'end_sec': 600,
                                        'core_start_sec': 0, 'core_end_sec': 600})
        write(attempt / 'transcript.json', {'status': 'transcribed', 'streams': {'1': 'transcribed'}, 'segments': [
            {'start': 90, 'end': 95, 'text': 'before', 'audio_stream': 1},
            {'start': 125, 'end': 130, 'text': 'after', 'audio_stream': 1}]})
        write(self.folder / 'packet-0000' / 'complete.json', {'attempt': attempt.name})
        write(self.folder / 'silence.json', {'settings': {'noise_db': SILENCE_DB, 'min_sec': SILENCE_MIN_SEC},
                                             'silences': []})
        self.data = {'schema_version': 1, 'sources': [{'id': 'main', 'path': str(self.media), 'duration_sec': 600}],
                     'events': [{'id': 'e1', 'title': 'Boss', 'marker_title': 'Boss Down', 'marker_summary': 'The boss falls.',
                                 'status': 'candidate', 'why': 'Payoff.', 'perspectives': [{
                                     'source_id': 'main', 'start_sec': 100, 'end_sec': 120, 'role': 'action',
                                     'alignment': 'observed', 'uncertainty_sec': 0, 'evidence': 'frames'}]}]}

    def tearDown(self):
        self.temp.cleanup()

    def test_events_gain_cuts_in_the_gaps_between_speech(self):
        summary = snap_events(self.data, {'main': self.folder})
        view = self.data['events'][0]['perspectives'][0]
        self.assertEqual(summary, {'snapped': 1, 'mid_speech': 0})
        self.assertEqual((view['cut_start_sec'], view['cut_end_sec']), (98, 121.5))
        export_events(self.data)

    def test_prepared_folder_from_another_recording_is_rejected(self):
        self.data['sources'][0]['path'] = str(self.root / 'other.mp4')
        with self.assertRaisesRegex(ValueError, 'different recording'):
            snap_events(self.data, {'main': self.folder})

    def test_cut_inside_the_marker_is_rejected_on_export(self):
        view = self.data['events'][0]['perspectives'][0]
        view.update(cut_start_sec=105, cut_end_sec=125)
        with self.assertRaisesRegex(ValueError, 'Cut points must contain'):
            export_events(self.data)
        view.update(cut_start_sec=90, cut_end_sec=700)
        with self.assertRaisesRegex(ValueError, 'Cut points must contain'):
            export_events(self.data)


if __name__ == '__main__':
    unittest.main()
