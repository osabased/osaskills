"""Read text from a fixed screen region (chat, kill feed, scoreboard) over a recording, for cross-POV matching."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from vod import number, probe, read, run_cli, text, write

OCR_SCRIPT = Path(__file__).with_name('ocr_frames.ps1')
CROP = re.compile(r'^(\d+):(\d+):(\d+):(\d+)$')
PTS_TIME = re.compile(r'pts_time:\s*([0-9.]+)')
WORD = re.compile(r"[^\W\d_]{3,}", re.UNICODE)
SAME_LINE_JACCARD = .5


def extract(source, start, end, crop, every, scale, folder):
    """One decoding pass; showinfo reports each selected frame's own source time."""
    select = f"select='isnan(prev_selected_t)+gte(t-prev_selected_t,{every})'"
    result = subprocess.run(
        ['ffmpeg', '-hide_banner', '-ss', str(start), '-t', str(end - start), '-i', str(source), '-an',
         '-vf', f'{select},crop={crop},scale=iw*{scale}:-2,showinfo', '-fps_mode', 'passthrough', '-q:v', '3',
         str(folder / 'crop_%05d.jpg')], check=True, capture_output=True, encoding='utf-8')
    times = [start + float(t) for t in PTS_TIME.findall(result.stderr)]
    files = sorted(folder.glob('crop_*.jpg'))
    if len(times) != len(files):
        raise RuntimeError('Selected frame count does not match reported timestamps; do not infer them')
    return list(zip(times, files))


def ocr(frames, source_id, workdir):
    if os.name != 'nt':
        raise RuntimeError('Region OCR uses the Windows OCR engine and needs Windows PowerShell')
    manifest, report = workdir / 'manifest.json', workdir / 'ocr.json'
    manifest.write_text(json.dumps([{'source_id': source_id, 'timestamp_sec': t, 'file': str(f.resolve())}
                                    for t, f in frames]), encoding='utf-8')
    # Documented fallback that works under a restrictive script execution policy.
    command = (f"$s=[IO.File]::ReadAllText('{OCR_SCRIPT}'); & ([scriptblock]::Create($s)) "
               f"-Manifest '{manifest}' -Out '{report}'")
    subprocess.run(['powershell.exe', '-NoProfile', '-Command', command], check=True, capture_output=True,
                   encoding='utf-8')
    return read(report)


def words_of(value):
    return {w.lower() for w in WORD.findall(value)}


def same_line(event, words, t, every):
    if t - event['last_sec'] > 2 * every:
        return False
    return len(event['_words'] & words) / len(event['_words'] | words) >= SAME_LINE_JACCARD


def merge_lines(frames, every):
    """Join the same on-screen line across consecutive samples into one interval."""
    events = []
    for frame in sorted(frames, key=lambda f: f['timestamp_sec']):
        t = frame['timestamp_sec']
        for line in frame['lines']:
            words = words_of(line['text'])
            if len(words) < 2:
                continue
            match = next((e for e in reversed(events) if same_line(e, words, t, every)), None)
            if match:
                match.update(last_sec=t, _words=match['_words'] | words)
            else:
                events.append({'first_sec': t, 'last_sec': t, 'text': line['text'], '_words': words})
    return [{k: v for k, v in e.items() if k != '_words'} for e in events]


def process(args):
    prepared = Path(args.prepared).resolve(strict=True)
    info = read(prepared / 'source.json')
    source = Path(args.source).resolve(strict=True)
    if Path(info['path']).resolve() != source:
        raise ValueError('--source must be the recording that --prepared was built from')
    if not CROP.match(args.crop):
        raise ValueError('--crop must be WIDTH:HEIGHT:X:Y in source pixels')
    every = number(args.every_sec, 'sampling interval', .5)
    duration = probe(source)[1]
    start = number(args.start, 'start')
    end = number(args.end, 'end', .001) if args.end is not None else duration
    if not start < end <= duration:
        raise ValueError('Window must lie inside the recording')
    folder = prepared / 'region-text' / text(args.name, 'region name')
    final = prepared / 'region-text' / f'{args.name}.json'
    if final.exists():
        raise ValueError('Region text already exists; use a new --name to preserve it')
    folder.mkdir(parents=True, exist_ok=True)
    frames = []
    for index, a in enumerate(range(int(start), int(end) + 1, args.chunk_sec)):
        b = min(a + args.chunk_sec, end)
        if a >= b:
            break
        chunk = folder / f'chunk-{index:04d}.json'
        if not chunk.exists():
            with tempfile.TemporaryDirectory(dir=folder) as scratch:
                scratch = Path(scratch)
                sampled = extract(source, max(a, start), b, args.crop, every, args.scale, scratch)
                report = ocr(sampled, info['id'], scratch) if sampled else {'frames': []}
                write(chunk, {'window': [max(a, start), b], 'frames': [
                    {'timestamp_sec': f['timestamp_sec'], 'lines': [{'text': line['text']} for line in f['lines']],
                    'image_sha256': f['image_sha256']}
                    for f in report['frames']]})
        frames.extend(read(chunk)['frames'])
        print(f'{max(a, start):.0f}-{b:.0f}s done', flush=True)
    lines = merge_lines(frames, every)
    write(final, {'schema': 'vod-region-text/v1', 'source_id': info['id'], 'source_path': str(source),
                  'name': args.name, 'crop': args.crop, 'every_sec': every, 'scale': args.scale,
                  'window': [start, end], 'sampled_frames': len(frames), 'lines': lines,
                  'limitations': 'Windows OCR over a fixed crop, sampled rather than continuous. Text can be misread '
                                 'or missed, and absence proves nothing. Lines are retrieval leads; confirm in the footage.'})
    print(f'{len(lines)} distinct lines from {len(frames)} samples -> {final}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--prepared', required=True, help="The source's prepared folder; output goes under region-text/")
    parser.add_argument('--name', required=True, help='Short name for the region, such as chat')
    parser.add_argument('--crop', required=True, help='WIDTH:HEIGHT:X:Y in source pixels, from a viewed frame')
    parser.add_argument('--every-sec', type=float, default=3)
    parser.add_argument('--scale', type=int, default=2, help='Upscale factor before OCR')
    parser.add_argument('--start', type=float, default=0)
    parser.add_argument('--end', type=float)
    parser.add_argument('--chunk-sec', type=int, default=600, help='Resumable unit; completed chunks are reused')
    process(parser.parse_args())


if __name__ == '__main__':
    run_cli(main)
