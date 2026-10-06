# Evidence and freshness

Use for library/tool first use, current platform or compatibility claims, recommendations, and demonstrated guidance drift. Embedded skill references supply navigation and compatibility context, not a guarantee of currentness.

## Match evidence to the claim

| Claim | Use |
| --- | --- |
| Project behavior or ownership | Implemented source, effective mappings, native manifests/locks/configuration, and available runtime evidence. Saved snapshots establish snapshot facts, not unseen live state. |
| Platform/tool behavior | Current canonical docs, source, and releases for the relevant behavior and the project's actual version/channel. Latest documentation alone cannot prove an older pin's behavior. |
| Recommended practice | Maintained primary guidance or inspectable implementations matched to the use case. Establish independent support before claiming consensus. Popularity and copied opinions are insufficient. |

Keep observations, conventions, recommendations, and uncertainty distinct. A supported compatibility/correctness failure is a defect; multiple viable approaches are choices.

## First use in a task

Before each needed library or tool's first use, including adopted resources and default tools, apply the shared [first-use freshness check](../../../roblox-resource-acquisition/references/first-use-check.md). Resolve identity and actual target, compare canonical stable releases and intended-use documentation, record the check, and disclose task-relevant changes or unavailable lookups. An adequate source review already done in this task suffices; reuse it while its inputs remain unchanged.

Check resources actually needed by this task, not the whole dependency graph. A newer release does not authorize an upgrade, and a failed currentness lookup does not erase valid exact-target proof. If the sibling policy is absent, perform the bounded check from canonical sources and disclose the unavailable shared maintenance capability. Unknown material identity, incompatibility, or a hard defect still blocks dependent use.

## Make a bounded recommendation

1. Resolve intended use, runtime/authoring environment, constraints, and deciding priorities from the request and project. Ask only when a missing input could change the choice, and wait on that choice while continuing independent research. Reuse fixed selectors and adequate authorized project capabilities.
2. Compare plausible candidates under the same needs using applicable canonical behavior/release evidence. Check fit, compatibility, maintenance, platform availability, license, and replacement cost where material. Separate stable releases from previews; confirm the source actually supports the attributed claim.
3. Recommend the supported fit, stating its decisive tradeoff, material uncertainty, and what would change it. Preserve genuinely unresolved consequential directions for the user. Cite material current claims with source/version/channel and review date; unavailable retrieval limits the claim rather than establishing a winner.

Identity and delivery are separate choices when acquisition/restoration matters. Preserve an established healthy manager and consider suitable native routes before custom tooling. Use [acquisition comparison](../../../roblox-resource-acquisition/references/qualification-workflow.md#compare-acquisition-and-maintenance-workflows) for that decision when the sibling is available.

## Respond to drift

Reinspect affected guidance when mapping, ownership, startup, target, dependency contracts, entry files, or commands change. A provisional observation, local exception, or failed lookup alone cannot justify rewriting project-wide conventions. Use [review and persistence](../conventions/project-profile-persistence.md) for project guide corrections.

Use [on-demand maintenance](../../../roblox-resource-acquisition/references/on-demand-maintenance.md) for actual skill-package upkeep and [resource acquisition](../../../roblox-resource-acquisition/SKILL.md) for acquisition/adoption/repair in scope. Healthy use does not start those full workflows. Preserve project pins and passing proof whose inputs remain valid; research supplies no new write authority.

## Starting sources

- Roblox: [Data model](https://create.roblox.com/docs/projects/data-model), [script locations](https://create.roblox.com/docs/scripting/locations), [Script Sync](https://create.roblox.com/docs/scripting/sync), [Studio testing](https://create.roblox.com/docs/studio/testing-modes), [client/server boundary](https://create.roblox.com/docs/scripting/security/client-server-boundary).
- Rojo: [versioned docs](https://rojo.space/docs/), [repository/releases](https://github.com/rojo-rbx/rojo).
- roblox-ts: [docs](https://roblox-ts.com/docs/), [usage](https://roblox-ts.com/docs/usage/), [repository](https://github.com/roblox-ts/roblox-ts).
- Other tools/frameworks: locate maintained canonical documentation, implementation, releases, and the adopted project contract.
