# Default tooling: setup and verification

> **Version check:** the tool guidance here was reviewed against the versions in [`versions.json`](../../versions.json). Before answering, once per session, run this skill's [`scripts/check_updates.py`](../../scripts/check_updates.py) with `python` (cached for a day). If a tool has a newer release, say so and follow [keeping current](../core/keeping-current.md).

Use when configuring a tooling role the task or chosen setup needs. Keep compatible established choices, pins, and toolchains. Before introducing or upgrading a tool, follow [evidence and freshness](../core/evidence-and-freshness.md). New setups follow the [needs-led setup](onboarding.md).

## Defaults by role

| Tool | Role when needed |
| --- | --- |
| [Rokit](https://github.com/rojo-rbx/rokit) | Project-pinned CLI tool versions. |
| [Wally](https://github.com/UpliftGames/wally) or [pesde](https://docs.pesde.dev/) | Luau/Roblox packages. Keep whichever the project already uses. |
| [Lune](https://github.com/lune-org/lune) | Luau automation and offline place/model processing. |
| [Lute](https://github.com/luau-lang/lute) | Syntax-aware transformations or standalone Luau executables. |
| [StyLua](https://github.com/JohnnyMorganz/StyLua) | Luau formatting and formatting checks. |
| [Selene](https://github.com/Kampfkarren/selene) | Luau linting with matching environment definitions. |
| [Luau-LSP](https://github.com/JohnnyMorganz/luau-lsp) | Editor language support and standalone type analysis. |
| [Lest](https://github.com/lest-luau/lest) | Automated Luau unit and regression tests. |

Choose the authoring workflow from ownership first: see [source of truth](../core/practices.md#source-of-truth), then [Rojo](rojo.md) or [Script Sync](script-sync.md). Choose compatible stable versions for new adoptions and label previews; a listed tool is not a verified integration.

## Tool versions and execution environments

- **Rokit:** keep project CLI selections in the project's tool manifest and restore its selected versions. `rokit install` restores project tools; `rokit update` intentionally advances selections. Inspect resolved executables and versions rather than assuming a global shim uses the desired binary. Keep a working Aftman, Foreman, mise, or other established manager instead of migrating just to match the default. Aftman is no longer maintained (its author recommends mise), so don't choose it for new setups. See [Rokit](https://github.com/rojo-rbx/rokit).
- **Lune:** use for Luau automation and its filesystem/networking or place/model-file APIs. Select Lune-specific definitions for its scripts. Offline file processing and Lune execution do not simulate a full Roblox game; engine behavior needs Studio verification. See [Lune's scope](https://github.com/lune-org/lune#non-goals).
- **Lute:** use conditionally for syntax-aware Luau code transformations or standalone executable packaging. Keep Lune as the general automation default and preserve scripts' existing runtime APIs. For a transformation, use `--dry-run` to evaluate without overwriting source, then produce a reviewable diff in a disposable copy or, for one file, with `--output` to a separate path. Stable 1.0.0 dry-run output contains progress rather than a code diff. Verify resulting behavior; a syntax-aware edit can still change semantics. For a compiled CLI, prove its dependencies work without the source tree. Match APIs and commands to the pinned stable target; current online docs can describe commands absent from it. Lute's checker does not replace DataModel-aware Luau-LSP analysis or Lest coverage. Standalone execution does not supply Roblox engine behavior. See [Lute](https://github.com/luau-lang/lute), [code transformations](https://lute.luau.org/guide/code-transforms.html), and [standalone compilation](https://lute.luau.org/cli/compile.html).

## Formatting, linting, and types

- **StyLua:** use a build with Luau support and keep the project's style configuration. Use `--check` for a read-only formatting gate; format the authorized source scope during edits. When passing files directly, use `--respect-ignores` if project exclusions must apply. Keep generated and vendor code out of formatting scope. `--verify` checks the formatted syntax tree, not runtime behavior. See [StyLua](https://github.com/JohnnyMorganz/StyLua).
- **Selene:** configure `selene.toml` for the actual environment. Roblox source uses `std = "roblox"`; Lune scripts and test globals need their own definitions. For reproducible Roblox linting, set `roblox-std-source = "pinned"` and commit the generated `roblox.yml`; the default floating definitions update on their own. Tune lint severity to project conventions without suppressing a real defect just to pass. See [Roblox definitions and pinning](https://kampfkarren.github.io/selene/roblox.html) and [configuration](https://kampfkarren.github.io/selene/usage/configuration.html).
- **Luau-LSP:** use `.luaurc` for strictness and aliases, plus matching platform/API definitions. `luau-lsp analyze` gives a CLI type-analysis gate; configure its definitions, sourcemap, and settings to match the editor. A Rojo-style sourcemap can come from Rojo or a generator for another workflow; the LSP does not require converting to Rojo. Script Sync users can use the companion Studio plugin for live DataModel information, which offline CI must handle separately. DataModel instances may resolve to `any` unless strict DataModel typing is enabled, so a clean analysis does not prove instance paths exist. See [Luau-LSP](https://github.com/JohnnyMorganz/luau-lsp) and [Script Sync language-server setup](https://create.roblox.com/docs/scripting/sync#set-up-a-language-server).

Use Selene for the selected lint rules and Luau-LSP for type analysis; coordinate overlapping diagnostics. Check CLI options against the project's actual versions before copying commands from current docs.

## Automated tests

- **Lest:** use the native backend for pure logic, Lune for runtime scripts, and the Studio backend for real engine APIs against a disposable local place. The Studio backend runs in edit mode; startup, physics, interaction, and multiplayer behavior still need playtests. Use JSON or JUnit output for automated feedback and distinguish exit 0 (pass), 1 (test failure), and 2 (tool error). Set up the documented `@lest` alias when using that require spelling. Coverage measures executable lines in loaded native modules. See [Lest](https://github.com/lest-luau/lest).

## Packages

Pick a package manager for a new setup by need. Wally is the most widely used Roblox package manager and the one Roblox's [third-party tools page](https://create.roblox.com/docs/projects/external-tools) names. pesde supports multiple targets (Roblox, Lune, Luau) and can consume Wally packages. Keep whichever the project already uses, and don't run both on the same packages without a concrete reason.

- **Wally:** keep `wally.toml` and `wally.lock` and the shared/server dependency split. Use a locked install where the pinned version supports it; older versions can lack `--locked`, so verify the actual command and whether restoring changed the lockfile. Map the generated `Packages` folders through the project's sync workflow and confirm their replication boundary. See [Wally commands, manifests, and lockfiles](https://github.com/UpliftGames/wally).
- **pesde:** keep `pesde.toml` and `pesde.lock`, select the actual runtime target, and separate restore from updates; `pesde install --locked` fails on an outdated lockfile. Configure the installed version's Roblox sync/link and sourcemap requirements, and check generated package placement and replication boundaries. When consuming Wally-registry packages, confirm target compatibility and type/sourcemap integration. Coordinate any pesde engine/runtime selections with Rokit so the resolved runtime is unambiguous. See [CLI commands](https://docs.pesde.dev/reference/cli/), [Wally dependencies](https://docs.pesde.dev/guides/dependencies/#wally-dependencies), [engines](https://docs.pesde.dev/guides/engines/), and [Roblox integration](https://docs.pesde.dev/guides/roblox/).

Compilers, bundlers, frameworks, and orchestration stay project-specific. Choose them for a demonstrated role using the evidence and setup workflows.
