"""Place accepted alternate POVs under every main block they cover, from a reviewed alignment span."""
import argparse
from pathlib import Path

from review_timeline import CLOSE_GAPS_SEC, LABELED_STATUSES, merged_blocks
from vod import number, read, run_cli, write

MINIMUM_EXCERPT_SEC = 3.0


def supported_ranges(span, covered):
    """Main-time stretches where the offset has evidence: the span minus its quiet gaps, plus confirmed ranges."""
    ranges, cursor = [], span['first_support_main_sec']
    for gap in span['quiet_gaps']:
        ranges.append((cursor, gap['from_main_sec']))
        cursor = gap['to_main_sec']
    ranges.append((cursor, span['last_support_main_sec']))
    return ranges + covered


def inside(interval, ranges):
    return any(a <= interval[0] and interval[1] <= b for a, b in ranges)


def block_events(data, main_id, block, statuses):
    """Events whose main view overlaps the block, in main-time order."""
    found = []
    for event in data['events']:
        for view in event['perspectives']:
            if view['source_id'] == main_id and event['status'] in statuses:
                start, end = view.get('cut_start_sec', view['start_sec']), view.get('cut_end_sec', view['end_sec'])
                if start < block[1] and end > block[0]:
                    found.append((start, event))
    return [event for _, event in sorted(found, key=lambda pair: pair[0])]


def place(data, alignment, accepted, covered, statuses, gap, note):
    main_id = alignment['main_source_id']
    sources = {s['id']: s for s in data['sources']}
    if main_id not in sources:
        raise ValueError('The alignment main source is not in the events file; use the prepared source IDs')
    blocks = merged_blocks(data, [main_id], statuses, gap)[main_id]
    placed, unchecked, skipped = [], [], []
    by_source = {a['source_id']: a for a in alignment['alternates']}
    for alt_id, index in accepted:
        if alt_id not in sources or alt_id not in by_source:
            raise ValueError(f'Alternate {alt_id} is not in the events file and the alignment')
        span = by_source[alt_id]['spans'][index]
        offset, duration = span['alt_equals_main_plus_sec'], sources[alt_id]['duration_sec']
        uncertainty = max(span['tolerance_sec'], span['offset_spread_sec'] / 2)
        ranges = supported_ranges(span, covered.get(alt_id, []))
        for block in blocks:
            start, end = max(block[0], -offset), min(block[1], duration - offset)
            if end - start < MINIMUM_EXCERPT_SEC:
                skipped.append({'alt_source_id': alt_id, 'main_from_sec': block[0], 'main_to_sec': block[1],
                                'reason': 'alternate recording does not cover this block'})
                continue
            if not inside((start, end), ranges):
                unchecked.append({'alt_source_id': alt_id, 'main_from_sec': round(start, 2), 'main_to_sec': round(end, 2),
                                  'reason': 'outside the span\'s supported stretches; check a pair sheet here'})
                continue
            events = block_events(data, main_id, block, statuses)
            middle = (start + end) / 2
            kinds = span['supporting_by_kind']
            placed.append({
                'source_id': alt_id, 'main_source_id': main_id, 'event_id': events[0]['id'] if events else None,
                'name': f"{sources[alt_id].get('label', alt_id)}: {events[0]['marker_title']}" if events
                        else sources[alt_id].get('label', alt_id),
                'source_start_sec': round(start + offset, 3), 'source_end_sec': round(end + offset, 3),
                'source_anchor_sec': round(middle + offset, 3), 'main_anchor_sec': round(middle, 3),
                'uncertainty_sec': uncertainty,
                'evidence': (f"Offset {offset:+.1f}s from {span['supporting_utterances']} matching utterances "
                             f"(speech {kinds['speech']}, on-screen text {kinds['screen']}) between main "
                             f"{span['first_support_main_sec']:.0f}-{span['last_support_main_sec']:.0f}s; "
                             f"accepted by the reviewer. {note}").strip()})
    return placed, unchecked, skipped


def parse_accept(value):
    alt_id, sep, index = value.rpartition(':')
    if not sep or not alt_id or not index.isdigit():
        raise ValueError(f'--accept needs ALT_SOURCE_ID:SPAN_INDEX, got {value!r}')
    return alt_id, int(index)


def parse_covered(values):
    covered = {}
    for value in values or []:
        alt_id, sep, span = value.rpartition('=')
        start, dash, end = span.partition('-')
        if not sep or not dash:
            raise ValueError(f'--covered needs ALT_SOURCE_ID=FROM-TO in main seconds, got {value!r}')
        covered.setdefault(alt_id, []).append((number(float(start), 'covered start'), number(float(end), 'covered end')))
    return covered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', required=True)
    parser.add_argument('--alignment', required=True, help='alignment.json from pov_alignment.py')
    parser.add_argument('--plan', required=True, help='Timeline plan to extend; its alternates are kept')
    parser.add_argument('--accept', action='append', required=True, type=parse_accept, metavar='ALT_SOURCE_ID:SPAN_INDEX',
                        help='Alignment span the reviewer confirmed on a pair sheet; repeatable')
    parser.add_argument('--covered', action='append', metavar='ALT_SOURCE_ID=FROM-TO',
                        help='Main seconds the reviewer confirmed on pair sheets beyond the span evidence; repeatable')
    parser.add_argument('--label-status', action='append', choices=['candidate', 'context', 'uncertain'],
                        help='Statuses that form blocks; must match review_timeline.py (default: candidate)')
    parser.add_argument('--close-gaps-sec', type=float, default=CLOSE_GAPS_SEC)
    parser.add_argument('--note', default='', help='Where the confirming pair sheets are saved')
    parser.add_argument('--out', required=True, help='New plan file')
    args = parser.parse_args()
    if Path(args.out).exists():
        raise ValueError('Use a new --out; the earlier plan is preserved')
    data, alignment, plan = read(args.events), read(args.alignment), read(args.plan)
    placed, unchecked, skipped = place(data, alignment, args.accept, parse_covered(args.covered),
                                       tuple(args.label_status or LABELED_STATUSES),
                                       number(args.close_gaps_sec, 'gap to close'), args.note)
    plan['alternates'] = plan.get('alternates', []) + placed
    write(args.out, plan)
    write(Path(args.out).with_suffix('.report.json'), {'placed': len(placed), 'unchecked': unchecked, 'skipped': skipped})
    print(f'{len(placed)} excerpts placed, {len(unchecked)} blocks need a pair-sheet check, '
          f'{len(skipped)} outside the alternate recording -> {args.out}')


if __name__ == '__main__':
    run_cli(main)
