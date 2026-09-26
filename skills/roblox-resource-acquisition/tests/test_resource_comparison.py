"""Static comparison-contract checks, not model-behavior evaluations."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = (ROOT / "references" / "evaluation-rubric.md").read_text(encoding="utf-8")


def test_resource_criteria_keep_evidence_without_default_weights():
    assert "## Weighted comparison" not in RUBRIC
    assert "Score each 0-5" not in RUBRIC
    assert "earned weighted points" not in RUBRIC
    assert "| Criterion | What good evidence looks like |" in RUBRIC
    assert "mandatory checklist or priority order" in RUBRIC
    for criterion in (
        "Requirement fit", "Correctness evidence", "Integration cost",
        "Maintenance/currentness", "API/documentation quality", "Security posture",
        "Dependency burden", "Testability", "Performance fit", "Portability/lock-in",
    ):
        assert f"| {criterion} |" in RUBRIC
    assert RUBRIC.index("## Hard gates") < RUBRIC.index("## Evidence-and-priority comparison")


def test_comparison_preserves_quantities_priorities_and_deciding_evidence():
    for boundary in (
        "threshold or an objective to optimize",
        "strict or permits tradeoffs",
        "do not replace requested optimization",
        "measurements in meaningful units",
        "task-supplied or evidence-backed numerical models",
        "separate observation from inference",
        "identity/version, environment, workload, and integration effects",
        "hypothetical fix as demonstrated capability",
        "missing evidence or a potentially material unresolved difference does not establish a tie",
        "applicable user/project tie-breakers first",
    ):
        assert boundary in RUBRIC


def test_direction_handoff_is_conditional_and_returns_to_acquisition():
    section = RUBRIC.split("## Decision ownership", 1)[1].split("## Evidence strength", 1)[0]
    for boundary in (
        "fixed targets, roles/pins",
        "adequate authorized project capabilities",
        "curated policy preferences",
        "trust into runtime proof",
        "Keep straightforward, supported choices local",
        "`direction-selection` when available",
        "applicability router, not directly into full mode",
        "do not restart completed qualification",
        "returns bounded resource-evidence answers to the owning comparison",
        "blocker cannot be bypassed by a local fallback",
        "Acquisition retains the authorized lifecycle work",
        "If that skill is unavailable",
        "Selection alone grants neither trust nor mutation authority",
    ):
        assert boundary in section


def test_selection_callers_do_not_require_the_removed_scorer():
    parent = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    qualification = (ROOT / "references" / "qualification-workflow.md").read_text(encoding="utf-8")
    runtime_files = [ROOT / "SKILL.md"]
    for directory in ("references", "templates"):
        runtime_files.extend((ROOT / directory).rglob("*.md"))
    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        for legacy_instruction in (
            "before scoring", "before any scoring", "weighted scoring",
            "score only survivors", "scores slightly higher", "reject or heavily penalize",
        ):
            assert legacy_instruction not in text, path
    assert "Follow its conditional direction-selection routing" in qualification
    assert "curation is a policy preference" in qualification
    assert "reject a candidate that fails an applicable hard gate" in qualification
    assert "does not authorize integration, child generation, or host adoption" in qualification


def test_comparison_case_definitions_are_well_formed():
    import json

    cases = json.loads((ROOT / "evals" / "comparison-cases.json").read_text(encoding="utf-8"))
    assert isinstance(cases, list) and cases
    ids = set()
    families = set()
    for case in cases:
        assert isinstance(case, dict)
        for field in ("id", "family", "prompt"):
            assert isinstance(case.get(field), str) and case[field].strip()
        assert case["id"] not in ids
        ids.add(case["id"])
        families.add(case["family"])
        for field in ("accept", "reject"):
            values = case.get(field)
            assert isinstance(values, list) and values
            assert all(isinstance(value, str) and value.strip() for value in values)
    for case in cases:
        related = case.get("related", [])
        assert isinstance(related, list)
        assert all(isinstance(item, str) and item in ids and item != case["id"] for item in related)
    assert {
        "priorities", "quantities", "close-comparison", "qualification", "authority",
        "proportionality", "verification", "candidate-treatment", "availability", "ownership",
    } <= families


def test_hard_gates_and_policy_trust_are_preserved():
    gates = RUBRIC.split("## Hard gates", 1)[1].split("## Evidence-and-priority comparison", 1)[0]
    assert "A candidate cannot be selected when any applicable hard gate fails" in gates
    for name in ("Fit", "Evaluability", "Compatibility", "Safety", "Legitimacy", "Proof"):
        assert f"- **{name}:**" in gates
    assert "Unknown is not automatically failure" in gates
    assert "Curated resources already have policy trust" in gates
    assert "unresolved facts still limit what can truthfully be called verified" in gates
