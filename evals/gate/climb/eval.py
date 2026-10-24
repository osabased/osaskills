"""Score the two Roblox workflow skills' descriptions by how often haiku loads them when it should and leaves
them alone when it should not. The autoresearch evaluator for the skill-description climb.

Usage: python evals/gate/climb/eval.py --cases search.json|holdout.json [--reps 2] [--model haiku] [--threads 4]
Runs every case through run() of agent-optimization-2026-10-17/harness.py with cond "new" and this checkout as
the plugin, so the skills under skills/ as they are on disk are what each headless run sees. The last stdout
line is JSON for hc: {"score", "valid", "metrics", ...}.
    score     mean of the two skills' positive pass rates (balanced, so one skill cannot carry the other)
    metrics   srp_rate, rra_rate, neg_rate (negatives that loaded no watched skill), srp_n, rra_n, neg_n,
              wrong_skill (positives that loaded the other skill), cost_usd, mean_turns, errors
A run with no result event is an error; any error makes the score invalid rather than a silent zero.
"""
import argparse
import concurrent.futures as cf
import importlib.util
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
EVALS = ROOT.parent.parent
REPO = EVALS.parent
HARNESS = EVALS / "agent-optimization-2026-10-17" / "harness.py"
SRP, RRA = "structure-roblox-projects", "roblox-resource-acquisition"
SKILLS = {"acquisition": RRA, "structure": SRP}


def load_harness():
    spec = importlib.util.spec_from_file_location("agent_optimization_harness", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def route(loaded):
    got = {k for k, v in SKILLS.items() if any(x.endswith(":" + v) for x in loaded)}
    return "both" if len(got) == 2 else next(iter(got), "neither")


def verdict(h, case, rec):
    if rec.get("turns") is None:
        return "ERROR"
    if "route_expect" in case:
        got = route(rec["loaded"])
        ok = got == case["route_expect"] or (got == "both" and case["route_expect"] != "neither")
        return "PASS" if ok else "FAIL"
    return h.verdict(rec)


def run_one(h, case, model, rep, workdir):
    try:
        rec = h.run(case, model, "new", rep, REPO, workdir)
    except Exception as exc:  # the harness raised: count it, never hide it
        return dict(case, loaded=[], cost=None, turns=None, verdict="ERROR", error=f"{type(exc).__name__}: {exc}"[:200])
    rec["verdict"] = verdict(h, case, rec)
    return rec


def rate(records, skill):
    mine = [r for r in records if r["skill"] == skill]
    return (sum(r["verdict"] == "PASS" for r in mine) / len(mine) if mine else None), len(mine)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=pathlib.Path, required=True)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args(argv)
    cases = json.loads(a.cases.read_text(encoding="utf-8"))
    h = load_harness()
    jobs = [(c, rep) for c in cases for rep in range(1, a.reps + 1)]
    with tempfile.TemporaryDirectory(prefix="climb-") as tmp, cf.ThreadPoolExecutor(a.threads) as ex:
        records = list(ex.map(lambda j: run_one(h, j[0], a.model, j[1], pathlib.Path(tmp)), jobs))
    for r in records:
        print(f"{r['verdict']:5} {r['id']:28} {r['skill']:28} loaded={r['loaded']}", file=sys.stderr)
    errors = sum(r["verdict"] == "ERROR" for r in records)
    srp, srp_n = rate(records, SRP)
    rra, rra_n = rate(records, RRA)
    neg, neg_n = rate(records, "none")
    positives = [r for r in records if r["skill"] in (SRP, RRA)]
    wrong = sum(any(x.endswith(":" + (RRA if r["skill"] == SRP else SRP)) for x in r["loaded"]) for r in positives)
    turns = [r["turns"] for r in records if r.get("turns") is not None]
    out = {
        "score": round((srp + rra) / 2, 4) if srp is not None and rra is not None else None,
        "valid": errors == 0 and srp is not None and rra is not None,
        "metrics": {
            "srp_rate": srp, "rra_rate": rra, "neg_rate": neg, "srp_n": srp_n, "rra_n": rra_n, "neg_n": neg_n,
            "wrong_skill": wrong, "cost_usd": round(sum(r.get("cost") or 0 for r in records), 4),
            "mean_turns": round(sum(turns) / len(turns), 2) if turns else None, "errors": errors,
        },
    }
    if errors:
        out["reason"] = f"{errors} run(s) errored"
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
