"""Draw the trigger cases for structure-roblox-projects and roblox-resource-acquisition into a search set and a
holdout, stratified by what each case expects (one skill, the other, or no skill), never by score.

Usage: python evals/gate/climb/split.py [--seed 20261023] [--search-share 0.6]
Writes search.json and holdout.json beside this file. Sources: the trigger cases of
agent-optimization-2026-10-17 and the boundary group of trigger-boundary-2026-10-18. Each case keeps its
harness fields and gains "skill" (the group it counts under) and, for route-style cases, "route_expect".
"""
import argparse
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent
EVALS = ROOT.parent.parent
SRP, RRA = "structure-roblox-projects", "roblox-resource-acquisition"
ROUTE_SKILL = {"structure": SRP, "acquisition": RRA, "neither": "none"}


def cases():
    out = []
    for c in json.loads((EVALS / "agent-optimization-2026-10-17" / "cases.json").read_text(encoding="utf-8")):
        if c["kind"] == "trigger":
            out.append(dict(c, skill="none" if c["expect"].startswith("!") else c["expect"]))
    for c in json.loads((EVALS / "trigger-boundary-2026-10-18" / "cases.json").read_text(encoding="utf-8")):
        if c["group"] == "boundary":
            out.append(dict(c, skill=ROUTE_SKILL[c["expect"]], route_expect=c["expect"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261023)
    ap.add_argument("--search-share", type=float, default=0.6)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    search, holdout = [], []
    for skill in (SRP, RRA, "none"):
        group = [c for c in cases() if c["skill"] == skill]
        rng.shuffle(group)
        n = round(len(group) * a.search_share)
        search += group[:n]
        holdout += group[n:]
    for name, items in (("search", search), ("holdout", holdout)):
        (ROOT / f"{name}.json").write_text(json.dumps(items, indent=1), encoding="utf-8", newline="\n")
        by = {s: sum(c["skill"] == s for c in items) for s in (SRP, RRA, "none")}
        print(f"{name}: {len(items)} cases {by}")


if __name__ == "__main__":
    main()
