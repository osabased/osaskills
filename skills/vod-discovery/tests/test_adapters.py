"""Run with Python's unittest; no models or user media needed."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("vod", Path(__file__).parents[1] / "scripts" / "vod.py")
vod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vod)


def fixture():
    return {"schema_version": 1, "sources": [
        {"id": "a", "path": "D:/VODs/a.mp4", "duration_sec": 8000},
        {"id": "b", "path": "D:/VODs/b.mp4", "duration_sec": 8100}],
        "events": [{"id": "e1", "title": "Quiet progression", "why": "A new path opens", "status": "uncertain",
        "marker_title": "Path Opens", "marker_summary": "Alice opens a path into the next area.",
        "perspectives": [
            {"source_id": "a", "start_sec": 7200.125, "end_sec": 7220.5, "role": "action",
             "alignment": "observed", "uncertainty_sec": 0, "evidence": "A detail frames 1–8"},
            {"source_id": "b", "start_sec": 7228.5, "end_sec": 7240, "role": "reaction",
             "alignment": "estimated", "uncertainty_sec": 2.5, "evidence": "B frame 8; shared dialogue"}]}]}


class ExportTests(unittest.TestCase):
    def test_preserves_uncertain_and_independent_source_clocks(self):
        result = vod.export_events(fixture())
        a, b = [s["markers"][0] for s in result["sources"]]
        self.assertEqual(a["start_sec"], 7200.125)
        self.assertEqual(b["start_sec"], 7228.5)
        self.assertEqual(a["name"], "Path Opens")
        self.assertIn("CHECK", a["comments"])
        self.assertIn("[VOD:e1]", a["comments"])
        self.assertIn("02:00:28.500", a["comments"])
        self.assertIn("CHECK sync ±2.5s", a["comments"])

    def test_compact_copy_preserves_evidence_and_related_times(self):
        data = fixture()
        original_evidence = data['events'][0]['perspectives'][0]['evidence']
        data['events'][0].update(marker_title='Path opens', marker_summary='Unlocks the next area.',
                                 review_note='Dialogue is unclear.')
        later = copy.deepcopy(data['events'][0])
        later.update(id='e2', related_events=[{'event_id': 'e1', 'source_id': 'b', 'relationship': 'earlier'}])
        later['perspectives'] = [later['perspectives'][0]]
        data['events'].append(later)
        out = vod.export_events(data)
        first, second = out['sources'][0]['markers']
        self.assertTrue(first['name'].startswith('Path opens'))
        self.assertNotIn(original_evidence, first['comments'])
        self.assertEqual(data['events'][0]['perspectives'][0]['evidence'], original_evidence)
        self.assertIn('EARLIER b 02:00:28.500', second['comments'])
        self.assertIn('CHECK: Dialogue is unclear.', first['comments'])
        self.assertEqual(first['key'], 'e1')

    def test_perspective_copy_and_provenance_stay_separate_from_labels(self):
        data = fixture()
        before = copy.deepcopy(data)
        data['events'][0]['perspectives'][1].update(marker_title="Victory Cheer",
            marker_summary="Bob cheers when the path opens.")
        a, b = [s['markers'][0] for s in vod.export_events(data)['sources']]
        self.assertEqual(b['name'], 'Victory Cheer')
        self.assertTrue(b['comments'].startswith('Bob cheers when the path opens.'))
        for m in [a, b]:
            self.assertNotIn('VOD:', m['name'])
            self.assertNotIn('CHECK', m['name'])
            self.assertEqual(m['comments'].count('[VOD:e1]'), 1)
        self.assertEqual(data['events'][0]['title'], before['events'][0]['title'])
        self.assertEqual(data['events'][0]['why'], before['events'][0]['why'])

    def test_missing_or_description_like_display_copy_requires_authoring(self):
        for field in ['marker_title', 'marker_summary']:
            data = fixture(); del data['events'][0][field]
            with self.subTest(field=field), self.assertRaises(ValueError): vod.export_events(data)
        for label in ['Johan gears up before his return', 'Gear Up [VOD:e1]', 'Gear Up | CHECK',
                      'Gear Up\n', 'Gear...', 'Gear…', '', '  Gear Up', 'Gear  Up']:
            data = fixture(); data['events'][0]['marker_title'] = label
            with self.subTest(label=label), self.assertRaises(ValueError): vod.export_events(data)
        data = fixture(); data['events'][0]['perspectives'][0]['marker_title'] = 'A very long descriptive marker name'
        with self.assertRaises(ValueError): vod.export_events(data)

    def test_missing_related_event_fails(self):
        data = fixture()
        data['events'][0]['related_events'] = [{'event_id': 'missing', 'source_id': 'b', 'relationship': 'earlier'}]
        with self.assertRaises(ValueError): vod.export_events(data)

    def test_invalid_intervals_fail(self):
        for start, end in [(-1, 2), (1, 1), (10, 9), (1, 9000), (float("nan"), 3), (1, float("inf")), (False, 3)]:
            data = fixture()
            data["events"][0]["perspectives"][0].update(start_sec=start, end_sec=end)
            with self.subTest(start=start, end=end), self.assertRaises(ValueError): vod.export_events(data)

    def test_estimate_requires_uncertainty(self):
        data = fixture(); data["events"][0]["perspectives"][1]["uncertainty_sec"] = 0
        with self.assertRaises(ValueError): vod.export_events(data)

    def test_unknown_source_and_duplicate_ids_fail(self):
        data = fixture(); data["events"][0]["perspectives"][1]["source_id"] = "missing"
        with self.assertRaises(ValueError): vod.export_events(data)
        data = fixture(); data["events"].append(copy.deepcopy(data["events"][0]))
        with self.assertRaises(ValueError): vod.export_events(data)

    def test_duplicate_media_paths_fail(self):
        data = fixture(); data["sources"][1]["path"] = "d:\\vods\\a.mp4"
        with self.assertRaises(ValueError): vod.export_events(data)

    def test_empty_events_are_valid(self):
        data = fixture(); data["events"] = []
        self.assertEqual(vod.export_events(data)["sources"], [])


if __name__ == "__main__": unittest.main()
