"""Host path mapping (for example a Cowork VM mount) and export overwrite protection."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import premiere_xml
import review_timeline
import vod
from premiere_xml import build_xml, media_url
from review_queue import selected_xml
from vod import map_path, parse_path_map

VM = '/sessions/abc/mnt/VODs'


def probe_fixture(fps='60/1'):
    return {'streams': [{'codec_type': 'video', 'r_frame_rate': fps, 'width': 1920, 'height': 1080},
                        {'codec_type': 'audio', 'channels': 2, 'sample_rate': '48000'}], 'format': {}}


def events_fixture(root):
    return {'schema_version': 1,
            'sources': [{'id': 'main', 'path': str(root / 'main.mp4'), 'label': 'Main', 'pov': 'Main', 'duration_sec': 600},
                        {'id': 'alt', 'path': str(root / 'alt.mp4'), 'label': 'Alt', 'pov': 'Alt', 'duration_sec': 600}],
            'events': [{'id': 'e1', 'title': 'Boss', 'marker_title': 'Boss Defeated', 'marker_summary': 'Alice wins.',
                        'status': 'candidate', 'why': 'payoff',
                        'perspectives': [{'source_id': 'main', 'start_sec': 100, 'end_sec': 110, 'role': 'action',
                                          'alignment': 'observed', 'uncertainty_sec': 0, 'evidence': 'frames'},
                                         {'source_id': 'alt', 'start_sec': 120, 'end_sec': 130, 'role': 'reaction',
                                          'alignment': 'estimated', 'uncertainty_sec': 1, 'evidence': 'frames'}]}]}


def plan_fixture():
    return {'title': 'Review', 'main_sources': ['main'], 'alternates': [
        dict(source_id='alt', main_source_id='main', event_id='e1', name='Alt view', source_start_sec=120,
             source_end_sec=130, source_anchor_sec=121, main_anchor_sec=101, uncertainty_sec=1, evidence='notice')]}


def pathurls(xml):
    return [e.text for e in ET.fromstring(xml).iter('pathurl')]


class ParseAndMap(unittest.TestCase):
    def test_parse_rejects_malformed_and_relative_hosts(self):
        for bad in ['nohost', '=D:/VODs', '/vm=', '/vm=relative/dir']:
            with self.assertRaises(ValueError):
                parse_path_map([bad])
        self.assertEqual(parse_path_map(None), [])

    def test_longest_prefix_wins_and_separators_normalize(self):
        mapping = parse_path_map([f'{VM}=D:\\VODs', f'{VM}/bob/=E:/Bob'])
        self.assertEqual(map_path(f'{VM}/alice/a.mp4', mapping), 'D:/VODs/alice/a.mp4')
        self.assertEqual(map_path(f'{VM}/bob/b.mp4', mapping), 'E:/Bob/b.mp4')

    def test_prefix_must_end_at_a_path_boundary_and_unmatched_sources_fail(self):
        mapping = parse_path_map([f'{VM}=D:/VODs'])
        with self.assertRaises(ValueError):
            map_path(VM + '-other/a.mp4', mapping)
        with self.assertRaises(ValueError):
            map_path('/elsewhere/a.mp4', mapping)

    def test_no_map_keeps_the_local_path(self):
        self.assertEqual(map_path('/media/a.mp4', []), '/media/a.mp4')

    def test_windows_local_prefixes_match_case_insensitively(self):
        mapping = parse_path_map(['C:/Shared=/Volumes/Shared'])
        self.assertEqual(map_path('c:\\shared\\x.mp4', mapping), '/Volumes/Shared/x.mp4')


class MediaUrls(unittest.TestCase):
    def test_windows_host_path_uses_premiere_localhost_form_on_any_os(self):
        self.assertEqual(media_url('D:/VODs/a b.mp4'), 'file://localhost/D%3a/VODs/a%20b.mp4')
        self.assertEqual(media_url('D:\\VODs\\a.mp4'), 'file://localhost/D%3a/VODs/a.mp4')

    def test_posix_and_unc_paths(self):
        self.assertEqual(media_url('/Users/ed/a.mp4'), 'file:///Users/ed/a.mp4')
        self.assertEqual(media_url('\\\\nas\\share\\a.mp4'), 'file://nas/share/a.mp4')


class MappedExports(unittest.TestCase):
    def setUp(self):
        self.root = Path(VM)
        self.data = events_fixture(self.root)
        self.markers = vod.export_events(self.data)
        self.probes = {'main': probe_fixture(), 'alt': probe_fixture('30/1')}
        self.mapping = parse_path_map([f'{VM}=D:/VODs'])

    def test_source_xml_writes_host_paths(self):
        urls = pathurls(build_xml(self.markers, self.probes, path_map=self.mapping))
        self.assertEqual(urls, ['file://localhost/D%3a/VODs/main.mp4', 'file://localhost/D%3a/VODs/alt.mp4'])

    def test_timeline_writes_host_paths(self):
        xml = review_timeline.build_review(self.markers, self.probes, plan_fixture(), self.mapping)
        self.assertEqual(set(pathurls(xml)), {'file://localhost/D%3a/VODs/main.mp4', 'file://localhost/D%3a/VODs/alt.mp4'})

    def test_queue_export_writes_host_paths(self):
        decisions = {'e1': {'decision': 'keep'}}
        xml, selected = selected_xml(self.data, plan_fixture(), self.probes, decisions, 'keep', self.mapping)
        self.assertEqual(selected, ['e1'])
        self.assertTrue(all(url.startswith('file://localhost/D%3a/VODs/') for url in pathurls(xml)))

    def test_unmapped_source_fails_instead_of_leaking_a_vm_path(self):
        with self.assertRaises(ValueError):
            build_xml(self.markers, self.probes, path_map=parse_path_map(['/other=D:/VODs']))


class CliOutputs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        data = events_fixture(self.root)
        for source in data['sources']:
            Path(source['path']).write_bytes(b'')
        self.events = self.root / 'events.json'
        self.events.write_text(json.dumps(data), encoding='utf-8')
        self.plan = self.root / 'plan.json'
        self.plan.write_text(json.dumps(plan_fixture()), encoding='utf-8')
        fake = lambda path: (probe_fixture(), 600.0)
        for module in (premiere_xml, review_timeline):
            patcher = patch.object(module, 'probe', side_effect=fake)
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_main(self, main, argv):
        with contextlib.redirect_stdout(io.StringIO()):
            main(argv)

    def test_source_xml_refuses_overwrite_without_force(self):
        out = self.root / 'markers.xml'
        argv = ['--events', str(self.events), '--out', str(out), '--path-map', f'{self.root}=D:/VODs']
        self.run_main(premiere_xml.main, argv)
        self.assertIn('file://localhost/D%3a/VODs/main.mp4', out.read_text(encoding='utf-8'))
        out.write_text('editor copy', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.run_main(premiere_xml.main, argv)
        self.assertEqual(out.read_text(encoding='utf-8'), 'editor copy')
        self.run_main(premiere_xml.main, argv + ['--force'])
        self.assertIn('<xmeml', out.read_text(encoding='utf-8'))

    def test_timeline_refuses_overwrite_without_force(self):
        out = self.root / 'timeline.xml'
        argv = ['--events', str(self.events), '--plan', str(self.plan), '--out', str(out)]
        self.run_main(review_timeline.main, argv)
        out.write_text('editor copy', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.run_main(review_timeline.main, argv)
        self.assertEqual(out.read_text(encoding='utf-8'), 'editor copy')
        self.run_main(review_timeline.main, argv + ['--force'])
        self.assertIn('<sequence', out.read_text(encoding='utf-8'))

    def test_marker_json_export_maps_paths_for_the_panel(self):
        out = self.root / 'markers.json'
        argv = ['vod.py', 'export', '--events', str(self.events), '--out', str(out),
                '--path-map', f'{self.root}=D:/VODs']
        with patch.object(sys, 'argv', argv), contextlib.redirect_stdout(io.StringIO()):
            vod.main()
        paths = [s['path'] for s in json.loads(out.read_text(encoding='utf-8'))['sources']]
        self.assertEqual(paths, ['D:/VODs/main.mp4', 'D:/VODs/alt.mp4'])

    def test_cli_errors_are_one_line_messages(self):
        def failing():
            raise ValueError('Marker name must be a clean 1–4-word label')
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as exit_info:
            vod.run_cli(failing)
        self.assertEqual(exit_info.exception.code, 1)
        self.assertEqual(stderr.getvalue(), 'ERROR: Marker name must be a clean 1–4-word label\n')


if __name__ == '__main__':
    unittest.main()
