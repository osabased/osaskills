# Setup and restoration

1. Use Roblox Studio, Python 3.11+ with PyYAML for the shared read-only helper and the active project's selected plugin metadata. Restore helper dependencies from the installed parent's requirements.txt with uv in the selected environment when needed. The documented project installer requires Windows and PowerShell 7.2+; on other hosts use the verified official asset through Studio's local plugin folder. This target is the plugin release `v1.6.1`, not the utility package's unrelated version. The official asset is https://github.com/PepeElToro41/ui-labs/releases/download/v1.6.1/Plugin.rbxm with SHA256 `c785b1fc2593d633ad3dba51aeb778cee3026393574b99438fa276ad31d5283b`.

For a project with the maintained pinned installer, run `pwsh scripts/install-studio-plugins.ps1`. It caches/downloads the exact release, verifies the digest, backs up a differing managed local plugin and installs `UILabsManagedPlugin.rbxm` in Studio's local Plugins folder. On other hosts resolve Studio's local plugin folder through Studio; verify the same digest before placing the official asset. Restart/reload Studio if it has not discovered the new file. Inspect existing installations and widget names before diagnosing duplicate entries; do not delete unrelated/account-managed plugins.

Story ModuleScripts end in `.story` and must be present in the development DataModel. A plain Vide story table needs the selected Vide package but no UI Labs utility package.

Resolve dependency aliases and source locations from the active manifest, lock and mapping. The shared checker accepts `--alias`, `--package-dir`, and explicit companion directories; project wrappers and mapping behavior belong to the project's integration checks.
