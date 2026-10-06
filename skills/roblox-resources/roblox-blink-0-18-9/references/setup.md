# Setup and restoration

Resolve the active Roblox project and its owned pin first. Reviewed pesde 0.7.4 supports this package directly; use pesde rather than introducing Wally as a separate manager. Use the installed parent's shared checker with Python 3.11+ and PyYAML.

1. Add `blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }` to `[dev_dependencies]`. Keep `[indices].default="https://github.com/pesde-pkg/index"` and a Lune engine (reviewed 0.10.5). No Studio compiler plugin is required.

Initial intentional resolution is `pesde install`; ordinary restoration is `pesde install --locked`. Do not modify package-generated wrappers or vendor source. MIT license.

Resolve dependency aliases and source locations from the active manifest, lock and mapping. The shared checker accepts `--alias`, `--package-dir`, and explicit companion directories; project wrappers and mapping behavior belong to the project's integration checks.
