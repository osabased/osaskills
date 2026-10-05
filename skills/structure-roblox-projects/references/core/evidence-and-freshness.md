# Evidence, currentness, and developer practices

Use when onboarding, setup, or structural work relies on platform/tool behavior, community practice, or a recommendation that may have changed. Skill references are navigational/compatibility guidance, not evidence that every embedded statement remains current.

## Match the claim to its authority

- **Project facts:** inspect applicable implemented source, effective mappings, native manifests/locks/configuration, and actual runtime evidence. Identify project scope and representation. Supplied snapshots support claims about that snapshot, not unseen live state.
- **Platform and tool facts:** read current Creator Hub/API/release documentation or the tool's canonical maintained docs/repository for the exact relevant behavior. Check version/channel and the project's adopted target. Documentation for latest alone cannot establish compatibility with an older pin.
- **Practice recommendations:** research the relevant decision and use case using maintained first-party guides, maintainer explanations, credible firsthand implementation reports, or inspectable production/reference projects. Identify authors, context, recency, and independent corroboration where a consensus claim is material. Popularity, search rank, and several copied opinions do not establish consensus.

Separate supported facts, local conventions, recommendations, and uncertainty in the overview. Present credible conflicting options with their fit and costs; do not fabricate a unified consensus. A demonstrated invalid execution or incompatible API is a correctness issue, not a matter of preference.

## Establish the selection brief

For an open-ended library, tool, or workflow choice, derive the actual purpose, relevant behavior/lifecycle, execution or authoring environment, and deciding priorities from the request, project evidence, and prior answers. API names alone may leave the intended use unresolved.

When purpose or another missing input could change the choice, ask one concise question or a small batch and wait before selecting, downloading a selected candidate, or creating its dependency files. Continue independent inspection or research while waiting. Resolve only decision-sensitive gaps; do not repeat answered questions or require an exhaustive questionnaire. A narrow evaluation/download-only scope still needs this intake when it could change the choice.

Preserve a fixed identity/selector and an adequate authorized project capability rather than reopening selection. A fixed target can still need a genuinely missing compatibility input. Use sufficient supplied context without an extra intake gate.

## Research a bounded decision

1. State what decision or claim depends on current evidence and what project constraints could change it.
2. Read the authoritative behavior sources and relevant stable release/compatibility information. Inspect local targets and installed versions where needed. Follow a documentation page's explicit version rather than assuming a search result is current.
3. For consequential practice/tool selection, compare approaches under the same needs. Evaluate actual role, authoring/runtime fit, support status, compatibility, maintenance burden, platform availability, license, and replacement cost. Prefer the few options with plausible fit over a library catalogue.
4. Cite sources near material conclusions and record the relevant source/version/channel and review date in the assessment or setup proposal. Check that the linked page actually supports the attributed claim; a matching label or search extraction can conceal an unrelated member URL or documentation version. When a documentation UI is unavailable, use its canonical maintained source if accessible and name that source. Qualify claims supported only by incomplete retrieval. A recent timestamp alone proves no behavior. Separate stable behavior from beta/preview proposals.
5. Recommend the currently best-supported fit once the brief and evidence suffice. State the decisive tradeoff, material uncertainty, and what would change the recommendation; an options list alone does not finish a selection request. Leave genuinely consequential unresolved directions to the user while making supported routine choices locally. Missing evidence does not establish a winner or consensus.
6. State unresolved claims and unavailable lookups precisely. If current evidence cannot be retrieved, preserve local knowledge as such, offer a provisional path only where it is justified, and do not claim a current recommendation is verified.

Treat library identity and acquisition/maintenance workflow as separate decisions when delivery, restoration, or updating matters. Consider suitable maintained native acquisition routes before proposing custom tooling; a missing manifest does not justify a custom lock/restore workflow. Preserve an established healthy manager for ordinary work unless reconsideration is authorized or a material problem is demonstrated. For resource-specific comparison, use [acquisition workflow guidance](../../../roblox-resource-acquisition/references/qualification-workflow.md#compare-acquisition-and-maintenance-workflows) when that sibling is available.

Before each needed library or development tool's first use in a task, including default tooling and resources with existing skills, apply the shared [first-use freshness check](../../../roblox-resource-acquisition/references/on-demand-maintenance.md#first-use-freshness-check). Compare canonical stable releases and relevant documentation with the actual installed/project-pinned target; verify that reused guidance fits that target. If the sibling policy is absent, perform the bounded check directly using canonical sources and disclose that the shared maintenance capability is unavailable. An adequate review already performed in this task satisfies the check; reuse unchanged evidence within the task, recheck changed inputs, and disclose unavailable currentness lookups. Finding a newer release does not authorize changing an established pin.

Existing-project orientation researches the current facts that affect interpretation and assessment and checks resources it will actually use; it does not audit every dependency for latest releases. New setup researches each selected workflow/tool/dependency role sufficiently to justify its fit. No scheduled maintenance or automatic upgrades are implied.

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
