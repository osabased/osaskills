"""The standing trigger gate: does each skill still load for the prompts that should load it, and stay out
for the prompts that should not. Deterministic checks only (which skill a headless run loaded); judged
rubric cases stay in the dated evals because judge scores need a blind grading step.

Usage:
    python evals/_lib/gate.py run [--model haiku] [--reps 1] [--skills a,b] [--ids x y] [--ledger PATH]
                                  [--dry-run] [--strict]
One run per (case, rep) through run() and verdict() of the agent-optimization-2026-10-17 harness, with
cond "new" and this checkout as the plugin, so it tests the current skills. Cases group under the skill
they expect; negative cases that expect no skill group under "none". Each (skill, model) appends one ledger
row (eval "gate", cond "new", source "gate", or "ci" when $CI is set, gate_ok true or false) and is compared
with the last row for that pair that the gate did not fail: the gate fails when the pass rate falls more
than one case's worth below it (--strict: any fall). Exit 1 if any skill fails. CI commits nothing back, so
its baseline is the committed ledger: to move it, run the gate locally and commit evals/ledger.jsonl. A skill with errored runs (no result from the CLI) gets no row and fails,
so an outage cannot lower the baseline. A partial run (--ids, --skills) writes its rows with cond
"partial", so they show in the report but never become a baseline.

Cases: the trigger cases of agent-optimization-2026-10-17 and the boundary group of
trigger-boundary-2026-10-18. They cover structure-roblox-projects and roblox-resource-acquisition. Not
covered yet: bigger-picture, think-tank, design-roblox-ui, sharpen, then-what, vod-discovery. To add one,
write a function returning normalized cases (see trigger_cases) and append it to CASE_SOURCES.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # `python -I` leaves it off
import ledger  # noqa: E402

EVALS = ledger.ROOT / "evals"
HARNESS = EVALS / "agent-optimization-2026-10-17" / "harness.py"
AGENT_CASES = EVALS / "agent-optimization-2026-10-17" / "cases.json"
BOUNDARY_CASES = EVALS / "trigger-boundary-2026-10-18" / "cases.json"
# Same mapping and rule as trigger-boundary-2026-10-18/driver.py, which cannot be imported without running
# its argument parsing at load time.
SKILLS = {"acquisition": "roblox-resource-acquisition", "structure": "structure-roblox-projects"}
# One case lost to rate rounding (rows keep 4 places) must not look like a drop beyond tolerance.
ROUNDING = 1e-4


def load_harness():
    spec = importlib.util.spec_from_file_location("agent_optimization_harness", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def keep_api_key(h) -> None:
    """The harness drops every ANTHROPIC* variable so a local run uses its own login. CI has no login, only
    the key, so hand that one variable back to the child there."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if os.environ.get("CI") and key:
        original = h.clean_env
        h.clean_env = lambda: {**original(), "ANTHROPIC_API_KEY": key}


def route(loaded: list[str]) -> str:
    got = {k for k, v in SKILLS.items() if any(x.endswith(":" + v) for x in loaded)}
    return "both" if len(got) == 2 else next(iter(got), "neither")


def passed(expect: str, got: str) -> bool:
    return got == expect or (got == "both" and expect != "neither")


def boundary_skill(expect: str) -> str:
    return SKILLS.get(expect, "none")


def _agent_optimization_cases() -> list[dict]:
    out = []
    for c in json.loads(AGENT_CASES.read_text(encoding="utf-8")):
        if c["kind"] != "trigger":
            continue
        expect = c["expect"]
        out.append(dict(c, skill="none" if expect.startswith("!") else expect))
    return out


def _boundary_cases() -> list[dict]:
    out = []
    for c in json.loads(BOUNDARY_CASES.read_text(encoding="utf-8")):
        if c["group"] == "boundary":
            out.append(dict(c, skill=boundary_skill(c["expect"]), route_expect=c["expect"]))
    return out


CASE_SOURCES = [_agent_optimization_cases, _boundary_cases]


def trigger_cases(skills: list[str] | None = None, ids: list[str] | None = None) -> list[dict]:
    """Normalized trigger cases: the harness case plus "skill" (the group) and, for route-style cases,
    "route_expect". Raises ValueError for a skill or id no source knows."""
    every = [c for source in CASE_SOURCES for c in source()]
    known_skills = sorted({c["skill"] for c in every})
    unknown = [s for s in skills or [] if s not in known_skills]
    if unknown:
        raise ValueError(f"no gate cases for skill {', '.join(unknown)}; covered: {', '.join(known_skills)}")
    missing = [i for i in ids or [] if i not in {c["id"] for c in every}]
    if missing:
        raise ValueError(f"unknown case id {', '.join(missing)}")
    return [c for c in every if (not skills or c["skill"] in skills) and (not ids or c["id"] in ids)]


def case_verdict(h, case: dict, record: dict) -> str:
    if "route_expect" in case:
        return "PASS" if passed(case["route_expect"], route(record["loaded"])) else "FAIL"
    return h.verdict(record)


def aggregate(records: list[dict]) -> dict[str, dict]:
    """Per skill: cases and passes over completed runs, errored runs apart, summed cost and seconds."""
    out: dict[str, dict] = {}
    for r in records:
        a = out.setdefault(r["skill"], {"cases": 0, "passed": 0, "errors": 0, "cost": 0.0, "seconds": 0.0})
        if r["verdict"] == "ERROR":
            a["errors"] += 1
        else:
            a["cases"] += 1
            a["passed"] += r["verdict"] == "PASS"
        a["cost"] += r.get("cost") or 0.0
        a["seconds"] += r.get("seconds") or 0.0
    return out


def tolerance_for(new_row: dict, strict: bool) -> float:
    cases = new_row.get("trigger_cases")
    return 0.0 if strict or not cases else 1 / cases


def decide(history: list[dict], new_row: dict, tolerance: float = 0.0) -> tuple[bool, str]:
    """Pass unless new_row's trigger rate is below the last recorded gate rate for its skill and model by
    more than tolerance. Rows the gate failed (gate_ok false) are recorded but never the baseline, so one
    drop keeps failing until the rate recovers instead of becoming the new normal."""
    new = new_row.get("trigger_rate")
    if not new_row.get("trigger_cases") or new is None:
        return False, "no cases ran"
    baseline_rows = [r for r in history if r.get("gate_ok") is not False]
    previous = ledger.latest(baseline_rows, "gate", new_row["skill"], new_row["model"], "new")
    before = previous.get("trigger_rate") if previous else None
    if before is None:
        return True, "first run"
    if new < before - tolerance - ROUNDING:
        return False, f"rate {new:.3f} fell below {before:.3f} (tolerance {tolerance:.3f})"
    return True, f"rate {new:.3f} against {before:.3f} (tolerance {tolerance:.3f})"


def planned_row(skill: str, model: str, cases: int, agg: dict | None = None, cond: str = "new") -> dict:
    agg = agg or {}
    return ledger.row(eval="gate", skill=skill, model=model, cond=cond, trigger_cases=cases,
                      trigger_pass=agg.get("passed"), cost_usd=round(agg["cost"], 4) if agg else None,
                      seconds=round(agg["seconds"], 1) if agg else None,
                      source="ci" if os.environ.get("CI") else "gate")


def evaluate(history: list[dict], records: list[dict], model: str, strict: bool, cond: str = "new") -> list[dict]:
    """One outcome per skill: {"row", "ok", "reason"}; row is None for a skill with errored runs. The row
    carries cond; the comparison is always with the last cond "new" row (decide), so a "partial" row is
    judged but never judged against."""
    out = []
    for skill, agg in sorted(aggregate(records).items()):
        if agg["errors"]:
            total = agg["cases"] + agg["errors"]
            out.append({"row": None, "ok": False, "skill": skill,
                        "reason": f"{agg['errors']} of {total} runs errored; no row written"})
            continue
        row = planned_row(skill, model, agg["cases"], agg, cond)
        ok, reason = decide(history, row, tolerance_for(row, strict))
        row["gate_ok"] = ok
        out.append({"row": row, "ok": ok, "skill": skill, "reason": reason})
    return out


def run_one(h, case: dict, model: str, rep: int, workdir: pathlib.Path) -> dict:
    started = time.monotonic()
    try:
        rec = h.run(case, model, "new", rep, ledger.ROOT, workdir)
    except Exception as exc:
        return dict(case, model=model, rep=rep, loaded=[], cost=None, turns=None, rc=None, verdict="ERROR",
                    error=f"{type(exc).__name__}: {exc}"[:200], seconds=time.monotonic() - started)
    rec["seconds"] = time.monotonic() - started
    # No result event from the CLI means no answer to judge, which a negative case must not count as a pass.
    rec["verdict"] = "ERROR" if rec.get("turns") is None else case_verdict(h, case, rec)
    return rec


def cmd_run(a: argparse.Namespace) -> int:
    ids = [i for chunk in a.ids or [] for i in chunk.split(",") if i]
    skills = [s for s in (a.skills or "").split(",") if s]
    cases = trigger_cases(skills, ids)
    if not cases:
        print("no cases selected")
        return 1
    counts: dict[str, int] = {}
    for c in cases:
        counts[c["skill"]] = counts.get(c["skill"], 0) + a.reps
    source = "ci" if os.environ.get("CI") else "gate"
    cond = "partial" if ids or skills else "new"
    if a.dry_run:
        for c in cases:
            print(f"case {c['id']} skill={c['skill']} model={a.model} reps={a.reps}")
        for skill, n in sorted(counts.items()):
            print(f"row gate {skill} {a.model} {cond} cases={n} source={source}")
        print(f"dry run: {len(cases) * a.reps} runs, nothing started, nothing written")
        return 0
    if cond == "partial":
        print("partial run: its rows are recorded as cond partial and never become a baseline")
    history = ledger.rows(a.ledger)
    h = load_harness()
    keep_api_key(h)
    jobs = [(c, rep) for c in cases for rep in range(1, a.reps + 1)]
    with tempfile.TemporaryDirectory(prefix="gate-") as tmp, cf.ThreadPoolExecutor(4) as ex:
        records = list(ex.map(lambda j: run_one(h, j[0], a.model, j[1], pathlib.Path(tmp)), jobs))
    for r in records:
        detail = f" error={r['error']}" if r.get("error") else ""
        print(f"{r['verdict']} {r['id']} {a.model} loaded={r['loaded']}{detail}")
    outcomes = evaluate(history, records, a.model, a.strict, cond)
    for o in outcomes:
        agg = aggregate(records)[o["skill"]]
        shown = o["row"]["trigger_pass"] if o["row"] else agg["passed"]
        print(f"{'ok' if o['ok'] else 'FAIL'} {o['skill']} {a.model}: {shown}/{agg['cases']} loaded as expected, {o['reason']}")
        if o["row"]:
            ledger.append(o["row"], a.ledger)
    print("total cost $%.2f" % sum(r.get("cost") or 0 for r in records))
    return 0 if all(o["ok"] for o in outcomes) else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run the trigger cases and compare with the ledger")
    run.add_argument("--model", default="haiku")
    run.add_argument("--reps", type=int, default=1)
    run.add_argument("--skills", help="comma-separated skills to run (none = the no-skill cases)")
    run.add_argument("--ids", nargs="+", help="only these case ids (space or comma separated)")
    run.add_argument("--ledger", type=pathlib.Path, default=ledger.LEDGER)
    run.add_argument("--dry-run", action="store_true", help="print the cases and planned rows; run nothing")
    run.add_argument("--strict", action="store_true", help="fail on any fall in the pass rate")
    a = ap.parse_args(argv)
    try:
        return cmd_run(a)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
