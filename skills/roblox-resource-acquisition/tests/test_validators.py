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


class GeneratedSkillTests(unittest.TestCase):
    def write_child(self, root: Path, name: str, description: str, use_when: str) -> Path:
        skill = root / name
        skill.mkdir(parents=True)
        skill.joinpath("SKILL.md").write_text(
            fixtures.valid_skill_text(name=name, description=description, use_when=use_when),
            encoding="utf-8",
        )
        return skill

    def make_conditional(self, skill: Path) -> None:
        path = skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "Policy: required — project package manifests can select a different materially version-sensitive release.",
            "Policy: conditional — the declared pin and lock identify healthy ordinary use while installed integrity can still drift.",
        ).replace(
            "Expected identity/state: widget-resource + https://example.com/widget + com.example.widget + 1.2.3.\n",
            "Expected identity/state: widget-resource + https://example.com/widget + com.example.widget + 1.2.3.\n"
            "- Integrity gate: Run `lute run scripts/verify.luau` before completing the task; pass when it prints `[verify] PASS` and exits with code `0`.\n"
            "- Escalation triggers: Escalate for a missing or mismatched pin/lock, adoption or upgrade, authorized repair, verifier failure or drift, a hard defect, or an already-known block.\n",
        ).replace(
            "Mismatch/unknown action: Stop the affected version-sensitive use and invoke `roblox-resource-acquisition` in `repair/reconcile` mode.",
            "Mismatch/unknown action: For every state escalation trigger, stop the affected version-sensitive use, perform the Parent-state check, and invoke `roblox-resource-acquisition` in `repair/reconcile` mode before continuing.",
        )
        path.write_text(text, encoding="utf-8")

    def test_valid_reconciliation_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            errors, _ = validate_skill(skill)
            self.assertEqual(errors, [])

    def test_repair_interrupt_rejects_silent_workaround_absorption(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8").replace(
                "Soft defect: If the workaround is safe and reversible, immediate work may continue, but invoke parent repair diagnosis and surface the reproduction, workaround, and durable correction before completion.",
                "Soft defect: If a workaround succeeds, continue the immediate task and do not interrupt delivery.",
            )
            path.write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertTrue(any("Repair interrupt Soft defect" in error for error in errors))

    def test_repair_interrupt_requires_parent_activation_and_hard_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8").replace(
                "Invoke `roblox-resource-acquisition` in `repair/reconcile` mode",
                "Note the issue locally",
                1,
            ).replace(
                "stop dependent work and enter parent reconciliation and repair before continuing",
                "continue carefully and mention the risk later",
                1,
            )
            path.write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertTrue(any("Repair interrupt Trigger" in error for error in errors))
            self.assertTrue(any("Repair interrupt Hard defect" in error for error in errors))

    def test_repair_interrupt_must_precede_common_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            match = re.search(
                r"^## Repair interrupt\s*$.*?(?=^## |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(match)
            repair = match.group(0)
            text = text[: match.start()] + text[match.end() :]
            marker = "## Operational reconciliation"
            text = text.replace(marker, repair + "\n" + marker, 1)
            path.write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertIn("generated skills must place Repair interrupt before Common path", errors)

    def test_parent_state_check_requires_discovery_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            concrete = (
                "Parent-state check: Resolve the affected Roblox project root, then read the matching schema-version 3 resource record at `.agents/roblox/resources/records/widget-resource.yaml` and resource-bound learnings from `.agents/roblox/resources/learnings/` relative to it; when no project root applies, use `~/.roblox-resources/records/widget-resource.yaml` and `~/.roblox-resources/learnings/`. Match by slug plus canonical identity."
            )
            weak = (
                "Parent-state check: Load matching schema-version 3 resource records and resource-bound learnings by slug plus canonical identity."
            )
            path.write_text(text.replace(concrete, weak), encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertIn(
                "Parent-state check must name a concrete record/learnings discovery route",
                errors,
            )

    def test_missing_operational_reconciliation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            text = skill.joinpath("SKILL.md").read_text(encoding="utf-8")
            text = re.sub(
                r"^## Operational reconciliation\s*$.*?(?=^## |\Z)",
                "",
                text,
                count=1,
                flags=re.MULTILINE | re.DOTALL,
            )
            skill.joinpath("SKILL.md").write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertTrue(any("Operational reconciliation" in error for error in errors))

    def test_conditional_reconciliation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            self.make_conditional(skill)
            errors, _ = validate_skill(skill)
            self.assertEqual(errors, [])

    def test_conditional_reconciliation_requires_fast_path_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for missing_label in ("Integrity gate", "Escalation triggers"):
                with self.subTest(missing_label=missing_label):
                    skill = self.write_child(
                        root,
                        f"roblox-widget-{missing_label.split()[0].lower()}",
                        "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                        "- Synchronizing replicated widget state across server-owned sessions.",
                    )
                    self.make_conditional(skill)
                    path = skill / "SKILL.md"
                    text = path.read_text(encoding="utf-8")
                    text = re.sub(rf"^- {re.escape(missing_label)}:.*\n", "", text, count=1, flags=re.MULTILINE)
                    path.write_text(text, encoding="utf-8")
                    errors, _ = validate_skill(skill)
                    self.assertIn(
                        f"conditional reconciliation is missing labeled field: {missing_label}",
                        errors,
                    )

    def test_conditional_reconciliation_rejects_weak_fast_path_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            self.make_conditional(skill)
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8").replace(
                "Integrity gate: Run `lute run scripts/verify.luau` before completing the task; pass when it prints `[verify] PASS` and exits with code `0`.",
                "Integrity gate: Check the verifier later.",
            ).replace(
                "Escalation triggers: Escalate for a missing or mismatched pin/lock, adoption or upgrade, authorized repair, verifier failure or drift, a hard defect, or an already-known block.",
                "Escalation triggers: Escalate when something seems wrong.",
            )
            path.write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertTrue(any("conditional Integrity gate" in error for error in errors))
            self.assertTrue(any("conditional Escalation triggers" in error for error in errors))

    def test_conditional_reconciliation_requires_identity_parent_route_and_repair_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            self.make_conditional(skill)
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            for label in ("Expected identity/state", "Parent-state check", "Defect handoff"):
                text = re.sub(rf"^- {re.escape(label)}:.*\n", "", text, count=1, flags=re.MULTILINE)
            path.write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            for label in ("Expected identity/state", "Parent-state check", "Defect handoff"):
                self.assertIn(
                    f"Operational reconciliation is missing labeled field: {label}",
                    errors,
                )

    def test_conditional_reconciliation_requires_every_trigger_to_use_parent_repair_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            self.make_conditional(skill)
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8").replace(
                "Mismatch/unknown action: For every state escalation trigger, stop the affected version-sensitive use, perform the Parent-state check, and invoke `roblox-resource-acquisition` in `repair/reconcile` mode before continuing.",
                "Mismatch/unknown action: Stop mismatched version use and invoke `roblox-resource-acquisition` in `repair/reconcile` mode.",
            )
            path.write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertTrue(any("every state escalation trigger" in error for error in errors))

    def test_immutable_not_applicable_reconciliation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                "Policy: required — project package manifests can select a different materially version-sensitive release.",
                "Policy: not-applicable — installation is pinned to the exact immutable reviewed package version.",
            ).replace(
                "Installed-state check: Inspect the project package manifest and read the `com.example.widget` version before requiring the module.",
                "Installed-state check: The package lockfile is pinned to the exact immutable `com.example.widget` version `1.2.3`.",
            ).replace(
                "Current-block check: Before affected use, run `python ~/.agents/skills/roblox-resource-acquisition/scripts/check_resource_status.py --pair .agents/skills/roblox-widget-resource .agents/roblox/resources/records/widget-resource.yaml`; proceed only on HEALTHY, and enter full parent-state reconciliation on BLOCKED or UNKNOWN.",
                "Current-block check: not-applicable — the package lockfile is pinned to the exact immutable reviewed package version.",
            )
            path.write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertEqual(errors, [])

    def test_missing_identity_and_weak_reconciliation_fields_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = self.write_child(
                Path(temp),
                "roblox-widget-resource",
                "Use Widget Resource for synchronized widget replication with deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget state across server-owned sessions.",
            )
            path = skill / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace("- Resource slug: widget-resource\n", "")
            text = text.replace(
                "Installed-state check: Inspect the project package manifest and read the `com.example.widget` version before requiring the module.",
                "Installed-state check: Review project state generally.",
            )
            text = text.replace(
                "Mismatch/unknown action: Stop the affected version-sensitive use and invoke `roblox-resource-acquisition` in `repair/reconcile` mode.",
                "Mismatch/unknown action: Continue cautiously and mention the difference later.",
            )
            text = text.replace(
                "Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth for evidence and parent activation.",
                "Defect handoff: Mention the problem in the final response.",
            )
            path.write_text(text, encoding="utf-8")
            errors, _ = validate_skill(skill)
            self.assertTrue(any("Resource slug" in error for error in errors))
            self.assertTrue(any("Installed-state check" in error for error in errors))
            self.assertTrue(any("Mismatch/unknown action" in error for error in errors))
            self.assertTrue(any("Defect handoff" in error for error in errors))

    def test_catalog_duplicates_overlap_fingerprint_and_budget(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.write_child(
                root,
                "roblox-widget-one",
                "Use Widget One for synchronized replicated widget sessions and deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget sessions with deterministic cleanup.",
            )
            second = self.write_child(
                root,
                "roblox-widget-two",
                "Use Widget Two for synchronized replicated widget sessions and deterministic lifecycle cleanup.",
                "- Synchronizing replicated widget sessions with deterministic cleanup.",
            )
            roots = collect_skill_directories([root])
            errors, _, overlaps, fingerprint = validate_catalog(roots, host="portable")
            self.assertEqual(errors, [])
            self.assertTrue(overlaps)
            reversed_result = validate_catalog(list(reversed(roots)), host="portable")
            self.assertEqual(fingerprint, reversed_result[3])

            duplicate = self.write_child(
                root / "duplicates",
                "roblox-widget-one",
                "Use a distinct child for a completely different rendering capability.",
                "- Rendering local decorative particles for one player.",
            )
            errors, _, _, _ = validate_catalog([first, duplicate], host="portable")
            self.assertTrue(any("duplicate skill name" in error for error in errors))

            same_description = self.write_child(
                root,
                "roblox-widget-three",
                "Use Widget One for synchronized replicated widget sessions and deterministic lifecycle cleanup.",
                "- Rendering local decorative particles for one player.",
            )
            errors, _, _, _ = validate_catalog([first, same_description], host="portable")
            self.assertTrue(any("duplicate normalized description" in error for error in errors))

            long_description = "Use Long Catalog for " + "synchronized routing boundary " * 300
            long_child = self.write_child(
                root,
                "roblox-long-catalog",
                long_description,
                "- Synchronizing a deliberately large routing catalog fixture.",
            )
            _, warnings, _, _ = validate_catalog([long_child, second], host="codex")
            self.assertTrue(any("fallback budget" in warning for warning in warnings))

            unrelated = self.write_child(
                root,
                "roblox-particle-renderer",
                "Use Particle Renderer for decorative local visual bursts and camera-facing sprites.",
                "- Rendering decorative particles locally for one player's camera.",
            )
            errors, _, unrelated_overlaps, _ = validate_catalog([first, unrelated], host="portable")
            self.assertEqual(errors, [])
            self.assertEqual(unrelated_overlaps, [])

    def test_catalog_propagates_invalid_child(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            invalid = self.write_child(
                root,
                "roblox-invalid-child",
                "Use Invalid Child for a deliberately malformed catalog fixture.",
                "- Exercising invalid-child propagation through catalog validation.",
            )
            path = invalid / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            text = re.sub(
                r"^## Operational reconciliation\s*$.*?(?=^## |\Z)",
                "",
                text,
                count=1,
                flags=re.MULTILINE | re.DOTALL,
            )
            path.write_text(text, encoding="utf-8")

            errors, _, _, _ = validate_catalog([invalid], host="portable")
            self.assertTrue(any("Operational reconciliation" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
