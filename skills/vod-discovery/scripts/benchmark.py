"""Score bounded discovery runs against authored, reviewed references; no inference."""
import argparse
from collections import defaultdict
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import uuid


REFERENCE = 'vod-discovery-benchmark/v1'
ADJUDICATION = 'vod-discovery-adjudication/v1'
RUN = 'vod-discovery-benchmark-run/v1'
REPORT = 'vod-discovery-benchmark-report/v1'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False, separators=(',', ':')).encode('utf-8')).hexdigest()


def write_new(path, value):
    path = Path(path)
    if path.exists():
        raise ValueError(f'Output already exists: {path}; use a new run filename')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
        # Exclusive destination creation protects an existing authored judgment.
        with path.open('xb') as output:
            output.write(temporary.read_bytes())
    finally:
        temporary.unlink(missing_ok=True)


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'Missing {label}')
    return value


def numeric(value, label, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise ValueError(f'Invalid {label}')
    return value


def media_path(value):
    value = nonempty(value, 'source path').replace('\\', '/')
    # Windows media identity is case-insensitive even when scored on another OS.
    if re.match(r'^[A-Za-z]:/', value) or value.startswith('//'):
        return value.casefold()
    return value


def source_map(items):
    if not isinstance(items, list) or not items:
        raise ValueError('sources must be a nonempty list')
    result, paths = {}, set()
    for item in items:
        sid = nonempty(item.get('id'), 'source id')
        path = media_path(item.get('path'))
        numeric(item.get('duration_sec'), 'source duration', .001)
        if sid in result or path in paths:
            raise ValueError('Duplicate source id or media path')
        result[sid] = item
        paths.add(path)
    return result


def interval(view, sources):
    sid = view.get('source_id')
    if sid not in sources:
        raise ValueError(f'Unknown source: {sid}')
    start = numeric(view.get('start_sec'), 'start_sec')
    end = numeric(view.get('end_sec'), 'end_sec')
    if start >= end or end > sources[sid]['duration_sec']:
        raise ValueError('Interval lies outside source bounds or is empty')
    return sid, start, end


def events_data(data):
    sources = source_map(data.get('sources'))
    events = data.get('events')
    if not isinstance(events, list):
        raise ValueError('events must be a list')
    ids = set()
    for event in events:
        eid = nonempty(event.get('id'), 'event id')
        if eid in ids:
            raise ValueError('Duplicate event id')
        ids.add(eid)
        views = event.get('perspectives')
        if not isinstance(views, list) or not views:
            raise ValueError(f'Event {eid} needs perspectives')
        seen = set()
        for view in views:
            sid, _, _ = interval(view, sources)
            if sid in seen:
                raise ValueError(f'Event {eid} has duplicate source perspective')
            seen.add(sid)
    return sources, events


def contained(sid, start, end, coverage):
    ranges = sorted((c['start_sec'], c['end_sec']) for c in coverage if c['source_id'] == sid)
    cursor = start
    for low, high in ranges:
        if low > cursor:
            return False
        if high > cursor:
            cursor = high
        if cursor >= end:
            return True
    return False


def reference_data(data):
    if data.get('schema') != REFERENCE:
        raise ValueError('Unknown reference schema')
    nonempty(data.get('name'), 'reference name')
    nonempty(data.get('reviewed_by'), 'reviewed_by: finish authoring the reference before scoring')
    nonempty(data.get('reviewed_at'), 'reviewed_at')
    basis = data.get('review_basis')
    if basis not in ('supplied-evidence', 'continuous-video'):
        raise ValueError('review_basis must be supplied-evidence or continuous-video')
    if not isinstance(data.get('exhaustive'), bool) or (basis == 'supplied-evidence' and data['exhaustive']):
        raise ValueError('Sampled supplied evidence cannot establish exhaustive reference coverage')
    sources = source_map(data.get('sources'))
    coverage = data.get('coverage')
    if not isinstance(coverage, list) or not coverage:
        raise ValueError('Reference needs explicit reviewed coverage')
    for span in coverage:
        interval(span, sources)
        if span.get('reviewed') is not True:
            raise ValueError('Reference coverage must be reviewed before scoring')
        nonempty(span.get('evidence'), 'coverage review evidence')
    moments = data.get('moments')
    if not isinstance(moments, list):
        raise ValueError('moments must be a list')
    # Reuse interval/ID validation, without requiring marker display copy.
    events_data({'sources': data['sources'], 'events': moments})
    for moment in moments:
        if moment.get('reviewed') is not True:
            raise ValueError(f'Reference moment {moment["id"]} has not been reviewed')
        tags = moment.get('tags', [])
        if not isinstance(tags, list) or any(not isinstance(t, str) or not t.strip() for t in tags):
            raise ValueError('Moment tags must be a list of nonempty strings')
        for view in moment['perspectives']:
            sid, start, end = interval(view, sources)
            nonempty(view.get('evidence'), 'reference perspective evidence')
            if not contained(sid, start, end, coverage):
                raise ValueError(f'Moment {moment["id"]} is outside reviewed coverage')
    return sources, {m['id']: m for m in moments}


def scaffold_reference(events, name):
    sources, candidates = events_data(events)
    return {'schema': REFERENCE, 'name': nonempty(name, 'reference name'),
            'reviewed_by': '', 'reviewed_at': '', 'review_basis': 'supplied-evidence', 'exhaustive': False,
            'sources': [{k: s[k] for k in ('id', 'path', 'duration_sec')} for s in sources.values()],
            'coverage': [{'source_id': sid, 'start_sec': 0, 'end_sec': s['duration_sec'],
                          'reviewed': False, 'evidence': ''} for sid, s in sources.items()],
            'moments': [{'id': e['id'], 'title': e.get('title', ''), 'reviewed': False, 'tags': [],
                         'perspectives': [{k: v[k] for k in ('source_id', 'start_sec', 'end_sec', 'evidence')
                                           if k in v} for v in e['perspectives']]} for e in candidates]}


def scope(reference, events):
    refs, _ = reference_data(reference)
    sources, candidates = events_data(events)
    for sid, original in refs.items():
        current = sources.get(sid)
        if current is None or media_path(current['path']) != media_path(original['path']) or current['duration_sec'] != original['duration_sec']:
            raise ValueError(f'Source identity changed for {sid}; benchmark the same media and clocks')
    observations, links, excluded = {}, {}, []
    for candidate in candidates:
        inside = []
        for view in candidate['perspectives']:
            sid, start, end = interval(view, sources)
            key = (candidate['id'], sid)
            if sid in refs and contained(sid, start, end, reference['coverage']):
                observations[key] = view
                inside.append(sid)
            else:
                partial = sid in refs and any(c['source_id'] == sid and max(start, c['start_sec']) < min(end, c['end_sec'])
                                             for c in reference['coverage'])
                excluded.append({'candidate_event_id': candidate['id'], 'source_id': sid,
                                 'partially_reviewed': partial,
                                 'reason': ('partially overlaps reviewed coverage; narrow the candidate or review the whole range'
                                            if partial else 'outside the reviewed reference ranges')})
        for pair in itertools.combinations(sorted(inside), 2):
            links[(candidate['id'], *pair)] = pair
    return observations, links, excluded


def scaffold_adjudication(reference, events):
    observations, links, excluded = scope(reference, events)
    return {'schema': ADJUDICATION, 'reference_sha256': digest(reference), 'events_sha256': digest(events),
            'observations': [{'candidate_event_id': eid, 'source_id': sid, 'verdict': 'pending',
                              'moment_id': None, 'note': ''} for eid, sid in observations],
            'pov_links': [{'candidate_event_id': eid, 'source_ids': [a, b], 'verdict': 'pending',
                           'note': ''} for eid, a, b in links], 'excluded_observations': excluded}


def score(reference, events, judgments, run=None):
    _, moments = reference_data(reference)
    observations, links, excluded = scope(reference, events)
    if judgments.get('schema') != ADJUDICATION or judgments.get('reference_sha256') != digest(reference) or judgments.get('events_sha256') != digest(events):
        raise ValueError('Judgments are stale or use the wrong reference/events')
    matched = defaultdict(list)
    pending, unmatched, seen, matched_keys = [], [], set(), {}
    if not isinstance(judgments.get('observations'), list) or not isinstance(judgments.get('pov_links'), list):
        raise ValueError('Judgments need observations and pov_links lists')
    for item in judgments['observations']:
        key = (item.get('candidate_event_id'), item.get('source_id'))
        if key not in observations or key in seen:
            raise ValueError('Unknown or duplicate observation judgment')
        seen.add(key)
        verdict = item.get('verdict')
        if verdict == 'pending':
            pending.append(item)
        elif verdict == 'unmatched':
            nonempty(item.get('note'), 'unmatched observation note')
            unmatched.append(item)
        elif verdict == 'match':
            nonempty(item.get('note'), 'matched observation note')
            moment = moments.get(item.get('moment_id'))
            target = next((v for v in moment['perspectives'] if v['source_id'] == key[1]), None) if moment else None
            view = observations[key]
            if target is None or max(view['start_sec'], target['start_sec']) >= min(view['end_sec'], target['end_sec']):
                raise ValueError('Match needs a known reference perspective and overlapping source-local range')
            matched[(moment['id'], key[1])].append(key[0])
            matched_keys[key] = moment['id']
        else:
            raise ValueError('Observation verdict must be pending, match or unmatched')
        if verdict != 'match' and item.get('moment_id') is not None:
            raise ValueError('Only a match may name a moment_id')
    if seen != observations.keys():
        raise ValueError('Missing observation judgments; generate a complete pending scaffold')
    link_counts = {'correct': 0, 'incorrect': 0, 'pending': 0}
    incorrect, pending_links, seen = [], [], set()
    for item in judgments['pov_links']:
        pair = item.get('source_ids')
        if not isinstance(pair, list) or len(pair) != 2 or any(not isinstance(s, str) for s in pair):
            raise ValueError('POV link needs two source_ids')
        key = (item.get('candidate_event_id'), *sorted(pair))
        if key not in links or key in seen:
            raise ValueError('Unknown or duplicate POV link judgment')
        seen.add(key)
        verdict = item.get('verdict')
        if verdict not in link_counts:
            raise ValueError('POV link verdict must be pending, correct or incorrect')
        if verdict != 'pending':
            nonempty(item.get('note'), 'POV judgment evidence note')
        if verdict == 'correct':
            left, right = (matched_keys.get((key[0], sid)) for sid in key[1:])
            if left is not None and right is not None and left != right:
                raise ValueError('A correct same-event POV link contradicts its different matched reference moments')
        link_counts[verdict] += 1
        if verdict == 'incorrect':
            incorrect.append(item)
        if verdict == 'pending':
            pending_links.append(item)
    if seen != links.keys():
        raise ValueError('Missing POV link judgments; generate a complete pending scaffold')
    missing_views = [{'moment_id': m['id'], 'source_id': v['source_id']}
                     for m in moments.values() for v in m['perspectives'] if (m['id'], v['source_id']) not in matched]
    found = {mid for mid, _ in matched}
    missing = [mid for mid in moments if mid not in found]
    partially_reviewed = [item for item in excluded if item['partially_reviewed']]
    complete = not pending and not partially_reviewed
    duplicates = [{'moment_id': mid, 'source_id': sid, 'candidate_event_ids': sorted(ids), 'extra_observations': len(ids) - 1}
                  for (mid, sid), ids in matched.items() if len(ids) > 1]
    tag_groups = defaultdict(set)
    for moment in moments.values():
        for tag in moment.get('tags', []):
            tag_groups[tag].add(moment['id'])
    by_tag = {tag: {'known_moments': len(ids), 'matched': len(ids & found),
                    'missed': len(ids - found) if complete else None}
              for tag, ids in sorted(tag_groups.items())}
    performance = None
    if run is not None:
        if run.get('schema') != RUN or run.get('events_sha256') != digest(events):
            raise ValueError('Run measurements are stale or for different events')
        numeric(run.get('elapsed_wall_sec'), 'elapsed_wall_sec')
        size = run.get('output_storage_bytes')
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ValueError('Invalid output_storage_bytes')
        performance = run
    return {'schema': REPORT, 'reference_sha256': digest(reference), 'events_sha256': digest(events),
            'adjudication_sha256': digest(judgments),
            'reference': {k: reference[k] for k in ('name', 'review_basis', 'exhaustive', 'reviewed_by', 'reviewed_at')},
            'quality': {'observation_judgments_complete': not pending, 'pov_judgments_complete': not pending_links,
                        'miss_scoring_complete': complete, 'partial_coverage_observations': len(partially_reviewed),
                        'known_moments': len(moments), 'known_moments_matched': len(found),
                        'known_moments_missed': len(missing) if complete else None,
                        'known_moment_recall': len(found) / len(moments) if moments and complete else None,
                        'known_perspectives_missed': len(missing_views) if complete else None,
                        'incorrect_pov_associations': link_counts['incorrect'],
                        'correct_pov_associations': link_counts['correct'], 'pending_pov_associations': link_counts['pending'],
                        'duplicate_observations': sum(d['extra_observations'] for d in duplicates),
                        'unmatched_candidate_observations': len(unmatched), 'pending_observations': len(pending)},
            'quality_by_tag': by_tag,
            'unmatched_reference_moments': missing if complete else None,
            'unmatched_reference_perspectives': missing_views if complete else None,
            'duplicates': duplicates, 'incorrect_pov_links': incorrect,
            'pending_observations': pending, 'pending_pov_links': pending_links,
            'excluded_observations': excluded, 'performance': performance,
            'limits': ['Matches and POV judgments are manually authored; interval overlap is validation, not event recognition.',
                       'Recall is relative to this reviewed reference and its coverage, not proof of full-session discovery.',
                       'Duplicate counts cover adjudicated matches only; pending observations can add duplicates.',
                       'related_events are not simultaneous POV associations and are not scored as links.']}


def record_run(events, label, elapsed, roots):
    sources, _ = events_data(events)
    numeric(elapsed, 'elapsed wall seconds')
    original_paths = {media_path(str(Path(s['path']).resolve())) for s in sources.values()}
    files, excluded_sources, skipped_links = set(), set(), set()
    def link(path):
        return path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction())
    supplied_roots = [Path(p).absolute() for p in roots]
    if any(link(p) for p in supplied_roots):
        raise ValueError('Artifact roots must not be symlinks or junctions')
    artifact_roots = [p.resolve(strict=True) for p in supplied_roots]
    if not artifact_roots or any(not p.is_dir() for p in artifact_roots):
        raise ValueError('Artifacts must be existing directories')
    for root in artifact_roots:
        for folder, dirs, names in os.walk(root, followlinks=False):
            base = Path(folder)
            for name in dirs[:]:
                child = base / name
                if link(child):
                    skipped_links.add(str(child))
                    dirs.remove(name)
            for name in names:
                child = base / name
                if link(child):
                    skipped_links.add(str(child))
                    continue
                canonical = child.resolve(strict=True)
                if media_path(str(canonical)) in original_paths:
                    excluded_sources.add(str(canonical))
                else:
                    files.add(canonical)
    return {'schema': RUN, 'label': nonempty(label, 'run label'), 'events_sha256': digest(events),
            'elapsed_wall_sec': elapsed, 'timing_basis': 'externally-measured-wall-time',
            'artifact_roots': [str(p) for p in artifact_roots],
            'output_storage_bytes': sum(p.stat().st_size for p in files), 'output_files': len(files),
            'excluded_source_files': sorted(excluded_sources), 'excluded_links': sorted(skipped_links)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    reference = sub.add_parser('reference', help='Create a pending reference scaffold from events')
    reference.add_argument('--events', required=True)
    reference.add_argument('--name', required=True)
    reference.add_argument('--out', required=True)
    judge = sub.add_parser('adjudication', help='Create pending manual judgments for a run')
    judge.add_argument('--reference', required=True)
    judge.add_argument('--events', required=True)
    judge.add_argument('--out', required=True)
    scoring = sub.add_parser('score', help='Score authored judgments; no automatic semantic matching')
    scoring.add_argument('--reference', required=True)
    scoring.add_argument('--events', required=True)
    scoring.add_argument('--adjudication', required=True)
    scoring.add_argument('--run')
    scoring.add_argument('--out', required=True)
    record = sub.add_parser('record', help='Record measured wall time and output-only storage')
    record.add_argument('--events', required=True)
    record.add_argument('--label', required=True)
    record.add_argument('--wall-seconds', type=float, required=True)
    record.add_argument('--artifacts', nargs='+', required=True)
    record.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        events = read(args.events)
        if args.command == 'reference':
            result = scaffold_reference(events, args.name)
        elif args.command == 'adjudication':
            result = scaffold_adjudication(read(args.reference), events)
        elif args.command == 'score':
            result = score(read(args.reference), events, read(args.adjudication), read(args.run) if args.run else None)
        else:
            result = record_run(events, args.label, args.wall_seconds, args.artifacts)
        write_new(args.out, result)
        print(json.dumps({'output': str(Path(args.out).resolve()), 'schema': result['schema']}))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
