"""Check skill triggering against the installed osaskills plugin.

Uses your normal Claude Code config, so install the plugin first, or pass --plugin-dir to load
a checkout instead (with the plugin not installed, so it isn't loaded twice). Usage:
    python harness.py [--cli PATH] [--plugin-dir DIR] [case-id ...]
"""
import argparse, json, os, shutil, subprocess, tempfile, pathlib, concurrent.futures as cf
ROOT = pathlib.Path(__file__).parent
SCAFFOLD = ROOT.parent / "sonnet-ab-2026-10-11" / "scaffold"

def clean_env():
    # Drop a parent Claude session's variables so the child uses its own login.
    drop = ("CLAUDE", "ANTHROPIC", "USE_LOCAL_OAUTH", "USE_STAGING_OAUTH")
    return {k: v for k, v in os.environ.items() if not k.upper().startswith(drop)}

def run(cli, case, workdir, plugin_dir=None):
    proj = workdir / case["id"]
    shutil.copytree(SCAFFOLD, proj)
    cmd = [cli, "-p", case["prompt"], "--model", "sonnet", "--output-format", "stream-json", "--verbose",
           "--max-turns", str(case.get("max_turns", 3)),
           "--disallowedTools", "Bash,PowerShell,Write,Edit,WebSearch,WebFetch,Agent,Task"]
    if plugin_dir:
        # Headless runs can't approve reads outside the project, so grant the checkout
        # (an installed plugin's skill files are readable without a prompt).
        cmd += ["--plugin-dir", plugin_dir, "--add-dir", plugin_dir]
    p = subprocess.run(cmd, cwd=proj, env=clean_env(), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600, stdin=subprocess.DEVNULL)
    loaded, reads, denied, tools, result, cost, init_skills = [], [], [], [], None, None, []
    pending = {}  # tool_use id -> skill-relative path of a Read
    for line in p.stdout.splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init":
            init_skills = [s for s in ev.get("skills", []) if s.startswith("osaskills:")]
        if t == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") != "tool_use": continue
                tools.append(c["name"])
                inp = c.get("input", {})
                if c["name"] == "Skill":
                    loaded.append("tool:" + str(inp.get("skill") or inp.get("command")))
                path = str(inp.get("file_path", "")).replace("\\", "/")
                if c["name"] == "Read" and "/skills/" in path:
                    pending[c.get("id")] = path.split("/skills/", 1)[1]
                    if path.endswith("SKILL.md"):
                        # The skill is the SKILL.md's own folder (library skills are nested).
                        loaded.append("read:" + pathlib.PurePosixPath(path).parent.name)
        if t == "user":
            # A Read counts only once its result comes back without an error (e.g. a permission denial).
            for c in ev.get("message", {}).get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in pending:
                    (denied if c.get("is_error") else reads).append(pending.pop(c["tool_use_id"]))
        if t == "result":
            result, cost = ev.get("result"), ev.get("total_cost_usd")
    # Results are committed, so drop the local temp path a reply may quote.
    result = result and result.replace(str(workdir), "<tmp>")
    return dict(case, loaded=loaded, reads=reads, denied=denied, tools=tools, cost=cost, rc=p.returncode,
                init_skills=len(init_skills), result=result, stderr=p.stderr[-400:])

def verdict(r):
    e = r["expect"]
    if e is None: return "INFO"
    hit = any(e.lstrip("!") in x for x in r["loaded"])
    if e.startswith("!"): return "PASS" if not hit else "FAIL"
    if not hit and r.get("markers"):
        # A slash-invoked skill expands into the prompt and leaves no tool event,
        # so judge it by a format cue from that skill's instructions.
        hit = any(m.lower() in (r["result"] or "").lower() for m in r["markers"])
    if hit and r.get("reads_expect"):
        # The skill must also reach this file (for a library skill, the parent's shared contract).
        hit = any(x.endswith(r["reads_expect"]) for x in r["reads"])
    return "PASS" if hit else "FAIL"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", default=shutil.which("claude") or "claude")
    ap.add_argument("--plugin-dir", help="load the plugin from this checkout instead of the installed copy")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8")) if not a.ids or c["id"] in a.ids]
    (ROOT / "results").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osaskills-trigger-") as tmp, cf.ThreadPoolExecutor(5) as ex:
        recs = list(ex.map(lambda c: run(a.cli, c, pathlib.Path(tmp), a.plugin_dir), cases))
    for r in recs:
        r["verdict"] = verdict(r)
        (ROOT / "results" / f"{r['id']}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{r['verdict']:5} {r['id']:18} loaded={r['loaded']} reads={len(r['reads'])} denied={r['denied']} init_skills={r['init_skills']} rc={r['rc']}")
    print("total cost $%.2f" % sum(r["cost"] or 0 for r in recs))
