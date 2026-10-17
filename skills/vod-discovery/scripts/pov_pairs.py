"""Tile main and alternate frames at a candidate offset so a viewer can confirm or reject the link."""
import argparse
from pathlib import Path
import subprocess

from vod import clock, number, probe, run_cli, write

CELL_WIDTH = 640
LABEL_HEIGHT = 22


def grab(source, seconds, target):
    subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{seconds:.3f}', '-i', str(source), '-frames:v', '1',
                    '-vf', f'scale={CELL_WIDTH}:-2', '-q:v', '3', str(target)], check=True)
    return target.is_file()


def tile(rows, out):
    from PIL import Image, ImageDraw
    images = [(label, Image.open(main), Image.open(alt)) for label, main, alt in rows]
    height = max(max(m.height, a.height) for _, m, a in images) + LABEL_HEIGHT
    sheet = Image.new('RGB', (2 * CELL_WIDTH, height * len(images)), 'black')
    draw = ImageDraw.Draw(sheet)
    for row, (label, main, alt) in enumerate(images):
        top = row * height
        draw.text((6, top + 5), label, fill='white')
        sheet.paste(main, (0, top + LABEL_HEIGHT))
        sheet.paste(alt, (CELL_WIDTH, top + LABEL_HEIGHT))
    sheet.save(out, quality=85)


def pairs(args):
    main_duration, alt_duration = probe(args.main_source)[1], probe(args.alt_source)[1]
    number(args.offset_sec, 'offset', -alt_duration)
    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a new --out folder; existing evidence is preserved')
    (out / 'frames').mkdir(parents=True, exist_ok=True)
    rows, records, skipped = [], [], []
    for index, t_main in enumerate(args.main_times):
        t_alt = t_main + args.offset_sec
        if not 0 <= t_main < main_duration or not 0 <= t_alt < alt_duration:
            skipped.append({'main_sec': t_main, 'reason': 'outside one of the recordings'})
            continue
        main_file, alt_file = out / 'frames' / f'main_{index:02d}.jpg', out / 'frames' / f'alt_{index:02d}.jpg'
        if grab(args.main_source, t_main, main_file) and grab(args.alt_source, t_alt, alt_file):
            rows.append((f'main {clock(t_main)}   |   alternate {clock(t_alt)}   (offset {args.offset_sec:+.1f}s)',
                         main_file, alt_file))
            records.append({'main_sec': t_main, 'alt_sec': t_alt, 'main_frame': main_file.name, 'alt_frame': alt_file.name})
    if not rows:
        raise ValueError('No requested time falls inside both recordings')
    sheets = []
    for number_, start in enumerate(range(0, len(rows), args.rows_per_sheet), 1):
        sheet = out / f'pairs_{number_:02d}.jpg'
        tile(rows[start:start + args.rows_per_sheet], sheet)
        sheets.append(sheet.name)
    write(out / 'pairs.json', {'schema': 'vod-pov-pairs/v1', 'main_source': str(Path(args.main_source).resolve()),
                              'alt_source': str(Path(args.alt_source).resolve()),
                              'alt_equals_main_plus_sec': args.offset_sec, 'pairs': records, 'skipped': skipped,
                              'sheets': sheets,
                              'limitations': 'Single sampled frames. Matching scenery proves nothing; look for the same '
                                             'event, item, notice or player action in both columns.'})
    print('\n'.join(str(out / name) for name in sheets))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main-source', required=True)
    parser.add_argument('--alt-source', required=True)
    parser.add_argument('--offset-sec', required=True, type=float, help='alternate seconds = main seconds + offset')
    parser.add_argument('--main-times', required=True, type=lambda v: [float(x) for x in v.split(',')],
                        help='Comma-separated main source seconds')
    parser.add_argument('--rows-per-sheet', type=int, default=4)
    parser.add_argument('--out', required=True, help='New folder for the sheets, frames and pairs.json')
    pairs(parser.parse_args())


if __name__ == '__main__':
    run_cli(main)
