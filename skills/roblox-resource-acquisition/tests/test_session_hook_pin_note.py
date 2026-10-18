"""The session hook's local note comparing the project's tool pins with the structure-roblox-projects review."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HEADER = "osaskills tool pins:"


@pytest.fixture(scope="module")
def hook():
    path = ROOT.parent.parent / "hooks" / "freshness.py"
    if not path.exists():
        pytest.skip("not running from the plugin repository")
    spec = importlib.util.spec_from_file_location("freshness_pins", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def reviewed(hook):
    items = json.loads(hook.VERSIONS.read_text(encoding="utf-8"))["items"]
    return {item["id"]: item["reviewed"] for item in items}


def write_tools(project: Path, *entries: str, manifest: str = "rokit.toml") -> Path:
    (project / manifest).write_text("[tools]\n" + "\n".join(entries) + "\n", encoding="utf-8")
    return project


def test_matching_pins_give_no_note(tmp_path, hook, reviewed):
    project = write_tools(tmp_path, f'rojo = "rojo-rbx/rojo@{reviewed["rojo"]}"')
    assert hook.pin_note(project) == ""


def test_a_newer_pin_is_listed(tmp_path, hook, reviewed):
    project = write_tools(tmp_path, 'rojo = "rojo-rbx/rojo@99.0.0"')
    note = hook.pin_note(project)
    assert note.startswith(HEADER)
    assert f"- Rojo: project pins 99.0.0, skill reviewed {reviewed['rojo']} (newer pin)" in note
    assert "Never change the project's pins" in note


def test_an_older_pin_is_listed(tmp_path, hook, reviewed):
    project = write_tools(tmp_path, 'rojo = "rojo-rbx/rojo@0.1.0"')
    assert f"- Rojo: project pins 0.1.0, skill reviewed {reviewed['rojo']} (older pin)" in hook.pin_note(project)


def test_the_repo_match_ignores_case(tmp_path, hook):
    project = write_tools(tmp_path, 'StyLua = "johnnymorganz/STYLUA@0.1.0"', 'selene = "kampfkarren/SELENE@0.1.0"')
    note = hook.pin_note(project)
    assert "- StyLua: project pins 0.1.0" in note and "- Selene: project pins 0.1.0" in note


def test_build_metadata_is_ignored(tmp_path, hook, reviewed):
    project = write_tools(tmp_path, f'pesde = "pesde-pkg/pesde@{reviewed["pesde"]}+registry.0.2.3"')
    assert hook.pin_note(project) == ""
    project = write_tools(tmp_path, 'pesde = "pesde-pkg/pesde@0.1.0+registry.0.2.3"')
    assert "project pins 0.1.0, skill reviewed" in hook.pin_note(project)


def test_an_unknown_tool_is_ignored(tmp_path, hook):
    assert hook.pin_note(write_tools(tmp_path, 'other = "someone/other@1.0.0"')) == ""


def test_an_unparseable_version_counts_as_differing(tmp_path, hook):
    note = hook.pin_note(write_tools(tmp_path, 'rojo = "rojo-rbx/rojo@nightly"'))
    assert "- Rojo: project pins nightly, skill reviewed" in note and "pin)" not in note


def test_no_manifest_gives_no_note(tmp_path, hook):
    assert hook.pin_note(tmp_path) == ""


def test_an_unreadable_manifest_gives_no_note(tmp_path, hook):
    (tmp_path / "rokit.toml").write_text("[tools\n", encoding="utf-8")
    assert hook.pin_note(tmp_path) == ""


def test_an_aftman_manifest_is_read(tmp_path, hook):
    project = write_tools(tmp_path, 'rojo = "rojo-rbx/rojo@99.0.0"', manifest="aftman.toml")
    assert "- Rojo: project pins 99.0.0" in hook.pin_note(project)


def test_rokit_wins_over_aftman_for_the_same_tool(tmp_path, hook, reviewed):
    write_tools(tmp_path, f'rojo = "rojo-rbx/rojo@{reviewed["rojo"]}"')
    write_tools(tmp_path, 'rojo = "rojo-rbx/rojo@99.0.0"', manifest="aftman.toml")
    assert hook.pin_note(tmp_path) == ""
