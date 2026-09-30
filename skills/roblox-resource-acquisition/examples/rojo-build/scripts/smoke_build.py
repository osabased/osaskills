"""Portable maintained fixture: actual Rojo build, omission and output ownership.

Generates a retained, disposable project under a supplied empty workspace.
The source of this fixture is this script; project-specific artifacts stay outside
the child. This does not exercise engine behavior or independent agent routing.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rojo", type=Path, required=True)
    parser.add_argument("--tool-lock", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    if workspace.exists() and any(workspace.iterdir()):
        parser.error("--workspace must be new or empty; the fixture owns only this chosen directory")
    workspace.mkdir(parents=True, exist_ok=True)
    sources = {
        "shared/Tag.lua": '--!strict\nreturn "rojo-smoke"\n',
        "server/Main.server.lua": '--!strict\nprint("smoke-server")\n',
        "client/Main.client.lua": '--!strict\nprint("smoke-client")\n',
    }
    for relative, content in sources.items():
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    tree = {
        "$className": "DataModel",
        "ReplicatedStorage": {"$className": "ReplicatedStorage", "Shared": {"$path": "shared"}},
        "ServerScriptService": {"$className": "ServerScriptService", "$path": "server"},
        "StarterPlayer": {"$className": "StarterPlayer", "StarterPlayerScripts": {
            "$className": "StarterPlayerScripts", "$path": "client"}},
    }
    project = workspace / "smoke.project.json"
    project.write_text(json.dumps({"name": "RojoSmoke", "emitLegacyScripts": True, "tree": tree}), encoding="utf-8")
    contract = workspace / "expected.json"
    contract.write_text(json.dumps({"scripts": [
        {"path": "ReplicatedStorage/Shared/Tag", "class": "ModuleScript", "sourceFile": "shared/Tag.lua"},
        {"path": "ServerScriptService/Main", "class": "Script", "sourceFile": "server/Main.server.lua"},
        {"path": "StarterPlayer/StarterPlayerScripts/Main", "class": "LocalScript", "sourceFile": "client/Main.client.lua"},
    ]}), encoding="utf-8")
    output = workspace / "place.rbxlx"
    helper = Path(__file__).with_name("check_build.py")
    checks = []
    for label, expected_exit in [("happy", 0), ("omission", 1)]:
        if label == "omission":
            tree["ServerScriptService"].pop("$path")
            project = workspace / "omit.project.json"
            project.write_text(json.dumps({"name": "RojoSmokeOmission", "emitLegacyScripts": True, "tree": tree}), encoding="utf-8")
        argv = [sys.executable, str(helper), "--rojo", str(args.rojo.resolve()),
                "--tool-lock", str(args.tool_lock.resolve()), "--project", str(project),
                "--expected", str(contract), "--output", str(output),
                "--report", str(workspace / f"{label}.json")]
        result = subprocess.run(argv, capture_output=True, text=True)
        observed = json.loads((workspace / f"{label}.json").read_text(encoding="utf-8"))
        checks.append({"label": label, "argv": argv, "expected_exit": expected_exit,
                       "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
                       "gate_report": observed})
        assert result.returncode == expected_exit, f"{label}: {result.stdout}"
        if label == "happy":
            assert len(observed["expected"]) == 3
            good_hash = hashlib.sha256(output.read_bytes()).hexdigest()
        else:
            assert "ServerScriptService/Main" in observed["error"]
            assert hashlib.sha256(output.read_bytes()).hexdigest() == good_hash
    assert not list(workspace.glob(".rojo-build-*"))
    report = {"status": "passed", "target": "rojo-rbx/rojo 7.7.0",
              "checks": checks, "last_good_output_preserved": True, "temporary_builds_cleaned": True}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS: actual 7.7.0 build; three script classes; omission failed; output retained; temporary builds cleaned")


if __name__ == "__main__":
    main()
