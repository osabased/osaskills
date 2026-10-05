# Setup and restoration

1. Use Python 3.11+ with PyYAML for the shared read-only checker, pesde with Git dependencies (reviewed 0.7.4), a Roblox-target project and a mapped generated package root. Restore helper dependencies from the installed parent's requirements.txt with uv in the selected environment when needed. Resolve the active project and its require path. The authoritative declaration is `vide = { repo = "https://github.com/centau/vide", rev = "5ed4c01940e6bd578fb83253cfbeda0a6c05177c" }` in `[dependencies]`. Resolve with `pesde install` only for an authorized initial adoption/change; ordinary restoration is `pesde install --locked`. Keep generated packages untouched and use the official pesde Rojo mapping hook when the project owns that workflow.

GitHub release 0.4.1 is marked prerelease. At review the registry and the tag's pesde manifest still said 0.4.0; `src/lib.luau` reports 0.4.1. The Git commit and lock tree, rather than that stale manifest version, identify this target. Use Luau LSP's new solver: CLI `--flag:LuauSolverV2=true`, VS Code `"luau-lsp.fflags.enableNewSolver": true`.

Resolve dependency aliases and source locations from the active manifest, lock and mapping. The shared checker accepts `--alias`, `--package-dir`, and explicit companion directories; project wrappers and mapping behavior belong to the project's integration checks.
