# Project guide

Use when writing or correcting a project's agent guidance, onboarding an agent to a project, or giving a project overview. Ordinary tasks orient only as far as the [work loop](../SKILL.md#work-loop) needs. Onboarding maps ownership and navigation; it is not a code or security audit.

## Where it lives

`AGENT_DIR` is `.claude/` if it exists, else `.agents/` if it exists, else a new `.claude/`. If both exist, use the one that already contains `roblox/`, and `.claude/` when neither or both do.

| File | Holds | Size |
| --- | --- | --- |
| `CLAUDE.md` (repo root) | Stack in one line, the check command, hard rules each naming the guard that enforces it, where library guidance lives, the pointer below | One screen. It loads every session, so every line costs every task |
| `AGENT_DIR/roblox/project.md` | Source of truth, filesystem-to-DataModel table, startup owners, runtime rules, and a "By task" index to the other guides | What every task needs |
| `AGENT_DIR/roblox/feature.md` | How to add a feature: the layer table (where server, client, shared, UI and network pieces go) and one worked example that passes the check | When the project has a repeated feature shape |
| `AGENT_DIR/roblox/checks.md` | Each verification rung this project supports and how to reach it ([verification](verification.md)) | When there's more than the check command |

Claude Code loads `CLAUDE.md` from the start directory and its ancestors, and a subdirectory's `CLAUDE.md` only when it reads files there. Other agents read `AGENTS.md`; if the project uses one, keep it a pointer to the same guides rather than a second copy.

## Shared or personal

Before the first write to a project's agent setup, ask once whether it is shared with the team (committed and run in CI) or personal to this user. Where the onboarding pointer lives records the answer: `CLAUDE.md` for shared, `CLAUDE.local.md` for personal. Before asking, compare the authors `git shortlog -sne HEAD` lists with `git config user.email`. When anyone else has committed, recommend personal, because a shared setup changes files and CI those people own, unless the repository already has a shared agent setup. Ask this as its own question before drafting the proposal, then propose only the layout for the answer given. Even after a go-ahead, list the paths you will write in one line before the first write.

A personal setup keeps every piece out of Git:

- The pointer goes in `CLAUDE.local.md`; the team's `CLAUDE.md` and any `AGENTS.md` stay as they are.
- The guide, the check script and guards live under `AGENT_DIR/roblox/`, and hooks and the allowlist in `.claude/settings.local.json` ([checks](checks.md)).
- Each file or directory the setup adds, such as `/CLAUDE.local.md` and `/.claude/roblox/`, goes in the exclude file that `git rev-parse --git-path info/exclude` names, which belongs to this clone and is never committed. Never exclude all of `/.claude/`, so files the team adds there later still show up. `.gitignore` is the team's.
- A file the team already tracks stays theirs: read and run it, but don't edit it for the setup.

A personal setup doesn't reach a fresh clone, another worktree or a cloud session, and its guards don't protect teammates. The setup's report names all three places and the teammate gap, and a later task that depends on either says so.

## What to write

- **Facts with sources.** Each claim names the file, doc or test it comes from, and the version or date it was checked. An agent can then recheck a claim instead of trusting or discarding the whole guide.
- **Decisions with reasons.** "Player data goes through X, because...; reconsider if..." lets a later agent tell a deliberate choice from an accident, and know when it's allowed to change.
- **Patterns, not inventories.** Link manifests, config and entry files. Don't copy trees, version lists or command lists that native config owns; they go stale silently.
- **Hard rules only where a check backs them.** A rule whose break is permanent or a security hole belongs in `CLAUDE.md` with its guard ([guards](checks.md#guards)). Everything else is guidance that can change with the project.
- **What it can't verify.** Name the Studio-only behavior and what proves it.

Leave out task logs, secrets and defaults nobody chose. Put risks and optional improvements in a separate assessment; an old pin or uncommon framework is not a defect.

## Reuse what exists

Read `CLAUDE.md`, the existing guide and the docs it links first. Extend a coherent guide rather than writing a competing one, and keep sections that still hold even when others are stale. The current request and `CLAUDE.md` win over guide content. A guide describes the project; it grants no edit permission. Resolve a filesystem/DataModel disagreement through the mapping before deciding which description is stale. Older projects may have an `AGENT_DIR/roblox/structure.md` profile: keep using it at its stated scope, link it from the guide, and don't delete it without approval.

## Map the project

Establish the roots, product type (game, places, plugin, package, tool), the directory agents start from, and what evidence is available. Live Studio state, saved places and source snapshots differ; trace authored source through compilers and mappings to the host. Cover each boundary deeply enough that a fresh agent can find where to work, and stop when each has an answer or a named gap:

| Boundary | Establish |
| --- | --- |
| Topology | Places, targets, shared source, build variants |
| Authoring | Who owns code, instances and assets; how they reach Studio |
| Generation | Compilers, generated and vendored output, dependency restore |
| Startup | Entrypoint paths and classes, startup owners, loaders, lifetimes |
| Systems | Major features, networking and authority, persistence, UI |
| Tools | Version pins and commands |
| Conventions | Naming, grouping, lifecycle, cleanup and test practice |
| Verification | The check command, CI, Studio rungs, dev/release boundary, who publishes |

## Save it

Show the content or diff and the destination before writing, unless the user already approved that exact write. Approving documentation doesn't authorize installs or architecture changes. Recheck the destination and keep concurrent user edits.

Add a pointer to `CLAUDE.md`, or `CLAUDE.local.md` for a [personal setup](#shared-or-personal), naming the guide's real path, in a managed block so later updates replace only the block:

```markdown
<!-- structure-roblox-projects:onboarding:start -->
## Roblox project guidance

Before Roblox work in this project, read `.claude/roblox/project.md`. Check claims against their linked sources. Propose guide corrections before saving them.
<!-- structure-roblox-projects:onboarding:end -->
```

Replace an existing managed block or append one, leaving other bytes unchanged. If agents start above a nested project, an ancestor pointer may be needed; propose it. Afterward, inspect the diff against what was approved and confirm the links resolve.

## Trial it with a fresh agent

A guide is done when an agent without your context can use it. Give a smaller model (Sonnet or Haiku) only the repository and a small feature that crosses the client/server boundary, for example "players earn 10 coins every 5 minutes played, shown in the HUD". Grade the outcome, not the route: it placed code where it runs, kept authority on the server, followed the project's patterns, passed the check, and was honest about what it didn't verify. Don't grade its library or style choices where the guide leaves them open. Where it stalled or guessed, fix the guide or add a guard, then delete the trial's code so the project stays clean.
