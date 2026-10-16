"""Packaging/navigation checks. Behavioral outcomes live in evals, not prose assertions."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PARENT = (ROOT / "SKILL.md").read_text(encoding="utf-8")
REFERENCES = {
    path.name: path.read_text(encoding="utf-8")
    for path in (ROOT / "references").glob("*.md")
}


def _mode(name: str) -> str:
    match = re.search(
        rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)",
        PARENT,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing parent mode {name!r}"
    return match.group(1)


def _links(text: str) -> set[str]:
    return set(re.findall(r"\[[^\]]+\]\(([^)]+)\)", text))


def _anchors(path: Path) -> set[str]:
    """GitHub-style heading anchors (the same rule validate_skill.py uses)."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        match = None if in_fence else re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not match:
            continue
        base = re.sub(r"[^\w\s-]", "", re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", match.group(1)).lower())
        base = re.sub(r"\s", "-", base)
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def test_parent_frontmatter_is_valid_for_claude():
    meta = yaml.safe_load(PARENT.split("---", 2)[1])
    assert meta["name"] == ROOT.name
    assert 0 < len(meta["description"]) <= 1024
    assert "<" not in meta["description"] and ">" not in meta["description"]


def test_relative_markdown_links_and_anchors_resolve():
    files = [
        ROOT / "SKILL.md",
        *(ROOT / "references").glob("*.md"),
        *(ROOT / "templates").glob("*.md"),
        *(ROOT / "examples").rglob("*.md"),
        ROOT / "evals" / "README.md",
    ]
    link_re = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
    for source in files:
        text = re.sub(r"```.*?```", "", source.read_text(encoding="utf-8"), flags=re.S)
        for target in link_re.findall(text):
            if "://" in target or target.startswith("mailto:"):
                continue
            path_part, _, anchor = target.partition("#")
            if source.parent.name == "templates" and path_part.startswith("references/"):
                continue  # scaffold link in the library skill template
            target_path = source if not path_part else (source.parent / path_part).resolve()
            if path_part.endswith(".example.yaml") or target_path.name == "resource.yaml":
                continue  # examples rename their descriptor when materialized
            assert target_path.exists(), f"{source}: missing link target {target}"
            if anchor:
                assert anchor in _anchors(target_path), f"{source}: missing anchor {target}"


def test_every_reference_is_linked_from_skill_md_or_another_reference():
    linked = set()
    for text in (PARENT, *REFERENCES.values()):
        for target in _links(text):
            linked.add(Path(target.partition("#")[0]).name)
    orphans = sorted(name for name in REFERENCES if name not in linked)
    assert orphans == [], f"unreferenced files: {orphans}"


def test_evaluate_compare_routes_only_to_choosing():
    assert _links(_mode("Evaluate or compare")) == {"references/choosing.md"}


def test_add_adopt_reaches_each_in_scope_reference():
    assert {
        "references/choosing.md",
        "references/adopting.md",
        "references/writing-library-skills.md",
    } <= _links(_mode("Add or adopt"))
    assert "references/library-skills.md" in _links(_mode("Library skills"))


def test_removed_lifecycle_machinery_stays_removed():
    texts = {"SKILL.md": PARENT, **REFERENCES}
    for name, text in texts.items():
        for removed in (
            "check_resource_status", "validate_resource_record", "validate_skill_catalog",
            ".skill-maintenance", "verified-acquisition", "learnings store", "roblox/resources/records",
        ):
            assert removed not in text, f"{name}: {removed}"


def test_no_codex_host_paths_or_invocation_syntax_remain():
    texts = {"SKILL.md": PARENT, **REFERENCES}
    texts.update({str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in (ROOT / "templates").glob("*")})
    for name, text in texts.items():
        assert ".agents/skills" not in text, name
        assert ".codex" not in text, name
        assert "$roblox-" not in text and "$skill-name" not in text, name
        assert ".roblox-resources" not in text, name
    assert not (ROOT / "agents").exists()


def test_templates_match_the_contract():
    spec = yaml.safe_load((ROOT / "templates/resource-skill-template.yaml").read_text(encoding="utf-8"))
    assert spec["scope"] == "project"
    assert spec["schema_version"] == 2 and spec["parent_contract"]["version"] == 2
    assert "reconciliation" not in spec and "shared_usage" not in spec["guidance"]
    template = (ROOT / "templates/resource-skill-template.md").read_text(encoding="utf-8")
    for heading in ("## Check the pin", "## Core API", "## Gotchas", "## Read further"):
        assert heading in template
    assert "`roblox-resource-acquisition`" in template and "](../" not in template


def test_reference_file_pointers_are_links_not_bare_code_paths():
    bare_reference = re.compile(r"`references/[A-Za-z0-9_.-]+\.md(?:#[A-Za-z0-9_.-]+)?`")
    for name, text in REFERENCES.items():
        assert not bare_reference.search(text), f"{name}: use a Markdown link for internal reference navigation"


def test_eval_case_files_are_well_formed():
    for path in (ROOT / "evals").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        cases = data["cases"] if isinstance(data, dict) else data
        ids = [case["id"] for case in cases]
        assert len(ids) == len(set(ids)), path
        for case in cases:
            if "should_trigger" in case:
                assert isinstance(case["should_trigger"], bool) and case["query"].strip()
                continue
            assert isinstance(case["prompt"], str) and case["prompt"].strip(), path
            for field in ("accept", "reject"):
                assert case[field] and all(isinstance(item, str) and item.strip() for item in case[field]), path
