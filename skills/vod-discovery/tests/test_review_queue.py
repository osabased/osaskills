import copy
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from review_queue import (SCHEMA, Store, Conflict, atomic_json, cards_for, digest,
                          file_hash, identity, make_server, selected_xml)


class ReviewQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        sources = []
        for sid, duration in [('a',600),('b',900),('c',800)]:
            path = self.root / (sid + '.mp4'); path.write_bytes(b'media')
            sources.append(dict(id=sid,path=str(path),label=sid,pov='Main' if sid in ('a','c') else 'Other',duration_sec=duration))
        def view(sid,start,end):
            return dict(source_id=sid,start_sec=start,end_sec=end,role='action',alignment='observed',uncertainty_sec=1,evidence='inspected notice')
        self.data = dict(schema_version=1,sources=sources,events=[
            dict(id='fight',title='A fight',marker_title='First Kill',marker_summary='The player wins.',status='candidate',why='outcome',perspectives=[view('a',108,119),view('b',190,202)]),
            dict(id='later',title='Later complaint',marker_title='No Help',marker_summary='The player complains.',status='uncertain',why='reaction',perspectives=[view('a',250,270)],related_events=[dict(event_id='fight',source_id='b',relationship='earlier')]),
            dict(id='social',title='Another conversation',marker_title='Banter',marker_summary='A conversation.',status='context',why='context',perspectives=[view('b',10,30)])])
        self.plan = dict(title='Review',main_sources=['a','c'],coverage_note='Pilot only',alternates=[dict(event_id='fight',source_id='b',main_source_id='a',source_start_sec=190,source_end_sec=200,source_anchor_sec=195,main_anchor_sec=113,uncertainty_sec=1,evidence='same notice',name='Fight')])
        self.probes={sid:{'streams':[dict(codec_type='video',r_frame_rate=fps,width=1920,height=1080),dict(codec_type='audio',channels=2,sample_rate='48000')]} for sid,fps in [('a','60/1'),('b','30/1'),('c','60/1')]}
        self.cards=cards_for(self.data,self.plan,3)
        (self.root/'previews').mkdir()
        for i,card in enumerate(self.cards):
            for j,view in enumerate(card['views']):
                view['file']=f'{i:04d}-{j:02d}.mp4'
                (self.root/'previews'/view['file']).write_bytes(b'0123456789')
        for name,value in [('events.json',self.data),('plan.json',self.plan),('probes.json',self.probes)]:atomic_json(self.root/name,value)
        self.queue=dict(schema=SCHEMA,cards=self.cards,coverage='Pilot',identities={s['id']:identity(s) for s in sources},snapshots={n:file_hash(self.root/n) for n in ('events.json','plan.json','probes.json')},inputs=[])
        atomic_json(self.root/'queue.json',self.queue)
        self.state=dict(schema=SCHEMA,queue_hash=digest(self.queue),revision=0,current_id='fight',decisions={e['id']:dict(decision='unreviewed',note='',view=0,positions={}) for e in self.data['events']},history=[])
        atomic_json(self.root/'state.json',self.state)
        self.store=Store(self.root)

    def test_persistence_resume_undo_and_conflicting_tab(self):
        state=self.store.mutate(dict(revision=0,event_id='fight',decision='keep',note='Use other angle',view=1,position_sec=4))
        reloaded=Store(self.root).state()
        self.assertEqual(reloaded,state)
        self.assertEqual(reloaded['decisions']['fight']['positions']['1'],4)
        with self.assertRaises(Conflict):self.store.mutate(dict(revision=0,event_id='fight',decision='skip'))
        state=self.store.mutate(dict(revision=1,event_id='later',decision='later'))
        state=self.store.mutate(dict(revision=2),undo=True)
        self.assertEqual(state['current_id'],'later')
        self.assertEqual(state['decisions']['later']['decision'],'unreviewed')
        self.assertEqual(state['decisions']['fight']['decision'],'keep')
        state=self.store.mutate(dict(revision=3),undo=True)
        self.assertEqual(state['decisions']['fight']['note'],'Use other angle')

    def test_invalid_save_cannot_destroy_previous_choices(self):
        before=(self.root/'state.json').read_bytes()
        for patch in [dict(decision='delete'),dict(view=-1),dict(note='x'*4001),dict(position_sec=float('nan')),dict(position_sec=9999)]:
            with self.assertRaises(ValueError):self.store.mutate(dict(revision=0,event_id='fight',**patch))
            self.assertEqual((self.root/'state.json').read_bytes(),before)

    def test_selected_export_keeps_full_main_grouped_audio_and_disabled_alternate(self):
        self.state['decisions']['fight']['decision']='keep'
        xml,ids=selected_xml(self.data,self.plan,self.probes,self.state['decisions'])
        root=ET.fromstring(xml)
        self.assertEqual(ids,['fight'])
        self.assertEqual([b.findtext('name') for b in root.findall('./project/children/bin')],['01 Media','02 Sequences'])
        seq=root.find('.//sequence')
        self.assertEqual(seq.findtext('duration'),'84000')
        main,alt=seq.findall('./media/video/track')
        self.assertEqual(len(main.findall('clipitem')),2)
        self.assertEqual(alt.findtext('clipitem/enabled'),'FALSE')
        self.assertEqual(alt.findtext('clipitem/in'),'11400')
        audio=seq.findall('./media/audio/track')
        self.assertEqual(len(audio),4)
        self.assertEqual(audio[2].attrib['premiereTrackType'],'Stereo')
        self.assertTrue(all(t.findtext('clipitem/enabled')=='FALSE' for t in audio[2:]))
        self.assertEqual([m.findtext('name') for m in root.findall('.//clip/marker')],['First Kill','First Kill'])

    def test_related_unselected_event_retains_reference_without_selecting_it(self):
        self.state['decisions']['later']['decision']='keep'
        xml,_=selected_xml(self.data,self.plan,self.probes,self.state['decisions'])
        root=ET.fromstring(xml)
        self.assertEqual([m.findtext('name') for m in root.findall('.//clip/marker')],['No Help'])
        self.assertIn('EARLIER b',root.findtext('.//clip/marker/comment'))
        self.assertEqual(len(root.findall('.//sequence/media/video/track')),1)

    def test_all_includes_uncertain_and_secondary_only_moments(self):
        with self.assertRaises(ValueError):selected_xml(self.data,self.plan,self.probes,self.state['decisions'])
        xml,ids=selected_xml(self.data,self.plan,self.probes,self.state['decisions'],'all')
        self.assertEqual(set(ids),{'fight','later','social'})
        self.assertEqual(len(ET.fromstring(xml).findall('.//clip/marker')),4)
        self.assertEqual([c['id'] for c in self.cards],['fight','later','social'])
        self.assertEqual(self.cards[0]['views'][1]['preview_start_sec'],187)

    def test_changed_media_or_snapshot_stops_export_without_touching_state(self):
        self.store.mutate(dict(revision=0,event_id='fight',decision='keep'))
        before=(self.root/'state.json').read_bytes()
        (self.root/'a.mp4').write_bytes(b'changed media')
        with self.assertRaises(ValueError):self.store.export(dict(revision=1))
        self.assertEqual((self.root/'state.json').read_bytes(),before)

    def test_exports_are_separate_snapshots_not_overwrites(self):
        self.store.mutate(dict(revision=0,event_id='fight',decision='keep'))
        a=self.store.export(dict(revision=1)); b=self.store.export(dict(revision=1))
        self.assertNotEqual(a['path'],b['path'])
        self.assertEqual(Path(a['path']).read_bytes(),Path(b['path']).read_bytes())
        self.assertTrue(Path(a['path']).with_name('decisions.json').exists())

    def test_http_ranges_access_controls_and_persistent_save(self):
        server=make_server(self.store)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        port=server.server_port
        def request(method,path,body=None,headers=None):
            c=http.client.HTTPConnection('127.0.0.1',port)
            c.request(method,path,body=body,headers=headers or {})
            r=c.getresponse();result=(r.status,r.read(),dict(r.getheaders()));c.close();return result
        status,raw,_=request('GET','/api/queue');self.assertEqual(status,200)
        token=json.loads(raw)['token']
        status,raw,headers=request('GET','/previews/0000-00.mp4',headers={'Range':'bytes=2-5'})
        self.assertEqual((status,raw),(206,b'2345'));self.assertEqual(headers['Content-Range'],'bytes 2-5/10')
        self.assertEqual(request('GET','/previews/0000-00.mp4',headers={'Range':'bytes=20-'})[0],416)
        self.assertEqual(request('GET','/../state.json')[0],404)
        self.assertEqual(request('GET','/api/queue',headers={'Host':'example.org'})[0],403)
        body=json.dumps(dict(revision=0,event_id='fight',decision='keep'))
        self.assertEqual(request('POST','/api/save',body,{'Content-Type':'application/json'})[0],403)
        headers={'Content-Type':'application/json','X-Review-Token':token,'Origin':f'http://127.0.0.1:{port}'}
        self.assertEqual(request('POST','/api/save',body,headers)[0],200)
        self.assertEqual(request('POST','/api/save',body,headers)[0],409)
        self.assertEqual(Store(self.root).state()['decisions']['fight']['decision'],'keep')

    def test_occupied_port_is_rejected_instead_of_sharing_a_listener(self):
        with make_server(self.store) as server:
            with self.assertRaises(OSError):
                make_server(self.store, server.server_port)


if __name__=='__main__':unittest.main()
