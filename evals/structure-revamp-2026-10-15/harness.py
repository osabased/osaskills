"""Compare two versions of the skills on triggering and task quality.

Each run copies a scaffold and one version's skills into a temporary project's .claude/skills/ and
runs headless Claude Code there with project settings only, so an installed osaskills plugin stays
out of it. "new" is this checkout's skills/; "old" is a skills/ tree you extract, for example
`git archive origin/main skills | tar -x -C <dir>`. Usage:
    python harness.py --old-skills <dir>/skills [--reps N] [--conds old,new] [--out results] [case-id ...]
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time, pathlib, concurrent.futures as cf
ROOT = pathlib.Path(__file__).parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(ROOT.parent / "_lib"))
import ledger
SCAFFOLDS = {"base": ROOT.parent / "sonnet-ab-2026-10-11" / "scaffold", "game": ROOT / "scaffold"}
DENY = {"trigger": "Bash,PowerShell,Write,Edit,WebSearch,WebFetch,Agent,Task",
        "quality": "Bash,PowerShell,WebSearch,WebFetch,Agent,Task"}

def clean_env():
    # Drop a parent Claude session's variables so the child uses its own login.
    drop = ("CLAUDE", "ANTHROPIC", "USE_LOCAL_OAUTH", "USE_STAGING_OAUTH")
    return {k: v for k, v in os.environ.items() if not k.upper().startswith(drop)}

def install_skills(src, dst):
    # Library skills are nested in roblox-resource-acquisition/libraries/; install them flat.
    for s in [*src.iterdir(), *(src / "roblox-resource-acquisition" / "libraries").glob("*")]:
        if (s / "SKILL.md").exists():
            shutil.copytree(s, dst / s.name, ignore=shutil.ignore_patterns("tests", "__pycache__"))

def changed_files(proj, scaffold):
    out = {}
    for f in proj.rglob("*"):
        rel = f.relative_to(proj)
        if not f.is_file() or ".claude" in rel.parts:
            continue
        orig = scaffold / rel
        if not orig.exists() or orig.read_bytes() != f.read_bytes():
            out[rel.as_posix()] = f.read_text(errors="replace")[:8000]
    return out

def run(case, cond, rep, skills_root, workdir):
    scaffold = SCAFFOLDS[case["scaffold"]]
    proj = workdir / f"{case['id']}-{cond}-{rep}"
    shutil.copytree(scaffold, proj)
    install_skills(skills_root, proj / ".claude" / "skills")
    cmd = ["claude", "-p", case["prompt"], "--model", "sonnet", "--output-format", "stream-json", "--verbose",
           "--max-turns", str(case["max_turns"]), "--setting-sources", "project,local", "--strict-mcp-config",
           "--permission-mode", "acceptEdits", "--disallowedTools", DENY[case["kind"]]]
    p = subprocess.run(cmd, cwd=proj, env=clean_env(), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900, stdin=subprocess.DEVNULL)
    loaded, reads, tools, pending = [], [], [], {}
    result = cost = turns = usage = None
    for line in p.stdout.splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        t = ev.get("type")
        if t == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") != "tool_use": continue
                tools.append(c["name"])
                inp = c.get("input", {})
                if c["name"] == "Skill":
                    loaded.append("tool:" + str(inp.get("skill") or inp.get("command")))
                path = str(inp.get("file_path", "")).replace("\\", "/")
                if c["name"] == "Read" and "/.claude/skills/" in path:
                    pending[c.get("id")] = path.split("/.claude/skills/", 1)[1]
                    if path.endswith("SKILL.md"):
                        loaded.append("read:" + pathlib.PurePosixPath(path).parent.name)
        if t == "user":
            # A Read counts once its result comes back without an error.
            for c in ev.get("message", {}).get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in pending:
                    rel = pending.pop(c["tool_use_id"])
                    if not c.get("is_error"):
                        f = proj / ".claude" / "skills" / rel
                        reads.append([rel, f.stat().st_size if f.is_file() else None])
        if t == "result":
            result, cost, turns, usage = ev.get("result"), ev.get("total_cost_usd"), ev.get("num_turns"), ev.get("usage")
    return dict(case, cond=cond, rep=rep, loaded=loaded, reads=reads, tools=tools, result=result, cost=cost,
                turns=turns, usage=usage, rc=p.returncode, stderr=p.stderr[-400:], written=changed_files(proj, scaffold))

def verdict(r):
    e = r.get("expect")
    if r["kind"] != "trigger" or e is None: return "-"
    hit = any(x.endswith(":" + e.lstrip("!")) for x in r["loaded"])
    return "PASS" if hit != e.startswith("!") else "FAIL"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-skills", required=True, type=pathlib.Path)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--conds", default="old,new", help="comma-separated conditions to run")
    ap.add_argument("--out", default="results", help="results directory under this eval")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    roots = {"old": a.old_skills, "new": REPO / "skills"}
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8")) if not a.ids or c["id"] in a.ids]
    jobs = [(c, cond, rep) for c in cases for cond in a.conds.split(",") for rep in range(1, a.reps + 1)]
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="srp-revamp-") as tmp, cf.ThreadPoolExecutor(5) as ex:
        recs = list(ex.map(lambda j: run(j[0], j[1], j[2], roots[j[1]], pathlib.Path(tmp)), jobs))
    for r in recs:
        r["verdict"] = verdict(r)
        (out / f"{r['id']}-{r['cond']}-{r['rep']}.json").write_text(
            json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        skill_bytes = sum(n or 0 for _, n in r["reads"])
        print(f"{r['verdict']:4} {r['id']:13} {r['cond']} {r['rep']} loaded={r['loaded']} reads={len(r['reads'])} "
              f"skill_bytes={skill_bytes} turns={r['turns']} cost={r['cost']} rc={r['rc']}")
    print("total cost $%.2f" % sum(r["cost"] or 0 for r in recs))
    ledger.record(ROOT.name, a.out, recs, lambda r: (r.get("expect") or "").lstrip("!") or None, model_of=lambda r: "sonnet",
                  skills=["structure-roblox-projects"] if any(r["kind"] == "quality" for r in recs) else [], started=started)
