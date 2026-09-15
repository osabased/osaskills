---
name: structure-roblox-projects
description: "Roblox project structure: place or organize DataModel/code, review structural boundaries, choose project conventions, or plan/perform migrations across Studio, Script Sync, or Rojo."
---

# Structure Roblox Projects

Preserve a coherent established structure unless the user requests redesign or migration. Inspect enough context to place and integrate the work correctly, while treating modification authority separately from technical context.

## Core loop

1. **Route** the request through the applicable Review, Design, Migration plan, Implementation, or Preference setup route(s).
2. **Establish project context:**
   - **Greenfield** means the user is creating or designing the project/experience from scratch. Resolve structure from the request, applicable project preferences/constraints, then recommendations/defaults; do not search for established conventions that do not exist.
   - **Established** means work occurs inside an existing project, including brand-new features and ordinary restructuring. Preserve applicable established conventions unless the user requests redesign.
   - Project context changes how a selected route resolves structure; it does not select or replace the route.
3. **Bootstrap** only the affected area until the material placement, integration, scope, and validation decisions are resolved.
4. **Load** only the references whose trigger is present.
5. Execute the selected route and run validation that covers the credible failure modes introduced by the work.

Migration is intent-gated: activate the Migration route only when the user explicitly requests the migration/transition/conversion itself or asks for migration planning. Do not infer Migration merely because ordinary Review, Design, or Implementation involves moves, renames, topology/identity changes, source-of-truth-sensitive edits, or multi-step restructuring.

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

Read [`references/core/modification-scope.md`](references/core/modification-scope.md) before mutation when a proposed write may cross an unclear, shared, generated, or protected boundary; a dirty worktree makes ownership ambiguous; or a broad tool can write outside the immediately requested content.

## Reference routing

Load a reference only when its branch is active. Evaluate specialist triggers against both the current structure and the requested target structure. Multiple specialist references may apply to one task.

An internal edit inside an already placed feature remains on the established-project fast path when it requires no placement, lifecycle, or structural-integration decision. Canonical SSA paths alone do not trigger an SSA reference.

| Branch | Trigger | Read |
| --- | --- | --- |
| **Canonical SSA feature integration** | A canonical SSA area—an applicable `Server/` or `Client/` root whose entrypoint directly calls the pinned `ModuleLoader.Start(...)` on that root, with no conflicting startup convention—needs a feature root added/moved, a Server/Client/Shared/Remotes placement chosen, or a feature lifecycle or structural integration changed | [`references/ssa/ssa.md`](references/ssa/ssa.md) |
| **Canonical SSA infrastructure** | Create canonical SSA; explicitly migrate to it; or change its entrypoints, loader identity/acquisition/configuration, discovery, or upgrade behavior | [`references/ssa/ssa.md`](references/ssa/ssa.md) and [`references/ssa/ssa-bootstrap.md`](references/ssa/ssa-bootstrap.md) |
| **Ordinary structure** | An ordinary Roblox structure choice or Review criterion remains unresolved outside the active canonical SSA contract | [`references/core/practices.md`](references/core/practices.md) |
| **Write boundary** | A write may cross an unclear/shared/protected boundary, broad generated output, or ambiguous pre-existing work | [`references/core/modification-scope.md`](references/core/modification-scope.md) |
| **Server Authority** | The current or target structure uses `Workspace.AuthorityMode = Server`, prediction/rollback APIs, or shared deterministic simulation; or the task explicitly reviews, designs, plans, enables, disables, or migrates to/from Server Authority | [`references/platform/server-authority.md`](references/platform/server-authority.md) |
| **Script Capabilities** | An active or materially suspected Script Capabilities sandbox can affect the work; or the task explicitly reviews, designs, plans, enables, disables, or changes the Script Capabilities security model | [`references/platform/script-capabilities.md`](references/platform/script-capabilities.md) |
| **Script Sync** | The task reviews, designs, plans, enables, disables, or changes Script Sync/conflict behavior or a sync boundary; or migrates/renames content into, out of, or within Script Sync-managed content where sync representation, metadata, child shape, packages, or conflict behavior can matter | [`references/workflows/script-sync.md`](references/workflows/script-sync.md) |
| **Rojo** | The task reviews, designs, plans, adopts, removes, or changes a Rojo mapping/workflow; changes a mapping/project/meta/model file; or migrates content into, out of, or within Rojo-mapped content where path, name, topology, version, syncback, or live-serve behavior can affect the resulting DataModel | [`references/workflows/rojo.md`](references/workflows/rojo.md) |
| **Migration workflow** | The user explicitly requests the migration/transition/conversion itself or asks for migration planning | [`references/workflows/migration.md`](references/workflows/migration.md) |
| **Structural-change safeguards** | Ordinary Review, Design, or Implementation includes moves, renames, topology/identity changes, source-of-truth-sensitive edits, or multi-step restructuring where reference tracing, recovery, specialist-boundary, or structural validation guidance is needed | Applicable safeguards in [`references/workflows/migration.md`](references/workflows/migration.md); this does not activate the Migration route |
| **Project profile** | A material convention remains unresolved and an existing `.codex/roblox-structure.md` may resolve it; the user requests profile creation/update; Implementation establishes a greenfield project's durable structure; an established-project Implementation lacks usable agent onboarding and either a useful profile already exists or the current bootstrap establishes at least one high-confidence durable structural convention; or an explicitly requested project-wide redesign/migration is being implemented and changes durable structural conventions | [`references/conventions/project-profile.md`](references/conventions/project-profile.md) |
| **Preferences** | The user explicitly asks to choose structural preferences, or a material organization choice remains unresolved after applicable request/project/profile evidence | [`references/conventions/preference-resolution.md`](references/conventions/preference-resolution.md) |

For version-sensitive platform behavior, re-open current authoritative documentation when external access is available instead of treating cached guidance as current by default.

## Resolve conventions

For ordinary work in an established project, resolve each material choice in this order:

1. explicit current request;
2. coherent convention in the affected area;
3. applicable project profile when the implementation still leaves the choice unresolved;
4. broader coherent project convention;
5. current-task recommendation or default.

For greenfield work or an explicitly requested redesign/migration target, use the requested target first, then an applicable project profile, relevant project constraints, and a current-task recommendation/default.

Check for the nearest project-local `.codex/roblox-structure.md` when a material convention remains unresolved, a Project profile persistence trigger above is active, or the user asks for reusable project preferences. Read `references/conventions/project-profile.md` before interpreting, creating, or updating that file. Treat the profile as convention memory, never as modification authority.

## Complete the selected route

### Preference setup

If the user requests reusable project-level convention memory, read `references/conventions/project-profile.md` first. Persist only durable conventions intentionally selected by the user or explicitly included in the requested project-level preference setup. Preserve unrelated existing profile sections, and treat missing sections as no project-profile preference. Read `references/conventions/preference-resolution.md` only for requested or otherwise intentionally included decisions that remain genuinely open.

Otherwise, read `references/conventions/preference-resolution.md` and resolve only choices that are genuinely open and material to the request. A clear established project should produce zero preference questions.

Finish when every material requested preference is directly implementable and any requested profile write is either completed with authorization or blocked with the exact reason.

### Review

Set breadth from the review question, not from modification authority. Inspect adjacent content when it can change the conclusion. Load the references selected by **Reference routing** when the conclusion depends on their structural rules.

For each material finding, report the **evidence**, **impact**, and **smallest compatible improvement**. Add confidence or scope when uncertainty or ownership materially affects interpretation. Treat style preferences as findings only when they conflict with an explicit request or established convention, create a supported-platform incompatibility, or have a concrete correctness, security, or maintainability consequence.

Finish when the material structural risks within the requested boundary are accounted for, including meaningful no-change areas or residual uncertainty when useful. Review remains read-only unless implementation is separately requested.

### Design

Preserve established conventions unless redesign is requested. When the project does not already resolve a material design choice, load the branch selected by **Reference routing**.

Provide the smallest structure that makes the requested work unambiguous: its DataModel/filesystem home, material runtime/replication/authoring boundaries, startup flow, dependency direction, integration contracts, and validation path. Load specialist references only for affected specialist branches. Identify any required boundary-crossing changes as approval-dependent or owner actions rather than silently folding them into the authorized design.

Design is read-only unless Implementation is separately requested. Finish when every designed item has an unambiguous home and startup/integration path and every material boundary contract is identified.

### Migration plan

Use this route only when the user explicitly requests the migration/transition/conversion itself or asks for migration planning. A request to review whether a migration should happen remains Review unless migration planning is also requested.

Read `references/workflows/migration.md` and every specialist reference whose current-state or requested target-state trigger is present. Keep planning read-only unless implementation is also requested.

Finish only at the migration reference's exhaustive completion criterion: every move, affected reference, material topology/identity assumption, required owner action, specialist boundary, verification step, and necessary recovery boundary is accounted for.

### Implementation

Use the established-project fast path when all of these are true:

- the affected area has a coherent supported structure;
- the requested work fits that structure without requested redesign or migration;
- the source-of-truth boundary is staying intact;
- no required write crosses an unclear or protected boundary; and
- no triggered reference above is required for correctness.

The fast path removes unnecessary structural ceremony and reference loading; it does not bypass write-set control, safeguards, or validation. A fast-path implementation needs no preference questions, profile write, architecture normalization, rollback ceremony, or specialist reference unless evidence triggers one.

Then:

1. In a version-controlled filesystem worktree, inspect relevant status or pre-existing changes before mutation. If they overlap the intended work or make ownership ambiguous, read `references/core/modification-scope.md` before writing.
2. Establish the intended authorized write set at the level the task requires.
3. Apply the smallest coherent change. Update the authorized paths, mappings, callers, requires, tests, or integration points needed for that change to work.
4. For ordinary moves, renames, topology/identity changes, source-of-truth-sensitive edits, or multi-step restructuring, apply only the relevant structural-change safeguards from `references/workflows/migration.md`. Reading or applying those safeguards does not activate the Migration route or its exhaustive completion criterion.
5. Follow the applicable persistence mode in `references/conventions/project-profile.md` when this Implementation establishes a greenfield project's durable structure, initializes missing established-project agent onboarding from durable conventions already established by the current bootstrap, or implements an explicitly requested project-wide redesign/migration that changes durable structural conventions. Established-project onboarding initialization must not expand discovery or persist task-local observations merely to populate the profile. Do not otherwise persist ordinary task-local feature work or restructuring merely because this skill was used.
6. Use an explicit recovery boundary when an operation is destructive, topology-sensitive, non-version-controlled, externally stateful, or difficult to reverse. Routine reversible filesystem edits already captured by version control do not need separate rollback bookkeeping.
7. Inspect the resulting diff or changed-output set when the operation is broad/generated, topology-sensitive, overlaps pre-existing work, or otherwise risks writes outside the intended set.
8. Run focused validation that covers the credible failure modes introduced by the change, including the persisted profile/onboarding when step 5 applies. Escalate validation when the affected boundary, risk, or a failed check warrants broader evidence.

Prefer existing static, type, lint, build, test, mapping, or hierarchy checks when they cover the failure mode. Use the smallest relevant Studio runtime checks when runtime/startup/client-server behavior needs execution evidence. Report checks that actually ran and any material residual risk from unavailable validation.

Finish when the requested structural outcome is complete and focused checks pass, or when blocked integration, required owner actions, unavailable checks, and residual risk are explicit.

## Invariants

- Keep critical rules/state, secrets, persistence, purchases, and client-input validation authoritative on the server. Treat client-visible code and data as inspectable.
- Put only code and data clients genuinely need in client-visible containers.
- Keep `ReplicatedFirst` limited to the earliest loading subset.
- Keep entrypoints focused on dependency assembly and startup; put feature behavior in cohesive ModuleScripts and keep dependency direction acyclic.
- Preserve coherent established conventions unless the request requires redesign or migration.
- Keep modification authority separate from technical context and project conventions.
- Introduce a framework, package manager, test framework, or generated hierarchy only when a requirement beyond organization justifies it and the resulting writes are authorized.
