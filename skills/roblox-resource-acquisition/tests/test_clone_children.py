"""Cloning catalog library skills into a project's .claude/skills/ and reporting clone state."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from conftest import load_script

ROOT = Path(__file__).resolve().parent.parent
clones = load_script("clone_children")

REGISTRY = "https://github.com/UpliftGames/wally-index"


@pytest.fixture
def catalog(tmp_path):
    root = tmp_path / "catalog"
    root.mkdir()
    shutil.copytree(ROOT / "libraries" / "roblox-lemonsignal", root / "roblox-lemonsignal")
    return root


def make_project(root: Path, version: str | None) -> Path:
    """A pesde project; version None declares no LemonSignal at all."""
    root.mkdir()
    dependency = f'LemonSignal = {{ wally = "data-oriented-house/lemonsignal", version = "={version}" }}\n' if version else ""
    (root / "pesde.toml").write_text(
        'name = "example/game"\nversion = "0.1.0"\n\n[target]\nenvironment = "roblox"\n\n'
        f'[wally_indices]\ndefault = "{REGISTRY}"\n\n[dependencies]\n{dependency}',
        encoding="utf-8")
    graph = (
        f'[graph."wally#data-oriented-house/lemonsignal@{version} roblox"]\n'
        f'direct = ["LemonSignal", {{ wally = "wally#data-oriented-house/lemonsignal", version = "={version}", index = "default" }}, "standard"]\n\n'
        f'[graph."wally#data-oriented-house/lemonsignal@{version} roblox".pkg_ref]\nref_ty = "wally"\nindex_url = "{REGISTRY}"\n'
    ) if version else ""
    (root / "pesde.lock").write_text(
        f'format = 2\nname = "example/game"\nversion = "0.1.0"\ntarget = "roblox"\n\n{graph}', encoding="utf-8")
    return root


def target(project: Path) -> Path:
    return project / ".claude" / "skills" / "roblox-lemonsignal"


def set_pin(skill: Path, pin: str) -> None:
    contract = skill / "resource.yaml"
    contract.write_text(contract.read_text(encoding="utf-8").replace("value: 2.0.0", f"value: {pin}"), encoding="utf-8")


def test_missing_clone_is_cloned_and_then_current(tmp_path, catalog):
    project = make_project(tmp_path / "game", "2.0.0")
    first = clones.clone("roblox-lemonsignal", project, catalog)
    assert first["status"] == "cloned" and first["declared"]["status"] == "PASS"
    assert clones.files(target(project)) == clones.files(catalog / "roblox-lemonsignal")
    assert clones.clone("roblox-lemonsignal", project, catalog)["status"] == "current"


def test_same_pin_with_different_files_is_refreshed_and_reports_changes(tmp_path, catalog):
    project = make_project(tmp_path / "game", "2.0.0")
    clones.clone("roblox-lemonsignal", project, catalog)
    (target(project) / "notes.md").write_text("local edit\n", encoding="utf-8")
    skill = catalog / "roblox-lemonsignal" / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nA catalog fix.\n", encoding="utf-8")
    assert clones.clone_state(catalog / "roblox-lemonsignal", target(project)) == "stale"
    result = clones.clone("roblox-lemonsignal", project, catalog)
    assert result["status"] == "refreshed"
    assert result["changed"] == ["SKILL.md", "notes.md"]
    assert not (target(project) / "notes.md").exists()


def test_line_endings_alone_do_not_make_a_clone_stale(tmp_path, catalog):
    project = make_project(tmp_path / "game", "2.0.0")
    clones.clone("roblox-lemonsignal", project, catalog)
    skill = target(project) / "SKILL.md"
    text = skill.read_bytes()
    flipped = text.replace(b"\r\n", b"\n") if b"\r\n" in text else text.replace(b"\n", b"\r\n")
    assert flipped != text
    skill.write_bytes(flipped)
    assert clones.clone_state(catalog / "roblox-lemonsignal", target(project)) == "current"


def test_foreign_folder_is_refused_and_left_alone(tmp_path, catalog):
    project = make_project(tmp_path / "game", "2.0.0")
    target(project).mkdir(parents=True)
    (target(project) / "SKILL.md").write_text("someone else's skill\n", encoding="utf-8")
    result = clones.clone("roblox-lemonsignal", project, catalog)
    assert result["status"] == "refused" and "different skill" in result["reason"]
    assert (target(project) / "SKILL.md").read_text(encoding="utf-8") == "someone else's skill\n"


def test_project_declaring_another_version_is_refused(tmp_path, catalog):
    project = make_project(tmp_path / "game", "1.9.0")
    result = clones.clone("roblox-lemonsignal", project, catalog)
    assert result["status"] == "refused" and result["declared"]["status"] == "FAIL"
    assert not target(project).exists()


def test_other_pin_clone_is_replaced_once_the_project_declares_the_catalog_pin(tmp_path, catalog):
    project = make_project(tmp_path / "game", "2.0.0")
    shutil.copytree(catalog / "roblox-lemonsignal", target(project))
    set_pin(target(project), "1.9.0")
    assert clones.clone_state(catalog / "roblox-lemonsignal", target(project)) == "other-pin"
    assert clones.clone("roblox-lemonsignal", project, catalog)["status"] == "refreshed"
    assert clones.identity(target(project)) == ("lemonsignal", "2.0.0")


def test_other_pin_clone_stays_when_the_declaration_cannot_be_checked(tmp_path, catalog):
    project = make_project(tmp_path / "game", None)
    shutil.copytree(catalog / "roblox-lemonsignal", target(project))
    set_pin(target(project), "1.9.0")
    result = clones.clone("roblox-lemonsignal", project, catalog)
    assert result["status"] == "refused" and result["declared"]["status"] == "UNAVAILABLE"
    assert clones.identity(target(project)) == ("lemonsignal", "1.9.0")


def test_unchecked_declaration_still_clones_a_missing_child(tmp_path, catalog):
    project = make_project(tmp_path / "game", None)
    result = clones.clone("roblox-lemonsignal", project, catalog)
    assert result["status"] == "cloned" and result["declared"]["status"] == "UNAVAILABLE"


def test_status_reports_each_catalog_child(tmp_path, catalog):
    project = make_project(tmp_path / "game", "2.0.0")
    assert clones.status(project, catalog) == [{
        "child": "roblox-lemonsignal", "pin": "2.0.0",
        "declared": {"status": "PASS", "reason": "pesde.toml and pesde.lock match the pin"}, "clone": "missing"}]


def test_status_compares_an_other_pin_clone_with_the_project(tmp_path, catalog):
    project = make_project(tmp_path / "game", "1.8.0")
    shutil.copytree(catalog / "roblox-lemonsignal", target(project))
    set_pin(target(project), "1.9.0")
    [row] = clones.status(project, catalog)
    assert row["clone"] == "other-pin" and row["clone_pin"] == "1.9.0"
    assert row["declared"]["status"] == "FAIL" and row["clone_declared"]["status"] == "FAIL"
    assert "=1.8.0" in row["clone_declared"]["reason"]


@pytest.fixture
def freshness():
    hook = ROOT.parent.parent / "hooks" / "freshness.py"
    if not hook.exists():
        pytest.skip("not running from the plugin repository")
    spec = importlib.util.spec_from_file_location("freshness", hook)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_session_hook_names_only_clones_the_project_needs(tmp_path, freshness):
    project = make_project(tmp_path / "game", "2.0.0")
    note = freshness.library_note(project)
    assert "- roblox-lemonsignal: the project declares" in note and note.count("\n- ") == 1
    clones.clone("roblox-lemonsignal", project)
    assert freshness.library_note(project) == ""
    (target(project) / "SKILL.md").write_text("edited\n", encoding="utf-8")
    assert "- roblox-lemonsignal: the clone differs" in freshness.library_note(project)


def test_session_hook_names_a_clone_the_project_pins_differently(tmp_path, freshness):
    project = make_project(tmp_path / "game", "1.9.0")
    assert freshness.library_note(project) == ""
    shutil.copytree(ROOT / "libraries" / "roblox-lemonsignal", target(project))
    note = freshness.library_note(project)
    assert "doesn't match the version these skills target" in note and "keep the project's pin" in note
    assert "- roblox-lemonsignal (targets 2.0.0): " in note and "=1.9.0" in note
    set_pin(target(project), "1.8.0")
    assert "- roblox-lemonsignal (targets 1.8.0): " in freshness.library_note(project)


def test_cli_refuses_unknown_children_with_exit_1(tmp_path):
    project = make_project(tmp_path / "game", None)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "clone_children.py"), "--project", str(project), "roblox-nonexistent"],
        capture_output=True, text=True)
    assert proc.returncode == 1, proc.stderr
    assert json.loads(proc.stdout)[0]["status"] == "refused"
    assert not (project / ".claude").exists()


def test_cli_requires_status_or_children(tmp_path):
    project = make_project(tmp_path / "game", None)
    script = str(ROOT / "scripts" / "clone_children.py")
    for extra in ([], ["--status", "roblox-lemonsignal"]):
        proc = subprocess.run([sys.executable, script, "--project", str(project), *extra], capture_output=True, text=True)
        assert proc.returncode == 2 and "not both" in proc.stderr
