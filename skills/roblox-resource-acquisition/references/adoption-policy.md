# Adoption policy

Apply these defaults to Roblox development work. Explicit user scope requests and the project's own constraints override them.

## Scope and autonomy

The resources in scope are libraries/modules and development tools used for Roblox development. Consider reuse when it could reduce total implementation and maintenance effort. Prefer built-ins, an adequate authorized project capability or small custom code when they are simpler overall. Ordinary use of an adopted resource does not restart acquisition, and unrelated tasks do not trigger discovery.

A normal "add/use a library" request covers research, comparison when needed, selection, pinning, isolated checks, reversible integration, the project's own checks, and the matching record and CLAUDE.md entry. Carry that authorization through routine reversible steps without asking again. Inspect transitive dependencies as needed for reliability; they are not adopted in their own right.

**Child skills are opt-in.** At the end of an adoption, offer a reusable child skill in one sentence. Generate, validate and install one only when the user asks, or when the same pinned resource is clearly reused across projects. Reuse a matching child in the intended scope instead of creating a duplicate. A bundled child for the same pin (see the [bundled catalog](bundled-skills.md)) can be installed instead of generating one.

Explicit evaluation or comparison requests stop at the decision. An explicit integration-only, child-only, user-wide or other scope request sets its own boundary. Proactive discovery never authorizes replacing an adequate project standard, expanding the feature or changing an externally owned pin.

Bring costs, major architectural changes, unresolved authority or identity collisions, and decisions the evidence cannot support to the user with a concrete proposal. Respect the environment's permissions. Corrections to skills and dependency upgrades follow [on-demand maintenance](on-demand-maintenance.md#authority).

## Selection priorities

Prioritize reliability for the required behavior and sustainable maintenance, supported by source, executable evidence, relevant defect history, compatible releases, maintained documentation and dependency health. Activity timestamps, stars and feature count alone establish neither. A stable resource need not release often; check relevant open defects and compatibility instead of applying an age cutoff.

Compare total integration, maintenance and reversal effort against built-ins and a local implementation. Prefer the smallest solution that supports the required behavior reliably. Preserve explicit priorities and fixed targets. Apply the [evaluation rubric](evaluation-rubric.md) to serious candidates without invented aggregate scores. Use the community-evidence section of the [search playbook](search-playbook.md#community-evidence) for discovery, comparison and new adoption; keep routine use proportionate.

## Required proof and completion

Before finalizing a new adoption, run the smallest checks that show the intended use works at the exact selected target: installation and import (or tool invocation), the required happy path, representative project integration, and material failure or cleanup behavior. Require Roblox runtime evidence only for claims that depend on it; a development tool may be verified with its actual CLI, analyzer or build. Existing passing evidence is reusable only when the target and the inputs that determine it are unchanged.

Trust is separate from proof. A trusted resource keeps its trust basis, but a new adoption stays pending when a required integration or reliability check is unavailable or fails. Continue research, staging and unrelated safe work, and state the exact missing check and how it can run. Do not record an incomplete candidate as an adopted choice. An existing adopted choice stays recorded with the affected use blocked or limited; it is not silently retired.

Adoption is complete when the resource proof passes, the project's own checks pass, and the record and CLAUDE.md entry agree. When a child was requested, completion also needs a child that passes structural and required behavioral checks and is installed in the resolved scope (see [installing children](operational-lifecycle.md)). Explicit narrower scopes finish at their requested boundary. `pending` describes unfinished work, not a schema status.

## Reuse across projects

Default to one editable child per project. Stage outside discovery at `<project>/.roblox-resources/artifacts/skills/<skill-name>/`, then move the validated child to `<project>/.claude/skills/<skill-name>/`. Resolve the project root first; if it cannot be found, report that and continue other preparation without installing user-wide. Records keep the selected identity, pin, role, integration evidence and authority. See [project adoption](project-adoption.md#place-project-children) and [installing children](operational-lifecycle.md#one-editable-copy-per-scope).

An explicit user-wide request may stage at `~/.roblox-resources/artifacts/skills/<skill-name>/` and install at `~/.claude/skills/<skill-name>/`. Reuse that child across projects in that scope; visibility does not adopt the resource in any project or transfer proof. Existing user-wide children stay where they are.

Write reusable installation, mental model, common APIs, lifecycle, verification and troubleshooting guidance. Resolve the active project, package placement, declared pin and records at use time; keep task-specific paths and historical evidence out of the shared instructions. Development-tool guidance covers the commands, configuration and outputs the tool actually owns.

Reuse a child only for its canonical identity, reviewed target and intended scope. Its content may seed another project's child, but the copy carries no trust, integration proof or install claim. Projects pinned to different versions keep their pins and need separate children when the guidance cannot be shared; give co-visible variants distinct names and version-specific descriptions, and test their routing. User-wide variant records follow [state policy](state-policy.md#portable-resource-record-location).
