# Shared child usage (contract 1)

Read this once per task when a child skill (for example `roblox-janitor`) is active. The child's `resource.yaml` holds the canonical identity, exact pin, check profile and the project record path.

## Find the parent and the project

- **Parent:** the `roblox-resource-acquisition` skill directory. Look first for the sibling `../roblox-resource-acquisition/` next to the child, then `.claude/skills/roblox-resource-acquisition/` in the project, then `~/.claude/skills/roblox-resource-acquisition/`. In a plugin install, the parent is the sibling folder.
- **Child:** the active child's own directory.
- **Project:** the root of the affected Roblox project (where `wally.toml`, `pesde.toml`, `package.json` or `default.project.json` lives).
- **Record:** `PROJECT/` plus the descriptor's `reconciliation.record`, normally `.roblox-resources/records/<slug>.yaml`. An explicitly supplied record path wins. Older projects may still have `.agents/roblox/resources/`; move it to `.roblox-resources/`.

## Run the checks

Use `uv` when it is available, because it supplies Python 3.11+ and PyYAML without a setup step:

```sh
uv run --no-project --python ">=3.11" --with pyyaml python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
uv run --no-project --python ">=3.11" --with pyyaml python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "RECORD"
```

Otherwise use any `python` 3.11+ with PyYAML installed. Replace `PARENT`, `CHILD`, `PROJECT` and `RECORD` with real paths.

`check_resource_install.py` reads `pesde.toml`/`pesde.lock`, `wally.toml`/`wally.lock` (with `Packages/_Index`), or `package.json`/`package-lock.json`, according to the child's profile. For a nonstandard layout pass `--manifest`, `--lock`, `--alias`, `--package-dir`, `--companion PACKAGE=DIR` or `--asset`. It never runs dependency code or commands taken from records.

## Act on the result

| Result | Meaning | Do |
| --- | --- | --- |
| `PASS`, `HEALTHY` | Pin matches; no recorded block. | Use the child normally. |
| `NO-RECORD` | The project has no record for this resource. | Use the child as advice; say record checks were skipped. |
| `UNAVAILABLE`, `UNKNOWN` (exit 2) | The check could not run or the record is inconclusive: no project, unsupported or missing manifest, library not declared, packages not installed, unreadable record, unknown reconciliation, a renamed `generated_skill`, or a host-local problem with this copy. | Continue in **advisory mode**: read the manifest/lock directly if you can, and say which check was skipped and why. |
| `FAIL` (install check, exit 1) | Observed mismatch (the pin or installed bytes differ from the child's target), a malformed manifest or lock, an ambiguous alias, or an update in progress. | **Stop** version-sensitive work. Report the mismatch; enter the parent's `repair/reconcile` mode. |
| `MISMATCH`, `BLOCKED`, `FAILED` (status check, exit 1) | The record names another identity/version, records a block, or records failed verification. | **Stop** the affected use and report the reason. |

Advisory mode also applies when the parent skill, Python or `uv` is missing (for example a standalone upload or a sandbox without Python): read the manifest and lock yourself, compare the pinned version with the child's target, and report which checks you could not run.

A guard file (`.skill-maintenance/<skill-name>.json` beside the child's or parent's folder) means an update is in progress. The checkers report it as blocked; finish or recover the update first.

## Reconciliation policies

- **conditional:** run the two checks above before version-sensitive use; run the full installed-integrity check (the first command without `--declared`) before you finish, when the project can be checked.
- **required:** run the full installed-integrity check before version-sensitive use, because installed state can drift without a lock change (for example a Studio plugin file). If a record exists, also load it and the project's learnings.
- **not-applicable:** the descriptor names a concrete reason why installed state cannot drift; only guards apply.

Optionally glance at the resource's releases page when the task depends on version-specific behavior; see [first use](on-demand-maintenance.md#first-use-freshness-check). A newer release is information, not a reason to change the pin.

## When guidance is wrong

A repeated workaround, or a guess you had to make, is a defect: report the reproduction, the workaround and the proposed fix before you finish (the parent's "When guidance is wrong" section). A hard defect (correctness, security, identity, version) stops the affected work. A harmless one-off adjustment needs no report. Edit the child only when the current task authorizes it; otherwise propose the exact change. Use [guarded maintenance](on-demand-maintenance.md#guarded-correction-and-recovery) for updates to an installed child.

## Finish with the right claim

Say what was checked: the pin and lock (declaration), the installed bytes (installed-integrity, exit 0 with `lane: installed-integrity`), and any project build or runtime checks you actually ran. Advice-only guidance implies no runtime proof. Trust, project role, runtime verification and child validation are separate claims.
