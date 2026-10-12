"""AGENT_DIR rule and descriptor record resolution."""
import pytest
import yaml

import fixtures
import _resource_contract as contract
import check_resource_status as status


@pytest.mark.parametrize("dirs,expected", [
    ((), ".claude"),
    ((".claude",), ".claude"),
    ((".agents",), ".agents"),
    ((".claude", ".agents"), ".claude"),
    ((".claude", ".agents", ".agents/roblox"), ".agents"),
    ((".claude", ".agents", ".claude/roblox"), ".claude"),
    ((".claude", ".agents", ".claude/roblox", ".agents/roblox"), ".claude"),
])
def test_agent_dir_rule(tmp_path, dirs, expected):
    for name in dirs:
        (tmp_path / name).mkdir(parents=True)
    assert contract.agent_dir(tmp_path) == tmp_path / expected


def test_agent_dir_creates_claude_only_on_request(tmp_path):
    assert not contract.agent_dir(tmp_path).exists()
    assert contract.agent_dir(tmp_path, create=True) == tmp_path / ".claude"
    assert (tmp_path / ".claude").is_dir()


def test_explicit_agent_paths_stay_project_relative(tmp_path):
    (tmp_path / ".claude").mkdir()
    value = ".agents/roblox/resources/records/x.yaml"
    assert contract.resolve_agent_path(tmp_path, value) == tmp_path / value
    assert contract.resolve_agent_path(tmp_path, "roblox/resources/records/x.yaml") == tmp_path / ".claude/roblox/resources/records/x.yaml"


def test_descriptor_paths_must_live_under_roblox_resources(tmp_path):
    child = tmp_path / "roblox-widget-resource"
    child.mkdir()
    (child / "SKILL.md").write_text(fixtures.valid_skill_text(), encoding="utf-8")
    data = fixtures.write_contract(child)
    for value in ("roblox/resources/records/w.yaml", ".agents/roblox/resources/records/w.yaml", ".claude/roblox/resources/records/w.yaml"):
        data["reconciliation"]["record"] = value
        (child / "resource.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
        contract.load_contract(child)
    data["reconciliation"]["record"] = ".roblox-resources/records/w.yaml"
    (child / "resource.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ValueError, match="AGENT_DIR"):
        contract.load_contract(child)


@pytest.mark.parametrize("agent", [".claude", ".agents"])
def test_status_child_mode_finds_the_record_in_either_agent_dir(tmp_path, capsys, agent):
    child = tmp_path / "roblox-widget-resource"
    child.mkdir()
    (child / "SKILL.md").write_text(fixtures.valid_skill_text(), encoding="utf-8")
    fixtures.write_contract(child)
    project = tmp_path / "game"
    record_path = project / agent / "roblox" / "resources" / "records" / "widget-resource.yaml"
    record_path.parent.mkdir(parents=True)
    assert status.main(["--child", str(child), "--project", str(project)]) == 0
    assert "NO-RECORD" in capsys.readouterr().out
    record = fixtures.matching_widget_record()
    record["reconciliation"]["status"] = "matched"
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    assert status.main(["--child", str(child), "--project", str(project)]) == 0
    assert "HEALTHY" in capsys.readouterr().out
    assert status.main(["--child", str(child)]) == 2
    assert "needs --project" in capsys.readouterr().out


def test_user_scope_reads_legacy_store_and_suggests_moving(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setattr(contract.Path, "home", classmethod(lambda cls: tmp_path / "home"))
    legacy = tmp_path / "home" / ".roblox-resources" / "records" / "w.yaml"
    legacy.parent.mkdir(parents=True)
    legacy.write_text("schema_version: 3\n", encoding="utf-8")
    path, note = contract.resolve_user_store_path("~/.claude/roblox/resources/records/w.yaml")
    assert path == legacy and "suggest moving" in note
    current = tmp_path / "home" / ".claude" / "roblox" / "resources" / "records" / "w.yaml"
    current.parent.mkdir(parents=True)
    current.write_text("schema_version: 3\n", encoding="utf-8")
    assert contract.resolve_user_store_path("~/.claude/roblox/resources/records/w.yaml") == (current, "")
