#!/usr/bin/env python3
"""Validate portable Roblox resource evidence records.

This is a structural and state-consistency validator. Passing does not establish
that the resource, source claims, or generated skill are actually correct.

PyYAML is required (see requirements.txt). A single parser everywhere keeps
trust/verification verdicts identical across environments; the script exits
with code 2 and an install hint when PyYAML is missing.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (
    DEVFORUM_TOPIC_PATH_RE,
    SLUG_RE,
    VOLATILE_VERSION_TOKEN_RE,
    has_immutable_version_evidence,
    load_yaml,
    normalize_empty_values,
    validate_date,
    validate_https_url,
    validated_url_host,
)
from validate_skill_catalog import CatalogSkill, catalog_fingerprint as compute_catalog_fingerprint, load_catalog_skill

TOP_LEVEL_FIELDS = {
    "schema_version",
    "resource",
    "slug",
    "discovery_origin",
    "project_use",
    "trust",
    "canonical_url",
    "package_id",
    "verification",
    "reconciliation",
    "capability",
    "devforum_url",
    "selection_reason",
    "alternatives_considered",
    "resource_proof",
    "generated_skill",
    "skill_validation",
    "host_adoptions",
    "limitations",
    "blocked_use_or_version",
    "rejection_reason",
    "reconsider_when",
}
REQUIRED_TOP_LEVEL_FIELDS = TOP_LEVEL_FIELDS
NESTED_FIELDS = {
    "project_use": {"status", "role", "scope", "authority"},
    "trust": {"level", "basis", "reason"},
    "verification": {"status", "validated_at", "version_or_commit"},
    "reconciliation": {
        "status",
        "checked_at",
        "installed_identity",
        "installed_version_or_commit",
        "detection_method",
        "parent_state_sources",
        "result",
    },
    "resource_proof": {"executed", "passed", "target_version_or_commit", "environment", "result", "unavailable_claims"},
    "skill_validation": {
        "structural_passed",
        "independent_behavioral_executed",
        "independent_behavioral_passed",
        "environment",
        "result",
        "catalog_routing_status",
        "catalog_fingerprint",
        "catalog_environment",
        "catalog_result",
        "checks",
        "claim_scope",
    },
}
OPTIONAL_NESTED_FIELDS = {
    "resource_proof": {"target_version_or_commit"},
    # ``checks`` is a schema-v3 extension. Omission remains readable as legacy
    # evidence, but strict finalization cannot treat prose/booleans as current.
    "skill_validation": {"checks", "claim_scope"},
}
LIST_FIELDS = {
    "alternatives_considered",
    "limitations",
    "resource_proof.unavailable_claims",
    "reconciliation.parent_state_sources",
}
BOOL_FIELDS = {
    "resource_proof.executed",
    "resource_proof.passed",
    "skill_validation.structural_passed",
    "skill_validation.independent_behavioral_executed",
    "skill_validation.independent_behavioral_passed",
}
STRING_FIELDS = {
    "resource",
    "slug",
    "discovery_origin",
    "canonical_url",
    "package_id",
    "capability",
    "devforum_url",
    "selection_reason",
    "generated_skill",
    "blocked_use_or_version",
    "rejection_reason",
    "reconsider_when",
    "project_use.status",
    "project_use.role",
    "project_use.scope",
    "project_use.authority",
    "trust.level",
    "trust.basis",
    "trust.reason",
    "verification.status",
    "verification.validated_at",
    "verification.version_or_commit",
    "reconciliation.status",
    "reconciliation.checked_at",
    "reconciliation.installed_identity",
    "reconciliation.installed_version_or_commit",
    "reconciliation.detection_method",
    "reconciliation.result",
    "resource_proof.target_version_or_commit",
    "resource_proof.environment",
    "resource_proof.result",
    "skill_validation.environment",
    "skill_validation.result",
    "skill_validation.catalog_routing_status",
    "skill_validation.catalog_fingerprint",
    "skill_validation.catalog_environment",
    "skill_validation.catalog_result",
    "skill_validation.claim_scope",
}
ALLOWED_ORIGINS = {"curated", "project", "devforum", "other"}
ALLOWED_PROJECT_USE = {"not-applicable", "adopted", "retired"}
ALLOWED_TRUST_LEVELS = {"trusted", "untrusted"}
ALLOWED_TRUST_BASES = {"", "curated", "verified-acquisition", "project", "explicit-user", "other"}
ALLOWED_VERIFICATION = {"unverified", "unavailable", "verified", "failed"}
ALLOWED_RECONCILIATION = {"matched", "mismatched", "blocked", "unknown", "not-applicable"}
ALLOWED_CATALOG_ROUTING = {"not-applicable", "unverified", "verified", "unavailable", "failed"}
ALLOWED_HOST_SCOPES = {"repo", "user", "admin", "plugin", "other"}
ALLOWED_HOST_STATUSES = {"installed", "operational", "blocked", "disabled", "removed", "unavailable", "failed"}
ALLOWED_PRESENCE = {"present", "absent", "not-applicable", "unknown"}
ALLOWED_DISCOVERY = {"yes", "no", "unknown"}
ALLOWED_ENABLED = {"yes", "no", "not-applicable", "unknown"}
ALLOWED_ACTIVATION = {"passed", "failed", "not-run", "unavailable"}
HOST_FIELDS = {"host", "scope", "location", "status", "checked_at", "result", "evidence"}
HOST_EVIDENCE_FIELDS = {"installed", "registered", "discoverable", "enabled", "explicit_activation"}
FINGERPRINT_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
CHECK_FIELDS = {
    "check_id",
    "kind",
    "execution_mode",
    "status",
    "tested_at",
    "target_version_or_commit",
    "inputs",
    "command",
    "result",
    "artifact",
    "tested_child_sha256",
    "scope_fingerprint",
}
OPTIONAL_CHECK_FIELDS = {"command", "artifact", "tested_child_sha256", "scope_fingerprint"}
CHECK_INPUT_FIELDS = {"role", "path", "section", "sha256"}
OPTIONAL_CHECK_INPUT_FIELDS = {"section"}
CHECK_KINDS = {
    "routing",
    "instruction-response",
    "executable-integration",
    "lifecycle-failure-cleanup",
}
EXECUTION_MODES = {"independent-agent", "same-agent-audit", "command", "studio-playtest"}
CHECK_STATUSES = {"passed", "failed", "unavailable", "historical"}
CHECK_INPUT_ROLES = {
    "fixture",
    "api",
    "contract",
    "configuration",
    "shared-dependency",
    "activation-metadata",
}
CLAIM_SCOPES = {"unclaimed", "advice-only", "executable-integration"}


def load_record(path: Path) -> dict[str, Any]:
    loaded = load_yaml(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("record must be a YAML mapping")
    normalize_empty_values(loaded, LIST_FIELDS)
    verification = loaded.get("verification")
    if isinstance(verification, dict) and isinstance(verification.get("validated_at"), date):
        verification["validated_at"] = verification["validated_at"].isoformat()
    reconciliation = loaded.get("reconciliation")
    if isinstance(reconciliation, dict) and isinstance(reconciliation.get("checked_at"), date):
        reconciliation["checked_at"] = reconciliation["checked_at"].isoformat()
    host_adoptions = loaded.get("host_adoptions")
    if isinstance(host_adoptions, list):
        for adoption in host_adoptions:
            if isinstance(adoption, dict) and isinstance(adoption.get("checked_at"), date):
                adoption["checked_at"] = adoption["checked_at"].isoformat()
            if isinstance(adoption, dict) and isinstance(adoption.get("evidence"), dict):
                evidence = adoption["evidence"]
                for field in ("discoverable", "enabled"):
                    if isinstance(evidence.get(field), bool):
                        evidence[field] = "yes" if evidence[field] else "no"
    skill_validation = loaded.get("skill_validation")
    if isinstance(skill_validation, dict) and isinstance(skill_validation.get("checks"), list):
        for check in skill_validation["checks"]:
            if isinstance(check, dict) and isinstance(check.get("tested_at"), date):
                check["tested_at"] = check["tested_at"].isoformat()
    return loaded


def dotted_get(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _section_bytes(path: Path, heading: str) -> bytes | None:
    """Return exact Markdown section bytes for scoped freshness hashing."""
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(rf"^##[ \t]+{re.escape(heading.strip())}[ \t]*$", text, re.M | re.I)
    if not match:
        return None
    next_heading = re.search(r"^##[ \t]+.+$", text[match.end() :], re.M)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.start() : end].encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _validate_skill_checks(
    data: dict[str, Any],
    errors: list[str],
    notes: list[str],
    *,
    current_skill_root: Path | None,
    require_current_evidence: bool,
) -> None:
    checks = dotted_get(data, "skill_validation.checks")
    independent_passed = dotted_get(data, "skill_validation.independent_behavioral_passed")
    claim_scope = dotted_get(data, "skill_validation.claim_scope")
    catalog_status = dotted_get(data, "skill_validation.catalog_routing_status")
    catalog_fingerprint = dotted_get(data, "skill_validation.catalog_fingerprint")
    if claim_scope is not None and (not isinstance(claim_scope, str) or claim_scope not in CLAIM_SCOPES):
        errors.append("skill_validation.claim_scope must be unclaimed, advice-only, or executable-integration")
    if checks is None:
        if independent_passed is True:
            message = (
                "legacy skill_validation booleans/prose do not establish current independent behavioral evidence"
            )
            if require_current_evidence:
                errors.append(message)
            else:
                notes.append(message)
        if catalog_status == "verified":
            message = "legacy catalog routing fields do not establish current structured routing evidence"
            if require_current_evidence:
                errors.append(message)
            else:
                notes.append(message)
        return
    if not isinstance(checks, list):
        return

    record_version = dotted_get(data, "verification.version_or_commit")
    current_independent_kinds: set[str] = set()
    current_routing_fingerprints: set[str] = set()
    seen_ids: set[str] = set()
    for index, check in enumerate(checks):
        prefix = f"skill_validation.checks[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        unknown = sorted(set(check) - CHECK_FIELDS)
        missing = sorted(CHECK_FIELDS - OPTIONAL_CHECK_FIELDS - set(check))
        if unknown:
            errors.append(f"{prefix} has unknown field(s): {', '.join(unknown)}")
        if missing:
            errors.append(f"{prefix} is missing field(s): {', '.join(missing)}")

        for field in CHECK_FIELDS - {"inputs"}:
            if field in check and not isinstance(check.get(field), str):
                errors.append(f"{prefix}.{field} must be a string")
        check_id = check.get("check_id")
        if not nonempty_string(check_id):
            errors.append(f"{prefix}.check_id must be a non-empty string")
        elif check_id.strip() in seen_ids:
            errors.append(f"duplicate skill validation check_id: {check_id.strip()}")
        else:
            seen_ids.add(check_id.strip())

        kind = check.get("kind")
        mode = check.get("execution_mode")
        status = check.get("status")
        tested_at = check.get("tested_at")
        target = check.get("target_version_or_commit")
        valid_kind = isinstance(kind, str) and kind in CHECK_KINDS
        valid_mode = isinstance(mode, str) and mode in EXECUTION_MODES
        valid_status = isinstance(status, str) and status in CHECK_STATUSES
        if not valid_kind:
            errors.append(f"{prefix}.kind has an invalid value")
        if not valid_mode:
            errors.append(f"{prefix}.execution_mode has an invalid value")
        if not valid_status:
            errors.append(f"{prefix}.status has an invalid value")
        if nonempty_string(tested_at):
            errors.extend(validate_date(tested_at.strip(), field=f"{prefix}.tested_at"))
        else:
            errors.append(f"{prefix}.tested_at must be a valid ISO date")
        if not nonempty_string(target):
            errors.append(f"{prefix}.target_version_or_commit must be non-empty")
        elif status != "historical" and nonempty_string(record_version) and target.strip() != record_version.strip():
            errors.append(f"{prefix}.target_version_or_commit must match verification.version_or_commit")

        tested_child = check.get("tested_child_sha256")
        scope_fingerprint = check.get("scope_fingerprint")
        if nonempty_string(tested_child) and not FINGERPRINT_RE.fullmatch(tested_child.strip()):
            errors.append(f"{prefix}.tested_child_sha256 must use sha256:<64 lowercase hex characters>")
        if nonempty_string(scope_fingerprint) and not FINGERPRINT_RE.fullmatch(scope_fingerprint.strip()):
            errors.append(f"{prefix}.scope_fingerprint must use sha256:<64 lowercase hex characters>")
        if kind == "routing" and status == "passed" and not nonempty_string(scope_fingerprint):
            errors.append(f"{prefix} passed routing evidence requires scope_fingerprint")
        if valid_kind and kind != "routing" and nonempty_string(scope_fingerprint):
            errors.append(f"{prefix}.scope_fingerprint is only valid for routing evidence")

        if status in ("passed", "failed", "unavailable", "historical") and not nonempty_string(check.get("result")):
            errors.append(f"{prefix}.result must be non-empty")
        if kind in ("executable-integration", "lifecycle-failure-cleanup") and status == "passed":
            if mode not in ("command", "studio-playtest", "independent-agent"):
                errors.append(f"{prefix} executable evidence requires command, studio-playtest, or independent-agent execution")
            if not nonempty_string(check.get("command")):
                errors.append(f"{prefix} passed executable evidence requires command")

        inputs = check.get("inputs")
        if not isinstance(inputs, list):
            errors.append(f"{prefix}.inputs must be a list")
            inputs = []
        if status == "passed" and kind != "routing" and not inputs:
            errors.append(f"{prefix} passed non-routing evidence requires scoped inputs")
        if status == "passed" and kind in ("executable-integration", "lifecycle-failure-cleanup"):
            if not any(isinstance(item, dict) and item.get("role") == "fixture" for item in inputs):
                errors.append(f"{prefix} passed executable evidence requires a maintained fixture input")
        if status == "passed" and kind == "routing":
            if not any(isinstance(item, dict) and item.get("role") == "activation-metadata" for item in inputs):
                errors.append(f"{prefix} passed routing evidence requires a current activation-metadata input")

        routing_skills: list[CatalogSkill] = []
        routing_has_current_child = False
        for input_index, evidence_input in enumerate(inputs):
            input_prefix = f"{prefix}.inputs[{input_index}]"
            if not isinstance(evidence_input, dict):
                errors.append(f"{input_prefix} must be a mapping")
                continue
            unknown_input = sorted(set(evidence_input) - CHECK_INPUT_FIELDS)
            missing_input = sorted(CHECK_INPUT_FIELDS - OPTIONAL_CHECK_INPUT_FIELDS - set(evidence_input))
            if unknown_input:
                errors.append(f"{input_prefix} has unknown field(s): {', '.join(unknown_input)}")
            if missing_input:
                errors.append(f"{input_prefix} is missing field(s): {', '.join(missing_input)}")
            role = evidence_input.get("role")
            input_path = evidence_input.get("path")
            section = evidence_input.get("section")
            digest = evidence_input.get("sha256")
            valid_role = isinstance(role, str) and role in CHECK_INPUT_ROLES
            if not valid_role:
                errors.append(f"{input_prefix}.role has an invalid value")
            if not nonempty_string(input_path):
                errors.append(f"{input_prefix}.path must be a non-empty string")
            if "section" in evidence_input and not isinstance(section, str):
                errors.append(f"{input_prefix}.section must be a string")
            if not nonempty_string(digest) or not FINGERPRINT_RE.fullmatch(digest.strip()):
                errors.append(f"{input_prefix}.sha256 must use sha256:<64 lowercase hex characters>")
            if status != "passed" or current_skill_root is None or not nonempty_string(input_path):
                continue
            resolved = Path(input_path)
            if not resolved.is_absolute():
                resolved = current_skill_root / resolved
            resolved = resolved.resolve()
            if not resolved.is_file():
                errors.append(f"{input_prefix} current input is missing: {resolved}")
                continue
            if role == "activation-metadata":
                expected_skill = (current_skill_root / "SKILL.md").resolve()
                if resolved.name.lower() != "skill.md" or nonempty_string(section):
                    errors.append(
                        f"{input_prefix} activation-metadata must identify a whole SKILL.md metadata surface"
                    )
                    continue
                try:
                    routing_skill = load_catalog_skill(resolved.parent)
                    current_activation = compute_catalog_fingerprint([routing_skill])
                except (OSError, UnicodeError, ValueError) as exc:
                    errors.append(f"{input_prefix} activation metadata could not be read: {exc}")
                    continue
                routing_skills.append(routing_skill)
                if resolved == expected_skill:
                    routing_has_current_child = True
                if nonempty_string(digest) and current_activation != digest.strip():
                    errors.append(f"{input_prefix} activation metadata hash is stale")
                continue
            try:
                payload = _section_bytes(resolved, section) if nonempty_string(section) else resolved.read_bytes()
            except (OSError, UnicodeError) as exc:
                errors.append(f"{input_prefix} could not be read: {exc}")
                continue
            if payload is None:
                errors.append(f"{input_prefix} section is missing: {section}")
            elif nonempty_string(digest) and _sha256_bytes(payload) != digest.strip():
                errors.append(f"{input_prefix} input hash is stale")

        if status == "passed" and kind == "routing" and current_skill_root is not None:
            if not routing_has_current_child:
                errors.append(f"{prefix} passed routing evidence must include the current child's activation metadata")
            if routing_skills and nonempty_string(scope_fingerprint):
                declared_scope = compute_catalog_fingerprint(routing_skills)
                if declared_scope != scope_fingerprint.strip():
                    errors.append(f"{prefix}.scope_fingerprint is stale for the declared routing inputs")

        if status == "passed" and mode == "independent-agent" and kind != "routing":
            current_independent_kinds.add(kind)
        if status == "passed" and mode == "independent-agent" and kind == "routing" and nonempty_string(scope_fingerprint):
            current_routing_fingerprints.add(scope_fingerprint.strip())

    if independent_passed is True and require_current_evidence:
        if claim_scope == "advice-only":
            if "instruction-response" not in current_independent_kinds:
                errors.append("advice-only independent_behavioral_passed requires a current independent instruction-response check")
        elif claim_scope == "executable-integration":
            required = {"executable-integration", "lifecycle-failure-cleanup"}
            missing = sorted(required - current_independent_kinds)
            if missing:
                errors.append(
                    "executable-integration independent_behavioral_passed requires current independent checks: "
                    + ", ".join(missing)
                )
        else:
            errors.append("independent_behavioral_passed requires an explicit current skill_validation.claim_scope")
    if catalog_status == "verified" and require_current_evidence:
        if not nonempty_string(catalog_fingerprint) or catalog_fingerprint.strip() not in current_routing_fingerprints:
            errors.append("verified catalog routing requires a current independent routing check for catalog_fingerprint")


def validate_record(
    path: Path,
    data: dict[str, Any],
    *,
    current_skill_root: Path | None = None,
    require_current_evidence: bool = False,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []

    unknown = sorted(set(data) - TOP_LEVEL_FIELDS)
    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(data))
    if unknown:
        errors.append(f"unknown top-level field(s): {', '.join(unknown)}")
    if missing:
        errors.append(f"missing required top-level field(s): {', '.join(missing)}")

    if data.get("schema_version") != 3:
        errors.append("schema_version must be integer 3; older records must enter repair/reconcile")

    for parent, allowed in NESTED_FIELDS.items():
        value = data.get(parent)
        if not isinstance(value, dict):
            errors.append(f"{parent} must be a mapping")
            continue
        nested_unknown = sorted(set(value) - allowed)
        optional = OPTIONAL_NESTED_FIELDS.get(parent, set())
        nested_missing = sorted((allowed - optional) - set(value))
        if nested_unknown:
            errors.append(f"unknown {parent} field(s): {', '.join(nested_unknown)}")
        if nested_missing:
            errors.append(f"missing required {parent} field(s): {', '.join(nested_missing)}")

    for field in STRING_FIELDS:
        value = dotted_get(data, field)
        if value is not None and not isinstance(value, str):
            errors.append(f"{field} must be a string")

    for field in LIST_FIELDS:
        value = dotted_get(data, field)
        if value is None:
            continue
        if not isinstance(value, list):
            errors.append(f"{field} must be a list")
            continue
        if any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"{field} must contain only non-empty strings")

    for field in BOOL_FIELDS:
        value = dotted_get(data, field)
        if value is not None and not isinstance(value, bool):
            errors.append(f"{field} must be true or false")

    resource = data.get("resource")
    if isinstance(resource, str) and not resource.strip():
        errors.append("resource must not be empty")

    slug = data.get("slug")
    if isinstance(slug, str) and slug.strip() and not SLUG_RE.fullmatch(slug.strip()):
        errors.append("slug must be lowercase kebab-case (a-z, 0-9, hyphen) when present")

    origin = data.get("discovery_origin")
    if isinstance(origin, str) and origin not in ALLOWED_ORIGINS:
        errors.append(f"discovery_origin must be one of: {', '.join(sorted(ALLOWED_ORIGINS))}")

    selection_reason = data.get("selection_reason")
    if origin == "other" and not nonempty_string(selection_reason):
        errors.append("discovery_origin other requires selection_reason to preserve selection provenance")

    project_status = dotted_get(data, "project_use.status")
    project_role = dotted_get(data, "project_use.role")
    project_scope = dotted_get(data, "project_use.scope")
    project_authority = dotted_get(data, "project_use.authority")
    if isinstance(project_status, str) and project_status not in ALLOWED_PROJECT_USE:
        errors.append("project_use.status must be not-applicable, adopted, or retired")
    if project_status in {"adopted", "retired"}:
        for field, value in (
            ("role", project_role),
            ("scope", project_scope),
            ("authority", project_authority),
        ):
            if not nonempty_string(value):
                errors.append(f"project_use.status {project_status!r} requires project_use.{field}")
    if project_status == "not-applicable" and any(
        nonempty_string(value) for value in (project_role, project_scope, project_authority)
    ):
        errors.append("project_use.status not-applicable requires empty role, scope, and authority")

    trust_level = dotted_get(data, "trust.level")
    trust_basis = dotted_get(data, "trust.basis")
    trust_reason = dotted_get(data, "trust.reason")
    if isinstance(trust_level, str) and trust_level not in ALLOWED_TRUST_LEVELS:
        errors.append("trust.level must be exactly trusted or untrusted")
    if isinstance(trust_basis, str) and trust_basis not in ALLOWED_TRUST_BASES:
        errors.append("trust.basis must be curated, verified-acquisition, project, explicit-user, other, or empty")
    if trust_level == "trusted":
        if not nonempty_string(trust_basis):
            errors.append("trusted records must name a trust.basis")
        if not nonempty_string(trust_reason):
            errors.append("trusted records must explain trust.reason")
        if not nonempty_string(slug):
            errors.append("trusted records require slug to bind trust to a stable identity")
        if not nonempty_string(data.get("canonical_url")) and not nonempty_string(data.get("package_id")):
            errors.append("trusted records require canonical_url or package_id to bind trust to canonical identity")
    if project_status == "adopted" and trust_level != "trusted":
        errors.append("project_use.status adopted requires trust.level: trusted")
    if trust_basis in {"curated", "verified-acquisition", "project", "explicit-user", "other"} and trust_level != "trusted":
        errors.append(f"trust.basis {trust_basis!r} requires trust.level: trusted")
    if trust_basis == "curated" and origin != "curated":
        errors.append("trust.basis curated requires discovery_origin: curated")
    if trust_basis == "verified-acquisition" and origin == "curated":
        errors.append("verified-acquisition is for previously untrusted discovery, not curated-origin records")

    canonical = data.get("canonical_url")
    if isinstance(canonical, str) and canonical.strip():
        errors.extend(validate_https_url(canonical.strip(), field="canonical_url"))
    devforum = data.get("devforum_url")
    if isinstance(devforum, str) and devforum.strip():
        devforum_value = devforum.strip()
        errors.extend(validate_https_url(devforum_value, field="devforum_url", expected_host="devforum.roblox.com"))
        try:
            parsed_devforum = urlparse(devforum_value)
        except ValueError:
            parsed_devforum = None
        if parsed_devforum is not None and validated_url_host(parsed_devforum) == "devforum.roblox.com":
            if not DEVFORUM_TOPIC_PATH_RE.fullmatch(parsed_devforum.path):
                errors.append("devforum_url must identify a specific DevForum topic, not a category/home/search page")

    status = dotted_get(data, "verification.status")
    validated_at = dotted_get(data, "verification.validated_at")
    version = dotted_get(data, "verification.version_or_commit")
    if isinstance(status, str) and status not in ALLOWED_VERIFICATION:
        errors.append("verification.status must be unverified, unavailable, verified, or failed")
    if isinstance(validated_at, str) and validated_at.strip():
        errors.extend(validate_date(validated_at.strip(), field="verification.validated_at"))
    if status in {"verified", "unavailable", "failed"} and not nonempty_string(validated_at):
        errors.append(f"verification.status {status!r} requires verification.validated_at")
    if status == "verified" and not nonempty_string(version):
        errors.append("verified resource records must name verification.version_or_commit")
    if status == "verified" and isinstance(version, str) and version.strip() and not has_immutable_version_evidence(version):
        errors.append(
            "verified resource records require an immutable version/commit, an explicitly labeled named tag/release/build, or a valid dated source state"
        )
    if isinstance(version, str) and version.strip() and VOLATILE_VERSION_TOKEN_RE.search(version):
        if not has_immutable_version_evidence(version):
            errors.append("verification.version_or_commit must not rely only on a volatile pointer such as latest/current/main")

    proof_executed = dotted_get(data, "resource_proof.executed")
    proof_passed = dotted_get(data, "resource_proof.passed")
    proof_target = dotted_get(data, "resource_proof.target_version_or_commit")
    proof_environment = dotted_get(data, "resource_proof.environment")
    proof_result = dotted_get(data, "resource_proof.result")
    unavailable_claims = dotted_get(data, "resource_proof.unavailable_claims")
    if proof_passed is True and proof_executed is not True:
        errors.append("resource_proof.passed cannot be true unless resource_proof.executed is true")
    if proof_executed is True:
        if not nonempty_string(proof_target):
            errors.append("executed resource proof must record resource_proof.target_version_or_commit")
        if not nonempty_string(proof_environment):
            errors.append("executed resource proof must record resource_proof.environment")
        if not nonempty_string(proof_result):
            errors.append("executed resource proof must record resource_proof.result")
    if proof_executed is True and nonempty_string(proof_target) and nonempty_string(version):
        if proof_target.strip() != version.strip():
            errors.append("executed resource proof target must exactly match verification.version_or_commit")
    if status == "verified":
        if proof_executed is not True or proof_passed is not True:
            errors.append("verification.status verified requires executed and passing resource_proof")
        if isinstance(unavailable_claims, list) and unavailable_claims:
            errors.append("verification.status verified cannot have material resource_proof.unavailable_claims")
    if status == "unavailable":
        if not isinstance(unavailable_claims, list) or not unavailable_claims:
            errors.append("verification.status unavailable requires at least one resource_proof.unavailable_claims entry")
        if proof_passed is True:
            errors.append("verification.status unavailable cannot have resource_proof.passed: true")
    if status == "failed" and proof_passed is True:
        errors.append("verification.status failed cannot have resource_proof.passed: true")
    if proof_passed is True and status not in {"verified"}:
        errors.append("passing overall resource_proof requires verification.status: verified")

    reconciliation_status = dotted_get(data, "reconciliation.status")
    reconciliation_checked = dotted_get(data, "reconciliation.checked_at")
    installed_identity = dotted_get(data, "reconciliation.installed_identity")
    installed_version = dotted_get(data, "reconciliation.installed_version_or_commit")
    detection_method = dotted_get(data, "reconciliation.detection_method")
    parent_sources = dotted_get(data, "reconciliation.parent_state_sources")
    reconciliation_result = dotted_get(data, "reconciliation.result")
    if isinstance(reconciliation_status, str) and reconciliation_status not in ALLOWED_RECONCILIATION:
        errors.append("reconciliation.status must be matched, mismatched, blocked, unknown, or not-applicable")
    if isinstance(reconciliation_checked, str) and reconciliation_checked.strip():
        errors.extend(validate_date(reconciliation_checked.strip(), field="reconciliation.checked_at"))
    if reconciliation_status in {"matched", "mismatched", "blocked", "not-applicable"}:
        if not nonempty_string(reconciliation_checked):
            errors.append(f"reconciliation.status {reconciliation_status!r} requires reconciliation.checked_at")
        if not nonempty_string(detection_method):
            errors.append(f"reconciliation.status {reconciliation_status!r} requires reconciliation.detection_method")
        if not nonempty_string(reconciliation_result):
            errors.append(f"reconciliation.status {reconciliation_status!r} requires reconciliation.result")
    if reconciliation_status == "matched":
        if not nonempty_string(installed_identity):
            errors.append("matched reconciliation requires reconciliation.installed_identity")
        if not nonempty_string(installed_version):
            errors.append("matched reconciliation requires reconciliation.installed_version_or_commit")
        if not isinstance(parent_sources, list) or not parent_sources:
            errors.append("matched reconciliation requires reconciliation.parent_state_sources")
    if reconciliation_status == "mismatched" and not (
        nonempty_string(installed_identity) or nonempty_string(installed_version)
    ):
        errors.append("mismatched reconciliation must record an observed installed identity or version/state")
    if reconciliation_status == "blocked" and not nonempty_string(data.get("blocked_use_or_version")):
        errors.append("blocked reconciliation requires blocked_use_or_version")

    structural = dotted_get(data, "skill_validation.structural_passed")
    independent_executed = dotted_get(data, "skill_validation.independent_behavioral_executed")
    independent_passed = dotted_get(data, "skill_validation.independent_behavioral_passed")
    skill_environment = dotted_get(data, "skill_validation.environment")
    skill_result = dotted_get(data, "skill_validation.result")
    if independent_passed is True and independent_executed is not True:
        errors.append("independent_behavioral_passed cannot be true unless independent_behavioral_executed is true")
    if independent_executed is True:
        if not nonempty_string(skill_environment):
            errors.append("executed independent behavioral validation must record skill_validation.environment")
        if not nonempty_string(skill_result):
            errors.append("executed independent behavioral validation must record skill_validation.result")

    _validate_skill_checks(
        data,
        errors,
        notes,
        current_skill_root=current_skill_root.resolve() if current_skill_root else None,
        require_current_evidence=require_current_evidence,
    )

    catalog_status = dotted_get(data, "skill_validation.catalog_routing_status")
    catalog_fingerprint = dotted_get(data, "skill_validation.catalog_fingerprint")
    catalog_environment = dotted_get(data, "skill_validation.catalog_environment")
    catalog_result = dotted_get(data, "skill_validation.catalog_result")
    if isinstance(catalog_status, str) and catalog_status not in ALLOWED_CATALOG_ROUTING:
        errors.append("skill_validation.catalog_routing_status must be not-applicable, unverified, verified, unavailable, or failed")
    if nonempty_string(catalog_fingerprint) and not FINGERPRINT_RE.fullmatch(catalog_fingerprint.strip()):
        errors.append("skill_validation.catalog_fingerprint must use sha256:<64 lowercase hex characters>")
    if catalog_status in {"verified", "unavailable", "failed"}:
        if not nonempty_string(catalog_fingerprint):
            errors.append(f"catalog routing status {catalog_status!r} requires skill_validation.catalog_fingerprint")
        if not nonempty_string(catalog_environment):
            errors.append(f"catalog routing status {catalog_status!r} requires skill_validation.catalog_environment")
        if not nonempty_string(catalog_result):
            errors.append(f"catalog routing status {catalog_status!r} requires skill_validation.catalog_result")

    host_adoptions = data.get("host_adoptions")
    if not isinstance(host_adoptions, list):
        errors.append("host_adoptions must be a list")
        host_adoptions = []
    seen_host_targets: set[tuple[str, str, str]] = set()
    for index, adoption in enumerate(host_adoptions):
        prefix = f"host_adoptions[{index}]"
        if not isinstance(adoption, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        unknown_host_fields = sorted(set(adoption) - HOST_FIELDS)
        missing_host_fields = sorted(HOST_FIELDS - set(adoption))
        if unknown_host_fields:
            errors.append(f"{prefix} has unknown field(s): {', '.join(unknown_host_fields)}")
        if missing_host_fields:
            errors.append(f"{prefix} is missing field(s): {', '.join(missing_host_fields)}")
        for field in ("host", "scope", "location", "status", "checked_at", "result"):
            if not nonempty_string(adoption.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
        scope = adoption.get("scope")
        host_status = adoption.get("status")
        if isinstance(scope, str) and scope not in ALLOWED_HOST_SCOPES:
            errors.append(f"{prefix}.scope must be repo, user, admin, plugin, or other")
        if isinstance(host_status, str) and host_status not in ALLOWED_HOST_STATUSES:
            errors.append(f"{prefix}.status must be installed, operational, blocked, disabled, removed, unavailable, or failed")
        checked_at = adoption.get("checked_at")
        if isinstance(checked_at, str) and checked_at.strip():
            errors.extend(validate_date(checked_at.strip(), field=f"{prefix}.checked_at"))
        target = tuple(str(adoption.get(field, "")).strip().lower() for field in ("host", "scope", "location"))
        if target in seen_host_targets:
            errors.append(f"duplicate host adoption target at {prefix}")
        seen_host_targets.add(target)

        evidence = adoption.get("evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{prefix}.evidence must be a mapping")
            continue
        evidence_unknown = sorted(set(evidence) - HOST_EVIDENCE_FIELDS)
        evidence_missing = sorted(HOST_EVIDENCE_FIELDS - set(evidence))
        if evidence_unknown:
            errors.append(f"{prefix}.evidence has unknown field(s): {', '.join(evidence_unknown)}")
        if evidence_missing:
            errors.append(f"{prefix}.evidence is missing field(s): {', '.join(evidence_missing)}")
        installed = evidence.get("installed")
        registered = evidence.get("registered")
        discoverable = evidence.get("discoverable")
        enabled = evidence.get("enabled")
        activation = evidence.get("explicit_activation")
        if installed not in ALLOWED_PRESENCE:
            errors.append(f"{prefix}.evidence.installed has an invalid state")
        if registered not in ALLOWED_PRESENCE:
            errors.append(f"{prefix}.evidence.registered has an invalid state")
        if discoverable not in ALLOWED_DISCOVERY:
            errors.append(f"{prefix}.evidence.discoverable has an invalid state")
        if enabled not in ALLOWED_ENABLED:
            errors.append(f"{prefix}.evidence.enabled has an invalid state")
        if activation not in ALLOWED_ACTIVATION:
            errors.append(f"{prefix}.evidence.explicit_activation has an invalid state")

        if host_status == "operational":
            if installed not in {"present", "not-applicable"}:
                errors.append(f"{prefix} operational requires installed present or not-applicable")
            if registered not in {"present", "not-applicable"}:
                errors.append(f"{prefix} operational requires registered present or not-applicable")
            if discoverable != "yes":
                errors.append(f"{prefix} operational requires discoverable: yes")
            if enabled not in {"yes", "not-applicable"}:
                errors.append(f"{prefix} operational requires enabled yes or not-applicable")
            if activation != "passed":
                errors.append(f"{prefix} operational requires explicit_activation: passed")
        elif host_status == "installed" and installed != "present":
            errors.append(f"{prefix} installed status requires evidence.installed: present")
        elif host_status == "blocked" and installed not in {"present", "not-applicable"}:
            errors.append(f"{prefix} blocked status requires installed present or not-applicable")
        elif host_status == "disabled" and enabled != "no":
            errors.append(f"{prefix} disabled status requires evidence.enabled: no")
        elif host_status == "removed" and installed != "absent":
            errors.append(f"{prefix} removed status requires evidence.installed: absent")
        elif host_status == "unavailable" and not (
            "unknown" in {installed, registered, discoverable, enabled} or activation == "unavailable"
        ):
            errors.append(f"{prefix} unavailable status requires unknown or unavailable evidence")
        elif host_status == "failed" and not (
            activation == "failed" or installed == "absent" or registered == "absent" or discoverable == "no"
        ):
            errors.append(f"{prefix} failed status requires a failed/negative evidence facet")

    generated_skill = data.get("generated_skill")
    if any(value is True for value in (structural, independent_executed, independent_passed)) and not nonempty_string(generated_skill):
        errors.append("skill validation evidence requires generated_skill to identify the generated skill")
    if not nonempty_string(generated_skill):
        if host_adoptions:
            errors.append("host_adoptions require generated_skill to identify the adopted generated child")
        if catalog_status in {"verified", "unavailable", "failed"} or any(
            nonempty_string(value) for value in (catalog_fingerprint, catalog_environment, catalog_result)
        ):
            errors.append("catalog routing evidence requires generated_skill to identify the generated child")

    if trust_basis == "verified-acquisition" and status != "verified":
        errors.append("verified-acquisition requires verification.status: verified")

    if trust_basis == "curated":
        if not nonempty_string(slug):
            errors.append("curated records must carry the curated slug")
        if not nonempty_string(canonical):
            errors.append("curated records must carry canonical_url so trust cannot drift to a same-named resource")
        if status == "unverified":
            notes.append("curated + trusted + unverified is valid; curation establishes trust, not runtime verification")

    if status == "failed":
        if trust_level == "trusted" and not nonempty_string(data.get("blocked_use_or_version")):
            errors.append("failed trusted records must identify blocked_use_or_version without revoking policy trust")
        elif trust_level == "untrusted" and not nonempty_string(data.get("rejection_reason")):
            notes.append("failed untrusted record has no rejection_reason yet; acceptable during investigation, but record one before final rejection")

    return errors, notes


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a portable Roblox resource evidence record for structural and lifecycle state consistency."
    )
    parser.add_argument("resource_record", type=Path, help="resource-record YAML file")
    parser.add_argument(
        "--current-skill",
        type=Path,
        help="generated skill root; enables strict current structured-evidence and input-hash checks",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = args.resource_record.resolve()
    if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml"}:
        print(f"FAIL\n- expected an existing .yaml/.yml resource record: {path}")
        return 1
    try:
        data = load_record(path)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"FAIL\n- {exc}")
        return 1

    current_skill = args.current_skill.resolve() if args.current_skill else None
    if current_skill is not None and not (current_skill / "SKILL.md").is_file():
        print(f"FAIL\n- --current-skill must contain SKILL.md: {current_skill}")
        return 1
    errors, notes = validate_record(
        path,
        data,
        current_skill_root=current_skill,
        require_current_evidence=current_skill is not None,
    )
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        for note in notes:
            print(f"NOTE: {note}")
        return 1

    print("PASS: resource-record structural/state checks passed")
    for note in notes:
        print(f"NOTE: {note}")
    print("NOTE: this does not prove source truth, resource behavior, project-use correctness, or generated-skill behavior; it only checks that the recorded state is internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
