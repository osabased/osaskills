# Reusable Roblox project guidance

Use when interpreting saved guidance or preparing requested onboarding/corrections. [Review and persistence](project-profile-persistence.md) owns guide, assessment, and instruction-pointer writes.

## Reuse and interpret

Read applicable instructions and their linked documentation first. Prefer a coherent existing project guide over a competing document. When no equivalent destination exists, propose `.agents/roblox/project.md` under the affected project root. Create durable guidance when requested, rather than as a prerequisite for an ordinary code task.

A useful guide covers the applicable boundaries in [project orientation](../workflows/project-orientation.md). Reuse supported sections even when another section is stale or incomplete. A title, fixed headings, or instruction marker does not prove completeness. The guide describes the project; it does not grant modification authority.

The current request and governing instructions prevail. Within those bounds, coherent implemented ownership and conventions guide ordinary work. Establish scope and freshness from linked source, effective authoring mappings, and runtime evidence. Resolve a filesystem/DataModel discrepancy through the mapping before deciding which description is stale.

## Keep the content durable

Explain scope, authoring/topology, startup/systems, non-obvious conventions, development/verification, and signals for reinspection. Link entry files, manifests, configuration, tests, and existing docs. Native configuration owns mutable inventories and versions; include commands only when an executable handoff needs them, with a link to their authoritative definition.

Record review date and evidence scope. Distinguish observed facts, provisional inferences, inaccessible surfaces, and checks run or unavailable. Keep optional improvements in a separate assessment until selected. Exclude temporary task logs, secrets, and unselected defaults.

Reinspect relevant claims when targets, mappings, ownership, startup, dependency contracts, entry files, or commands change. A local exception, unexplained dirty edit, or failed web lookup alone does not overturn project-wide conventions. Present the smallest supported correction under the existing review preference; an explicit approved update needs no second confirmation.

## Legacy `.agents/roblox/structure.md`

Legacy profiles remain useful at their stated scope. Preserve supported choices and `Freshness` guidance, including deliberately owned dependency targets. Missing fields express no preference, and a sparse conventions profile is not a complete overview.

If broader onboarding is requested, extend existing documentation or reference the profile from the guide. Review any pointer replacement or content migration; never automatically delete the profile or create a duplicate authority.

## Agent reachability

Use a small pointer in applicable project instructions and preserve human content. Verify the intended entry directory and instruction scope using the actual host's discovery behavior. A nested guide/pointer is not automatically visible to agents starting above that project.

An ancestor pointer must remain project-scoped and within the user's authorized scope. Do not claim usable fresh-agent onboarding merely because a file exists. If discovery or the write is unavailable, identify the required entry directory or owner action. Saving follows [review and persistence](project-profile-persistence.md).
