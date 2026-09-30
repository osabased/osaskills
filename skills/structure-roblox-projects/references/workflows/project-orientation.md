# Orient an agent in an existing Roblox project

Use for initial onboarding, requested broad orientation, or a material gap in reusable guidance. The deliverable is a navigable project overview and separate assessment, presented for review. Broad coverage concerns ownership and integration boundaries; it is not an exhaustive code/security audit.

## Identify the project and available evidence

Read applicable instructions and existing project documentation first. Establish repository/workspace and project roots, product type, intended agent entry directory, and available surfaces. A repository may contain multiple places, packages, plugins, tools, and non-Roblox projects; map their boundaries rather than treating every manifest as one experience.

Recognize evidence from Studio/DataModel access, saved places/models, exports, source trees, manifests, locks, build configurations, tests, CI, and supplied project facts. Distinguish live state from saved snapshots. Do not infer an empty/new project from an empty working directory when the experience may exist in Studio or elsewhere. Ask for the smallest missing location or representation when it prevents useful orientation. Use available tools or owner-supplied artifacts; tool availability never proves an unseen surface is empty.

Studio-only, Script Sync, Rojo, Luau, roblox-ts/other compilers, custom sync/build systems, frameworks, packages/models, plugins, multi-place experiences, and mixed workflows are all valid inputs. These are detection examples, not an exhaustive classifier. Document an unfamiliar workflow's real input/output/ownership contract using its maintained sources.

If `.codegraph/` exists and project instructions require CodeGraph, use it for locating/understanding code; otherwise use focused file/symbol searches. Do not index a project solely for onboarding.

## Build a broad map from actual boundaries

Cover the following at the granularity needed for a future agent to choose where to work. Mark relevant missing evidence; omit inapplicable topics with a reason rather than inventing content.

| Area | What to establish and useful evidence |
| --- | --- |
| Identity and topology | Experience/place, plugin, package/model, or other artifact; project roots, multiple places/targets, shared code, build variants, external surfaces, and intended agent entry directory. |
| Authoring ownership | Where code, instances, assets, metadata, and configuration are edited; how changes reach Studio or another host; sync/conflict owners; live sessions and permissions only when relevant. Mixed ownership may vary by subtree. |
| Language and generation | Authored languages, compiler inputs/outputs, generated/vendor directories, package restoration, and the canonical build pipeline. Trace imported source through generated output to the mapped artifact before assuming disk code executes. |
| Execution and startup | Effective DataModel/host paths, classes and relevant execution context, enabled state, bootstrap/discovery owners, lifecycle ordering/readiness/failure handling, object/character/plugin lifetimes, and separate runtimes/Actors when present. Trace every identified major startup mechanism, not merely a file named Main. |
| Systems and interfaces | Major feature/domain areas, their responsibilities and entry files, dependency direction, networking/authority, persistent state, UI, assets, reusable packages, and externally integrated services when present. Use representative traces to understand each major boundary; do not inventory every function or Remote by default. |
| Dependencies and tools | Distinguish runtime libraries, development tools, editor/Studio integrations, and generated artifacts. Find authoritative identities/versions and commands in manifests/locks/configuration. Verify actual installations when a check depends on them. |
| Conventions | Coherent local naming/grouping/API/lifecycle/error/cleanup/test practices, instruction scope, and intentional exceptions. Trace representative real modules; a framework name is insufficient evidence of its adopted contract. |
| Verification and delivery | Preparation, formatting/type/lint/test/build paths, CI expectations, Studio or host checks, release/development separation, and publish/deploy ownership. Distinguish a documented command from one actually run. |

Start from roots/manifests and then follow mappings, startup, imports/requires, and major integration edges. Inspect source as well as prose. Cross-check conflicting README/profile/manifest claims against the applicable implemented source and runtime representation; preserve uncertainty until ownership and recency are established. Old source, disabled bootstraps, fixtures, examples, dependency caches, and unmapped directories may not be active project code.

Stop broad discovery when each applicable area above has an evidence-backed navigational answer or a specific documented gap, all identified project targets and startup/authoring mechanisms are accounted for at overview level, and further reading is unlikely to change that map. Assess these coverage obligations rather than using a fixed file count or claiming completeness from one successful command. Deep behavior questions beyond this boundary belong to the current task or a separately requested review.

## Present a reusable overview

Write for a fresh agent who lacks this session. Include:

- project scope and available/unavailable surfaces;
- a concise topology or ownership table linking actual entry files and authoritative configurations;
- how to edit, build/sync, start, and verify the project without writing generated or foreign-owned content;
- major systems, integration rules, conventions, and exceptions;
- what was inspected, checked, inferred, or remains unknown, including the precise owner evidence needed to resolve important gaps.

Link stable entry files and sources of truth rather than copying complete trees, scripts, tool version lists, dependency graphs, or runtime inventories. Anchor significant conclusions to those sources. Configuration supplies mutable values; guidance explains interpretation, relationships, and non-obvious conventions. Broad does not mean duplicating the repository.

## Keep assessment distinct

After the factual overview, report supported risks, incompatible/outdated behavior, relevant tooling gaps, and optional improvements with evidence, impact, and tradeoffs. Use [evidence and freshness](../core/evidence-and-freshness.md) for currentness and developer-practice claims. An older pin or uncommon framework is not itself a defect.

When credible approaches disagree, present options and ask the user to select any consequential direction before it shapes implementation. Orientation neither upgrades dependencies nor normalizes architecture. It may reveal a concrete current-task blocker; keep that blocker separate from optional modernization.

## Review and handoff

Use [project guide interpretation](../conventions/project-profile.md) to integrate existing documentation and [review and persistence](../conventions/project-profile-persistence.md) for the exact save preview. Saving is pending until the user approves; an unsaved overview can still support authorized work.

Onboarding is ready for review when the coverage obligations above are satisfied at the stated evidence level and a fresh agent can locate the owned source, understand how it becomes executable, preserve the key conventions, and choose the applicable checks. If Studio/host/other required evidence is unavailable, label the overview provisional for those surfaces rather than claim fully verified onboarding.
