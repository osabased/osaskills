"""The eval ledger: one JSON row per eval run, appended to evals/ledger.jsonl, and a report over it.

Usage:
    python evals/_lib/ledger.py report [--eval NAME] [--skill NAME]
From a harness or the gate:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_lib"))
    import ledger
    ledger.append(ledger.row(eval="my-eval-2026-11-01", skill="think-tank", model="sonnet", cond="new",
                             trigger_cases=20, trigger_pass=19, cost_usd=1.2, source="harness"))

A row describes one (eval folder, skill, model, cond) aggregate, not one case. Fields:
    at              ISO date the runs happened (the folder's date for backfilled rows)
    commit          short sha of the skills under test, or "" when the run didn't record one
    eval            the dated folder name, or "gate" for the standing gate
    skill           the skill under test, or "all"
    model           the model alias the harness asked for (haiku, sonnet, opus)
    cond            what was run: new, old, bare, with, without, or an eval's own arm name
    trigger_cases   trigger cases run; trigger_pass of them loaded the expected skill (both null when none)
    trigger_rate    trigger_pass / trigger_cases, or null
    judge_cases     judged cases; judge_mean their mean score on the eval's scale, judge_max that scale's top
    cost_usd        total cost of the runs, or null
    seconds         total wall time, or null
    source          backfill, harness, gate or ci
Rows are append-only; a corrected run is a new row. The ledger is tracked in git so the trend travels
with the repo.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
LEDGER = ROOT / "evals" / "ledger.jsonl"
FIELDS = ("at", "commit", "eval", "skill", "model", "cond", "trigger_cases", "trigger_pass", "trigger_rate",
          "judge_cases", "judge_mean", "judge_max", "cost_usd", "seconds", "source")


def head() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 else ""
    except OSError:
        return ""


def row(**fields) -> dict:
    """A complete row: every FIELDS key present, trigger_rate derived, today's date and HEAD as defaults."""
    r = {k: fields.get(k) for k in FIELDS}
    r.update({k: v for k, v in fields.items() if k not in FIELDS})
    r["at"] = r["at"] or date.today().isoformat()
    r["commit"] = r["commit"] if r["commit"] is not None else head()
    r["skill"] = r["skill"] or "all"
    r["source"] = r["source"] or "harness"
    cases, passed = r["trigger_cases"], r["trigger_pass"]
    r["trigger_rate"] = round(passed / cases, 4) if cases and passed is not None else None
    return r


def append(r: dict, path: pathlib.Path = LEDGER) -> None:
    missing = [k for k in ("eval", "model", "cond") if not r.get(k)]
    if missing:
        raise ValueError(f"ledger row needs {', '.join(missing)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n")


def rows(path: pathlib.Path = LEDGER) -> list[dict]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def latest(all_rows: list[dict], eval_name: str, skill: str, model: str, cond: str) -> dict | None:
    """The newest row for that (eval, skill, model, cond), by position in the file."""
    found = [r for r in all_rows if (r.get("eval"), r.get("skill"), r.get("model"), r.get("cond")) == (eval_name, skill, model, cond)]
    return found[-1] if found else None


def fmt(value, width: int, places: int = 2) -> str:
    text = "-" if value is None else (f"{value:.{places}f}" if isinstance(value, float) else str(value))
    return text.rjust(width)


def report(all_rows: list[dict], eval_name: str | None = None, skill: str | None = None) -> str:
    """One line per row, grouped by eval folder, newest group last; a table that reads in a terminal."""
    picked = [r for r in all_rows if (not eval_name or r.get("eval") == eval_name) and (not skill or r.get("skill") == skill)]
    if not picked:
        return "no rows"
    lines = ["date        eval                                 skill                          model  cond         trig     rate  judge  cost     s  source"]
    groups: dict[str, list[dict]] = {}
    for r in picked:
        groups.setdefault(r.get("eval", ""), []).append(r)
    for name, group in sorted(groups.items(), key=lambda kv: min(str(r.get("at", "")) for r in kv[1])):
        for r in group:
            trig = "-" if r.get("trigger_cases") is None else f"{r.get('trigger_pass')}/{r['trigger_cases']}"
            judge = "-" if r.get("judge_cases") is None else f"{r.get('judge_mean'):.1f}/{r.get('judge_max')}"
            lines.append(" ".join([
                str(r.get("at", ""))[:10].ljust(11), name[:36].ljust(36), str(r.get("skill", ""))[:30].ljust(30),
                str(r.get("model", ""))[:6].ljust(6), str(r.get("cond", ""))[:12].ljust(12), trig.rjust(7),
                fmt(r.get("trigger_rate"), 8, 3), judge.rjust(6), fmt(r.get("cost_usd"), 6), fmt(r.get("seconds"), 5, 0),
                str(r.get("source", "")),
            ]))
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    rep = sub.add_parser("report", help="print the ledger as a table")
    rep.add_argument("--eval", help="only this eval folder")
    rep.add_argument("--skill", help="only this skill")
    rep.add_argument("--ledger", type=pathlib.Path, default=LEDGER)
    a = ap.parse_args(argv)
    print(report(rows(a.ledger), a.eval, a.skill))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
