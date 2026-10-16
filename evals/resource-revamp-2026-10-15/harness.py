"""Compare two plugin versions of roblox-resource-acquisition on triggering and task quality.

Each run copies the scaffold, one version's top-level skills and the case's cloned library skills
into a temporary project, adds session_hook.py as a SessionStart hook for that version, and runs
headless Claude Code there with project settings only, so an installed osaskills plugin stays out
of it. Quality runs may execute `python` and `uv` commands; trigger runs can't execute anything.
"new" is this checkout; "old" is a plugin tree you extract, for example
`git archive 20d318a skills hooks | tar -x -C <dir>`. Results have local paths replaced. Usage:
    python harness.py --old-root <dir> [--reps N] [--conds old,new] [--out results] [case-id ...]
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, pathlib, concurrent.futures as cf
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent.parent
DENY = {"trigger": "Bash,PowerShell,Write,Edit,WebSearch,WebFetch,Agent,Task",
        "quality": "PowerShell,WebSearch,WebFetch,Agent,Task"}
ALLOW = {"trigger": [], "quality": ["Bash(python:*)", "Bash(python3:*)", "Bash(uv:*)"]}
SKILL = "roblox-resource-acquisition"

def clean_env():
    # Drop a parent Claude session's variables so the child uses its own login.
    drop = ("CLAUDE", "ANTHROPIC", "USE_LOCAL_OAUTH", "USE_STAGING_OAUTH")
    return {k: v for k, v in os.environ.items() if not k.upper().startswith(drop)}

def path_pattern(path):
    parts = pathlib.PureWindowsPath(path).parts
    drive = parts[0][0]
    rest = r"[\\/]+".join(re.escape(p) for p in parts[1:])
    return re.compile(rf"(?:{drive}:|/{drive})[\\/]+{rest}", re.IGNORECASE)

def scrubber(pairs):
    patterns = [(path_pattern(p), label) for p, label in pairs]
    def scrub(value):
        if isinstance(value, str):
            for pattern, label in patterns:
                value = pattern.sub(label, value)
            return value
        if isinstance(value, list):
            return [scrub(v) for v in value]
        if isinstance(value, dict):
            return {k: scrub(v) for k, v in value.items()}
        return value
    return scrub

def install(plugin, case, proj):
    skills = proj / ".claude" / "skills"
    for s in (plugin / "skills").iterdir():
        if (s / "SKILL.md").exists():
            shutil.copytree(s, skills / s.name, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    for name in case.get("clones", []):
        shutil.copytree(plugin / "skills" / SKILL / "libraries" / name, skills / name)
    hook = f'python "{(ROOT / "session_hook.py").as_posix()}" "{plugin.as_posix()}"'
    settings = {"hooks": {"SessionStart": [{"matcher": "startup", "hooks": [{"type": "command", "command": hook, "timeout": 30}]}]}}
    (proj / ".claude" / "settings.json").write_text(json.dumps(settings, indent=1), encoding="utf-8")

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

def step(name, inp):
    for key in ("command", "file_path", "pattern", "skill", "path"):
        if inp.get(key):
            return [name, str(inp[key])[:300]]
    return [name, ""]

def run(case, cond, rep, plugin, workdir):
    scaffold = ROOT / "scaffold"
    proj = workdir / f"{case['id']}-{cond}-{rep}"
    shutil.copytree(scaffold, proj)
    install(plugin, case, proj)
    before = {p.name for p in (proj / ".claude" / "skills").iterdir()}
    cmd = ["claude", "-p", case["prompt"], "--model", "sonnet", "--output-format", "stream-json", "--verbose",
           "--max-turns", str(case["max_turns"]), "--setting-sources", "project,local", "--strict-mcp-config",
           "--permission-mode", "acceptEdits", "--disallowedTools", DENY[case["kind"]]]
    if ALLOW[case["kind"]]:
        cmd += ["--allowedTools", *ALLOW[case["kind"]]]
    p = subprocess.run(cmd, cwd=proj, env=clean_env(), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900, stdin=subprocess.DEVNULL)
    loaded, reads, steps, pending = [], [], [], {}
    result = cost = turns = usage = denials = None
    for line in p.stdout.splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        t = ev.get("type")
        if t == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") != "tool_use": continue
                inp = c.get("input", {})
                steps.append(step(c["name"], inp))
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
            denials = [step(d.get("tool_name", ""), d.get("tool_input", {})) for d in ev.get("permission_denials") or []]
    clones = sorted({p.name for p in (proj / ".claude" / "skills").iterdir()} - before)
    return dict(case, cond=cond, rep=rep, loaded=loaded, reads=reads, steps=steps, denials=denials, clones=clones,
                result=result, cost=cost, turns=turns, usage=usage, rc=p.returncode, stderr=p.stderr[-400:],
                written=changed_files(proj, scaffold))

def verdict(r):
    e = r.get("expect")
    if r["kind"] != "trigger" or e is None: return "-"
    hit = any(x.endswith(":" + e.lstrip("!")) for x in r["loaded"])
    return "PASS" if hit != e.startswith("!") else "FAIL"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-root", required=True, type=pathlib.Path, help="plugin tree holding skills/ and hooks/")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--conds", default="old,new", help="comma-separated conditions to run")
    ap.add_argument("--out", default="results", help="results directory under this eval")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    roots = {"old": a.old_root.resolve(), "new": REPO}
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8")) if not a.ids or c["id"] in a.ids]
    jobs = [(c, cond, rep) for c in cases for cond in a.conds.split(",") for rep in range(1, a.reps + 1)]
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rra-revamp-") as tmp, cf.ThreadPoolExecutor(5) as ex:
        recs = list(ex.map(lambda j: run(j[0], j[1], j[2], roots[j[1]], pathlib.Path(tmp)), jobs))
        scrub = scrubber([(tmp, "<runs>"), (roots["old"], "<old-plugin>"), (REPO, "<new-plugin>"),
                          (sys.executable, "python"), (pathlib.Path.home(), "~")])
        recs = [scrub(r) for r in recs]
    for r in recs:
        r["verdict"] = verdict(r)
        (out / f"{r['id']}-{r['cond']}-{r['rep']}.json").write_text(
            json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        skill_bytes = sum(n or 0 for _, n in r["reads"])
        print(f"{r['verdict']:4} {r['id']:16} {r['cond']} {r['rep']} loaded={r['loaded']} reads={len(r['reads'])} "
              f"skill_bytes={skill_bytes} clones={r['clones']} denials={len(r['denials'] or [])} "
              f"turns={r['turns']} cost={r['cost']} rc={r['rc']}")
    print("total cost $%.2f" % sum(r["cost"] or 0 for r in recs))
