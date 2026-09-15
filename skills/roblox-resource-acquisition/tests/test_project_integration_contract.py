"""Regression checks for project-level Roblox agent state and cross-skill ownership."""
from pathlib import Path

RESOURCE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = RESOURCE_ROOT.parent
STRUCTURE_ROOT = SKILLS_ROOT / "structure-roblox-projects"


def _markdown_texts(root: Path):
    seen: set[Path] = set()
    for path in (root / "SKILL.md", *root.rglob("*.md")):
        if path.is_file() and path not in seen:
            seen.add(path)
            yield path, path.read_text(encoding="utf-8")


def test_structure_profile_has_one_canonical_agents_location():
    for path, text in _markdown_texts(STRUCTURE_ROOT):
        assert ".codex/roblox-structure.md" not in text, path
    profile = (
        STRUCTURE_ROOT / "references" / "conventions" / "project-profile.md"
    ).read_text(encoding="utf-8")
    assert ".agents/roblox/structure.md" in profile
    assert "Structural dependencies" in profile


def test_canonical_ssa_owns_module_loader_target_end_to_end():
    ssa = (STRUCTURE_ROOT / "references" / "ssa" / "ssa-bootstrap.md").read_text(
        encoding="utf-8"
    )
    preferences = (
        STRUCTURE_ROOT / "references" / "conventions" / "preference-resolution.md"
    ).read_text(encoding="utf-8")
    assert "ActualFire-Games/module-loader" in ssa
    assert "3.0.4" in ssa
    assert "b427a3e03fe9368a26e344b5e37f7466fe2ca878" in ssa
    assert "structure-roblox-projects` owns this dependency" in ssa
    assert "must not select a substitute, advance the pin" in ssa
    assert "Structural dependencies" in preferences


def test_resource_project_state_uses_agents_namespace_and_schema_v3():
    state = (RESOURCE_ROOT / "references" / "state-policy.md").read_text(
        encoding="utf-8"
    )
    adoption = (RESOURCE_ROOT / "references" / "project-adoption.md").read_text(
        encoding="utf-8"
    )
    template = (RESOURCE_ROOT / "templates" / "resource-record.yaml").read_text(
        encoding="utf-8"
    )
    assert "<project-root>/.agents/roblox/resources/records/<slug>.yaml" in state
    assert "<project-root>/.roblox-resources/records/<slug>.yaml" not in state
    assert "schema-version 3" in state
    assert "schema_version: 3" in template
    assert "project_use:" in template
    assert "<!-- roblox-resource-acquisition:onboarding:start -->" in adoption
    assert "<project-root>/.agents/roblox/resources/artifacts/skills/<skill-name>/" in adoption
    assert "<skill-scope-root>/.agents/skills/<skill-name>/" in adoption


def test_agent_facing_resource_docs_have_no_stale_v2_record_contract():
    for path, text in _markdown_texts(RESOURCE_ROOT):
        assert "schema-version 2" not in text, path
        assert "<project-root>/.roblox-resources/records/<slug>.yaml" not in text, path


def test_generated_child_contract_uses_current_record_schema():
    contract = (RESOURCE_ROOT / "references" / "resource-skill-contract.md").read_text(
        encoding="utf-8"
    )
    template = (RESOURCE_ROOT / "templates" / "resource-skill-template.md").read_text(
        encoding="utf-8"
    )
    operational = (RESOURCE_ROOT / "references" / "operational-lifecycle.md").read_text(
        encoding="utf-8"
    )
    for path, text in (
        ("resource-skill-contract.md", contract),
        ("resource-skill-template.md", template),
        ("operational-lifecycle.md", operational),
    ):
        assert "schema-version 3" in text, path


def test_external_project_authority_is_preserved_not_reselected():
    parent = (RESOURCE_ROOT / "SKILL.md").read_text(encoding="utf-8")
    adoption = (RESOURCE_ROOT / "references" / "project-adoption.md").read_text(
        encoding="utf-8"
    )
    assert "project-use authority" in parent
    assert "must not substitute, retarget, upgrade, or retire it independently" in adoption
    assert "structure-roblox-projects" in adoption
