#!/usr/bin/env python3
"""Measure the main colours of reference images, as hex with each one's share.

A model looking at a picture guesses its colours; this reads them. Each image is
shrunk to --size, its see-through pixels are dropped, and its colours are grouped
by median cut. Groups closer than --merge, a distance in RGB units, are joined
under the larger one's colour. Colours under --min-share of an image are left
out, so lower it to catch a small accent. With several images, a last section
weighs each image equally, to show the colours they share.

Exit codes: 0 colours printed; 2 bad arguments, or an image that can't be read or has no opaque pixels.
Needs Python 3.11+ and Pillow 10.1+: uv run --no-project --with pillow python palette.py ...
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:  # pragma: no cover - exercised via subprocess in tests
    script = os.path.basename(sys.argv[0]) or "palette.py"
    print(
        f"ERROR: Pillow is required to run {script}. "
        "Install it with: python -m pip install pillow, or run: "
        f"uv run --no-project --with pillow python {sys.argv[0] or script} ...",
        file=sys.stderr,
    )
    sys.exit(2)

GROUPS = 16

RGB = tuple[int, int, int]
Swatch = tuple[RGB, float]


def opaque_pixels(path: str, size: int) -> bytes:
    """The image's opaque pixels, packed as RGB bytes."""
    with Image.open(path) as image:
        image = image.convert("RGBA")
    # Nearest keeps every sampled pixel a colour the image really has; averaging would invent edge blends.
    image.thumbnail((size, size), Image.Resampling.NEAREST)
    data = image.tobytes()
    return b"".join(data[start : start + 3] for start in range(0, len(data), 4) if data[start + 3] >= 128)


def groups(pixels: bytes) -> list[Swatch]:
    total = len(pixels) // 3
    strip = Image.frombytes("RGB", (total, 1), pixels)
    quantized = strip.quantize(colors=GROUPS, method=Image.Quantize.MEDIANCUT)
    flat = quantized.getpalette() or []
    return [
        ((flat[index * 3], flat[index * 3 + 1], flat[index * 3 + 2]), count / total)
        for count, index in quantized.getcolors(GROUPS) or []
    ]


def merged(swatches: list[Swatch], distance: float) -> list[Swatch]:
    kept: list[list] = []
    for rgb, share in sorted(swatches, key=lambda swatch: swatch[1], reverse=True):
        for entry in kept:
            if math.dist(rgb, entry[0]) <= distance:
                entry[1] += share
                break
        else:
            kept.append([rgb, share])
    return sorted(((rgb, share) for rgb, share in kept), key=lambda swatch: swatch[1], reverse=True)


def shown(swatches: list[Swatch], minimum: float, limit: int) -> list[Swatch]:
    return [swatch for swatch in swatches if swatch[1] >= minimum][:limit]


def hex_of(rgb: RGB) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("images", nargs="+", metavar="IMAGE", help="reference images, such as docs/design/refs/*.png")
    parser.add_argument("--colours", type=int, default=8, help="the most colours to list per image (default 8)")
    parser.add_argument("--min-share", type=float, default=0.02, help="the least share of an image to list (default 0.02)")
    parser.add_argument("--merge", type=float, default=24, help="join colours this close in RGB units (default 24)")
    parser.add_argument("--size", type=int, default=256, help="shrink each image to this many pixels on its long side first (default 256)")
    parser.add_argument("--json", action="store_true", help="print one JSON object instead of text")
    args = parser.parse_args(argv)
    if args.colours < 1:
        parser.error("--colours must be at least 1")
    if not 0 <= args.min_share <= 1:
        parser.error("--min-share must be from 0 to 1")
    if args.merge < 0:
        parser.error("--merge can't be negative")
    if args.size < 8:
        parser.error("--size must be at least 8")

    per_image: dict[str, list[Swatch]] = {}
    for path in args.images:
        try:
            pixels = opaque_pixels(path, args.size)
        except (OSError, UnidentifiedImageError) as error:
            parser.error(f"can't read {path}: {error}")
        if not pixels:
            parser.error(f"{path} has no opaque pixels")
        per_image[path] = merged(groups(pixels), args.merge)

    sections = [(path, shown(swatches, args.min_share, args.colours)) for path, swatches in per_image.items()]
    if len(per_image) > 1:
        pooled = [(rgb, share / len(per_image)) for swatches in per_image.values() for rgb, share in swatches]
        sections.append((f"All {len(per_image)} images", shown(merged(pooled, args.merge), args.min_share, args.colours)))

    if args.json:
        print(json.dumps({name: [{"hex": hex_of(rgb), "share": round(share, 4)} for rgb, share in swatches] for name, swatches in sections}, indent=1))
    else:
        for name, swatches in sections:
            print(name)
            for rgb, share in swatches:
                print(f"  {hex_of(rgb)}  {share:>6.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
