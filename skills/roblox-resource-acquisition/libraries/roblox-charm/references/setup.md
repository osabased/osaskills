# Charm setup

The reviewed project installed Charm from the Wally index through pesde (reviewed 0.7.4):

```toml
[dependencies]
Charm = { wally = "littensy/charm", version = "=0.11.1" }

[wally_indices]
default = "https://github.com/UpliftGames/wally-index"
```

A plain Wally project declares `Charm = "littensy/charm@0.11.1"` in `wally.toml` and relies on `wally.lock` for the exact version.

- First install, when adding or changing the dependency: `pesde install`. Restoring an existing lock: `pesde install --locked`.
- Map `roblox_packages` with the official pesde Rojo scripts and require the generated wrapper (normally `Packages.Charm`). Check the sourcemap before choosing a require path.
- The package's `charm` ModuleScript has a `system` child that it loads with `require("@self/system")`. The reviewed Roblox host resolves this without patches. If a host fails on `@self`, confirm the mapped class and source first; don't rewrite vendor files.
- MIT licensed, with no runtime dependencies.
