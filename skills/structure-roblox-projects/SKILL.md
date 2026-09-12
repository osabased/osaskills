---
name: structure-roblox-projects
description: "Roblox project structure: place or organize DataModel/code, review structural boundaries, choose project conventions, or plan/perform migrations across Studio, Script Sync, or Rojo."
---

# Structure Roblox Projects

Preserve a coherent established structure unless the user requests redesign or migration. Inspect enough context to place and integrate the work correctly, while treating modification authority separately from technical context.

## Core loop

1. **Route** the request as Review, Design, Migration plan, Implementation, or Preference setup.
2. **Bootstrap** only the affected area until the material placement, integration, scope, and validation decisions are resolved.
3. **Disclose** only the references whose trigger is present.
4. For Implementation, determine whether the established-project fast path applies.
5. Execute the selected route and run validation that covers the credible failure modes introduced by the work.

Stop expanding discovery when more inspection is unlikely to change placement, integration, modification scope, or validation.

## Bootstrap the affected area

Establish the minimum sufficient working model for the current task:

- **Modification boundary:** what the request clearly authorizes, and which adjacent content is context only.
- **Source of truth:** Studio-owned, Script Sync-managed, Rojo-mapped, or another established workflow relevant to the affected content.
- **Placement and runtime:** where the work belongs and whether server, client, shared, replication visibility, or an active simulation/security boundary matters.
- **Startup and integration:** the relevant entrypoint, dependency, Remote/Bindable, loader, discovery, or lifecycle path.
- **Local convention:** the organization, naming, module style, or framework convention the work should preserve.
- **Validation path:** the focused checks capable of catching the structural failures this task could introduce.

Skip an item when it cannot affect the task. Prefer concrete paths, instances, entrypoints, and dependency edges over architecture labels.

Bootstrap is complete when every material item above is either established or identified as a blocker. A UI task should not trigger a survey of unrelated combat, persistence, NPC, or matchmaking systems.

## Modification scope

A clear request authorizes its stated project, system, feature, path, files, instances, or other concrete work boundary, plus new artifacts clearly owned by that deliverable. Adjacent content may be inspected for compatibility and integration.

Access, technical necessity, project conventions, profiles, dependencies, or failing validation do not independently grant authority to modify adjacent content.

Read [`references/modification-scope.md`](references/modification-scope.md) before mutation when a proposed write may cross an unclear, shared, generated, or protected boundary; a dirty worktree makes ownership ambiguous; or a broad tool can write outside the immediately requested content.

## Established-project Implementation fast path

Use this fast path only for **Implementation**, and only when all of these are true:

- the affected area has a coherent supported structure;
- the requested work fits that structure without redesign or migration;
- the source-of-truth boundary is staying intact;
- no required write crosses an unclear or protected boundary; and
- no triggered reference below is required for correctness.

The fast path is an eligibility shortcut, not a separate mutation procedure. It means the agent may skip unnecessary structural ceremony and extra reference loading, but it must still follow the Implementation route's pre-mutation status check, write-set control, mutation, and validation steps.

A fast-path Implementation needs no preference questions, profile write, architecture normalization, rollback ceremony, or specialist reference unless evidence causes one of those triggers to fire. Review, Design, Migration plan, and Preference setup never become mutating through this fast path.

## Reference routing

Load a reference only when its branch is active. Evaluate specialist triggers against both the current structure and the requested target structure. Multiple specialist references may apply to one task.

| Trigger | Read |
| --- | --- |
| An architecture Review depends on ordinary Roblox layout, placement, runtime, entrypoint, grouping, module-style, or source-of-truth rules; a task reviews, designs, plans, changes, or validates a DataModel placement, entrypoint type/location, or source-of-truth workflow whose Roblox platform semantics can affect correctness; or the project does not already resolve a material layout, placement, entrypoint, grouping, module-style, or source-of-truth choice | [`references/practices.md`](references/practices.md) |
| A write may cross an unclear/shared/protected boundary, broad generated output, or ambiguous pre-existing work | [`references/modification-scope.md`](references/modification-scope.md) |
| The current or target structure uses Server Authority (`Workspace.AuthorityMode = Server`), prediction/rollback APIs, or shared deterministic simulation; or the task explicitly reviews, designs, plans, enables, disables, or migrates to/from Server Authority | [`references/server-authority.md`](references/server-authority.md) |
| An active or materially suspected Script Capabilities sandbox can affect the work; or the task explicitly reviews, designs, plans, enables, disables, or changes the Script Capabilities security model | [`references/script-capabilities.md`](references/script-capabilities.md) |
| Reviewing, designing, planning, enabling, disabling, or changing Script Sync/conflict behavior or a sync boundary; or migrating/renaming content into, out of, or within Script Sync-managed content where sync representation, metadata, or child shape can matter | [`references/script-sync.md`](references/script-sync.md) |
| Reviewing, designing, planning, adopting, removing, or changing a Rojo mapping/workflow; changing a mapping/project/meta/model file; or migrating content into, out of, or within Rojo-mapped content where path, name, topology, version, syncback, or live-serve behavior can affect the resulting DataModel | [`references/rojo.md`](references/rojo.md) |
| Moves, renames, topology/identity changes, source-of-truth migration, or multi-step restructuring are planned | [`references/migration.md`](references/migration.md) |
| The user requests reusable structural preferences, or a material organization choice remains genuinely unresolved | [`references/preference-wizard.md`](references/preference-wizard.md) |

For version-sensitive platform behavior, re-open current authoritative documentation when external access is available instead of treating cached guidance as current by default.

## Resolve conventions

For ordinary work in an established project, resolve each material choice in this order:

1. explicit current request;
2. coherent convention in the affected area;
3. applicable project profile for a choice the implementation still leaves unresolved;
4. broader coherent project convention;
5. current-task recommendation or default.

For greenfield work or explicit redesign/migration, use the requested target first, then an applicable project profile, relevant project constraints, and a current-task recommendation/default.

Check for the nearest project-local `.codex/roblox-structure.md` only when a material convention remains unresolved or the user asks for reusable project preferences. Treat the profile as convention memory, never as modification authority. When it conflicts with a coherent implemented convention during ordinary established-project work, preserve the implementation and treat the discrepancy as profile drift. Update the profile only when that write is explicitly requested and authorized.

## Complete the selected route

### Preference setup

Read `references/preference-wizard.md`. Resolve only choices that are genuinely open and material to the request. A clear established project should produce zero preference questions.

Persist `.codex/roblox-structure.md` only when the user explicitly requests project-level convention memory and authorizes that write. Keep persistent profiles about durable conventions rather than task scope, current dependency graphs, transient layout observations, or temporary risks.

Finish when every material requested preference is directly implementable and any requested profile write is either completed with authorization or blocked with the exact reason.

### Review

Set breadth from the review question, not from modification authority. Inspect adjacent content when it can change the conclusion. Read `references/practices.md` when the conclusion depends on ordinary Roblox layout, placement, runtime, replication, entrypoint, grouping, module-style, or source-of-truth rules, and load any specialist reference whose trigger is present.

For each material finding, report the **evidence**, **impact**, and **smallest compatible improvement**. Add confidence or scope when uncertainty or ownership materially affects interpretation. Treat style preferences as findings only when they conflict with an explicit request or established convention, create a supported-platform incompatibility, or have a concrete correctness, security, or maintainability consequence.

Finish when the material structural risks within the requested boundary are accounted for, including meaningful no-change areas or residual uncertainty when useful. Review remains read-only unless implementation is separately requested.

### Design

Preserve established conventions unless redesign is requested. When the project does not already resolve a material design choice, read `references/practices.md`.

Provide the smallest structure that makes the requested work unambiguous: its DataModel/filesystem home, material runtime/replication/authoring boundaries, startup flow, dependency direction, integration contracts, and validation path. Load specialist references only for affected specialist branches. Identify any required boundary-crossing changes as approval-dependent or owner actions rather than silently folding them into the authorized design.

Design is read-only unless Implementation is separately requested. Finish when every designed item has an unambiguous home and startup/integration path and every material boundary contract is identified.

### Migration plan

Read `references/migration.md` and every specialist reference whose current-state or target-state trigger is present. Keep planning read-only unless implementation is also requested.

Finish only at the migration reference's exhaustive completion criterion: every move, affected reference, material topology/identity assumption, required owner action, specialist boundary, verification step, and necessary recovery boundary is accounted for.

### Implementation

Determine whether the established-project fast path applies, but always follow the pre-mutation and validation steps below. Fast-path eligibility only removes unnecessary structural ceremony; it never bypasses safeguards or triggered references.

1. In a version-controlled filesystem worktree, inspect relevant status or pre-existing changes before mutation. If they overlap the intended work or make ownership ambiguous, read `references/modification-scope.md` before writing.
2. Establish the intended authorized write set at the level the task requires.
3. Apply the smallest coherent change. Update the authorized paths, mappings, callers, requires, tests, or integration points needed for that change to work.
4. For moves, renames, topology changes, or multi-step restructuring, follow `references/migration.md`.
5. Use an explicit recovery boundary when an operation is destructive, topology-sensitive, non-version-controlled, externally stateful, or difficult to reverse. Routine reversible filesystem edits already captured by version control do not need separate rollback bookkeeping.
6. Inspect the resulting diff or changed-output set when the operation is broad/generated, topology-sensitive, overlaps pre-existing work, or otherwise risks writes outside the intended set.
7. Run focused validation that covers the credible failure modes introduced by the change. Escalate validation when the affected boundary, risk, or a failed check warrants broader evidence.

Prefer existing static, type, lint, build, test, mapping, or hierarchy checks when they cover the failure mode. Use the smallest relevant Studio runtime checks when runtime/startup/client-server behavior needs execution evidence. Report checks that actually ran and any material residual risk from unavailable validation.

Finish when the requested structural outcome is complete and focused checks pass, or when blocked integration, required owner actions, unavailable checks, and residual risk are explicit.

## Invariants

- Keep critical rules/state, secrets, persistence, purchases, and client-input validation authoritative on the server. Treat client-visible code and data as inspectable.
- Put only code and data clients genuinely need in client-visible containers.
- Keep `ReplicatedFirst` limited to the earliest loading subset.
- Keep entrypoints focused on dependency assembly and startup; put feature behavior in cohesive ModuleScripts and keep dependency direction acyclic.
- Preserve established names and casing. For a new project with no stronger convention, use PascalCase for folders, scripts, and module tables; camelCase for functions and locals; and UPPER_SNAKE_CASE for constants.
- Prefer explicit dependencies. Add `Init` and `Start` phases only when ordering or cross-system readiness requires them.
- Retain multiple entrypoints when object lifetime, `Actor` parallelism, character/tool behavior, or isolation makes them the simpler fit.
- Introduce a framework, package manager, test framework, or generated hierarchy only when a requirement beyond organization justifies it and the resulting writes are authorized.