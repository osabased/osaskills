#!/usr/bin/env python3
"""Clone catalog library skills into a project's .claude/skills/, or report their clone state.

The catalog is this skill's libraries/ folder. A clone lands at
PROJECT/.claude/skills/<child>/ and loads as a project skill from the next session on.

Clone states: missing (no folder), foreign (the folder holds a different skill), other-pin
(a clone of another pin), stale (same pin, files differ from the catalog) and current.

A clone is refused when the folder is foreign, when the project's manifest and lock declare a
different version (FAIL), or when replacing an other-pin clone without the project declaring
the catalog pin (PASS). An UNAVAILABLE declaration check still clones and is reported.
A refresh replaces the whole folder, so local edits to a clone are overwritten.

Prints a JSON array. Exit codes: 0 every request done; 1 a child was refused or unknown.
Needs Python 3.11+ and PyYAML, like check_resource_install.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from _common import load_yaml
import check_resource_install

CATALOG = Path(__file__).resolve().parent.parent / "libraries"
IGNORED = ("__pycache__",)


def catalog_children(catalog: Path = CATALOG) -> dict[str, Path]:
    return {path.name: path for path in sorted(catalog.iterdir()) if (path / "resource.yaml").is_file()}


def files(root: Path) -> dict[str, bytes]:
    """Map each file's relative POSIX path to its bytes, with CRLF read as LF so checkouts compare equal."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes().replace(b"\r\n", b"\n")
        for path in sorted(root.rglob("*"))
        if path.is_file() and not set(path.relative_to(root).parts) & set(IGNORED)
    }


def identity(root: Path) -> tuple[str, str] | None:
    """Return the (slug, pin) in root/resource.yaml, or None when it is missing or unreadable."""
    try:
        resource = load_yaml((root / "resource.yaml").read_text(encoding="utf-8-sig"))["resource"]
        return resource["slug"], resource["selector"]["value"]
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        return None


def declared(child: Path, project: Path) -> dict[str, str]:
    """Run the parent's declaration check for child against project, as check_resource_install's CLI reports it."""
    try:
        result = check_resource_install.check(child, project, declared_only=True)
    except PermissionError as exc:
        return {"status": "UNAVAILABLE", "reason": f"manifest read denied: {exc}"}
    except check_resource_install.Unavailable as exc:
        return {"status": "UNAVAILABLE", "reason": str(exc)}
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return {"status": "FAIL", "reason": str(exc)}
    return {"status": result["status"], "reason": result.get("reason", "declared at the catalog pin")}


def clone_state(child: Path, target: Path) -> str:
    if not target.exists():
        return "missing"
    cloned, catalog = identity(target), identity(child)
    if cloned is None or cloned[0] != catalog[0]:
        return "foreign"
    if cloned[1] != catalog[1]:
        return "other-pin"
    return "current" if files(target) == files(child) else "stale"


def target_for(project: Path, name: str) -> Path:
    return project / ".claude" / "skills" / name


def status(project: Path, catalog: Path = CATALOG) -> list[dict]:
    return [
        {"child": name, "pin": identity(child)[1], "declared": declared(child, project), "clone": clone_state(child, target_for(project, name))}
        for name, child in catalog_children(catalog).items()
    ]


def sync(child: Path, target: Path) -> list[str]:
    """Replace target with a copy of child and return the relative paths that changed."""
    before = files(target) if target.exists() else {}
    after = files(child)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(child, target, ignore=shutil.ignore_patterns(*IGNORED))
    return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def clone(name: str, project: Path, catalog: Path = CATALOG) -> dict:
    child = catalog_children(catalog).get(name)
    if child is None:
        return {"child": name, "status": "refused", "reason": f"no catalog child named {name} in {catalog}"}
    target = target_for(project, name)
    state = clone_state(child, target)
    report = {"child": name, "pin": identity(child)[1], "declared": declared(child, project)}
    if state == "current":
        return {**report, "status": "current"}
    if state == "foreign":
        return {**report, "status": "refused", "reason": f"{target} holds a different skill; resolve the collision by hand"}
    if report["declared"]["status"] == "FAIL":
        return {**report, "status": "refused", "reason": "the project declares a different version than the catalog pin; keep the project's pin"}
    if state == "other-pin" and report["declared"]["status"] != "PASS":
        return {**report, "status": "refused", "reason": f"the existing clone targets pin {identity(target)[1]}; replace it only once the project declares {report['pin']}"}
    changed = sync(child, target)
    if state == "missing":
        return {**report, "status": "cloned"}
    return {**report, "status": "refreshed", "changed": changed}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("children", nargs="*", help="catalog child names, such as roblox-vide")
    parser.add_argument("--project", type=Path, required=True, help="project root that holds .claude/skills/")
    parser.add_argument("--status", action="store_true", help="report every catalog child's clone state instead of cloning")
    args = parser.parse_args(argv)
    if args.status == bool(args.children):
        parser.error("give --status or child names, not both")
    if not args.project.is_dir():
        parser.error(f"project directory not found: {args.project}")
    project = args.project.resolve()
    if args.status:
        print(json.dumps(status(project), indent=2))
        return 0
    results = [clone(name, project) for name in dict.fromkeys(args.children)]
    print(json.dumps(results, indent=2))
    return 1 if any(result["status"] == "refused" for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
