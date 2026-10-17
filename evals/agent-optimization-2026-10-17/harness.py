"""Check trimmed skill descriptions and the non-Rojo routes of structure-roblox-projects on several models.

Trigger cases repeat the trigger prompts of structure-revamp-2026-10-15 ("srp" suite) and
resource-revamp-2026-10-15 ("rra" suite), each installed as that eval installed it, and run under the
skills on main ("old") and this checkout ("new"). Quality cases run under "new" and "bare", which is
"new" without structure-roblox-projects. Each run copies the case's scaffold and one version's skills
into a temporary project and runs headless Claude Code there with project settings only, so an
installed osaskills plugin stays out of it. "old" is a plugin tree you extract, for example
`git archive origin/main skills hooks | tar -x -C <dir>`. Results have local paths replaced. Usage:
    python harness.py --old-root <dir> [--models sonnet,haiku] [--reps N] [--conds old,new,bare] [--out results] [case-id ...]
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, pathlib, concurrent.futures as cf
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent.parent
SCAFFOLDS = {"base": ROOT.parent / "sonnet-ab-2026-10-11" / "scaffold",
             "game": ROOT.parent / "structure-revamp-2026-10-15" / "scaffold",
             "coin": ROOT.parent / "resource-revamp-2026-10-15" / "scaffold",
             "sync": ROOT / "scaffold-sync", "studio": ROOT / "scaffold-studio"}
SESSION_HOOK = ROOT.parent / "resource-revamp-2026-10-15" / "session_hook.py"
CONDS = {"trigger": ("old", "new"), "quality": ("new", "bare")}
DENY = {"trigger": "Bash,PowerShell,Write,Edit,WebSearch,WebFetch,Agent,Task",
        "quality": "Bash,PowerShell,WebSearch,WebFetch,Agent,Task"}
RRA = "roblox-resource-acquisition"

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

def install(plugin, case, cond, proj):
    skills = proj / ".claude" / "skills"
    top = [s for s in (plugin / "skills").iterdir() if (s / "SKILL.md").exists()]
    if cond == "bare":
        top = [s for s in top if s.name != "structure-roblox-projects"]
    if case["suite"] == "srp":
        libraries = [s for s in (plugin / "skills" / RRA / "libraries").iterdir() if (s / "SKILL.md").exists()]
    else:
        libraries = [plugin / "skills" / RRA / "libraries" / name for name in case.get("clones", [])]
    for s in [*top, *libraries]:
        shutil.copytree(s, skills / s.name, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    if case["suite"] == "rra":
        hook = f'python "{SESSION_HOOK.as_posix()}" "{plugin.as_posix()}"'
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

def run(case, model, cond, rep, plugin, workdir):
    scaffold = SCAFFOLDS[case["scaffold"]]
    proj = workdir / f"{case['id']}-{model}-{cond}-{rep}"
    shutil.copytree(scaffold, proj)
    install(plugin, case, cond, proj)
    cmd = ["claude", "-p", case["prompt"], "--model", model, "--output-format", "stream-json", "--verbose",
           "--max-turns", str(case["max_turns"]), "--setting-sources", "project,local", "--strict-mcp-config",
           "--permission-mode", "acceptEdits", "--disallowedTools", DENY[case["kind"]]]
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
    return dict(case, model=model, cond=cond, rep=rep, loaded=loaded, reads=reads, steps=steps, denials=denials,
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
    ap.add_argument("--models", default="sonnet,haiku", help="comma-separated --model values")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--conds", default="old,new,bare", help="comma-separated conditions to run where a case allows them")
    ap.add_argument("--out", default="results", help="results directory under this eval")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    roots = {"old": a.old_root.resolve(), "new": REPO, "bare": REPO}
    conds = a.conds.split(",")
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8")) if not a.ids or c["id"] in a.ids]
    jobs = [(c, m, cond, rep) for c in cases for m in a.models.split(",") for cond in CONDS[c["kind"]]
            if cond in conds for rep in range(1, a.reps + 1)]
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True, env=clean_env()).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="agent-opt-") as tmp, cf.ThreadPoolExecutor(5) as ex:
        recs = list(ex.map(lambda j: run(*j, roots[j[2]], pathlib.Path(tmp)), jobs))
        scrub = scrubber([(tmp, "<runs>"), (roots["old"], "<old-plugin>"), (REPO, "<new-plugin>"),
                          (sys.executable, "python"), (pathlib.Path.home(), "~")])
        recs = [scrub(r) for r in recs]
    passes = Counter()
    for r in recs:
        r["verdict"], r["cli"] = verdict(r), version
        (out / f"{r['id']}-{r['model']}-{r['cond']}-{r['rep']}.json").write_text(
            json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        if r["verdict"] != "-":
            passes[(r["suite"], r["model"], r["cond"])] += r["verdict"] == "PASS"
            passes[(r["suite"], r["model"], r["cond"], "n")] += 1
        skill_bytes = sum(n or 0 for _, n in r["reads"])
        print(f"{r['verdict']:4} {r['id']:16} {r['model']:6} {r['cond']:4} {r['rep']} loaded={r['loaded']} "
              f"reads={len(r['reads'])} skill_bytes={skill_bytes} turns={r['turns']} cost={r['cost']} rc={r['rc']}")
    for key in sorted(k for k in passes if len(k) == 3):
        print("%s %s %s: %d/%d trigger checks pass" % (*key, passes[key], passes[(*key, "n")]))
    print("total cost $%.2f" % sum(r["cost"] or 0 for r in recs))
