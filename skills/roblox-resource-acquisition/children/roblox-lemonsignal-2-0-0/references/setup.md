# Setup and restoration

Resolve the active Roblox project and its owned pin first. Reviewed pesde 0.7.4 supports this package directly; use pesde rather than introducing Wally as a separate manager. Use the installed parent's shared checker with Python 3.11+ and PyYAML.

1. Add `LemonSignal = { wally = "data-oriented-house/lemonsignal", version = "=2.0.0" }` to `[dependencies]`; keep `[wally_indices].default="https://github.com/UpliftGames/wally-index"`. Map roblox_packages to a shared Packages folder with official pesde/scripts_rojo mapping and sourcemap hooks. The native Wally wrapper maps to a lowercase internal ModuleScript and requires correctly; verify the actual map before using a path.

Initial intentional resolution is `pesde install`; ordinary restoration is `pesde install --locked`. Do not modify package-generated wrappers or vendor source. MIT license.

Resolve dependency aliases and source locations from the active manifest, lock and mapping. The shared checker accepts `--alias`, `--package-dir`, and explicit companion directories; project wrappers and mapping behavior belong to the project's integration checks.
