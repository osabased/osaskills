"""Tally graded answers by case and arm, with each panel's round-1 majority beside its final answer. Usage:
    python tally.py --results results/full --key grading/key.json --grades grading/grades.json
"""
import argparse, json, re, pathlib
from collections import Counter, defaultdict
ROOT = pathlib.Path(__file__).resolve().parent

def majority(verdicts):
    top, n = Counter(verdicts).most_common(1)[0]
    return top if n >= 2 else "split"

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
    totals = defaultdict(Counter)
    print("| Case | Single (final) | Panel (final) | Panel round-1 majority | Panel header | Checked line |")
    print("| --- | --- | --- | --- | --- | --- |")
    for c in cases:
        cid = c["id"]
        singles = [by_source[f"{run}:final"]["verdict"] for run in runs if run.startswith(f"{cid}-single-")]
        if not singles and not any(run.startswith(f"{cid}-panel-") for run in runs):
            continue
        finals, firsts, headers, checked = [], [], [], []
        for run, r in runs.items():
            if not run.startswith(f"{cid}-panel-"):
                continue
            finals.append(by_source[f"{run}:final"]["verdict"])
            r1 = [v["verdict"] for s, v in by_source.items() if s.startswith(f"{run}:") and s.endswith(":round1")]
            firsts.append(f"{majority(r1)} ({'/'.join(r1)})")
            text = r["result"] or ""
            tally = re.search(r"### Recommendation \(([^)]*)\)", text)
            mode = re.search(r"·\s*(debate[^\n]*|quick)\s*$", text.split("\n### ")[0], re.M)
            headers.append(f"{tally.group(1) if tally else '?'}; {mode.group(1) if mode else '?'}")
            checked.append("yes" if re.search(r"^\s*\**Checked", text, re.M) else "no")
        for v in singles:
            totals[(c["kind"], "single")][v] += 1
        for v in finals:
            totals[(c["kind"], "panel")][v] += 1
        print(f"| {cid} | {', '.join(singles)} | {', '.join(finals)} | {'; '.join(firsts)} | {' / '.join(headers)} | {', '.join(checked)} |")
    print()
    for (kind, arm), counts in sorted(totals.items()):
        n = sum(counts.values())
        print(f"{kind:7} {arm:6}: right {counts['right']}/{n}, trap {counts['trap']}, hedge {counts['hedge']}")
    for arm in ("single", "panel"):
        costs = [r["cost"] or 0 for run, r in runs.items() if r["arm"] == arm]
        mins = [r["minutes"] or 0 for run, r in runs.items() if r["arm"] == arm]
        if costs:
            print(f"{arm}: {len(costs)} runs, ${sum(costs):.2f} total, ${sum(costs)/len(costs):.2f} mean, "
                  f"{sum(mins)/len(mins):.1f} min mean")
    advisor = sum(p["advisor_calls"] for r in runs.values() for p in r["panelists"])
    print(f"advisor calls by panelists: {advisor}")
