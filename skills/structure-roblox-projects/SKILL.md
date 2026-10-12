---
name: structure-roblox-projects
description: "Roblox/Luau project structure and integration: where scripts and modules belong (ServerScriptService, ReplicatedStorage, StarterPlayerScripts, ServerStorage, ReplicatedFirst), Script vs LocalScript vs RunContext, client/server boundaries and RemoteEvents, startup/bootstrap wiring, and moving or renaming modules safely. Use when Roblox work touches Rojo (default.project.json, *.project.json, sourcemap.json, rojo build/serve/syncback), Studio Script Sync, roblox-ts output, Rokit/Wally/pesde/StyLua/selene/luau-lsp setup, a new Roblox project, onboarding to an unfamiliar Roblox repo or writing its agent guide, or migrating between Studio, Script Sync and Rojo. Also covers Server Authority prediction/rollback and Script Capabilities sandbox boundaries. Not needed for small edits inside an already-understood file."
---

# Structure Roblox Projects

Work from where the project's code actually lives and how it actually starts. Keep a coherent existing structure, toolchain, and pins, and finish the requested task. The defaults here are for choices the project has not already made.

**First, once per session:** run `python scripts/check_updates.py` from this skill's folder (cached for a day, no packages needed). If it prints `OUTDATED`, tell the user which tool has a newer release, and after the task follow [keeping current](references/core/keeping-current.md). Skip silently if it can't run.

## Placement quick reference

- Server-only code: `Script`s in `ServerScriptService`; server-only modules and assets in `ServerScriptService` or `ServerStorage`. Clients never receive them.
- Client entrypoint: a `Script` with `RunContext = Client` in `ReplicatedStorage` (Roblox's current recommendation), or a `LocalScript` in `StarterPlayerScripts`, `StarterCharacterScripts`, `StarterGui`, or `StarterPack`. A `LocalScript` in `ReplicatedStorage` never runs. A Client-RunContext `Script` in a Starter container runs twice (original and clone).
- Rojo 7 file suffixes: `*.client.luau` builds a `LocalScript` unless the project sets `"emitLegacyScripts": false`, which makes it a `Script` with `RunContext = Client` (`*.server.luau` likewise becomes `RunContext = Server`). So a default-settings `init.client.luau` mapped into `ReplicatedStorage` never runs. Script Sync's suffixes (`.local.luau`, `.legacy.luau`) mean nothing to Rojo, which builds them as ModuleScripts.
- Shared modules, types, constants, and Remotes: `ReplicatedStorage`. Everything there is visible to clients, so keep secrets out.
- Earliest loading UI only: `ReplicatedFirst`.
- A ModuleScript runs once per Luau environment (server, each client, each `Actor`). Its returned state is not shared between them.
- Validate all client input on the server. Keep DataStores, purchases, and authoritative game state server-side, and replicate only what clients need.

## Work loop

1. **Locate the owned source.** Read the project's instructions (`CLAUDE.md`) and existing guidance, such as `.claude/roblox/project.md` or `.agents/roblox/project.md`. Identify the affected project or place, authored versus generated files, which workflow syncs them (Studio, Script Sync, Rojo, a compiler), and the startup path that reaches the code. Follow mappings and `require`s; don't infer execution from folder names. An empty folder does not mean the Studio place is empty.
2. **Trace only the boundary the change crosses.** Check client/server placement and replication, startup and lifecycle, dependencies, and the checks that cover them. Recheck stale or contradictory guidance against source. Stop when those questions have answers or specific gaps. A routine edit needs no project overview, new guide, or architecture review.
3. **Do the work.** Include the caller, entrypoint, mapping, configuration, and focused-test edits the change needs to actually run. Trace moves and renames before applying them, and keep a way to undo risky ones.
4. **Verify and stop.** Inspect the diff and any generated output, then run the smallest checks that cover the change. Broaden only for failures or unresolved integration risk. Name checks you could not run. A build, an offline run, or a loader's "loaded" flag does not prove Studio startup, rendering, input, or multiplayer behavior.

Give each execution environment one clear startup owner and keep the earliest-loading content small.

If the user restricts which files you may edit, or ownership of existing or generated files is unclear, use [modification scope](references/core/modification-scope.md). A shared file is not automatically restricted. Do the authorized part and name the exact edit that stays blocked.

## Match the deliverable

- **Ordinary task:** the work loop above.
- **Project overview or agent guide:** [project guide](references/conventions/project-guide.md). Keep facts separate from suggested improvements.
- **New project or new foundation:** [needs-led setup](references/workflows/onboarding.md). Propose one setup for review before building it, unless the user already approved it or asked you to just build it.
- **Review or design:** stay read-only unless asked to implement. Back findings with concrete project impact. A design names source/generated ownership, exact entrypoint paths, classes or RunContexts and owners, communication boundaries, and the checks for the proposed behavior.
- **Migration:** [migration](references/workflows/migration.md) for an explicit migration or plan. Ordinary moves use only its tracing and recovery safeguards.

## Boundary references

| When the task needs it | Read |
| --- | --- |
| Placement, entrypoints, grouping, source of truth (Studio vs Script Sync vs Rojo), or Remote design | [Practices](references/core/practices.md) |
| A consequential project choice is still open | [Preference resolution](references/conventions/preference-resolution.md) |
| Rojo mapping, build/serve, topology, or dev/release composition changes | [Rojo](references/workflows/rojo.md) |
| Script Sync ownership, conflicts, managed topology, or metadata changes | [Script Sync](references/workflows/script-sync.md) |
| Configuring formatters, linters, type checking, tests, packages, or tool versions | [Default tooling](references/workflows/default-tooling.md) |
| The project uses or explicitly selects the ModuleLoader SSA contract | [SSA](references/ssa/ssa.md); [bootstrap](references/ssa/ssa-bootstrap.md) for loader or entrypoint changes |
| Server Authority prediction/rollback or shared deterministic simulation | [Server Authority](references/platform/server-authority.md) |
| An active or likely Script Capabilities sandbox | [Script Capabilities](references/platform/script-capabilities.md) |

Plugins, packages/models, compilers, and custom or mixed workflows keep their real host and consumer contracts. Use their own documentation where these references don't cover them.

## Current facts

Running a project's already-pinned tools needs no freshness research. Check current docs and releases only when you adopt, add, or upgrade a tool or library, rely on version-sensitive behavior you have not confirmed for the project's pinned version, or make a recommendation. Then follow [evidence and freshness](references/core/evidence-and-freshness.md). Platform pages change: re-open the linked official page before relying on version-sensitive behavior, and say which lookups you could not make.

## Companion skill

The `roblox-resource-acquisition` skill is optional. If it is installed beside this one ([SKILL.md](../roblox-resource-acquisition/SKILL.md)), use it to choose, acquire, adopt, or repair libraries and tools. If it is missing, use canonical sources directly; nothing here requires it.
