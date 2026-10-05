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
        for source, pov in zip(self.markers['sources'], ['Main', 'Alternate', 'Main']):
            source['pov'] = pov
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
        top = root.find('./project/children')
        self.assertEqual([b.findtext('name') for b in top.findall('bin')], ['01 Media', '02 Sequences'])
        self.assertEqual(top.findall('sequence'), [])
        sequence_bin = top.findall('bin')[1]
        self.assertEqual(len(sequence_bin.findall('children/sequence')), 1)
        self.assertEqual(root.findtext('.//clip/marker/name'), 'Boss Defeated')
        self.assertEqual(root.findtext('.//clip/marker/comment'),
                         'Alice defeats the boss. / Ref [VOD:e1]')
        seq = root.find('.//sequence')
        self.assertEqual(seq.findtext('duration'), str(1400*60))
        main, alt = seq.findall('./media/video/track')
        parts = main.findall('clipitem')
        self.assertEqual([p.findtext('masterclipid') for p in parts], ['vod-master-0']*3 + ['vod-master-2'])
        self.assertEqual([(p.findtext('start'),p.findtext('end')) for p in parts],
                         [('0','6480'),('6480','7140'),('7140','36000'),('36000','84000')])
        self.assertEqual([p.findtext('labels/label2') for p in parts], [None,'Mango',None,None])
        clip = alt.find('clipitem')
        self.assertEqual(clip.findtext('masterclipid'), 'vod-master-1')
        self.assertEqual((clip.findtext('start'),clip.findtext('end')), ('6480','7080'))
        self.assertEqual((clip.findtext('in'),clip.findtext('out')), ('11400','12000'))
        self.assertEqual(clip.findtext('enabled'),'FALSE')
        self.assertEqual(clip.findtext('labels/label2'),'Mango')
        audio = seq.findall('./media/audio/track')
        self.assertEqual(len(audio),4)  # Two stereo tracks, channel records are grouped by Premiere.
        for track in audio[2:]:
            self.assertEqual(track.findtext('clipitem/enabled'),'FALSE')
            self.assertEqual(track.findtext('clipitem/in'),'11400')
        self.assertEqual(len({c.get('id') for c in seq.findall('.//clipitem')}),15)
        # Each edit has its own linked video/stereo records at identical cuts.
        for medium in ('video','audio'):
            for track in seq.findall(f'./media/{medium}/track'):
                for item in track.findall('clipitem'):
                    if item.findtext('labels/label2') is None:
                        self.assertIsNone(item.find('labels'))  # No empty override on ordinary footage.
                    for link in item.findall('link'):
                        kind = link.findtext('mediatype')
                        target_track = seq.findall(f'./media/{kind}/track')[int(link.findtext('trackindex'))-1]
                        target = target_track.findall('clipitem')[int(link.findtext('clipindex'))-1]
                        self.assertEqual(target.get('id'), link.findtext('linkclipref'))
                        for tag in ('start','end','in','out','enabled','labels/label2'):
                            self.assertEqual(target.findtext(tag), item.findtext(tag))
                        if kind == 'audio': self.assertEqual(link.findtext('groupindex'),'1')
        self.assertEqual(root.findall('.//clip/labels'), [])
        self.assertEqual(root.findall('.//clip/media/video/track/clipitem/labels'), [])

    def test_overlapping_nested_adjacent_and_duplicate_ranges_keep_every_edge_once(self):
        source = self.markers['sources'][0]
        template = source['markers'][0]
        # Deliberately unsorted; the last range touches the end of the source.
        ranges = [(20,40),(0,15),(10,30),(20,40),(11,12),(40,50),(590,600)]
        source['markers'] = [dict(template,key=f'e{i}',comments=f'Observed outcome. [VOD:e{i}]',start_sec=a,end_sec=b)
                             for i,(a,b) in enumerate(ranges)]
        self.plan['alternates'] = []
        seq = ET.fromstring(build_review(self.markers,self.probes,self.plan)).find('.//sequence')
        parts = seq.findall('./media/video/track/clipitem')
        boundaries = [0,10,11,12,15,20,30,40,50,590,600]
        self.assertEqual([(int(p.findtext('in')),int(p.findtext('out'))) for p in parts[:-1]],
                         [(a*60,b*60) for a,b in zip(boundaries,boundaries[1:])])
        self.assertEqual([p.findtext('labels/label2') for p in parts],
                         ['Mango']*8 + [None,'Mango',None])
        self.assertEqual(sum(int(p.findtext('end'))-int(p.findtext('start')) for p in parts),84000)
        for left,right in zip(parts,parts[1:]):
            self.assertEqual(left.findtext('end'),right.findtext('start'))

    def test_second_part_boundaries_use_its_source_clock_and_sequence_origin(self):
        self.markers['sources'][2]['markers'] = [dict(self.markers['sources'][0]['markers'][0],
                                                   start_sec=0,end_sec=2)]
        seq = ET.fromstring(build_review(self.markers,self.probes,self.plan)).find('.//sequence')
        parts = seq.find('./media/video/track').findall('clipitem')[-2:]
        self.assertEqual([(p.findtext('in'),p.findtext('out')) for p in parts],[('0','120'),('120','48000')])
        self.assertEqual([(p.findtext('start'),p.findtext('end')) for p in parts],
                         [('36000','36120'),('36120','84000')])
        self.assertEqual([p.findtext('labels/label2') for p in parts],['Mango',None])

    def test_ntsc_rounding_matches_source_markers_with_mono_or_no_audio(self):
        self.plan.update(main_sources=['a'],alternates=[])
        self.markers['sources'] = self.markers['sources'][:1]
        source = self.markers['sources'][0]
        source['markers'][0].update(start_sec=1.001,end_sec=1.02)
        for channels in (0,1):
            with self.subTest(channels=channels):
                self.probes['a']['streams'] = [dict(codec_type='video',r_frame_rate='30000/1001',width=1920,height=1080)]
                if channels:
                    self.probes['a']['streams'].append(dict(codec_type='audio',channels=channels,sample_rate='48000'))
                root = ET.fromstring(build_review(self.markers,self.probes,self.plan))
                seq = root.find('.//sequence')
                parts = seq.findall('./media/video/track/clipitem')
                self.assertEqual([(p.findtext('in'),p.findtext('out')) for p in parts],
                                 [('0','30'),('30','31'),('31','17982')])
                marker = root.find('.//clip/marker')
                for tag in ('in','out'):self.assertEqual(marker.findtext(tag),parts[1].findtext(tag))
                audio = seq.findall('./media/audio/track')
                self.assertEqual(len(audio),channels)
                if channels:
                    self.assertEqual(audio[0].get('premiereTrackType'),'Mono')
                    self.assertEqual(len(audio[0].findall('clipitem')),3)

    def test_whole_source_moment_has_no_empty_edge_clips(self):
        self.markers['sources'][0]['markers'][0].update(start_sec=0,end_sec=600)
        seq = ET.fromstring(build_review(self.markers,self.probes,self.plan)).find('.//sequence')
        parts = seq.find('./media/video/track').findall('clipitem')
        self.assertEqual(len(parts),2)
        self.assertEqual([p.findtext('labels/label2') for p in parts],['Mango',None])

    def test_invalid_alignment_and_overlaps_are_rejected(self):
        for change in [lambda p:p['alternates'][0].update(source_anchor_sec=220),
                       lambda p:p['alternates'][0].update(main_anchor_sec=0),
                       lambda p:p['alternates'][0].update(evidence=''),
                       lambda p:p['alternates'].append(copy.deepcopy(p['alternates'][0]))]:
            plan=copy.deepcopy(self.plan)
            change(plan)
            with self.assertRaises(ValueError):build_review(self.markers,self.probes,plan)


if __name__ == '__main__':unittest.main()
