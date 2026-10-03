import copy
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from review_timeline import build_review


class TimelineDelivery(unittest.TestCase):
    def setUp(self):
        self.markers = {'sources': [dict(id=s,path=str(Path(s+'.mp4').resolve()),duration_sec=d,markers=[])
                                   for s,d in [('a',600),('b',900),('c',800)]]}
        self.markers['sources'][0]['markers'] = [dict(key='e1', name='Boss Defeated',
            comments='Alice defeats the boss.\nRef [VOD:e1]', start_sec=108, end_sec=119)]
        self.probes = {s:{'streams':[{'codec_type':'video','r_frame_rate':fps,'width':1920,'height':1080},
                                    {'codec_type':'audio','channels':2,'sample_rate':'48000'}]}
                       for s,fps in [('a','60/1'),('b','30/1'),('c','60/1')]}
        self.plan = {'title':'Review','main_sources':['a','c'],'alternates':[
            dict(source_id='b', main_source_id='a', source_start_sec=190,source_end_sec=200,
                 source_anchor_sec=195,main_anchor_sec=113,uncertainty_sec=1,evidence='shared visible notice',name='fight')]}

    def test_full_main_parts_mixed_rates_disabled_alternate_and_audio_groups(self):
        root = ET.fromstring(build_review(self.markers,self.probes,self.plan))
        self.assertEqual(root.findtext('./project/children/clip/marker/name'), 'Boss Defeated')
        self.assertEqual(root.findtext('./project/children/clip/marker/comment'),
                         'Alice defeats the boss. / Ref [VOD:e1]')
        seq = root.find('.//sequence')
        self.assertEqual(seq.findtext('duration'), str(1400*60))
        main, alt = seq.findall('./media/video/track')
        parts = main.findall('clipitem')
        self.assertEqual([(p.findtext('start'),p.findtext('end')) for p in parts], [('0','36000'),('36000','84000')])
        clip = alt.find('clipitem')
        self.assertEqual((clip.findtext('start'),clip.findtext('end')), ('6480','7080'))
        self.assertEqual((clip.findtext('in'),clip.findtext('out')), ('11400','12000'))
        self.assertEqual(clip.findtext('enabled'),'FALSE')
        audio = seq.findall('./media/audio/track')
        self.assertEqual(len(audio),4)  # Two stereo tracks, channel records are grouped by Premiere.
        for track in audio[2:]:
            self.assertEqual(track.findtext('clipitem/enabled'),'FALSE')
            self.assertEqual(track.findtext('clipitem/in'),'11400')
        self.assertEqual(len({c.get('id') for c in seq.findall('.//clipitem')}),9)

    def test_invalid_alignment_and_overlaps_are_rejected(self):
        for change in [lambda p:p['alternates'][0].update(source_anchor_sec=220),
                       lambda p:p['alternates'][0].update(main_anchor_sec=0),
                       lambda p:p['alternates'][0].update(evidence=''),
                       lambda p:p['alternates'].append(copy.deepcopy(p['alternates'][0]))]:
            plan=copy.deepcopy(self.plan)
            change(plan)
            with self.assertRaises(ValueError):build_review(self.markers,self.probes,plan)


if __name__ == '__main__':unittest.main()
