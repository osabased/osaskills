"""Execute the worked authoring artifacts through the real structural gates."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import yaml

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def load_helper(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("folder", ["goodsignal", "rojo-build"])
def test_worked_child_bundle(tmp_path, bundle_mod, folder):
    source = EXAMPLES / folder
    record_path = source / "resource-record.example.yaml"
    record = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    candidate = tmp_path / record["generated_skill"]
    shutil.copytree(source, candidate)
    (candidate / "SKILL.md").write_bytes((source / "SKILL.example.md").read_bytes())
    (candidate / "resource.yaml").write_bytes((source / "resource.example.yaml").read_bytes())
    skill = candidate / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8").replace("resource.example.yaml", "resource.yaml"), encoding="utf-8")
    errors, _ = bundle_mod.validate_bundle(record_path, record, candidate)
    assert errors == []
    # These examples do not import behavioral claims from structural evidence.
    assert record["verification"]["status"] == "unverified"
    assert record["skill_validation"]["checks"] == []
    assert record["host_adoptions"] == []


def test_tool_fixture_contract_and_failure_ownership(tmp_path, monkeypatch):
    """A controlled CLI double tests the wrapper, not upstream Rojo behavior."""
    scripts = EXAMPLES / "rojo-build" / "scripts"
    smoke = load_helper(scripts / "smoke_build.py", "example_smoke")
    helper = load_helper(scripts / "check_build.py", "example_build")
    executable = tmp_path / "controlled-rojo"
    executable.write_bytes(b"test-only CLI double")
    lock = tmp_path / "tool-lock.json"
    lock.write_text(json.dumps({
        "canonical_url": "https://github.com/rojo-rbx/rojo",
        "package_id": "rojo-rbx/rojo", "version": "7.7.0",
        "sha256": helper.sha256(executable),
    }), encoding="utf-8")
    generated = tmp_path / "generated"
    report = tmp_path / "result.json"

    def controlled_command(argv, **_kwargs):
        if Path(argv[0]) == executable:
            if argv[1] == "--version":
                return subprocess.CompletedProcess(argv, 0, "Rojo 7.7.0", "")
            project = Path(argv[2])
            config = json.loads(project.read_text(encoding="utf-8"))
            tree = ET.Element("roblox")

            def item(parent, name, cls, source=None):
                node = ET.SubElement(parent, "Item", {"class": cls})
                props = ET.SubElement(node, "Properties")
                ET.SubElement(props, "string", {"name": "Name"}).text = name
                if source is not None:
                    ET.SubElement(props, "ProtectedString", {"name": "Source"}).text = source
                return node

            shared = item(item(tree, "ReplicatedStorage", "ReplicatedStorage"), "Shared", "Folder")
            item(shared, "Tag", "ModuleScript", (project.parent / "shared/Tag.lua").read_text())
            server = item(tree, "ServerScriptService", "ServerScriptService")
            if "$path" in config["tree"]["ServerScriptService"]:
                item(server, "Main", "Script", (project.parent / "server/Main.server.lua").read_text())
            client = item(item(tree, "StarterPlayer", "StarterPlayer"), "StarterPlayerScripts", "StarterPlayerScripts")
            item(client, "Main", "LocalScript", (project.parent / "client/Main.client.lua").read_text())
            ET.ElementTree(tree).write(argv[-1], encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "Build complete", "")
        assert Path(argv[1]).name == "check_build.py"
        with monkeypatch.context() as context:
            context.setattr(sys, "argv", argv[1:])
            exit_code = helper.main()
        return subprocess.CompletedProcess(argv, exit_code, "controlled wrapper run", "")

    monkeypatch.setattr(subprocess, "run", controlled_command)
    monkeypatch.setattr(sys, "argv", ["smoke_build.py", "--rojo", str(executable),
        "--tool-lock", str(lock), "--workspace", str(generated), "--report", str(report)])
    smoke.main()
    result = json.loads(report.read_text(encoding="utf-8"))
    assert [check["exit"] for check in result["checks"]] == [0, 1]
    assert result["last_good_output_preserved"] is True
    assert result["temporary_builds_cleaned"] is True
    # An otherwise valid changed build cannot publish if its report cannot be
    # written. The former ordering replaced the last good output then raised.
    previous = (generated / "place.rbxlx").read_bytes()
    (generated / "shared/Tag.lua").write_text("return 'report-error-control'\n")
    blocked = tmp_path / "report-parent-is-file"
    blocked.write_text("blocked")
    arguments = list(result["checks"][0]["argv"][1:])
    arguments[arguments.index("--report") + 1] = str(blocked / "report.json")
    monkeypatch.setattr(sys, "argv", arguments)
    assert helper.main() == 1
    assert (generated / "place.rbxlx").read_bytes() == previous
    assert not list(generated.glob(".rojo-*"))
    # A changed executable must fail before building and preserve the last good output.
    previous = (generated / "place.rbxlx").read_bytes()
    executable.write_bytes(b"unexpected executable replacement")
    monkeypatch.setattr(sys, "argv", result["checks"][0]["argv"][1:])
    assert helper.main() == 1
    assert (generated / "place.rbxlx").read_bytes() == previous
