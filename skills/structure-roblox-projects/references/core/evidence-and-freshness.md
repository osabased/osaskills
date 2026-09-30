# Evidence, currentness, and developer practices

Use when onboarding, setup, or structural work relies on platform/tool behavior, community practice, or a recommendation that may have changed. Skill references are navigational/compatibility guidance, not evidence that every embedded statement remains current.

## Match the claim to its authority

- **Project facts:** inspect applicable implemented source, effective mappings, native manifests/locks/configuration, and actual runtime evidence. Identify project scope and representation. Supplied snapshots support claims about that snapshot, not unseen live state.
- **Platform and tool facts:** read current Creator Hub/API/release documentation or the tool's canonical maintained docs/repository for the exact relevant behavior. Check version/channel and the project's adopted target. Documentation for latest alone cannot establish compatibility with an older pin.
- **Practice recommendations:** research the relevant decision and use case using maintained first-party guides, maintainer explanations, credible firsthand implementation reports, or inspectable production/reference projects. Identify authors, context, recency, and independent corroboration where a consensus claim is material. Popularity, search rank, and several copied opinions do not establish consensus.

Separate supported facts, local conventions, recommendations, and uncertainty in the overview. Present credible conflicting options, their fit and costs, and the decision needed from the user; do not fabricate a unified consensus. A demonstrated invalid execution or incompatible API is a correctness issue, not a matter of preference.

## Research a bounded decision

1. State what decision or claim depends on current evidence and what project constraints could change it.
2. Read the authoritative behavior sources and relevant stable release/compatibility information. Inspect local targets and installed versions where needed. Follow a documentation page's explicit version rather than assuming a search result is current.
3. For consequential practice/tool selection, compare approaches under the same needs. Evaluate actual role, authoring/runtime fit, support status, compatibility, maintenance burden, platform availability, license, and replacement cost. Prefer the few options with plausible fit over a library catalogue.
4. Cite sources near material conclusions and record the relevant source/version/channel and review date in the assessment or setup proposal. Check that the linked page actually supports the attributed claim; a matching label or search extraction can conceal an unrelated member URL or documentation version. When a documentation UI is unavailable, use its canonical maintained source if accessible and name that source. Qualify claims supported only by incomplete retrieval. A recent timestamp alone proves no behavior. Separate stable behavior from beta/preview proposals.
5. State unresolved claims and unavailable lookups precisely. If current evidence cannot be retrieved, preserve local knowledge as such, offer a provisional path only where it is justified, and do not claim a current recommendation is verified.

Existing-project orientation researches the current facts that affect interpretation and assessment; it does not audit every dependency for latest releases. New setup researches each selected workflow/tool/dependency role sufficiently to justify its fit. Reuse evidence while its source, target, claim, and assumptions remain unchanged within the task. No scheduled maintenance or automatic upgrades are implied.

## Keep guidance useful over time

The project guide links mutable facts to their source of truth and states when reinspection is needed: changed mappings or generated ownership, new/removed targets, changed bootstraps/lifecycle, dependency identity or API changes, moved entry files, inconsistent commands, or observed documentation drift. Future agents verify relevant links/claims before relying on them and inspect only the affected gaps.

Propose a correction with evidence when a saved guide is stale. [Review and persistence](../conventions/project-profile-persistence.md) governs writes. A provisional observation, local exception, dirty unexplained edit, or failed web lookup is insufficient to rewrite project-wide conventions.

Use the shared [on-demand maintenance policy](../../../roblox-resource-acquisition/references/on-demand-maintenance.md) for authorized skill-package upkeep, and [resource acquisition](../../../roblox-resource-acquisition/SKILL.md) when selecting, qualifying, adopting, or repairing a community resource is actually in scope. Read the relevant branch rather than starting a resource lifecycle for every installed package. If that sibling is absent, use canonical sources and the current task's authorization; disclose the unavailable qualification/upkeep capability when it matters.

## Starting sources

Resolve versions and follow maintained links; these are starting points rather than a preferred stack.

- Roblox: [Data model](https://create.roblox.com/docs/projects/data-model), [Script types and locations](https://create.roblox.com/docs/scripting/locations), [Script Sync](https://create.roblox.com/docs/scripting/sync), [Studio testing](https://create.roblox.com/docs/studio/testing-modes), [client/server security](https://create.roblox.com/docs/scripting/security/client-server-boundary).
- Rojo: [versioned documentation](https://rojo.space/docs/), [canonical repository and releases](https://github.com/rojo-rbx/rojo).
- roblox-ts: [maintained documentation](https://roblox-ts.com/docs/), [usage](https://roblox-ts.com/docs/usage/), [canonical repository](https://github.com/roblox-ts/roblox-ts).
- Other workflows/frameworks/tools: locate their canonical maintained docs, implementation, releases, and the project's actual contract before applying advice.
