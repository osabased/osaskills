# Orient an agent in an existing Roblox project

Use when the user requests a reusable overview or agent onboarding. Ordinary task orientation stays scoped to the affected source and integration edges in the [work loop](../../SKILL.md#work-loop). Broad onboarding maps ownership and navigation; it is not a code or security audit.

## Locate the project

Read applicable instructions and existing documentation. Establish project roots, product type, targets, intended agent entry directory, and available evidence. A repository may contain multiple places, plugins, packages, tools, or unrelated projects. An empty folder or unavailable Studio connection does not prove that an experience is empty. Ask for the smallest missing location or representation only when it blocks useful work.

Distinguish live Studio state from saved places/models, exports, and source snapshots. Trace authored source through compilers, generated output, and mappings to the actual host. Disabled bootstraps, examples, fixtures, caches, and unmapped files may not be active code. Use project-required navigation tools when available; indexing the entire project is not an onboarding prerequisite.

## Map ownership and integration

Cover applicable boundaries at enough depth that a fresh agent can find where to work. Use representative source traces and links to authoritative configurations rather than exhaustive inventories.

| Boundary | Establish |
| --- | --- |
| Identity and topology | Artifact type, roots, places/targets, shared source, build variants, and external surfaces. |
| Authoring | Who owns code, instances, assets, metadata, and configuration; how they reach Studio/another host; sync and conflict ownership. |
| Language and generation | Authored inputs, compiler/build pipeline, generated/vendor outputs, and dependency restoration. |
| Execution and startup | Effective paths, classes/context, enabled state, startup/discovery owners, readiness/failure handling, and relevant object/character/plugin/Actor lifetimes. |
| Systems and interfaces | Major domains and entry files, dependency direction, networking/authority, persistence, UI/assets, packages, and external integrations. |
| Tools and dependencies | Native identity/version sources and commands; runtime libraries versus development tools and host integrations. |
| Conventions | Implemented naming/grouping/API/lifecycle/error/cleanup/test practices, instruction scope, and intentional exceptions. |
| Verification and delivery | Preparation/check/build/sync paths, CI, Studio/host checks, development/release boundaries, and publishing ownership. |

Cross-check contradictory prose against its applicable source and mapping before declaring it stale. Preserve uncertainty where ownership or recency is unresolved. Custom compilers, packages, plugins, and mixed workflows keep their own host/consumer contract; a missing specialist reference does not justify replacing them.

Stop discovery when every applicable boundary and identified target/startup mechanism has a navigational answer or a specific evidence gap. Further reading should be driven by a gap that can change the map, not a fixed file count.

## Present the overview and assessment

The overview explains project scope, source/host ownership, major systems, how to edit and verify, and non-obvious conventions. Link actual entry files and source-of-truth definitions; avoid copying trees, dependency/version lists, or command inventories that are cheap to inspect. Mark what was inspected, inferred, run, or unavailable. A saved snapshot supports snapshot claims only.

Keep supported risks and optional improvements in a separate assessment, with evidence, impact, and tradeoffs. Use [evidence and freshness](../core/evidence-and-freshness.md) for current platform/tool or practice claims. An older pin or uncommon framework is not itself a defect; onboarding does not select upgrades or redesigns.

Use [project guidance](../conventions/project-profile.md) to reuse existing documentation and [review and persistence](../conventions/project-profile-persistence.md) before saving. The result is ready for review when a fresh agent can locate owned source, understand how it executes, preserve conventions, and choose the checks at the stated evidence level. Name missing Studio/host evidence without claiming full runtime verification. An unsaved overview can support separately authorized work.
