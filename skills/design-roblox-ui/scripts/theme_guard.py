#!/usr/bin/env python3
"""Fail on colours, fonts and text sizes written into UI code instead of taken from the theme.

Checks the .luau and .lua files under each folder given, and each file given by
name. It flags Color3.new, Color3.fromRGB, Color3.fromHex, Color3.fromHSV,
BrickColor, Font.new, Font.fromEnum, Font.fromName, Font.fromId and Enum.Font,
and TextSize, MinTextSize or MaxTextSize set to a number. Comments and strings
are skipped, and so is a line whose comment says "-- theme-guard: allow <reason>".
Allow the theme module itself, and style-tile drafts while they exist, with --allow.

Exit codes: 0 no raw values; 1 raw values found; 2 bad arguments or an unreadable file.
Needs Python 3.11+ and nothing else.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import sys

NAME_START = r"(?<![\w.:])"
PATTERNS = [
    ("raw colour", re.compile(NAME_START + r"(?P<what>Color3\s*\.\s*(?:new|fromRGB|fromHex|fromHSV))\b")),
    ("raw colour", re.compile(NAME_START + r"(?P<what>BrickColor)\s*\.")),
    ("raw font", re.compile(NAME_START + r"(?P<what>Font\s*\.\s*(?:new|fromEnum|fromName|fromId))\b")),
    ("raw font", re.compile(NAME_START + r"(?P<what>Enum\s*\.\s*Font)\s*\.")),
    ("raw text size", re.compile(r"\b(?P<what>(?:Min|Max)?TextSize\s*=\s*\d[\d.]*)")),
]
ALLOW_RE = re.compile(r"--\s*theme-guard:\s*allow\b(.*)")
LONG_OPEN_RE = re.compile(r"\[(=*)\[")
LINE_END_RE = re.compile(r"[\r\n]")
WHITESPACE_RE = re.compile(r"\s+")
LUAU_SPACE = " \t\r\n\v\f"
SUFFIXES = (".luau", ".lua")
FIX = 'Take them from the theme module, or mark a real one-off with "-- theme-guard: allow <reason>".'


@dataclass
class Finding:
    number: int
    values: list[str]
    needs_reason: bool = False


# Mirrors Luau's readBackslashInString, so a string continued onto the next line reads as Luau reads it.
def _after_escape(source: str, index: int) -> int:
    index += 1
    if index >= len(source):
        return index
    if source[index] == "\r":
        index += 1
        return index + 1 if source.startswith("\n", index) else index
    if source[index] == "z":
        index += 1
        while index < len(source) and source[index] in LUAU_SPACE:
            index += 1
        return index
    return index + 1


def _quoted_end(source: str, index: int, delimiter: str) -> int:
    while index < len(source) and source[index] not in (delimiter, "\r", "\n"):
        index = _after_escape(source, index) if source[index] == "\\" else index + 1
    return index


def _backtick_end(source: str, index: int) -> int:
    while index < len(source) and source[index] not in ("`", "{", "\r", "\n"):
        if source.startswith("\\u{", index):
            index += 3
        else:
            index = _after_escape(source, index) if source[index] == "\\" else index + 1
    return index


def _long_end(source: str, index: int, level: int) -> int:
    close = source.find("]" + "=" * level + "]", index)
    return len(source) if close < 0 else close


def split_code(source: str) -> tuple[str, str]:
    """Split Luau source into its code and its comments, each as long as the source with newlines kept.

    The code has comments and string contents blanked but keeps string delimiters; the
    comments have everything else blanked.
    """
    code = list(source)
    comments = ["\n" if char == "\n" else " " for char in source]

    def blank(start: int, end: int) -> None:
        for position in range(start, end):
            if code[position] != "\n":
                code[position] = " "

    # One entry per interpolation open in a backtick string: the braces opened inside it so far.
    braces: list[int] = []
    index = 0
    while index < len(source):
        char = source[index]
        if source.startswith("--", index):
            opener = LONG_OPEN_RE.match(source, index + 2)
            if opener:
                level = len(opener[1])
                end = min(_long_end(source, opener.end(), level) + level + 2, len(source))
            else:
                line_end = LINE_END_RE.search(source, index)
                end = line_end.start() if line_end else len(source)
            comments[index:end] = source[index:end]
            blank(index, end)
            index = end
        elif char in "\"'":
            end = _quoted_end(source, index + 1, char)
            blank(index + 1, end)
            index = end + 1 if source.startswith(char, end) else end
        elif char == "`" or (char == "}" and braces and braces[-1] == 0):
            if char == "}":
                braces.pop()
            end = _backtick_end(source, index + 1)
            blank(index + 1, end)
            closer = source[end : end + 1]
            if closer == "{":
                braces.append(0)
            index = end + 1 if closer in ("`", "{") else end
        elif char in "{}" and braces:
            braces[-1] += 1 if char == "{" else -1
            index += 1
        elif char == "[" and (opener := LONG_OPEN_RE.match(source, index)):
            level = len(opener[1])
            end = _long_end(source, opener.end(), level)
            blank(opener.end(), end)
            index = min(end + level + 2, len(source))
        else:
            index += 1
    return "".join(code), "".join(comments)


def scan(source: str) -> list[Finding]:
    """The lines of Luau source that hold raw values, in order, leaving out lines allowed with a reason."""
    code, comments = split_code(source)
    line_starts = [0, *(match.end() for match in re.finditer("\n", code))]
    found: dict[int, list[tuple[int, str]]] = {}
    for kind, pattern in PATTERNS:
        for match in pattern.finditer(code):
            number = bisect_right(line_starts, match.start())
            found.setdefault(number, []).append((match.start(), f"{kind} {WHITESPACE_RE.sub('', match['what'])}"))
    comment_lines = comments.split("\n")
    findings = []
    for number in sorted(found):
        marker = ALLOW_RE.search(comment_lines[number - 1])
        if marker and marker[1].strip():
            continue
        findings.append(Finding(number, [value for _, value in sorted(found[number])], marker is not None))
    return findings


def allow_glob(text: str) -> str:
    glob = PurePosixPath(text.replace("\\", "/")).as_posix()
    if glob == ".":
        raise argparse.ArgumentTypeError(f"an --allow glob must name a file or folder, not {text!r}")
    return glob


def allowed(path: Path, globs: list[str]) -> bool:
    """Whether the file, or a folder it is in, matches one of the globs."""
    candidate = PurePosixPath(path.as_posix())
    return any(part.match(glob) for part in (candidate, *candidate.parents) if part.name for glob in globs)


def plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("paths", nargs="+", type=Path, metavar="PATH", help="folders to search for .luau and .lua files, or files to check")
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        type=allow_glob,
        metavar="GLOB",
        help="skip files that match, or that sit in a folder that matches, such as the theme module (repeatable)",
    )
    args = parser.parse_args(argv)

    files: dict[Path, None] = {}
    for path in args.paths:
        if path.is_file():
            files[path] = None
        elif path.is_dir():
            found = [child for child in path.rglob("*") if child.suffix in SUFFIXES and child.is_file()]
            if not found:
                parser.error(f"{path.as_posix()} has no .luau or .lua files")
            files.update(dict.fromkeys(found))
        else:
            parser.error(f"path not found: {path.as_posix()}")

    sources: dict[Path, str] = {}
    for path in sorted(files, key=lambda file: file.as_posix()):
        if allowed(path, args.allow):
            continue
        try:
            sources[path] = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            print(f"theme_guard: {path.as_posix()} is not UTF-8 text", file=sys.stderr)
            return 2
        except OSError as error:
            print(f"theme_guard: can't read {path.as_posix()}: {error.strerror or error}", file=sys.stderr)
            return 2

    values = 0
    flagged = 0
    for path, source in sources.items():
        findings = scan(source)
        if not findings:
            continue
        flagged += 1
        lines = source.split("\n")
        for finding in findings:
            values += len(finding.values)
            note = " (an allow marker needs a reason)" if finding.needs_reason else ""
            print(f"{path.as_posix()}:{finding.number}: {', '.join(finding.values)}: {lines[finding.number - 1].strip()}{note}")

    if values:
        print(f"theme_guard: {plural(values, 'raw value')} in {plural(flagged, 'file')}. {FIX}")
        return 1
    print(f"theme_guard: {plural(len(sources), 'file')} checked, no raw values.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
