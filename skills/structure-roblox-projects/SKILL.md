---
name: structure-roblox-projects
description: "Orient in Roblox projects and resolve placement, startup, authoring, or migration boundaries. Use for unfamiliar projects, structural work, requested reusable guidance, and new-project setup. Reuse established guidance and investigate only what the task needs."
---

# Structure Roblox Projects

Work from the project's actual authoring and runtime ownership. Preserve a coherent existing foundation and finish the requested task; examples and preferred tools are options for unresolved needs.

## Work loop

1. **Locate the owned source.** Read project instructions and useful existing guidance. Establish the affected project/targets, authored versus generated content, authoring/sync owners, and the startup or consumer paths relevant to this task. Follow mappings and imports instead of inferring execution from folder names. An empty working directory does not establish that an existing Studio project is empty.
2. **Trace the affected boundary.** Resolve runtime/replication, lifecycle, dependencies, and the checks needed for the change. Recheck stale or contradictory guidance locally. Stop orientation when these questions have supported answers or specific material gaps; a routine edit does not require a broad overview, a new guide, or an architecture assessment.
3. **Complete the authorized work.** Preserve established conventions, toolchain, and pins. Include necessary caller, entrypoint, mapping, configuration, and focused-check edits. Trace topology-sensitive moves before applying them and keep a proportionate recovery path. Use the references below for boundaries the task actually crosses.
4. **Verify and stop.** Inspect the diff and generated effect, then run the smallest checks covering the changed behavior. Broaden only for failures or unresolved integration risks. Completion means the requested behavior is integrated and applicable checks pass; identify blocked or unavailable checks precisely. A build, offline execution, or loader-state flag alone does not prove Studio startup, rendering, input, or multiplayer behavior.

Keep privileged gameplay rules/state, secrets, persistence, purchases, and client-input validation server-authoritative; replicate only what clients need. Shared ModuleScript source does not share mutable state across Luau environments. Give each execution environment a clear startup/lifecycle owner, and keep earliest-loading content small.

For explicit restrictions or ambiguous pre-existing/generated ownership, use [modification scope](references/core/modification-scope.md). A shared file is not automatically restricted. Continue independent authorized work when a required write is blocked, and identify the exact unfinished integration.

## Match the requested deliverable

- **Reusable onboarding:** use [project orientation](references/workflows/project-orientation.md) when the user wants a project overview or durable agent guidance. Cover the actual project broadly at ownership/integration boundaries and keep factual guidance separate from optional improvements. [Project guidance](references/conventions/project-profile.md) covers reuse and saving; honor its review preference without blocking separately authorized code work.
- **New setup or a deliberately changed foundation:** use [needs-led setup](references/workflows/onboarding.md). Resolve material needs, research the fit, and present one implementable setup for review. Act on an already approved setup without asking again.
- **Review or design:** stay read-only unless implementation is requested. Support findings with concrete project impact. A design identifies source/generated ownership, exact entrypoint paths/classes/contexts and owners, dependency/communication boundaries, and checks for the proposed behavior.
- **Migration:** use [migration](references/workflows/migration.md) for an explicit migration or plan. Ordinary moves use its relevant tracing/recovery safeguards without a migration-wide inventory.

## Boundary references

| When the task needs it | Read |
| --- | --- |
| Placement, executable entrypoints, grouping, source of truth, or Remote design | [Practices](references/core/practices.md) |
| A consequential project choice remains unresolved | [Preference resolution](references/conventions/preference-resolution.md) |
| Rojo mapping, build/serve workflow, topology, or artifact composition changes | [Rojo](references/workflows/rojo.md) |
| Script Sync ownership, conflicts, managed topology, or metadata changes | [Script Sync](references/workflows/script-sync.md) |
| The exact documented ModuleLoader SSA contract is adopted or explicitly selected | [SSA compatibility](references/ssa/ssa.md); [bootstrap](references/ssa/ssa-bootstrap.md) for infrastructure changes |
| Server Authority prediction/rollback or shared deterministic simulation | [Server Authority](references/platform/server-authority.md) |
| An active or materially suspected capability sandbox | [Script Capabilities](references/platform/script-capabilities.md) |

Plugins, packages/models, compilers, and custom or mixed workflows keep their real host/consumer contracts. Use their canonical documentation when these references do not cover the boundary.

## Default tooling

When configuring tools, use [tooling defaults and verification](references/workflows/default-tooling.md) for the roles needed. Compatible established choices take precedence, including Wally. Choose the authoring workflow from source ownership before enabling sync. Acquisition, integration, or upgrades use [resource acquisition](../roblox-resource-acquisition/SKILL.md) within the authorized scope.

## Current evidence and maintenance

Before a needed library or tool's first use in a task, follow [evidence and freshness](references/core/evidence-and-freshness.md). Reuse unchanged checks within the task and preserve adopted targets. Current platform, compatibility, or recommendation claims need authoritative evidence for the actual project version; disclose unavailable lookups.

At activation, check the sibling `.skill-maintenance/structure-roblox-projects.json` guard. If present, ordinary dependent use waits for recovery through [on-demand maintenance](../roblox-resource-acquisition/references/on-demand-maintenance.md). Use that policy for a demonstrated reusable-guidance defect or package upkeep, not as an extra project workflow. If the sibling is unavailable, use canonical sources and disclose the missing capability when it matters.
