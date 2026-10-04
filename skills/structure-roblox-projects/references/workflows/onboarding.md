# Needs-led Roblox project setup

Use for creating or setting up a new Roblox project, or deliberately choosing an established project's new foundation. Existing-project orientation uses [project orientation](project-orientation.md). A bare invocation first resolves which of these jobs is needed.

The user wants this sequence: learn their needs, research current suitable approaches, present one coherent setup for review, then implement the approved setup. An initial generic invocation is not approval to scaffold, install, sync, or save project guidance.

## Learn the needs that change the setup

Inspect supplied context and ask unanswered questions in small rounds, normally one to three independent questions. Resolve material needs before selecting a stack:

- artifact/product: experience and intended systems, multiple places, reusable package/model, plugin, prototypes, or other project type;
- authoring: Studio and external editor preferences, Luau/TypeScript or another language, ownership of code/assets, collaboration, Git/reproducible builds/CI, and existing Studio content;
- architecture and dependencies: scale, runtime/lifetime constraints, networking/state/persistence/UI/testing needs, library/framework posture, existing choices, deployment environment, and budget/maintenance constraints when relevant.

Skip answered or irrelevant subjects. Reuse explicit project choices and the applicable [default tooling](../../SKILL.md#default-tooling) rather than reopening those choices. Ask about use cases for unresolved roles; keep remaining architecture, languages, tools, and frameworks open. Reuse an explicitly provided needs brief instead of requiring another intake round.

## Research suitable approaches

Use [evidence and freshness](../core/evidence-and-freshness.md). Research workflow candidates and tool/library roles under the actual needs, current supported behavior, compatibility, and maintenance constraints. Confirm current authoritative documentation and compatible stable targets before presenting a current recommendation. Separate beta/preview options from established support.

Compare meaningful candidates for unresolved roles rather than collecting a catalogue. Plain modules and built-in tooling are valid candidates, as are frameworks or compiler pipelines when their roles fit. Apply [default tooling](../../SKILL.md#default-tooling) to the roles the setup needs, including Pesde for new package selections and the authoring choice that matches source ownership. No default Canonical SSA, ModuleLoader identity, language, framework, or orchestrator is assumed.

When credible approaches compete without a clear project-specific basis for selection, present their fit, costs, and uncertainties as options for the user to choose. Resolve those consequential choices before the final coherent setup. Do not ask the user to choose every trivial folder or configuration value; make routine choices consistent with the selected direction.

If a community resource is selected for a role, use the available resource-acquisition workflow for relevant qualification/adoption. Selection does not authorize installation; implementation follows review. Preserve existing project-owned identities and pins when setting up an established project unless the selected change includes replacing them.

## Present one coherent review proposal

Once needs and consequential options are resolved, present an implementable plan with:

- requirements/constraints served and why the selected approach fits;
- artifact/place/project roots, authoring owners, source/generated/asset boundaries, and filesystem-to-DataModel or host mapping;
- executable entrypoint path/class/context/owner, discovery/lifecycle/readiness and dependency direction;
- major feature/shared/network/asset boundaries and concrete communication ownership for planned interfaces;
- selected tools/dependencies by role, compatible targets, preparation and update/restore behavior, and source citations for material current recommendations;
- canonical local/CI checks where applicable, focused iteration checks, and separate Studio/host runtime checks;
- intended edits/installations/sync operations, any owner actions, recovery where needed, and proposed project guidance/pointer destination;
- unresolved evidence and what the user is being asked to approve.

Use [practices](../core/practices.md) for execution/placement/Remote contracts and relevant specialist references for the chosen workflow. A plugin/package/custom pipeline needs its own host/consumer contract rather than an invented game bootstrap pair.

Present the complete proposal before implementation and wait for user approval. If the request already approves a specific previously reviewed setup, act on that approval. An initial request to help set up a project starts this workflow; it does not waive the review preference. Guidance saving follows [review and persistence](../conventions/project-profile-persistence.md); include the exact guide/pointer preview if it is to be authorized in the same review.

## Implement and qualify the selected foundation

Implement the reviewed setup through this skill's Implementation route. Use the project's selected/native tools and runtime; make commands portable to the supported host/CI environment. Keep dependency restoration distinct from intentional updates and authored source distinct from compiler outputs. Add only roles justified by the selected setup.

Prove the relevant gate covers the selected source classes, mappings/host topology, startup and dependencies, development/release boundaries, and intended runtime behavior. For a new/materially changed gate, use small isolated negative probes when needed to establish that it catches meaningful errors rather than merely exits successfully. Restore the clean fixture after a probe. Ordinary feature work reuses this passing evidence while its inputs remain valid.

Run the smallest applicable checks and distinguish static/build proof from Studio/host execution. Setup is complete when the reviewed foundation works at the claimed evidence level, selected dependencies have clear roles/owners, applicable checks pass or specific unavailable checks are named, and any approved guidance save is verified. Pending documentation approval or unavailable runtime evidence must remain explicit.
