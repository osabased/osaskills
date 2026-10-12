#!/usr/bin/env python3
"""Read-only current block query for generated Roblox resource skills.

The command intentionally reads the static child resource contract and only the matching
record's schema, identity, version, block, reconciliation, verification, and
matching-host status fields. It never executes evidence commands or performs
full lifecycle reconciliation.

Statuses: HEALTHY and NO-RECORD (no project record; advisory use) exit 0;
BLOCKED and MISMATCH (an observed block or identity/version mismatch: stop) exit 1;
UNKNOWN (the record could not be read or is incomplete: continue in advisory mode
and report it) exits 2.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_resource_bundle import (
    _child_provenance,
    _concrete_url,
    _same_url,
)
from validate_resource_record import load_record, nonempty_string
from guard_skill_update import marker_path
from _resource_contract import load_contract, resolve_agent_path, resolve_user_store_path

RECONCILIATION_STATES = {"matched", "mismatched", "blocked", "unknown", "not-applicable"}
VERIFICATION_STATES = {"unverified", "unavailable", "verified", "failed"}
HOST_STATES = {"installed", "operational", "blocked", "disabled", "removed", "unavailable", "failed"}


RECORD_DIRS = ([".claude", "roblox", "resources", "records"], [".agents", "roblox", "resources", "records"])


def _host_adoption_match(adoption: dict[str, Any], child_name: str, skill_root: Path, record_path: Path) -> str | None:
    """Return "exact" when the entry's location is this child, "name" when only the skill name matches."""
    location = adoption.get("location")
    if not isinstance(location, str) or not location.strip():
        return None
    location_path = Path(location)
    candidates = [location_path]
    record_parts = [part.lower() for part in record_path.parent.parts]
    for record_dir in RECORD_DIRS:
        if record_parts[-len(record_dir):] == record_dir and len(record_path.parents) > len(record_dir):
            candidates.append(record_path.parents[len(record_dir)] / location_path)
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved == skill_root or resolved == skill_root / "SKILL.md":
            return "exact"
    normalized = location.replace("\\", "/").rstrip("/").lower()
    if normalized.endswith(f"/{child_name.lower()}") or normalized.endswith(f"/{child_name.lower()}/skill.md"):
        return "name"
    return None


def _host_adoption_matches_child(adoption: dict[str, Any], child_name: str, skill_root: Path, record_path: Path) -> bool:
    return _host_adoption_match(adoption, child_name, skill_root, record_path) is not None


def query_pair(skill_root: Path, record_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "skill": str(skill_root),
        "record": str(record_path),
        "status": "unknown",
        "reason": "",
    }
    try:
        guards = [marker_path(skill_root.resolve()), marker_path(Path(__file__).resolve().parent.parent)]
        if any(guard.exists() or guard.is_symlink() for guard in guards):
            result["status"] = "blocked"
            result["reason"] = "skill promotion is pending or interrupted; reconcile its maintenance transaction"
            return result
        if not (skill_root / "SKILL.md").is_file():
            raise ValueError("generated skill directory does not contain SKILL.md")
        if not record_path.exists():
            result["status"] = "no-record"
            result["reason"] = "no project record; use the child as advice and report that record checks were skipped"
            return result
        if not record_path.is_file() or record_path.suffix.lower() not in {".yaml", ".yml"}:
            raise ValueError("resource record is not a YAML file")
        metadata, child = _child_provenance(skill_root)
        record = load_record(record_path)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        result["reason"] = str(exc)
        return result

    if type(record.get("schema_version")) is not int or record.get("schema_version") != 3:
        result["reason"] = "record schema_version is not 3"
        return result

    child_name = metadata.get("name")
    if not isinstance(child_name, str) or not child_name.strip():
        result["reason"] = "child frontmatter name is missing"
        return result
    if not isinstance(record.get("generated_skill"), str) or record.get("generated_skill") != child_name.strip():
        result["reason"] = "record generated_skill does not match child name (update the record after a rename)"
        return result

    child_slug = child.get("slug")
    if not child_slug or not isinstance(record.get("slug"), str) or record.get("slug") != child_slug.strip():
        result["status"] = "mismatch"
        result["reason"] = "record slug does not match child resource contract"
        return result

    child_canonical = _concrete_url(child.get("canonical_url")) or _concrete_url(child.get("devforum_url"))
    record_canonical = record.get("canonical_url")
    if not child_canonical or not nonempty_string(record_canonical):
        result["reason"] = "canonical identity is missing"
        return result
    if not _same_url(record_canonical.strip(), child_canonical):
        result["status"] = "mismatch"
        result["reason"] = "record canonical identity does not match child resource contract"
        return result

    child_package = child.get("package_id")
    record_package = record.get("package_id")
    if child_package is None:
        if nonempty_string(record_package):
            result["status"] = "mismatch"
            result["reason"] = "record package identity conflicts with child resource contract"
            return result
    elif not child_package or not nonempty_string(record_package) or record_package.strip() != child_package.strip():
        result["status"] = "mismatch"
        result["reason"] = "record package identity does not match child resource contract"
        return result

    verification = record.get("verification")
    verification_status = verification.get("status") if isinstance(verification, dict) else None
    if not isinstance(verification_status, str) or verification_status not in VERIFICATION_STATES:
        result["reason"] = "verification state is missing or malformed"
        return result
    record_version = verification.get("version_or_commit") if isinstance(verification, dict) else None
    child_version = child.get("version")
    if not child_version or not nonempty_string(record_version) or record_version.strip() != child_version.strip():
        result["status"] = "mismatch"
        result["reason"] = "record version/state does not match child resource contract"
        return result

    reconciliation = record.get("reconciliation")
    reconciliation_status = reconciliation.get("status") if isinstance(reconciliation, dict) else None
    if not isinstance(reconciliation_status, str) or reconciliation_status not in RECONCILIATION_STATES:
        result["reason"] = "reconciliation state is missing or malformed"
        return result
    block = record.get("blocked_use_or_version")
    if not isinstance(block, str):
        result["reason"] = "blocked_use_or_version must be a string"
        return result
    if nonempty_string(block) or reconciliation_status == "blocked":
        result["status"] = "blocked"
        result["reason"] = block.strip() if nonempty_string(block) else "matching record is blocked"
        return result

    host_adoptions = record.get("host_adoptions")
    if not isinstance(host_adoptions, list):
        result["reason"] = "host_adoptions must be a list"
        return result
    for index, adoption in enumerate(host_adoptions):
        if not isinstance(adoption, dict):
            result["reason"] = f"host_adoptions[{index}] is malformed"
            return result
        location = adoption.get("location")
        if not isinstance(location, str) or not location.strip():
            result["reason"] = f"host_adoptions[{index}].location is missing or malformed"
            return result
        host_status = adoption.get("status")
        if not isinstance(host_status, str) or host_status not in HOST_STATES:
            result["reason"] = f"host_adoptions[{index}].status is malformed"
            return result
        match = _host_adoption_match(adoption, child_name.strip(), skill_root, record_path)
        host = adoption.get("host") if isinstance(adoption.get("host"), str) else "unknown host"
        # A content block follows the skill to every host copy; host-local states apply only to that copy.
        if host_status == "blocked" and match is not None:
            result["status"] = "blocked"
            adoption_result = adoption.get("result")
            detail = adoption_result.strip() if isinstance(adoption_result, str) and adoption_result.strip() else "no reason recorded"
            result["reason"] = f"host adoption for {host} at {location.strip()} is blocked: {detail}"
            return result
        if host_status in {"disabled", "removed", "failed", "unavailable"} and match == "exact":
            result["reason"] = f"host adoption for {host} at {location.strip()} is {host_status}"
            return result

    if reconciliation_status == "mismatched":
        result["status"] = "mismatch"
        result["reason"] = "matching record reports mismatched installed state"
        return result
    if reconciliation_status == "unknown":
        result["reason"] = "matching record reports unknown reconciliation state"
        return result
    if verification_status == "failed":
        result["status"] = "failed"
        result["reason"] = "matching record reports failed verification"
        return result

    result["status"] = "healthy"
    result["reason"] = "matching schema-v3 identity/version has no recorded current block"
    return result


def resolve_record(skill_root: Path, project: Path | None) -> tuple[Path | None, str]:
    """Find the child's record from its descriptor: AGENT_DIR/roblox/resources/records/<slug>.yaml."""
    contract = load_contract(skill_root, check_documents=False)
    reconciliation = contract["reconciliation"]
    if project is not None:
        return resolve_agent_path(project.resolve(), reconciliation["record"]), ""
    if contract["scope"] == "user":
        return resolve_user_store_path(reconciliation["no_project_record"])
    return None, "project-scoped child needs --project; record checks skipped"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only batch query for current blocks on generated resource skills."
    )
    parser.add_argument(
        "--pair",
        action="append",
        nargs=2,
        default=[],
        metavar=("SKILL_DIR", "RECORD_YAML"),
        help="child directory and an explicit record path (a missing file reports NO-RECORD); repeat for a batch",
    )
    parser.add_argument(
        "--child",
        action="append",
        default=[],
        metavar="SKILL_DIR",
        help="child directory whose record is found from its resource.yaml under the project's AGENT_DIR "
             "(.claude/ or .agents/); repeat for a batch",
    )
    parser.add_argument("--project", type=Path, help="project root used to resolve AGENT_DIR for --child")
    parser.add_argument("--json", action="store_true", help="emit one JSON array instead of line output")
    args = parser.parse_args(argv)
    if not args.pair and not args.child:
        parser.error("supply --pair SKILL_DIR RECORD_YAML or --child SKILL_DIR [--project PROJECT]")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    results = [query_pair(Path(skill).resolve(), Path(record).resolve()) for skill, record in args.pair]
    for skill in args.child:
        skill_root = Path(skill).resolve()
        try:
            record, note = resolve_record(skill_root, args.project)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            results.append({"skill": str(skill_root), "record": "", "status": "unknown", "reason": str(exc)})
            continue
        if record is None:
            results.append({"skill": str(skill_root), "record": "", "status": "unknown", "reason": note})
            continue
        result = query_pair(skill_root, record.resolve())
        if note:
            result["note"] = note
        results.append(result)
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for result in results:
            suffix = f" ({result['note']})" if result.get("note") else ""
            print(f"{result['status'].upper()}: {result['skill']} :: {result['reason']}{suffix}")
    if any(result["status"] in {"blocked", "mismatch", "failed"} for result in results):
        return 1
    if any(result["status"] == "unknown" for result in results):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
