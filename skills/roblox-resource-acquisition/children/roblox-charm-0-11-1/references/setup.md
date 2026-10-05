# Setup and restoration

Resolve the active Roblox project and its owned pin first. Use pesde (reviewed 0.7.4), not a second package manager. Use the installed parent's shared checker with Python 3.11+ and PyYAML.

1. Add `Charm = { wally = "littensy/charm", version = "=0.11.1" }` in `[dependencies]`, with `[wally_indices].default = "https://github.com/UpliftGames/wally-index"`. Initial authorized resolution is `pesde install`; restoration is `pesde install --locked`. Map roblox_packages with the official pesde/scripts_rojo hooks. Inspect the resulting sourcemap and mapped wrapper before requiring it. The standard alias maps to `Packages.Charm`; the internal `charm` ModuleScript has a `system` child. Source uses `require("@self/system")`; the reviewed Roblox host resolves it without a vendor patch. Do not rewrite generated source or introduce a source-rewriting hook by assumption. MIT license, no runtime package dependencies.

Resolve dependency aliases and source locations from the active manifest, lock and mapping. The shared checker accepts `--alias`, `--package-dir`, and explicit companion directories; project wrappers and mapping behavior belong to the project's integration checks.
