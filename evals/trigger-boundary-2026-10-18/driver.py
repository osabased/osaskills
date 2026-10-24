"""Run the boundary trigger cases against two plugin trees and record which skill each run loads.

Reuses run() from ../agent-optimization-2026-10-17/harness.py, so isolation, installs and scrubbing match
that eval. Usage:
    python driver.py --old-root <dir> --new-root <dir> [--reps sonnet=3,haiku=5] [--out results] [--groups boundary,anchor,srp-spot]
"""
import argparse, concurrent.futures as cf, importlib.util, json, pathlib, subprocess, sys, tempfile, time
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_lib"))
import ledger
spec = importlib.util.spec_from_file_location("h", ROOT.parent / "agent-optimization-2026-10-17" / "harness.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
SKILLS = {"acquisition": "roblox-resource-acquisition", "structure": "structure-roblox-projects"}

def route(loaded):
    got = {k for k, v in SKILLS.items() if any(x.endswith(":" + v) for x in loaded)}
    return "both" if len(got) == 2 else next(iter(got), "neither")

def passed(expect, got):
    return got == expect or (got == "both" and expect != "neither")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-root", required=True, type=pathlib.Path)
    ap.add_argument("--new-root", required=True, type=pathlib.Path)
    ap.add_argument("--reps", default="sonnet=3,haiku=5")
    ap.add_argument("--groups", default="boundary,anchor,srp-spot")
    ap.add_argument("--out", default="results")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    reps = {m: int(n) for m, n in (p.split("=") for p in a.reps.split(","))}
    roots = {"old": a.old_root.resolve(), "new": a.new_root.resolve()}
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8"))
             if c["group"] in a.groups.split(",") and (not a.ids or c["id"] in a.ids)]
    jobs = [(c, m, cond, r) for c in cases for m, n in reps.items() for cond in roots for r in range(1, n + 1)]
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True, env=h.clean_env()).stdout.strip()
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="boundary-") as tmp, cf.ThreadPoolExecutor(5) as ex:
        recs = list(ex.map(lambda j: h.run(*j[:3], j[3], roots[j[2]], pathlib.Path(tmp)), jobs))
        scrub = h.scrubber([(tmp, "<runs>"), (roots["old"], "<old-plugin>"), (roots["new"], "<new-plugin>"),
                            (sys.executable, "python"), (pathlib.Path.home(), "~")])
        recs = [scrub(r) for r in recs]
    for r in recs:
        r["route"] = route(r["loaded"])
        r["verdict"] = "PASS" if passed(r["expect"], r["route"]) else "FAIL"
        r["cli"] = version
        (out / f"{r['id']}-{r['model']}-{r['cond']}-{r['rep']}.json").write_text(
            json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{r['verdict']:4} {r['id']:26} {r['model']:6} {r['cond']:4} {r['rep']} route={r['route']} cost={r['cost']} rc={r['rc']}")
    print("total cost $%.2f" % sum(r["cost"] or 0 for r in recs))
    ledger.record(ROOT.name, a.out, recs, lambda r: SKILLS.get(r["expect"]), started=started, cli=version)
