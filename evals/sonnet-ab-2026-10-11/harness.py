"""Run one headless Claude Code case and record skill usage + answer."""
import json, os, shutil, subprocess, sys, tempfile, time, pathlib
ROOT = pathlib.Path(__file__).parent
REPO = ROOT.parent.parent
SCAFFOLD = ROOT / "scaffold"

def make_project(with_skills):
    d = pathlib.Path(tempfile.mkdtemp(prefix="proj-", dir=ROOT / "projects"))
    shutil.copytree(SCAFFOLD, d, dirs_exist_ok=True)
    if with_skills:
        dst = d / ".claude" / "skills"
        dst.mkdir(parents=True)
        src = REPO / "skills"
        # Library skills are nested in roblox-resource-acquisition/libraries/; install them flat.
        for s in [*src.iterdir(), *(src / "roblox-resource-acquisition" / "libraries").glob("*")]:
            if (s / "SKILL.md").exists():
                shutil.copytree(s, dst / s.name, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    return d

def run(case):
    proj = make_project(case["with_skills"])
    cfg = ROOT / "cfgs" / case["id"]
    cfg.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, CLAUDE_CONFIG_DIR=str(cfg))
    cmd = ["claude", "-p", case["prompt"], "--model", case.get("model", "sonnet"),
           "--output-format", "stream-json", "--verbose",
           "--max-turns", str(case.get("max_turns", 12)),
           "--permission-mode", "acceptEdits",
           "--disallowedTools", "Bash,WebSearch,WebFetch,Agent,Task"]
    t = time.time()
    p = subprocess.run(cmd, cwd=proj, env=env, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    skills, tools, result, cost, turns = [], [], None, None, None
    for line in p.stdout.splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    tools.append(c["name"])
                    if c["name"] == "Skill":
                        skills.append(c["input"].get("skill") or c["input"].get("command"))
                    if c["name"] == "Read" and "/.claude/skills/" in str(c["input"].get("file_path", "")):
                        skills.append("read:" + str(c["input"]["file_path"]).split("/.claude/skills/")[1])
        if ev.get("type") == "result":
            result, cost, turns = ev.get("result"), ev.get("total_cost_usd"), ev.get("num_turns")
    out = dict(case, skills=skills, tools=tools, result=result, cost=cost, turns=turns,
               seconds=round(time.time() - t, 1), rc=p.returncode, stderr=p.stderr[-500:], project=str(proj))
    # capture files the model wrote
    written = {}
    for f in proj.rglob("*"):
        if f.is_file() and ".claude" not in f.parts and not (SCAFFOLD / f.relative_to(proj)).exists():
            written[str(f.relative_to(proj))] = f.read_text(errors="replace")[:6000]
    out["written"] = written
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / f"{case['id']}.json").write_text(json.dumps(out, indent=1))
    print(case["id"], "skills=", skills, "cost=", cost, "turns=", turns, flush=True)

if __name__ == "__main__":
    cases = {c["id"]: c for c in json.load(open(sys.argv[1]))}
    run(cases[sys.argv[2]])
