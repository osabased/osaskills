# Roblox structure preference resolution

Use this reference only when:

- the user explicitly asks to choose structural preferences; or
- structural bootstrap, applicable project-profile evidence, and existing project conventions leave a material organization decision unresolved and that decision affects the current task.

Resolve only choices that are genuinely open and material. A clear established project should produce zero preference questions.

Read [`practices.md`](practices.md) when technical definitions, diagrams, use cases, constraints, or naming defaults are needed. Applicable project-profile evidence should already be applied before entering this reference. If reusable project-level persistence is requested, `project-profile.md` owns normalization, preview, and the authorized write after the open choices are resolved. Resolve preferences without expanding modification authority.

## Decision contract

1. Start from the structural bootstrap and current task. Reuse its evidence instead of re-inspecting the whole project.
2. Separate **detected convention** from **recommended default**:
   - A detected convention is supported by concrete project evidence and should be preserved in ordinary established-project work.
   - A recommended default is an agent choice used only when the project, applicable profile, and current request do not resolve a material decision.
3. For an established project, fit into coherent existing conventions rather than normalizing toward skill defaults unless migration or redesign is requested.
4. Resolve only choices that are genuinely open and material to the current task or explicit preference request.
5. If the current request, coherent established conventions, or an applicable project profile already resolve every material choice, ask **zero preference questions** and continue the requested task.
6. When a choice remains open, recommend the smallest compatible option first. Ask the user only when the decision is material and cannot be selected safely from the task, project constraints, profile, or skill defaults.
7. Batch independent unresolved choices into one compact prompt when answers do not depend on each other. Serialize only dependent choices or clarification follow-ups. Stop as soon as every material choice is directly implementable.
8. Accept `use recommended`, `preserve detected`, `customize`, a named option, or a natural-language preference. `use recommended` accepts recommendations for unresolved choices only. `preserve detected` keeps coherent detected conventions and leaves only genuinely open choices to resolve.
9. Use diagrams or representative trees only when they materially clarify an unresolved entrypoint or module-organization decision, or when the user asks for one. Use diagrams from `practices.md` rather than inventing competing architecture vocabulary.
10. Preference resolution must produce a directly implementable agent decision. Record enough specificity to guide placement and organization, but do not encode transient repository observations as preferences.
11. Project-level persistence is optional and must be explicitly requested. Treat applicable profile evidence as caller-provided context; send resolved durable choices to `project-profile.md` only when persistence is requested.

## Decision catalogue

Use this catalogue only for choices that remain open. Do not mechanically resolve every field.

### Source of truth

Options and meanings come from `practices.md`:

- Preserve the detected supported workflow
- Studio-native
- Script Sync
- Rojo

For an established project, preserve the detected supported workflow unless migration or redesign is requested. For greenfield work with no stronger requirement, default to Studio-native. If the user wants external editing, Git, CI, packages, or reproducible filesystem builds, recommend the smallest workflow that actually satisfies those requirements rather than defaulting from tool familiarity alone.

When a detected workflow will be persisted, normalize it to the concrete workflow (`Studio-native`, `Script Sync`, or `Rojo`) rather than the phrase `Preserve detected workflow`.

### Entrypoints

- Single client/server entrypoint pair (SSA; greenfield default)
- Multiple entrypoints
- Preserve established entrypoints
- Custom entrypoints

Preserve coherent established startup topology. For greenfield work, recommend a single client/server entrypoint pair unless object lifetime, `Actor` parallelism, character/tool behavior, isolation, or another concrete runtime requirement makes multiple entrypoints the simpler fit.

For **Multiple entrypoints**, use the derivation rules in `practices.md` and resolve only startup details needed to make each independently starting path unambiguous.

For **Custom entrypoints**, resolve the count, runtime owner, location, startup behavior, and runtime-specific exceptions for every entrypoint the design actually requires.

Example normalized preference: `Single client/server entrypoint pair (SSA), with ServerMain and ClientMain starting feature root modules explicitly.`

### Module organization

- Feature-first (greenfield default)
- Runtime layers
- Service/controller
- Components or ECS
- Preserve established organization
- Custom

Preserve a coherent established organization. For greenfield work, recommend feature-first grouping inside explicit runtime boundaries unless the project is small enough that shallow runtime layers are simpler or a concrete component/ECS/service-controller model better matches the domain.

For **Custom**, resolve grouping rules inside server, client, and shared boundaries, including naming and material exceptions.

Example normalized preference: `Feature-first inside separate Server, Client, and Shared boundaries.`

### Module style

- Plain Luau (greenfield default)
- Preserve an existing framework
- Named framework or custom lifecycle

Preserve an established framework or lifecycle unless migration is requested. For greenfield work, recommend plain Luau with explicit dependencies and add lifecycle phases only when ordering or readiness is observable.

For a named framework or custom lifecycle, resolve the framework name, module discovery rule, lifecycle phases, dependency ownership, and material exceptions.

Example normalized preference: `Plain Luau with explicit requires and Init/Start only where readiness ordering is observable.`

### Naming

Use the naming rules in `practices.md`. Ask only when naming is materially unresolved or the user wants a reusable convention different from detected/default behavior.

### Tests

Prefer existing checks and test placement. For a new project with no explicit test convention, use existing static/type/lint/build checks when introduced by the project and the smallest relevant Studio playtests for runtime behavior. Ask only when test placement, framework choice, or validation policy is itself a material organization decision.

## Defaults and summary

When `use recommended` is selected, keep every value already resolved by the explicit request, coherent established conventions, or applicable project profile, then accept recommendations for remaining choices. If a recommendation still needs a fallback, use:

- detected supported source-of-truth workflow, otherwise Studio-native;
- coherent established entrypoints, otherwise Single client/server entrypoint pair (SSA);
- coherent established module organization, otherwise feature-first grouping within runtime boundaries;
- coherent established module style, otherwise plain Luau;
- coherent established naming, otherwise the new-project naming defaults in `practices.md`;
- existing checks and test placement, otherwise the smallest relevant available validation.

For task-local decisions, summarize only the resolved choices that materially affect the current task, then continue without an extra approval stop unless the user requested one.

If the user explicitly requests reusable project-level conventions, pass the resolved durable choices to `project-profile.md` for normalization, preview, and authorized persistence.

Preference resolution is complete when every material open choice is directly implementable or explicitly blocked.
