# Unfamiliar stacks

Use when a project relies on a sync workflow, compiler, package manager, loader, framework or test runner these references don't describe, or describe at a version other than the project's pin. Roblox tooling and practice change faster than this skill, so the tools named elsewhere are examples of a role, not requirements. This method works for whatever fills the role.

## Work out its contract

First use what is already recorded: the project guide, a `roblox-<tool>` skill the project has, or one the `roblox-resource-acquisition` catalog has at this pin (cloned through that skill when it is installed). List `.claude/skills/` by name before reading `node_modules`, since a glob over the project root can skip hidden folders. Work out only the rows they don't answer.

Answer from the project first (manifests, lockfiles, config, entry files, generated output, CI), then from the tool's canonical docs, source and release notes for the pinned version ([keeping current](keeping-current.md#claims-about-current-tools-and-platform)). Answer only the rows the task touches.

| Row | Establish | It decides |
| --- | --- | --- |
| Role | Which role it fills: sync, compiler, packages, loader or framework, codegen, formatter, linter, type checker, test runner. One tool can fill several | Which check step and which reference it stands in for |
| Mapping | How authored files become instances: paths, class and `RunContext` rules, generated or vendored output, what Studio still owns | Where code actually runs; the [facts models get wrong](../SKILL.md#facts-models-get-wrong) apply to the result, not the source |
| Startup | Entrypoints, the discovery rule (what counts as a unit, at what depth, what hides one), the entrypoint's scan paths or globs (anything added under them is discovered, specs and data included), lifecycle phases and their order, what one unit's failure does to the rest | Where a new feature goes and what a move or rename breaks |
| Boundaries | Its client/server split, how it declares or generates Remotes, what it replicates | Whether authority stays on the server |
| Restore | The committed manifest and lockfile that install it and its dependencies at a fixed version. Restore covers every manifest the check depends on (for example both `package.json` and `rokit.toml`); a binary missing because a manifest wasn't restored is a restore gap, not a blocked check. When a tool the manifest pins won't run, check whether its install step, such as `rokit install`, has run before naming another cause | The check's restore step and fresh checkouts |
| Check | Its command, exit codes and machine-readable output; what a pass proves and what it can't | Which check step and [verification](verification.md) rung it fills |
| Release | Dev-only content it produces and how that is kept out of a published place | The dev/release boundary |

Don't infer behavior from a name or from resemblance to a tool described here: a loader that looks like ModuleLoader still has its own discovery rule, and a compiler's file suffixes may not mean what Rojo's do. When a row has no answer from evidence, name the gap and what would settle it, such as a probe build of one file or a disposable module that logs whether discovery reached it in a play-test.

Copying a neighbouring file's pattern doesn't establish a row: it shows what one file does, not the rule behind it. For each row the task touches, quote the line from the tool's own docs, README or type declarations (for an npm package, under `node_modules/<package>`, including `out/`; search there before calling a source unavailable) that answers it. A row with no quoted line is a gap, even when existing code suggests the answer.

If restore or the check can't run, report the failing step and the pin behind it. Don't substitute another install, a global tool or an `npx` fetch of a same-named package; a result from a workaround in a scratch copy is reported as unverified.

## Record and apply it

This holds for a routine edit too. When the guide doesn't record the contract, finish the task, then propose the rows you worked out as a guide diff for review ([save it](project-guide.md#save-it)); don't write it unasked. End the report with the diff itself, one line per row:

```markdown
| Row | Claim | Source | Version | Checked | Status | To settle |
| --- | --- | --- | --- | --- | --- | --- |
| Startup | <what it discovers and when> | <file and the quoted line> | <pinned version> | <date> | read, inferred or gap | <the probe, for inferred or gap> |

Reuse: <tool and pin>; skill: <the project or catalog skill used, or none in `.claude/skills/` or the catalog>; catalog PR: <offered, or why not>
```

Status is `read` when Source quotes a line that states the claim (for Restore, the manifest line; for Check, the script body or the tool's documented exit behavior; for a row taken from a skill, the line the skill quotes), `inferred` when it names only a file, a script or existing code, or rests on an absence such as a missing key, and `gap` when nothing answers it. What the quote doesn't cover goes in To settle; it doesn't downgrade the row.

Skip the diff only when every row the task touched came from the guide or a skill; rows you worked out yourself still go in it. A report that says a proposal is owed but doesn't contain one is incomplete. End every report that used this method with the `Reuse:` line, even when no diff is owed.

When the catalog has no skill for the tool at this pin and at least one row quoted from the tool's own docs is `read`, offer in one sentence to turn them into a catalog library skill through `roblox-resource-acquisition`, so other projects on that pin don't rediscover them; rows that aren't `read` don't cancel the offer, and the offer doesn't wait on judging whether a row is general enough. Write it only when the user asks. Project facts, such as this project's mapping paths, stay in the guide.

Write the contract into the project guide with each claim's source, version and date ([what to write](project-guide.md#what-to-write)), and make the feature guide's layer table follow the tool's discovery rule. Then use it where the rest of this skill would use a described tool:

- **Placement:** judge containers and entrypoints by the built DataModel, not the source tree.
- **Checks:** put the tool in its role's step of the [check command](checks.md#one-check-command). A tool that fills several roles, such as a compiler that also type-checks, runs once; don't add a second tool for a role it already covers.
- **Guards:** a discovery or mapping rule whose break is silent, such as a helper at a depth where the loader starts it, is a [guard](checks.md#guards) candidate, pinned to the version it was reviewed against.
- **Migration:** add the tool's mapping and discovery rows to [what a move can break](migration.md#trace-what-a-move-can-break).

## Keep it current

The project's pin decides. When the project upgrades the tool, recheck the rows its release notes touch. If this skill's guidance about a tool proves wrong for the project's version, follow the project's evidence, say so, and propose a skill correction ([keeping this skill current](keeping-current.md#keeping-this-skill-current)).
