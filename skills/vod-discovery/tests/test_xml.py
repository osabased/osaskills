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
        c = r.find('./project/children/clip')
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

    def test_stereo_channels_form_one_group_without_losing_right_channel(self):
        c = ET.fromstring(build_xml(self.markers, self.probes)).find('./project/children/clip')
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
        c = ET.fromstring(build_xml(self.markers, self.probes)).find('./project/children/clip')
        tracks = c.findall('./media/audio/track')
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0].get('premiereTrackType'), 'Mono')
        self.assertEqual(tracks[0].find('clipitem').get('premiereChannelType'), 'mono')

    def test_fractional_frame_quantization_is_bounded(self):
        self.probes['a']['streams'][0]['r_frame_rate'] = '30000/1001'
        c = ET.fromstring(build_xml(self.markers, self.probes)).find('./project/children/clip')
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
