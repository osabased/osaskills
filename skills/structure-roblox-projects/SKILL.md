---
name: structure-roblox-projects
description: "Design, review, or change Roblox project structure when placement, runtime/source-of-truth, startup/lifecycle, mappings, conventions, or migration is material. Do not use for ordinary logic or value edits inside already placed modules."
---

# Structure Roblox Projects

Preserve a coherent established structure unless the user requests redesign or migration. Inspect enough context to place and integrate the work correctly, while treating modification authority separately from technical context. Explicit user instructions take precedence over this skill's defaults and recommendations unless higher-priority instructions prevent it.

## Activation gate

Activate this skill only when the request materially depends on at least one structural decision: DataModel or filesystem placement, server/client/shared ownership, executable startup or lifecycle, source-of-truth or mapping behavior, a durable project convention, structural review, or an explicit migration/transition. An ordinary logic, bug, text, tuning, or value edit inside already placed modules selects no route here when it preserves those boundaries. A named package, canonical path, or existing Wally/Rojo mapping does not by itself create a structural task.

Apply this gate before routing. If no structural decision remains, stop without selecting this skill; do not turn incidental project context into a Review or Implementation route.

A fixed-target resource adoption does not activate this skill when the package location, mapping, startup, and source-of-truth topology are already established and the request says to preserve them. Likewise, a resource qualification or repair that mentions client/server security does not activate this skill unless the user also requests a project-structure review/change or a material placement, startup, lifecycle, mapping, or source-of-truth decision remains unresolved.

## Core loop

1. **Apply the activation gate**, then route an active request through the applicable Onboarding, Review, Design, Migration plan, Implementation, or Preference setup route(s).
2. **Establish project context:**
   - **Greenfield** means the user is creating or designing the project/experience from scratch. Resolve structure from the request, applicable project preferences/constraints, then recommendations/defaults; do not search for established conventions that do not exist.
   - **Established** means work occurs inside an existing project, including brand-new features and ordinary restructuring. Preserve applicable established conventions unless the user requests redesign.
   - Project context changes how a selected route resolves structure; it does not select or replace the route.
3. **Bootstrap** only the affected area until the material placement, integration, scope, and validation decisions are resolved.
4. **Load** only the references whose trigger is present.
5. Execute the selected route and run validation that covers the credible failure modes introduced by the work.

Migration is intent-gated: activate the Migration route only when the user explicitly requests the migration/transition/conversion itself or asks for migration planning. Do not infer Migration merely because ordinary Review, Design, or Implementation involves moves, renames, topology/identity changes, source-of-truth-sensitive edits, or multi-step restructuring.

An explicit invocation with no concrete work activates Onboarding. Inspect only the minimal available project context, then guide the user toward a concrete recommended setup or relevant established-project improvements. Do not turn a bare invocation into a repository-wide review or implementation authorization.

Stop expanding discovery when more inspection is unlikely to change placement, integration, modification scope, or validation.

## Bootstrap the affected area

Establish the minimum sufficient working model for the current task:

- **Modification boundary:** what the request clearly authorizes, and which adjacent content is context only.
- **Source of truth:** Studio-owned, Script Sync-managed, Rojo-mapped, or another established workflow relevant to the affected content.
- **Placement and runtime:** where the work belongs and whether server, client, shared, replication visibility, or an active simulation/security boundary matters.
- **Startup and integration:** the relevant entrypoint, dependency, Remote/Bindable, loader, discovery, or lifecycle path.
- **Local convention:** the organization, naming, module style, or framework convention the work should preserve.
- **Validation path:** the focused checks capable of catching the structural failures this task could introduce.
- **Development artifact intent:** when the task authors or restructures demos, stories, previews, test bootstraps, or similar development tooling, whether each artifact ships or is excluded and how that boundary will be proved. For Rojo projects, load the Rojo reference for the detailed profile, artifact, and observable-client proof contract.

Skip an item when it cannot affect the task. Prefer concrete paths, instances, entrypoints, and dependency edges over architecture labels.

Bootstrap is complete when every material item above is either established or identified as a blocker. A UI task should not trigger a survey of unrelated combat, persistence, NPC, or matchmaking systems.

## Conditional development-tooling setup

When the authorized task creates or changes demos, stories, previews, test bootstraps, artifact composition, or an interactive proof workflow, load the applicable workflow reference. For Rojo, [`references/workflows/rojo.md`](references/workflows/rojo.md) owns the detailed ship/exclude, profile-composition, artifact-assertion, and observable-client proof contract. If an external preview/test library must be evaluated or adopted, route only that resource-evidence question through Roblox resource acquisition; project topology and artifact composition remain here.

## Modification scope

A clear request authorizes its stated project, system, feature, path, files, instances, or other concrete work boundary, plus new artifacts clearly owned by that deliverable. Adjacent content may be inspected for compatibility and integration.

Access, technical necessity, project conventions, profiles, dependencies, or failing validation do not independently grant authority to modify adjacent content.

Read [`references/core/modification-scope.md`](references/core/modification-scope.md) before mutation when a proposed write may cross an unclear, shared, generated, or protected boundary; a dirty worktree makes ownership ambiguous; or a broad tool can write outside the immediately requested content.

## Reference routing

Load a reference only when its branch is active. Evaluate specialist triggers against both the current structure and the requested target structure. Multiple specialist references may apply to one task.

An internal edit inside an already placed feature that requires no placement, lifecycle, mapping, source-of-truth, or structural-integration decision is outside this skill under the activation gate. Canonical SSA paths alone do not trigger this skill or an SSA reference.

| Branch | Trigger | Read |
| --- | --- | --- |
| **Onboarding/setup** | The skill is explicitly invoked without concrete work; or the user requests guided project setup, setup customization, or a recommendation for a Roblox project foundation | [`references/workflows/onboarding.md`](references/workflows/onboarding.md) |
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
| **Project profile** | A material convention remains unresolved and an existing `.agents/roblox/structure.md` may resolve it; the user requests profile creation/update; Implementation establishes a greenfield project's durable structure; an established-project Implementation lacks usable agent onboarding and either a useful profile already exists or the current bootstrap establishes at least one high-confidence durable structural convention; or an explicitly requested project-wide redesign/migration is being implemented and changes durable structural conventions | [`references/conventions/project-profile.md`](references/conventions/project-profile.md); that file discloses persistence/onboarding guidance only when a persistence branch is active |
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

Check for the nearest project-local `.agents/roblox/structure.md` when a material convention remains unresolved, a Project profile persistence trigger above is active, or the user asks for reusable project preferences. Read `references/conventions/project-profile.md` before interpreting, creating, or updating that file; when persistence handling is in scope, continue into the persistence reference it discloses. Treat the profile as convention memory, never as modification authority.

## Complete the selected route

### Onboarding

Read `references/workflows/onboarding.md`. Inspect minimal context, resolve unknown use cases before recommending libraries, and give a concrete provisional setup immediately under explicit assumptions. Ask only questions that could materially change it; questions refine the recommendation rather than replace it. A bare invocation remains read-only until the user selects a setup. When the user already requested setup implementation, or selects the proposed setup, continue through the applicable Design and Implementation routes without asking for the same authorization again.

The first answer must contain the provisional recommendation itself: source-of-truth workflow, runtime roots, executable entrypoint form, shared/dependency placement, and one validation path or targeted established-project improvement. Saying that a recommendation will be provided is incomplete.

Finish when the user has a directly implementable recommendation and requested setup work is either completed and validated or blocked with the exact unresolved choice or integration condition.

### Preference setup

If the user requests reusable project-level convention memory, read `references/conventions/project-profile.md` first and follow its disclosed persistence reference for persistence handling. Persist only durable conventions intentionally selected by the user or explicitly included in the requested project-level preference setup. Preserve unrelated existing profile sections, and treat missing sections as no project-profile preference. Read `references/conventions/preference-resolution.md` only for requested or otherwise intentionally included decisions that remain genuinely open.

Otherwise, read `references/conventions/preference-resolution.md` and resolve only choices that are genuinely open and material to the request. A clear established project should produce zero preference questions.

Finish when every material requested preference is directly implementable and any requested profile write is either completed with authorization or blocked with the exact reason.

### Review

Set breadth from the review question, not from modification authority. Inspect adjacent content when it can change the conclusion. Load the references selected by **Reference routing** when the conclusion depends on their structural rules.

Treat supplied paths, instance trees, manifests, mappings, diffs, and stated project facts as evidence; do not defer a supported conclusion merely because a full repository is unavailable. For each material finding, name the concrete evidence, explain its runtime, authority/security, source-of-truth, or maintainability impact as applicable, and give the smallest compatible improvement. State meaningful no-change areas, confidence, and the exact missing evidence only when it could change the conclusion. Treat style preferences as findings only when they conflict with an explicit request or established convention, create a supported-platform incompatibility, or have a concrete correctness, security, or maintainability consequence.

Use scenario facts at their stated granularity. For example, “server-only economy modules are accidentally replicated” is direct evidence for a server-authority finding even when individual filenames are absent. Do not relabel supplied evidence as unavailable; qualify only the path-level details that truly remain unknown.

Finish when the material structural risks within the requested boundary are accounted for, including meaningful no-change areas or residual uncertainty when useful. Review remains read-only unless implementation is separately requested.

### Design

Preserve established conventions unless redesign is requested. When the project does not already resolve a material design choice, load the branch selected by **Reference routing**.

Provide the smallest structure that makes the requested work unambiguous: its DataModel/filesystem home, material runtime/replication/authoring boundaries, startup flow, dependency direction, integration contracts, and validation path. For every executable entrypoint, name its exact DataModel and filesystem path when applicable, its Roblox class or `RunContext`, the startup owner or caller, its direct dependencies, and the check that proves it starts. Reject path/class combinations that Roblox will not execute—for example, a `LocalScript` under `ReplicatedStorage`; use an executable client location or a `Script` with `RunContext = Client` there. Load specialist references only for affected specialist branches. Identify any required boundary-crossing changes as approval-dependent or owner actions rather than silently folding them into the authorized design.

Resolve each entrypoint to one concrete path/class/owner contract in the recommended design. Do not leave mutually exclusive placement alternatives in the main topology; mention an alternative only after the chosen contract and state what would replace, rather than coexist with, it. Files named as controller modules are `ModuleScript` dependencies unless the design explicitly makes them independent executable entrypoints and defines their coordination.

Design is read-only unless Implementation is separately requested. Finish when every designed item has an unambiguous home and startup/integration path and every material boundary contract is identified.

Put the complete design in the answer itself. A checklist that says to define filesystem mappings, startup flow, dependency direction, Remote contracts, or validation later does not satisfy Design.

### Migration plan

Use this route only when the user explicitly requests the migration/transition/conversion itself or asks for migration planning. A request to review whether a migration should happen remains Review unless migration planning is also requested.

Read `references/workflows/migration.md` and every specialist reference whose current-state or requested target-state trigger is present. Keep planning read-only unless implementation is also requested.

Produce concrete migration slices rather than phase headings. Each slice names the current item/path and target item/path, affected callers/requires/remotes/configuration, source-of-truth cutover point, owner action, recovery boundary, and verification. Finish only at the migration reference's exhaustive completion criterion: every move, affected reference, material topology/identity assumption, required owner action, specialist boundary, verification step, and necessary recovery boundary is accounted for.

When only hierarchy categories or proposed artifacts are supplied, produce provisional slices for each supplied category and label path-level assumptions; do not refuse to plan merely because file contents are absent. The answer must contain the slices rather than an action to create them later.

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
5. Follow the applicable persistence mode disclosed by `references/conventions/project-profile.md` when this Implementation establishes a greenfield project's durable structure, initializes missing established-project agent onboarding from durable conventions already established by the current bootstrap, or implements an explicitly requested project-wide redesign/migration that changes durable structural conventions. Established-project onboarding initialization must not expand discovery or persist task-local observations merely to populate the profile. Do not otherwise persist ordinary task-local feature work or restructuring merely because this skill was used.
6. Use an explicit recovery boundary when an operation is destructive, topology-sensitive, non-version-controlled, externally stateful, or difficult to reverse. Routine reversible filesystem edits already captured by version control do not need separate rollback bookkeeping.
7. Inspect the resulting diff or changed-output set when the operation is broad/generated, topology-sensitive, overlaps pre-existing work, or otherwise risks writes outside the intended set.
8. Run focused validation that covers the credible failure modes introduced by the change, including the persisted profile/onboarding when step 5 applies. Escalate validation when the affected boundary, risk, or a failed check warrants broader evidence.

For any topology-sensitive implementation—moves or renames, mapping/model/meta changes, source-of-truth cutovers, entrypoint or lifecycle rewiring, generated hierarchy output, or multi-step restructuring—completion requires all five safeguards: an explicit intended write set; tracing of affected requires, callers, remotes, mappings, and startup references; a recovery boundary before mutation; inspection of the resulting diff or generated output against the write set; and focused structural plus runtime validation for the changed boundary. If one cannot be performed, report it as a blocker or residual risk rather than implying the restructuring is complete.

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
