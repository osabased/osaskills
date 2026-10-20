"""Compare think-tank with a single Opus session on decisions whose confident answer is wrong.

Each case in cases.json is a question with a verified answer and a tempting wrong one; controls are
questions whose obvious answer is right. The "single" arm asks the question in a headless Opus session,
and the "verify" arm asks it with one line telling the session to check official docs first. The "panel"
arm runs `/think-tank <question>`, so the skill picks its default panel, and the "solo" arm runs this
folder's think-tank-solo variant, which asks one panelist and skips the debate. All arms run at the same
effort in a fresh temporary project holding this checkout's think-tank skill, the solo variant and the
panelist agent, with project settings only, so an installed osaskills plugin and a saved advisor stay out.
Panel and solo runs also record each panelist's answer to every message it got, from the run's subagent
transcripts, which are then deleted. Results have local paths replaced. Usage:
    python harness.py [--arms single,verify,solo,panel] [--effort high] [--model opus] [--panel-args "haiku low"] [--reps N] [--out results/NAME] [case-id ...]
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time, pathlib, concurrent.futures as cf
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent.parent
HOME = pathlib.Path.home()
PROJECTS = HOME / ".claude" / "projects"
MAIN = pathlib.Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()).parent
PREFIX = "tt-traps-"
ALLOW = "Read,Grep,Glob,WebSearch,WebFetch,Agent,Task,SendMessage,Skill,ToolSearch"
DENY = "Bash,PowerShell,Write,Edit,NotebookEdit"
NOTE = "The project I'm describing isn't in this directory."
VERIFY = "Before answering, check the current official documentation, and say which claims you verified."
ARMS = ("single", "verify", "solo", "panel")
WEB = ("WebSearch", "WebFetch")
KEY = re.compile(r"osabased", re.IGNORECASE)

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

def install(proj, case_id):
    shutil.copytree(REPO / "skills" / "think-tank", proj / ".claude" / "skills" / "think-tank")
    shutil.copytree(ROOT / "think-tank-solo", proj / ".claude" / "skills" / "think-tank-solo")
    (proj / ".claude" / "agents").mkdir(parents=True)
    shutil.copy(REPO / "agents" / "think-tank-member.md", proj / ".claude" / "agents")
    # --setting-sources doesn't stop the user's ~/.claude/CLAUDE.md from loading. Runs can also search the
    # home directory, where this repo holds the answer key, past sessions and installed skills hold answers,
    # and other runs of the same case keep their transcripts while they work.
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(MAIN))
    deny = [f"Read(~/{MAIN.relative_to(HOME).as_posix()}/**)", f"Read(~/.claude/projects/{slug}*/**)",
            "Read(~/.claude/plugins/**)", "Read(~/.claude/skills/**)"]
    deny += [f"Read(~/.claude/projects/*-{case_id}-{arm}-{n}/**)" for arm in ARMS for n in range(1, 10)
             if f"{case_id}-{arm}-{n}" != proj.name]
    # The answer key is also public on GitHub, and other GitHub pages hold sources runs need, so a hook
    # blocks fetches of that one repo rather than a deny rule on the whole domain.
    hook = f'"{pathlib.Path(sys.executable).as_posix()}" "{(ROOT / "block_key.py").as_posix()}"'
    settings = {"claudeMdExcludes": ["**/.claude/CLAUDE.md"], "permissions": {"deny": deny},
                "hooks": {"PreToolUse": [{"matcher": "WebFetch", "hooks": [{"type": "command", "command": hook}]}]}}
    (proj / ".claude" / "settings.json").write_text(json.dumps(settings), encoding="utf-8")

def step(name, inp):
    for key in ("description", "file_path", "pattern", "skill", "query", "url", "to", "path"):
        if inp.get(key):
            return [name, str(inp[key])[:300]]
    return [name, ""]

def key_hits(events):
    """Web lookups whose input or result mentions the public repo that holds the answer key."""
    web, hits = {}, []
    for ev in events:
        content = (ev.get("message") or {}).get("content")
        for c in content if isinstance(content, list) else []:
            if not isinstance(c, dict):
                continue
            if c.get("type") in ("tool_use", "server_tool_use") and c.get("name") in WEB:
                web[c["id"]] = step(c["name"], c.get("input", {}))
                if KEY.search(json.dumps(c.get("input"))):
                    hits.append(web[c["id"]] + ["input"])
            if c.get("type") == "tool_result" and c.get("tool_use_id") in web and KEY.search(json.dumps(c.get("content"))):
                hits.append(web[c["tool_use_id"]] + ["result"])
    return hits

def texts_of(content):
    if isinstance(content, str):
        return [content]
    return [c["text"] for c in content if isinstance(c, dict) and c.get("type") == "text"]

def panelist(path):
    """One subagent transcript as the prompts it got and its final reply to each."""
    turns, models, tools, advisor, attached, events = [], set(), [], 0, False, []
    for line in path.read_text(encoding="utf-8").splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        events.append(ev)
        if (ev.get("attachment") or {}).get("type") == "advisor_tool":
            attached = True
        msg = ev.get("message") or {}
        if ev.get("type") == "user":
            content = msg.get("content")
            if isinstance(content, list) and any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
                continue
            turns.append({"prompt": "\n".join(texts_of(content)), "reply": ""})
        elif ev.get("type") == "assistant":
            models.add(msg.get("model"))
            for c in msg.get("content", []):
                if c.get("type") in ("tool_use", "server_tool_use"):
                    tools.append(c["name"])
                    advisor += c["name"] == "advisor"
            text = "\n".join(texts_of(msg.get("content", [])))
            if text.strip() and turns:
                turns[-1]["reply"] = text
    return {"agent_id": path.stem.removeprefix("agent-"), "models": sorted(m for m in models if m),
            "tools": tools, "advisor_attached": attached, "advisor_calls": advisor, "key_hits": key_hits(events),
            "turns": turns}

def run(case, arm, rep, model, effort, panel_args, workdir):
    proj = workdir / f"{case['id']}-{arm}-{rep}"
    install(proj, case["id"])
    question = f"{case['prompt']} {NOTE}"
    prompt = {"single": question, "verify": f"{case['prompt']} {VERIFY} {NOTE}",
              "solo": " ".join(filter(None, ["/think-tank-solo", panel_args, question])),
              "panel": " ".join(filter(None, ["/think-tank", panel_args, question]))}[arm]
    cmd = ["claude", "-p", prompt, "--model", model, "--effort", effort, "--output-format", "stream-json",
           "--verbose", "--max-turns", "80", "--setting-sources", "project,local", "--strict-mcp-config",
           "--allowedTools", ALLOW, "--disallowedTools", DENY]
    started = time.time()
    p = subprocess.run(cmd, cwd=proj, env=clean_env(), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=3600, stdin=subprocess.DEVNULL)
    session = result = cost = turns = usage = model_usage = denials = None
    steps, texts, spawned, agent_ids, events = [], [], {}, {}, []
    for line in p.stdout.splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        if not ev.get("parent_tool_use_id"):
            events.append(ev)
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init":
            session = ev.get("session_id")
        if t == "assistant" and not ev.get("parent_tool_use_id"):
            for c in ev["message"].get("content", []):
                if c.get("type") == "text":
                    texts.append(c["text"])
                if c.get("type") in ("tool_use", "server_tool_use"):
                    inp = c.get("input", {})
                    steps.append(step(c["name"], inp))
                    if c["name"] in ("Agent", "Task"):
                        spawned[c["id"]] = {"description": inp.get("description"), "model": inp.get("model"),
                                            "effort": inp.get("effort"), "type": inp.get("subagent_type")}
        if t == "user" and not ev.get("parent_tool_use_id"):
            for c in ev.get("message", {}).get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in spawned:
                    found = re.search(r"agentId:\s*(\w+)", json.dumps(c.get("content")))
                    if found:
                        agent_ids[found.group(1)] = spawned[c["tool_use_id"]]
        if t == "result":
            result, cost, turns = ev.get("result"), ev.get("total_cost_usd"), ev.get("num_turns")
            usage, model_usage = ev.get("usage"), ev.get("modelUsage")
            denials = [step(d.get("tool_name", ""), d.get("tool_input", {})) for d in ev.get("permission_denials") or []]
    panelists = []
    for d in PROJECTS.glob(f"*{PREFIX}*"):
        if session and ((d / session).exists() or (d / f"{session}.jsonl").exists()):
            for f in sorted((d / session / "subagents").glob("agent-*.jsonl")):
                rec = panelist(f)
                rec.update(agent_ids.get(rec["agent_id"], {}))
                panelists.append(rec)
            shutil.rmtree(d, ignore_errors=True)
    hits = key_hits(events) + [h for x in panelists for h in x["key_hits"]]
    return dict(case, arm=arm, rep=rep, model=model, effort=effort, panel_args=panel_args, result=result, texts=texts, steps=steps,
                panelists=panelists, key_hits=hits, cost=cost, turns=turns, minutes=round((time.time() - started) / 60, 1),
                usage=usage, model_usage=model_usage, denials=denials, rc=p.returncode, stderr=p.stderr[-400:])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="single,panel")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--model", default="opus", help="the session model in every arm")
    ap.add_argument("--panel-args", default="", help="model and effort words passed to /think-tank or /think-tank-solo before the question")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results", help="results directory under this eval")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8")) if not a.ids or c["id"] in a.ids]
    jobs =[(c, arm, rep) for rep in range(1, a.reps + 1) for arm in a.arms.split(",") for c in cases]
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True, env=clean_env()).stdout.strip()
    with tempfile.TemporaryDirectory(prefix=PREFIX) as tmp, cf.ThreadPoolExecutor(a.workers) as ex:
        recs = list(ex.map(lambda j: run(*j, a.model, a.effort, a.panel_args, pathlib.Path(tmp)), jobs))
        scrub = scrubber([(tmp, "<runs>"), (REPO, "<repo>"), (HOME, "~")])
        home_slug = re.sub(r"[^A-Za-z0-9]", "-", str(HOME))
        recs = [json.loads(json.dumps(scrub(r)).replace(home_slug, "<home>")) for r in recs]
    for r in recs:
        r["cli"] = version
        (out / f"{r['id']}-{r['arm']}-{r['rep']}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        models = {m: round(u.get("costUSD", 0), 3) for m, u in (r["model_usage"] or {}).items()}
        print(f"{r['id']:18} {r['arm']:6} {r['rep']} cost={r['cost']} turns={r['turns']} min={r['minutes']} "
              f"panelists={len(r['panelists'])} advisor={sum(x['advisor_calls'] for x in r['panelists'])} "
              f"denials={len(r['denials'] or [])} key_hits={len(r['key_hits'])} rc={r['rc']} by_model={models}")
    print("total cost $%.2f" % sum(r["cost"] or 0 for r in recs))
