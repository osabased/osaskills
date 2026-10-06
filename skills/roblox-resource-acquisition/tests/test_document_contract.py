"""Packaging/navigation checks. Behavioral outcomes live in evals, not prose assertions."""
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
        rf"^### `{re.escape(name)}`\n(.*?)(?=^## |^### |\Z)",
        PARENT,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing parent mode {name!r}"
    return match.group(1)


def _links(text: str) -> set[str]:
    return set(re.findall(r"\[[^\]]+\]\(([^)]+)\)", text))


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


def test_evaluate_compare_routes_only_decision_and_state_references():
    # Scope behavior is covered by explicit-evaluation-only/fixed-target cases.
    assert _links(_mode("evaluate/compare")) == {
        "references/qualification-workflow.md",
        "references/evaluation-rubric.md",
        "references/state-policy.md",
    }


def test_acquire_adopt_reaches_each_in_scope_lifecycle_contract():
    # Adoption scenarios test scope, status separation and completion behavior.
    assert {
        "references/adoption-policy.md",
        "references/qualification-workflow.md",
        "references/project-adoption.md",
        "references/generation-validation.md",
        "references/operational-lifecycle.md",
        "references/state-policy.md",
    } <= _links(_mode("acquire/adopt"))


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


def test_refresh_routes_changed_input_validation_surfaces():
    assert {
        "references/qualification-workflow.md",
        "references/project-adoption.md",
        "references/generation-validation.md",
        "references/operational-lifecycle.md",
        "references/repair-loop.md",
        "references/state-policy.md",
    } <= _links(_mode("refresh"))


def test_repair_reconcile_reaches_each_affected_surface_contract():
    assert {
        "references/qualification-workflow.md",
        "references/project-adoption.md",
        "references/generation-validation.md",
        "references/operational-lifecycle.md",
        "references/repair-loop.md",
        "references/state-policy.md",
    } <= _links(_mode("repair/reconcile"))


def test_repair_scenarios_cover_hard_soft_and_harmless_boundaries():
    import json

    cases = json.loads((ROOT / "evals" / "maintenance-cases.json").read_text(encoding="utf-8"))
    assert {"hard-identity-mismatch", "soft-recurring-guidance", "harmless-local-adjustment"} <= {
        case["id"] for case in cases
    }


def test_lifecycle_reporting_has_one_reachable_contract():
    assert "references/state-policy.md" in _links(PARENT)
    # Runtime record/bundle validators test actual target/state binding; this
    # assertion checks navigation, not whether a model reports the right facts.
    assert "scripts/validate_resource_record.py" in REFERENCES["state-policy.md"]
    assert "scripts/validate_resource_bundle.py" in REFERENCES["state-policy.md"]


def test_post_adoption_defect_classifies_before_host_state_change():
    operational = REFERENCES["operational-lifecycle.md"]
    repair = REFERENCES["repair-loop.md"]
    assert "classify the defect before changing lifecycle state" in operational
    assert "**Hard:** Mark matching operational entries `blocked`" in operational
    assert "**Soft, authorized child repair:** Keep the host truthfully `installed`" in operational
    assert "operational-lifecycle.md#post-adoption-defects" in repair


def test_repair_interrupt_anchor_remains_reachable_from_compatibility_router():
    assert "repair-interrupt" in _anchors(ROOT / "SKILL.md")
    assert "../SKILL.md#repair-interrupt" in _links(REFERENCES["repair-reconcile-workflow.md"])


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
    spec = yaml.safe_load((ROOT / 'templates/resource-skill-template.yaml').read_text(encoding='utf-8'))
    assert spec['reconciliation']['policy'] == 'conditional'
    usage = REFERENCES['child-usage.md']
    policies = set(re.findall(r'\*\*([a-z-]+):\*\*', usage))
    assert policies == {'required', 'conditional', 'not-applicable'}
    assert 'check_resource_install.py' in usage
    assert 'check_resource_status.py' in usage
    assert 'For `conditional`, run both branches' in REFERENCES['testing-protocol.md']
    assert 'do not load records or learnings' in REFERENCES['learnings-store.md']



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


def test_first_use_route_does_not_require_loading_the_repair_transaction():
    assert "first-use-check.md" in _links(REFERENCES["child-usage.md"])
    assert "on-demand-maintenance.md#first-use-freshness-check" not in _links(REFERENCES["child-usage.md"])
    assert "first-use-freshness-check" in _anchors(ROOT / "references/on-demand-maintenance.md")
    assert "first-use-check.md" in _links(REFERENCES["on-demand-maintenance.md"])
    assert "first-use-check.md#source-observations" in _links(REFERENCES["on-demand-maintenance.md"])


def test_maintenance_case_definitions_are_well_formed():
    import json

    cases = json.loads((ROOT / "evals/maintenance-cases.json").read_text(encoding="utf-8"))
    ids = set()
    for case in cases:
        assert case["id"] not in ids
        ids.add(case["id"])
        assert isinstance(case["prompt"], str) and case["prompt"].strip()
        for field in ("accept", "reject"):
            assert case[field] and all(isinstance(item, str) and item.strip() for item in case[field])
    assert {"refresh-unchanged-runtime", "healthy-conditional", "required-plugin-drift", "unknown-project"} <= ids
