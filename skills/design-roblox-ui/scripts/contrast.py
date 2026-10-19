#!/usr/bin/env python3
"""Report the WCAG contrast ratio of foreground and background colour pairs.

Colours come in pairs, foreground first: contrast.py 2B1D14 F3E9D2 FFF8EC B54A24.
A colour is RRGGBB or RGB hex, with or without "#", or R,G,B from 0 to 255. Add
@T for a Roblox Transparency from 0 (opaque) to 1 (invisible), as in 2B1D14@0.35.
A see-through colour is composited the way the screen shows it, rounded to 8 bits.
A see-through background is checked over white and over black, since either can
be behind it, and the worse ratio is reported.

Exit codes: 0 every pair meets --min; 1 a pair falls short; 2 bad arguments.
Needs Python 3.11+ and nothing else.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import re
import sys

COLOUR_RE = re.compile(
    r"^(?:#?([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})|(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3}))"
    r"(?:@(\d+(?:\.\d*)?|\.\d+))?$"
)
FORMS = "use RRGGBB or RGB hex, or R,G,B from 0 to 255, each with an optional @T transparency from 0 to 1"
BACKDROPS = {"white": (255, 255, 255), "black": (0, 0, 0)}

RGB = tuple[int, int, int]


@dataclass(frozen=True)
class Colour:
    rgb: RGB
    transparency: float = 0.0

    def __str__(self) -> str:
        text = "{:02X}{:02X}{:02X}".format(*self.rgb)
        return f"{text}@{self.transparency:g}" if self.transparency else text


def parse_colour(text: str) -> Colour:
    match = COLOUR_RE.match(text.strip())
    if not match:
        raise ValueError(f"not a colour: {text} ({FORMS})")
    hex_digits, red, green, blue, transparency_text = match.groups()
    if hex_digits:
        if len(hex_digits) == 3:
            hex_digits = "".join(digit * 2 for digit in hex_digits)
        rgb = (int(hex_digits[0:2], 16), int(hex_digits[2:4], 16), int(hex_digits[4:6], 16))
    else:
        rgb = (int(red), int(green), int(blue))
    transparency = float(transparency_text) if transparency_text else 0.0
    if max(rgb) > 255 or transparency > 1:
        raise ValueError(f"not a colour: {text} ({FORMS})")
    return Colour(rgb, transparency)


def composite(colour: Colour, under: RGB) -> RGB:
    """The 8-bit colour the screen shows for colour drawn over under."""
    alpha = 1 - colour.transparency
    red, green, blue = (math.floor(top * alpha + below * (1 - alpha) + 0.5) for top, below in zip(colour.rgb, under))
    return red, green, blue


def luminance(rgb: RGB) -> float:
    def linear(value: int) -> float:
        channel = value / 255
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(value) for value in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def ratio(first: RGB, second: RGB) -> float:
    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def worst_ratio(foreground: Colour, background: Colour) -> tuple[float, str | None]:
    """The pair's contrast ratio, and the backdrop it was worst over when the background is see-through."""
    if not background.transparency:
        return ratio(composite(foreground, background.rgb), background.rgb), None
    results = []
    for name, backdrop in BACKDROPS.items():
        under = composite(background, backdrop)
        results.append((ratio(composite(foreground, under), under), name))
    return min(results, key=lambda result: result[0])


def shown(value: float, minimum: float) -> str:
    # WCAG doesn't round, so 4.499 fails 4.5 and must not read as 4.50.
    text = f"{value:.2f}"
    if value < minimum <= float(text):
        text = f"{math.floor(value * 100) / 100:.2f}"
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("colours", nargs="+", metavar="COLOUR", help="foreground then background, repeated for each pair")
    parser.add_argument("--min", type=float, default=4.5, help="the ratio each pair needs (default 4.5, body text)")
    parser.add_argument("--json", action="store_true", help="print one JSON array instead of text")
    args = parser.parse_args(argv)
    if not 1 <= args.min <= 21:
        parser.error("--min must be from 1 to 21")
    if len(args.colours) % 2:
        parser.error(f"colours come in pairs, foreground then background; got {len(args.colours)}")
    try:
        colours = [parse_colour(text) for text in args.colours]
    except ValueError as error:
        parser.error(str(error))

    results = []
    for foreground, background in zip(colours[::2], colours[1::2]):
        value, backdrop = worst_ratio(foreground, background)
        results.append(
            {
                "fg": str(foreground),
                "bg": str(background),
                "ratio": value,
                "min": args.min,
                "pass": value >= args.min,
                "backdrop": backdrop,
            }
        )

    if args.json:
        print(json.dumps(results, indent=1))
    else:
        for result in results:
            verdict = "PASS" if result["pass"] else "FAIL"
            line = f"{shown(result['ratio'], args.min):>5}:1  {verdict} {args.min:g}  {result['fg']} on {result['bg']}"
            if result["backdrop"]:
                line += f" (over {result['backdrop']})"
            print(line)
    return 0 if all(result["pass"] for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
