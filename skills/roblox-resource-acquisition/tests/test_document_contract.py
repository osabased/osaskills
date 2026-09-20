"""Regression checks for the parent router and internal document navigation."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PARENT = (ROOT / "SKILL.md").read_text(encoding="utf-8")
REFERENCES = {
    path.name: path.read_text(encoding="utf-8")
    for path in (ROOT / "references").glob("*.md")
}


def _mode(name: str) -> str:
    match = re.search(
        rf"^### `{re.escape(name)}`\n(.*?)(?=^### `|^## Shared invariants)",
        PARENT,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing parent mode {name!r}"
    return match.group(1)


def _anchor(text: str) -> str:
    text = re.sub(r"[`*_~]", "", text.strip().lower())
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def _anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not match:
            continue
        base = _anchor(match.group(1))
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def test_relative_markdown_links_and_anchors_resolve():
    files = [
        ROOT / "SKILL.md",
        *(ROOT / "references").glob("*.md"),
        *(ROOT / "templates").glob("*.md"),
    ]
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for source in files:
        for target in link_re.findall(source.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("mailto:"):
                continue
            path_part, _, anchor = target.partition("#")
            target_path = source if not path_part else (source.parent / path_part).resolve()
            assert target_path.is_file(), f"{source}: missing link target {target}"
            if anchor:
                assert anchor in _anchors(target_path), f"{source}: missing anchor {target}"


def test_evaluate_compare_stops_before_integration_and_generation():
    section = _mode("evaluate/compare")
    assert "qualification-workflow.md" in section
    assert "evaluation-rubric.md" in section
    assert section.index("hard gates") < section.index("scoring")
    assert "state-policy.md" in section
    assert "Integration/project mutation" in section
    assert "child generation or validation" in section
    assert "operational host adoption" in section


def test_acquire_adopt_routes_project_state_and_keeps_child_adoption_conditional():
    section = _mode("acquire/adopt")
    assert "project-adoption.md" in section
    assert "When reusable child guidance is in scope" in section
    assert "generation-validation.md" in section
    assert "When operational host adoption of generated guidance is requested" in section
    assert "operational-lifecycle.md" in section
    assert "state-policy.md" in section
    assert "Report five statuses separately" in section
    assert "not applicable" in section


def test_portable_record_location_has_one_canonical_owner():
    state = REFERENCES["state-policy.md"]
    operational = REFERENCES["operational-lifecycle.md"]

    explicit = "an explicit record path supplied by the user, project, or environment"
    project = "`<project-root>/.agents/roblox/resources/records/<slug>.yaml`"
    user = "`~/.roblox-resources/records/<slug>.yaml`"
    positions = [state.index(explicit), state.index(project), state.index(user)]
    assert positions == sorted(positions)

    assert (
        "[portable resource-record location](state-policy.md#portable-resource-record-location)"
        in operational
    )
    assert project not in operational
    assert user not in operational


def test_refresh_preserves_authority_and_target_bound_proof():
    section = _mode("refresh")
    assert "externally owned target" in section
    assert "Prior runtime proof remains bound to its recorded target" in section
    assert "actual installed state" in section
    assert "recorded state" in section
    assert "List the inputs that changed" in section
    assert "Rerun only proof invalidated" in section
    assert "project-adoption.md" in section
    assert "repair-loop.md" in section


def test_repair_reconcile_keeps_upstream_and_child_revalidation_conditional():
    section = _mode("repair/reconcile")
    assert "project-adoption.md" in section
    assert "qualification-workflow.md" in section
    assert "when upstream identity, source facts, qualification, trust, or a hard security boundary is in question" in section
    assert "generation-validation.md" in section
    assert "only for child validation surfaces invalidated by the repair" in section


def test_hard_identity_or_security_repair_loads_complete_repair_stack():
    section = _mode("repair/reconcile")
    hard = section.split("For a hard identity", 1)[1].split("For other hard defects", 1)[0]
    for reference in (
        "operational-lifecycle.md",
        "repair-loop.md",
        "qualification-workflow.md",
        "state-policy.md",
    ):
        assert reference in hard
    for field in (
        "exact canonical identity and selector",
        "smallest reproduction",
        "proposed durable correction",
        "invalidated evidence",
        "owner/authority",
    ):
        assert field in section


def test_verification_reporting_is_bound_to_exact_identity_and_selector():
    invariants = PARENT.split("## Shared invariants", 1)[1].split("## Completion", 1)[0]
    assert "every verification claim" in invariants
    assert "canonical identity and material selector/version" in invariants
    qualification = REFERENCES["qualification-workflow.md"]
    state = REFERENCES["state-policy.md"]
    assert "Every verification sentence" in qualification
    assert "canonical resource identity plus material selector/version" in state
    assert "generated skill location/name, or `not applicable`" in state


def test_post_adoption_defect_classifies_before_host_state_change():
    operational = REFERENCES["operational-lifecycle.md"]
    repair = REFERENCES["repair-loop.md"]
    assert "classify the defect before changing lifecycle state" in operational
    assert "**Hard:** Mark matching operational entries `blocked`" in operational
    assert "**Soft, authorized child repair:** Keep the host truthfully `installed`" in operational
    assert "operational-lifecycle.md#post-adoption-defects" in repair


def test_parent_self_invokes_for_recurring_workarounds_and_separates_soft_state_work():
    assert "## Repair interrupt" in PARENT
    interrupt = PARENT.split("## Repair interrupt", 1)[1].split("## Route the operating mode", 1)[0]
    assert "bypassing an instruction" in interrupt
    assert "Do not silently absorb the defect" in interrupt
    assert "does not by itself require unrelated pin, provenance, record, or learning reconciliation" in interrupt
    repair = _mode("repair/reconcile")
    assert "The user need not name this skill" in repair
    assert "soft instruction defect" in repair


def test_self_package_repair_honors_existing_authorization_and_blocks_ungranted_edits():
    state = REFERENCES["state-policy.md"]
    assert "current request already authorizes modifying this package" in state
    assert "do not add a redundant per-diff confirmation" in state
    assert "When package edits are not already authorized" in state
    assert "wait for explicit user authorization in chat" in state
    assert "expands beyond the existing authorized scope requires new authorization" in state


def test_generated_child_description_carries_preload_routing_boundary():
    contract = REFERENCES["resource-skill-contract.md"]
    template = (ROOT / "templates" / "resource-skill-template.md").read_text(
        encoding="utf-8"
    )
    assert "pre-load routing contract" in contract
    assert "material exclusion" in contract
    assert "incorrect implicit activation" in contract
    assert "USE-TRIGGER-IN-ONE-SENTENCE" in template
    assert "ADD-MATERIAL-ROUTING-EXCLUSION-WHEN-NEEDED" in template


def test_conditional_reconciliation_contract_preserves_existing_policies():
    contract = REFERENCES["resource-skill-contract.md"]
    lifecycle = REFERENCES["operational-lifecycle.md"]
    testing = REFERENCES["testing-protocol.md"]
    learnings = REFERENCES["learnings-store.md"]
    template = (ROOT / "templates" / "resource-skill-template.md").read_text(
        encoding="utf-8"
    )

    assert "exactly `required`, `conditional`, or `not-applicable`" in contract
    assert "`Integrity gate`" in contract
    assert "`Escalation triggers`" in contract
    assert "every version-sensitive use" in lifecycle
    assert "declared pin plus its lock/header counterpart" in lifecycle
    assert "For `conditional`, run both branches" in testing
    assert "do not load records or learnings" in learnings
    assert template.index("## Repair interrupt") < template.index("## Common path")
    assert template.index("## Common path") < template.index("## Operational reconciliation")
    assert "REQUIRED/CONDITIONAL/NOT-APPLICABLE" in template


def test_reference_file_pointers_are_links_not_bare_code_paths():
    bare_reference = re.compile(r"`references/[A-Za-z0-9_.-]+\.md(?:#[A-Za-z0-9_.-]+)?`")
    for name, text in REFERENCES.items():
        assert not bare_reference.search(text), f"{name}: use a Markdown link for internal reference navigation"


def test_openai_skill_metadata_is_parseable_and_matches_parent_modes():
    data = yaml.safe_load((ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    interface = data["interface"]
    assert interface["display_name"] == "Roblox Resource Acquisition"
    assert interface["short_description"].strip()
    prompt = interface["default_prompt"]
    assert "$roblox-resource-acquisition" in prompt
    for mode in ("evaluate/compare", "acquire/adopt", "refresh", "repair/reconcile"):
        assert mode in prompt
