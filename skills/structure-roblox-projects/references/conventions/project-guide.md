# Project guide: orient, write, and save

Use when the user asks for a project overview, agent onboarding, or a saved guide, or when existing guidance needs a correction. Ordinary tasks orient only as far as the [work loop](../../SKILL.md#work-loop) needs. Broad onboarding maps ownership and navigation; it is not a code or security audit.

## Reuse existing guidance

Read `CLAUDE.md` and the docs it links first. Prefer extending a coherent existing guide over creating a competing one. Reuse sections that are still supported even if another section is stale. A title, fixed headings, or a marker comment does not prove a guide is complete. A guide describes the project; it grants no edit permission.

The current request and `CLAUDE.md` win over guide content. Resolve a filesystem/DataModel disagreement through the mapping before deciding which description is stale. A local exception, an unexplained dirty edit, or a failed web lookup does not overturn a project-wide convention.

Older projects may have `.agents/roblox/project.md` or a sparse `.agents/roblox/structure.md` profile. Keep using them at their stated scope, including any pinned structural dependencies and freshness notes. Missing fields express no preference, and a sparse profile is not a full overview. Extend or link them; don't delete them or create a second authority without approval.

## Map the project

Read applicable instructions and docs. Establish project roots, product type (game, places, plugin, package/model, tool), targets, the directory agents start from, and what evidence is available. A repository may hold several places, plugins, packages, tools, or unrelated projects. An empty folder or unavailable Studio connection does not prove an experience is empty. Ask for the smallest missing location or representation only when it blocks useful work.

Distinguish live Studio state from saved places, exports, and source snapshots. Trace authored source through compilers, generated output, and mappings to the actual host. Disabled bootstraps, examples, fixtures, caches, and unmapped files may not run. Indexing the whole project is not a prerequisite.

Cover the applicable boundaries deeply enough that a fresh agent can find where to work. Use representative traces and links to authoritative configuration, not exhaustive inventories.

| Boundary | Establish |
| --- | --- |
| Identity and topology | Artifact type, roots, places/targets, shared source, build variants, external surfaces. |
| Authoring | Who owns code, instances, assets, metadata, and configuration; how they reach Studio or another host; sync and conflict ownership. |
| Language and generation | Authored inputs, compiler/build pipeline, generated/vendor output, dependency restoration. |
| Execution and startup | Effective paths, classes/RunContext, enabled state, startup/discovery owners, readiness/failure handling, relevant object/character/plugin/Actor lifetimes. |
| Systems and interfaces | Major domains and entry files, dependency direction, networking/authority, persistence, UI/assets, packages, external integrations. |
| Tools and dependencies | Native version sources and commands; runtime libraries versus dev tools. |
| Conventions | Implemented naming, grouping, API, lifecycle, error, cleanup, and test practices; instruction scope; intentional exceptions. |
| Verification and delivery | Prepare/check/build/sync paths, CI, Studio checks, development/release boundaries, publishing ownership. |

Cross-check contradictory prose against source and mappings before calling it stale. Custom compilers, packages, plugins, and mixed workflows keep their own host/consumer contract; a missing specialist reference doesn't justify replacing them. Stop when each applicable boundary has a navigational answer or a specific evidence gap.

## Write the overview

- Explain scope, source/host ownership, major systems, how to edit and verify, non-obvious conventions, and signals that should trigger reinspection.
- Link entry files, manifests, configuration, tests, and existing docs. Don't copy trees, version lists, or command inventories that are cheap to inspect; native configuration owns them. Include a command only when a handoff needs it, with a link to its definition.
- Record the review date and what was inspected, inferred, run, or unavailable. A saved snapshot supports snapshot claims only.
- Put risks and optional improvements in a separate assessment with evidence and tradeoffs. An old pin or uncommon framework is not itself a defect; onboarding doesn't choose upgrades or redesigns.
- Leave out task logs, secrets, and defaults nobody selected.

The overview is ready when a fresh agent can find owned source, understand how it runs, keep its conventions, and pick the checks. Name missing Studio evidence rather than claiming runtime verification. An unsaved overview can still support other authorized work.

## Save it

Show the content or diff, the destination, and any `CLAUDE.md` pointer before writing, unless the user already approved that exact write or asked you to save it. A changed scope, ownership, or recommendation needs a new preview; routine factual adjustments within an approval don't. Approving documentation does not authorize installs, upgrades, or architecture changes.

1. **Destination.** Use the existing guide. Otherwise propose `docs/roblox-project.md` under the affected project root. Recheck the destination and keep concurrent user edits.
2. **Pointer.** Add a small pointer to the project's `CLAUDE.md`, reusing any existing pointer convention instead of creating another authority. Use a managed block so later updates replace only it:

   ```markdown
   <!-- structure-roblox-projects:onboarding:start -->
   ## Roblox project guidance

   Before Roblox work in this project, read `docs/roblox-project.md`. Check claims against their linked sources. Propose guide corrections before saving them.
   <!-- structure-roblox-projects:onboarding:end -->
   ```

3. **Write.** Replace only an existing managed block or append the pointer, leaving other bytes unchanged. Claude Code loads `CLAUDE.md` from the start directory and its ancestors, and loads a subdirectory's `CLAUDE.md` only when it reads files there. If agents start above a nested project, an ancestor pointer may be needed; that is a separate write to propose. If you can't confirm the host will load the pointer, say which directory or setting it needs.
4. **Check.** Inspect the diff against what was approved and against the implemented project. Confirm links resolve. Report what was saved and the remaining evidence gaps.
