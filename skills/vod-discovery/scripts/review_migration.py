"""Conservative review-decision transfer between immutable discovery queues."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json


# These describe how evidence was gathered or where to find it. Authored claims,
# review checks, uncertainty, ranges and placements remain part of the material.
PROVENANCE = {'evidence_refs', 'frame_refs', 'transcript_refs', 'packet_refs',
              'provenance', 'reviewed_packets', 'inspected_sheets', 'prepared_at', 'generated_at'}


def canonical(value, ignore=()):
    if isinstance(value, dict):
        return {k: canonical(v, ignore) for k, v in sorted(value.items()) if k not in ignore}
    if isinstance(value, list):
        return [canonical(v, ignore) for v in value]
    if type(value) is float and value.is_integer():
        return int(value)
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def source_material(source, identities, probes):
    value = dict(source=canonical(source, PROVENANCE), identity=identities[source['id']])
    if probes is not None:
        keys = ('codec_type', 'codec_name', 'index', 'width', 'height', 'r_frame_rate',
                'avg_frame_rate', 'time_base', 'start_time', 'channels', 'channel_layout', 'sample_rate')
        value['streams'] = [{k: stream[k] for k in keys if k in stream}
                            for stream in probes[source['id']]['streams']]
        value['timecode'] = [stream.get('tags', {}).get('timecode')
                             for stream in probes[source['id']]['streams']]
    return canonical(value)


def material(event, data, plan, identities, probes=None, aliases=None):
    aliases = aliases or {}
    sources = {s['id']: s for s in data['sources']}
    events = {e['id']: e for e in data['events']}
    copy = {k: v for k, v in event.items() if k not in PROVENANCE | {'id', 'perspectives', 'related_events'}}
    views = sorted(event['perspectives'], key=lambda v: v['source_id'])
    related = []
    for relation in event.get('related_events', []):
        target = events[relation['event_id']]
        view = next(v for v in target['perspectives'] if v['source_id'] == relation['source_id'])
        related.append(dict(relation={**relation, 'event_id': aliases.get(target['id'], target['id'])},
                            view=view, title=target['marker_title'], summary=target['marker_summary'],
                            check=target.get('review_note', ''), status=target['status'],
                            source=source_material(sources[view['source_id']], identities, probes)))
    placements = [{k: v for k, v in alt.items() if k != 'event_id'}
                  for alt in plan.get('alternates', []) if alt.get('event_id') == event['id']]
    main = plan['main_sources']
    origins, cursor = {}, 0.0
    fps = None
    if probes is not None:
        from premiere_xml import frame_rate
        fps = frame_rate(next(s for s in probes[main[0]]['streams'] if s['codec_type'] == 'video'))[2]
    for sid in main:
        origins[sid] = cursor
        duration = sources[sid]['duration_sec']
        cursor += float(round(Fraction(str(duration)) * fps) / fps) if fps else duration
    parts = dict(
        copy=canonical(copy, PROVENANCE),
        perspectives=canonical(views, PROVENANCE),
        sources={v['source_id']: source_material(sources[v['source_id']], identities, probes) for v in views},
        placements=sorted((canonical(a, PROVENANCE) for a in placements), key=lambda a: json.dumps(a, sort_keys=True)),
        main_role={v['source_id']: origins.get(v['source_id']) for v in views},
        related=sorted((canonical(r, PROVENANCE) for r in related), key=lambda r: json.dumps(r, sort_keys=True)),
        plan_options=canonical({k: v for k, v in plan.items()
                                if k not in {'title', 'coverage_note', 'main_sources', 'alternates'}}, PROVENANCE))
    return canonical(parts)


def prepare_migration(previous, data, plan, probes, identities):
    old_data, old_plan = previous['snapshots']['events.json'], previous['snapshots']['plan.json']
    old_probes = previous['snapshots']['probes.json'] if probes is not None else None
    old_ids = previous['snapshots']['queue.json']['identities']
    old_events = {e['id']: e for e in old_data['events']}
    new_events = {e['id']: e for e in data['events']}
    explicit = previous.get('event_map', {})
    if any(new not in new_events or old not in old_events for new, old in explicit.items()):
        raise ValueError('Every explicit event match must reference a previous and a revised event')
    matches = {new: explicit.get(new, new if new in old_events else None) for new in new_events}
    matched = [old for old in matches.values() if old is not None]
    if len(matched) != len(set(matched)):
        raise ValueError('An old moment cannot be matched to multiple revised moments')
    old_material = {eid: material(e, old_data, old_plan, old_ids, old_probes) for eid, e in old_events.items()}
    reasons = dict(copy='Description, rationale or review checks changed', perspectives='POV ranges, roles, evidence or alignment changed',
                   sources='Source media, identity or playback layout changed', placements='Alternate excerpts or anchors changed',
                   main_role='Main chronology or POV role changed', related='Related moment references changed',
                   plan_options='Timeline options changed')
    moments = {}
    for eid, event in new_events.items():
        current = material(event, data, plan, identities, probes, {n: o for n, o in matches.items() if o})
        old = matches[eid]
        if old is None:
            candidates = [oid for oid, value in old_material.items() if value == current and oid not in matched]
            moments[eid] = dict(status='ambiguous' if len(candidates) > 1 else 'new', previous_id=None,
                                possible_previous_ids=candidates, reasons=['No stable event identity match'])
            continue
        changes = [reasons[key] for key in reasons if old_material[old][key] != current[key]]
        moments[eid] = dict(status='changed' if changes else 'unchanged', previous_id=old,
                            previous_decision=previous['snapshots']['state.json']['decisions'][old]['decision'],
                            reasons=changes,
                            metadata_changed=not changes and canonical(old_events[old]) != canonical({**event, 'id': old}))
    counts = {key: sum(item['status'] == key for item in moments.values())
              for key in ('unchanged', 'changed', 'new', 'ambiguous')}
    return dict(schema='vod-review-migration/v1', previous_queue=previous['folder'],
                previous_queue_hash=previous['snapshots']['state.json']['queue_hash'],
                previous_state_hash=digest(previous['snapshots']['state.json']),
                previous_revision=previous['snapshots']['state.json']['revision'],
                preserved_ancestor_queue_hashes=sorted({name.split('/')[1] for name in previous.get('ancestor_snapshots', {})}),
                moments=moments, removed_event_ids=sorted(set(old_events) - set(matched)), counts=counts)


def migrated_state(manifest, previous):
    old_state = previous['snapshots']['state.json']
    report = manifest['migration']
    state = dict(schema=manifest['schema'], queue_hash=digest(manifest), revision=0,
                 current_id=manifest['cards'][0]['id'], decisions={}, history=[],
                 previous_queue_hash=old_state['queue_hash'])
    remapped = {}
    for card in manifest['cards']:
        match = report['moments'][card['id']]
        old = match['previous_id']
        item = dict(decision='unreviewed', note='', view=0, positions={}, source_positions={})
        if old is not None:
            prior = old_state['decisions'][old]
            old_card = previous['cards'][old]
            item['note'] = prior['note']
            if match['status'] == 'unchanged':
                item['decision'] = prior['decision']
                remapped[old] = card['id']
            for index, view in enumerate(card['views']):
                old_index = next((i for i, v in enumerate(old_card['views']) if v['source_id'] == view['source_id']), None)
                if old_index is None:
                    continue
                if prior['view'] == old_index:
                    item['view'] = index
                if manifest['identities'][view['source_id']] != previous['snapshots']['queue.json']['identities'][view['source_id']]:
                    continue
                key = str(old_index)
                source_time = prior.get('source_positions', {}).get(key)
                if source_time is None and key in prior['positions']:
                    source_time = old_card['views'][old_index].get('base_preview_start_sec',
                        old_card['views'][old_index]['preview_start_sec']) + prior['positions'][key]
                if source_time is not None and view['preview_start_sec'] <= source_time <= view['preview_end_sec']:
                    item['source_positions'][str(index)] = source_time
                    item['positions'][str(index)] = source_time - view['preview_start_sec']
            if old_state['current_id'] == old:
                state['current_id'] = card['id']
        state['decisions'][card['id']] = item
    # Carry Undo only for unchanged material. Full prior history remains archived,
    # including removed/changed decisions that must never reactivate accidentally.
    for entry in old_state['history']:
        if entry['id'] in remapped:
            state['history'].append({**deepcopy(entry), 'id': remapped[entry['id']]})
    return state
