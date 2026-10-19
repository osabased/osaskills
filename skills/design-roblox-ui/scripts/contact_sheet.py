#!/usr/bin/env python3
"""Lay renders out in one labelled grid image, to compare them side by side.

IMAGE may carry a label after "=", as in phone.png="Shop on phone"; the default
label is the file name. Images are scaled to --cell-width and laid out in rows.
Each --backdrop (white, black, busy, or an image such as a game screenshot) shows
every image over it, one cell per image and backdrop, to check that see-through
UI stays readable; render those images with rhr ui --transparent.

Exit codes: 0 sheet written; 2 bad arguments, an unreadable image or an unwritable --out.
Needs Python 3.11+ and Pillow 10.1+: uv run --no-project --with pillow python contact_sheet.py ...
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import os
from pathlib import Path
import random
import sys

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:  # pragma: no cover - exercised via subprocess in tests
    script = os.path.basename(sys.argv[0]) or "contact_sheet.py"
    print(
        f"ERROR: Pillow is required to run {script}. "
        "Install it with: python -m pip install pillow, or run: "
        f"uv run --no-project --with pillow python {sys.argv[0] or script} ...",
        file=sys.stderr,
    )
    sys.exit(2)

PADDING = 16
LABEL_GAP = 6
LABEL_SIZE = 18
TITLE_SIZE = 28
BACKGROUND = (38, 38, 38)
LABEL_COLOUR = (238, 238, 238)
BUSY_BLOCK = 32
NAMED_BACKDROPS = ("white", "black", "busy")


@dataclass(frozen=True)
class Cell:
    path: Path
    label: str
    backdrop: str | None = None


def positive(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, not {value}")
    return value


def parse_entry(text: str) -> tuple[Path, str]:
    """The image path and label in IMAGE or IMAGE=LABEL; the label defaults to the file name."""
    if Path(text).is_file():
        return Path(text), Path(text).stem
    for index, char in enumerate(text):
        if char == "=" and Path(text[:index]).is_file():
            return Path(text[:index]), text[index + 1 :]
    raise ValueError(f"image not found: {text}")


def backdrop_name(backdrop: str) -> str:
    return backdrop if backdrop in NAMED_BACKDROPS else Path(backdrop).stem


def expand(entries: list[tuple[Path, str]], backdrops: list[str]) -> list[Cell]:
    """One cell per image, or with backdrops one per image and backdrop, image by image."""
    if not backdrops:
        return [Cell(path, label) for path, label in entries]
    return [Cell(path, f"{label} · {backdrop_name(backdrop)}", backdrop) for path, label in entries for backdrop in backdrops]


def busy_backdrop(size: tuple[int, int]) -> Image.Image:
    """Blocks of random colour, the same every time, standing in for a busy game world."""
    columns, rows = (math.ceil(side / BUSY_BLOCK) for side in size)
    blocks = Image.frombytes("RGB", (columns, rows), random.Random(0).randbytes(columns * rows * 3))
    return blocks.resize((columns * BUSY_BLOCK, rows * BUSY_BLOCK), Image.Resampling.NEAREST).crop((0, 0, *size))


def backdrop_image(backdrop: str, size: tuple[int, int], loaded: dict[Path, Image.Image]) -> Image.Image:
    if backdrop == "white":
        return Image.new("RGBA", size, (255, 255, 255, 255))
    if backdrop == "black":
        return Image.new("RGBA", size, (0, 0, 0, 255))
    if backdrop == "busy":
        return busy_backdrop(size).convert("RGBA")
    return ImageOps.fit(loaded[Path(backdrop)], size, Image.Resampling.LANCZOS)


def label_font(size: int = LABEL_SIZE) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def text_height(font: ImageFont.FreeTypeFont) -> int:
    return sum(font.getmetrics())


def fit_text(text: str, font: ImageFont.FreeTypeFont, width: int) -> str:
    """The text, shortened with an ellipsis if it is wider than width."""
    if font.getlength(text) <= width:
        return text
    while text and font.getlength(text + "…") > width:
        text = text[:-1]
    return text.rstrip() + "…"


def scale_to_width(image: Image.Image, width: int) -> Image.Image:
    if image.width == width:
        return image
    return image.resize((width, max(1, round(image.height * width / image.width))), Image.Resampling.LANCZOS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("images", nargs="+", metavar="IMAGE", help='a render to show; add =LABEL to name its cell, as in phone.png="Shop on phone"')
    parser.add_argument("--out", type=Path, required=True, help="the PNG file to write")
    parser.add_argument("--columns", type=positive, help="cells per row (default: one per backdrop, or a near-square grid)")
    parser.add_argument("--cell-width", type=positive, default=600, metavar="PX", help="the width each image is scaled to (default 600)")
    parser.add_argument(
        "--backdrop",
        action="append",
        default=[],
        help="white, black, busy or an image file to show every image over (repeatable)",
    )
    parser.add_argument("--title", help="a heading above the grid")
    parser.add_argument("--max-size", type=positive, metavar="PX", help="shrink the finished sheet so its long side is at most PX")
    args = parser.parse_args(argv)

    try:
        entries = [parse_entry(text) for text in args.images]
    except ValueError as error:
        parser.error(str(error))
    for backdrop in args.backdrop:
        if backdrop not in NAMED_BACKDROPS and not Path(backdrop).is_file():
            parser.error(f"backdrop not found: {backdrop} (use white, black, busy or an image file)")

    renders = list(dict.fromkeys(path for path, _ in entries))
    pictures = [Path(backdrop) for backdrop in args.backdrop if backdrop not in NAMED_BACKDROPS]
    loaded: dict[Path, Image.Image] = {}
    for path in [*renders, *pictures]:
        try:
            with Image.open(path) as image:
                loaded[path] = image.convert("RGBA")
        except (OSError, Image.DecompressionBombError) as error:
            print(f"contact_sheet: can't read {path.as_posix()} as an image: {error}", file=sys.stderr)
            return 2
    if args.backdrop:
        for path in renders:
            if loaded[path].getextrema()[3][0] == 255:
                print(
                    f"contact_sheet: {path.as_posix()} has no see-through pixels, so its backdrops won't show; "
                    "render it with rhr ui --transparent",
                    file=sys.stderr,
                )

    cells = expand(entries, args.backdrop)
    scaled = {path: scale_to_width(loaded[path], args.cell_width) for path in renders}
    columns = args.columns or (len(args.backdrop) if len(args.backdrop) > 1 else math.ceil(math.sqrt(len(cells))))
    columns = min(columns, len(cells))
    rows = [cells[start : start + columns] for start in range(0, len(cells), columns)]

    font = label_font()
    title_font = label_font(TITLE_SIZE)
    label_height = text_height(font)
    title_height = text_height(title_font) + PADDING if args.title else 0
    row_heights = [label_height + LABEL_GAP + max(scaled[cell.path].height for cell in row) for row in rows]
    width = PADDING + columns * (args.cell_width + PADDING)
    height = PADDING + title_height + sum(row_height + PADDING for row_height in row_heights)

    sheet = Image.new("RGBA", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    y = PADDING
    if args.title:
        draw.text((PADDING, y), fit_text(args.title, title_font, width - 2 * PADDING), font=title_font, fill=LABEL_COLOUR)
        y += title_height
    for row, row_height in zip(rows, row_heights):
        for column, cell in enumerate(row):
            x = PADDING + column * (args.cell_width + PADDING)
            draw.text((x, y), fit_text(cell.label, font, args.cell_width), font=font, fill=LABEL_COLOUR)
            image = scaled[cell.path]
            top = y + label_height + LABEL_GAP
            if cell.backdrop:
                sheet.alpha_composite(backdrop_image(cell.backdrop, image.size, loaded), (x, top))
            sheet.alpha_composite(image, (x, top))
        y += row_height + PADDING

    if args.max_size and max(sheet.size) > args.max_size:
        scale = args.max_size / max(sheet.size)
        sheet = sheet.resize(tuple(max(1, round(side * scale)) for side in sheet.size), Image.Resampling.LANCZOS)

    try:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        sheet.convert("RGB").save(args.out, format="PNG")
    except OSError as error:
        print(f"contact_sheet: can't write {args.out.as_posix()}: {error.strerror or error}", file=sys.stderr)
        return 2
    print(f"wrote {args.out.as_posix()} ({sheet.width}x{sheet.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
