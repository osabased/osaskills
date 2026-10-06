# Needs-led Roblox project setup

Use for new-project setup or a deliberately chosen new foundation. Existing-project onboarding uses [project orientation](project-orientation.md). A bare invocation first establishes which job is needed, including whether a project already exists in Studio or elsewhere.

The recorded review preference is: learn the needs, research suitable approaches, present a coherent setup, then implement the approved result. A generic setup request starts this workflow; an already approved setup proceeds without another approval round.

## Resolve the needs that change the setup

Use supplied context and project evidence first. Ask unanswered, decision-sensitive questions in small rounds, normally one to three:

- Product/host: game and intended systems, places, plugin, package/model, or prototype.
- Authoring: Studio/external editor, language, code/asset ownership, existing content, collaboration, Git/build/CI needs.
- Constraints: runtime/lifetimes, networking/persistence/UI/testing, library posture, existing choices, maintenance or deployment constraints.

Skip answered and irrelevant subjects. Make routine details consistent with the chosen direction; use [preference resolution](../conventions/preference-resolution.md) for genuinely consequential open choices.

## Choose a supported fit

Research relevant approaches using [evidence and freshness](../core/evidence-and-freshness.md). Compare plausible candidates for unresolved roles, including plain modules and built-in capabilities. Use [tooling defaults](default-tooling.md) only where the setup needs those roles; preserve established compatible choices. Match authoring to source ownership before selecting synchronization. No language, framework, SSA contract, or loader is universal.

Recommend the supported fit with its deciding tradeoff and remaining material uncertainty. When credible alternatives lack a project-specific basis for selection, present the unresolved choice for the user. Qualifying a resource does not authorize installation before the setup review; [resource acquisition](../../../roblox-resource-acquisition/SKILL.md) handles relevant qualification/adoption without reselecting project-owned pins.

## Present one implementable proposal

Show enough detail to review what will exist and how it will work:

- Needs served, selected approach, and material source-backed tradeoffs.
- Project/artifact roots, authored/generated/asset ownership, and filesystem-to-DataModel or host mapping.
- Exact executable paths, classes/contexts and owners; lifecycle/readiness, dependencies, and planned communication/authority boundaries.
- Needed tools/dependencies and compatible targets; preparation/restore behavior and local/CI checks.
- Separate Studio/host validation, intended edits/installations/sync, owner actions, and recovery where needed.
- Remaining evidence gaps and proposed guidance destination.

Use [practices](../core/practices.md) and references for the selected boundaries. A package/plugin needs its consumer or host contract, not invented game bootstraps. If saving guidance in the same approval, include its exact content/pointer under [review and persistence](../conventions/project-profile-persistence.md).

Present the concrete proposal and wait for review unless it has already been approved. This review does not reopen choices the user has already settled.

## Implement and verify

Implement the approved foundation with native project tools. Keep restore distinct from updates and authored source distinct from generated output. Add only needed roles and qualify new verification gates with representative failing probes when their ability to catch meaningful errors is uncertain.

Run the applicable checks and distinguish static/build results from Studio/host execution. Setup is complete at the claimed evidence level when the approved foundation is integrated, dependencies and startup have clear ownership, and applicable checks pass. Name required unavailable checks; verify approved guidance writes separately. Material deviations from the reviewed setup return for review rather than becoming new defaults.
