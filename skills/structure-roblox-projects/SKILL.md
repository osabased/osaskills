---
name: structure-roblox-projects
description: "Design, review, or change Roblox project structure when placement, runtime/source-of-truth, startup/lifecycle, mappings, conventions, or migration is material. Do not use for ordinary logic or value edits inside already placed modules."
---

# Structure Roblox Projects

Integrate features into coherent existing structure and give new projects a concrete foundation. Preserve established conventions unless the user requests redesign. Explicit user choices override this skill's defaults.

At activated use, check for the sibling `.skill-maintenance/structure-roblox-projects.json` promotion guard; ordinary dependent use waits while it exists. For task-relevant current platform/tool facts, source drift or a reusable guidance defect, dependency proposals, or consequential practice decisions, read the shared [on-demand maintenance policy](../roblox-resource-acquisition/references/on-demand-maintenance.md). It supplies the user's narrow factual-repair grant and guarded update procedure. Healthy immutable-target use keeps its cheap path; upkeep creates no schedule.

That maintenance branch requires the sibling `roblox-resource-acquisition` package. If it is missing, report shared upkeep unavailable and continue structural work under the current request and this skill's own evidence rules. Skill repairs require applicable task authorization and an established recovery procedure; obtain current authoritative evidence for any version-sensitive claim before relying on it.

## Activation and task selection

Use this skill when a material decision concerns placement, server/client/shared ownership, startup/lifecycle, source of truth, mapping, or durable structural conventions. An ordinary internal logic/value edit with those boundaries unchanged needs no structural route, even if it mentions SSA, Rojo, a package, or client/server security. Fixed-target package adoption with all structural choices already resolved belongs to resource acquisition.

Choose the work from the request:

- **Feature integration / Implementation:** implement requested structural work, including its necessary integration edits.
- **Onboarding:** recommend a foundation or guide setup; a bare invocation starts here and remains read-only until setup is selected.
- **Design or Review:** deliver the requested design or findings; these remain read-only unless implementation is also requested.
- **Migration:** use the full migration workflow only for an explicitly requested migration, transition, conversion, or migration plan. Ordinary moves and renames use its applicable safeguards without becoming a migration.
- **Preference setup:** resolve requested durable choices through the profile and preference references.

A new feature in an existing project is established-project work. Greenfield means creating the project/experience itself.

## Establish enough context

Inspect only the affected area and relevant integration edges. Resolve:

- the requested outcome and any explicit write restrictions;
- the authoring owner: Studio, Script Sync, Rojo, or the established alternative;
- runtime and replication placement;
- startup, dependency, discovery, and lifecycle paths;
- applicable local conventions; and
- focused checks for the structural failures the change could introduce.

For demos, stories, previews, and test bootstraps, also resolve whether they ship and how exclusion and interactive behavior will be proved. Stop discovery when further inspection is unlikely to change placement, integration, scope, or validation. Missing evidence should identify a specific unresolved decision, not trigger an unrelated project survey.

Resolve established-project choices in this order: current request, coherent affected-area convention, applicable project profile, broader coherent project convention, then the current-task recommendation. For greenfield or a requested redesign target, use the requested target, applicable profile and constraints, then defaults. Ask only about material choices that remain unresolved; clear established work needs no preference questions.

Before loading version-sensitive shared feature guidance, resolve the project's adopted exact target and applicable project-local compatibility profile/child. A matching `ModuleLoader.Start(...)` signature does not establish compatibility with a later shared recommendation. Keep this lookup scoped to the affected dependency and convention.

## Load the applicable references

Evaluate triggers against both current and target structure. Load only branches needed for this task.

| Branch | Trigger and reference |
| --- | --- |
| Setup | Bare invocation, guided setup, or a recommended foundation: [onboarding](references/workflows/onboarding.md). |
| Ordinary structure | An unresolved placement, entrypoint, grouping, runtime, or source-of-truth choice; or those criteria are needed for Review/Design: [practices](references/core/practices.md). |
| Canonical SSA feature | Add/move a feature root or change placement, lifecycle, or integration in an area whose entrypoint directly calls the pinned `ModuleLoader.Start(...)` on its `Server/` or `Client/` root, with no conflicting startup convention: [SSA](references/ssa/ssa.md). |
| Canonical SSA infrastructure | Create SSA or change entrypoints, loader identity/acquisition/configuration, discovery, or upgrades: [SSA](references/ssa/ssa.md) and [bootstrap](references/ssa/ssa-bootstrap.md). |
| Write boundary | Explicit restrictions, ambiguous ownership/pre-existing changes, or a broad/generated operation may exceed the requested outcome: [modification scope](references/core/modification-scope.md). A shared file alone is not a permission boundary. |
| Server Authority | Current/target `Workspace.AuthorityMode = Server`, prediction/rollback, shared deterministic simulation, or an explicit review/change of this model: [Server Authority](references/platform/server-authority.md). |
| Script Capabilities | An active or materially suspected sandbox affects the work, or its security model is explicitly reviewed/changed: [Script Capabilities](references/platform/script-capabilities.md). |
| Script Sync | Review/change its workflow, conflicts, or sync boundaries; move/rename managed content where representation, metadata, children, or packages matter: [Script Sync](references/workflows/script-sync.md). |
| Rojo | Review/change mappings or workflow; edit project/meta/model files; move mapped content where path, identity, topology, version, syncback, or live serving matters; author development/release artifacts or previews: [Rojo](references/workflows/rojo.md). |
| Migration or structural safeguards | Explicit migration planning/implementation, or ordinary moves, renames, topology/identity changes, source-of-truth changes, or multi-step restructuring needing tracing/recovery: [migration](references/workflows/migration.md), using only the applicable mode. |
| Project profile | A material convention remains unresolved; following a profile reveals material drift; profile setup/update is requested; implementation establishes a greenfield foundation or changes project-wide conventions through requested redesign/migration; or established-project implementation lacks usable agent onboarding and bootstrap already established durable conventions (or a useful profile exists): [project profile](references/conventions/project-profile.md). |
| Preferences | Requested preference choices or material organization decisions remain open after project/profile evidence: [preference resolution](references/conventions/preference-resolution.md). |

The profile reference owns interpretation of the nearest project-local `.agents/roblox/structure.md` and discloses persistence rules when needed. Profiles record durable conventions, not task inventories or modification authority. Routine feature work does not require a profile rewrite or additional discovery to populate one.

For version-sensitive behavior, verify current authoritative documentation and the project's actual tool versions. Distinguish supported platform behavior from skill defaults and pinned dependency contracts; newer releases alone do not authorize upgrades. Shared recommendations prefer current stable guidance; an established project's exact target remains owned by its project authority.

## Complete the work

### Feature integration and Implementation

The requested outcome authorizes the smallest necessary edits to its modules, callers, shared entrypoints, mappings, configuration, and focused checks, unless the user explicitly limits those writes. Existing/shared content is not automatically protected. Preserve unrelated content and pre-existing changes; ask when ownership is ambiguous, an explicit restriction would be crossed, or the work materially expands the requested outcome. Use the modification-scope reference for those cases.

1. Identify the affected write set and inspect relevant pre-existing changes. Preserve the established startup, placement, and authoring model.
2. Apply a coherent change across its integration edges. For SSA, follow the feature contract and load bootstrap guidance only if infrastructure actually changes. Avoid architecture normalization and unrelated cleanup.
3. For topology-sensitive work, trace affected requires, callers, remotes, mappings, discovery and startup references; establish recovery before mutation; inspect the resulting diff or generated output against the write set; and run focused structural plus runtime validation. Use the migration reference for the applicable safeguards. Version control can supply recovery for fully captured reversible filesystem edits; Studio state and uncaptured files need their own recovery source.
4. Apply profile persistence only when its routed trigger is active and the durable outcome is known.
5. Run the smallest checks covering the changed boundary. Reuse passing evidence until relevant inputs change; broaden for failures, shared-interface risks, or remaining uncertainty.

Completion means the requested behavior is integrated and the focused checks pass. If Studio or another required check is unavailable, distinguish completed source changes from unverified runtime behavior and state the exact remaining check. A successful build or loader-state attribute alone does not prove startup or lifecycle success.

### Onboarding and preferences

Follow onboarding for a concrete provisional setup immediately under stated assumptions: source-of-truth workflow, runtime roots, executable entrypoint form, shared/dependency placement, and one validation path. For an established project, offer a targeted compatible improvement. Questions refine this recommendation; they do not replace it.

Use the defaults owned by preference resolution and the tooling baseline owned by onboarding only for unresolved choices. Explain the selected runtime dependencies and tooling obligations, honoring user constraints before defaults.

When setup implementation is already requested or the user accepts an offered setup action, implement it without another authorization round. Acceptance of a design-only recommendation stays design-only. Complete when the requested choices are implementable and authorized setup is validated, or the exact unresolved condition is stated.

### Review and Design

For Review, use supplied paths, trees, manifests, diffs, and stated project facts as evidence at their given granularity. Each material finding needs concrete evidence, its runtime/security/source-of-truth/maintainability impact, and the smallest compatible improvement. Treat style as a finding only when it violates an explicit convention or has a concrete consequence. Report missing evidence only when it could change the conclusion; include meaningful no-change areas when useful.

For Design, put the complete recommended topology in the answer: DataModel/filesystem homes, runtime/replication/authoring boundaries, startup, dependency direction, Remote contracts, and checks. Follow the entrypoint and Remote contracts in practices; load that reference when designing either. Resolve one concrete executable path/class/owner per entrypoint. Alternatives must state what they replace. Name any explicitly restricted integration changes and the minimum owner action.

Finish when the requested risks are accounted for or every designed item has an unambiguous home and startup/integration contract. A checklist promising to define the structure later is incomplete.

### Migration plan

Follow migration's full workflow and completion criterion. Deliver concrete slices in the answer, with source/target paths, affected references, source-of-truth cutover, owner actions, recovery, and verification. When supplied evidence is only hierarchy categories, give provisional slices at that granularity and label unresolved leaf paths. Keep planning read-only unless implementation is requested.

## Structural invariants

- Keep privileged rules/state, secrets, persistence, purchases, and client-input validation authoritative on the server. Client-visible code and data are inspectable; replicate only what clients need.
- Keep `ReplicatedFirst` limited to the earliest loading subset.
- Keep entrypoints focused on assembly/startup, feature behavior in cohesive ModuleScripts, and dependency direction acyclic.
- Shared module source does not share mutable state between Luau environments.
- Add frameworks, packages, lifecycle machinery, or generated hierarchy only for a justified role; preserve explicit user constraints and coherent existing ownership.

