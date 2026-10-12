# UI Labs setup

## Install the plugin file

- Official asset: `https://github.com/PepeElToro41/ui-labs/releases/download/v1.6.1/Plugin.rbxm`
- SHA-256: `c785b1fc2593d633ad3dba51aeb778cee3026393574b99438fa276ad31d5283b` (963,906 bytes)

Steps:

1. Download the asset and verify its hash (`sha256sum Plugin.rbxm` or `Get-FileHash Plugin.rbxm`). Never install a file whose hash differs.
2. Put it in Studio's local Plugins folder (Studio: **Plugins > Plugins Folder**).
3. Restart Studio, or reload plugins, if the toolbar doesn't appear.

A project may have its own pinned installer (the reviewed project used `pwsh scripts/install-studio-plugins.ps1` on Windows with PowerShell 7.2+). That installer cached the release, checked the digest, backed up a differing managed copy, and installed it as `UILabsManagedPlugin.rbxm`. Prefer the project's installer when one exists.

Before diagnosing anything, list the existing UI Labs files in the Plugins folder. Don't delete plugins that are account-managed or unrelated.

## Project side

- Stories need the UI library they render (for example Vide) available in the edit DataModel. Plain Vide, generic and function stories don't need the UI Labs utility package.
- Map story folders only in development Rojo projects, so release builds exclude them.
