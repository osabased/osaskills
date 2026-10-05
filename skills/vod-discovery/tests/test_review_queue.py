import copy
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from review_queue import (SCHEMA, Store, Conflict, Preferences, DEFAULT_KEYS, atomic_json, build_lock,
                          cards_for, digest, file_hash, identity, initialize, make_server,
                          render_preview, selected_xml)


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
        self.assertEqual(len(main.findall('clipitem')),4)
        self.assertEqual([(p.findtext('start'),p.findtext('end'),p.findtext('labels/label2'))
                          for p in main.findall('clipitem')],
                         [('0','6480',None),('6480','7140','Mango'),
                          ('7140','36000',None),('36000','84000',None)])
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
        main = ET.fromstring(xml).find('.//sequence/media/video/track')
        self.assertEqual([(p.findtext('start'),p.findtext('end')) for p in main.findall('clipitem')
                          if p.findtext('labels/label2')=='Mango'],[('6480','7140'),('15000','16200')])

    def test_secondary_only_selection_retains_unmarked_main_without_invented_cuts(self):
        self.state['decisions']['social']['decision']='keep'
        before = copy.deepcopy((self.data,self.plan,self.state))
        xml,ids=selected_xml(self.data,self.plan,self.probes,self.state['decisions'])
        root=ET.fromstring(xml)
        self.assertEqual(ids,['social'])
        parts=root.findall('.//sequence/media/video/track/clipitem')
        self.assertEqual([(p.findtext('start'),p.findtext('end'),p.findtext('labels/label2')) for p in parts],
                         [('0','36000',None),('36000','84000',None)])
        self.assertEqual(root.findtext('.//clip/marker/name'),'Banter')
        self.assertEqual((self.data,self.plan,self.state),before)

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
        profile=Preferences(self.root/'shared'/'keys.json')
        server=make_server(self.store,preferences=profile)
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
        keys=json.loads(request('GET','/api/keys')[1])
        self.assertEqual(keys['profile']['keys'],DEFAULT_KEYS)
        changed=dict(keys['profile'],keys={**DEFAULT_KEYS,'pov':'KeyV'})
        self.assertEqual(request('POST','/api/keys',json.dumps(changed),headers)[0],200)
        self.assertEqual(request('POST','/api/keys',json.dumps(changed),headers)[0],409)
        self.assertEqual(Preferences(profile.path).read()['keys']['pov'],'KeyV')
        self.assertEqual(Store(self.root).state()['revision'],1)

    def test_occupied_port_is_rejected_instead_of_sharing_a_listener(self):
        with make_server(self.store) as server:
            with self.assertRaises(OSError):
                make_server(self.store, server.server_port)

    def test_playback_metadata_uses_local_plan_without_changing_saved_choices(self):
        self.store.mutate(dict(revision=0,event_id='fight',decision='keep',note='Preserve me',position_sec=4))
        before={name:(self.root/name).read_bytes() for name in ('queue.json','state.json','plan.json')}
        playback=self.store.playback_queue()
        link=playback['cards'][0]['sync_links'][0]
        self.assertEqual(link,dict(main_source_id='a',source_id='b',offset_sec=82,
                         source_start_sec=190,source_end_sec=200,uncertainty_sec=1))
        self.assertEqual(playback['cards'][1]['sync_links'],[])  # Later reaction is not simultaneous.
        for name,raw in before.items():self.assertEqual((self.root/name).read_bytes(),raw)
        self.assertNotIn('sync_links',self.store.queue['cards'][0])

    def test_timeline_stacks_local_alternates_and_matches_exported_part_origins(self):
        data=self.store.playback_queue()['timeline']
        self.assertEqual(data['total'],1400)
        self.assertEqual(data['parts'][1]['start'],600)
        self.assertEqual([l['id'] for l in data['lanes']],['b','main'])
        alt=next(s for s in data['segments'] if s['lane']=='b')
        self.assertEqual((alt['start'],alt['end'],alt['offset'],alt['view']),(108,118,82,1))
        self.assertNotIn('social',[s['eid'] for s in data['segments']])
        self.data['sources'][0]['duration_sec']=600.011
        atomic_json(self.root/'events.json',self.data)
        updated=self.store.timeline_data()
        self.assertAlmostEqual(updated['parts'][1]['start'],600+1/60)
        xml,_=selected_xml(self.data,self.plan,self.probes,self.state['decisions'],'all')
        second=ET.fromstring(xml).find(".//sequence/media/video/track/clipitem[masterclipid='vod-master-2']")
        self.assertAlmostEqual(updated['parts'][1]['start'],int(second.findtext('start'))/60)

    def test_keyboard_profile_shares_across_instances_and_rejects_lost_updates(self):
        path=self.root/'shared'/'keys.json'
        first,second=Preferences(path),Preferences(path)
        self.assertFalse(path.exists())
        self.assertEqual(first.read()['revision'],0)
        value=first.save(dict(revision=0,keys={**DEFAULT_KEYS,'pov':'KeyV'}))
        self.assertEqual(second.read(),value)
        with self.assertRaises(Conflict):second.save(dict(revision=0,keys=DEFAULT_KEYS))
        before=path.read_bytes()
        for keys in [{**DEFAULT_KEYS,'pov':'Digit1'},{**DEFAULT_KEYS,'pov':'Ctrl+KeyW'},dict(pov='KeyV')]:
            with self.assertRaises(ValueError):second.save(dict(revision=1,keys=keys))
            self.assertEqual(path.read_bytes(),before)
        self.assertEqual(second.save(dict(revision=1,keys=DEFAULT_KEYS))['keys'],DEFAULT_KEYS)

    def test_profile_os_lock_prevents_cross_server_writes(self):
        first=Preferences(self.root/'shared'/'keys.json')
        second=Preferences(first.path)
        with first.exclusive():
            with self.assertRaises(Conflict):second.save(dict(revision=0,keys=DEFAULT_KEYS))
        self.assertEqual(second.save(dict(revision=0,keys=DEFAULT_KEYS))['revision'],1)

    def build_inputs(self):
        folder = self.root / 'inputs'
        folder.mkdir(exist_ok=True)
        events, plan = folder / 'events.json', folder / 'plan.json'
        atomic_json(events, self.data); atomic_json(plan, self.plan)
        metadata = copy.deepcopy(self.probes)
        for value in metadata.values():
            for index, stream in enumerate(value['streams']):
                stream['index'] = index
        durations = {s['id']: s['duration_sec'] for s in self.data['sources']}
        def source_probe(path):
            sid = Path(path).stem
            return metadata[sid], durations[sid]
        return events, plan, source_probe

    @staticmethod
    def fake_preview(source, metadata, view, dest):
        dest.write_bytes(('preview ' + dest.name).encode())
        return dict(sha256=file_hash(dest),
                    duration_sec=view['preview_end_sec'] - view['preview_start_sec'])

    def test_failed_build_resumes_verified_previews_and_repairs_corruption(self):
        events, plan, source_probe = self.build_inputs()
        for corrupt in (False, True):
            with self.subTest(corrupt=corrupt):
                out = self.root / ('build-corrupt' if corrupt else 'build-resume')
                def fail_one(source, metadata, view, dest):
                    if dest.name == '0000-01.mp4':
                        raise RuntimeError('Interrupted encoder')
                    return self.fake_preview(source, metadata, view, dest)
                with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=fail_one):
                    with self.assertRaisesRegex(RuntimeError, 'Interrupted'):
                        initialize(events, plan, out, jobs=1)
                self.assertFalse((out / 'queue.json').exists())
                record = json.loads((out / 'build.json').read_text())
                self.assertIn('0000-00.mp4', record['completed'])
                reused = set(record['completed'])
                original = {name: (out / 'previews' / name).stat().st_mtime_ns for name in reused}
                if corrupt:
                    (out / 'previews' / '0000-00.mp4').write_bytes(b'corrupt')
                    reused.remove('0000-00.mp4')
                with patch('review_queue.render_preview', side_effect=self.fake_preview) as renderer:
                    initialize(events, plan, out, jobs=2, resume=True)
                rendered = {call.args[3].name for call in renderer.call_args_list}
                self.assertEqual(rendered, {'0000-00.mp4', '0000-01.mp4', '0001-00.mp4', '0002-00.mp4'} - reused)
                for name in reused:
                    self.assertEqual((out / 'previews' / name).stat().st_mtime_ns, original[name])
                store = Store(out)
                self.assertEqual(store.state()['revision'], 0)
                self.assertTrue(all(s['decision'] == 'unreviewed' for s in store.state()['decisions'].values()))

    def test_resume_rejects_changed_inputs_media_settings_and_snapshots(self):
        events, plan, source_probe = self.build_inputs()
        for change in ('events', 'media', 'padding', 'snapshot'):
            with self.subTest(change=change):
                out = self.root / ('changed-' + change)
                with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=RuntimeError('Interrupted')):
                    with self.assertRaises(RuntimeError):
                        initialize(events, plan, out, jobs=1)
                target = events if change == 'events' else self.root / 'a.mp4' if change == 'media' else out / 'probes.json'
                before, stat = target.read_bytes(), target.stat()
                if change != 'padding':
                    target.write_bytes(before + b' ')
                with patch('review_queue.render_preview') as renderer:
                    with self.assertRaisesRegex(ValueError, 'changed'):
                        initialize(events, plan, out, padding=4 if change == 'padding' else 3, resume=True)
                    renderer.assert_not_called()
                target.write_bytes(before)
                import os
                os.utime(target, ns=(stat.st_atime_ns, stat.st_mtime_ns))

    def test_parallel_build_is_bounded_and_completed_queue_preserves_choices(self):
        events, plan, source_probe = self.build_inputs()
        out = self.root / 'parallel-build'
        barrier, lock = threading.Barrier(2, timeout=3), threading.Lock()
        active = peak = 0
        def parallel_preview(*args):
            nonlocal active, peak
            with lock:
                active += 1; peak = max(peak, active)
            try:
                barrier.wait()
                return self.fake_preview(*args)
            finally:
                with lock:
                    active -= 1
        with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=parallel_preview):
            initialize(events, plan, out, jobs=2)
        self.assertEqual(peak, 2)
        store = Store(out)
        store.mutate(dict(revision=0, event_id='fight', decision='keep', note='Preserve'))
        before = (out / 'state.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'complete'):
            initialize(events, plan, out, resume=True)
        self.assertEqual((out / 'state.json').read_bytes(), before)

    def test_build_lock_prevents_two_preparers(self):
        with build_lock(self.root):
            with self.assertRaises(Conflict):
                with build_lock(self.root):
                    self.fail('Second preparer acquired the build lock')

    def test_invalid_preview_cannot_replace_completed_file(self):
        dest = self.root / 'validated.mp4'
        dest.write_bytes(b'previous validated preview')
        def encode(command, **kwargs):
            Path(command[-1]).write_bytes(b'incomplete preview')
        metadata = dict(streams=[dict(codec_type='video', index=0)])
        view = dict(preview_start_sec=10, preview_end_sec=20)
        with patch('review_queue.subprocess.run', side_effect=encode), patch('review_queue.probe', return_value=({}, 3)):
            with self.assertRaisesRegex(ValueError, 'duration'):
                render_preview(self.data['sources'][0], metadata, view, dest)
        self.assertEqual(dest.read_bytes(), b'previous validated preview')
        self.assertEqual(list(self.root.glob('*.tmp.mp4')), [])

    def test_invalid_worker_count_does_not_create_build(self):
        events, plan, _ = self.build_inputs()
        for jobs in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                initialize(events, plan, self.root / 'invalid-build', jobs=jobs)
        self.assertFalse((self.root / 'invalid-build').exists())

    def test_interruption_cancels_encodes_that_have_not_started(self):
        events, plan, source_probe = self.build_inputs()
        out = self.root / 'interrupted-build'
        release = threading.Event()
        rendered = []
        def blocked_preview(*args):
            rendered.append(args[3].name)
            if not release.wait(3):
                raise RuntimeError('Workers were not released')
            return self.fake_preview(*args)
        def interrupt(futures):
            timer = threading.Timer(.05, release.set)
            timer.daemon = True; timer.start()
            raise KeyboardInterrupt
        with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=blocked_preview), patch('review_queue.as_completed', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                initialize(events, plan, out, jobs=2)
        self.assertLessEqual(len(rendered), 2)
        self.assertFalse((out / 'queue.json').exists())
        self.assertTrue((out / 'build.json').exists())


if __name__=='__main__':unittest.main()
