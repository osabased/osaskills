"""Tests for the eval ledger: appending rows, the report, and the gate decision. Run with
`python -m pytest -q evals/_lib`."""
import io, json, pathlib, sys
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ledger


def row(**over):
    base = dict(date="2026-10-20", commit="abc1234", eval="gate", run="2026-10-20-1200", model="haiku", cond="new",
                skills=["structure-roblox-projects"], trigger={"structure-roblox-projects": {"pass": 8, "n": 9}},
                judge=None, cost_usd=0.21, minutes=3.5, cli="2.1.296", cases=9, gate_ok=None, note="")
    base.update(over)
    return base


def test_append_and_load_round_trip(tmp_path):
    path = tmp_path / "ledger.jsonl"
    rows = [row(), row(date="2026-10-21", run="2026-10-21-0900")]
    assert ledger.append_rows(rows, path) == 2
    assert ledger.load(path) == rows
    # The same (eval, run, model, cond) is one run: appending it again adds nothing.
    assert ledger.append_rows(rows, path) == 0
    assert len(ledger.load(path)) == 2
    assert path.read_text(encoding="utf-8").count("\n") == 2


def test_rows_from_records_groups_by_model_and_cond():
    recs = [dict(id="t-a", model="haiku", cond="new", expect="srp", verdict="PASS", cost=0.01),
            dict(id="t-a", model="haiku", cond="new", expect="srp", verdict="FAIL", cost=0.01),
            dict(id="t-b", model="haiku", cond="new", expect="!rra", verdict="PASS", cost=0.02),
            dict(id="t-a", model="sonnet", cond="old", expect="srp", verdict="PASS", cost=0.10),
            dict(id="q-x", model="sonnet", cond="old", kind="quality", verdict="-", cost=0.30)]
    skill_of = lambda r: r["expect"].lstrip("!") if r.get("expect") else None
    rows = ledger.rows_from_records("ev", "round1", recs, skill_of, date="2026-10-17", commit="a2edc2b", cli="2.1.296")
    assert [(r["model"], r["cond"]) for r in rows] == [("haiku", "new"), ("sonnet", "old")]
    assert rows[0]["trigger"] == {"srp": {"pass": 1, "n": 2}, "rra": {"pass": 1, "n": 1}}
    assert rows[0]["skills"] == ["rra", "srp"]
    assert rows[0]["cases"] == 3 and rows[0]["cost_usd"] == pytest.approx(0.04)
    assert rows[1]["trigger"] == {"srp": {"pass": 1, "n": 1}}
    assert rows[1]["cases"] == 2 and rows[1]["judge"] is None
    assert rows[1]["eval"] == "ev" and rows[1]["run"] == "round1" and rows[1]["date"] == "2026-10-17"


def test_report_one_line_per_run_grouped_newest_last():
    rows = [row(eval="b-eval", date="2026-10-19", run="full", skills=["think-tank"], trigger=None,
                judge={"metric": "right", "score": 1.0, "n": 8}),
            row(eval="a-eval", date="2026-10-21", run="round2", trigger={"structure-roblox-projects": {"pass": 30, "n": 50}}),
            row(eval="a-eval", date="2026-10-17", run="round1", trigger={"structure-roblox-projects": {"pass": 25, "n": 50}})]
    out = io.StringIO()
    ledger.report(rows, out)
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    assert lines[0].startswith("a-eval")
    body = [l for l in lines if l.startswith("  ")]
    assert len(body) == 3
    assert "round1" in body[0] and "round2" in body[1] and "full" in body[2]
    assert "structure-roblox-projects 25/50" in body[0]
    assert "right 1.00 (n=8)" in body[2]


def test_wilson_lower_bound():
    assert ledger.wilson_lower(0, 0) == 0.0
    assert ledger.wilson_lower(9, 9) == pytest.approx(0.70, abs=0.01)
    assert ledger.wilson_lower(18, 18) > ledger.wilson_lower(9, 9)
    assert ledger.wilson_lower(5, 10) == pytest.approx(0.237, abs=0.01)


def test_gate_trigger_drop_fails_only_beyond_tolerance():
    base = row(trigger={"srp": {"pass": 9, "n": 9}, "rra": {"pass": 6, "n": 9}})
    same = row(trigger={"srp": {"pass": 9, "n": 9}, "rra": {"pass": 6, "n": 9}})
    assert ledger.gate_decision(base, same) == []
    dip = row(trigger={"srp": {"pass": 8, "n": 9}, "rra": {"pass": 5, "n": 9}})
    assert ledger.gate_decision(base, dip, trigger_tol=0.2) == []
    fails = ledger.gate_decision(base, dip, trigger_tol=0.0)
    assert len(fails) == 2 and all("trigger" in f for f in fails)
    drop = row(trigger={"srp": {"pass": 6, "n": 9}, "rra": {"pass": 6, "n": 9}})
    fails = ledger.gate_decision(base, drop, trigger_tol=0.2)
    assert len(fails) == 1 and "srp" in fails[0] and "6/9" in fails[0] and "9/9" in fails[0]


def test_gate_skips_skills_without_a_comparable_baseline():
    base = row(trigger={"srp": {"pass": 9, "n": 9}})
    new = row(trigger={"srp": {"pass": 3, "n": 6}, "rra": {"pass": 0, "n": 3}})
    # A different case count or a skill the baseline never ran is not a regression.
    assert ledger.gate_decision(base, new) == []
    assert ledger.gate_decision(None, new) == []


def test_gate_judged_uses_lower_confidence_bound_and_band():
    base = row(trigger=None, judge={"metric": "criteria", "score": 0.90, "n": 3, "passes": 27, "total": 30})
    noise = row(trigger=None, judge={"metric": "criteria", "score": 0.87, "n": 3, "passes": 26, "total": 30})
    assert ledger.gate_decision(base, noise) == []
    bad = row(trigger=None, judge={"metric": "criteria", "score": 0.50, "n": 3, "passes": 15, "total": 30})
    fails = ledger.gate_decision(base, bad, judge_tol=0.04)
    assert len(fails) == 1 and "judge" in fails[0] and "0.50" in fails[0] and "0.90" in fails[0]
    # One run of a judged case is never enough to fail the gate.
    single = row(trigger=None, judge={"metric": "criteria", "score": 0.50, "n": 1, "passes": 5, "total": 10})
    assert ledger.gate_decision(base, single) == []


def test_baseline_is_the_last_row_for_the_same_eval_and_model():
    rows = [row(date="2026-10-18", run="a", model="haiku"), row(date="2026-10-19", run="b", model="sonnet"),
            row(date="2026-10-20", run="c", model="haiku"), row(date="2026-10-21", run="d", model="haiku", eval="other")]
    assert ledger.baseline(rows, "gate", "haiku")["run"] == "c"
    assert ledger.baseline(rows, "gate", "opus") is None
    assert ledger.baseline(rows, "gate", "haiku", before="c")["run"] == "a"
    failed = row(date="2026-10-22", run="e", model="haiku", gate_ok=False, note="FAIL: trigger srp: 6/9 is below the last 9/9")
    partial = row(date="2026-10-23", run="f", model="haiku", cond="partial", gate_ok=True)
    rows += [failed, partial]
    assert ledger.baseline(rows, "gate", "haiku")["run"] == "f"
    assert ledger.baseline(rows, "gate", "haiku", passing=True)["run"] == "f"
    assert ledger.baseline(rows, "gate", "haiku", passing=True, cond="new")["run"] == "c"
    assert ledger.baseline(rows, "gate", "haiku", cond="new")["run"] == "e"


def test_record_appends_from_a_harness_and_prints(tmp_path):
    path = tmp_path / "ledger.jsonl"
    recs = [dict(id="t-a", model="haiku", cond="new", expect="srp", verdict="PASS", cost=0.01),
            dict(id="t-b", model="haiku", cond="new", expect="!srp", verdict="FAIL", cost=0.01)]
    out = io.StringIO()
    rows = ledger.record("some-eval", pathlib.PureWindowsPath("results") / "round1", recs,
                         lambda r: r["expect"].lstrip("!"), started=0, path=path, cli="2.1.296", out=out)
    assert rows[0]["run"] == "results/round1" and rows[0]["minutes"] > 0
    assert rows[0]["trigger"] == {"srp": {"pass": 1, "n": 2}}
    assert ledger.load(path)[0]["eval"] == "some-eval"
    assert "1 of 1 rows appended" in out.getvalue() and "srp 1/2" in out.getvalue()


def test_gate_cli_reads_the_ledger(tmp_path, capsys):
    path = tmp_path / "ledger.jsonl"
    ledger.append_rows([row(run="a", trigger={"srp": {"pass": 9, "n": 9}}),
                        row(run="b", date="2026-10-21", trigger={"srp": {"pass": 4, "n": 9}})], path)
    assert ledger.main(["--ledger", str(path), "gate", "--eval", "gate", "--model", "haiku"]) == 1
    assert "FAIL trigger srp" in capsys.readouterr().out
    assert ledger.main(["--ledger", str(path), "gate", "--model", "sonnet"]) == 2
    capsys.readouterr()
    ledger.main(["--ledger", str(path), "report"])
    assert capsys.readouterr().out.startswith("gate" + chr(10) + "  2026-10-20")
