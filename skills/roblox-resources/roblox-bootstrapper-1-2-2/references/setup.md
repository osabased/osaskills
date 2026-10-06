# Setup and restoration

Use a Roblox project, pesde with Git/Wally compatibility (reviewed 0.7.4), a mapped
package root and official sourcemap/mapping hooks. Use the installed parent's shared checker with Python 3.11+ and PyYAML.
1. Add `Bootstrapper = { repo = "https://github.com/LDGerrits/Bootstrapper", rev = "ff6700d32875dde5ef9e3625a159436ebd4dc3e9" }`
to `[dependencies]` only when adoption is authorized. Initial resolution is `pesde install`;
ordinary restoration is `pesde install --locked`. Its Wally-format package is supported
directly by pesde: retain a `[scripts].sourcemap_generator` hook for exported types.
Resolve the mapped ModuleScript before choosing its require path. At the reviewed pesde 0.7.4 Git/Wally layout, the generated wrapper looks for lowercase bootstrapper but upstream's Rojo root is Bootstrapper. Changing alias casing and clean restoration did not repair it. Use a project-owned import adapter that requires the actual Bootstrapper ModuleScript under the locked .pesde package namespace. Keep its path bound to the selected lock tree and verify its class/source in artifacts; do not edit generated packages or upstream source.

Resolve dependency aliases and source locations from the active manifest, lock and mapping. The shared checker accepts `--alias`, `--package-dir`, and explicit companion directories; project wrappers and mapping behavior belong to the project's integration checks.
