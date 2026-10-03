"""Suggest a LOCAL audio correspondence; never modify media or a timeline."""
import argparse
import contextlib
import hashlib
import importlib.metadata
import io
import json
import math
from pathlib import Path
import subprocess

from vod import number, probe, write


def peak_summary(result):
    if not result or not result.get('match_info'):
        return None
    if len(result['match_info']) != 1:
        raise ValueError('Expected exactly one comparison file')
    name, data = next(iter(result['match_info'].items()))
    offsets, strengths = data.get('offset_seconds', []), data.get('confidence', [])
    if not offsets or len(offsets) != len(strengths):
        return None
    values = [(float(t), float(s)) for t, s in zip(offsets, strengths)]
    if not all(math.isfinite(t) and math.isfinite(s) for t, s in values):
        raise ValueError('Non-finite matching result')
    offset, strength = values[0]
    # Adjacent peaks from one waveform/hash bin are not independent alternatives.
    rivals = [s for t, s in values[1:] if abs(t - offset) > .25]
    rival = max(rivals, default=0)
    return {'offset_b_local_minus_a_local_sec': offset, 'strength': strength,
            'strongest_separate_peak': rival,
            'dominance_ratio': strength / rival if rival > 0 else None,
            'upstream_rank': result.get('rankings', {}).get('match_info', {}).get(name),
            'peaks': [{'offset_sec': t, 'strength': s} for t, s in values]}


def assess(fingerprint, correlation, start_a, start_b):
    """Conservative triage from the small pilot; not calibrated confidence."""
    fp, corr = peak_summary(fingerprint), peak_summary(correlation)
    reasons = []
    if fp is None or corr is None:
        reasons.append('One or both methods returned no match')
    else:
        if fp['strength'] < 30:
            reasons.append('Fewer than 30 fingerprint matches')
        for label, result in [('Fingerprint', fp), ('Waveform', corr)]:
            if result['strength'] <= 0 or (result['dominance_ratio'] is not None and result['dominance_ratio'] < 2):
                reasons.append(label + ' peak is weak or ambiguous')
        if abs(fp['offset_b_local_minus_a_local_sec'] - corr['offset_b_local_minus_a_local_sec']) > .15:
            reasons.append('Fingerprint and waveform offsets disagree by more than 0.15 seconds')
    supported = not reasons
    offset = start_b - start_a + corr['offset_b_local_minus_a_local_sec'] if supported else None
    return {'status': 'candidate_needs_review' if supported else 'unresolved',
            'candidate_offset_b_minus_a_sec': offset,
            'clock_equation': 'B source seconds = A source seconds + candidate_offset_b_minus_a_sec',
            'fingerprint': fp, 'waveform_correlation': corr, 'reasons': reasons,
            'heuristics': {'minimum_fingerprint_matches': 30, 'minimum_separate_peak_ratio': 2,
                           'peak_separation_sec': .25, 'maximum_method_disagreement_sec': .15},
            'limitations': 'Pilot heuristics only, not a probability or synchronization guarantee. '
                          'Inspect shared audio and nearby visual evidence. Call latency can differ from picture timing. '
                          'A weak match does not mean the event is absent. Do not extrapolate across drift or discontinuities.'}


def validate_window(path, start, end, stream):
    path = Path(path).resolve(strict=True)
    metadata, duration = probe(path)
    number(start, 'window start'); number(end, 'window end')
    if not start < end <= duration:
        raise ValueError('Audio window must lie within the source duration')
    streams = [s['index'] for s in metadata['streams'] if s['codec_type'] == 'audio']
    if stream is None:
        if len(streams) != 1:
            raise ValueError('Choose --stream-a/--stream-b explicitly when a source has multiple audio streams')
        stream = streams[0]
    if stream not in streams:
        raise ValueError('Selected stream is not an audio stream')
    stat = path.stat()
    return {'path': str(path), 'start_sec': start, 'end_sec': end, 'audio_stream': stream,
            'source_duration_sec': duration, 'source_size': stat.st_size, 'source_mtime_ns': stat.st_mtime_ns}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for side in ('a', 'b'):
        parser.add_argument('--source-' + side, required=True)
        parser.add_argument('--start-' + side, required=True, type=float)
        parser.add_argument('--end-' + side, required=True, type=float)
        parser.add_argument('--stream-' + side, type=int, help='Absolute ffprobe stream index; inferred only for single-stream sources')
    parser.add_argument('--out', required=True, help='New output folder for analysis WAVs, raw results and candidate.json')
    args = parser.parse_args()
    if importlib.metadata.version('audalign') != '1.3.1':
        raise RuntimeError('Use the isolated Audalign 1.3.1 environment')
    import audalign as ad
    sources = [validate_window(getattr(args, 'source_' + s), getattr(args, 'start_' + s),
                              getattr(args, 'end_' + s), getattr(args, 'stream_' + s)) for s in ('a', 'b')]
    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a new output folder; existing matching evidence is preserved')
    out.mkdir(parents=True, exist_ok=True)
    for name, source in zip(('a', 'b'), sources):
        subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(source['start_sec']), '-i', source['path'],
                        '-t', str(source['end_sec'] - source['start_sec']), '-map', f"0:{source['audio_stream']}",
                        '-vn', '-ac', '1', '-ar', '44100', '-c:a', 'pcm_s16le', str(out / (name + '.wav'))], check=True)
    raw = {}
    for name, factory in [('fingerprint', ad.FingerprintRecognizer), ('correlation', ad.CorrelationRecognizer)]:
        recognizer = factory()
        recognizer.config.multiprocessing = False
        recognizer.config.num_processors = 1
        if name == 'fingerprint':
            recognizer.config.set_accuracy(3)
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            raw[name] = ad.recognize(str(out / 'a.wav'), str(out / 'b.wav'), recognizer=recognizer)
        # Audalign can return NumPy scalars; normalize before the standard writer.
        raw[name] = json.loads(json.dumps(raw[name], default=lambda x: x.item()))
        write(out / (name + '.json'), raw[name])
        (out / (name + '.log')).write_text(log.getvalue(), encoding='utf-8')
    result = {'schema': 'vod-local-audio-match/v1', 'audalign_version': '1.3.1',
              'analysis': {'sample_rate': 44100, 'channels': 1, 'fingerprint_accuracy': 3,
                           'multiprocessing': False,
                           'wav_sha256': {n: hashlib.sha256((out / (n + '.wav')).read_bytes()).hexdigest() for n in ('a', 'b')}},
              'source_a': sources[0], 'source_b': sources[1],
              **assess(raw['fingerprint'], raw['correlation'], sources[0]['start_sec'], sources[1]['start_sec'])}
    write(out / 'candidate.json', result)
    print(json.dumps({'status': result['status'], 'offset_b_minus_a_sec': result['candidate_offset_b_minus_a_sec'],
                      'reasons': result['reasons'], 'report': str(out / 'candidate.json')}, indent=2))


if __name__ == '__main__':
    main()
