from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

import fixtures
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_resource_record import load_record, validate_record
from validate_skill import validate_skill
from validate_skill_catalog import collect_skill_directories, validate_catalog


class ResourceRecordTests(unittest.TestCase):
    def validate(self, record: dict) -> tuple[list[str], list[str]]:
        return validate_record(Path("record.yaml"), record)

    def test_artifact_only_v3_record_passes(self) -> None:
        errors, _ = self.validate(fixtures.valid_record())
        self.assertEqual(errors, [])

    def test_project_use_adopted_requires_role_scope_authority_and_trust(self) -> None:
        record = fixtures.valid_record()
        record["project_use"] = {
            "status": "adopted",
            "role": "persistent player data",
            "scope": "project",
            "authority": "roblox-resource-acquisition",
        }
        errors, _ = self.validate(record)
        self.assertEqual(errors, [])

        for field in ("role", "scope", "authority"):
            broken = fixtures.valid_record()
            broken["project_use"] = {
                "status": "adopted",
                "role": "persistent player data",
                "scope": "project",
                "authority": "roblox-resource-acquisition",
            }
            broken["project_use"][field] = ""
            errors, _ = self.validate(broken)
            self.assertIn(
                f"project_use.status 'adopted' requires project_use.{field}",
                errors,
            )

        record["trust"] = {"level": "untrusted", "basis": "", "reason": ""}
        errors, _ = self.validate(record)
        self.assertIn("project_use.status adopted requires trust.level: trusted", errors)

    def test_not_applicable_project_use_must_not_carry_project_authority(self) -> None:
        record = fixtures.valid_record()
        record["project_use"]["authority"] = "structure-roblox-projects"
        errors, _ = self.validate(record)
        self.assertIn(
            "project_use.status not-applicable requires empty role, scope, and authority",
            errors,
        )

    def test_retired_project_use_preserves_prior_role_and_authority(self) -> None:
        record = fixtures.valid_record()
        record["project_use"] = {
            "status": "retired",
            "role": "persistent player data",
            "scope": "project",
            "authority": "roblox-resource-acquisition",
        }
        errors, _ = self.validate(record)
        self.assertEqual(errors, [])

    def test_direct_evaluation_target_preserves_provenance_without_trust(self) -> None:
        record = fixtures.valid_record()
        record["discovery_origin"] = "other"
        record["selection_reason"] = "User directly targeted this canonical resource for evaluation only."
        record["trust"] = {"level": "untrusted", "basis": "", "reason": ""}
        errors, _ = self.validate(record)
        self.assertEqual(errors, [])

        record["selection_reason"] = ""
        errors, _ = self.validate(record)
        self.assertIn(
            "discovery_origin other requires selection_reason to preserve selection provenance",
            errors,
        )

    def test_direct_use_target_can_record_explicit_user_trust_separately(self) -> None:
        record = fixtures.valid_record()
        record["discovery_origin"] = "other"
        record["selection_reason"] = "User directly selected this canonical resource for current-task use."
        record["trust"] = {
            "level": "trusted",
            "basis": "explicit-user",
            "reason": "The user directed use of the established canonical identity.",
        }
        errors, _ = self.validate(record)
        self.assertEqual(errors, [])

        record["slug"] = ""
        record["canonical_url"] = ""
        record["package_id"] = ""
        errors, _ = self.validate(record)
        self.assertIn(
            "trusted records require slug to bind trust to a stable identity",
            errors,
        )
        self.assertIn(
            "trusted records require canonical_url or package_id to bind trust to canonical identity",
            errors,
        )

    def test_operational_adoption_requires_every_facet(self) -> None:
        record = fixtures.valid_record()
        record["host_adoptions"] = [fixtures.operational_adoption()]
        errors, _ = self.validate(record)
        self.assertEqual(errors, [])
        record["host_adoptions"][0]["evidence"]["explicit_activation"] = "not-run"
        errors, _ = self.validate(record)
        self.assertTrue(any("explicit_activation: passed" in error for error in errors))

    def test_blocked_disabled_and_removed_states(self) -> None:
        for status, evidence_field, evidence_value in (
            ("blocked", "installed", "present"),
            ("disabled", "enabled", "no"),
            ("removed", "installed", "absent"),
        ):
            record = fixtures.valid_record()
            adoption = fixtures.operational_adoption()
            adoption["status"] = status
            adoption["evidence"][evidence_field] = evidence_value
            record["host_adoptions"] = [adoption]
            errors, _ = self.validate(record)
            self.assertEqual(errors, [], (status, errors))

    def test_reconciliation_mismatch_requires_observed_state(self) -> None:
        record = fixtures.valid_record()
        record["reconciliation"].update(
            {
                "status": "mismatched",
                "checked_at": "2026-08-16",
                "detection_method": "Read project package manifest",
                "result": "Installed state differs",
            }
        )
        errors, _ = self.validate(record)
        self.assertTrue(any("observed installed identity or version" in error for error in errors))

    def test_schema_v2_record_is_rejected(self) -> None:
        record = fixtures.valid_record()
        record["schema_version"] = 2
        errors, _ = self.validate(record)
        self.assertIn("schema_version must be integer 3; older records must enter repair/reconcile", errors)

    def test_yaml_loader_rejects_old_schema_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "old.yaml"
            old = fixtures.valid_record()
            old["schema_version"] = 2
            path.write_text(yaml.safe_dump(old, sort_keys=False), encoding="utf-8")
            loaded = load_record(path)
            errors, _ = validate_record(path, loaded)
            self.assertTrue(errors)

    def test_yaml_loader_normalizes_yes_no_host_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "operational.yaml"
            record = fixtures.valid_record()
            record["host_adoptions"] = [fixtures.operational_adoption()]
            dumped = yaml.safe_dump(record, sort_keys=False).replace(
                "discoverable: 'yes'", "discoverable: yes"
            ).replace("enabled: 'yes'", "enabled: yes")
            path.write_text(dumped, encoding="utf-8")
            loaded = load_record(path)
            errors, _ = validate_record(path, loaded)
            self.assertEqual(errors, [])
