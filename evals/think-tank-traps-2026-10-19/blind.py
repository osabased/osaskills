"""Write one shuffled, unlabelled grading file per case from a results folder, and the key to their labels.

Each file holds the case's question and every answer to it: single-session answers, panel syntheses, and
each panelist's round-1 answer. Run directory names, which name the arm, are replaced with <project>. The
key maps each label to its run and source, and is written outside grading/ so a grader can't open it. Usage:
    python blind.py --results results/full --key <path outside this folder> [--seed N]
"""
import argparse, json, random, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--key", required=True, type=pathlib.Path)
    ap.add_argument("--seed", type=int, default=20261019)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    cases = {c["id"]: c for c in json.load(open(ROOT / "cases.json", encoding="utf-8"))}
    answers = {}
    for f in sorted((ROOT / a.results).glob("*.json")):
        r = json.load(open(f, encoding="utf-8"))
        run = f"{r['id']}-{r['arm']}-{r['rep']}"
        answers.setdefault(r["id"], []).append((f"{run}:final", r["result"] or "(no answer)"))
        for p in r["panelists"]:
            if p["turns"]:
                answers[r["id"]].append((f"{run}:{p.get('description', p['agent_id'])}:round1", p["turns"][0]["reply"] or "(no answer)"))
    key = {}
    out = ROOT / "grading"
    out.mkdir(exist_ok=True)
    for case_id, items in answers.items():
        rng.shuffle(items)
        hide = re.compile(rf"{re.escape(case_id)}-(single|panel)-\d+")
        parts = [f"# {case_id}\n\nQuestion asked:\n\n> {cases[case_id]['prompt']}\n"]
        for i, (source, text) in enumerate(items, 1):
            key[f"{case_id}:R{i}"] = source
            parts.append(f"## R{i}\n\n{hide.sub('<project>', text).strip()}\n")
        (out / f"{case_id}.md").write_text("\n".join(parts), encoding="utf-8")
    a.key.write_text(json.dumps(key, indent=1), encoding="utf-8")
    print(f"{len(key)} answers in {len(answers)} files; key at {a.key}")
