"""Backfill against a tiny fake eval tree: shapes taken from the real folders, content cut to a few runs."""
import json
import pathlib

import pytest

import backfill
import ledger


def put(path: pathlib.Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def tree(tmp_path):
    evals = tmp_path / "evals"
    agent = evals / "agent-optimization-2026-10-17"
    trig = {"kind": "trigger", "model": "sonnet", "cond": "new", "expect": "structure-roblox-projects"}
    put(agent / "results/round1/trigger/t-a-sonnet-new-1.json", {**trig, "verdict": "PASS", "cost": 0.1})
    put(agent / "results/round1/trigger/t-a-sonnet-new-2.json", {**trig, "verdict": "FAIL", "cost": 0.2})
    put(agent / "results/round1/quality/q-x-sonnet-new-1.json",
        {"kind": "quality", "model": "sonnet", "cond": "new", "verdict": "-", "cost": 0.3})
    put(agent / "results/round2/trigger/t-a-sonnet-new-1.json",
        {**trig, "expect": "!structure-roblox-projects", "verdict": "PASS", "cost": 0.4})
    put(agent / "grading/key.json", {"q-x:R1": "round1/quality/q-x-sonnet-new-1"})
    put(agent / "grading/grades.json", {"q-x": {"R1": {"criteria": {}, "overall": 7}}})

    plugin = evals / "plugin-trigger-2026-10-11" / "results"
    put(plugin / "pos-vide.json", {"id": "pos-vide", "expect": "roblox-vide", "verdict": "PASS", "cost": 0.07})
    put(plugin / "probe-listing.json", {"id": "probe-listing", "expect": None, "verdict": "INFO", "cost": 0.05})

    boundary = evals / "trigger-boundary-2026-10-18" / "results"
    base = {"kind": "trigger", "model": "haiku", "cond": "old", "verdict": "PASS", "cost": 0.01}
    put(boundary / "boundary/b-1.json", {**base, "expect": "neither"})
    put(boundary / "boundary/b-2.json", {**base, "expect": "acquisition", "verdict": "FAIL"})
    put(boundary / "rerun/b-1.json", {**base, "expect": "acquisition"})

    tank = evals / "think-tank-traps-2026-10-19"
    for n, minutes in ((1, 2.0), (2, 3.0)):
        put(tank / f"results/full/c-single-{n}.json", {"arm": "single", "model": "opus", "cost": 1.0, "minutes": minutes})
    put(tank / "grading/key.json",
        {"c:R1": "c-single-1:final", "c:R2": "c-single-2:final", "c:R3": "c-single-1:Panelist A:round1"})
    put(tank / "grading/grades.json",
        {"c:R1": {"verdict": "right"}, "c:R2": {"verdict": "trap"}, "c:R3": {"verdict": "trap"}})

    put(evals / "skill-simplification-2026-10-06/judgments.json", {"a": 1})
    return evals


def by_key(rows):
    return {(r["eval"], r["skill"], r["model"], r["cond"]): r for r in rows}


def test_build_rows_aggregates_per_skill_model_cond(tree):
    rows, notes = backfill.build_rows(tree)
    got = by_key(rows)

    r = got[("agent-optimization-2026-10-17", "structure-roblox-projects", "sonnet", "new")]
    assert (r["trigger_cases"], r["trigger_pass"], r["trigger_rate"]) == (2, 1, 0.5)
    assert (r["judge_cases"], r["judge_mean"], r["judge_max"]) == (1, 7, 10)
    assert r["cost_usd"] == pytest.approx(0.6)
    assert (r["at"], r["commit"], r["source"]) == ("2026-10-17", "", "backfill")
    assert r["seconds"] is None

    # Later rounds are their own condition, and a "!skill" expectation belongs to that skill.
    r2 = got[("agent-optimization-2026-10-17", "structure-roblox-projects", "sonnet", "new-r2")]
    assert (r2["trigger_cases"], r2["trigger_pass"], r2["judge_cases"]) == (1, 1, None)

    assert any("skill-simplification-2026-10-06" in n and "skip" in n for n in notes)


def test_info_runs_cost_money_but_are_not_cases(tree):
    rows, _ = backfill.build_rows(tree)
    r = by_key(rows)[("plugin-trigger-2026-10-11", "all", "sonnet", "plugin")]
    assert (r["trigger_cases"], r["trigger_pass"]) == (1, 1)
    assert r["cost_usd"] == pytest.approx(0.12)


def test_boundary_routes_become_skills_and_reruns_stay_apart(tree):
    got = by_key(backfill.build_rows(tree)[0])
    none = got[("trigger-boundary-2026-10-18", "none", "haiku", "old")]
    assert (none["trigger_cases"], none["trigger_pass"]) == (1, 1)
    acq = got[("trigger-boundary-2026-10-18", "roblox-resource-acquisition", "haiku", "old")]
    assert (acq["trigger_cases"], acq["trigger_pass"]) == (1, 0)
    rerun = got[("trigger-boundary-2026-10-18", "roblox-resource-acquisition", "haiku", "old-rerun")]
    assert (rerun["trigger_cases"], rerun["trigger_pass"]) == (1, 1)


def test_think_tank_judge_is_the_share_of_right_final_answers(tree):
    r = by_key(backfill.build_rows(tree)[0])[("think-tank-traps-2026-10-19", "think-tank", "opus", "single")]
    assert (r["judge_cases"], r["judge_mean"], r["judge_max"]) == (2, 0.5, 1)  # the panelist round-1 label is not counted
    assert r["trigger_cases"] is None
    assert r["cost_usd"] == pytest.approx(2.0) and r["seconds"] == pytest.approx(300.0)


def test_backfill_appends_then_refuses_duplicates(tree, tmp_path):
    path = tmp_path / "ledger.jsonl"
    added, skipped, _ = backfill.backfill(tree, path)
    assert added > 0 and skipped == 0
    before = path.read_text(encoding="utf-8")
    assert len(ledger.rows(path)) == added

    added2, skipped2, _ = backfill.backfill(tree, path)
    assert (added2, skipped2) == (0, added)
    assert path.read_text(encoding="utf-8") == before


def test_a_harness_row_does_not_block_a_backfill_row(tree, tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger.append(ledger.row(eval="plugin-trigger-2026-10-11", skill="all", model="sonnet", cond="plugin",
                             source="harness", commit=""), path)
    added, skipped, _ = backfill.backfill(tree, path)
    assert skipped == 0
    assert len(ledger.rows(path)) == added + 1


def test_dry_run_writes_nothing_and_says_what_it_would_add(tree, tmp_path, capsys):
    path = tmp_path / "ledger.jsonl"
    assert backfill.main(["--ledger", str(path), "--evals", str(tree), "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert not path.exists()
    assert "would add" in out and "agent-optimization-2026-10-17" in out
    assert "skip" in out and "skill-simplification-2026-10-06" in out


def test_main_writes_the_ledger_and_reports_duplicates(tree, tmp_path, capsys):
    path = tmp_path / "ledger.jsonl"
    assert backfill.main(["--ledger", str(path), "--evals", str(tree)]) == 0
    n = len(ledger.rows(path))
    capsys.readouterr()
    assert backfill.main(["--ledger", str(path), "--evals", str(tree)]) == 0
    assert len(ledger.rows(path)) == n
    assert "already in the ledger" in capsys.readouterr().out
