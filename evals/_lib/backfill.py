"""Turn the dated eval folders under evals/ into ledger rows, so the trend starts from what is already recorded.

Usage:
    python evals/_lib/backfill.py [--ledger PATH] [--dry-run]

Each folder has its own result shape, so each gets a small reader below; the aggregation is shared. A row is
one (folder, skill, model, cond). Where a folder ran more than one round or rerun, only its first group keeps
the plain cond ("new"); later groups get a suffix ("new-r2", "new-rerun") because their skills or rubric
differ from the first group's, and mixing them would blur the comparison the folder's README makes.

Rows are appended with source="backfill". A row whose (eval, skill, model, cond) already has a backfill row in
the ledger is skipped, so a rerun adds nothing. Folders with no per-run results are listed and skipped.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ledger  # noqa: E402

EVALS = ledger.ROOT / "evals"
RRA = "roblox-resource-acquisition"
SRP = "structure-roblox-projects"
VERDICT = {"PASS": True, "FAIL": False}  # anything else (INFO, "-") is not a trigger case
# The harness's short route names, from trigger-boundary-2026-10-18/driver.py SKILLS; "neither" expects no skill.
ROUTE_SKILL = {"acquisition": RRA, "structure": SRP, "neither": "none"}
# Which skill each judged task exercises; the result files record the task but not the skill under test.
SONNET_AB_TASKS = {"q-vide": "roblox-vide", "q-blink": "roblox-blink", "q-janitor": "roblox-janitor", "q-glob": SRP,
                   "q-entry": SRP, "q-review": "system-review", "q-addsignal": RRA}
RRA_SLIM_TASKS = {"q-addsignal": RRA, "q-compare": RRA, "q-mismatch": "roblox-janitor", "q-tool": SRP}
SHORT_GROUP = {"quality-fixed": "fixed"}
SKIPPED = {
    "skill-simplification": "no per-run results (hand-written judgments only)",
    "ssa-moduleloader-4": "no per-run results (a build, not a run)",
}


def jload(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run(skill, model, cond, *, trig=None, cost=None, seconds=None, score=None, score_max=None, commit="") -> dict:
    return {"skill": skill, "model": model, "cond": cond, "trig": trig, "cost": cost, "seconds": seconds,
            "score": score, "score_max": score_max, "commit": commit}


def result_files(results: pathlib.Path):
    """(path relative to results without .json, first directory or "", parsed record) for every run file."""
    for p in sorted(results.rglob("*.json")):
        data = jload(p)
        if isinstance(data, dict):
            rel = p.relative_to(results)
            yield rel.with_suffix("").as_posix(), (rel.parts[0] if len(rel.parts) > 1 else ""), data


def cond_for(cond: str, group: str, primary: set[str]) -> str:
    if group in primary:
        return cond
    short = re.sub(r"^round(\d+)$", r"r\1", SHORT_GROUP.get(group, group))
    return f"{cond}-{short}"


class Scores:
    """Judge scores joined from grading/key.json (blind label to results path) and grading/grades.json."""

    def __init__(self, folder: pathlib.Path):
        self.by_path: dict[str, float] = {}
        self.used: set[str] = set()
        key_file, grades_file = folder / "grading" / "key.json", folder / "grading" / "grades.json"
        if not (key_file.is_file() and grades_file.is_file()):
            return
        key, grades = jload(key_file), jload(grades_file)
        for label, path in key.items():
            task, _, blind = label.partition(":")
            entry = grades.get(task, {}).get(blind)
            # sonnet-ab stores [rubric_hits, rubric_max, overall]; the others a dict with "overall".
            if isinstance(entry, list) and len(entry) == 3:
                overall = entry[2]
            else:
                overall = entry.get("overall") if isinstance(entry, dict) else None
            if overall is not None:
                self.by_path[re.sub(r"\.json$", "", path)] = float(overall)

    def get(self, stem: str):
        if stem in self.by_path:
            self.used.add(stem)
        return self.by_path.get(stem)

    def leftover(self, folder_name: str) -> list[str]:
        gone = sorted(set(self.by_path) - self.used)
        return [f"warn {folder_name}: {len(gone)} graded run(s) have no result file, e.g. {gone[0]}"] if gone else []


def agent_optimization(folder, notes):
    scores = Scores(folder)
    for stem, group, j in result_files(folder / "results"):
        cond = cond_for(j["cond"], group, {"round1"})
        if j["kind"] == "trigger":
            yield run(j["expect"].lstrip("!"), j["model"], cond, trig=VERDICT.get(j["verdict"]), cost=j["cost"])
        else:
            yield run(SRP, j["model"], cond, cost=j["cost"], score=scores.get(stem), score_max=10)
    notes.extend(scores.leftover(folder.name))


def trigger_boundary(folder, notes):
    for _, group, j in result_files(folder / "results"):
        yield run(ROUTE_SKILL[j["expect"]], j["model"], cond_for(j["cond"], group, {"boundary"}),
                  trig=VERDICT.get(j["verdict"]), cost=j["cost"])


def structure_revamp(folder, notes):
    scores = Scores(folder)
    for stem, group, j in result_files(folder / "results"):  # the harness hardcodes --model sonnet
        cond = cond_for(j["cond"], group, {"round1"})
        if j["kind"] == "trigger":
            yield run(j["expect"].lstrip("!"), "sonnet", cond, trig=VERDICT.get(j["verdict"]), cost=j["cost"])
        else:
            yield run(SRP, "sonnet", cond, cost=j["cost"], score=scores.get(stem), score_max=10)
    notes.extend(scores.leftover(folder.name))


def resource_revamp(folder, notes):
    scores = Scores(folder)
    for stem, group, j in result_files(folder / "results"):
        cond = cond_for(j["cond"], group, {"trigger", "quality"})
        if j["kind"] == "trigger":
            yield run(j["expect"].lstrip("!"), "sonnet", cond, trig=VERDICT.get(j["verdict"]), cost=j["cost"])
        else:
            yield run(RRA, "sonnet", cond, cost=j["cost"], score=scores.get(stem), score_max=10)
    notes.extend(scores.leftover(folder.name))


def plugin_trigger(folder, notes):
    for _, _, j in result_files(folder / "results"):  # one run per prompt over many skills, so skill is "all"
        yield run("all", "sonnet", "plugin", trig=VERDICT.get(j["verdict"]), cost=j["cost"])


def bigger_picture(folder, notes):
    for results in sorted(folder.glob("results*")):
        cond = results.name.removeprefix("results").lstrip("-") or "plain"
        for _, _, j in result_files(results):
            if not j.get("soft"):  # soft cases are reported by the folder but do not count
                yield run("bigger-picture", j["model"], cond, trig=VERDICT.get(j["verdict"]), cost=j["cost"])


def sonnet_ab_trigger(j) -> bool | None:
    """The folder records which skills loaded but no verdict; this is the rule its README describes."""
    expect, loaded = j.get("expect"), j.get("skills") or []
    if expect == "then-what":
        return None  # slash-invoked, which leaves no tool event to grade
    names = {s[len("read:"):].split("/")[0] if s.startswith("read:") else s for s in loaded}
    if expect is None or expect.startswith("-none"):
        return not names
    return expect in names


def sonnet_ab(folder, notes):
    scores = Scores(folder)
    for stem, _, j in result_files(folder / "results"):
        if j["kind"] == "trigger":
            yield run("all", "sonnet", "with", trig=sonnet_ab_trigger(j), cost=j["cost"], seconds=j.get("seconds"))
        else:
            cond = j["cond"] + ("-v2" if stem.endswith("-v2") else "")
            yield run(SONNET_AB_TASKS[j["task"]], "sonnet", cond, cost=j["cost"], seconds=j.get("seconds"),
                      score=scores.get(stem), score_max=10)
    notes.extend(scores.leftover(folder.name))


def rra_slim(folder, notes):
    scores = Scores(folder)
    harness = folder / "harness.py"
    found = re.search(r'^BASELINE\s*=\s*"([0-9a-f]{7,40})"', harness.read_text(encoding="utf-8"), re.M) if harness.is_file() else None
    baseline = found.group(1) if found else ""
    for stem, _, j in result_files(folder / "results"):
        yield run(RRA_SLIM_TASKS[j["task"]], "sonnet", j["cond"], cost=j["cost"], seconds=j.get("seconds"),
                  score=scores.get(stem), score_max=10, commit=baseline if j["cond"].startswith("old") else "")
    notes.extend(scores.leftover(folder.name))


def think_tank(folder, notes):
    """Judged only: score is 1 for a final answer graded "right", else 0; panelists' round-1 labels are skipped."""
    graded = {"full": folder / "grading", "full-verify-solo": folder / "grading" / "verify-solo"}
    for group, grading in graded.items():
        verdicts = {}
        if (grading / "key.json").is_file():
            key, grades = jload(grading / "key.json"), jload(grading / "grades.json")
            verdicts = {src[: -len(":final")]: grades[label]["verdict"] for label, src in key.items() if src.endswith(":final")}
        for p in sorted((folder / "results" / group).glob("*.json")):
            j = jload(p)
            verdict = verdicts.get(p.stem)
            minutes = j.get("minutes")
            yield run("think-tank", j["model"], j["arm"], cost=j["cost"], seconds=None if minutes is None else minutes * 60,
                      score=None if verdict is None else float(verdict == "right"), score_max=1)
    for p in sorted((folder / "results").iterdir()):
        if p.is_dir() and p.name not in graded:
            notes.append(f"skip {folder.name}/results/{p.name}: calibration or pilot runs, never graded")


ADAPTERS = {
    "agent-optimization": agent_optimization,
    "bigger-picture": bigger_picture,
    "plugin-trigger": plugin_trigger,
    "resource-revamp": resource_revamp,
    "rra-slim": rra_slim,
    "sonnet-ab": sonnet_ab,
    "structure-revamp": structure_revamp,
    "think-tank-traps": think_tank,
    "trigger-boundary": trigger_boundary,
}


def aggregate(name: str, at: str, runs: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for r in runs:
        groups.setdefault((r["skill"], r["model"], r["cond"]), []).append(r)
    out = []
    for (skill, model, cond), rs in sorted(groups.items()):
        trig = [r["trig"] for r in rs if r["trig"] is not None]
        scored = [r for r in rs if r["score"] is not None]
        costs = [r["cost"] for r in rs if r["cost"] is not None]
        secs = [r["seconds"] for r in rs if r["seconds"] is not None]
        out.append(ledger.row(
            at=at, commit=next((r["commit"] for r in rs if r["commit"]), ""), eval=name, skill=skill, model=model,
            cond=cond, trigger_cases=len(trig) or None, trigger_pass=sum(trig) if trig else None,
            judge_cases=len(scored) or None,
            judge_mean=round(sum(r["score"] for r in scored) / len(scored), 4) if scored else None,
            judge_max=scored[0]["score_max"] if scored else None,
            cost_usd=round(sum(costs), 4) if costs else None, seconds=round(sum(secs), 1) if secs else None,
            source="backfill"))
    return out


def build_rows(evals: pathlib.Path = EVALS) -> tuple[list[dict], list[str]]:
    rows, notes = [], []
    for folder in sorted(p for p in evals.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        m = re.fullmatch(r"(.+)-(\d{4}-\d{2}-\d{2})", folder.name)
        if not m:
            notes.append(f"skip {folder.name}: not a dated eval folder")
        elif m.group(1) in SKIPPED:
            notes.append(f"skip {folder.name}: {SKIPPED[m.group(1)]}")
        elif m.group(1) not in ADAPTERS:
            notes.append(f"skip {folder.name}: no reader for its results")
        else:
            rows.extend(aggregate(folder.name, m.group(2), list(ADAPTERS[m.group(1)](folder, notes))))
    return rows, notes


def identity(r: dict) -> tuple:
    return (r.get("eval"), r.get("skill"), r.get("model"), r.get("cond"))


def plan(evals: pathlib.Path, path: pathlib.Path) -> tuple[list[dict], list[dict], list[str]]:
    """(rows to add, rows already in the ledger from a backfill, notes)."""
    have = {identity(r) for r in ledger.rows(path) if r.get("source") == "backfill"}
    rows, notes = build_rows(evals)
    return [r for r in rows if identity(r) not in have], [r for r in rows if identity(r) in have], notes


def backfill(evals: pathlib.Path = EVALS, path: pathlib.Path = ledger.LEDGER, dry_run: bool = False):
    """Append the new rows (not with dry_run); returns (added, skipped, notes) as counts and notes."""
    new, dupes, notes = plan(evals, path)
    if not dry_run:
        for r in new:
            ledger.append(r, path)
    return len(new), len(dupes), notes


def describe(r: dict) -> str:
    bits = [f"{r['eval']} {r['skill']} {r['model']} {r['cond']}"]
    if r["trigger_cases"]:
        bits.append(f"trig {r['trigger_pass']}/{r['trigger_cases']}")
    if r["judge_cases"]:
        bits.append(f"judge {r['judge_mean']:.2f}/{r['judge_max']} over {r['judge_cases']}")
    bits.append("cost -" if r["cost_usd"] is None else f"cost {r['cost_usd']:.2f}")
    return "  ".join(bits)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ledger", type=pathlib.Path, default=ledger.LEDGER)
    ap.add_argument("--evals", type=pathlib.Path, default=EVALS, help="the folder holding the dated eval folders")
    ap.add_argument("--dry-run", action="store_true", help="print what would be added and write nothing")
    a = ap.parse_args(argv)
    new, dupes, notes = plan(a.evals, a.ledger)
    verb = "would add" if a.dry_run else "add"
    for note in notes:
        print(note)
    for r in dupes:
        print(f"skip {describe(r)}  (already in the ledger)")
    for r in new:
        print(f"{verb} {describe(r)}")
    if not a.dry_run:
        for r in new:
            ledger.append(r, a.ledger)
    print(f"{'would add' if a.dry_run else 'added'} {len(new)} row(s), {len(dupes)} already in the ledger")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
