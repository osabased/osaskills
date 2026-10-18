"""Offline checks for check_updates.py and the versions.json manifests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from conftest import load_script

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT.parent
STRUCTURE = SKILLS / "structure-roblox-projects"
updates = load_script("check_updates")


def manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("text, expected", [
    ("v7.7.1", ((7, 7, 1), False)),
    ("0.32.0", ((0, 32, 0), False)),
    ("1.2", ((1, 2, 0), False)),
    ("v0.7.4+registry.0.2.3", ((0, 7, 4), False)),
    ("0.11.0-rc.6", ((0, 11, 0), True)),
    ("@quenty/blend@12.50.2", ((12, 50, 2), False)),
    ("nightly", None),
])
def test_parse_version(text, expected):
    assert updates.parse_version(text) == expected


def test_newest_prefers_highest_stable_version_not_newest_date():
    tags = [("v2.0.0-beta.1", "b"), ("v1.10.0", "a"), ("v1.9.9", "c"), ("junk", "d")]
    assert updates.newest(tags, allow_prerelease=False) == ("v1.10.0", "a")
    assert updates.newest(tags, allow_prerelease=True) == ("v2.0.0-beta.1", "b")


def write_manifest(tmp_path: Path, items: list[dict]) -> Path:
    path = tmp_path / "versions.json"
    path.write_text(json.dumps({"schema": 1, "items": items}), encoding="utf-8")
    return path


def test_statuses_exit_codes_and_cache(tmp_path, monkeypatch, capsys):
    calls = []

    def fake_lookup(source, allow_prerelease):
        calls.append(source)
        if source.get("github") == "broken/repo":
            raise LookupError("no versioned releases")
        return {"old/tool": ("v1.3.0", "u1"), "new/tool": ("1.0.0", "u2")}[source["github"]]

    monkeypatch.setattr(updates, "lookup", fake_lookup)
    path = write_manifest(tmp_path, [
        {"id": "old", "name": "Old", "source": {"github": "old/tool"}, "reviewed": "1.2.9"},
        {"id": "new", "name": "New", "source": {"github": "new/tool"}, "reviewed": "1.0.0"},
        {"id": "broken", "name": "Broken", "source": {"github": "broken/repo"}, "reviewed": "1.0.0"},
    ])
    cache = tmp_path / "cache.json"
    assert updates.main([str(path), "--cache", str(cache)]) == 1
    out = capsys.readouterr().out
    assert "OUTDATED old: reviewed 1.2.9, latest 1.3.0 (u1)" in out
    assert "current  new 1.0.0" in out and "UNKNOWN  broken" in out
    assert len(calls) == 3
    # Cached lookups are reused; the failed one is retried.
    assert updates.main([str(path), "--cache", str(cache)]) == 1
    assert len(calls) == 4


def test_all_unknown_is_exit_2_and_all_current_is_exit_0(tmp_path, monkeypatch):
    monkeypatch.setattr(updates, "lookup", lambda source, allow: (_ for _ in ()).throw(OSError("offline")))
    path = write_manifest(tmp_path, [{"id": "a", "name": "A", "source": {"npm": "a"}, "reviewed": "1.0.0"}])
    assert updates.main([str(path), "--no-cache"]) == 2
    monkeypatch.setattr(updates, "lookup", lambda source, allow: ("1.0.0", "u"))
    assert updates.main([str(path), "--no-cache"]) == 0


def test_unsupported_schema_is_rejected(tmp_path):
    path = tmp_path / "versions.json"
    path.write_text(json.dumps({"schema": 2, "items": []}), encoding="utf-8")
    with pytest.raises(ValueError):
        updates.check([path], None, 24)


@pytest.mark.parametrize("skill", [ROOT, STRUCTURE], ids=lambda p: p.name)
def test_manifests_are_well_formed(skill):
    if not (skill / "versions.json").exists():
        pytest.skip("sibling skill not present")
    data = manifest(skill / "versions.json")
    assert data["schema"] == 1
    ids = [item["id"] for item in data["items"]]
    assert ids and len(ids) == len(set(ids))
    for item in data["items"]:
        assert set(item["source"]) & {"github", "npm", "wally"}, item["id"]
        assert updates.parse_version(item["reviewed"]) is not None, item["id"]
        assert item["files"], item["id"]
        for relative in item["files"]:
            assert (skill / relative).exists(), f"{item['id']}: {relative}"


def test_bundled_children_match_their_descriptors():
    tracked: dict[str, list[dict]] = {}
    for item in manifest(ROOT / "versions.json")["items"]:
        tracked.setdefault(item["files"][0], []).append(item)
    children = sorted(path.parent for path in (ROOT / "libraries").glob("roblox-*/resource.yaml"))
    assert children, "bundled children not found"
    for child in children:
        key = f"libraries/{child.name}/"
        assert key in tracked, f"{child.name} is not tracked in versions.json"
        resource = yaml.safe_load((child / "resource.yaml").read_text(encoding="utf-8"))["resource"]
        # The primary package is the one the descriptor names; companions are checked below.
        item = next((i for i in tracked[key] if resource["package_id"] in i["source"].values()), tracked[key][0])
        assert item["reviewed_on"] == str(resource["source_review_date"]), child.name
        if resource["selector"]["kind"] == "version":
            assert item["reviewed"] == resource["selector"]["value"], child.name
    companions = yaml.safe_load((ROOT / "libraries" / "roblox-nevermore-ui" / "resource.yaml").read_text(encoding="utf-8"))
    pins = {c["package_id"]: c["version"] for c in companions["installation"]["companions"]}
    npm = {item["source"]["npm"]: item["reviewed"] for item in manifest(ROOT / "versions.json")["items"] if "npm" in item["source"]}
    for package, version in pins.items():
        assert npm.get(package) == version, package


def test_structure_copy_of_the_checker_is_identical():
    copy = STRUCTURE / "scripts" / "check_updates.py"
    if not copy.exists():
        pytest.skip("sibling skill not present")
    assert copy.read_bytes() == (ROOT / "scripts" / "check_updates.py").read_bytes()


def test_plugin_session_hook_is_registered_and_never_fails():
    repo = SKILLS.parent
    hooks = repo / "hooks" / "hooks.json"
    if not hooks.exists():
        pytest.skip("not running from the plugin repository")
    spec = json.loads(hooks.read_text(encoding="utf-8"))["hooks"]["SessionStart"][0]
    command = spec["hooks"][0]["command"]
    assert "${CLAUDE_PLUGIN_ROOT}/hooks/freshness.py" in command and command.rstrip().endswith("|| true")
    text = (repo / "hooks" / "freshness.py").read_text(encoding="utf-8")
    assert "structure-roblox-projects" in text


def test_plugin_version_follows_commits():
    plugin = SKILLS.parent / ".claude-plugin" / "plugin.json"
    if not plugin.exists():
        pytest.skip("not running from the plugin repository")
    # A pinned version would hold installed copies on old skill content until someone bumps it.
    data = json.loads(plugin.read_text(encoding="utf-8"))
    assert "version" not in data
    # Library skills are cloned into each project that uses them, never loaded for every project.
    assert "skills" not in data
