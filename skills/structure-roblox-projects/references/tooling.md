# Tooling

Tool facts here were reviewed against the versions in [`versions.json`](../versions.json). Use this when setting up or changing a tool role a project needs. Keep a project's working tools and pins; adopting or upgrading one follows [keeping current](keeping-current.md). The [check command](checks.md#one-check-command) is where these run. The table lists one reviewed tool per role, not a required stack: another tool in a role is fine once its [contract](unfamiliar-stack.md) is worked out.

| Tool | Role |
| --- | --- |
| [Rokit](https://github.com/rojo-rbx/rokit) | Pins CLI tool versions per project |
| [Wally](https://github.com/UpliftGames/wally) or [pesde](https://docs.pesde.dev/) | Luau and Roblox packages |
| [Lune](https://github.com/lune-org/lune) | Luau scripts and offline place or model processing |
| [Lute](https://github.com/luau-lang/lute) | Syntax-aware code transforms, standalone executables |
| [StyLua](https://github.com/JohnnyMorganz/StyLua) | Formatting |
| [Selene](https://github.com/Kampfkarren/selene) | Linting |
| [luau-lsp](https://github.com/JohnnyMorganz/luau-lsp) | Editor support and CLI type analysis |
| [Lest](https://github.com/lest-luau/lest) | Tests: native, Lune and Studio backends ([verification](verification.md)) |

- **Rokit:** `rokit install` restores the manifest's versions; `rokit update` advances them on purpose. Check which binary actually runs rather than trusting a global shim. Keep a working Aftman, Foreman or mise; Aftman is unmaintained (its author recommends mise), so don't choose it for new setups.
- **Lune:** automation with filesystem, networking and place-file APIs; it doesn't simulate a Roblox game. Give its scripts Lune's own definitions.
- **Lute:** for a transform, `--dry-run` evaluates without writing; stable 1.0.0's dry run prints progress, not a diff, so write to a separate path with `--output` or work in a copy and diff it. Match commands to the pinned version; current docs can describe commands it lacks. It doesn't replace luau-lsp analysis or tests.
- **StyLua:** `--check` for the check command. When passing files directly, add `--respect-ignores` so `.styluaignore` applies. Keep generated and vendored code out of scope. `--verify` checks the syntax tree, not behavior.
- **Selene:** `std = "roblox"` in `selene.toml`; Lune scripts and test globals need their own definitions. Set `roblox-std-source = "pinned"` and commit the generated `roblox.yml`, or the definitions float. Don't suppress a real defect to pass.
- **luau-lsp:** `.luaurc` sets strictness and aliases. `luau-lsp analyze` with the sourcemap, definitions and settings the editor uses is the CLI type gate. A Rojo-style sourcemap can come from another workflow's generator. Under Script Sync, luau-lsp writes one from the companion Studio plugin's data for the editor only, so CI needs a generated one ([Script Sync checks](script-sync.md#checks)). DataModel instances can resolve to `any`, so a clean analysis doesn't prove instance paths exist.

## Packages

Keep whichever manager the project uses, and don't run both on the same packages. For a new setup: Wally is the most widely used and the one Roblox's [third-party tools page](https://create.roblox.com/docs/projects/external-tools) names; pesde supports several targets (Roblox, Lune, Luau) and can consume Wally packages.

- **Wally:** commit `wally.toml` and `wally.lock`, keep the shared/server split, and map the `Packages` folders through the sync workflow. Older versions lack `--locked`; check the command and whether restoring changed the lockfile.
- **pesde:** commit `pesde.toml` and `pesde.lock`; `pesde install --locked` fails on an outdated lockfile. Set the Roblox target and its sync and sourcemap settings. Coordinate pesde engine selections with Rokit so one runtime version resolves. Docs: [CLI](https://docs.pesde.dev/reference/cli/), [Wally dependencies](https://docs.pesde.dev/guides/dependencies/#wally-dependencies), [engines](https://docs.pesde.dev/guides/engines/), [Roblox](https://docs.pesde.dev/guides/roblox/).

Check package placement and replication: a package mapped into `ReplicatedStorage` is client-readable. Compilers, frameworks and libraries stay project choices.
