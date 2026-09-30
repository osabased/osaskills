"""Build a Rojo place and fail if the project's expected script contract is absent.

Uses the actual pinned executable. Owns only a temporary build, the requested
successful output, and its explicit JSON report. Never starts Studio or a server.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(args: list[str], report: dict) -> subprocess.CompletedProcess:
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    report["commands"].append({
        "argv": args, "exit": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
    })
    if result.returncode:
        raise ValueError(f"command exited {result.returncode}: {args[1]}")
    return result


def aliases(first: Path, second: Path) -> bool:
    return first == second or (first.exists() and second.exists() and first.samefile(second))


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rojo-report-", dir=path.parent) as temp_dir:
        candidate = Path(temp_dir) / "report.json"
        candidate.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        os.replace(candidate, path)


def index_items(root: ET.Element) -> dict[str, list[dict]]:
    items: dict[str, list[dict]] = {}

    def walk(item: ET.Element, parent: str) -> None:
        properties = {p.get("name"): p.text or "" for p in item.findall("./Properties/*")}
        name = properties.get("Name", "")
        if not name or "/" in name:
            raise ValueError("item has an absent or slash-containing Name")
        path = f"{parent}/{name}" if parent else name
        items.setdefault(path, []).append({
            "class": item.get("class"), "source": properties.get("Source", ""),
        })
        for child in item.findall("./Item"):
            walk(child, path)

    for item in root.findall("./Item"):
        walk(item, "")
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rojo", type=Path, required=True)
    parser.add_argument("--tool-lock", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = {"status": "failed", "commands": [], "expected": [], "error": ""}
    output = args.output.resolve()
    report_path = args.report.resolve()
    prepared = None
    safe_report = True
    try:
        rojo = args.rojo.resolve(strict=True)
        project = args.project.resolve(strict=True)
        inputs = [rojo, project, args.tool_lock.resolve(strict=True), args.expected.resolve(strict=True)]
        if aliases(output, report_path) or any(aliases(report_path, path) for path in inputs):
            safe_report = False
            raise ValueError("report must be distinct from output and every input")
        if any(aliases(output, path) for path in inputs):
            raise ValueError("output must be distinct from every input")
        if output.suffix != ".rbxlx":
            raise ValueError("this content verifier requires an XML place output ending .rbxlx")
        if report_path.suffix != ".json" or report_path.is_dir():
            raise ValueError("report must name a writable .json file")
        lock = json.loads(args.tool_lock.read_text(encoding="utf-8-sig"))
        if (lock["canonical_url"] != "https://github.com/rojo-rbx/rojo"
                or lock["package_id"] != "rojo-rbx/rojo"
                or lock["version"] != "7.7.0"):
            raise ValueError("tool lock does not identify reviewed rojo-rbx/rojo 7.7.0")
        actual_hash = sha256(rojo)
        if actual_hash != lock["sha256"]:
            raise ValueError("executable SHA256 differs from the project tool lock")
        version = run_command([str(rojo), "--version"], report).stdout.strip()
        if version != f"Rojo {lock['version']}":
            raise ValueError(f"version mismatch: expected Rojo {lock['version']}, observed {version}")
        report["target"] = {**lock, "observed_version": version, "executable": str(rojo)}
        expected = json.loads(args.expected.read_text(encoding="utf-8-sig"))["scripts"]
        names = [entry["path"] for entry in expected]
        if not names or len(names) != len(set(names)):
            raise ValueError("expected script contract must be nonempty and have unique paths")
        for entry in expected:
            if entry["class"] not in {"Script", "LocalScript", "ModuleScript"}:
                raise ValueError(f"unsupported expected script class: {entry['class']}")
            source = (project.parent / entry["sourceFile"]).resolve(strict=True)
            if aliases(report_path, source):
                safe_report = False
                raise ValueError("report must be distinct from every source input")
            if aliases(output, source):
                raise ValueError("output must be distinct from every source input")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".rojo-build-", dir=output.parent) as temp_dir:
            candidate = Path(temp_dir) / "place.rbxlx"
            run_command([str(rojo), "build", str(project), "--output", str(candidate)], report)
            built = index_items(ET.parse(candidate).getroot())
            for entry in expected:
                matches = built.get(entry["path"], [])
                if len(matches) != 1:
                    raise ValueError(f"expected exactly one {entry['path']}; observed {len(matches)}")
                item = matches[0]
                if item["class"] != entry["class"]:
                    raise ValueError(f"wrong class for {entry['path']}: {item['class']}")
                if not item["source"].strip():
                    raise ValueError(f"empty Source for {entry['path']}")
                source = project.parent / entry["sourceFile"]
                source_text = source.read_text(encoding="utf-8-sig")
                if item["source"].replace("\r\n", "\n") != source_text.replace("\r\n", "\n"):
                    raise ValueError(f"source mismatch for {entry['path']}")
                report["expected"].append({"path": entry["path"], "class": item["class"], "source_matches": True})
            descriptor, ready_name = tempfile.mkstemp(prefix=".rojo-ready-", suffix=".rbxlx", dir=output.parent)
            os.close(descriptor)
            prepared = Path(ready_name)
            os.replace(candidate, prepared)
            report["output_sha256"] = sha256(prepared)
        report["status"] = "passed"
        report["output"] = str(output)
        # Report preparation and build-directory cleanup finish before the last
        # fallible publication operation, preserving last-good output on errors.
        write_report(report_path, report)
        os.replace(prepared, output)
        prepared = None
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError, subprocess.TimeoutExpired) as error:
        report["status"] = "failed"
        report["error"] = str(error)
    finally:
        if prepared is not None:
            try:
                prepared.unlink(missing_ok=True)
            except OSError as error:
                report["error"] += f"; cleanup failed for {prepared}: {error}"
    if report["status"] == "failed" and safe_report:
        try:
            write_report(report_path, report)
        except OSError as error:
            report["error"] += f"; report unavailable: {error}"
    print(f"{report['status'].upper()}: {len(report['expected'])} expected scripts; {report['error'] or report.get('output', '')}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
