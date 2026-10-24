"""Tests for the gate harness's baseline rules, on fixture records with no model calls."""
import importlib.util, io, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ledger
spec = importlib.util.spec_from_file_location("gate_harness", pathlib.Path(__file__).resolve().parent.parent / "gate" / "harness.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
SRP = "structure-roblox-projects"


def gate_row(**over):
    base = dict(date="2026-10-23", commit="abc1234", eval="gate", run="results/x", model="haiku", cond="new",
                skills=[SRP], trigger={SRP: {"pass": 9, "n": 9}}, judge=None, cost_usd=0.2, minutes=3.0,
                cli="2.1.296", cases=9, gate_ok=None, note="")
    base.update(over)
    return base


def test_partial_run_writes_partial_rows_that_are_not_a_baseline():
    assert gate.cond_for(["srp-glob"], list(gate.KINDS)) == "partial"
    assert gate.cond_for([], ["trigger"]) == "partial"
    assert gate.cond_for([], list(gate.KINDS)) == "new"
    partial = gate_row(run="results/a", cond="partial", trigger={SRP: {"pass": 2, "n": 9}}, gate_ok=True)
    # A later full run sees no baseline: the partial row is judged, never judged against.
    full = gate_row(run="results/b")
    out = io.StringIO()
    assert gate.evaluate([partial], [full], 0.2, 0.04, out) == []
    assert full["gate_ok"] is True and "sets the baseline" in out.getvalue()


def test_a_failed_row_is_recorded_but_never_the_baseline():
    good = gate_row(run="results/a")
    bad = gate_row(run="results/b", trigger={SRP: {"pass": 4, "n": 9}}, gate_ok=False, note="FAIL: trigger")
    again = gate_row(run="results/c", trigger={SRP: {"pass": 4, "n": 9}})
    fails = gate.evaluate([good, bad], [again], 0.2, 0.04, io.StringIO())
    assert len(fails) == 1 and "9/9" in fails[0] and again["gate_ok"] is False
    assert again["note"].startswith("FAIL: trigger " + SRP)


def test_evaluate_marks_rows_with_the_gate_outcome():
    first = gate_row(run="results/a")
    assert gate.evaluate([], [first], 0.2, 0.04, io.StringIO()) == []
    assert first["gate_ok"] is True and first["note"] == "pass"
    same = gate_row(run="results/b")
    assert gate.evaluate([first], [same], 0.2, 0.04, io.StringIO()) == []
    assert same["gate_ok"] is True


def test_gate_ok_is_written_to_the_ledger(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger.append_rows([gate_row(gate_ok=False)], path)
    assert ledger.load(path)[0]["gate_ok"] is False
