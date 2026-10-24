"""Ledger rows from the results folders of the dated evals, one per results directory, model and condition.

Each row's date and commit are those of the commit that added its results directory. Trigger counts come from
each record's verdict, judge scores from grading/grades.json joined through grading/key.json where an eval was
graded. Run through `python evals/_lib/ledger.py backfill [--dry-run]`.
"""
import json, pathlib, subprocess
import ledger

EVALS = ledger.EVALS
SRP, RRA = "structure-roblox-projects", "roblox-resource-acquisition"
SUITE = {"srp": SRP, "rra": RRA}
ROUTE = {"structure": SRP, "acquisition": RRA}


def load(p):
    return json.load(open(p, encoding="utf-8"))


def records(folder):
    return {p.stem: load(p) for p in sorted(folder.glob("*.json"))}


def added(path):
    """(date, short commit) of the commit that added path, from git."""
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%h %ad", "--date=short", "--", str(path)],
                         cwd=EVALS, capture_output=True, text=True).stdout.strip().splitlines()
    if not out:
        return None, None
    commit, date = out[-1].split()
    return date, commit


def cli_of(recs):
    versions = {str(r.get("cli")).split()[0] for r in recs.values() if r.get("cli")}
    return ",".join(sorted(versions)) or None


def graded(eval_dir, grading="grading"):
    """run stem -> grade entry, through the blind key."""
    g = eval_dir / grading
    if not (g / "grades.json").exists():
        return {}
    key, grades = load(g / "key.json"), load(g / "grades.json")
    out = {}
    for task, labels in grades.items():
        if task in key:  # flat grades, keyed "case:label" like the key itself
            out[key[task]] = labels
            continue
        if not isinstance(labels, dict):
            continue
        for label, entry in labels.items():
            source = key.get(f"{task}:{label}")
            if source:
                out[source] = entry
    return out


def criteria_judge(stems, grades):
    """Pooled criteria passes and mean overall for the graded runs among stems."""
    passes = total = n = 0
    overall = []
    for stem in stems:
        e = grades.get(stem)
        if not e:
            continue
        n += 1
        if isinstance(e, list):  # sonnet-ab: [rubric met, rubric max, overall]
            passes, total = passes + e[0], total + e[1]
            overall.append(e[2])
            continue
        c = e.get("criteria") or {}
        for v in c.values():
            total += 1
            passes += bool(v[0] if isinstance(v, list) else v)
        if e.get("overall") is not None:
            overall.append(e["overall"])
    if not n:
        return None
    j = {"metric": "criteria", "score": round(passes / total, 3) if total else None, "n": n, "passes": passes, "total": total}
    if overall:
        j["overall"] = round(sum(overall) / len(overall), 2)
    return j


def rows_for(eval_dir, rel, recs, skill_of, *, skills=None, grades=None, model_of=None, cond_of=None,
             judge_stems=None):
    date, commit = added(eval_dir / rel)
    if not date:
        date = eval_dir.name[-10:]
    judge = None
    if grades:
        def judge(model, cond):
            stems = [s for s, r in recs.items() if (model_of or (lambda r: r.get("model")))(r) == model
                     and (cond_of or (lambda r: r.get("cond")))(r) == cond]
            return criteria_judge([judge_stems(s) if judge_stems else s for s in stems], grades)
    return ledger.rows_from_records(eval_dir.name, rel.replace("\\", "/"), list(recs.values()), skill_of, date=date,
                                    commit=commit, cli=cli_of(recs), skills=skills, judge=judge, note="backfill",
                                    model_of=model_of, cond_of=cond_of)


def expect_skill(r):
    e = r.get("expect")
    return e.lstrip("!") if isinstance(e, str) and e else None


def agent_optimization():
    d = EVALS / "agent-optimization-2026-10-17"
    grades = graded(d)
    rows = []
    for rel in ["round1/trigger", "round1/trigger-haiku", "round1/quality", "round2/trigger", "round2/quality",
                "round3", "round4", "round5"]:
        recs = records(d / "results" / rel)
        skills = sorted({SUITE[r["suite"]] for r in recs.values() if r.get("kind") == "quality" and r.get("cond") != "bare"})
        rows += rows_for(d, "results/" + rel, recs, expect_skill, skills=skills, grades=grades,
                         judge_stems=lambda s, rel=rel: f"{rel}/{s}")
    return rows


def bigger_picture():
    d = EVALS / "bigger-picture-2026-10-17"
    rows = []
    for folder, cond in [("results", "new"), ("results-hook", "hook"), ("results-tagged", "tagged")]:
        for model_dir in sorted((d / folder).iterdir()):
            recs = records(model_dir)
            rows += rows_for(d, f"{folder}/{model_dir.name}", recs, lambda r: "bigger-picture", cond_of=lambda r: cond)
    return rows


def plugin_trigger():
    d = EVALS / "plugin-trigger-2026-10-11"
    recs = {s: r for s, r in records(d / "results").items() if r.get("verdict") in ("PASS", "FAIL")}
    return rows_for(d, "results", recs, expect_skill, model_of=lambda r: "sonnet", cond_of=lambda r: "plugin")


def resource_revamp():
    d = EVALS / "resource-revamp-2026-10-15"
    grades = graded(d)
    rows = rows_for(d, "results/trigger", records(d / "results/trigger"), expect_skill, model_of=lambda r: "sonnet")
    for rel in ["quality", "quality-fixed"]:
        rows += rows_for(d, "results/" + rel, records(d / "results" / rel), lambda r: None, skills=[RRA], grades=grades,
                         model_of=lambda r: "sonnet", judge_stems=lambda s, rel=rel: f"{rel}/{s}")
    return rows


def rra_slim():
    d = EVALS / "rra-slim-2026-10-11"
    recs = records(d / "results")
    for r in recs.values():
        r["minutes"] = round((r.get("seconds") or 0) / 60, 2)
    return rows_for(d, "results", recs, lambda r: None, skills=[RRA], grades=graded(d), model_of=lambda r: "sonnet")


def sonnet_ab():
    d = EVALS / "sonnet-ab-2026-10-11"
    recs = records(d / "results")
    cases = {c["id"]: c for c in load(d / "trigger_cases.json")}
    for stem, r in recs.items():
        c = cases.get(stem)
        if not c:
            r.setdefault("cond", "with" if r.get("with_skills") else "without")
            continue
        e = c.get("expect")
        loaded = r.get("skills") or []
        if e is None or e.startswith("-none"):
            r["verdict"] = "PASS" if not loaded else "FAIL"
            r["expect"] = "!" + e.split("user-only ")[1].rstrip(")") if e else None
        else:
            r["verdict"] = "PASS" if any(e in s for s in loaded) else "FAIL"
            r["expect"] = e
        r["cond"] = "with"
        r["minutes"] = round((r.get("seconds") or 0) / 60, 2)
    return rows_for(d, "results", recs, expect_skill, grades=graded(d), model_of=lambda r: "sonnet")


def structure_revamp():
    d = EVALS / "structure-revamp-2026-10-15"
    grades = graded(d)
    rows = []
    for rel in ["round1", "round2"]:
        recs = records(d / "results" / rel)
        rows += rows_for(d, "results/" + rel, recs, expect_skill, skills=[SRP], grades=grades,
                         model_of=lambda r: "sonnet", judge_stems=lambda s, rel=rel: f"{rel}/{s}")
    return rows


def think_tank():
    d = EVALS / "think-tank-traps-2026-10-19"
    rows = []
    for rel, grading in [("pilot", None), ("calibration-1", None), ("calibration-2", None), ("full", "grading"),
                         ("pilot-verify-solo", None), ("full-verify-solo", "grading/verify-solo")]:
        recs = records(d / "results" / rel)
        finals = {}
        if grading:
            finals = {s.removesuffix(":final"): e for s, e in graded(d, grading).items() if s.endswith(":final")}

        def judge(model, cond, recs=recs, finals=finals):
            stems = [s for s, r in recs.items() if r.get("arm") == cond and s in finals]
            if not stems:
                return None
            right = sum(finals[s]["verdict"] == "right" for s in stems)
            return {"metric": "right", "score": round(right / len(stems), 3), "n": len(stems), "passes": right,
                    "total": len(stems)}
        date, commit = added(d / "results" / rel)
        for cond in sorted({r.get("arm") for r in recs.values()}):
            group = {s: r for s, r in recs.items() if r.get("arm") == cond}
            rows += ledger.rows_from_records(d.name, f"results/{rel}", list(group.values()), lambda r: None, date=date,
                                             commit=commit, cli=cli_of(group), note="backfill",
                                             skills=["think-tank"] if cond in ("panel", "solo") else [],
                                             judge=judge, cond_of=lambda r: r.get("arm"))
    return rows


def trigger_boundary():
    d = EVALS / "trigger-boundary-2026-10-18"
    rows = []
    for rel in ["boundary", "rerun", "srp-spot"]:
        rows += rows_for(d, "results/" + rel, records(d / "results" / rel), lambda r: ROUTE.get(r.get("expect")))
    return rows


def rows():
    out = []
    for fn in (sonnet_ab, rra_slim, plugin_trigger, structure_revamp, resource_revamp, agent_optimization,
               bigger_picture, trigger_boundary, think_tank):
        out += fn()
    return sorted(out, key=lambda r: (r["date"], r["eval"], r["run"], r["model"] or "", r["cond"] or ""))
