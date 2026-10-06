# Default tooling: setup and verification

Use when configuring a needed tooling role. Compatible established choices take precedence; preserve existing pins and toolchains. Add only roles justified by the task or selected setup. Before a needed tool's first use, follow [evidence and freshness](../core/evidence-and-freshness.md). New setup follows the [reviewed setup workflow](onboarding.md).

## Preferred defaults by role

| Tool | Role when needed |
| --- | --- |
| [Rokit](https://github.com/rojo-rbx/rokit) | Project-pinned CLI tool versions. |
| [Pesde](https://docs.pesde.dev/) | Luau/Roblox packages; preserve an established Wally setup. |
| [Lune](https://github.com/lune-org/lune) | Luau automation and offline place/model processing. |
| [Lute](https://github.com/luau-lang/lute) | Syntax-aware transformations or standalone Luau executables. |
| [StyLua](https://github.com/JohnnyMorganz/StyLua) | Luau formatting and formatting checks. |
| [Selene](https://github.com/Kampfkarren/selene) | Luau linting with matching environment definitions. |
| [Luau-LSP](https://github.com/JohnnyMorganz/luau-lsp) | Editor language support and standalone type analysis. |
| [Lest](https://github.com/lest-luau/lest) | Automated Luau unit and regression tests. |
| [Roblox Headless Renderer](https://github.com/TabooHarmony/roblox-headless-renderer) | UI layout, text overflow, and clipping diagnostics across viewports. |

Choose authoring from ownership: [Rojo](rojo.md) for filesystem-owned mappings, [Script Sync](script-sync.md) for external code editing while Studio owns the project. Reuse the selected workflow. Choose compatible stable targets for new adoptions and identify previews explicitly; a preferred tool is not a verified integration.

## Tool versions and execution environments

- **Rokit:** keep project CLI selections in the project's tool manifest and restore its selected versions. `rokit install` restores project tools; `rokit update` intentionally advances selections. Inspect resolved executables and versions rather than assuming a global shim uses the desired binary. Preserve a working Aftman, Foreman, mise, or other established manager instead of migrating merely to match the default. See [Rokit](https://github.com/rojo-rbx/rokit).
- **Lune:** use for Luau automation and its filesystem/networking or place/model-file APIs. Select Lune-specific definitions for its scripts. Offline file processing and Lune execution do not simulate a full Roblox game; engine behavior needs Studio verification. See [Lune's scope](https://github.com/lune-org/lune#non-goals).
- **Lute:** use conditionally for syntax-aware Luau code transformations or standalone executable packaging. Keep Lune as the general automation default and preserve scripts' existing runtime APIs. For a transformation, use `--dry-run` to evaluate without overwriting source, then produce a reviewable diff in a disposable copy or, for one file, with `--output` to a separate path. Stable 1.0.0 dry-run output contains progress rather than a code diff. Verify resulting behavior; a syntax-aware edit can still change semantics. For a compiled CLI, prove its dependencies work without the source tree. Match APIs and commands to the pinned stable target; current online docs can describe commands absent from it. Lute's checker does not replace DataModel-aware Luau-LSP analysis or Lest coverage. Standalone execution does not supply Roblox engine behavior. See [Lute](https://github.com/luau-lang/lute), [code transformations](https://lute.luau.org/guide/code-transforms.html), and [standalone compilation](https://lute.luau.org/cli/compile.html).

## Formatting, linting, and types

- **StyLua:** use a build with Luau support and preserve project style configuration. Use `--check` for a read-only formatting gate; format the authorized source scope during edits. When passing files directly, use `--respect-ignores` if project exclusions must apply. Keep generated/vendor code outside formatting scope. `--verify` checks the formatted syntax tree, not runtime behavior. See [StyLua](https://github.com/JohnnyMorganz/StyLua).
- **Selene:** configure `selene.toml` for the actual environment. Roblox source uses `std = "roblox"`; Lune scripts and test-specific globals need their own matching definitions. For reproducible Roblox linting, select the documented pinned standard-library mode and retain the reviewed `roblox.yml`; floating definitions can change independently of the CLI version. Tune lint severity to project conventions without suppressing a real defect merely to pass. See [Roblox definitions and pinning](https://kampfkarren.github.io/selene/roblox.html) and [configuration](https://kampfkarren.github.io/selene/usage/configuration.html).
- **Luau-LSP:** use `.luaurc` for strictness/aliases and the matching platform/API definitions. `luau-lsp analyze` supplies a CLI type-analysis gate; configure its definitions, sourcemap, and settings consistently with the editor. A Rojo-style sourcemap can come from Rojo or a generator matching another workflow; the LSP does not require converting a project to Rojo. Script Sync users can use the companion Studio plugin for live DataModel information, which must be accounted for separately in offline CI. DataModel instances may resolve to `any` in diagnostics unless strict DataModel typing is enabled; a clean analysis is not proof that instance paths exist. See [Luau-LSP](https://github.com/JohnnyMorganz/luau-lsp) and [Script Sync language-server setup](https://create.roblox.com/docs/scripting/sync#set-up-a-language-server).

Use Selene for the selected lint rules and Luau-LSP for type analysis; coordinate overlapping diagnostics. Check CLI options against the project's actual versions before copying current documentation commands.

## Automated tests and UI diagnostics

- **Lest:** use the native backend for pure logic, Lune for runtime scripts, and the Studio backend for real engine APIs against a disposable local place. The Studio backend runs in edit mode; startup, physics, interaction, and multiplayer behavior still need playtests. Use JSON or JUnit output for automated feedback and distinguish exit 0 (pass), 1 (test failure), and 2 (tool error). Set up the documented `@lest` alias when using that require spelling. Coverage measures executable lines in loaded native modules. See [Lest](https://github.com/lest-luau/lest).
- **Roblox Headless Renderer:** export the actual UI properties and match viewport, insets, and coordinate origin to the Studio view. Inspect finding severity even when the command exits successfully; warnings can return exit 0. Confirm the final UI in Studio because font and image rendering can differ. Manage its Python environment with uv when available, following the host's Python preference. See [Roblox Headless Renderer](https://github.com/TabooHarmony/roblox-headless-renderer).

## Dependencies and authoring

- **Pesde:** prefer for new Luau/Roblox package selections when packages are needed. Preserve `pesde.toml` and `pesde.lock`, select the actual runtime target, and separate dependency restoration from updates; use `pesde install --locked` for a locked gate where the pinned version supports it. Configure the installed version's Roblox sync/link and sourcemap requirements, and verify generated package placement and replication boundaries. Pesde can consume Wally registry packages; qualify their target compatibility and type/sourcemap integration rather than assuming a second package manager is necessary. Coordinate any Pesde engine/runtime selections with Rokit so the resolved runtime is unambiguous. See [multi-target support](https://docs.pesde.dev/), [CLI commands](https://docs.pesde.dev/reference/cli/), [Wally dependencies](https://docs.pesde.dev/guides/dependencies/#wally-dependencies), [engines](https://docs.pesde.dev/guides/engines/), and [Roblox integration](https://docs.pesde.dev/guides/roblox/).
- **Wally:** preserve an established setup, or use it for a concrete compatibility need that Pesde cannot meet. Keep its manifest/lockfile and shared/server dependency boundaries. Use a locked installation mode where the pinned version supports it; older versions can lack `--locked`, so verify the actual command and whether restoration changed the lockfile. See [Wally commands, manifests, and lockfiles](https://github.com/UpliftGames/wally).
- **Rojo:** prefer for a filesystem-owned mapped project when that authoring role is selected. Follow [Rojo guidance](rojo.md) for source/generated ownership, mappings, serve/build checks, and preserving Studio-owned content.
- **Script Sync:** prefer for external script editing while Studio owns the project. Follow [Script Sync guidance](script-sync.md) for bidirectional ownership, conflicts, supported topology, and metadata limits. Coordinate sync owners for a tree rather than enabling competing systems on the same content.

Compilers, bundlers, frameworks, and orchestration remain project-specific choices. Select them for a demonstrated role using the existing evidence and setup routes.
