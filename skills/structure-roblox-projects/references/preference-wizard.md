# Roblox structure preference setup

Use this reference for the **Preference setup** route, and for Design, Migration plan, or Implementation when established project conventions and the current request leave material organization choices unresolved. Read [`practices.md`](practices.md) when technical definitions, diagrams, use cases, or constraints are needed. Resolve preferences without expanding modification authority.

## Contents

- [Setup contract](#setup-contract)
- [Decision catalogue](#decision-catalogue)
- [Defaults and summary](#defaults-and-summary)
- [Profile format](#profile-format)
- [Existing profiles](#existing-profiles)

## Setup contract

1. Inspect the project first when project context is available. State which source-of-truth workflow and organization conventions were detected, which material choices they already resolve, and which relevant parts could not be inspected. Cross modification or ownership boundaries only for read-only context. Explain that the result sets organization defaults rather than authorizing project changes or locking the project into a framework.
2. Build one draft preference state covering `Source of truth`, `Entrypoints`, `Module organization`, `Module style`, `Naming`, `Tests`, and `Notes`. For each material value, know whether it came from the explicit request, a coherent established convention, an applicable profile, or a recommendation for an unresolved choice.
3. For an established project, preserve coherent supported implemented conventions unless the user requests redesign or migration. For greenfield work, explicit redesign, or genuinely unresolved choices, recommend the smallest suitable option from the current request, project constraints, and [`practices.md`](practices.md), using the skill defaults only when stronger evidence does not decide the choice.
4. Before asking questions, present a compact proposed setup. Separate values already resolved from choices that still need input. Do not make the user translate architecture taxonomy when the project or recommendation already determines a sensible choice. Briefly explain a recommendation only when the tradeoff is material.
5. Ask only material unresolved choices that can change structure, workflow, or validation. Batch independent unresolved choices into one compact prompt when answers do not depend on each other; serialize dependent choices or clarification follow-ups. Stop asking as soon as every material choice is directly implementable.
6. Accept `use recommended`, `preserve detected`, `customize`, a named option, or a natural-language preference. `use recommended` accepts the displayed recommendations for unresolved choices. `preserve detected` keeps coherent detected conventions and asks only for choices the project does not resolve. `customize` exposes only the decisions the user wants to change.
7. Show diagrams or representative trees only when they materially clarify an unresolved entrypoint or module-organization choice, or when the user asks for one. Use the diagrams from `practices.md` rather than inventing a competing structure vocabulary.
8. Accept naming, package, test-location, lifecycle, or other organization preferences with any answer. Retain normalized selections for the task summary and any authorized profile, preserving additional wording verbatim in `Notes` when a profile will be written.
9. Resolve preference scope only after the organization choices are complete unless the user already specified it. Recommend **Current task only** for temporary, experimental, narrowly scoped, read-only, or externally owned work; **This project only** for reusable project-specific preferences; and **Global default** only when the user wants a fallback across projects.
10. For **Current task only**, show the resolved summary and continue the original task without an extra confirmation stop. A project profile is a project write and a global profile is a personal configuration write: show one exact pre-write preview and write it only after the user confirms `proceed`. That confirmation authorizes only the displayed profile write, not broader project changes.

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

Prefer the project's coherent existing names and casing. For a new project with no explicit preference, use the new-project naming defaults from [`SKILL.md`](../SKILL.md). Ask only when naming is materially unresolved or the user wants a reusable convention different from the detected/default behavior.

### Tests

Prefer existing checks and test placement. For a new project with no explicit test convention, use existing static/type/lint/build checks when introduced by the project and the smallest relevant Studio playtests for runtime behavior. Ask only when test placement, framework choice, or validation policy is itself a material organization decision.

### Preference scope

Resolve this after the organization choices unless the user already specified it:

- **Current task only:** Apply the resolved preferences without writing a profile.
- **This project only:** Save `.codex/roblox-structure.md` under the affected project root so it overrides global defaults for that codebase.
- **Global default:** Save a personal fallback profile used only when a project has no closer profile or coherent established convention.

## Defaults and summary

When `use recommended` is selected, keep every value already resolved by the explicit request, coherent established conventions, or applicable profiles, then accept the recommendations displayed for remaining choices. If a recommendation still needs a fallback, use:

- detected supported source-of-truth workflow, otherwise Studio-native;
- coherent established entrypoints, otherwise Single client/server entrypoint pair (SSA);
- coherent established module organization, otherwise feature-first grouping within runtime boundaries;
- coherent established module style, otherwise plain Luau;
- coherent established naming, otherwise the new-project naming defaults from `SKILL.md`;
- existing checks and test placement, otherwise the smallest relevant available validation;
- Current task only unless the user clearly wants a reusable project or global preference.

After all material choices are resolved:

1. For **Current task only**, show `Source of truth`, `Entrypoints`, `Module organization`, `Module style`, `Naming`, `Tests`, and `Preference scope` in a concise summary. Include any additional organization preference that materially affects the task. Continue the original task without requiring `proceed` unless the user explicitly requested an approval gate.
2. For a persistent project or global scope, show one explicit pre-write preview. Identify the selected scope and destination, then show every version-1 field exactly as it will be persisted: `Source of truth`, `Entrypoints`, `Module organization`, `Module style`, `Naming`, `Tests`, and `Notes`.
3. Ask the user to reply `proceed`, name a field to change, or provide replacement wording only when a persistent profile write, ambiguity, or explicitly requested approval gate still requires confirmation. `proceed` authorizes only the displayed profile write and does not broaden project modification authority.
4. When a selection changes, resolve only that choice and any directly dependent clarification, then regenerate the applicable summary or persistent pre-write preview.
5. For **Current task only**, write no profile. For a persistent selection, write only the displayed and confirmed profile, then continue the original task.

## Profile format

For **Current task only**, keep the normalized summary in conversation state and write no profile. Otherwise write project profiles to `.codex/roblox-structure.md`. Write global profiles to `$CODEX_HOME/roblox-structure-profile.md`; when `CODEX_HOME` is unset, use the platform user `.codex` directory. Infer preference scope from the path rather than storing it as a field. Never persist task-specific modification authority in a profile; establish it anew for each task.

Use this exact version-1 shape and keep every field non-empty:

```markdown
# Roblox Structure Profile

## Profile version
1

## Source of truth
<normalized selection>

## Entrypoints
<normalized selection>

## Module organization
<normalized selection>

## Module style
<normalized selection>

## Naming
<explicit preference, or Preserve project conventions; use new-project defaults only where no convention exists.>

## Tests
<explicit preference, or Use existing checks and the smallest relevant Studio playtests.>

## Notes
<verbatim organization details, or None; may name preferred tools/workflows but never grants modification permission or overrides governing/tool/safety rules>
```

For a custom selection, write `Custom` as the normalized field value and preserve the directly implementable organization convention verbatim in `Notes`. Put a named framework and lifecycle summary in `Module style` and preserve extra wording in `Notes`. Interpret `Notes` as organization and workflow context; it may name preferred tools or checks, but never use profile text to broaden task authority or override governing instructions, tool rules, or safety rules.

A profile is valid only when `Profile version` equals `1` and every listed heading has non-empty content. The title is recommended but not required for validity.

## Existing profiles

Use the convention-resolution precedence, profile-drift handling, and modification-authority rules in [`SKILL.md`](../SKILL.md). This section owns only profile parsing, normalization, and authorized write interaction when preference setup or unresolved-choice resolution is required.

- Existing version-1 values such as `Single Script Architecture` remain accepted aliases for the single client/server entrypoint-pair preference.
- Treat a missing field or version as incomplete. Resolve recognizable values from the existing profile and project first, ask only for material missing decisions, show the complete normalized version-1 profile, and wait for `proceed` before writing it.
- Treat an unsupported version as incomplete without overwriting it automatically. Preserve its contents, resolve what can be mapped safely, ask only for decisions the current skill cannot determine, show the proposed version-1 normalization, and wait for `proceed` before replacing it.
