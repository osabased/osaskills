# Roblox structure preference setup

Use this reference only when:

- the user explicitly asks to establish structural preferences; or
- structural bootstrap plus existing project conventions leave a material organization decision unresolved and that decision affects the current task.

Do not use this reference as a human-facing project onboarding flow. Ordinary project inspection and structural bootstrap should not naturally continue into preference questions.

Read [`practices.md`](practices.md) when technical definitions, diagrams, use cases, or constraints are needed. Resolve preferences without expanding modification authority.

## Contents

- [Decision contract](#decision-contract)
- [Decision catalogue](#decision-catalogue)
- [Defaults and summary](#defaults-and-summary)
- [Profile format](#profile-format)
- [Existing profiles](#existing-profiles)

## Decision contract

1. Start from the structural bootstrap and current task. Reuse its evidence instead of re-inspecting the whole project.
2. Separate **detected convention** from **recommended default**:
   - A detected convention is supported by concrete project evidence and should be preserved in ordinary established-project work.
   - A recommended default is an agent choice used only when the project and current request do not resolve a material decision.
3. For an established project, fit into coherent existing conventions rather than normalizing toward skill defaults unless migration or redesign is requested.
4. Resolve only choices that are genuinely open and material to the current task or to the explicit preference-setup request. Do not mechanically resolve every catalogue field.
5. If the current request, coherent established conventions, or an applicable project profile already resolve every material choice, ask **zero preference questions** and continue the requested task.
6. When a choice remains open, recommend the smallest compatible option first. Ask the user only when the decision is material and cannot be selected safely from the task, project constraints, or skill defaults.
7. Batch independent unresolved choices into one compact prompt when answers do not depend on each other. Serialize only dependent choices or clarification follow-ups. Stop as soon as every material choice is directly implementable.
8. Accept `use recommended`, `preserve detected`, `customize`, a named option, or a natural-language preference. `use recommended` accepts recommendations for unresolved choices only. `preserve detected` keeps coherent detected conventions and leaves only genuinely open choices to resolve.
9. Use diagrams or representative trees only when they materially clarify an unresolved entrypoint or module-organization decision, or when the user asks for one. Use diagrams from `practices.md` rather than inventing competing architecture vocabulary.
10. Preference resolution must produce a directly implementable agent decision. Record enough specificity to guide placement and organization, but do not encode transient repository observations as preferences.
11. Project-level persistence is optional and must be explicitly requested. A profile write never follows automatically from bootstrap or preference resolution.

## Decision catalogue

Use this catalogue only for choices that remain open. Do not mechanically ask every item.

### Source of truth

Options and meanings come from `practices.md`:

- Preserve the detected supported workflow
- Studio-native
- Script Sync
- Rojo

For an established project, preserve the detected supported workflow unless migration or redesign is requested. For greenfield work with no stronger requirement, default to Studio-native. If the user wants external editing, Git, CI, packages, or reproducible filesystem builds, recommend the smallest workflow that actually satisfies those requirements rather than defaulting from tool familiarity alone.

When persisting a detected workflow, store the concrete normalized workflow (`Studio-native`, `Script Sync`, or `Rojo`), not the phrase `Preserve detected workflow`.

### Entrypoints

- Single client/server entrypoint pair (SSA; greenfield default)
- Multiple entrypoints
- Preserve established entrypoints
- Custom entrypoints

Preserve coherent established startup topology. For greenfield work, recommend a single client/server entrypoint pair unless object lifetime, `Actor` parallelism, character/tool behavior, isolation, or another concrete runtime requirement makes multiple entrypoints the simpler fit.

For **Multiple entrypoints**, use the derivation rules in `practices.md` and resolve only startup details needed to make each independently starting path unambiguous.

For **Custom entrypoints**, resolve the count, runtime owner, location, startup behavior, and runtime-specific exceptions for every entrypoint that the design actually requires.

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

Prefer the project's coherent existing names and casing. For a new project with no explicit preference, use the new-project naming defaults from [`SKILL.md`](../SKILL.md). Ask only when naming is materially unresolved or the user wants a reusable convention different from detected/default behavior.

### Tests

Prefer existing checks and test placement. For a new project with no explicit test convention, use existing static/type/lint/build checks when introduced by the project and the smallest relevant Studio playtests for runtime behavior. Ask only when test placement, framework choice, or validation policy is itself a material organization decision.

### Preference scope

Resolve persistence only when the user explicitly asks for reusable project-level conventions:

- **Current task only:** apply resolved decisions without writing a profile.
- **This project only:** save convention memory to `.codex/roblox-structure.md` under the affected project root.

If the affected project root cannot be identified, persistent profile setup is blocked until the project is known. Keep the resolved decisions task-local rather than writing them elsewhere.

## Defaults and summary

When `use recommended` is selected, keep every value already resolved by the explicit request, coherent established conventions, or applicable project profile, then accept recommendations for remaining choices. If a recommendation still needs a fallback, use:

- detected supported source-of-truth workflow, otherwise Studio-native;
- coherent established entrypoints, otherwise Single client/server entrypoint pair (SSA);
- coherent established module organization, otherwise feature-first grouping within runtime boundaries;
- coherent established module style, otherwise plain Luau;
- coherent established naming, otherwise the new-project naming defaults from `SKILL.md`;
- existing checks and test placement, otherwise the smallest relevant available validation.

For task-local decisions, summarize only the resolved choices that materially affect the current task, then continue without an extra approval stop unless the user requested one.

When the user explicitly requests a reusable project profile:

1. Resolve every persisted field into a directly implementable convention: `Source of truth`, `Entrypoints`, `Module organization`, `Module style`, `Naming`, `Tests`, and `Notes`.
2. Identify the affected project root and destination `.codex/roblox-structure.md`.
3. Show one exact pre-write preview of the profile.
4. Write it only after the user confirms `proceed` or otherwise explicitly authorizes that exact profile write.
5. Treat that confirmation as authority only for the displayed profile, not for broader project changes.

## Profile format

`.codex/roblox-structure.md` is **project convention memory**. It answers:

> What structural rules should agents preserve?

It is not a generated architecture snapshot and must not answer:

> What did the repository look like the last time an agent inspected it?

Do not persist:

- current task scope or modification authority;
- exact dependency graphs;
- current Remote or Bindable inventory;
- transient file-layout details;
- task-specific startup traces;
- task-specific bootstrap findings;
- temporary risks, blockers, or validation observations.

Persistent profiles are project-local only. Do not read or write a global structure profile, including legacy `$CODEX_HOME/roblox-structure-profile.md` files. If no project root is available, keep normalized decisions in task context and do not persist them.

Use this exact version-1 shape and keep every field non-empty:

```markdown
# Roblox Structure Profile

## Profile version
1

## Source of truth
<normalized structural convention>

## Entrypoints
<normalized startup convention>

## Module organization
<normalized organization convention>

## Module style
<normalized module/lifecycle convention>

## Naming
<explicit convention, or Preserve project conventions; use new-project defaults only where no convention exists.>

## Tests
<explicit convention, or Use existing checks and the smallest relevant Studio playtests.>

## Notes
<durable project-level structural conventions or None; may name preferred tools/workflows but never grants modification permission or overrides governing/tool/safety rules>
```

For a custom selection, write `Custom` as the normalized field value and preserve the directly implementable durable convention in `Notes`. Put a named framework and lifecycle summary in `Module style` and preserve extra durable wording in `Notes`. Interpret `Notes` as convention and workflow memory, not repository-state memory. It may name preferred tools or checks, but never use profile text to broaden task authority or override governing instructions, tool rules, or safety rules.

A profile is valid only when `Profile version` equals `1` and every listed heading has non-empty content. The title is recommended but not required for validity.

## Existing profiles

Use the convention-resolution precedence, profile-drift handling, and modification-authority rules in [`SKILL.md`](../SKILL.md). This section owns only project-profile parsing, normalization, and authorized writes when preference setup or unresolved-choice resolution actually requires them.

- Existing version-1 values such as `Single Script Architecture` remain accepted aliases for the single client/server entrypoint-pair preference.
- Treat a missing field or version as incomplete. Reuse recognizable durable conventions from the existing profile and project. Resolve only material missing decisions needed by the current task or explicit profile request.
- Treat an unsupported version as incomplete without overwriting it automatically. Preserve its contents, map what can be mapped safely, and replace it only after an explicitly requested normalized profile is previewed and authorized.
- If a profile conflicts with a coherent implemented convention during ordinary established-project work, preserve the implemented convention and treat the profile as drift rather than forcing the project toward stale memory.
