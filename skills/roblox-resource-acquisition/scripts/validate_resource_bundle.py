#!/usr/bin/env python3
"""Validate consistency between a resource record and its generated child skill.

The standalone validators remain authoritative for each artifact. This coupled
validator adds only relationship checks so a valid record cannot accidentally
be paired with a valid child for a different resource/version/state.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_resource_record import load_record, nonempty_string, validate_record
from validate_skill import parse_frontmatter, validate_skill
from _resource_contract import child_identity, load_contract, url_identity


def _child_provenance(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    metadata, _body = parse_frontmatter((root / "SKILL.md").read_text(encoding="utf-8-sig"))
    return metadata, child_identity(root)


def _concrete_url(value: str | None) -> str | None:
    if not value:
        return None
    try:
        url_identity(value)
    except ValueError:
        return None
    return value


def _same_url(left: str, right: str) -> bool:
    try:
        return url_identity(left) == url_identity(right)
    except ValueError:
        return left.strip() == right.strip()


def validate_bundle(
    record_path: Path,
    record: dict[str, Any],
    skill_root: Path,
) -> tuple[list[str], list[str]]:
    """Return relationship errors/notes after validating both artifacts."""
    errors: list[str] = []
    notes: list[str] = []

    record_errors, record_notes = validate_record(
        record_path,
        record,
        current_skill_root=skill_root,
        require_current_evidence=True,
    )
    skill_errors, skill_warnings = validate_skill(skill_root)
    errors.extend(f"resource record: {message}" for message in record_errors)
    errors.extend(f"generated skill: {message}" for message in skill_errors)
    notes.extend(f"resource record: {message}" for message in record_notes)
    notes.extend(f"generated skill warning: {message}" for message in skill_warnings)
    if record_errors or skill_errors:
        return errors, notes

    metadata, child = _child_provenance(skill_root)
    child_name = metadata.get("name")
    record_skill = record.get("generated_skill")
    if not isinstance(child_name, str):
        errors.append("generated skill frontmatter name is unavailable for bundle matching")
    elif not nonempty_string(record_skill) or record_skill.strip() != child_name.strip():
        errors.append("generated_skill must exactly match the child frontmatter name")

    skill_validation = record.get("skill_validation")
    if not isinstance(skill_validation, dict) or skill_validation.get("structural_passed") is not True:
        errors.append(
            "bundle finalization requires skill_validation.structural_passed: true after the current child passes validate_skill.py"
        )

    record_slug = record.get("slug")
    child_slug = child.get("slug")
    if not nonempty_string(record_slug) or not child_slug or record_slug.strip() != child_slug.strip():
        errors.append("resource record slug must exactly match child resource.yaml slug")

    child_canonical = _concrete_url(child.get("canonical_url"))
    child_devforum = _concrete_url(child.get("devforum_url"))
    effective_child_canonical = child_canonical or child_devforum
    record_canonical = record.get("canonical_url")
    if effective_child_canonical:
        if not nonempty_string(record_canonical):
            errors.append("resource record canonical_url must carry the canonical URL used by the child resource contract")
        elif not _same_url(record_canonical.strip(), effective_child_canonical):
            errors.append("resource record canonical_url must match the child canonical provenance URL")

    record_devforum = record.get("devforum_url")
    if child_devforum:
        if not nonempty_string(record_devforum):
            errors.append("resource record devforum_url must match the concrete DevForum provenance recorded by the child")
        elif not _same_url(record_devforum.strip(), child_devforum):
            errors.append("resource record devforum_url must match the child DevForum provenance URL")
    elif nonempty_string(record_devforum):
        errors.append("resource record devforum_url is populated but the child resource contract explicitly has no DevForum URL")

    record_package = record.get("package_id")
    child_package = child.get("package_id")
    if child_package is None:
        if nonempty_string(record_package):
            errors.append("resource record package_id must be empty when child resource contract states no package identity exists")
    elif child_package:
        if not nonempty_string(record_package) or record_package.strip() != child_package.strip():
            errors.append("resource record package_id must exactly match child resource.yaml package identity")

    verification = record.get("verification")
    record_version = verification.get("version_or_commit") if isinstance(verification, dict) else None
    child_version = child.get("version")
    if not nonempty_string(record_version) or not child_version or record_version.strip() != child_version.strip():
        errors.append("resource record verification.version_or_commit must exactly match the child reviewed source state")


    contract = load_contract(skill_root)
    recorded_scope = skill_validation.get("claim_scope", "") if isinstance(skill_validation, dict) else ""
    if recorded_scope and recorded_scope != contract["guidance"]["claim_scope"]:
        errors.append("recorded guidance claim_scope differs from resource.yaml")
    return errors, notes


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate consistency between a portable resource record and its generated child skill."
    )
    parser.add_argument("resource_record", type=Path, help="resource-record YAML file")
    parser.add_argument("generated_skill_directory", type=Path, help="directory containing child SKILL.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    record_path = args.resource_record.resolve()
    skill_root = args.generated_skill_directory.resolve()
    if not record_path.is_file() or record_path.suffix.lower() not in {".yaml", ".yml"}:
        print(f"FAIL\n- expected an existing .yaml/.yml resource record: {record_path}")
        return 1
    if not (skill_root / "SKILL.md").is_file():
        print(f"FAIL\n- expected generated skill directory containing SKILL.md: {skill_root}")
        return 1
    try:
        record = load_record(record_path)
        errors, notes = validate_bundle(record_path, record, skill_root)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"FAIL\n- {exc}")
        return 1
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        for note in notes:
            print(f"NOTE: {note}")
        return 1
    print("PASS: resource-record/generated-skill bundle consistency checks passed")
    for note in notes:
        print(f"NOTE: {note}")
    print("NOTE: bundle consistency does not establish independent behavioral validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
