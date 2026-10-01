# Resolve material Roblox project choices

Use when the current request, project evidence, and applicable instructions/guidance leave a consequential choice open. New-project choices are resolved inside [needs-led setup](../workflows/onboarding.md). This reference supplies decision discipline rather than a fixed preference questionnaire.

## Existing projects

Preserve coherent implemented conventions and adopted dependency targets for ordinary work. Apply scope correctly: one feature's exception is not a replacement project-wide convention. Resolve authoring mappings before comparing filesystem layout with DataModel guidance.

Ask no preference questions when the task and project already resolve the material decisions. For a missing minor convention, choose a compatible local implementation; do not introduce a project-wide default or save a preference as an incidental step.

When conventions conflict or a material gap remains, state the exact choice, evidence already available, and smallest input needed from the user. A demonstrated compatibility/correctness failure is a finding; divergent viable styles are options.

## New or intentionally redesigned projects

The user has not selected global architecture/tooling defaults. Learn their needs and research choices; do not infer a preference from this skill's examples.

Possible decision dimensions include authoring ownership (Studio, Script Sync, filesystem mapping, or custom/mixed), language/compiler, entrypoint/lifecycle ownership, grouping, dependency posture, assets and place boundaries, test strategy, and development/release workflow. Resolve only dimensions relevant to the project. Framework and startup choices must identify a clear owner for each concern rather than layer competing owners.

Single bootstrap pairs, independent scripts, service/controller modules, feature grouping, components/ECS, explicit requires, and lifecycle loaders are options whose suitability depends on the needs. The [documented ModuleLoader SSA contract](../ssa/ssa-bootstrap.md) is an exact compatibility option for a deliberately adopted target, not the default for new projects or a currentness claim.

## Present options and carry the choice forward

For credible competing approaches, present a small useful set with project fit, ownership, costs/constraints, current evidence, and uncertainty, and recommend the supported fit with its decisive tradeoff and what would change it. Let the user choose genuinely consequential unresolved directions; make supported routine choices within the authorized task. An options list does not replace a justified recommendation. Batch independent choices; serialize dependent ones. A tool's popularity or release recency does not settle suitability.

Accept natural-language preferences and preserve previously selected decisions. After the choice, produce one coherent implementable setup/design; routine details follow that direction. Do not add another approval stop for task-local implementation already authorized, except the explicit setup review and documentation save gates.

Use [practices](../core/practices.md) for technical contracts and [evidence and freshness](../core/evidence-and-freshness.md) for current facts and developer-practice disputes. [Project guidance](project-profile.md) interprets durable decisions, while [review and persistence](project-profile-persistence.md) governs saving them.

Resolution is complete when consequential open choices have been selected or the exact unresolved decision is named, and the resulting implementation/design has unambiguous ownership and verification.
