"""Isolation for headless `claude -p` eval runs, shared by evals written after 2026-10-21.

The dated eval folders keep their own copies of this code so they still rerun as recorded; don't port them.
Import it from an eval folder with:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_lib"))
    import isolation
"""
import json, os, pathlib, re, subprocess, sys

HOME = pathlib.Path.home()
PROJECTS = HOME / ".claude" / "projects"
LIB = pathlib.Path(__file__).resolve().parent
FLAGS = ["--setting-sources", "project,local", "--strict-mcp-config", "--output-format", "stream-json", "--verbose"]

def clean_env():
    """os.environ without a parent Claude session's variables, so the child run uses its own login."""
    drop = ("CLAUDE", "ANTHROPIC", "USE_LOCAL_OAUTH", "USE_STAGING_OAUTH")
    return {k: v for k, v in os.environ.items() if not k.upper().startswith(drop)}

def main_checkout(path=LIB):
    """The main working tree of the repo holding path, also when path is inside a worktree."""
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=path,
                            capture_output=True, text=True, check=True).stdout.strip()
    return pathlib.Path(common).parent

def project_slug(path):
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))

def home_rule(path):
    return f"~/{pathlib.Path(path).resolve().relative_to(HOME).as_posix()}/**"

def isolate(proj, hide=(), block_fetch=None):
    """Write proj/.claude/settings.json so a run there sees only what the eval gives it.

    `--setting-sources` alone still loads ~/.claude/CLAUDE.md, and a run can read the whole home directory,
    where past session transcripts and installed skills hold answers. This excludes the user's CLAUDE.md,
    denies reads of it, this repo's session transcripts, installed plugins and skills, and every path in hide
    (paths under the home directory), and with block_fetch, a regex, blocks WebFetch of matching URLs.
    Deny rules cover Read, Glob and Grep, and the hook also fires inside subagents.
    """
    deny = [f"~/.claude/projects/{project_slug(main_checkout())}*/**", "~/.claude/plugins/**", "~/.claude/skills/**",
            "~/.claude/CLAUDE.md"]
    deny += [home_rule(p) for p in hide]
    settings = {"claudeMdExcludes": ["**/.claude/CLAUDE.md"], "permissions": {"deny": [f"Read({d})" for d in deny]}}
    if block_fetch:
        hook = f'"{pathlib.Path(sys.executable).as_posix()}" "{(LIB / "block_fetch.py").as_posix()}" "{block_fetch}"'
        settings["hooks"] = {"PreToolUse": [{"matcher": "WebFetch", "hooks": [{"type": "command", "command": hook}]}]}
    (proj / ".claude").mkdir(parents=True, exist_ok=True)
    (proj / ".claude" / "settings.json").write_text(json.dumps(settings, indent=1), encoding="utf-8")
    return settings

def events(stdout):
    """The JSON events in a stream-json run's stdout, skipping any line that isn't JSON."""
    out = []
    for line in stdout.splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out

def model_ids(evs):
    """Every model id a run used, resolved from aliases like `sonnet`, so results stay comparable across releases."""
    ids = set()
    for ev in evs:
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            ids.add(ev.get("model"))
        if ev.get("type") == "assistant":
            ids.add((ev.get("message") or {}).get("model"))
        if ev.get("type") == "result":
            ids.update(ev.get("modelUsage") or {})
    return sorted(i for i in ids if i and not i.startswith("<"))

def cli_version():
    return subprocess.run(["claude", "--version"], capture_output=True, text=True, env=clean_env()).stdout.strip()

def path_pattern(path):
    parts = pathlib.PureWindowsPath(path).parts
    rest = r"[\\/]+".join(re.escape(p) for p in parts[1:])
    return re.compile(rf"(?:{parts[0][0]}:|/{parts[0][0]})[\\/]+{rest}", re.IGNORECASE)

def scrubber(pairs):
    """A function that replaces each (path, label) path, in either slash style, inside nested results."""
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
