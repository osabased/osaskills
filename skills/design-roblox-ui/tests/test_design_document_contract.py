"""Packaging and reference integrity; behavior is evaluated with scenario runs."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PARENT_PATH = ROOT / "SKILL.md"
PARENT = PARENT_PATH.read_text(encoding="utf-8")
DOCS = [PARENT_PATH, *sorted((ROOT / "references").rglob("*.md"))]
AGENT_PATH = ROOT.parent.parent / "agents" / "roblox-ui-reviewer.md"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SCRIPT_RE = re.compile(r"<skill>/scripts/(\w+\.py)")
# claude.ai rejects an uploaded skill whose frontmatter has other keys.
BASE_SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def _frontmatter(text: str) -> dict:
    match = FRONTMATTER_RE.match(text)
    assert match, "file must begin with YAML frontmatter"
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
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        match = None if in_fence else re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not match:
            continue
        base = _anchor(match.group(1))
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def _relative_links(path: Path) -> list[str]:
    return [
        target
        for target in LINK_RE.findall(path.read_text(encoding="utf-8"))
        if "://" not in target and not target.startswith("mailto:")
    ]


def test_frontmatter_is_valid():
    data = _frontmatter(PARENT)
    assert set(data) <= BASE_SPEC_KEYS
    assert data["name"] == ROOT.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", data["name"]) and len(data["name"]) <= 64
    assert isinstance(data["description"], str)
    assert 0 < len(data["description"]) <= 1024
    assert "<" not in data["description"] and ">" not in data["description"]


def test_relative_markdown_links_and_anchors_resolve():
    for source in DOCS:
        for target in _relative_links(source):
            path_part, _, anchor = target.partition("#")
            target_path = source if not path_part else (source.parent / path_part).resolve()
            assert target_path.is_file(), f"{source}: missing link target {target}"
            if anchor:
                assert anchor in _anchors(target_path), f"{source}: missing anchor {target}"


def test_links_stay_inside_the_skill():
    # A standalone install copies this folder alone, so a link out of it would break.
    for source in DOCS:
        for target in _relative_links(source):
            path_part = target.partition("#")[0]
            if path_part:
                destination = (source.parent / path_part).resolve()
                assert destination.is_relative_to(ROOT.resolve()), f"{source}: link leaves the skill: {target}"


def test_all_references_are_reachable_from_the_entrypoint():
    pending = [PARENT_PATH.resolve()]
    visited = set()
    while pending:
        source = pending.pop()
        if source in visited:
            continue
        visited.add(source)
        for target in _relative_links(source):
            path_part = target.partition("#")[0]
            if path_part:
                destination = (source.parent / path_part).resolve()
                if destination.suffix == ".md":
                    pending.append(destination)
    expected = {p.resolve() for p in (ROOT / "references").rglob("*.md")}
    assert expected <= visited, f"Unreachable references: {expected - visited}"


def test_scripts_the_docs_name_exist():
    bundled = {p.name for p in (ROOT / "scripts").glob("*.py")}
    for source in DOCS:
        named = set(SCRIPT_RE.findall(source.read_text(encoding="utf-8")))
        assert named <= bundled, f"{source}: names missing scripts {named - bundled}"


def test_skill_md_names_every_bundled_script():
    bundled = {p.name for p in (ROOT / "scripts").glob("*.py")}
    assert bundled
    assert bundled <= set(SCRIPT_RE.findall(PARENT)), "SKILL.md's Tools must name every script"


def test_reviewer_agent_is_read_only_and_on_opus():
    data = _frontmatter(AGENT_PATH.read_text(encoding="utf-8"))
    assert data["name"] == "roblox-ui-reviewer"
    assert data["model"] == "opus"
    assert {tool.strip() for tool in data["tools"].split(",")} == {"Read", "Glob"}
    assert data["omitClaudeMd"] is True
    assert data["description"]


def test_review_md_quotes_the_reviewer_instructions_word_for_word():
    body = FRONTMATTER_RE.sub("", AGENT_PATH.read_text(encoding="utf-8"), count=1).strip()
    review = (ROOT / "references" / "review.md").read_text(encoding="utf-8")
    match = re.search(
        r"^## The reviewer's instructions\n.*?^```text\n(.*?)^```$", review, re.MULTILINE | re.DOTALL
    )
    assert match, "review.md must quote the instructions in a text block"
    assert match.group(1).strip() == body
