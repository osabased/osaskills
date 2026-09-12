---
name: structure-roblox-projects
description: Design, place, review, or migrate Roblox code and DataModel structure; resolve project conventions.
---

# Structure Roblox Projects

Preserve coherent established structure unless redesign or migration is requested. Inspect enough to place and integrate the work correctly; technical context and modification authority are separate.

## Bootstrap the affected area

Establish only what can affect this task: the authorized modification boundary, source of truth (Studio, Script Sync, Rojo, or another established workflow), placement and server/client/shared runtime, replication or security boundaries, startup/integration path, local conventions, and useful validation.

Prefer concrete paths, instances, entrypoints, and dependency edges over labels. Stop expanding once the material placement, integration, scope, and validation decisions are resolved or explicitly blocked. A local UI task does not need a survey of unrelated systems.

## Modification scope

A clear request authorizes its stated project, system, feature, path, files, instances, or other concrete boundary, plus new artifacts clearly owned by that deliverable. Adjacent content can be inspected for compatibility and integration. Access, technical necessity, dependencies, conventions, profiles, and failed validation do not independently authorize adjacent writes.

Before a write that may cross an unclear/shared/generated/protected boundary, overlap ambiguously owned pre-existing work, or use a broad tool with wider outputs, read [modification-scope.md](references/modification-scope.md).

## Reference routing

Read only active branches. Evaluate triggers against **both current and requested target structure**, including review/design/planning as well as implementation. Adopting, disabling, replacing, or migrating a specialist feature activates its reference; several can apply together.

| Branch | Trigger | Reference |
| --- | --- | --- |
| Ordinary structure | A review depends on ordinary layout/runtime/replication/entrypoint/grouping/module-style/source-of-truth rules; DataModel placement, entrypoint, or authoring-workflow semantics can affect correctness; or a material ordinary structural choice remains unresolved | [practices.md](references/practices.md) |
| Write boundary | Unclear/shared/protected scope, broad generated output, or ambiguous pre-existing work | [modification-scope.md](references/modification-scope.md) |
| Server Authority | `Workspace.AuthorityMode = Server`, prediction/rollback APIs, shared deterministic simulation, or a change to/from Server Authority | [server-authority.md](references/server-authority.md) |
| Script Capabilities | An active or materially suspected sandbox affects the work, or its security model is being evaluated or changed | [script-capabilities.md](references/script-capabilities.md) |
| Script Sync | Sync workflow, boundary, or conflicts; managed moves/renames where representation, metadata, child shape, or packages matter | [script-sync.md](references/script-sync.md) |
| Rojo | Mapping/workflow changes, project/meta/model files, or mapped moves/renames/topology where paths, names, versions, syncback, or live serve affect the DataModel | [rojo.md](references/rojo.md) |
| Migration | Planned moves, renames, topology/identity changes, authoring/source-of-truth migration, or multi-step restructuring | [migration.md](references/migration.md) |
| Project profile | A material convention remains unresolved and a local profile may resolve it, or reusable project preferences/profile creation or update are requested | [project-profile.md](references/project-profile.md) |
| Preferences | Explicit convention selection, or a material choice remains open after applicable request/project/profile evidence | [preference-resolution.md](references/preference-resolution.md) |

For version-sensitive platform behavior, consult current authoritative documentation when external access is available rather than assuming cached guidance is current.

## Resolve conventions

For ordinary established-project work, use: **explicit request → coherent affected-area convention → applicable profile if still unresolved → broader coherent project convention → current-task recommendation/default**.

For greenfield work or explicit redesign/migration, use: **requested target → applicable profile → relevant project constraints → current-task recommendation/default**.

Check only the nearest project-local `.codex/roblox-structure.md`, and only for an unresolved material convention or requested reusable preferences. Read [project-profile.md](references/project-profile.md) before interpreting or writing it. It is convention memory, never modification authority.

## Complete the selected route

### Preference setup

For reusable convention memory, follow [project-profile.md](references/project-profile.md), resolving persisted fields from the request, coherent conventions, and applicable profile evidence. Use [preference-resolution.md](references/preference-resolution.md) only for genuinely open fields or an explicit preference-selection task. An established project with settled choices needs zero preference questions.

Finish when material requested choices are implementable and any requested profile write satisfies its confirmation/persistence contract, or the exact blocker is reported. An unidentified project root blocks persistence, not task-local convention resolution.

### Review

Set breadth from the review question, not write authority. Inspect relevant adjacent content and apply triggered references. Report each material finding's **evidence, impact, and smallest compatible improvement**; add confidence/scope when material.

Style is a finding only when it conflicts with the request or established convention, creates supported-platform incompatibility, or has concrete correctness, security, or maintainability consequences. Finish when structural risks within the requested boundary and meaningful uncertainty are accounted for. Review remains read-only unless implementation is also requested.

### Design

Provide the smallest structure that makes the requested work unambiguous: DataModel/filesystem home, material runtime/replication/authoring boundaries, startup, dependency direction, integration contracts, and validation path. Preserve established conventions unless redesign is requested. Identify boundary-crossing changes as approval-dependent or owner actions.

Finish when each designed item has a clear home and startup/integration path and all material boundary contracts are identified. Design remains read-only unless implementation is also requested.

### Migration plan

Follow [migration.md](references/migration.md) and all current/target specialist branches. Planning remains read-only unless implementation is requested.

Finish at the migration reference's completion criterion: every move, affected reference, topology/identity assumption, owner action, specialist boundary, verification step, and necessary recovery boundary is accounted for.

### Implementation

For work that fits a coherent established structure without redesign, migration, source-of-truth change, or unclear/protected write boundaries, implement directly after resolving the material bootstrap items and triggered references. This fast path needs no extra preference setup, profile write, architecture normalization, or unrelated survey.

Establish the authorized write set and inspect relevant pre-existing changes before filesystem mutation. Apply the smallest coherent change, including authorized mappings, callers, requires, tests, and integration points. Follow [migration.md](references/migration.md) for moves, renames, topology changes, or multi-step restructuring.

Use an explicit recovery boundary for destructive, topology-sensitive, non-version-controlled, externally stateful, or hard-to-reverse work. Routine reversible edits already captured by version control need no separate rollback bookkeeping. Inspect the resulting diff/output set when broad generation, topology changes, overlapping work, or other scope risk warrants it.

Validate credible failure modes introduced by the work. Prefer existing static/type/lint/build/test/mapping/hierarchy checks when sufficient; use focused Studio runtime checks when startup or client-server behavior needs execution evidence. Broaden validation when risk or a failed check calls for it, not as a fixed second pass. Respect the write boundary when a check exposes adjacent work.

Finish when the requested structural outcome is complete and focused checks pass, or report exact blocked integration, owner actions, unavailable checks, and residual risk. Continue the authorized implementation and its corrections without an extra review checkpoint; existing approval requirements still apply.

## Invariants

- Keep critical rules/state, secrets, persistence, purchases, and client-input validation authoritative on the server; client-visible code/data are inspectable.
- Put only what clients genuinely need in client-visible containers, and only the earliest loading subset in `ReplicatedFirst`.
- Keep entrypoints focused on dependency assembly/startup, feature behavior in cohesive ModuleScripts, and dependency direction acyclic.
- Preserve coherent conventions unless redesign/migration is requested; keep convention memory separate from write authority.
- Introduce frameworks, package managers, test frameworks, or generated hierarchies only for requirements beyond organization and within authorized writes.
