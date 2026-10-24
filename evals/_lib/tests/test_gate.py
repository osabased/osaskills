"""Tests for the trigger gate: the decision rule, case mapping, per-skill aggregation and --dry-run."""
import gate
import ledger
import pytest

RPA = "roblox-resource-acquisition"
SRP = "structure-roblox-projects"


def gate_row(skill=SRP, model="haiku", cases=10, passed=10, **extra):
    return ledger.row(eval="gate", skill=skill, model=model, cond="new", trigger_cases=cases, trigger_pass=passed,
                      source="gate", at="2026-10-23", commit="abc1234", **extra)


# --- decide ---

def test_first_run_passes_with_no_history():
    ok, reason = gate.decide([], gate_row())
    assert ok and reason == "first run"


def test_first_run_ignores_other_skills_models_and_evals():
    history = [gate_row(skill=RPA, passed=10), gate_row(model="sonnet", passed=10),
               ledger.row(eval="think-tank-2026-10-19", skill=SRP, model="haiku", cond="new", trigger_cases=5, trigger_pass=5)]
    ok, reason = gate.decide(history, gate_row(passed=1))
    assert ok and reason == "first run"


def test_equal_rate_passes():
    ok, reason = gate.decide([gate_row(passed=9)], gate_row(passed=9))
    assert ok and "0.900" in reason


def test_rise_passes():
    assert gate.decide([gate_row(passed=8)], gate_row(passed=10))[0]


def test_drop_within_tolerance_passes():
    assert gate.decide([gate_row(passed=10)], gate_row(passed=9), tolerance=0.1)[0]


def test_drop_beyond_tolerance_fails_with_both_rates_in_reason():
    ok, reason = gate.decide([gate_row(passed=10)], gate_row(passed=8), tolerance=0.1)
    assert not ok and "0.800" in reason and "1.000" in reason


def test_strict_tolerance_fails_on_one_case_drop():
    assert not gate.decide([gate_row(passed=10)], gate_row(passed=9), tolerance=0.0)[0]


def test_default_tolerance_of_decide_is_strict():
    assert not gate.decide([gate_row(passed=10)], gate_row(passed=9))[0]


def test_uses_the_latest_row_not_the_best():
    history = [gate_row(passed=10), gate_row(passed=7)]
    assert gate.decide(history, gate_row(passed=7))[0]


def test_zero_cases_fails():
    ok, reason = gate.decide([gate_row()], gate_row(cases=0, passed=None))
    assert not ok and reason == "no cases ran"


def test_zero_cases_fails_even_without_history():
    assert gate.decide([], gate_row(cases=0, passed=None)) == (False, "no cases ran")


def test_previous_row_without_a_rate_counts_as_no_baseline():
    ok, reason = gate.decide([gate_row(cases=0, passed=None)], gate_row())
    assert ok and reason == "first run"


@pytest.mark.parametrize("cases,passed", [(6, 5), (7, 6), (12, 11), (3, 2)])
def test_one_case_tolerance_survives_rate_rounding(cases, passed):
    prev = gate_row(cases=cases, passed=cases)
    one_down, two_down = gate_row(cases=cases, passed=passed), gate_row(cases=cases, passed=passed - 1)
    tolerance = gate.tolerance_for(one_down, strict=False)
    assert gate.decide([prev], one_down, tolerance=tolerance)[0]
    assert not gate.decide([prev], two_down, tolerance=tolerance)[0]


def test_tolerance_for():
    assert gate.tolerance_for(gate_row(cases=10), strict=False) == pytest.approx(0.1)
    assert gate.tolerance_for(gate_row(cases=10), strict=True) == 0.0
    assert gate.tolerance_for(gate_row(cases=0, passed=None), strict=False) == 0.0


# --- case mapping ---

def test_route_maps_loaded_skills():
    assert gate.route([f"tool:{SRP}"]) == "structure"
    assert gate.route([f"read:{RPA}"]) == "acquisition"
    assert gate.route([f"tool:{SRP}", f"read:{RPA}"]) == "both"
    assert gate.route(["tool:caveman"]) == "neither"
    assert gate.route([]) == "neither"


def test_boundary_expectations_map_to_skills():
    assert gate.boundary_skill("structure") == SRP
    assert gate.boundary_skill("acquisition") == RPA
    assert gate.boundary_skill("neither") == "none"


def test_boundary_pass_rule():
    assert gate.passed("structure", "structure")
    assert gate.passed("acquisition", "both")
    assert not gate.passed("neither", "both")
    assert not gate.passed("structure", "acquisition")
    assert not gate.passed("neither", "structure")


def test_cases_cover_the_two_standing_skills_and_none():
    cases = gate.trigger_cases()
    assert {c["skill"] for c in cases} == {SRP, RPA, "none"}
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))
    assert all(c["kind"] == "trigger" for c in cases)


def test_cases_from_both_sources_with_the_right_group():
    by_id = {c["id"]: c for c in gate.trigger_cases()}
    assert by_id["t-entry"]["skill"] == SRP
    assert by_id["selene-pin-bump"]["skill"] == RPA
    assert by_id["own-signal-class"]["skill"] == "none"
    assert not any(c["id"].startswith("anchor") for c in by_id.values())


def test_negative_agent_optimization_case_goes_under_none():
    negatives = [c for c in gate.trigger_cases() if str(c.get("expect", "")).startswith("!")]
    assert negatives and all(c["skill"] == "none" for c in negatives)


def test_filters_by_skill_and_ids():
    only = gate.trigger_cases(skills=[RPA])
    assert only and {c["skill"] for c in only} == {RPA}
    assert [c["id"] for c in gate.trigger_cases(ids=["t-entry"])] == ["t-entry"]
    assert gate.trigger_cases(skills=[SRP], ids=["selene-pin-bump"]) == []


def test_unknown_id_or_skill_raises():
    with pytest.raises(ValueError, match="nope"):
        gate.trigger_cases(ids=["nope"])
    with pytest.raises(ValueError, match="think-tank"):
        gate.trigger_cases(skills=["think-tank"])


def test_case_verdict_for_both_case_shapes():
    h = gate.load_harness()
    by_id = {c["id"]: c for c in gate.trigger_cases()}
    pos = by_id["t-entry"]
    assert gate.case_verdict(h, pos, {**pos, "loaded": [f"tool:{SRP}"]}) == "PASS"
    assert gate.case_verdict(h, pos, {**pos, "loaded": []}) == "FAIL"
    neg = next(c for c in by_id.values() if str(c.get("expect", "")).startswith("!"))
    assert gate.case_verdict(h, neg, {**neg, "loaded": []}) == "PASS"
    assert gate.case_verdict(h, neg, {**neg, "loaded": [f"tool:{neg['expect'][1:]}"]}) == "FAIL"
    bound = by_id["selene-pin-bump"]
    assert gate.case_verdict(h, bound, {**bound, "loaded": [f"read:{RPA}"]}) == "PASS"
    assert gate.case_verdict(h, bound, {**bound, "loaded": [f"read:{SRP}"]}) == "FAIL"
    none = by_id["own-signal-class"]
    assert gate.case_verdict(h, none, {**none, "loaded": []}) == "PASS"
    assert gate.case_verdict(h, none, {**none, "loaded": [f"tool:{SRP}"]}) == "FAIL"


def test_keep_api_key_only_under_ci(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    h = gate.load_harness()
    assert "ANTHROPIC_API_KEY" not in h.clean_env()
    monkeypatch.delenv("CI", raising=False)
    gate.keep_api_key(h)
    assert "ANTHROPIC_API_KEY" not in h.clean_env()
    monkeypatch.setenv("CI", "1")
    gate.keep_api_key(h)
    assert h.clean_env()["ANTHROPIC_API_KEY"] == "sk-test"


# --- aggregation ---

def rec(skill, verdict, cost=0.01, seconds=2.0):
    return {"skill": skill, "verdict": verdict, "cost": cost, "seconds": seconds}


def test_aggregate_groups_by_skill():
    records = [rec(SRP, "PASS"), rec(SRP, "FAIL"), rec(SRP, "PASS", cost=None), rec("none", "PASS"), rec(RPA, "PASS")]
    agg = gate.aggregate(records)
    assert agg[SRP] == {"cases": 3, "passed": 2, "errors": 0, "cost": pytest.approx(0.02), "seconds": 6.0}
    assert agg["none"]["cases"] == 1 and agg[RPA]["passed"] == 1


def test_aggregate_counts_errors_apart_from_cases():
    agg = gate.aggregate([rec(SRP, "PASS"), rec(SRP, "ERROR")])
    assert agg[SRP]["cases"] == 1 and agg[SRP]["errors"] == 1


def test_evaluate_decides_per_skill(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    history = [gate_row(skill=SRP, cases=2, passed=2), gate_row(skill=RPA, cases=2, passed=2)]
    records = [rec(SRP, "PASS"), rec(SRP, "FAIL"), rec(RPA, "PASS"), rec(RPA, "PASS")]
    lenient = {o["row"]["skill"]: o["ok"] for o in gate.evaluate(history, records, "haiku", strict=False)}
    assert lenient == {SRP: True, RPA: True}  # 1 of 2 against 2 of 2 is one case's drop
    strict = {o["row"]["skill"]: o["ok"] for o in gate.evaluate(history, records, "haiku", strict=True)}
    assert strict == {SRP: False, RPA: True}


def test_evaluate_row_fields_and_source(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    [out] = gate.evaluate([], [rec(SRP, "PASS", cost=0.05, seconds=3.0)], "haiku", strict=False)
    row = out["row"]
    assert (row["eval"], row["cond"], row["skill"], row["model"], row["source"]) == ("gate", "new", SRP, "haiku", "gate")
    assert (row["trigger_cases"], row["trigger_pass"], row["trigger_rate"]) == (1, 1, 1.0)
    assert row["cost_usd"] == pytest.approx(0.05) and row["seconds"] == 3.0
    monkeypatch.setenv("CI", "1")
    [out] = gate.evaluate([], [rec(SRP, "PASS")], "haiku", strict=False)
    assert out["row"]["source"] == "ci"


def test_evaluate_errored_runs_fail_without_a_row():
    [out] = gate.evaluate([gate_row()], [rec(SRP, "PASS"), rec(SRP, "ERROR")], "haiku", strict=False)
    assert out["row"] is None and not out["ok"] and "errored" in out["reason"]


# --- CLI ---

def test_dry_run_lists_cases_and_rows_and_spawns_nothing(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(gate, "load_harness", lambda: pytest.fail("dry run loaded the harness"))
    path = tmp_path / "ledger.jsonl"
    code = gate.main(["run", "--dry-run", "--model", "haiku", "--reps", "2", "--ledger", str(path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "t-entry" in out and "selene-pin-bump" in out and "own-signal-class" in out
    assert f"row gate {SRP} haiku new" in out and "cases=" in out
    assert not path.exists()


def test_dry_run_respects_ids(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(gate, "load_harness", lambda: pytest.fail("loaded"))
    gate.main(["run", "--dry-run", "--ids", "t-entry,selene-pin-bump", "--ledger", str(tmp_path / "l.jsonl")])
    out = capsys.readouterr().out
    assert "t-entry" in out and "selene-pin-bump" in out and "own-signal-class" not in out


class FakeHarness:
    """Stands in for harness.py: loads each positive case's skill (or nothing when load is False)."""
    def __init__(self, load=True):
        self.calls = []
        self.load = load

    def run(self, case, model, cond, rep, plugin, workdir):
        self.calls.append((case["id"], model, cond, rep, plugin))
        loaded = [f"tool:{case['skill']}"] if self.load and case["skill"] != "none" else []
        return dict(case, model=model, cond=cond, rep=rep, loaded=loaded, cost=0.01, turns=2, rc=0)

    def verdict(self, r):
        e = r["expect"]
        hit = any(x.endswith(":" + e.lstrip("!")) for x in r["loaded"])
        return "PASS" if hit != e.startswith("!") else "FAIL"


def test_run_writes_one_row_per_skill_and_exits_zero_on_pass(monkeypatch, capsys, tmp_path):
    fake = FakeHarness()
    monkeypatch.setattr(gate, "load_harness", lambda: fake)
    monkeypatch.delenv("CI", raising=False)
    path = tmp_path / "ledger.jsonl"
    code = gate.main(["run", "--skills", SRP, "--ledger", str(path)])
    out = capsys.readouterr().out
    written = ledger.rows(path)
    assert code == 0
    assert [r["skill"] for r in written] == [SRP] and written[0]["source"] == "gate"
    assert all(call[2] == "new" and call[1] == "haiku" and call[4] == ledger.ROOT for call in fake.calls)
    assert "PASS t-entry haiku" in out and "total cost" in out


def test_run_exits_one_when_rate_drops(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(gate, "load_harness", lambda: FakeHarness(load=False))
    path = tmp_path / "ledger.jsonl"
    n = len(gate.trigger_cases(skills=[SRP]))
    ledger.append(gate_row(skill=SRP, cases=n, passed=n), path)
    code = gate.main(["run", "--skills", SRP, "--ledger", str(path)])
    assert code == 1
    assert "FAIL" in capsys.readouterr().out
    assert ledger.rows(path)[-1]["trigger_pass"] == 0


def test_partial_run_writes_partial_rows_that_are_not_a_baseline(monkeypatch, capsys, tmp_path):
    fake = FakeHarness()
    monkeypatch.setattr(gate, "load_harness", lambda: fake)
    monkeypatch.delenv("CI", raising=False)
    path = tmp_path / "ledger.jsonl"
    assert gate.main(["run", "--skills", SRP, "--ledger", str(path)]) == 0
    written = ledger.rows(path)
    assert written[-1]["cond"] == "partial"
    assert "partial run" in capsys.readouterr().out
    # A later full run of that skill sees no baseline: the partial row is judged, never judged against.
    row = gate.planned_row(SRP, "haiku", 1, {"passed": 0, "cost": 0.0, "seconds": 0.0})
    assert gate.decide(written, row) == (True, "first run")


def test_a_failed_row_is_recorded_but_never_the_baseline():
    good = gate_row(skill=SRP, cases=10, passed=10)
    bad = dict(gate_row(skill=SRP, cases=10, passed=5), gate_ok=False)
    again = gate_row(skill=SRP, cases=10, passed=5)
    ok, reason = gate.decide([good, bad], again, tolerance=0.1)
    assert not ok and "1.000" in reason


def test_evaluate_marks_rows_with_the_gate_outcome():
    rows = [dict(c, verdict="PASS", skill=SRP, cost=0.0) for c in gate.trigger_cases(skills=[SRP])]
    out = gate.evaluate([], rows, "haiku", strict=False)
    assert out[0]["row"]["gate_ok"] is True
