"""The standing eval subset that gates changes to skills, hooks and agents.

Three kinds of case in cases.json run against this checkout loaded as the plugin (`--plugin-dir`), in a fresh
copy of the Sonnet comparison's scaffold, with project settings only and the user's CLAUDE.md, transcripts and
installed skills excluded:
- registered: the init event lists every skill, so a plugin or frontmatter break shows before any model call;
- trigger: a prompt loads the expected skill (through the Skill tool or by reading its SKILL.md), does not load a
  skill marked `!name`, or, for a slash-invoked skill that leaves no tool event, answers in that skill's format;
- judged: a short task graded by a second model against the case's ground truth and criteria, pooled over reps.
Each run writes one JSON record under --out. Then one ledger row per model is built, compared with the baseline
in evals/ledger.jsonl, appended, and the exit code is 1 on a regression. Two rules keep the baseline honest:
- A run narrowed to fewer cases than the full subset (case ids, or --kinds without every kind) writes its rows
  with cond "partial" instead of "new". The comparison reads only cond "new" rows, so a partial run is judged
  but never judged against.
- Every gate row carries gate_ok, the gate's own decision for it. The baseline is the latest cond "new" row for
  the model whose gate_ok is not false, so one regression keeps failing until the rate recovers.
CI commits nothing back, so its baseline is the committed ledger: to move it, run the gate locally and commit
evals/ledger.jsonl. Usage:
    python harness.py [--plugin-dir DIR] [--model haiku] [--judge-model sonnet] [--reps 3] [--judged-reps 3]
                      [--kinds registered,trigger,judged] [--out results/<stamp>] [--no-ledger] [case-id ...]
"""
import argparse, datetime, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time, concurrent.futures as cf
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(ROOT.parent / "_lib"))
import isolation, ledger
SCAFFOLD = ROOT.parent / "sonnet-ab-2026-10-11" / "scaffold"
DENY = "Bash,PowerShell,Write,Edit,NotebookEdit,WebSearch,WebFetch,Agent,Task"
JUDGE_DENY = DENY + ",Read,Glob,Grep,Skill,ToolSearch"
KINDS = ("registered", "trigger", "judged")


def env():
    e = isolation.clean_env()
    # clean_env drops a parent session's ANTHROPIC_* variables; CI has no session and needs its key.
    if os.environ.get("CI") and os.environ.get("ANTHROPIC_API_KEY"):
        e["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]
    return e


def claude(prompt, cwd, model, max_turns, deny, plugin_dir=None, timeout=900):
    cmd = ["claude", "-p", prompt, "--model", model, *isolation.FLAGS, "--max-turns", str(max_turns),
           "--disallowedTools", deny]
    if plugin_dir:
        # A headless run can't approve reads outside the project, so the checkout's skill files need --add-dir.
        cmd += ["--plugin-dir", str(plugin_dir), "--add-dir", str(plugin_dir)]
    p = subprocess.run(cmd, cwd=cwd, env=env(), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
    return p, isolation.events(p.stdout)


def parse(evs):
    loaded, init_skills, result, cost, pending = [], [], None, None, {}
    for ev in evs:
        t = ev.get("type")
        if t == "system" and ev.get("subtype") == "init":
            init_skills = [s for s in ev.get("skills", []) if s.startswith("osaskills:")]
        if t == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") != "tool_use":
                    continue
                inp = c.get("input", {})
                if c["name"] == "Skill":
                    loaded.append("tool:" + str(inp.get("skill") or inp.get("command")))
                path = str(inp.get("file_path", "")).replace("\\", "/")
                if c["name"] == "Read" and "/skills/" in path and path.endswith("SKILL.md"):
                    pending[c.get("id")] = "read:" + pathlib.PurePosixPath(path).parent.name
        if t == "user":
            # A read counts once its result comes back without an error such as a permission denial.
            for c in ev.get("message", {}).get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in pending:
                    name = pending.pop(c["tool_use_id"])
                    if not c.get("is_error"):
                        loaded.append(name)
        if t == "result":
            result, cost = ev.get("result"), ev.get("total_cost_usd")
    return loaded, init_skills, result, cost


def hit(skill, loaded):
    return any(x.split(":")[-1].split("/")[-1] == skill for x in loaded)


def checks(r):
    """(skill, verdict) pairs a run record settles."""
    if r["kind"] == "registered":
        return [(s, "PASS" if f"osaskills:{s}" in r["init_skills"] else "FAIL") for s in r["skills"]]
    if r["kind"] != "trigger":
        return []
    out = []
    for e in [r["expect"]] if isinstance(r["expect"], str) else r["expect"]:
        skill, want = e.lstrip("!"), not e.startswith("!")
        got = hit(skill, r["loaded"])
        if want and not got and r.get("markers"):
            got = any(m.lower() in (r["result"] or "").lower() for m in r["markers"])
        out.append((skill, "PASS" if got == want else "FAIL"))
    return out


def run(case, rep, model, plugin_dir, workdir):
    proj = workdir / f"{case['id']}-{rep}"
    shutil.copytree(SCAFFOLD, proj)
    isolation.isolate(proj)
    p, evs = claude(case["prompt"], proj, model, case.get("max_turns", 3), DENY, plugin_dir)
    loaded, init_skills, result, cost = parse(evs)
    result = result and result.replace(str(workdir), "<runs>")
    return dict(case, rep=rep, model=model, loaded=loaded, init_skills=init_skills, result=result, cost=cost,
                models=isolation.model_ids(evs), rc=p.returncode, stderr=p.stderr[-400:])


def judge(r, judge_model, workdir):
    """Grade a judged run's answer: the judge sees the question, the ground truth, the criteria and the answer."""
    crit = "\n".join(f"- {k}: {v}" for k, v in r["criteria"].items())
    prompt = (f"You are grading one answer to a question against verified ground truth.\n\nQuestion:\n{r['prompt']}\n\n"
              f"Ground truth:\n{r['truth']}\n\nCriteria:\n{crit}\n\nAnswer:\n<answer>\n{r['result'] or ''}\n</answer>\n\n"
              "Decide for each criterion whether the answer meets it. Reply with only a JSON object mapping each "
              "criterion id to true or false, and nothing else.")
    proj = workdir / f"judge-{r['id']}-{r['rep']}"
    proj.mkdir()
    isolation.isolate(proj)
    p, evs = claude(prompt, proj, judge_model, 1, JUDGE_DENY)
    _, _, text, cost = parse(evs)
    found = re.search(r"\{.*\}", text or "", re.S)
    try:
        grades = json.loads(found.group(0)) if found else {}
    except ValueError:
        grades = {}
    r["grades"] = {k: bool(grades.get(k)) for k in r["criteria"]}
    r["judge_cost"], r["judge_models"], r["judge_raw"] = cost, isolation.model_ids(evs), (text or "")[-400:]
    return r


def judged_score(recs):
    graded = [r for r in recs if r.get("grades")]
    if not graded:
        return None
    passes = sum(sum(r["grades"].values()) for r in graded)
    total = sum(len(r["grades"]) for r in graded)
    return {"metric": "criteria", "score": round(passes / total, 3), "n": len(graded), "passes": passes, "total": total}


def cond_for(ids, kinds):
    return "partial" if ids or set(kinds) != set(KINDS) else "new"


def evaluate(previous, rows, trigger_tol, judge_tol, out=None):
    """Decide each new row against the last passing cond "new" row for its model, mark it, and return the failures."""
    out = out or sys.stdout
    fails = []
    for row in rows:
        base = ledger.baseline(previous, "gate", row["model"], passing=True, cond="new")
        print("gate: new      " + ledger.line(row), file=out)
        if base:
            print("gate: baseline " + ledger.line(base), file=out)
            mine = ledger.gate_decision(base, row, trigger_tol, judge_tol)
        else:
            print(f"gate: no earlier passing gate row for {row['model']}; this run sets the baseline", file=out)
            mine = []
        row["gate_ok"] = not mine
        row["note"] = ("FAIL: " + "; ".join(mine)) if mine else "pass"
        fails += mine
    return fails


def flatten(recs):
    """One record per check, carrying each run's cost once, for the ledger's per-skill counts."""
    out = []
    for r in recs:
        cs = checks(r) or [(None, "-")]
        for i, (skill, verdict) in enumerate(cs):
            out.append({"id": r["id"], "model": r["model"], "skill": skill, "verdict": verdict,
                        "cost": ((r.get("cost") or 0) + (r.get("judge_cost") or 0)) if i == 0 else None})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plugin-dir", default=REPO, type=pathlib.Path)
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--judge-model", default="sonnet")
    ap.add_argument("--reps", type=int, default=3, help="runs per trigger case")
    ap.add_argument("--judged-reps", type=int, default=3, help="runs per judged case; the gate needs at least 2")
    ap.add_argument("--kinds", default=",".join(KINDS))
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--out", default=None, help="results directory under this eval; default results/<timestamp>")
    ap.add_argument("--no-ledger", action="store_true", help="write results only; no ledger row and no gate")
    ap.add_argument("--trigger-tol", type=float, default=0.2)
    ap.add_argument("--judge-tol", type=float, default=0.04)
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    out = ROOT / (a.out or f"results/{stamp}")
    out.mkdir(parents=True, exist_ok=True)
    kinds = a.kinds.split(",")
    cond = cond_for(a.ids, kinds)
    if cond == "partial":
        print("partial run: its rows are recorded as cond partial and never become a baseline")
    cases = [c for c in json.load(open(ROOT / "cases.json", encoding="utf-8"))
             if c["kind"] in kinds and (not a.ids or c["id"] in a.ids)]
    reps = {"registered": 1, "trigger": a.reps, "judged": a.judged_reps}
    jobs = [(c, rep) for c in cases for rep in range(1, reps[c["kind"]] + 1)]
    plugin_dir = a.plugin_dir.resolve()
    version = isolation.cli_version()
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="osaskills-gate-") as tmp, cf.ThreadPoolExecutor(a.workers) as ex:
        work = pathlib.Path(tmp)
        recs = list(ex.map(lambda j: run(*j, a.model, plugin_dir, work), jobs))
        recs = list(ex.map(lambda r: judge(r, a.judge_model, work) if r["kind"] == "judged" else r, recs))
        scrub = isolation.scrubber([(tmp, "<runs>"), (plugin_dir, "<plugin>"), (pathlib.Path.home(), "~")])
        recs = [scrub(r) for r in recs]
    for r in recs:
        r["checks"], r["cli"] = checks(r), version
        (out / f"{r['id']}-{r['rep']}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        summary = r.get("grades") or dict(r["checks"])
        print(f"{r['kind']:10} {r['id']:20} {r['rep']} {summary} loaded={r['loaded']} cost={r['cost']} rc={r['rc']}")
    print("total cost $%.2f" % sum((r["cost"] or 0) + (r.get("judge_cost") or 0) for r in recs))
    if a.no_ledger:
        sys.exit(0)
    score = judged_score(recs)
    rows = ledger.rows_from_records("gate", out.relative_to(ROOT).as_posix(), flatten(recs), lambda c: c["skill"],
                                    commit=ledger.head_commit(REPO), cli=version, judge=lambda m, c: score,
                                    cond_of=lambda c: cond, minutes=round((time.time() - started) / 60, 1))
    fails = evaluate(ledger.load(), rows, a.trigger_tol, a.judge_tol)
    ledger.append_rows(rows)
    for f in fails:
        print("FAIL " + f)
    print("gate: " + ("FAIL" if fails else "PASS"))
    sys.exit(1 if fails else 0)
