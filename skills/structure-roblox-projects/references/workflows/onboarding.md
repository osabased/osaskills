# Roblox project onboarding and setup

Use this reference when `structure-roblox-projects` is explicitly invoked without concrete work, or when the user asks for guided project setup, setup customization, or a recommended project foundation.

This is interactive project onboarding. The **Agent onboarding** contract in `../conventions/project-profile.md` separately governs durable `.agents/roblox/structure.md` guidance and its `AGENTS.md` pointer.

## Establish the smallest useful context

Inspect only facts that can change the first recommendation:

- whether the project is greenfield or established;
- the active source of truth, if one exists;
- visible tool, package, mapping, test, and project-profile manifests;
- established entrypoint and module-organization conventions when present; and
- gaps that matter to the user's stated setup goal.

For an established project, preserve coherent choices and recommend only relevant gaps or deliberate customizations. For an empty workspace or a greenfield request, do not search for conventions that cannot exist. A bare invocation authorizes this focused read-only inspection, not a repository-wide review or any writes.

Context is sufficient when the response can state the detected project state, the decisions already resolved by it, and the small set of user inputs that would materially change the recommendation.

## Learn use cases before naming libraries

Ask only unanswered questions that change the setup. Lead with the detected context and concrete choices; do not ask a generic “what do you want?” question. Keep each round compact, normally one to three independent questions, and skip questions already answered or irrelevant to the project.

Resolve these subjects only when material:

1. **Product and systems:** what the experience needs now, such as gameplay services, substantial UI, shared state, client/server protocols, persistence, isolated UI stories, or unusual runtime constraints.
2. **Authoring workflow:** Studio-first, Script Sync, or filesystem-first development with Git/CI and external editors. Apply the source-of-truth guidance in `../core/practices.md` rather than selecting Rojo from familiarity alone.
3. **Dependency posture:** plain Luau and Roblox built-ins where they are sufficient, focused libraries for selected roles, or a broader framework whose ownership model the project intentionally adopts.

Ask about use cases and dependency posture before presenting library names. When the user has already supplied enough product and workflow context, proceed directly to a recommendation.

Apply a plain/no-library choice to startup and lifecycle dependencies too, unless the user limits that choice to a particular role. Use project-owned explicit startup when community runtime dependencies are excluded. When recommending Canonical SSA, disclose its community ModuleLoader dependency; plain gameplay modules do not make that whole setup dependency-free.

## Recommend one coherent setup

Separate the recommendation into:

- detected decisions to preserve;
- the recommended structural and tooling baseline;
- only the role-specific libraries justified by the use cases;
- optional or deferred choices; and
- the exact implementation and validation boundary.

For a filesystem-first project that wants external editing, Git, reproducible builds, or CI, recommend this reusable Rojo tooling baseline unless established project constraints resolve it differently:

- **Rokit** for pinned project tools;
- **Rojo** for filesystem/DataModel mapping, sourcemaps, serving, and builds;
- **Lute** for project-owned Luau orchestration and deterministic tooling scripts;
- **StyLua** for formatting;
- **Selene** for linting;
- **luau-lsp** for strict analysis using the effective Rojo mapping and package types;
- **Lest** for native tests and opt-in Studio suites when engine behavior requires them; and
- **Wally** plus a package-type generator when the selected project actually uses Wally packages.

Recommend the roles and verification contract, not a copy of another repository's scripts, profile names, pins, exclusions, or generated artifacts. Resolve current compatible versions during authorized implementation using the applicable authoritative or resource-acquisition workflow. Studio-native and Script Sync projects should receive the smallest compatible checks rather than an unnecessary Rojo stack.

For an established project, treat the baseline as a gap checklist. Preserve coherent equivalents and avoid replacing working tools merely to match the list.

An implemented baseline needs a documented preparation path and one project-owned verification command used locally and in CI. Cover the selected tools' formatting, lint, type analysis, native tests, and Rojo build checks; provide focused checks for iteration and separate engine-dependent Studio verification. Declare required runtimes and generated inputs, keep locked dependency restoration distinct from intentional updates, and report only checks actually executed. Derive checks from this project's selected stack rather than copying another project's feature assertions.

### Prove the setup's verification boundaries

When creating or materially changing that baseline, establish what the gate covers, not merely which tools it runs:

- **Owned source coverage:** account for runtime modules, tests, and development/tooling scripts using each runtime's appropriate analyzer. Discover files from their owned roots so new files enter coverage automatically. Keep generated dependencies separate; if dependency-internal diagnostics block analysis, use a supported narrowly scoped diagnostic exclusion while retaining analysis of owned files and their imports. Compiling or executing a test is not static type checking. Report any remaining uncovered source class explicitly rather than describing the setup as fully type-checked.
- **Runtime placement:** follow [Rojo topology validation](rojo.md#validate-runtime-topology) for the selected startup and sharing boundaries. A successful build alone does not establish that an entrypoint will run where intended.
- **Installed identity:** qualify the actual local and CI installation paths through the resource-acquisition workflow. Declared pins and parsed CI configuration alone do not prove that an installer honors those pins.

Use small isolated negative probes to verify these boundaries: a type error in a newly added file from each owned source class must fail its corresponding gate, and a misplaced critical entrypoint must fail topology validation. Exercise the same checks used by the canonical command, retain reproducible regressions where useful, and restore a clean passing fixture afterward. Keep probes proportional to the setup being established; ordinary feature work does not require rebuilding this qualification suite.

## Choose dependencies by role

Plain Luau or Roblox built-ins are valid recommendations when they keep the ownership model clear and satisfy the use case. Surface only candidates for roles the user actually needs. The links below are discovery starting points supplied for onboarding; they are not equally suitable, pre-vetted, or approved for adoption.

| Role | Lean option | Discovery candidates |
| --- | --- | --- |
| UI rendering | Roblox UI instances and plain Luau | [React Luau](https://github.com/Roblox/react-luau), [Fusion](https://github.com/dphfox/Fusion), [Vide](https://github.com/centau/vide) |
| UI motion and reactive animation | Roblox tween facilities or the selected UI system's own primitives | [Ripple](https://github.com/littensy/ripple), [Seam](https://github.com/MiaGobble/Seam) (reactive state and animation) |
| Domain/shared reactive state | Plain typed tables and explicit update functions | [Charm](https://github.com/littensy/charm), [Roblox signals](https://github.com/Roblox/signals) |
| In-process events | `RBXScriptSignal`, Bindables, or a small owned callback surface | [LemonSignal](https://github.com/Data-Oriented-House/LemonSignal) |
| Client/server protocols | Roblox remotes with explicit validation | [Blink](https://github.com/1Axen/blink) |
| Lifecycle cleanup | Direct disconnect/destroy for small, obvious ownership | [Janitor](https://github.com/howmanysmall/Janitor) |
| Persistent player data | A directly owned Roblox persistence layer | [Scribe](https://github.com/ericplane/Scribe) |
| Isolated UI stories | A small project-owned development harness | [UI Labs](https://github.com/PepeElToro41/ui-labs) |
| Broader ecosystems and utility collections | The selected entrypoint/module model plus only required utilities | [Nevermore](https://quenty.github.io/NevermoreEngine/), [RbxUtil](https://github.com/Sleitnick/RbxUtil) |

Evaluate a collection's selected packages individually; a utility collection is not automatically an application framework or a commitment to adopt every package. Before recommending a framework that owns architecture, compare its ownership of entrypoints, discovery/lifecycle, dependency access, services/controllers, networking, state, and cleanup with the proposed structure. Select one clear owner for each concern. Do not layer a framework over Canonical SSA when both would own startup or lifecycle; that requires an explicit alternative design or migration decision.

Canonical SSA's ModuleLoader identity, pin, acquisition form, placement, and upgrade behavior remain owned by `structure-roblox-projects` through `../ssa/ssa-bootstrap.md`. For other dependency comparison, qualification, acquisition, or verification, use [`roblox-resource-acquisition`](../../../roblox-resource-acquisition/SKILL.md) after the relevant role and intended use are known. A user request for a lightweight recommendation does not require an exhaustive external survey.

## Offer a concrete next choice

For a bare invocation, present the recommendation with a compact choice such as:

- use the recommended setup;
- customize named decisions; or
- keep the result as a design only.

State the important tradeoff beside each alternative. Once the user selects the setup, continue through the applicable Design and Implementation routes. If the user's initial request already explicitly authorizes setup implementation and the material unknowns are resolved, proceed without another confirmation.

Make the offered action explicit: “set up the recommendation” authorizes implementation when accepted, including a natural-language reply such as “use recommended.” Acceptance of a design-only proposal stays design-only. Ask follow-ups only for still-unresolved material choices, not to reconfirm an accepted setup action.

Do not create a profile schema field merely to copy native manifests. Tool identities and versions belong in tool/package manifests and configuration files. Persist only durable structural conventions through `../conventions/project-profile.md` when one of its persistence modes applies; use its existing `Tests` field only for a durable test-placement or validation convention that is not just a duplicate command or version list.

Onboarding is complete when the recommendation is specific enough to implement, every included dependency has a justified role and clear owner, framework overlaps are resolved, and authorized setup is implemented and validated through the existing routes.
