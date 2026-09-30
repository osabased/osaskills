---
name: structure-roblox-projects
description: "Situate agents in unfamiliar Roblox projects, maintain reusable project guidance, and guide new-project setup. Also use for material placement, startup, authoring, or migration decisions. Reuse usable guidance for routine edits rather than repeating onboarding."
---

# Structure Roblox Projects

Help an agent understand how to work in this Roblox project, or help the user establish a suitable new project. Detect the actual project; no language, framework, authoring workflow, game topology, or tool stack is the universal default.

## Choose the work

- **Existing-project onboarding:** when entering an unfamiliar Roblox project without usable guidance, build a broad reusable overview using [project orientation](references/workflows/project-orientation.md). Trigger this during ordinary project tasks too. Present the overview and a separate assessment for user review before saving either or adding an instruction pointer. Continue independently authorized work while documentation review is pending when sufficient evidence supports that work.
- **Reuse existing guidance:** read the applicable project guide, check its scope and relevant facts against current evidence, and inspect the current task's integration edges. Missing or stale sections call for focused investigation, not a full repeat of onboarding. A legacy conventions profile alone may be useful without constituting a complete overview.
- **New-project setup:** ask about the user's needs, research suitable current approaches, and present one coherent setup for review before implementation. Follow [setup](references/workflows/onboarding.md); a bare invocation first determines whether a project already exists.
- **Implementation, Design, Review, or Migration:** complete the requested work through the routes below. Orientation supplies context; it does not convert a value edit into structural redesign or an ordinary move into a migration.

Project guidance belongs to the affected project. [Project guide interpretation](references/conventions/project-profile.md) covers existing documentation and legacy profiles; [review and persistence](references/conventions/project-profile-persistence.md) covers saving. Honor existing project instructions and explicit restrictions.

## Establish reliable context

Resolve project boundaries, authoring owners, source/generated distinctions, runtime and replication boundaries, startup and lifecycle, major systems and dependencies, conventions, and verification. For initial onboarding, cover the project broadly at those boundaries; for subsequent work, investigate only relevant edges. Directory names, method signatures, and installed tools are clues, not proof of their roles.

Use [evidence and freshness](references/core/evidence-and-freshness.md) for current platform/tool claims and practice recommendations. Separate observed project facts, supported platform/tool behavior, and options. Check actual project versions before applying version-sensitive advice. Present credible disputed options and their tradeoffs for the user to choose; distinguish dispute from a demonstrable compatibility or correctness defect. Preserve established targets until an upgrade or redesign is selected.

At activated use, check for the sibling `.skill-maintenance/structure-roblox-projects.json` guard; ordinary dependent use waits while it exists. For reusable guidance defects or package maintenance, use the shared [on-demand maintenance policy](../roblox-resource-acquisition/references/on-demand-maintenance.md) when available. It does not select project architecture or grant project writes. If the sibling package is missing, use this skill's evidence rules and report only the upkeep capability that is unavailable.

## Load specialist guidance when needed

Evaluate both current and proposed structures. Initial orientation may inspect mappings and entrypoints without applying an implementation procedure.

| Decision or boundary | Reference |
| --- | --- |
| Ordinary placement, executable entrypoints, grouping, source of truth, or Remote design | [Practices](references/core/practices.md) |
| Material project choices still unresolved after inspection or setup intake | [Preference resolution](references/conventions/preference-resolution.md) |
| Explicit restrictions, ambiguous pre-existing ownership, or broad/generated writes | [Modification scope](references/core/modification-scope.md) |
| Rojo mapping, build/serve workflow, topology changes, or artifact composition | [Rojo](references/workflows/rojo.md) |
| Script Sync ownership, conflicts, managed topology, or metadata | [Script Sync](references/workflows/script-sync.md) |
| The exact documented ModuleLoader SSA contract is adopted or explicitly selected | [SSA compatibility](references/ssa/ssa.md); load [bootstrap](references/ssa/ssa-bootstrap.md) for infrastructure changes |
| Server Authority prediction/rollback or shared deterministic simulation | [Server Authority](references/platform/server-authority.md) |
| An active or materially suspected capability sandbox | [Script Capabilities](references/platform/script-capabilities.md) |
| Explicit migration, or topology-sensitive moves requiring tracing/recovery | [Migration](references/workflows/migration.md), using its applicable mode |

Other compilers, sync systems, frameworks, plugins, packages, models, and build pipelines use the same orientation/evidence contracts and their canonical documentation. A missing specialist reference is not grounds to reshape a project into a familiar template.

## Complete the requested work

### Feature integration and Implementation

The requested behavior authorizes necessary edits to modules, callers, shared entrypoints, mappings, configuration, and focused checks, subject to explicit restrictions. Preserve pre-existing work and coherent ownership; use modification scope only when a real boundary is unresolved.

Trace affected startup, require/import, discovery, communication, and mapping edges before topology-sensitive changes. Establish recovery for those changes, inspect the diff/generated output, and run the smallest checks covering the changed boundary. Broaden for failures or unresolved integration risks. Preserve compiled/generated output ownership.

Saving new or revised guidance follows the review gate even during implementation. Documentation approval is independent of authorization for the requested code change. A reviewed setup can include an exact guide/pointer preview and authorize those writes together; re-preview material differences from that approved result.

Completion means the behavior is integrated and applicable checks pass. Distinguish source/build evidence from Studio runtime proof and name any unavailable required check. A successful build or loader-state flag alone does not prove successful startup.

### Review and Design

Support material findings with project evidence, concrete impact, and the smallest compatible improvement. Describe conflicting supported approaches as options. Separate observed weaknesses from suggestions and unresolved evidence.

For Design, provide an implementable topology: filesystem/DataModel or host homes, source and generated ownership, execution/replication boundaries, startup/lifecycle, dependencies, communication contracts, and checks. Name executable path/class/context/owner per entrypoint. Review and design stay read-only unless implementation is requested.

### Migration

Use the full migration workflow only for an explicitly requested migration or migration plan. Account for concrete source/target paths, affected references, cutover, recovery, owner actions, and verification. Ordinary moves apply relevant safeguards without triggering unrelated migration accounting.

## Structural invariants

- Keep privileged gameplay rules/state, secrets, persistence, purchases, and client-input validation server-authoritative. Replicate only what clients need.
- Keep earliest-loading content small and intentional.
- Identify a clear startup owner and lifecycle for each execution environment; point dependencies toward cohesive domain/shared modules.
- Shared module source does not share mutable state across Luau environments.
- Adopt tools, frameworks, packages, or lifecycle machinery for demonstrated project needs. Explicit user choices and coherent established ownership govern the project.
