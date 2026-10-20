"""Tally graded answers by case and arm, with each think-tank run's round-1 verdicts beside its final answer
and the web lookups each run made (the session's own, then each panelist's). Usage:
    python tally.py --results results/full --key grading/key.json --grades grading/grades.json
"""
import argparse, json, re, pathlib
from collections import Counter, defaultdict
ROOT = pathlib.Path(__file__).resolve().parent
ARMS = ("single", "verify", "solo", "panel")
WEB = ("WebSearch", "WebFetch")

def majority(verdicts):
    top, n = Counter(verdicts).most_common(1)[0]
    return top if n >= 2 else "split"

def lookups(r):
    counts = [sum(s[0] in WEB for s in r["steps"])] + [sum(t in WEB for t in p["tools"]) for p in r["panelists"]]
    return "+".join(map(str, counts))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--grades", required=True)
    a = ap.parse_args()
    key = json.load(open(ROOT / a.key, encoding="utf-8"))
    grades = json.load(open(ROOT / a.grades, encoding="utf-8"))
    by_source = {source: grades[label] for label, source in key.items()}
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8"))]
    runs = {f.stem: json.load(open(f, encoding="utf-8")) for f in sorted((ROOT / a.results).glob("*.json"))}
    arms = [arm for arm in ARMS if any(r["arm"] == arm for r in runs.values())]
    totals = defaultdict(Counter)
    print("| Case | Arm | Final | Round 1 | Header | Checked line | Lookups |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for c in cases:
        cid = c["id"]
        for arm in arms:
            mine = {run: r for run, r in runs.items() if run.startswith(f"{cid}-{arm}-")}
            if not mine:
                continue
            finals, firsts, headers, checked = [], [], [], []
            for run, r in mine.items():
                finals.append(by_source[f"{run}:final"]["verdict"])
                totals[(c["kind"], arm)][finals[-1]] += 1
                if not r["panelists"]:
                    continue
                r1 = [v["verdict"] for s, v in by_source.items() if s.startswith(f"{run}:") and s.endswith(":round1")]
                firsts.append(r1[0] if len(r1) == 1 else f"{majority(r1)} ({'/'.join(r1)})")
                text = r["result"] or ""
                tally = re.search(r"### Recommendation \(([^)]*)\)", text)
                mode = re.search(r"·\s*(debate[^\n]*|quick)\s*$", text.split("\n### ")[0], re.M)
                if tally or mode:
                    headers.append(f"{tally.group(1) if tally else '?'}; {mode.group(1) if mode else '?'}")
                checked.append("yes" if re.search(r"^\s*\**Checked", text, re.M) else "no")
            print(f"| {cid} | {arm} | {', '.join(finals)} | {'; '.join(firsts)} | {' / '.join(headers)} | "
                  f"{', '.join(checked)} | {', '.join(lookups(r) for r in mine.values())} |")
    print()
    for (kind, arm), counts in sorted(totals.items(), key=lambda t: (t[0][0], ARMS.index(t[0][1]))):
        n = sum(counts.values())
        print(f"{kind:7} {arm:6}: right {counts['right']}/{n}, trap {counts['trap']}, hedge {counts['hedge']}")
    for arm in arms:
        mine = [r for r in runs.values() if r["arm"] == arm]
        costs = [r["cost"] or 0 for r in mine]
        mins = [r["minutes"] or 0 for r in mine]
        print(f"{arm}: {len(mine)} runs, ${sum(costs):.2f} total, ${sum(costs)/len(costs):.2f} mean, "
              f"{sum(mins)/len(mins):.1f} min mean")
    advisor = sum(p["advisor_calls"] for r in runs.values() for p in r["panelists"])
    print(f"advisor calls by panelists: {advisor}")
    hits = [f"{run}: {h}" for run, r in runs.items() for h in r.get("key_hits", [])]
    print(f"web lookups that touched the public answer key: {len(hits)}", *hits, sep="\n  ")
