"""The eval ledger: one row per eval run in evals/ledger.jsonl, a report across runs, and a regression gate.

A row is one harness invocation on one model and condition: its date, the commit under test, the eval folder,
the results directory, the skills under test, a per-skill trigger count, a judge score when the run was graded,
cost, duration, cases run and the Claude Code version. Usage:
    python evals/_lib/ledger.py report [--eval NAME] [--skill NAME]
    python evals/_lib/ledger.py backfill [--dry-run]
    python evals/_lib/ledger.py gate [--eval gate] [--model haiku] [--trigger-tol 0.2] [--judge-tol 0.04]
From a harness, after the results are written:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_lib"))
    import ledger
    ledger.record(ROOT.name, a.out, recs, skill_of=lambda r: ..., started=t0, cli=version)
"""
import argparse, datetime, json, math, pathlib, subprocess, sys

LIB = pathlib.Path(__file__).resolve().parent
EVALS = LIB.parent
LEDGER = EVALS / "ledger.jsonl"
KEY = ("eval", "run", "model", "cond")
FIELDS = ("date", "commit", "eval", "run", "model", "cond", "skills", "trigger", "judge", "cost_usd", "minutes",
          "cli", "cases", "gate_ok", "note")


def load(path=LEDGER):
    if not pathlib.Path(path).exists():
        return []
    return [json.loads(line) for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def key_of(row):
    return tuple(row.get(k) for k in KEY)


def append_rows(rows, path=LEDGER):
    """Append the rows whose (eval, run, model, cond) the ledger lacks, and return how many were added."""
    path = pathlib.Path(path)
    seen = {key_of(r) for r in load(path)}
    added = 0
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for row in rows:
            if key_of(row) in seen:
                continue
            seen.add(key_of(row))
            f.write(json.dumps({k: row.get(k) for k in FIELDS}, ensure_ascii=False) + "\n")
            added += 1
    return added


def head_commit(path=EVALS):
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=path, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return None


def rows_from_records(eval_name, run, recs, skill_of, *, date=None, commit=None, cli=None, minutes=None,
                      skills=None, judge=None, note="", model_of=None, cond_of=None):
    """Group run records by (model, cond) into ledger rows.

    skill_of(record) names the skill a trigger record tests, or returns None for a record that isn't one; its
    verdict must be PASS or FAIL to count. judge(model, cond) may return a judge dict for a group. skills adds
    skills under test that no trigger record names, such as the skill a quality task runs with.
    """
    model_of = model_of or (lambda r: r.get("model"))
    cond_of = cond_of or (lambda r: r.get("cond"))
    groups = {}
    for r in recs:
        groups.setdefault((model_of(r), cond_of(r)), []).append(r)
    rows = []
    for (model, cond), group in groups.items():
        trigger = {}
        for r in group:
            skill = skill_of(r)
            if skill and r.get("verdict") in ("PASS", "FAIL"):
                t = trigger.setdefault(skill, {"pass": 0, "n": 0})
                t["n"] += 1
                t["pass"] += r["verdict"] == "PASS"
        costs = [r.get("cost") for r in group if r.get("cost") is not None]
        mins = minutes
        if mins is None and any(r.get("minutes") is not None for r in group):
            mins = round(sum(r.get("minutes") or 0 for r in group), 1)
        rows.append({"date": date or datetime.date.today().isoformat(), "commit": commit, "eval": eval_name,
                     "run": run, "model": model, "cond": cond, "skills": sorted(set(trigger) | set(skills or [])),
                     "trigger": trigger or None, "judge": judge(model, cond) if judge else None,
                     "cost_usd": round(sum(costs), 4) if costs else None, "minutes": mins, "cli": cli,
                     "cases": len(group), "note": note})
    return rows


def record(eval_name, run, recs, skill_of, *, started=None, path=LEDGER, out=None, **kw):
    """Append this invocation's rows from a harness and print them. Returns the rows."""
    import time
    out = out or sys.stdout
    if started is not None and "minutes" not in kw:
        kw["minutes"] = round((time.time() - started) / 60, 1)
    kw.setdefault("commit", head_commit())
    rows = rows_from_records(eval_name, str(run).replace("\\", "/"), recs, skill_of, **kw)
    added = append_rows(rows, path)
    print(f"ledger: {added} of {len(rows)} rows appended to {pathlib.Path(path).as_posix()}", file=out)
    for row in rows:
        print("  " + line(row), file=out)
    return rows


def fmt_judge(j):
    if not j:
        return "-"
    s = f"{j['metric']} {j['score']:.2f}"
    if j.get("overall") is not None:
        s += f" overall {j['overall']:.1f}"
    return s + f" (n={j.get('n')})"


def line(row):
    trig = " ".join(f"{s} {t['pass']}/{t['n']}" for s, t in sorted((row.get("trigger") or {}).items())) or "-"
    cost = f"${row['cost_usd']:.2f}" if row.get("cost_usd") is not None else "$-"
    mins = f"{row['minutes']}min" if row.get("minutes") is not None else "-"
    skills = ",".join(row.get("skills") or []) or "-"
    return (f"{row['date']} {row.get('commit') or '-':8} {row['run']:28} {row.get('model') or '-':7} "
            f"{row.get('cond') or '-':8} trigger {trig} | judge {fmt_judge(row.get('judge'))} | {cost} {mins} "
            f"n={row.get('cases')} skills={skills}")


def report(rows, out=None, eval_filter=None, skill_filter=None):
    """Print one line per run, newest last, grouped by eval folder (folders in order of their first run)."""
    out = out or sys.stdout
    rows = [r for r in rows if (not eval_filter or r["eval"] == eval_filter)
            and (not skill_filter or skill_filter in (r.get("skills") or []))]
    groups = {}
    for r in rows:
        groups.setdefault(r["eval"], []).append(r)
    for name, group in sorted(groups.items(), key=lambda kv: (min(r["date"] for r in kv[1]), kv[0])):
        print(name, file=out)
        for r in sorted(group, key=lambda r: (r["date"], r["run"], r.get("model") or "", r.get("cond") or "")):
            print("  " + line(r), file=out)


def wilson_lower(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (centre - spread) / denom)


def wilson_upper(k, n, z=1.96):
    if n == 0:
        return 1.0
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (centre + spread) / denom)


def baseline(rows, eval_name, model, before=None, passing=False, cond=None):
    """The last row for this eval and model, or the last one before the run named by `before`.

    With passing, rows the gate failed (gate_ok false) are skipped, so one regression keeps failing until the
    rate recovers instead of becoming the new normal. With cond, only rows of that condition count, which keeps
    a partial run's rows out of the comparison.
    """
    last = None
    for r in rows:
        if before is not None and r["eval"] == eval_name and r["run"] == before:
            break
        if r["eval"] != eval_name or r.get("model") != model:
            continue
        if (passing and r.get("gate_ok") is False) or (cond is not None and r.get("cond") != cond):
            continue
        last = r
    return last


def gate_decision(base, new, trigger_tol=0.2, judge_tol=0.04):
    """Why the new row regresses against the baseline row; an empty list passes.

    Trigger: a skill fails when its pass rate is below the baseline rate by more than trigger_tol, compared only
    when the baseline ran the same number of cases for that skill. Judged: the score fails when it is below the
    baseline score by more than judge_tol and the new score's 95% upper bound is also below the baseline, which
    needs at least two runs of the judged cases.
    """
    fails = []
    if not base:
        return fails
    for skill, t in sorted((new.get("trigger") or {}).items()):
        b = (base.get("trigger") or {}).get(skill)
        if not b or b["n"] != t["n"] or t["n"] == 0:
            continue
        rate, brate = t["pass"] / t["n"], b["pass"] / b["n"]
        if rate < brate - trigger_tol - 1e-9:
            fails.append(f"trigger {skill}: {t['pass']}/{t['n']} is below the last {b['pass']}/{b['n']} "
                         f"({base['date']} {base['run']}) by more than {trigger_tol:.2f}")
    j, bj = new.get("judge"), base.get("judge")
    if j and bj and j.get("metric") == bj.get("metric") and (j.get("n") or 0) >= 2 and j.get("total"):
        upper = wilson_upper(j["passes"], j["total"])
        if j["score"] < bj["score"] - judge_tol - 1e-9 and upper < bj["score"]:
            fails.append(f"judge {j['metric']}: {j['score']:.2f} (upper bound {upper:.2f} over {j['n']} runs) is "
                         f"below the last {bj['score']:.2f} ({base['date']} {base['run']}) by more than {judge_tol:.2f}")
    return fails


def gate(rows, eval_name, model, trigger_tol, judge_tol, out=None):
    """Judge the last row for eval_name and model against the one before it. Returns the exit code."""
    out = out or sys.stdout
    new = baseline(rows, eval_name, model)
    if not new:
        print(f"gate: no {eval_name} row for {model} in the ledger", file=out)
        return 2
    base = baseline(rows, eval_name, model, before=new["run"], passing=True)
    print("gate: new      " + line(new), file=out)
    if not base:
        print(f"gate: no earlier {eval_name} row for {model}; this run sets the baseline", file=out)
        return 0
    print("gate: baseline " + line(base), file=out)
    fails = gate_decision(base, new, trigger_tol, judge_tol)
    for f in fails:
        print("FAIL " + f, file=out)
    print("gate: " + ("FAIL" if fails else "PASS"), file=out)
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default=LEDGER, type=pathlib.Path)
    sub = ap.add_subparsers(dest="cmd", required=True)
    rep = sub.add_parser("report", help="one line per run, newest last, grouped by eval folder")
    rep.add_argument("--eval")
    rep.add_argument("--skill")
    bf = sub.add_parser("backfill", help="add rows from the results folders of the dated evals")
    bf.add_argument("--dry-run", action="store_true")
    g = sub.add_parser("gate", help="compare the last row of an eval and model with the one before it")
    g.add_argument("--eval", default="gate")
    g.add_argument("--model", default="haiku")
    g.add_argument("--trigger-tol", type=float, default=0.2)
    g.add_argument("--judge-tol", type=float, default=0.04)
    a = ap.parse_args(argv)
    if a.cmd == "report":
        report(load(a.ledger), eval_filter=a.eval, skill_filter=a.skill)
        return 0
    if a.cmd == "backfill":
        import backfill
        rows = backfill.rows()
        if a.dry_run:
            report(rows)
            return 0
        print(f"backfill: {append_rows(rows, a.ledger)} of {len(rows)} rows appended")
        return 0
    return gate(load(a.ledger), a.eval, a.model, a.trigger_tol, a.judge_tol)


if __name__ == "__main__":
    sys.exit(main())
