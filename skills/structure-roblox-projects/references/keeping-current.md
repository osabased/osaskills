# Keeping current

This skill's references give structure and compatibility context, not a guarantee of currentness. Running a project's already-pinned tools needs none of this.

## Claims about current tools and platform

Use when adopting, adding or upgrading a tool or library, relying on version-sensitive behavior not yet confirmed for the project's pin, or recommending a practice as current.

| Claim | Evidence |
| --- | --- |
| How this project behaves | Its source, effective mappings, manifests, lockfiles and runtime evidence. A saved snapshot proves only the snapshot. |
| How a tool or the platform behaves | Canonical docs, source and releases for the project's actual version. The latest docs can't prove an older pin's behavior. |
| What practice is recommended | Maintained primary guidance or inspectable implementations matched to the use case. Popularity isn't evidence; don't claim consensus without independent support. |

**Introducing a tool or library:** resolve its canonical identity and target version, read its releases and the docs for the intended use, separate stable releases from previews, and tell the user about relevant incompatibilities or lookups you couldn't make. Check only what the task uses. A newer release doesn't authorize an upgrade, and a failed lookup doesn't erase valid evidence for an unchanged pin.

**Recommending:** resolve the use, environment and priorities; compare plausible candidates on fit, compatibility, maintenance, license and replacement cost; recommend one with its deciding tradeoff and what would change it; cite source, version and date. Leave a genuinely open consequential choice to the user. When the `roblox-resource-acquisition` skill is installed ([SKILL.md](../../roblox-resource-acquisition/SKILL.md)), use it to choose and acquire libraries.

**Drift:** recheck guide claims when mappings, ownership, startup, dependencies or commands change. A local exception or failed lookup doesn't justify rewriting project-wide conventions; propose corrections through the [project guide](project-guide.md#save-it).

Starting sources: Roblox ([data model](https://create.roblox.com/docs/projects/data-model), [script locations](https://create.roblox.com/docs/scripting/locations), [Studio testing](https://create.roblox.com/docs/studio/testing-modes), [client-server boundary](https://create.roblox.com/docs/scripting/security/client-server-boundary)); Rojo ([docs](https://rojo.space/docs/), [changelog](https://github.com/rojo-rbx/rojo/blob/master/CHANGELOG.md)); roblox-ts ([docs](https://roblox-ts.com/docs/)).

## Keeping this skill current

[`versions.json`](../versions.json) lists each tool the skill describes: its source, the version the guidance was last reviewed against (`reviewed`), and the files that depend on it. The guidance is updated on demand, not on a schedule. This is about the skill's content; a user's project keeps its own pins unless the user asks to upgrade.

### Check

Only when a task depends on a tool's version-specific guidance, compare the project's pin with `reviewed`:

- **Same version:** trust the guidance.
- **Project pin newer:** check the release notes between the two versions for the claims the task uses, follow the newer behavior, and tell the user in one line.
- **Project pin older:** confirm the claims the task uses at the pinned version, and warn the user.
- **No pin:** use the installed version (`<tool> --version`) as the baseline. If the tool isn't installed, check the claims the task uses against the current docs.

Studio-dependent behavior has no version to compare. When a task depends on it, check it against the Roblox docs or the running Studio. Never change the project's pins to fit the skill.

In a plugin install, a session-start hook compares the project's `rokit.toml` and `aftman.toml` pins with `reviewed`, without network access, and adds an "osaskills tool pins" note only when they differ. Act on it only for a tool the task depends on.

`scripts/check_updates.py` lists tools whose latest stable release is newer than `reviewed` (Python 3.9+ and network access; exit 0 means all current, 1 something newer, 2 nothing checked). Run it when you need that, such as before an update. A weekly workflow runs it for the maintainer's tracking issue.

### Update

Update only on demand: when the user asks ("update rojo"), or when you offer it in one line after a task whose check found a gap and the user agrees. Target the project's pin or a version the user names, and never lower `reviewed`.

Only a full review sets `reviewed` to a version X: the release notes up to X checked against every file listed for the tool. A fix to a single claim goes in its own PR titled `Fix <name>: <claim>` and leaves `reviewed` and `reviewed_on` unchanged.

You can update the skill when `gh repo view osabased/osaskills --json viewerPermission` reports `WRITE`, `MAINTAIN` or `ADMIN`. Otherwise report the gap and suggest updating the installed plugin or skill later. One tool or one fix per pull request:

1. **Skip duplicates:** `gh pr list --repo osabased/osaskills --state open --search "<name> in:title"` lists open `Update <name>` and `Fix <name>` PRs. Stop if one already does this work: an update to the same or a later version, or a fix to the same claim. An update and a fix don't block each other; name the other PR in yours.
2. **Work outside the user's checkout.** Inside an osaskills clone, `git fetch` and `git worktree add <temp-dir> -b update/<id>-<version> origin/main` (a fix: `fix/<id>-<slug>`); otherwise `gh repo clone osabased/osaskills <temp-dir>` and branch there.
3. **Read what changed:** the release notes for every version between `reviewed` and the target, or for a fix, those that bear on the claim. Note new or removed commands and flags, changed defaults, new config fields, deprecations, and fixes to anything the guidance warns about.
4. **Update the files** listed for the tool (`files` relative to this skill, `repo_files` relative to the repository root): version-specific claims, commands, flags, "verified on" notes and doc links. A fix changes only its claim. If nothing the guidance says changed, only the manifest changes.
5. **Verify with the real tool.** Rojo: put the new release first on `PATH` and run `REQUIRE_ROJO=1 python -m pytest -q tests` from the skill folder, so a real-Rojo test fails instead of skipping when that binary can't run. Other tools: run the commands the guidance documents in a scratch project. Say what you couldn't run.
6. **ModuleLoader** is the fixed SSA contract: follow [migration and upgrade](ssa.md#migration-and-upgrade) in full before changing its pin, covering API, discovery defaults, lifecycle order, failure behavior, the asset's SHA-256 and the license. A new major version needs a fresh review of every rule in [SSA](ssa.md).
7. **Record it:** add an entry dated today under this skill in `CHANGELOG.md` at the repository root. After a full review, also set `reviewed` and `reviewed_on` in `versions.json`; a fix leaves both unchanged.
8. **Open the PR** titled `Update <name> to <version>` or `Fix <name>: <claim>`, with the old and new versions (for a fix, the version the claim was checked at) and release links, what changed upstream that matters, what you changed, what you verified and what you couldn't. If a check fails or a behavior change can't be resolved with confidence, open a draft listing the open questions.

Remove the temporary worktree or clone when done. Installed plugin copies pick up the merge on their next update; no version bump is needed.
