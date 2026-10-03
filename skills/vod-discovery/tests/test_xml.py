import copy
from fractions import Fraction
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from premiere_xml import build_xml


class XmlDelivery(unittest.TestCase):
    def setUp(self):
        self.markers = {'sources': [{'id': 'a', 'path': str(Path('a & b.mp4').resolve()),
            'duration_sec': 300, 'markers': [{'key': 'e1', 'name': 'Kill & Reaction',
            'comments': 'Alice kills the boss.\nPOV: 03:15\nRef [VOD:e1]', 'start_sec': 108, 'end_sec': 119}]}]}
        self.probes = {'a': {'streams': [{'codec_type': 'video', 'r_frame_rate': '60/1',
            'width': 1920, 'height': 1080}, {'codec_type': 'audio', 'channels': 2, 'sample_rate': '48000'}]}}

    def test_master_source_markers_and_media_references(self):
        r = ET.fromstring(build_xml(self.markers, self.probes))
        self.assertEqual(r.findall('.//sequence'), [])
        c = r.find('.//clip')
        self.assertEqual(c.findtext('marker/in'), '6480')
        self.assertEqual(c.findtext('marker/out'), '7140')
        self.assertEqual(c.findtext('marker/name'), 'Kill & Reaction')
        self.assertEqual(c.findtext('marker/comment'), 'Alice kills the boss. / POV: 03:15 / Ref [VOD:e1]')
        f = c.find('./media/video/track/clipitem/file')
        self.assertIn('a%20%26%20b.mp4', f.findtext('pathurl'))
        references = c.findall('./media/audio/track/clipitem/file')
        self.assertEqual([x.get('id') for x in references], [f.get('id')] * 2)

    def test_direct_xml_input_cannot_bypass_presentation_contract(self):
        for changes in [{'name': 'Kill [VOD:e1]'}, {'comments': 'Ref [VOD:wrong]'},
                        {'comments': 'Description without provenance'}]:
            data = copy.deepcopy(self.markers)
            data['sources'][0]['markers'][0].update(changes)
            with self.assertRaises(ValueError): build_xml(data, self.probes)

    def test_interleaved_pov_parts_share_bins_and_references_stay_valid(self):
        original = self.markers['sources'][0]
        self.markers['sources'] = [dict(copy.deepcopy(original), id=sid, label=label, pov=pov,
            path=str(Path(filename).resolve())) for sid, label, pov, filename in [
                ('a', 'Alice part 1', 'Alice & friends', 'a1.mp4'),
                ('b', 'Bob', 'Bob', 'b.mp4'),
                ('c', 'Alice part 2', 'Alice & friends', 'a2.mp4')]]
        self.probes.update(b=copy.deepcopy(self.probes['a']), c=copy.deepcopy(self.probes['a']))
        root = ET.fromstring(build_xml(self.markers, self.probes))
        top = root.find('./project/children')
        self.assertEqual(top.findall('clip'), [])
        self.assertEqual([b.findtext('name') for b in top.findall('bin')], ['01 Media'])
        bins = top.findall('bin/children/bin')
        self.assertEqual([b.findtext('name') for b in bins], ['Alice & friends', 'Bob'])
        self.assertEqual([c.get('id') for c in bins[0].findall('children/clip')],
                         ['vod-master-0', 'vod-master-2'])
        clips = root.findall('.//clip')
        self.assertEqual(len(clips), 3)
        items = {c.get('id'): c for c in root.findall('.//clipitem')}
        for master in clips:
            self.assertEqual(master.findtext('marker/name'), 'Kill & Reaction')
            for item in master.findall('.//clipitem'):
                self.assertEqual(item.findtext('masterclipid'), master.get('id'))
                for link in item.findall('link'):
                    self.assertEqual(items[link.findtext('linkclipref')].findtext('masterclipid'), master.get('id'))
        self.assertEqual(len([f for f in root.findall('.//file') if f.find('pathurl') is not None]), 3)

    def test_empty_export_has_no_empty_bins(self):
        root = ET.fromstring(build_xml({'sources': []}, {}))
        self.assertEqual(list(root.find('./project/children')), [])

    def test_stereo_channels_form_one_group_without_losing_right_channel(self):
        c = ET.fromstring(build_xml(self.markers, self.probes)).find('.//clip')
        tracks = c.findall('./media/audio/track')
        self.assertEqual([t.get('currentExplodedTrackIndex') for t in tracks], ['0', '1'])
        for channel, track in enumerate(tracks, 1):
            self.assertEqual(track.get('totalExplodedTrackCount'), '2')
            self.assertEqual(track.get('premiereTrackType'), 'Stereo')
            item = track.find('clipitem')
            self.assertEqual(item.get('premiereChannelType'), 'stereo')
            self.assertEqual(item.findtext('sourcetrack/trackindex'), str(channel))
            links = [x for x in item.findall('link') if x.findtext('mediatype') == 'audio']
            self.assertEqual([x.findtext('groupindex') for x in links], ['1', '1'])

    def test_mono_is_not_duplicated_into_stereo(self):
        self.probes['a']['streams'][1]['channels'] = 1
        c = ET.fromstring(build_xml(self.markers, self.probes)).find('.//clip')
        tracks = c.findall('./media/audio/track')
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0].get('premiereTrackType'), 'Mono')
        self.assertEqual(tracks[0].find('clipitem').get('premiereChannelType'), 'mono')

    def test_fractional_frame_quantization_is_bounded(self):
        self.probes['a']['streams'][0]['r_frame_rate'] = '30000/1001'
        c = ET.fromstring(build_xml(self.markers, self.probes)).find('.//clip')
        self.assertEqual(c.findtext('rate/ntsc'), 'TRUE')
        actual = Fraction(int(c.findtext('marker/in'))) / Fraction(30000, 1001)
        self.assertLessEqual(abs(actual - 108), Fraction(1001, 60000))

    def test_unvalidated_source_layouts_fail(self):
        cases = [lambda p: p['a']['streams'].append(copy.deepcopy(p['a']['streams'][1])),
                 lambda p: p['a']['streams'][0].update(r_frame_rate='31/1'),
                 lambda p: p['a']['streams'][0].update(tags={'timecode': '01:00:00:00'})]
        for change in cases:
            p = copy.deepcopy(self.probes)
            change(p)
            with self.assertRaises(ValueError):
                build_xml(self.markers, p)


if __name__ == '__main__':
    unittest.main()
