---
name: structure-roblox-projects
description: "Structure Roblox/Luau projects and make them agent-ready. Use for Roblox work on: where scripts go and whether they run (ServerScriptService, ReplicatedStorage, StarterPlayerScripts, ReplicatedFirst; Script, LocalScript, RunContext); Remotes and client/server authority; Rojo config (*.project.json, globIgnorePaths, sourcemap.json, rojo build/serve/syncback), Studio Script Sync, a Studio-only place or roblox-ts output; first-time Rokit, Wally, pesde, StyLua, Selene, luau-lsp or Lest setup; a check script, guards (a check failing on a renamed DataStore, banned API or misplaced script), Claude Code hooks or CI; Studio play-tests, or editing or testing through the Studio MCP; a new project, onboarding or agent guide; moving or migrating scripts; Server Authority or Script Capabilities. Use it even when the answer seems familiar: it records current Rojo and engine behavior models get wrong. Not for edits inside one already-understood file, or picking or upgrading a specific package (roblox-resource-acquisition)."
---

# Structure Roblox Projects

Two jobs: put code where Roblox actually runs it, and give a Roblox project what an agent needs to work in it without a human watching. Keep a project's coherent structure, toolchain and pins. The defaults here are for choices the project hasn't made, and stack choices (libraries, frameworks) belong to the project, not to this skill. Tools named here are examples of a role; a project's stack can be anything, and an [unfamiliar one](references/unfamiliar-stack.md) gets its contract worked out, not assumed.

**First, once per session:** run `python scripts/check_updates.py` from this skill's folder (cached for a day, no packages needed). If it prints `OUTDATED`, tell the user which tool has a newer release, and after the task follow [keeping this skill current](references/keeping-current.md#keeping-this-skill-current). Skip silently if it can't run.

## Facts models get wrong

- A `LocalScript` runs only under a player (`PlayerScripts`, `PlayerGui`, `Backpack`, the character; usually placed through the Starter containers) or in `ReplicatedFirst`. In `ReplicatedStorage` it never runs. A `Script` with `RunContext = Client` runs from `ReplicatedStorage`, which is Roblox's current recommendation for client entrypoints; in a Starter container it runs twice (original and clone).
- Rojo 7: `*.client.luau` builds a `LocalScript` unless the project sets `"emitLegacyScripts": false`, which makes it a `Script` with `RunContext = Client` (`*.server.luau` likewise gets `RunContext = Server`). So a default-settings `init.client.luau` mapped into `ReplicatedStorage` never runs. Script Sync's `.local.luau` and `.legacy.luau` suffixes mean nothing to Rojo, which builds them as ModuleScripts.
- A ModuleScript runs once per Luau environment (the server, each client, each `Actor`). Its state is never shared between them.
- Everything in `ReplicatedStorage` and `ReplicatedFirst` reaches clients. Secrets, DataStores, purchases, validation and authoritative state stay in `ServerScriptService` or `ServerStorage`. Validate every client-to-server payload on the server.
- Don't call `require()` in a desynchronized parallel phase; require first, in serial context.
- A build, an offline test run or a loader's "loaded" flag proves nothing about Studio startup, rendering, input or multiplayer.

## Work loop

1. **Locate.** Read `CLAUDE.md` and the project guide it points to. Find the files that own the change, which workflow syncs them (Rojo, Script Sync, Studio, a compiler), and the startup path that reaches them. Follow mappings and `require`s; don't infer execution from folder names. An empty folder doesn't mean the Studio place is empty.
2. **Trace the boundary the change crosses:** client/server placement, startup, Remotes, saved data, and the checks that cover them. Stop when each has an answer or a named gap. A routine edit needs no overview or new guide, unless it relies on a stack the guide doesn't record ([unfamiliar stacks](references/unfamiliar-stack.md#record-and-apply-it)).
3. **Do the whole change,** including the caller, entrypoint, mapping and test edits it needs to run. If the user restricts which files you may edit, do the allowed part and name the exact edit that stays blocked ([write scope](references/migration.md#write-scope)).
4. **Verify** with the project's check command (if no guide names it, look in `scripts/`, the README and CI config), then the lowest rung of the [verification ladder](references/verification.md) that can observe the change. Name the rungs you couldn't run, and never report an unrun check as passed. If the task relied on a stack these references don't describe, even one a library skill partly covers, end the report as [unfamiliar stacks](references/unfamiliar-stack.md#record-and-apply-it) says: the proposed guide diff and the `Reuse:` line.

## An agent-ready project

An agent works safely in a Roblox project that has the pieces below. When you set up a project or write its guide, first compare the authors `git shortlog -sne HEAD` lists with `git config user.email`. Then ask once, in a message of its own with no proposal, whether the setup is shared with the team or [personal](references/project-guide.md#shared-or-personal), recommending personal when anyone else has committed and the repository has no shared agent setup; a personal one keeps every piece out of Git and CI. Then propose the missing pieces for that answer, sized to the project, and build them after the user reviews the proposal. When asked whether a project is agent-ready, check each row. A place whose code lives only in Studio can't have most of them; start from [Studio-only](references/studio-only.md).

| Piece | Done when | Details |
| --- | --- | --- |
| Guide | `CLAUDE.md` fits on a screen and points to task guides; claims cite their source | [project guide](references/project-guide.md) |
| One check command | Restore, guards, codegen, tests, format, lint and types (plus builds and topology under Rojo) run from one command that prints one line per step | [checks](references/checks.md#one-check-command) |
| Guards | A rule whose break is permanent, a security hole or silent fails the check; library-coupled guards are pinned to the version they were reviewed against | [guards](references/checks.md#guards) |
| Hooks and CI | Format on edit, the check before the agent stops and before push, the same command in CI, tools installable in a fresh checkout | [hooks and CI](references/checks.md#hooks-and-ci) |
| Verification ladder | The guide says how to reach each rung this project supports, up to a Studio play-test | [verification](references/verification.md) |
| Dev/release boundary | Dev-only content can't ship or run in live servers, and live sync is locked to the right place | [Rojo](references/rojo.md#dev-and-release-builds), [Script Sync](references/script-sync.md#dev-content-and-publishing) |
| Fresh-agent trial | A new agent built a small feature from the repo alone, and the guide was fixed where it stalled | [trial](references/project-guide.md#trial-it-with-a-fresh-agent) |

Be strict only where a mistake is permanent or a security hole. Libraries, the engine and community practice change, so everything else lives in the guide, where it can change without fighting a check.

## Route by task

| Task | Read |
| --- | --- |
| Ordinary edit | The work loop only |
| Placement, entrypoints, Remotes, grouping, or choosing Studio vs Script Sync vs Rojo | [Placement](references/placement.md) |
| Project overview, agent guide or `CLAUDE.md` pointer | [Project guide](references/project-guide.md) |
| Agent readiness, checks, guards, hooks or CI | [Checks](references/checks.md) |
| Tests, Studio engine tests, play-tests, Studio MCP | [Verification](references/verification.md) |
| New project or new foundation | [New project](references/new-project.md) |
| Rojo mapping, build/serve, topology, dev/release builds | [Rojo](references/rojo.md) |
| Script Sync edits, boundaries, conflicts, checks or publishing | [Script Sync](references/script-sync.md) |
| Code that lives only in Studio, worked through the Studio MCP | [Studio-only](references/studio-only.md) |
| Formatter, linter, type checker, test runner, packages or tool versions | [Tooling](references/tooling.md) |
| Move, rename, restructure or migrate | [Migration](references/migration.md) |
| The project uses ModuleLoader SSA | [SSA](references/ssa.md) |
| A sync tool, compiler (roblox-ts), loader, framework or test runner these references don't describe | [Unfamiliar stacks](references/unfamiliar-stack.md) |
| Server Authority or Script Capabilities | [Engine modes](references/engine-modes.md) |
| Adopting or upgrading a tool or library, or a claim about what is current | [Keeping current](references/keeping-current.md) |

Reviews and designs stay read-only unless the user asks for the change; back each finding with its concrete effect on the project. Plugins, packages and compiler pipelines keep their own host and consumer contracts; work them out from their documentation where these references don't cover them ([unfamiliar stacks](references/unfamiliar-stack.md)). Running a project's already-pinned tools needs no freshness research.

## Companion skill

The `roblox-resource-acquisition` skill is optional. If it is installed beside this one ([SKILL.md](../roblox-resource-acquisition/SKILL.md)), use it to choose, adopt, upgrade or repair libraries and tools. If it is missing, use canonical sources directly; nothing here requires it.
