"""Run one headless Claude Code case and record skill usage + answer.

Each case picks `skills: "old"` (the skills at BASELINE) or `"new"` (this checkout's skills/),
and may override scaffold files with `patch: {relative path: content}`."""
import json, os, shutil, subprocess, sys, tempfile, time, pathlib
ROOT = pathlib.Path(__file__).parent
REPO = ROOT.parent.parent
SCAFFOLD = ROOT.parent / "sonnet-ab-2026-10-11" / "scaffold"
BASELINE = "cf9847e"  # main before the slimming


def skills_dir(which):
    if which == "new":
        return REPO / "skills"
    old = ROOT / "old" / "skills"
    if not old.exists():
        (ROOT / "old").mkdir(exist_ok=True)
        archive = subprocess.run(["git", "archive", BASELINE, "skills"], cwd=REPO, capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(ROOT / "old")], input=archive, check=True)
    return old

def make_project(case):
    (ROOT / "projects").mkdir(exist_ok=True)
    d = pathlib.Path(tempfile.mkdtemp(prefix="proj-", dir=ROOT / "projects"))
    shutil.copytree(SCAFFOLD, d, dirs_exist_ok=True)
    for rel, text in case.get("patch", {}).items():
        (d / rel).write_text(text)
    if case["with_skills"]:
        dst = d / ".claude" / "skills"
        dst.mkdir(parents=True)
        src = skills_dir(case.get("skills", "new"))
        # Library skills are nested in roblox-resource-acquisition/libraries/; install them flat.
        for s in [*src.iterdir(), *(src / "roblox-resource-acquisition" / "libraries").glob("*")]:
            if (s / "SKILL.md").exists():
                shutil.copytree(s, dst / s.name, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    return d

def run(case):
    proj = make_project(case)
    # Project/local settings only: user plugins, user skills and MCP servers stay out.
    env = dict(os.environ)
    cmd = ["claude", "-p", case["prompt"], "--model", case.get("model", "sonnet"),
           "--output-format", "stream-json", "--verbose",
           "--max-turns", str(case.get("max_turns", 12)),
           "--permission-mode", "acceptEdits",
           "--setting-sources", "project,local", "--strict-mcp-config",
           "--disallowedTools", "Bash,WebSearch,WebFetch,Agent,Task"]
    t = time.time()
    p = subprocess.run(cmd, cwd=proj, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900, stdin=subprocess.DEVNULL)
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
                    if c["name"] == "Read" and "/.claude/skills/" in str(c["input"].get("file_path", "")).replace("\\", "/"):
                        skills.append("read:" + str(c["input"]["file_path"]).replace("\\", "/").split("/.claude/skills/")[1])
        if ev.get("type") == "result":
            result, cost, turns = ev.get("result"), ev.get("total_cost_usd"), ev.get("num_turns")
    out = dict(case, skills=skills, tools=tools, result=result, cost=cost, turns=turns,
               seconds=round(time.time() - t, 1), rc=p.returncode, stderr=p.stderr[-500:], project=proj.relative_to(ROOT).as_posix())
    # capture files the model wrote
    written = {}
    for f in proj.rglob("*"):
        rel = f.relative_to(proj) if f.is_file() else None
        if not rel or ".claude" in f.parts:
            continue
        patched = case.get("patch", {}).get(rel.as_posix())
        before = patched.encode() if patched is not None else (SCAFFOLD / rel).read_bytes() if (SCAFFOLD / rel).exists() else None
        if before is None or before.replace(b"\r\n", b"\n") != f.read_bytes().replace(b"\r\n", b"\n"):
            written[str(f.relative_to(proj))] = f.read_text(errors="replace")[:6000]
    out["written"] = written
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / f"{case['id']}.json").write_text(json.dumps(out, indent=1))
    print(case["id"], "skills=", skills, "cost=", cost, "turns=", turns, flush=True)

if __name__ == "__main__":
    cases = {c["id"]: c for c in json.load(open(sys.argv[1]))}
    run(cases[sys.argv[2]])
