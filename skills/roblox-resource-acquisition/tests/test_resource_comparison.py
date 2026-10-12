"""Static comparison-contract checks, not model-behavior evaluations."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = (ROOT / "references" / "evaluation-rubric.md").read_text(encoding="utf-8")


def test_resource_criteria_keep_evidence_without_default_weights():
    assert "## Weighted comparison" not in RUBRIC
    assert "Score each 0-5" not in RUBRIC
    assert "earned weighted points" not in RUBRIC
    assert "| Criterion | What good evidence looks like |" in RUBRIC
    for criterion in (
        "Requirement fit", "Correctness evidence", "Integration cost",
        "Maintenance/currentness", "API/documentation quality", "Security posture",
        "Dependency burden", "Testability", "Performance fit", "Portability/lock-in",
    ):
        assert f"| {criterion} |" in RUBRIC
    assert RUBRIC.index("## Hard gates") < RUBRIC.index("## Evidence-and-priority comparison")


def test_selection_callers_do_not_require_the_removed_scorer():
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
        "proportionality", "verification", "candidate-treatment", "comparison", "ownership",
    } <= families


def test_hard_gates_come_before_comparison():
    gates = RUBRIC.split("## Hard gates", 1)[1].split("## Evidence-and-priority comparison", 1)[0]
    for name in ("Fit", "Evaluability", "Compatibility", "Safety", "Legitimacy", "Proof"):
        assert f"- **{name}:**" in gates
