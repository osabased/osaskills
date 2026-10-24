"""Pins the ledger's row shape, append/read behavior and report layout."""
import json
from datetime import date

import pytest

import ledger


def make(**over):
    base = dict(eval="e-2026-10-11", skill="think-tank", model="sonnet", cond="new", at="2026-10-11", commit="abc1234",
                source="backfill")
    base.update(over)
    return ledger.row(**base)


def test_row_has_every_field_and_derives_rate():
    r = make(trigger_cases=3, trigger_pass=1)
    assert all(k in r for k in ledger.FIELDS)
    assert r["trigger_rate"] == 0.3333
    assert make(trigger_cases=4, trigger_pass=4)["trigger_rate"] == 1.0


@pytest.mark.parametrize("cases,passed", [(None, None), (0, 0), (5, None), (None, 3)])
def test_rate_is_null_without_cases_or_passes(cases, passed):
    assert make(trigger_cases=cases, trigger_pass=passed)["trigger_rate"] is None


def test_rate_ignores_a_supplied_value():
    assert make(trigger_cases=2, trigger_pass=1, trigger_rate=0.99)["trigger_rate"] == 0.5


def test_row_defaults(monkeypatch):
    monkeypatch.setattr(ledger, "head", lambda: "feed123")
    r = ledger.row(eval="e", model="m", cond="c")
    assert r["at"] == date.today().isoformat()
    assert r["commit"] == "feed123"
    assert r["skill"] == "all"
    assert r["source"] == "harness"
    for k in ("trigger_cases", "trigger_pass", "judge_cases", "judge_mean", "judge_max", "cost_usd", "seconds"):
        assert r[k] is None


def test_blank_commit_is_kept_not_replaced_by_head(monkeypatch):
    monkeypatch.setattr(ledger, "head", lambda: "feed123")
    assert ledger.row(eval="e", model="m", cond="c", commit="")["commit"] == ""


def test_extra_keys_are_kept():
    r = make(note="rerun", batch=3)
    assert r["note"] == "rerun" and r["batch"] == 3


@pytest.mark.parametrize("missing", ["eval", "model", "cond"])
def test_append_refuses_a_row_without_identity(tmp_path, missing):
    path = tmp_path / "ledger.jsonl"
    r = make()
    r[missing] = ""
    with pytest.raises(ValueError, match=missing):
        ledger.append(r, path)
    assert not path.exists()


def test_append_and_rows_round_trip_in_order(tmp_path):
    path = tmp_path / "nested" / "ledger.jsonl"
    first, second = make(cond="old", note="ünï"), make(cond="new")
    ledger.append(first, path)
    ledger.append(second, path)
    assert path.read_text(encoding="utf-8").count("\n") == 2
    assert ledger.rows(path) == [first, second]


def test_rows_on_a_missing_file_is_empty(tmp_path):
    assert ledger.rows(tmp_path / "nope.jsonl") == []


def test_rows_skips_blank_lines(tmp_path):
    path = tmp_path / "l.jsonl"
    path.write_text(json.dumps(make()) + "\n\n  \n" + json.dumps(make(cond="old")) + "\n", encoding="utf-8")
    assert [r["cond"] for r in ledger.rows(path)] == ["new", "old"]


def test_latest_is_the_last_match_by_position():
    rs = [make(trigger_cases=1, trigger_pass=0), make(skill="other"), make(trigger_cases=1, trigger_pass=1)]
    found = ledger.latest(rs, "e-2026-10-11", "think-tank", "sonnet", "new")
    assert found is rs[2]


def test_latest_needs_all_four_keys_to_match():
    rs = [make()]
    assert ledger.latest(rs, "e-2026-10-11", "think-tank", "sonnet", "old") is None
    assert ledger.latest(rs, "e-2026-10-11", "think-tank", "haiku", "new") is None
    assert ledger.latest(rs, "e-2026-10-11", "all", "sonnet", "new") is None
    assert ledger.latest(rs, "other", "think-tank", "sonnet", "new") is None
    assert ledger.latest([], "e", "s", "m", "c") is None


@pytest.fixture
def two_rows():
    return [
        make(eval="late-2026-10-19", skill="s2", model="opus", cond="solo", at="2026-10-19", judge_cases=6,
             judge_mean=0.5, judge_max=1, cost_usd=1.5, seconds=120.0),
        make(eval="early-2026-10-11", skill="s1", model="sonnet", cond="new", trigger_cases=4, trigger_pass=3,
             judge_cases=2, judge_mean=7.5, judge_max=10, cost_usd=0.1234, seconds=20.4),
    ]


def test_report_layout(two_rows):
    lines = ledger.report(two_rows).split("\n")
    assert len(lines) == 3
    assert lines[0].split()[:3] == ["date", "eval", "skill"] and lines[0].split()[-1] == "source"
    # Oldest folder first, whatever the file order.
    assert lines[1].split() == ["2026-10-11", "early-2026-10-11", "s1", "sonnet", "new", "3/4", "0.750", "7.5/10",
                                "0.12", "20", "backfill"]
    assert lines[2].split() == ["2026-10-19", "late-2026-10-19", "s2", "opus", "solo", "-", "-", "0.5/1", "1.50",
                                "120", "backfill"]
    assert len({len(line) for line in lines[1:]}) == 1  # fixed-width columns


def test_report_filters_and_empty(two_rows):
    assert len(ledger.report(two_rows, eval_name="early-2026-10-11").split("\n")) == 2
    assert len(ledger.report(two_rows, skill="s2").split("\n")) == 2
    assert ledger.report(two_rows, skill="nope") == "no rows"
    assert ledger.report([]) == "no rows"


def test_report_cli_reads_the_given_ledger(tmp_path, capsys, two_rows):
    path = tmp_path / "l.jsonl"
    for r in two_rows:
        ledger.append(r, path)
    assert ledger.main(["report", "--ledger", str(path), "--skill", "s1"]) == 0
    out = capsys.readouterr().out.split("\n")
    assert out[1].split()[2] == "s1" and len([x for x in out if x]) == 2
