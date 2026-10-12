# Vide setup

## Declare the pin

The reviewed project installed Vide with pesde (reviewed 0.7.4) as a Git dependency in `pesde.toml`:

```toml
[dependencies]
vide = { repo = "https://github.com/centau/vide", rev = "5ed4c01940e6bd578fb83253cfbeda0a6c05177c" }
```

- First install, when adding or changing the dependency: `pesde install`. Restoring an existing lock: `pesde install --locked`.
- Map `roblox_packages` with the official pesde Rojo scripts. Require Vide through the generated wrapper at the path the project's mapping produces. Don't edit generated package files.
- The commit, not a version string, identifies this target. At this commit `pesde.toml` and `wally.toml` say `0.4.0`, while `src/lib.luau` reports `version = { major = 0, minor = 4, patch = 1 }`.
- Outside Roblox (for example Lune tests), require `src/lib.luau`. `init.luau` asserts that `game` exists.

## Type checking

The typed `create` uses user-defined type functions, which need Luau's new solver:

- Luau LSP CLI: `--flag:LuauSolverV2=true`
- VS Code: `"luau-lsp.fflags.enableNewSolver": true`

Run strict analysis on your own modules. The vendor package may report internal diagnostics; report them separately and don't patch them.

## Newer code

Upstream master has unreleased commits after 0.4.1, including `UIPadding`/`UISizeConstraint` types (#92). Keep the project's pin unless the task is an upgrade.
