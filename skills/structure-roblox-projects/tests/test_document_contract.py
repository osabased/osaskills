"""Deterministic checks for the structure skill's routing contract."""
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


def test_frontmatter_is_valid_and_activation_description_is_discriminating():
    data = _frontmatter()
    assert data["name"] == "structure-roblox-projects"
    description = data["description"].lower()
    for material_boundary in ("placement", "source-of-truth", "startup", "migration"):
        assert material_boundary in description
    assert "do not use" in description
    assert "ordinary logic" in description
    assert len(description) <= 360


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


def test_activation_gate_precedes_routing_and_excludes_internal_edits():
    activation = PARENT.index("## Activation gate")
    core_loop = PARENT.index("## Core loop")
    routing = PARENT.index("## Reference routing")
    assert activation < core_loop < routing
    gate = PARENT[activation:core_loop].lower()
    assert "ordinary logic" in gate
    assert "inside already placed modules" in gate
    assert "selects no route" in gate
    assert "apply this gate before routing" in gate


def test_route_table_connects_each_route_to_its_reference():
    table = PARENT.split("## Reference routing", 1)[1].split("## Resolve conventions", 1)[0]
    expected = {
        "Onboarding/setup": "references/workflows/onboarding.md",
        "Ordinary structure": "references/core/practices.md",
        "Write boundary": "references/core/modification-scope.md",
        "Script Sync": "references/workflows/script-sync.md",
        "Rojo": "references/workflows/rojo.md",
        "Migration workflow": "references/workflows/migration.md",
        "Structural-change safeguards": "references/workflows/migration.md",
    }
    for branch, reference in expected.items():
        row = next(line for line in table.splitlines() if f"**{branch}**" in line)
        assert reference in row


def test_route_completion_contracts_are_concrete():
    assert "concrete provisional setup immediately" in PARENT
    assert "Treat supplied paths, instance trees, manifests, mappings, diffs" in PARENT
    assert "For every executable entrypoint" in PARENT
    assert "Produce concrete migration slices rather than phase headings" in PARENT
    topology = PARENT.split("For any topology-sensitive implementation", 1)[1]
    for requirement in (
        "intended write set",
        "tracing of affected requires",
        "recovery boundary",
        "inspection of the resulting diff",
        "focused structural plus runtime validation",
    ):
        assert requirement in topology


def test_development_tooling_detail_lives_in_rojo_reference():
    parent_section = PARENT.split("## Conditional development-tooling setup", 1)[1].split(
        "## Modification scope", 1
    )[0]
    rojo = (ROOT / "references" / "workflows" / "rojo.md").read_text(encoding="utf-8")
    assert "owns the detailed ship/exclude" in parent_section
    assert len(parent_section.splitlines()) <= 6
    assert "## Development and release artifacts" in rojo
    assert "## Observable client previews" in rojo

