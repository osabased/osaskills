from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import fixtures
import yaml


def _digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _write_child(root: Path) -> Path:
    child = root / "roblox-widget-resource"
    child.mkdir()
    (child / "SKILL.md").write_text(fixtures.valid_skill_text(), encoding="utf-8")
    return child


def _check(kind: str, fixture: Path, child: Path, *, check_id: str) -> dict:
    return {
        "check_id": check_id,
        "kind": kind,
        "execution_mode": "independent-agent",
        "status": "passed",
        "tested_at": "2026-09-18",
        "target_version_or_commit": "1.2.3",
        "inputs": [
            {
                "role": "fixture",
                "path": fixture.relative_to(child).as_posix(),
                "section": "",
                "sha256": _digest(fixture.read_bytes()),
            }
        ],
        "command": "lute run references/fixtures/widget-integration.luau",
        "result": "Fixture completed activation and cleanup assertions with exit code 0.",
        "artifact": "",
        "tested_child_sha256": "",
        "scope_fingerprint": "",
    }


def _executable_record(child: Path, fixture: Path) -> dict:
    record = fixtures.matching_widget_record()
    record["skill_validation"].update(
        {
            "independent_behavioral_executed": True,
            "independent_behavioral_passed": True,
            "environment": "fresh independent agent with executable fixture",
            "result": "Representative integration and teardown checks passed.",
            "claim_scope": "executable-integration",
            "checks": [
                _check("executable-integration", fixture, child, check_id="representative-integration"),
                _check("lifecycle-failure-cleanup", fixture, child, check_id="teardown-cancellation"),
            ],
        }
    )
    return record


def test_legacy_boolean_claim_is_readable_but_not_current(record_mod, tmp_path):
    child = _write_child(tmp_path)
    record = fixtures.matching_widget_record()
    record["skill_validation"].update(
        {
            "independent_behavioral_executed": True,
            "independent_behavioral_passed": True,
            "environment": "fresh-agent instruction-response runner",
            "result": "Read-only prompts followed the instructions.",
        }
    )

    errors, notes = record_mod.validate_record(Path("record.yaml"), record)
    assert errors == []
    assert any("legacy" in note for note in notes)

    errors, _ = record_mod.validate_record(
        Path("record.yaml"),
        record,
        current_skill_root=child,
        require_current_evidence=True,
    )
    assert any("legacy" in error for error in errors)


def test_advice_only_claim_needs_instruction_evidence_but_no_runtime_fixture(record_mod, tmp_path):
    child = _write_child(tmp_path)
    section = record_mod._section_bytes(child / "SKILL.md", "API used by this skill")
    assert section is not None
    record = fixtures.matching_widget_record()
    record["skill_validation"].update(
        {
            "independent_behavioral_executed": True,
            "independent_behavioral_passed": True,
            "environment": "fresh independent instruction-response agent",
            "result": "Agent chose the documented API without executable claims.",
            "claim_scope": "advice-only",
            "checks": [
                {
                    "check_id": "api-advice",
                    "kind": "instruction-response",
                    "execution_mode": "independent-agent",
                    "status": "passed",
                    "tested_at": "2026-09-18",
                    "target_version_or_commit": "1.2.3",
                    "inputs": [
                        {
                            "role": "api",
                            "path": "SKILL.md",
                            "section": "API used by this skill",
                            "sha256": _digest(section),
                        }
                    ],
                    "command": "",
                    "result": "Agent selected the three documented lifecycle calls.",
                    "artifact": "",
                    "tested_child_sha256": "",
                    "scope_fingerprint": "",
                }
            ],
        }
    )
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert errors == []

def test_executable_claim_rejects_instruction_only_evidence(record_mod, tmp_path):
    child = _write_child(tmp_path)
    record = fixtures.matching_widget_record()
    record["skill_validation"].update(
        {
            "independent_behavioral_executed": True,
            "independent_behavioral_passed": True,
            "environment": "fresh instruction-response agent",
            "result": "Prompts passed without running implementation.",
            "claim_scope": "executable-integration",
            "checks": [],
        }
    )
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert any("executable-integration independent_behavioral_passed" in error for error in errors)


def test_fixture_change_or_deletion_stales_current_claim_and_historical_remains_readable(record_mod, tmp_path):
    child = _write_child(tmp_path)
    fixture = child / "references" / "fixtures" / "widget-integration.luau"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("return 'integration-v1'\n", encoding="utf-8")
    record = _executable_record(child, fixture)

    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert errors == []

    fixture.write_text("return 'integration-v2'\n", encoding="utf-8")
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert any("input hash is stale" in error for error in errors)

    fixture.unlink()
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert any("current input is missing" in error for error in errors)

    historical = deepcopy(record)
    historical["skill_validation"].update(
        {
            "independent_behavioral_executed": False,
            "independent_behavioral_passed": False,
            "claim_scope": "unclaimed",
        }
    )
    for check in historical["skill_validation"]["checks"]:
        check["status"] = "historical"
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), historical, current_skill_root=child, require_current_evidence=True
    )
    assert errors == []


def test_historical_check_retains_original_target_after_record_upgrade(record_mod, tmp_path):
    child = _write_child(tmp_path)
    fixture = child / "references" / "fixtures" / "widget-integration.luau"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("return 'integration-v1'\n", encoding="utf-8")
    record = _executable_record(child, fixture)
    record["verification"]["version_or_commit"] = "2.0.0"
    record["skill_validation"].update(
        {
            "independent_behavioral_executed": False,
            "independent_behavioral_passed": False,
            "claim_scope": "unclaimed",
        }
    )
    for check in record["skill_validation"]["checks"]:
        check["status"] = "historical"

    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert errors == []


def test_malformed_structured_check_enums_return_errors_instead_of_raising(record_mod, tmp_path):
    child = _write_child(tmp_path)
    record = fixtures.matching_widget_record()
    record["skill_validation"].update(
        {
            "claim_scope": "unclaimed",
            "checks": [
                {
                    "check_id": "malformed-values",
                    "kind": [],
                    "execution_mode": {"bad": "mode"},
                    "status": ["passed"],
                    "tested_at": "2026-09-18",
                    "target_version_or_commit": "1.2.3",
                    "inputs": [
                        {
                            "role": {"bad": "role"},
                            "path": "SKILL.md",
                            "sha256": "sha256:" + "a" * 64,
                        }
                    ],
                    "result": "Malformed values must be reported.",
                }
            ],
        }
    )
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert any(".kind has an invalid value" in error for error in errors)
    assert any(".execution_mode has an invalid value" in error for error in errors)
    assert any(".status has an invalid value" in error for error in errors)
    assert any(".role has an invalid value" in error for error in errors)


def test_routing_evidence_recomputes_current_child_activation_metadata(record_mod, tmp_path):
    child = _write_child(tmp_path)
    activation_fingerprint = record_mod.compute_catalog_fingerprint([record_mod.load_catalog_skill(child)])
    record = fixtures.matching_widget_record()
    record["skill_validation"].update(
        {
            "catalog_routing_status": "verified",
            "catalog_fingerprint": activation_fingerprint,
            "catalog_environment": "single-child isolated routing surface",
            "catalog_result": "Independent explicit and implicit routing checks passed.",
            "claim_scope": "unclaimed",
            "checks": [
                {
                    "check_id": "routing-surface",
                    "kind": "routing",
                    "execution_mode": "independent-agent",
                    "status": "passed",
                    "tested_at": "2026-09-18",
                    "target_version_or_commit": "1.2.3",
                    "inputs": [
                        {
                            "role": "activation-metadata",
                            "path": "SKILL.md",
                            "sha256": activation_fingerprint,
                        }
                    ],
                    "result": "The intended child handled the scoped prompt.",
                    "scope_fingerprint": activation_fingerprint,
                }
            ],
        }
    )
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert errors == []

    skill = child / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(
            "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
            "Use Widget Resource for local-only widget formatting and deterministic lifecycle cleanup.",
        ),
        encoding="utf-8",
    )
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert any("activation metadata hash is stale" in error for error in errors)

def test_unrelated_child_edit_does_not_stale_fixture_bound_evidence(record_mod, tmp_path):
    child = _write_child(tmp_path)
    fixture = child / "references" / "fixtures" / "widget-integration.luau"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("return 'integration-v1'\n", encoding="utf-8")
    record = _executable_record(child, fixture)
    skill = child / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8").replace(
        "Does not replace server-side validation", "Still requires server-side validation"
    ), encoding="utf-8")
    errors, _ = record_mod.validate_record(
        Path("record.yaml"), record, current_skill_root=child, require_current_evidence=True
    )
    assert errors == []


def test_status_query_healthy_legacy_block_unknown_and_never_executes_evidence(status_mod, tmp_path):
    child = _write_child(tmp_path)
    record = fixtures.matching_widget_record()
    record["reconciliation"]["status"] = "matched"
    sentinel = tmp_path / "must-not-exist"
    record["skill_validation"]["checks"] = [
        {
            "check_id": "untrusted-command-text",
            "kind": "instruction-response",
            "execution_mode": "command",
            "status": "historical",
            "tested_at": "2026-09-18",
            "target_version_or_commit": "1.2.3",
            "inputs": [],
            "command": f"write forbidden output to {sentinel}",
            "result": "Historical prose only.",
            "artifact": "",
            "tested_child_sha256": "",
            "scope_fingerprint": "",
        }
    ]
    record_path = tmp_path / "record.yaml"
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    result = status_mod.query_pair(child, record_path)
    assert result["status"] == "healthy"
    assert not sentinel.exists()

    record["blocked_use_or_version"] = "Cleanup is unsafe for this selected state."
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    assert status_mod.query_pair(child, record_path)["status"] == "blocked"

    record["blocked_use_or_version"] = ""
    record["verification"]["version_or_commit"] = "9.9.9"
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    assert status_mod.query_pair(child, record_path)["status"] == "unknown"
    assert status_mod.query_pair(child, tmp_path / "missing.yaml")["status"] == "unknown"


def test_status_query_rejects_malformed_block_unknown_state_failed_verification_and_honors_host_block(status_mod, tmp_path):
    child = _write_child(tmp_path)
    record = fixtures.matching_widget_record()
    record_path = tmp_path / "record.yaml"

    record["blocked_use_or_version"] = {"reason": "must not be ignored"}
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    assert status_mod.query_pair(child, record_path)["status"] == "unknown"

    record = fixtures.matching_widget_record()
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    assert status_mod.query_pair(child, record_path)["status"] == "unknown"

    record["reconciliation"]["status"] = "matched"
    record["verification"]["status"] = "failed"
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    assert status_mod.query_pair(child, record_path)["status"] == "unknown"

    record = fixtures.matching_widget_record()
    adoption = fixtures.operational_adoption()
    adoption["location"] = str(child / "SKILL.md")
    adoption["status"] = "blocked"
    adoption["result"] = "Current host activation is blocked by cleanup regression."
    record["host_adoptions"] = [adoption]
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    result = status_mod.query_pair(child, record_path)
    assert result["status"] == "blocked"
    assert "cleanup regression" in result["reason"]


def test_status_query_malformed_state_types_and_adverse_host_states_are_unknown(status_mod, tmp_path):
    child = _write_child(tmp_path)
    record_path = tmp_path / "record.yaml"
    for field, malformed in (("verification", []), ("reconciliation", {"bad": "state"})):
        record = fixtures.matching_widget_record()
        record["reconciliation"]["status"] = "matched"
        record[field]["status"] = malformed
        record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
        assert status_mod.query_pair(child, record_path)["status"] == "unknown"

    for malformed in ([], {"bad": "state"}):
        record = fixtures.matching_widget_record()
        record["reconciliation"]["status"] = "matched"
        adoption = fixtures.operational_adoption()
        adoption["location"] = str(child)
        adoption["status"] = malformed
        record["host_adoptions"] = [adoption]
        record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
        assert status_mod.query_pair(child, record_path)["status"] == "unknown"

    for adverse in ("disabled", "removed", "failed", "unavailable"):
        record = fixtures.matching_widget_record()
        record["reconciliation"]["status"] = "matched"
        adoption = fixtures.operational_adoption()
        adoption["location"] = str(child)
        adoption["status"] = adverse
        record["host_adoptions"] = [adoption]
        record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
        result = status_mod.query_pair(child, record_path)
        assert result["status"] == "unknown"
        assert adverse in result["reason"]


def test_status_cli_batches_pairs_and_returns_nonzero_for_block(status_mod, tmp_path, capsys):
    child = _write_child(tmp_path)
    healthy = fixtures.matching_widget_record()
    healthy["reconciliation"]["status"] = "matched"
    blocked = deepcopy(healthy)
    blocked["blocked_use_or_version"] = "All uses of this selected record are blocked."
    healthy_path = tmp_path / "healthy.yaml"
    blocked_path = tmp_path / "blocked.yaml"
    healthy_path.write_text(yaml.safe_dump(healthy, sort_keys=False), encoding="utf-8")
    blocked_path.write_text(yaml.safe_dump(blocked, sort_keys=False), encoding="utf-8")
    code = status_mod.main(
        [
            "--pair", str(child), str(healthy_path),
            "--pair", str(child), str(blocked_path),
            "--json",
        ]
    )
    assert code == 1
    output = json.loads(capsys.readouterr().out)
    assert [item["status"] for item in output] == ["healthy", "blocked"]


def test_status_cli_real_process_reports_unknown_and_exit_two(tmp_path, scripts_dir):
    child = _write_child(tmp_path)
    record = fixtures.matching_widget_record()
    record["reconciliation"]["status"] = "matched"
    record["blocked_use_or_version"] = {"reason": "malformed block must stop use"}
    record_path = tmp_path / "record.yaml"
    record_path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(scripts_dir / "check_resource_status.py"),
            "--pair",
            str(child),
            str(record_path),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    output = json.loads(completed.stdout)
    assert output[0]["status"] == "unknown"
    assert "must be a string" in output[0]["reason"]


def test_child_contract_rejects_missing_block_query_and_unowned_pending_work(skill_mod, tmp_path):
    child = _write_child(tmp_path)
    skill = child / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    text = text.replace(
        "- Current-block check: Before affected use, run `python ~/.agents/skills/roblox-resource-acquisition/scripts/check_resource_status.py --pair .agents/skills/roblox-widget-resource .agents/roblox/resources/records/widget-resource.yaml`; proceed only on HEALTHY, and enter full parent-state reconciliation on BLOCKED or UNKNOWN.\n",
        "",
    ).replace(
        "- Cleanup/destruction: Invalidate or cancel pending waits and spawned tasks, then call the documented destroy method when the owning system stops.",
        "- Cleanup/destruction: Call the documented destroy method eventually.",
    )
    skill.write_text(text, encoding="utf-8")
    errors, _ = skill_mod.validate_skill(child)
    assert any("Current-block check" in error for error in errors)
    assert any("pending wait/task" in error for error in errors)
