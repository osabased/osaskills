"""Packaging and reference integrity; behavior is evaluated with scenario runs."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PARENT_PATH = ROOT / "SKILL.md"
PARENT = PARENT_PATH.read_text(encoding="utf-8")


def _frontmatter() -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", PARENT, re.DOTALL)
    assert match, "SKILL.md must begin with YAML frontmatter"
    data = yaml.safe_load(match.group(1))
    assert isinstance(data, dict)
    return data


def _anchor(text: str) -> str:
    text = re.sub(r"[`*_~]", "", text.strip().lower())
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def _anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not match:
            continue
        base = _anchor(match.group(1))
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def test_frontmatter_is_valid():
    data = _frontmatter()
    assert data["name"] == ROOT.name
    assert isinstance(data["description"], str)
    assert 0 < len(data["description"]) <= 360


def test_relative_markdown_links_and_anchors_resolve():
    files = [PARENT_PATH, *(ROOT / "references").rglob("*.md")]
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for source in files:
        for target in link_re.findall(source.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("mailto:"):
                continue
            path_part, _, anchor = target.partition("#")
            target_path = source if not path_part else (source.parent / path_part).resolve()
            assert target_path.is_file(), f"{source}: missing link target {target}"
            if anchor:
                assert anchor in _anchors(target_path), f"{source}: missing anchor {target}"


def test_all_references_are_reachable_from_the_entrypoint():
    pending = [PARENT_PATH.resolve()]
    visited = set()
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    while pending:
        source = pending.pop()
        if source in visited:
            continue
        visited.add(source)
        for target in link_re.findall(source.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("mailto:"):
                continue
            path_part = target.partition("#")[0]
            destination = (source.parent / path_part).resolve() if path_part else source
            if destination.is_relative_to(ROOT.resolve()) and destination.suffix == ".md":
                pending.append(destination)
    expected = {p.resolve() for p in (ROOT / "references").rglob("*.md")}
    assert expected <= visited, f"Unreachable references: {expected - visited}"
