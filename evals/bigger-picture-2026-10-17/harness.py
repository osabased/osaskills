"""Check when bigger-picture triggers in multi-turn sessions, and how long and how plain its output is.

Each case is a sequence of user turns sent to one headless session (`claude -p`, then `--resume`)
in a fresh copy of scaffold/. Load the plugin from a checkout with --plugin-dir. Usage:
    python harness.py --plugin-dir DIR [--model sonnet] [--runs 1] [case-id ...]
"""
import argparse, json, os, re, shutil, subprocess, tempfile, pathlib, uuid, concurrent.futures as cf
ROOT = pathlib.Path(__file__).parent
SCAFFOLD = ROOT / "scaffold"
BASE = {
    "@base1": "I want a wishlist that follows me across devices. Start by adding a heart button on each product that adds it to a wishlist.",
    "@base2": "Now make the wishlist save to the signed-in user's account with PUT /api/wishlist/:userId, so it shows up on my other devices.",
    "@base3": "Load it back from the API when the page opens.",
    "@base3-login": "Load it back from the API when the page opens, and add a line on the login page telling people to sign in to keep their wishlist.",
}
PLAN = """# Plan: wishlist

1. Add a heart button on each product that adds it to a wishlist.
2. Save the wishlist to the signed-in user's account (PUT /api/wishlist/:userId) and load it when the page opens.
3. Rename the "Preferences" link in the header to "Settings".
4. Move the files in src/ into feature folders (src/features/header/, src/features/products/, and so on).
5. Show a wishlist count in the header.
"""
IMPL = re.compile(r"`|\b[\w-]+\.(?:js|html|json|md)\b|\b\w+\(|localStorage|PUT\b|/api/")
TAGS = ["Done", "Done, not asked for but needed", "Next", "Next, not asked for but needed", "Kept", "Skipped"]
OFF = "Not needed for the goal"

def clean_env():
    # Drop a parent Claude session's variables so the child uses its own login.
    drop = ("CLAUDE", "ANTHROPIC", "USE_LOCAL_OAUTH", "USE_STAGING_OAUTH")
    return {k: v for k, v in os.environ.items() if not k.upper().startswith(drop)}

def turn(cli, prompt, proj, session, first, model, plugin_dir):
    cmd = [cli, "-p", prompt, "--model", model, "--output-format", "stream-json", "--verbose",
           "--max-turns", "15", "--permission-mode", "acceptEdits",
           "--disallowedTools", "Bash,PowerShell,WebSearch,WebFetch,Agent,Task",
           "--plugin-dir", plugin_dir, "--add-dir", plugin_dir]
    cmd += ["--session-id", session] if first else ["--resume", session]
    p = subprocess.run(cmd, cwd=proj, env=clean_env(), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900, stdin=subprocess.DEVNULL)
    skills, text, trace, cost, init = [], [], [], None, []
    for line in p.stdout.splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            init = [s for s in ev.get("skills", []) if "bigger-picture" in s or "then-what" in s]
        if ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    trace.append("tool:" + c["name"])
                    if c["name"] == "Skill":
                        skills.append(str(c["input"].get("skill") or c["input"].get("command")))
                if c.get("type") == "text":
                    text.append(c["text"])
                    trace.append("text:" + c["text"][:60])
        if ev.get("type") == "result":
            cost = ev.get("total_cost_usd")
    return dict(prompt=prompt, skills=skills, text="\n\n".join(text), trace=trace, cost=cost, rc=p.returncode,
                init=init, stderr=p.stderr[-300:])

def block(text):
    # The bigger-picture output: from its Goal line through the bullets under "Not needed for the goal".
    m = re.search(r"(?:🎯\s*)?\**Goal\b.*?" + OFF + r"[^\n]*(?:\n[ \t>]*\n?[ \t>]*[-*•][^\n]*)*", text, re.S)
    return m.group(0) if m else None

def bullets(out):
    lines = [re.sub(r"^[\s>]*", "", l) for l in out.splitlines()]
    return [re.sub(r"^[-*•]\s*", "", l) for l in lines if re.match(r"[-*•]\s", l)]

def shape(out):
    # Both headings, no quote markers, a Goal line without steps, known tags in the skill's order,
    # one Skipped, every bullet under 20 words.
    bs = bullets(out)
    tags = [b.split(":")[0].strip("* ") for b in bs]
    known = all(t in TAGS for t in tags)
    quoted = re.search(r"^\s*>", out, re.M) is not None
    steps = re.search(r"starting with|start(?:ing)? by|, then\b", out.splitlines()[0], re.I) is not None
    short = all(len(b.split()) < 20 for b in bs)
    return ("Helps the goal" in out and not quoted and not steps and known and short and len(tags) <= 6
            and tags.count("Skipped") <= 1 and tags == sorted(tags, key=TAGS.index)), tags

def grade(case, turns):
    checked = turns[case["check_from"]:]
    loaded = any("bigger-picture" in s for t in turns for s in t["skills"])
    loaded_checked = any("bigger-picture" in s for t in checked for s in t["skills"])
    out = next((b for t in reversed(checked) if (b := block(t["text"]))), None)
    q = {}
    if out:
        off = out[out.find(OFF):].lower()
        shape_ok, tags = shape(out)
        q = dict(words=len(re.sub(r"[*🎯⚠️>]|^\s*[-•]\s", "", out, flags=re.M).split()),
                 max_bullet_words=max((len(b.split()) for b in bullets(out)), default=0),
                 shape_ok=shape_ok, tags=tags, impl=sorted(set(IMPL.findall(out))),
                 off_goal_hits=[w for w in case.get("off_goal", []) if w in off])
    e = case["expect"]
    # A check the user can't see doesn't count, so a trigger also needs the printed output.
    if e == "trigger": ok = loaded_checked and out is not None and q["shape_ok"]
    elif e == "none": ok = not loaded
    else: ok = out is not None and q["shape_ok"]
    if ok and case.get("off_goal") and out is not None:
        ok = len(q["off_goal_hits"]) == len(case["off_goal"])
    return ("PASS" if ok else "FAIL"), dict(loaded=loaded, loaded_in_checked=loaded_checked, output=out, **q)

def run(cli, case, n, model, plugin_dir, workdir):
    proj = workdir / f"{model}-{case['id']}-{n}"
    shutil.copytree(SCAFFOLD, proj)
    if case.get("plan"):
        (proj / "PLAN.md").write_text(PLAN, encoding="utf-8")
    session, turns = str(uuid.uuid4()), []
    for i, t in enumerate(case["turns"]):
        turns.append(turn(cli, BASE.get(t, t), proj, session, i == 0, model, plugin_dir))
    verdict, g = grade(case, turns)
    for t in turns:
        t["text"] = t["text"].replace(str(proj), "<proj>")
    return dict(id=case["id"], run=n, model=model, expect=case["expect"], soft=case.get("soft", False),
                verdict=verdict, **g, cost=sum(t["cost"] or 0 for t in turns), turns=turns)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", default=shutil.which("claude") or "claude")
    ap.add_argument("--plugin-dir", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--out", default="results")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8")) if not a.ids or c["id"] in a.ids]
    jobs = [(c, n) for c in cases for n in range(1, a.runs + 1)]
    out = ROOT / a.out / a.model
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osaskills-bp-") as tmp, cf.ThreadPoolExecutor(5) as ex:
        recs = list(ex.map(lambda j: run(a.cli, j[0], j[1], a.model, a.plugin_dir, pathlib.Path(tmp)), jobs))
    for r in recs:
        (out / f"{r['id']}-{r['run']}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        soft = " (soft)" if r["soft"] else ""
        print(f"{r['verdict']:5} {r['id']:15}{soft:7} run={r['run']} loaded={r['loaded_in_checked']} "
              f"words={r.get('words')} bullet<={r.get('max_bullet_words')} tags={r.get('tags')} "
              f"impl={r.get('impl')} off={r.get('off_goal_hits')} ${r['cost']:.2f}")
    print("total cost $%.2f" % sum(r["cost"] for r in recs))
