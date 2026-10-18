# Unfamiliar stacks

Use when a project relies on a sync workflow, compiler, package manager, loader, framework or test runner these references don't describe, or describe at a version other than the project's pin. Roblox tooling and practice change faster than this skill, so the tools named elsewhere are examples of a role, not requirements. This method works for whatever fills the role.

## Work out its contract

Answer from the project first (manifests, lockfiles, config, entry files, generated output, CI), then from the tool's canonical docs, source and release notes for the pinned version ([keeping current](keeping-current.md#claims-about-current-tools-and-platform)). Answer only the rows the task touches.

| Row | Establish | It decides |
| --- | --- | --- |
| Role | Which role it fills: sync, compiler, packages, loader or framework, codegen, formatter, linter, type checker, test runner. One tool can fill several | Which check step and which reference it stands in for |
| Mapping | How authored files become instances: paths, class and `RunContext` rules, generated or vendored output, what Studio still owns | Where code actually runs; the [facts models get wrong](../SKILL.md#facts-models-get-wrong) apply to the result, not the source |
| Startup | Entrypoints, the discovery rule (what counts as a unit, at what depth, what hides one), lifecycle phases and their order, what one unit's failure does to the rest | Where a new feature goes and what a move or rename breaks |
| Boundaries | Its client/server split, how it declares or generates Remotes, what it replicates | Whether authority stays on the server |
| Restore | The committed manifest and lockfile that install it and its dependencies at a fixed version | The check's restore step and fresh checkouts |
| Check | Its command, exit codes and machine-readable output; what a pass proves and what it can't | Which check step and [verification](verification.md) rung it fills |
| Release | Dev-only content it produces and how that is kept out of a published place | The dev/release boundary |

Don't infer behavior from a name or from resemblance to a tool described here: a loader that looks like ModuleLoader still has its own discovery rule, and a compiler's file suffixes may not mean what Rojo's do. When a row has no answer from evidence, name the gap and what would settle it, such as a probe build of one file or a disposable module that logs whether discovery reached it in a play-test.

## Record and apply it

Write the contract into the project guide with each claim's source, version and date ([what to write](project-guide.md#what-to-write)), and make the feature guide's layer table follow the tool's discovery rule. Then use it where the rest of this skill would use a described tool:

- **Placement:** judge containers and entrypoints by the built DataModel, not the source tree.
- **Checks:** put the tool in its role's step of the [check command](checks.md#one-check-command). A tool that fills several roles, such as a compiler that also type-checks, runs once; don't add a second tool for a role it already covers.
- **Guards:** a discovery or mapping rule whose break is silent, such as a helper at a depth where the loader starts it, is a [guard](checks.md#guards) candidate, pinned to the version it was reviewed against.
- **Migration:** add the tool's mapping and discovery rows to [what a move can break](migration.md#trace-what-a-move-can-break).

## Keep it current

The project's pin decides. When the project upgrades the tool, recheck the rows its release notes touch. If this skill's guidance about a tool proves wrong for the project's version, follow the project's evidence, say so, and propose a skill correction ([keeping this skill current](keeping-current.md#keeping-this-skill-current)).
