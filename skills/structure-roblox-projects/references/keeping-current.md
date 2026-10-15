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

The skill tracks the latest stable release of each tool it describes. [`versions.json`](../versions.json) lists each one's source, the version the guidance was last reviewed against (`reviewed`), and the files that depend on it. This is about the skill's content; a user's project keeps its own pins unless the user asks to upgrade.

### Check

Run once per session, before relying on version-specific guidance (cached for a day):

```sh
python "SKILL_DIR/scripts/check_updates.py"
```

It needs Python 3.9+ and network access. Exit 0 means everything is current, 1 means something is outdated, 2 means nothing could be checked. If it can't run, carry on and don't mention it unless the task depends on a version. In a plugin install, a session-start hook runs the same check and adds an "osaskills freshness check" note when something is outdated; treat that note like this script's output.

When an item is outdated and the task depends on it, say so before using version-specific guidance and check the claim against the project's actual pin. Otherwise finish the task first, then mention it in one line. Update the skill afterward if you can; don't hold up the user's task for it.

### Update

You can update the skill when `gh repo view osabased/osaskills --json viewerPermission` reports `WRITE`, `MAINTAIN` or `ADMIN`. Otherwise report the outdated items and suggest updating the installed plugin or skill later. One tool per pull request:

1. **Skip duplicates:** `gh pr list --repo osabased/osaskills --state open --search "update <id>"`. If a PR covers the tool, stop.
2. **Work outside the user's checkout.** Inside an osaskills clone, `git fetch` and `git worktree add <temp-dir> -b update/<id>-<version> origin/main`; otherwise `gh repo clone osabased/osaskills <temp-dir>` and branch there.
3. **Read what changed:** the release notes for every version between `reviewed` and the latest. Note new or removed commands and flags, changed defaults, new config fields, deprecations, and fixes to anything the guidance warns about.
4. **Update the files** listed for the tool (`files` relative to this skill, `repo_files` relative to the repository root): version-specific claims, commands, flags, "verified on" notes and doc links. If nothing the guidance says changed, only the manifest changes.
5. **Verify with the real tool.** Rojo: put the new release first on `PATH` and run `python -m pytest -q tests` from the skill folder; the real-Rojo tests must run, not skip. Other tools: run the commands the guidance documents in a scratch project. Say what you couldn't run.
6. **ModuleLoader** is the fixed SSA contract: follow [migration and upgrade](ssa.md#migration-and-upgrade) in full before changing its pin, covering API, discovery defaults, lifecycle order, failure behavior, the asset's SHA-256 and the license. A new major version needs a fresh review of every rule in [SSA](ssa.md).
7. **Record it:** set `reviewed` and `reviewed_on` in `versions.json`.
8. **Open the PR** titled `Update <name> to <version>`, with the old and new versions and release links, what changed upstream that matters, what you changed, what you verified and what you couldn't. If a check fails or a behavior change can't be resolved with confidence, open a draft listing the open questions.

Remove the temporary worktree or clone when done. Installed plugin copies pick up the merge on their next update; no version bump is needed.
