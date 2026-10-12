"""Regression tests for Agent Skills frontmatter and child entrypoint invariants."""
import fixtures


def test_skill_directory_must_match_frontmatter_name(skill_mod, tmp_path):
    child = tmp_path / "wrong-directory"
    child.mkdir()
    (child / "SKILL.md").write_text(fixtures.valid_skill_text(), encoding="utf-8")
    fixtures.write_contract(child)
    errors, _warnings = skill_mod.validate_skill(child)
    assert "frontmatter name must match the generated skill directory name" in errors


def test_skill_description_has_agent_skills_length_limit(skill_mod, tmp_path):
    child = tmp_path / "roblox-widget-resource"
    child.mkdir()
    description = "Use Widget Resource when " + ("replicated lifecycle coordination " * 80)
    assert len(description) > 1024
    (child / "SKILL.md").write_text(
        fixtures.valid_skill_text(description=description), encoding="utf-8"
    )
    fixtures.write_contract(child)
    errors, _warnings = skill_mod.validate_skill(child)
    assert "frontmatter description must be at most 1024 characters" in errors


def test_skill_name_has_agent_skills_length_limit(skill_mod, tmp_path):
    name = "roblox-" + ("a" * 60)
    assert len(name) > 64
    child = tmp_path / name
    child.mkdir()
    (child / "SKILL.md").write_text(fixtures.valid_skill_text(name=name), encoding="utf-8")
    fixtures.write_contract(child)
    errors, _warnings = skill_mod.validate_skill(child)
    assert "frontmatter name must be at most 64 characters" in errors


def test_optional_frontmatter_types_and_compatibility_limit(skill_mod, tmp_path):
    child = tmp_path / "roblox-widget-resource"
    child.mkdir()
    text = fixtures.valid_skill_text().replace(
        "description: Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.\n",
        "description: Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.\n"
        "compatibility: " + ("x" * 501) + "\n"
        "license: 123\n"
        "allowed-tools: 456\n"
        "disable-model-invocation: maybe\n",
    )
    (child / "SKILL.md").write_text(text, encoding="utf-8")
    fixtures.write_contract(child)
    errors, _warnings = skill_mod.validate_skill(child)
    assert "frontmatter compatibility must be 1 to 500 characters" in errors
    assert "frontmatter license must be a string" in errors
    assert "frontmatter allowed-tools must be a string or list" in errors
    assert "frontmatter disable-model-invocation must be true or false" in errors


def test_claude_code_frontmatter_is_accepted_and_unknown_keys_only_warn(skill_mod, tmp_path):
    child = tmp_path / "roblox-widget-resource"
    child.mkdir()
    text = fixtures.valid_skill_text().replace(
        "description: Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.\n",
        "description: Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.\n"
        "disable-model-invocation: false\n"
        "user-invocable: true\n"
        "argument-hint: '[task]'\n"
        "model: inherit\n"
        "allowed-tools:\n  - Read\n  - Bash\n"
        "future-field: x\n",
    )
    (child / "SKILL.md").write_text(text, encoding="utf-8")
    fixtures.write_contract(child)
    errors, warnings = skill_mod.validate_skill(child)
    assert errors == []
    assert any("future-field" in warning for warning in warnings)


def test_lean_template_headings_are_required(skill_mod, tmp_path):
    child = tmp_path / "roblox-widget-resource"
    child.mkdir()
    (child / "SKILL.md").write_text(fixtures.valid_skill_text().replace("## Gotchas", "## Notes"), encoding="utf-8")
    fixtures.write_contract(child)
    errors, _warnings = skill_mod.validate_skill(child)
    assert "entrypoint is missing the required heading '## Gotchas'" in errors


def test_valid_metadata_mapping_is_supported(skill_mod, tmp_path):
    child = tmp_path / "roblox-widget-resource"
    child.mkdir()
    text = fixtures.valid_skill_text().replace(
        "description: Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.\n",
        "description: Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.\n"
        "metadata:\n"
        "  resource-slug: widget-resource\n"
        "  lifecycle: generated\n",
    )
    (child / "SKILL.md").write_text(text, encoding="utf-8")
    fixtures.write_contract(child)
    errors, _warnings = skill_mod.validate_skill(child)
    assert errors == []


def test_metadata_requires_string_keys_and_values(skill_mod, tmp_path):
    child = tmp_path / "roblox-widget-resource"
    child.mkdir()
    text = fixtures.valid_skill_text().replace(
        "description: Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.\n",
        "description: Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.\n"
        "metadata:\n"
        "  resource-slug: 123\n",
    )
    (child / "SKILL.md").write_text(text, encoding="utf-8")
    fixtures.write_contract(child)
    errors, _warnings = skill_mod.validate_skill(child)
    assert "frontmatter metadata keys and values must be strings" in errors
