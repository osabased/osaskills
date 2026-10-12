# Needs-led Roblox project setup

Use for a new project or a deliberately chosen new foundation. For an existing project's overview, use the [project guide](../conventions/project-guide.md). A bare "help me set up a project" first establishes which job is needed, including whether a project already exists in Studio or elsewhere.

Default flow: learn the needs, research suitable approaches, propose one setup, then build it once approved. If the user already approved a setup or asked you to just build it, skip the review step.

## Resolve the needs that change the setup

Use supplied context and project evidence first. Ask the unanswered, decision-changing questions in small rounds, usually one to three:

- Product/host: game and intended systems, places, plugin, package/model, or prototype.
- Authoring: Studio or external editor, language, code/asset ownership, existing content, collaboration, Git/build/CI needs.
- Constraints: runtime lifetimes, networking/persistence/UI/testing, attitude to third-party libraries, existing choices, deployment.

Skip answered and irrelevant subjects. Make routine details consistent with the chosen direction; use [preference resolution](../conventions/preference-resolution.md) for genuinely consequential open choices.

## Choose a supported fit

Research the relevant approaches using [evidence and freshness](../core/evidence-and-freshness.md). Compare plausible candidates for each open role, including plain modules and built-in features. Use [default tooling](default-tooling.md) only for roles the setup needs. Choose the authoring workflow from source ownership (see [source of truth](../core/practices.md#source-of-truth)) before choosing sync. No language, framework, SSA contract, or loader is universal.

Recommend the supported fit with its deciding tradeoff and remaining uncertainty. When credible alternatives have no project-specific tiebreaker, give the choice to the user. Researching a resource does not authorize installing it before the review.

## Propose one implementable setup

Show enough to review what will exist and how it works:

- Needs served, the chosen approach, and its sourced tradeoffs.
- Project roots, authored/generated/asset ownership, and the filesystem-to-DataModel (or host) mapping.
- Exact executable paths, classes or RunContexts and owners; lifecycle/readiness, dependencies, and communication/authority boundaries.
- Tools and dependencies with compatible versions; restore commands and local/CI checks.
- Studio checks, planned installs/sync, owner actions, and recovery where needed.
- Remaining evidence gaps and where project guidance will be saved.

Use [practices](../core/practices.md) and the specialist references for the chosen boundaries. A package or plugin needs its consumer or host contract, not invented game bootstraps. If guidance will be saved as part of the setup, include its content and `CLAUDE.md` pointer (see the [project guide](../conventions/project-guide.md#save-it)).

Present the proposal and wait for review unless it is already approved. The review does not reopen choices the user already settled.

## Implement and verify

Build the approved foundation with native project tools. Keep restore separate from updates and authored source separate from generated output. Add only needed roles. When it's unclear whether a new check catches real errors, try it once against a deliberately broken input.

Run the applicable checks and report static/build results separately from Studio results. Setup is done when the approved foundation is integrated, dependencies and startup have clear owners, and applicable checks pass. Name required checks you couldn't run. Material deviations from the reviewed setup go back for review.
