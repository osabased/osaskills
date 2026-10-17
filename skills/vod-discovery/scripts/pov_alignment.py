"""Suggest where each alternate POV overlaps the main POV from shared speech; never writes a placement."""
import argparse
from bisect import bisect_left, bisect_right
from collections import defaultdict
import itertools
import math
from pathlib import Path
import random
import re

from evidence import completed_packets
from vod import number, read, run_cli, write

WORD = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.UNICODE)
QUIET_GAP_SEC = 240
SHUFFLES = 20


def evidence_lines(prepared):
    """Speech from each packet's core interval (so overlaps are not counted twice) plus any region text."""
    info, lines = speech_lines(prepared)
    for path in sorted((Path(prepared) / 'region-text').glob('*.json')):
        region = read(path)
        if region['schema'] != 'vod-region-text/v1' or region['source_id'] != info['id']:
            raise ValueError(f'{path} does not belong to this prepared source')
        for line in region['lines']:
            words = [w.lower() for w in WORD.findall(line['text'])]
            if words:
                lines.append({'id': f'screen:{path.stem}:{len(lines)}', 'start': line['first_sec'],
                              'end': line['first_sec'], 'words': words})
    return info, lines


def speech_lines(prepared):
    info, packets = completed_packets(prepared)
    lines = []
    for attempt in packets:
        packet, transcript = read(attempt / 'packet.json'), read(attempt / 'transcript.json')
        core_start, core_end = packet['core_start_sec'], packet['core_end_sec']
        for segment in transcript['segments']:
            a, b = number(segment['start'], 'speech start'), number(segment['end'], 'speech end')
            if not core_start <= (a + b) / 2 < core_end or b <= a:
                continue
            words = [w.lower() for w in WORD.findall(segment['text'])]
            if words:
                lines.append({'id': f'speech:{len(lines)}', 'start': a, 'end': b, 'words': words})
    return info, lines


def phrase_index(lines):
    """Map each phrase to (estimated time, utterance) pairs; a phrase's time follows its word position in the segment."""
    index = defaultdict(list)
    for line in lines:
        words, seen = line['words'], set()
        for size in (1, 2, 3):
            for i in range(len(words) - size + 1):
                phrase = ' '.join(words[i:i + size])
                if size == 1 and len(phrase) < 5 or phrase in seen:
                    continue
                seen.add(phrase)
                position = (i + size / 2) / len(words)
                index[phrase].append((line['start'] + position * (line['end'] - line['start']), line['id']))
    return index


def word_rarity(all_lines):
    """Words heard in many utterances across every POV say little about shared moments."""
    document_frequency = defaultdict(int)
    for line in all_lines:
        for word in set(line['words']):
            document_frequency[word] += 1
    total = len(all_lines)
    return lambda word: math.log(total / document_frequency.get(word, 1))


def votes(main_index, alt_index, max_repeats, rarity):
    """Every shared rare phrase votes for the offset between the two clocks."""
    found = []
    for phrase, main_times in main_index.items():
        alt_times = alt_index.get(phrase)
        if not alt_times or len(main_times) > max_repeats or len(alt_times) > max_repeats:
            continue
        weight = sum(rarity(word) for word in phrase.split()) / (len(main_times) * len(alt_times))
        for (t_main, utterance), (t_alt, _) in itertools.product(main_times, alt_times):
            found.append({'phrase': phrase, 'main_sec': t_main, 'alt_sec': t_alt, 'utterance': utterance,
                          'offset_sec': t_alt - t_main, 'weight': weight})
    return found


def utterance_score(group):
    """Each main utterance counts once, through its most distinctive shared phrase."""
    best = defaultdict(float)
    for vote in group:
        best[vote['utterance']] = max(best[vote['utterance']], vote['weight'])
    return sum(best.values()), len(best)


def peaks(found, tolerance, minimum_utterances, count, floor=0.0):
    """Greedy offset peaks scored by the distinct utterances that agree within the tolerance."""
    remaining, result = sorted(found, key=lambda v: v['offset_sec']), []
    while remaining and len(result) < count:
        offsets = [v['offset_sec'] for v in remaining]
        scored = []
        for o in offsets:
            low, high = bisect_left(offsets, o - tolerance), bisect_right(offsets, o + tolerance)
            score, utterances = utterance_score(remaining[low:high])
            scored.append((score, utterances, low, high))
        score, utterances, low, high = max(scored)
        if score <= floor or utterances < minimum_utterances:
            break
        group = remaining[low:high]
        offset = sum(v['offset_sec'] for v in group) / len(group)
        result.append({'offset_sec': offset, 'score': score, 'distinct_utterances': utterances, 'votes': group})
        remaining = [v for v in remaining if abs(v['offset_sec'] - offset) > 5 * tolerance]
    return result


def chance_floor(main_index, alt_lines, alt_duration, max_repeats, rarity, tolerance):
    """Strongest peak that speech re-timed at random produces; a real offset has to beat it."""
    generator, best = random.Random(0), 0.0
    for _ in range(SHUFFLES):
        moved = [dict(line, start=start, end=start + line['end'] - line['start'])
                 for line, start in ((line, generator.uniform(0, alt_duration)) for line in alt_lines)]
        found = votes(main_index, phrase_index(moved), max_repeats, rarity)
        top = peaks(found, tolerance, 1, 1)
        best = max(best, top[0]['score'] if top else 0.0)
    return best


def quiet_gaps(times):
    """Stretches inside a span where no utterance supports the offset."""
    times = sorted(set(times))
    return [{'from_main_sec': round(x, 2), 'to_main_sec': round(y, 2)}
            for x, y in zip(times, times[1:]) if y - x > QUIET_GAP_SEC]


def describe(peak, floor, alt_info, tolerance):
    group = sorted(peak['votes'], key=lambda v: v['main_sec'])
    utterances = {v['utterance'] for v in group}
    offsets = [v['offset_sec'] for v in group]
    examples = sorted(group, key=lambda v: -v['weight'])[:5]
    return {'status': 'candidate_needs_review' if peak['score'] > floor else 'weak_lead',
            'alt_source_id': alt_info['id'],
            'alt_equals_main_plus_sec': round(peak['offset_sec'], 2),
            'offset_spread_sec': round(max(offsets) - min(offsets), 2),
            'tolerance_sec': tolerance,
            'first_support_main_sec': round(group[0]['main_sec'], 2),
            'last_support_main_sec': round(group[-1]['main_sec'], 2),
            'supporting_utterances': peak['distinct_utterances'],
            'supporting_by_kind': {kind: sum(1 for u in utterances if u.startswith(kind)) for kind in ('speech', 'screen')},
            'score': round(peak['score'], 1),
            'strongest_chance_score': round(floor, 1),
            'quiet_gaps': quiet_gaps(v['main_sec'] for v in group),
            'strongest_phrases': [{'phrase': v['phrase'], 'main_sec': round(v['main_sec'], 2),
                                   'alt_sec': round(v['alt_sec'], 2)} for v in examples]}


def align(main_dir, alt_dirs, tolerance=3.0, minimum_utterances=3, max_repeats=3, count=4):
    main_info, main_lines = evidence_lines(main_dir)
    alternates = [evidence_lines(alt_dir) for alt_dir in alt_dirs]
    rarity = word_rarity(main_lines + [line for _, lines in alternates for line in lines])
    main_index = phrase_index(main_lines)
    report = {'schema': 'vod-pov-alignment/v1', 'main_source_id': main_info['id'],
              'clock_equation': 'alt source seconds = main source seconds + alt_equals_main_plus_sec',
              'settings': {'tolerance_sec': tolerance, 'minimum_distinct_utterances': minimum_utterances,
                           'maximum_phrase_repeats': max_repeats, 'quiet_gap_sec': QUIET_GAP_SEC,
                           'chance_shuffles': SHUFFLES},
              'limitations': 'Speech-derived leads at transcript-segment resolution, not synchronization. '
                             'Verify at least one visual anchor per span before placing footage. '
                             "Coverage outside a span's supported interval and inside its quiet gaps is unknown, "
                             'and no match is not absence.',
              'alternates': []}
    for alt_info, alt_lines in alternates:
        found = votes(main_index, phrase_index(alt_lines), max_repeats, rarity)
        floor = chance_floor(main_index, alt_lines, alt_info['duration_sec'], max_repeats, rarity, tolerance)
        spans = [describe(p, floor, alt_info, tolerance)
                 for p in peaks(found, tolerance, minimum_utterances, count)]
        report['alternates'].append({'source_id': alt_info['id'], 'path': alt_info['path'],
                                     'shared_phrase_votes': len(found),
                                     'status': 'candidates' if any(x['status'] == 'candidate_needs_review' for x in spans) else 'weak_leads_only' if spans else 'unresolved',
                                     'spans': spans})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', required=True, help='Prepared folder of the main POV (one folder per part)')
    parser.add_argument('--alt', action='append', required=True, help='Prepared folder of an alternate POV; repeatable')
    parser.add_argument('--out', required=True, help='New alignment.json path')
    parser.add_argument('--tolerance-sec', type=float, default=3.0)
    parser.add_argument('--minimum-utterances', type=int, default=3)
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists():
        raise ValueError('Use a new --out; existing alignment evidence is preserved')
    report = align(args.main, args.alt, args.tolerance_sec, args.minimum_utterances)
    write(out, report)
    for alt in report['alternates']:
        print(alt['source_id'], alt['status'], f"({alt['shared_phrase_votes']} shared-phrase votes)")
        for span in alt['spans']:
            print(f"  alt = main {span['alt_equals_main_plus_sec']:+.1f}s  main {span['first_support_main_sec']:.0f}-"
                  f"{span['last_support_main_sec']:.0f}s  {span['supporting_utterances']} utterances  "
                  f"score {span['score']} vs chance {span['strongest_chance_score']}  [{span['status']}]")


if __name__ == '__main__':
    run_cli(main)
