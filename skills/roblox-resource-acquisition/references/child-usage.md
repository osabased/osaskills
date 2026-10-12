# Shared child usage (contract 1)

> **Version check:** before answering, once per session, also run `python "PARENT/scripts/check_updates.py"` (cached for a day). If the child's library has a newer release, say so; the project's pin still decides what you use. Then follow [keeping current](keeping-current.md).

Read this once per task when a child skill (for example `roblox-janitor`) is active. The child's `resource.yaml` holds the canonical identity, exact pin and install-check profile.

## Check the pin

Find the paths:

- **Parent:** this skill's folder. Look for the sibling `../roblox-resource-acquisition/` next to the child, then `.claude/skills/roblox-resource-acquisition/` in the project, then `~/.claude/skills/roblox-resource-acquisition/`.
- **Child:** the active child's own folder.
- **Project:** the Roblox project root (where `wally.toml`, `pesde.toml`, `package.json` or `default.project.json` lives).

Run the install check. `uv` supplies Python 3.11+ and PyYAML without setup; otherwise use any Python 3.11+ with PyYAML:

```sh
uv run --no-project --python ">=3.11" --with pyyaml python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
```

`--declared` compares the manifest and lock with the child's pin. Without it, the check also hashes the installed package source. It reads `wally.toml`/`wally.lock` (with `Packages/_Index`), `pesde.toml`/`pesde.lock`, or `package.json`/`package-lock.json`, according to the child's profile. For a nonstandard layout pass `--manifest`, `--lock`, `--alias`, `--package-dir`, `--companion PACKAGE=DIR` or `--asset`. It never runs dependency code.

| Result | Meaning | Do |
| --- | --- | --- |
| `PASS` (exit 0) | The pin (and, without `--declared`, the installed bytes) match the child. | Use the child normally. |
| `UNAVAILABLE` (exit 2) | The check couldn't run: no project, unsupported or missing manifest, library not declared, or packages not installed. | Continue as advice. Read the manifest and lock yourself if you can, and say which check was skipped. |
| `FAIL` (exit 1) | The pin or installed bytes differ from the child's target, or the manifest or lock is malformed. | Report the mismatch and keep the project's pin. Don't carry version-specific guidance across versions: continue only with API you can confirm at the project's version, and stop (or ask) where the task depends on behavior that may differ. Use the parent's add/adopt/upgrade flow if the pin should change. |

If the parent, Python or `uv` is missing (a standalone upload, or a sandbox without Python), read the manifest and lock yourself, compare the pinned version with the child's target, and say which check you couldn't run.

The child's `reconciliation.policy` says when to check:

- **conditional:** run the `--declared` check before version-sensitive use, and the full check (without `--declared`) before you finish, when the project can be checked.
- **required:** run the full check before version-sensitive use, because installed state can drift without a lock change (for example a Studio plugin file).
- **not-applicable:** the descriptor gives a concrete reason installed state can't drift; no check is needed.

Also check the project's `CLAUDE.md` resource list for a known issue or blocked use noted against this resource.

A newer upstream release is information, not a reason to change the pin.

## When guidance is wrong

A repeated workaround, or a guess you had to make, is a defect. Report the reproduction, the workaround and the proposed fix before you finish (see the parent's "When a child's guidance is wrong"). A hard defect (correctness, security, identity, version) stops the affected work. A harmless one-off adjustment needs no report. Edit the child only when the current task authorizes it; otherwise propose the exact change.

## Finish with the right claim

Say what was checked: the declared pin, the installed bytes, and any build or runtime checks you actually ran. Advice-only guidance implies no runtime proof.
