"""Move each moment's cut points out to pauses in speech so sections start and end between sentences."""
import argparse
from pathlib import Path
import re
import subprocess

from pov_alignment import speech_lines
from vod import number, read, run_cli, write

LEAD_IN_SEC = 2.0
TAIL_SEC = 1.5
PAUSE_SEC = .5
SEARCH_SEC = 8.0
EDGE_SEC = .25
MIN_PADDING_SEC = .5
SILENCE_DB = -35
SILENCE_MIN_SEC = .3
SILENCE_EDGE = re.compile(r'silence_(start|end): ([0-9.]+)')


def speech_gaps(lines, duration):
    """Silent stretches between transcribed speech, with segments closer than PAUSE_SEC treated as one run."""
    runs = []
    for line in sorted(lines, key=lambda l: l['start']):
        if runs and line['start'] - runs[-1][1] < PAUSE_SEC:
            runs[-1][1] = max(runs[-1][1], line['end'])
        else:
            runs.append([line['start'], line['end']])
    edges = [0.0] + [t for run in runs for t in run] + [duration]
    return [(a, b) for a, b in zip(edges[::2], edges[1::2])]


def audio_silences(source, prepared):
    """Dips in the recording's first audio stream; cached beside the prepared packets."""
    cache = Path(prepared) / 'silence.json'
    settings = {'noise_db': SILENCE_DB, 'min_sec': SILENCE_MIN_SEC}
    if cache.exists() and read(cache)['settings'] == settings:
        return [tuple(pair) for pair in read(cache)['silences']]
    result = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(source), '-map', '0:a:0', '-vn', '-af',
                             f'silencedetect=n={SILENCE_DB}dB:d={SILENCE_MIN_SEC}', '-f', 'null', '-'],
                            check=True, capture_output=True, encoding='utf-8')
    silences, opened = [], None
    for kind, value in SILENCE_EDGE.findall(result.stderr):
        if kind == 'start':
            opened = float(value)
        elif opened is not None:
            silences.append((opened, float(value)))
            opened = None
    write(cache, {'settings': settings, 'silences': silences})
    return silences


def pauses(lines, silences, duration):
    """Every stretch with no speech or no sound at all, overlapping stretches joined."""
    merged = []
    for a, b in sorted(speech_gaps(lines, duration) + list(silences)):
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def snap(target, bound, found, outward):
    """The pause nearest the target that keeps the cut outside the moment; None if none is within reach."""
    best = None
    for a, b in found:
        edge = min(EDGE_SEC, (b - a) / 2)
        cut = min(max(target, a + edge), b - edge)
        too_close = cut > bound - MIN_PADDING_SEC if outward < 0 else cut < bound + MIN_PADDING_SEC
        if too_close:
            continue
        if abs(cut - target) <= SEARCH_SEC and (best is None or abs(cut - target) < abs(best - target)):
            best = cut
    return best


def snap_view(view, found, duration):
    start_target, end_target = max(0.0, view['start_sec'] - LEAD_IN_SEC), min(duration, view['end_sec'] + TAIL_SEC)
    start, end = snap(start_target, view['start_sec'], found, -1), snap(end_target, view['end_sec'], found, 1)
    notes = []
    if start is None:
        start = start_target
        notes.append('start has no speech pause within reach')
    if end is None:
        end = end_target
        notes.append('end has no speech pause within reach')
    return {'cut_start_sec': round(start, 3), 'cut_end_sec': round(end, 3), 'cut_notes': notes}


def snap_events(data, prepared):
    sources = {s['id']: s for s in data['sources']}
    found = {}
    for sid, folder in prepared.items():
        if sid not in sources:
            raise ValueError(f'Unknown source id {sid}')
        info, lines = speech_lines(folder)
        if Path(info['path']).resolve() != Path(sources[sid]['path']).resolve():
            raise ValueError(f'Prepared folder for {sid} was built from a different recording')
        duration = number(sources[sid]['duration_sec'], 'duration', .001)
        found[sid] = pauses(lines, audio_silences(sources[sid]['path'], folder), duration)
    summary = {'snapped': 0, 'mid_speech': 0}
    for event in data['events']:
        for view in event['perspectives']:
            if view['source_id'] in found:
                result = snap_view(view, found[view['source_id']], sources[view['source_id']]['duration_sec'])
                view.update(result)
                summary['mid_speech' if result['cut_notes'] else 'snapped'] += 1
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', required=True)
    parser.add_argument('--prepared', action='append', required=True, metavar='SOURCE_ID=FOLDER',
                        help='Prepared folder whose transcript sets the pauses for that source; repeatable')
    parser.add_argument('--out', required=True, help='New events file with cut_start_sec/cut_end_sec added')
    args = parser.parse_args()
    if Path(args.out).exists():
        raise ValueError('Use a new --out; the reviewed events file is preserved')
    prepared = {}
    for value in args.prepared:
        sid, sep, folder = value.partition('=')
        if not sep or not sid or not folder:
            raise ValueError(f'--prepared needs SOURCE_ID=FOLDER, got {value!r}')
        prepared[sid] = folder
    data = read(args.events)
    summary = snap_events(data, prepared)
    write(args.out, data)
    print(f"{summary['snapped']} views snapped to speech pauses, {summary['mid_speech']} left mid-speech -> {args.out}")


if __name__ == '__main__':
    run_cli(main)
