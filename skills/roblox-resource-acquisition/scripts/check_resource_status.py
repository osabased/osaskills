#!/usr/bin/env python3
"""Read-only current block query for generated Roblox resource skills.

The command intentionally reads child provenance labels and only the matching
record's schema, identity, version, block, reconciliation, verification, and
matching-host status fields. It never executes evidence commands or performs
full lifecycle reconciliation.
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
from validate_skill import NO_PACKAGE_IDENTITY_RE

RECONCILIATION_STATES = {"matched", "mismatched", "blocked", "unknown", "not-applicable"}
VERIFICATION_STATES = {"unverified", "unavailable", "verified", "failed"}
HOST_STATES = {"installed", "operational", "blocked", "disabled", "removed", "unavailable", "failed"}


def _host_adoption_matches_child(adoption: dict[str, Any], child_name: str, skill_root: Path, record_path: Path) -> bool:
    location = adoption.get("location")
    if not isinstance(location, str) or not location.strip():
        return False
    location_path = Path(location)
    candidates = [location_path]
    record_parts = [part.lower() for part in record_path.parts]
    if len(record_path.parents) >= 5 and record_parts[-5:-1] == [".agents", "roblox", "resources", "records"]:
        candidates.append(record_path.parents[4] / location_path)
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved == skill_root or resolved == skill_root / "SKILL.md":
            return True
    normalized = location.replace("\\", "/").rstrip("/").lower()
    return normalized.endswith(f"/{child_name.lower()}") or normalized.endswith(
        f"/{child_name.lower()}/skill.md"
    )


def query_pair(skill_root: Path, record_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "skill": str(skill_root),
        "record": str(record_path),
        "status": "unknown",
        "reason": "",
    }
    try:
        if not (skill_root / "SKILL.md").is_file():
            raise ValueError("generated skill directory does not contain SKILL.md")
        if not record_path.is_file() or record_path.suffix.lower() not in {".yaml", ".yml"}:
            raise ValueError("resource record is missing or is not YAML")
        metadata, child = _child_provenance(skill_root)
        record = load_record(record_path)
    except (OSError, UnicodeError, ValueError) as exc:
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
        result["reason"] = "record generated_skill does not match child name"
        return result

    child_slug = child.get("slug")
    if not child_slug or not isinstance(record.get("slug"), str) or record.get("slug") != child_slug.strip():
        result["reason"] = "record slug does not match child provenance"
        return result

    child_canonical = _concrete_url(child.get("canonical_url")) or _concrete_url(child.get("devforum_url"))
    record_canonical = record.get("canonical_url")
    if not child_canonical or not nonempty_string(record_canonical):
        result["reason"] = "canonical identity is missing"
        return result
    if not _same_url(record_canonical.strip(), child_canonical):
        result["reason"] = "record canonical identity does not match child provenance"
        return result

    child_package = child.get("package_id")
    record_package = record.get("package_id")
    if child_package and NO_PACKAGE_IDENTITY_RE.fullmatch(child_package.strip()):
        if nonempty_string(record_package):
            result["reason"] = "record package identity conflicts with child provenance"
            return result
    elif not child_package or not nonempty_string(record_package) or record_package.strip() != child_package.strip():
        result["reason"] = "record package identity does not match child provenance"
        return result

    verification = record.get("verification")
    verification_status = verification.get("status") if isinstance(verification, dict) else None
    if not isinstance(verification_status, str) or verification_status not in VERIFICATION_STATES:
        result["reason"] = "verification state is missing or malformed"
        return result
    record_version = verification.get("version_or_commit") if isinstance(verification, dict) else None
    child_version = child.get("version")
    if not child_version or not nonempty_string(record_version) or record_version.strip() != child_version.strip():
        result["reason"] = "record version/state does not match child provenance"
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
        host_status = adoption.get("status")
        if not isinstance(host_status, str) or host_status not in HOST_STATES:
            result["reason"] = f"host_adoptions[{index}].status is malformed"
            return result
        if host_status == "blocked" and _host_adoption_matches_child(
            adoption, child_name.strip(), skill_root, record_path
        ):
            result["status"] = "blocked"
            adoption_result = adoption.get("result")
            result["reason"] = (
                adoption_result.strip()
                if isinstance(adoption_result, str) and adoption_result.strip()
                else "matching host adoption is blocked"
            )
            return result
        if host_status in {"disabled", "removed", "failed", "unavailable"} and _host_adoption_matches_child(
            adoption, child_name.strip(), skill_root, record_path
        ):
            result["reason"] = f"matching host adoption is {host_status}"
            return result

    if reconciliation_status in {"mismatched", "unknown"}:
        result["reason"] = f"matching record reports {reconciliation_status} reconciliation state"
        return result
    if verification_status == "failed":
        result["reason"] = "matching record reports failed verification without a usable block description"
        return result

    result["status"] = "healthy"
    result["reason"] = "matching schema-v3 identity/version has no recorded current block"
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only batch query for current blocks on generated resource skills."
    )
    parser.add_argument(
        "--pair",
        action="append",
        nargs=2,
        metavar=("SKILL_DIR", "RECORD_YAML"),
        required=True,
        help="generated child directory and its matching portable resource record; repeat for a batch",
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON array instead of line output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    results = [query_pair(Path(skill).resolve(), Path(record).resolve()) for skill, record in args.pair]
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for result in results:
            print(f"{result['status'].upper()}: {result['skill']} :: {result['reason']}")
    if any(result["status"] == "unknown" for result in results):
        return 2
    if any(result["status"] == "blocked" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
