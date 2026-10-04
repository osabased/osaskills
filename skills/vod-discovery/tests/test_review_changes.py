import copy
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import test_review_queue as fixtures
from review_queue import (Conflict, DEFAULT_KEYS, LEGACY_KEYS, Preferences, Store, atomic_json,
                          build_lock, digest, file_hash, initialize, main, make_server, update_queue)
from review_migration import prepare_migration


class ReviewChangesTests(unittest.TestCase):
    build_inputs = fixtures.ReviewQueueTests.build_inputs
    fake_preview = staticmethod(fixtures.ReviewQueueTests.fake_preview)

    def setUp(self):
        fixtures.ReviewQueueTests.setUp(self)
        for value in self.probes.values():
            for index, stream in enumerate(value['streams']):
                stream['index'] = index
        atomic_json(self.root / 'probes.json', self.probes)
        self.queue['snapshots']['probes.json'] = file_hash(self.root / 'probes.json')
        atomic_json(self.root / 'queue.json', self.queue)
        self.state['queue_hash'] = digest(self.queue)
        atomic_json(self.root / 'state.json', self.state)
        self.store = Store(self.root)
        self.addCleanup(self.store.context.close)
        self.destination = tempfile.TemporaryDirectory()
        self.addCleanup(self.destination.cleanup)
        self.out = Path(self.destination.name) / 'revised'

    def request(self, eid='fight', index=0, direction='before', preview=None):
        view = preview or self.store.context.view(eid, index)
        return dict(event_id=eid, view=index, direction=direction,
                    preview_start_sec=view['preview_start_sec'], preview_end_sec=view['preview_end_sec'])

    def test_migration_rebinds_transcript_on_unchanged_media_and_archives_exact_snapshot(self):
        from review_transcript import SCHEMA as TRANSCRIPT_SCHEMA
        rows = [dict(id=digest([sid, 110]), source_id=sid, audio_stream=1, start_sec=110, end_sec=114,
                     text='Synthetic speech', refs=[]) for sid in ('a', 'b')]
        attached = dict(schema=TRANSCRIPT_SCHEMA, queue_hash=self.store.queue_hash, rows=rows,
            coverage=[dict(source_id=sid, core_ranges_sec=[[0, 600]]) for sid in ('a', 'b')],
            unmapped_sources=[], excluded_invalid_segments=0, inputs={}, limitations='Software fixture')
        atomic_json(self.root / 'transcript.json', attached)
        raw = (self.root / 'transcript.json').read_bytes()
        revised = self.migrate()
        self.assertEqual(revised.transcript.summary()['status'], 'ready')
        self.assertEqual(revised.transcript.rows, rows)
        self.assertEqual(revised.transcript.snapshot['queue_hash'], revised.queue_hash)
        self.assertEqual((self.out / 'migration' / 'previous' / 'transcript.json').read_bytes(), raw)

    def test_migration_does_not_reuse_transcript_for_replaced_source_media(self):
        from review_transcript import SCHEMA as TRANSCRIPT_SCHEMA
        atomic_json(self.root / 'transcript.json', dict(schema=TRANSCRIPT_SCHEMA, queue_hash=self.store.queue_hash,
            rows=[dict(id=digest(['a', 110]), source_id='a', audio_stream=1, start_sec=110, end_sec=114,
                       text='Old media speech', refs=[])], coverage=[dict(source_id='a', core_ranges_sec=[[0, 600]])],
            unmapped_sources=[], excluded_invalid_segments=0, inputs={}, limitations='Software fixture'))
        changed = copy.deepcopy(self.data)
        replacement_folder = self.root / 'replacement'; replacement_folder.mkdir()
        replacement = replacement_folder / 'a.mp4'; replacement.write_bytes(b'changed original')
        changed['sources'][0]['path'] = str(replacement)
        revised = self.migrate(data=changed)
        self.assertEqual(revised.transcript.rows, [])
        self.assertEqual(revised.transcript.summary()['coverage'], [])

    def complete(self, request, renderer=None):
        with patch('review_queue.render_preview', side_effect=renderer or self.fake_preview):
            job = self.store.context.request(request)
            self.store.context.close()
        return self.store.context.status(job['id']) if 'id' in job else job

    def reviewed(self):
        for eid, decision, index, position in [('fight', 'keep', 1, 4), ('later', 'later', 0, 6), ('social', 'skip', 0, 3)]:
            revision = self.store.state()['revision']
            self.store.mutate(dict(revision=revision, event_id=eid, decision=decision,
                                   note='Note for ' + eid, view=index, position_sec=position))

    def migrate(self, data=None, plan=None, **kwargs):
        events, placement, source_probe = self.build_inputs()
        atomic_json(events, data or self.data); atomic_json(placement, plan or self.plan)
        with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=self.fake_preview):
            update_queue(self.root, events, placement, self.out, **kwargs)
        return Store(self.out)

    def test_context_preserves_state_event_bounds_and_original_export(self):
        self.reviewed()
        original = {name: (self.root / name).read_bytes() for name in ('queue.json', 'state.json', 'events.json', 'plan.json')}
        xml = Path(self.store.export(dict(revision=3))['path']).read_bytes()
        result = self.complete(self.request())
        self.assertEqual(result['status'], 'ready')
        view = result['preview']
        self.assertEqual((view['preview_start_sec'], view['preview_end_sec']), (90, 122))
        self.assertEqual((view['start_sec'], view['end_sec']), (108, 119))
        self.assertEqual(self.store.playback_queue()['cards'][0]['sync_links'][0]['source_end_sec'], 200)
        for name, content in original.items():
            self.assertEqual((self.root / name).read_bytes(), content)
        self.assertEqual(Path(self.store.export(dict(revision=3))['path']).read_bytes(), xml)

    def test_source_position_before_original_preview_survives_reload(self):
        self.complete(self.request())
        state = self.store.mutate(dict(revision=0, event_id='fight', source_position_sec=94, note='Earlier setup', decision='later'))
        self.assertEqual(state['decisions']['fight']['source_positions']['0'], 94)
        restored = Store(self.root)
        self.assertEqual(restored.state(), state)
        self.assertEqual(restored.context.view('fight', 0)['preview_start_sec'], 90)
        with self.assertRaises(ValueError):
            restored.mutate(dict(revision=1, event_id='fight', source_position_sec=89))
        self.assertEqual(restored.state(), state)

    def test_context_retry_is_idempotent_and_media_start_is_bounded(self):
        request = self.request('social')
        result = self.complete(request)
        self.assertEqual(result['preview']['preview_start_sec'], 0)
        before = (self.root / 'context.json').read_bytes()
        with patch('review_queue.render_preview') as renderer:
            repeated = self.store.context.request(request)
        self.assertEqual(repeated['status'], 'ready')
        renderer.assert_not_called()
        self.assertEqual((self.root / 'context.json').read_bytes(), before)
        self.assertEqual(self.complete(self.request())['preview']['preview_start_sec'], 90)
        self.assertEqual(self.complete(self.request(direction='after'))['preview']['preview_end_sec'], 137)

    def test_context_encoder_failure_can_retry_without_losing_good_preview(self):
        first = self.complete(self.request())
        before = (self.root / 'context.json').read_bytes()
        request = self.request(direction='after')
        failed = self.complete(request, lambda *args: (_ for _ in ()).throw(RuntimeError('Encoder failed')))
        self.assertEqual(failed['status'], 'error')
        self.assertEqual((self.root / 'context.json').read_bytes(), before)
        self.assertTrue((self.root / 'previews' / first['preview']['file']).is_file())
        self.assertEqual(self.complete(request)['preview']['preview_end_sec'], 137)

    def test_failed_context_publication_preserves_registered_preview(self):
        first = self.complete(self.request())
        before = (self.root / 'context.json').read_bytes()
        real_write = atomic_json
        def fail_publication(path, value):
            if Path(path).name == 'context.json':
                raise OSError('Disk publication failed')
            return real_write(path, value)
        with patch('review_queue.atomic_json', side_effect=fail_publication):
            failed = self.complete(self.request(direction='after'))
        self.assertEqual(failed['status'], 'error')
        self.assertEqual((self.root / 'context.json').read_bytes(), before)
        self.assertEqual(self.store.context.view('fight', 0)['file'], first['preview']['file'])

    def test_duplicate_requests_coalesce_and_choices_save_during_encoding(self):
        entered, release = threading.Event(), threading.Event()
        def blocked(*args):
            entered.set()
            if not release.wait(3):
                raise RuntimeError('Test worker not released')
            return self.fake_preview(*args)
        request = self.request()
        with patch('review_queue.render_preview', side_effect=blocked) as renderer:
            first = self.store.context.request(request)
            self.assertTrue(entered.wait(2))
            second = self.store.context.request(request)
            self.assertEqual(first['id'], second['id'])
            with self.assertRaises(Conflict):
                self.store.context.request(self.request(direction='after'))
            self.store.mutate(dict(revision=0, event_id='fight', note='While encoding', decision='keep'))
            release.set(); self.store.context.executor.shutdown(wait=True); self.store.context.close()
            self.assertEqual(renderer.call_count, 1)
        self.assertEqual(self.store.state()['decisions']['fight']['decision'], 'keep')
        self.assertEqual(self.store.context.status(first['id'])['status'], 'ready')

    def test_context_worker_count_is_bounded(self):
        entered, release, lock = threading.Event(), threading.Event(), threading.Lock()
        active = peak = 0
        def blocked(*args):
            nonlocal active, peak
            with lock:
                active += 1; peak = max(peak, active)
                if active == 2: entered.set()
            try:
                if not release.wait(3): raise RuntimeError('Test worker not released')
                return self.fake_preview(*args)
            finally:
                with lock: active -= 1
        with patch('review_queue.render_preview', side_effect=blocked):
            for eid in ('fight', 'later', 'social'):
                self.store.context.request(self.request(eid))
            self.assertTrue(entered.wait(2)); self.assertEqual(peak, 2)
            release.set(); self.store.context.executor.shutdown(wait=True); self.store.context.close()
        self.assertEqual(len(self.store.context.record['completed']), 3)
        self.assertEqual(peak, 2)

    def test_source_change_during_extension_prevents_publication(self):
        def changed(*args):
            result = self.fake_preview(*args)
            (self.root / 'a.mp4').write_bytes(b'changed source')
            return result
        result = self.complete(self.request(), changed)
        self.assertEqual(result['status'], 'error')
        self.assertFalse((self.root / 'context.json').exists())
        self.assertEqual(self.store.context.view('fight', 0)['preview_start_sec'], 105)
        self.assertEqual(self.store.state()['revision'], 0)

    def test_damaged_context_is_rebuilt_on_idempotent_retry(self):
        request = self.request()
        first = self.complete(request)
        dest = self.root / 'previews' / first['preview']['file']
        expected = dest.read_bytes(); dest.write_bytes(b'broken cache')
        second = self.complete(request)
        self.assertEqual(second['status'], 'ready')
        self.assertEqual(dest.read_bytes(), expected)
        self.assertEqual(second['preview']['preview_start_sec'], 90)

    def test_restart_repairs_missing_context_before_resuming_added_source_position(self):
        first = self.complete(self.request())
        self.store.mutate(dict(revision=0, event_id='fight', source_position_sec=94, note='Added context'))
        before = (self.root / 'state.json').read_bytes()
        (self.root / 'previews' / first['preview']['file']).unlink()
        with patch('review_queue.render_preview', side_effect=self.fake_preview) as renderer:
            restored = Store(self.root)
        self.assertEqual(renderer.call_count, 1)
        self.assertEqual(restored.context.view('fight', 0)['preview_start_sec'], 90)
        self.assertEqual(restored.state()['decisions']['fight']['source_positions']['0'], 94)
        self.assertEqual((self.root / 'state.json').read_bytes(), before)

    def test_context_http_registry_keeps_prior_urls_and_rejects_unknown_files(self):
        first = self.complete(self.request())['preview']['file']
        second = self.complete(self.request(direction='after'))['preview']['file']
        server = make_server(self.store, preferences=Preferences(self.root / 'isolated-keys.json'))
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        def get(path, method='GET', body=None, headers=None):
            c = http.client.HTTPConnection('127.0.0.1', server.server_port)
            c.request(method, path, body=body, headers=headers or {})
            r = c.getresponse(); result = (r.status, r.read()); c.close(); return result
        for name in (first, second): self.assertEqual(get('/previews/' + name)[0], 200)
        self.assertEqual(get('/previews/context-' + '0' * 64 + '.mp4')[0], 404)
        self.assertEqual(get('/api/context', 'POST', json.dumps(self.request()))[0], 403)
        token = json.loads(get('/api/queue')[1])['token']
        headers = {'Origin': f'http://127.0.0.1:{server.server_port}', 'Content-Type': 'application/json', 'X-Review-Token': token}
        self.assertEqual(get('/api/context', 'POST', json.dumps(self.request()), headers)[0], 200)
        self.assertEqual(self.store.state()['revision'], 0)

    def test_old_keyboard_profile_preserves_custom_bindings_and_file_bytes(self):
        path = self.root / 'legacy-keys.json'
        old = {k: v for k, v in DEFAULT_KEYS.items() if k in LEGACY_KEYS}
        old.update(pov='BracketLeft', play='BracketRight')
        atomic_json(path, dict(schema=1, revision=7, keys=old)); before = path.read_bytes()
        profile = Preferences(path).read()
        self.assertEqual({k: profile['keys'][k] for k in old}, old)
        self.assertEqual(len(set(profile['keys'].values())), len(DEFAULT_KEYS))
        self.assertEqual(profile['revision'], 7); self.assertEqual(path.read_bytes(), before)
        saved = Preferences(path).save(profile)
        self.assertEqual(saved['revision'], 8)

    def test_unchanged_material_retains_all_choices_notes_positions_history(self):
        self.reviewed()
        before = {n: (self.root / n).read_bytes() for n in ('queue.json', 'state.json', 'events.json', 'plan.json', 'probes.json')}
        data = copy.deepcopy(self.data); plan = copy.deepcopy(self.plan)
        data['events'][0]['perspectives'][0]['evidence_refs'] = ['new-packet/frame.jpg']
        data['events'][0]['provenance'] = {'frame': 'new-frame.jpg'}
        data['events'][0]['perspectives'][0]['start_sec'] = 108.0
        plan.update(title='New export title', coverage_note='More packets reviewed')
        migrated = self.migrate(data, plan)
        state = migrated.state()
        for eid, item in self.store.state()['decisions'].items():
            self.assertEqual(state['decisions'][eid]['decision'], item['decision'])
            self.assertEqual(state['decisions'][eid]['note'], item['note'])
            self.assertEqual(state['decisions'][eid]['source_positions'], item['source_positions'])
        self.assertEqual(state['history'], self.store.state()['history'])
        self.assertEqual(migrated.queue['migration']['counts']['unchanged'], 3)
        archived = json.loads((self.out / 'migration' / 'previous' / 'state.json').read_text())
        self.assertEqual(archived, self.store.state())
        for n, content in before.items():
            self.assertEqual((self.root / n).read_bytes(), content)
            self.assertEqual((self.out / 'migration' / 'previous' / n).read_bytes(), content)

    def test_changed_material_requires_review_and_preserves_note_and_prior_decision(self):
        self.reviewed()
        data = copy.deepcopy(self.data)
        data['events'][0]['marker_summary'] = 'The player loses.'
        migrated = self.migrate(data)
        item = migrated.state()['decisions']['fight']
        self.assertEqual(item['decision'], 'unreviewed'); self.assertEqual(item['note'], 'Note for fight')
        match = migrated.queue['migration']['moments']['fight']
        self.assertEqual(match['status'], 'changed'); self.assertEqual(match['previous_decision'], 'keep')
        self.assertNotIn('fight', [e['id'] for e in migrated.state()['history']])
        self.assertEqual(migrated.state()['decisions']['social']['decision'], 'skip')

    def test_changed_freeform_evidence_cannot_silently_keep_a_prior_choice(self):
        self.reviewed()
        data = copy.deepcopy(self.data)
        data['events'][0]['perspectives'][0]['evidence'] = 'Closer inspection shows a different outcome'
        migrated = self.migrate(data)
        self.assertEqual(migrated.state()['decisions']['fight']['decision'], 'unreviewed')
        self.assertEqual(migrated.queue['migration']['moments']['fight']['previous_decision'], 'keep')

    def test_anchor_uncertainty_ranges_and_media_identity_changes_are_material(self):
        self.reviewed()
        for field, value in [('source_anchor_sec', 195.2), ('source_end_sec', 201), ('uncertainty_sec', 2)]:
            with self.subTest(field=field):
                plan = copy.deepcopy(self.plan); plan['alternates'][0][field] = value
                self.out = Path(self.destination.name) / field
                migrated = self.migrate(plan=plan)
                self.assertEqual(migrated.state()['decisions']['fight']['decision'], 'unreviewed')
                self.assertEqual(migrated.state()['decisions']['later']['decision'], 'later')
        (self.root / 'b.mp4').write_bytes(b'changed media identity')
        self.out = Path(self.destination.name) / 'media'
        migrated = self.migrate()
        self.assertEqual(migrated.state()['decisions']['fight']['decision'], 'unreviewed')
        self.assertEqual(migrated.state()['decisions']['social']['decision'], 'unreviewed')
        self.assertEqual(migrated.state()['decisions']['later']['decision'], 'unreviewed')  # Its referenced earlier POV changed too.

    def test_new_and_removed_ids_never_get_a_choice_from_title_or_time(self):
        self.reviewed()
        data = copy.deepcopy(self.data)
        data['events'][0]['id'] = 'new-fight'
        data['events'][1]['related_events'][0]['event_id'] = 'new-fight'
        plan = copy.deepcopy(self.plan); plan['alternates'][0]['event_id'] = 'new-fight'
        migrated = self.migrate(data, plan)
        self.assertEqual(migrated.state()['decisions']['new-fight']['decision'], 'unreviewed')
        self.assertEqual(migrated.queue['migration']['removed_event_ids'], ['fight'])
        self.assertEqual(migrated.queue['migration']['moments']['new-fight']['status'], 'new')
        self.assertEqual(migrated.state()['decisions']['new-fight']['note'], '')

    def test_explicit_id_mapping_is_one_to_one_and_still_compares_content(self):
        self.reviewed()
        data = copy.deepcopy(self.data); data['events'][0]['id'] = 'renamed'
        data['events'][1]['related_events'][0]['event_id'] = 'renamed'
        plan = copy.deepcopy(self.plan); plan['alternates'][0]['event_id'] = 'renamed'
        mapping = self.root / 'id-map.json'
        atomic_json(mapping, dict(schema='vod-review-event-map/v1', matches=[dict(event_id='renamed', previous_id='fight')]))
        migrated = self.migrate(data, plan, event_map=mapping)
        self.assertEqual(migrated.state()['decisions']['renamed']['decision'], 'keep')
        self.assertEqual(migrated.state()['decisions']['later']['decision'], 'later')
        self.assertIn('renamed', [e['id'] for e in migrated.state()['history']])
        self.out = Path(self.destination.name) / 'changed-rename'
        data['events'][0]['review_note'] = 'Check a different outcome'
        changed = self.migrate(data, plan, event_map=mapping)
        self.assertEqual(changed.state()['decisions']['renamed']['decision'], 'unreviewed')

    def test_ambiguous_repeated_material_is_not_automatically_matched(self):
        old_data = copy.deepcopy(self.data)
        old_data['events'].append({**copy.deepcopy(old_data['events'][2]), 'id': 'social-repeat'})
        old_state = copy.deepcopy(self.state)
        old_state['decisions']['social']['decision'] = 'keep'
        old_state['decisions']['social-repeat'] = dict(decision='skip', note='', view=0, positions={})
        previous = dict(folder=str(self.root), event_map={}, cards={}, snapshots={
            'events.json': old_data, 'plan.json': self.plan, 'probes.json': self.probes,
            'state.json': old_state, 'queue.json': self.queue})
        new_data = copy.deepcopy(self.data); new_data['events'][2]['id'] = 'different-social-id'
        report = prepare_migration(previous, new_data, self.plan, self.probes, self.queue['identities'])
        item = report['moments']['different-social-id']
        self.assertEqual(item['status'], 'ambiguous')
        self.assertEqual(set(item['possible_previous_ids']), {'social', 'social-repeat'})
        self.assertIsNone(item['previous_id'])

    def test_update_preserves_requested_context_and_source_position(self):
        self.complete(self.request())
        self.store.mutate(dict(revision=0, event_id='fight', source_position_sec=94, note='Setup', decision='later'))
        migrated = self.migrate()
        self.assertEqual(migrated.cards['fight']['views'][0]['preview_start_sec'], 90)
        self.assertEqual(migrated.state()['decisions']['fight']['source_positions']['0'], 94)
        self.assertEqual(migrated.state()['decisions']['fight']['decision'], 'later')

    def test_update_refuses_active_previous_server_or_overlapping_folders(self):
        events, plan, source_probe = self.build_inputs()
        before = (self.root / 'state.json').read_bytes()
        with build_lock(self.root, '.server.lock'):
            with self.assertRaisesRegex(Conflict, 'Stop'):
                update_queue(self.root, events, plan, self.out)
        with self.assertRaisesRegex(ValueError, 'separate'):
            update_queue(self.root, events, plan, self.root / 'revised')
        self.assertEqual((self.root / 'state.json').read_bytes(), before)
        self.assertFalse(self.out.exists())

    def test_update_uses_preserved_snapshots_when_external_inputs_changed(self):
        events, plan, source_probe = self.build_inputs()
        self.queue['inputs'] = [dict(path=str(p), sha256=file_hash(p)) for p in (events, plan)]
        atomic_json(self.root / 'queue.json', self.queue)
        self.state['queue_hash'] = digest(self.queue)
        atomic_json(self.root / 'state.json', self.state)
        self.store = Store(self.root)
        self.store.mutate(dict(revision=0, event_id='fight', decision='keep', note='Preserved snapshot'))
        revised = copy.deepcopy(self.data); revised['events'][1]['review_note'] = 'Check updated reaction'
        atomic_json(events, revised)
        with self.assertRaisesRegex(ValueError, 'inputs changed'): Store(self.root)
        with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=self.fake_preview):
            update_queue(self.root, events, plan, self.out)
        migrated = Store(self.out)
        self.assertEqual(migrated.state()['decisions']['fight']['decision'], 'keep')
        self.assertEqual(migrated.queue['migration']['moments']['later']['status'], 'changed')
        self.assertEqual(json.loads((self.out / 'migration' / 'previous' / 'events.json').read_text()), self.data)

    def test_update_rejects_tampered_queue_snapshots_without_touching_choices(self):
        self.reviewed(); events, plan, _ = self.build_inputs()
        before = (self.root / 'state.json').read_bytes()
        (self.root / 'events.json').write_bytes((self.root / 'events.json').read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'snapshot changed'):
            update_queue(self.root, events, plan, self.out)
        self.assertEqual((self.root / 'state.json').read_bytes(), before)
        self.assertFalse(self.out.exists())

    def test_second_update_keeps_ancestor_history_without_restoring_changed_choice(self):
        self.reviewed()
        original = (self.root / 'state.json').read_bytes()
        original_hash = self.store.queue_hash
        data = copy.deepcopy(self.data); data['events'][0]['marker_summary'] = 'Different outcome'
        first = self.migrate(data)
        self.assertEqual(first.state()['decisions']['fight']['decision'], 'unreviewed')
        events, plan, source_probe = self.build_inputs()
        atomic_json(events, data)
        next_out = Path(self.destination.name) / 'third'
        with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=self.fake_preview):
            update_queue(self.out, events, plan, next_out)
        second = Store(next_out)
        self.assertEqual(second.state()['decisions']['fight']['decision'], 'unreviewed')
        ancestor = next_out / 'migration' / 'ancestors' / original_hash / 'state.json'
        self.assertEqual(ancestor.read_bytes(), original)
        self.assertEqual(json.loads(ancestor.read_text())['decisions']['fight']['decision'], 'keep')
        self.assertIn(original_hash, second.queue['migration']['preserved_ancestor_queue_hashes'])

    def test_archive_keeps_original_serialization_and_snapshot_hashes(self):
        raw = json.dumps(self.data, indent=1).encode('utf-8') + b'\r\n'
        (self.root / 'events.json').write_bytes(raw)
        self.queue['snapshots']['events.json'] = file_hash(self.root / 'events.json')
        atomic_json(self.root / 'queue.json', self.queue)
        self.state['queue_hash'] = digest(self.queue)
        atomic_json(self.root / 'state.json', self.state)
        self.store = Store(self.root)
        self.migrate()
        archive = self.out / 'migration' / 'previous'
        self.assertEqual((archive / 'events.json').read_bytes(), raw)
        archived_queue = json.loads((archive / 'queue.json').read_text())
        for name, expected in archived_queue['snapshots'].items():
            self.assertEqual(file_hash(archive / name), expected)

    def test_second_server_refuses_before_startup_cache_repair(self):
        with build_lock(self.root, '.server.lock'), patch('review_queue.Store') as constructor:
            with patch('sys.argv', ['review_queue.py', 'serve', '--queue', str(self.root)]):
                with self.assertRaisesRegex(SystemExit, 'already open'):
                    main()
            constructor.assert_not_called()

    def test_explicit_mapping_cannot_assign_one_prior_choice_to_two_moments(self):
        self.reviewed(); data = copy.deepcopy(self.data)
        data['events'].append({**copy.deepcopy(data['events'][2]), 'id': 'renamed-social'})
        mapping = self.root / 'bad-id-map.json'
        atomic_json(mapping, dict(schema='vod-review-event-map/v1', matches=[dict(event_id='renamed-social', previous_id='social')]))
        events, plan, _ = self.build_inputs(); atomic_json(events, data)
        with self.assertRaisesRegex(ValueError, 'multiple'):
            update_queue(self.root, events, plan, self.out, event_map=mapping)
        self.assertFalse(self.out.exists())

    def test_context_rejects_invented_source_ranges_and_unknown_views(self):
        before = (self.root / 'state.json').read_bytes()
        request = self.request()
        for extra in (dict(preview_start_sec=-1), dict(preview_start_sec=float('nan')),
                      dict(preview_end_sec=601), dict(preview_start_sec=50), dict(view=True),
                      dict(event_id='unknown'), dict(direction='both')):
            with self.assertRaises(ValueError): self.store.context.request({**request, **extra})
        self.assertEqual((self.root / 'state.json').read_bytes(), before)
        self.assertFalse((self.root / 'context.json').exists())

    def test_failed_update_resumes_but_rejects_changed_donor_decisions(self):
        self.reviewed(); events, plan, source_probe = self.build_inputs()
        with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=RuntimeError('Encode failed')):
            with self.assertRaises(RuntimeError): update_queue(self.root, events, plan, self.out, jobs=1)
        self.assertFalse((self.out / 'queue.json').exists())
        with patch('review_queue.render_preview', side_effect=self.fake_preview):
            update_queue(self.root, events, plan, self.out, resume=True)
        self.assertEqual(Store(self.out).state()['decisions']['fight']['decision'], 'keep')
        self.out = Path(self.destination.name) / 'failed-again'
        with patch('review_queue.probe', side_effect=source_probe), patch('review_queue.render_preview', side_effect=RuntimeError('Encode failed')):
            with self.assertRaises(RuntimeError): update_queue(self.root, events, plan, self.out)
        self.store.mutate(dict(revision=3, event_id='fight', decision='skip'))
        with patch('review_queue.render_preview') as renderer:
            with self.assertRaisesRegex(ValueError, 'changed'):
                update_queue(self.root, events, plan, self.out, resume=True)
            renderer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
