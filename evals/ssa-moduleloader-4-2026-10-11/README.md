# ModuleLoader 4.0.0 Studio probe (2026-10-11)

[PR #48](https://github.com/osabased/osaskills/pull/48) moved the SSA contract ([`ssa-bootstrap.md`](../../skills/structure-roblox-projects/references/ssa/ssa-bootstrap.md)) to ModuleLoader 4.0.0 from the source and release notes alone. This place checks those claims in a live Studio session.

## Build

```sh
python build.py --rojo <path to rojo 7.7>
```

`build.py` downloads the pinned commit `1f7e2db`, builds its ModuleLoader, and then builds `ml4-probe.rbxl`. The release `ModuleLoader.rbxm` can't be mapped directly, because it's a starter bundle (see [what this found](#what-building-it-found)). The module inside it comes from this same source.

The place uses the canonical SSA layout: `ServerMain` and `ClientMain` each call `ModuleLoader.Start`, and nothing else. Two report scripts wait for the loader's `ServerLoaded` or `ClientLoaded` attribute and then print one line per check.

| # | Claim | Probe |
|---|---|---|
| 1 | Discovery goes through plain Folders at any depth | `Server/Probes/Deep/DeepProbe` and `Client/Ui/Deep/ClientDeepProbe` should each run Init once |
| 2 | A ModuleScript nested under another ModuleScript isn't loaded on its own | `Server/Owner` runs Init; `Owner/Helper` must not |
| 3 | Start is skipped after a failed Init | `FailInit` errors in Init; its Start must not run |
| 4 | An inherited Init runs once, on the defining module | `Derived` inherits `Base.Init`; it should run once, with `self = Base` |
| 5 | `IgnoreLoader` keeps a module from being required | `Ignored` must never be required |
| 6 | Requiring the loader in edit mode does nothing | Manual command-bar check, below |

## Run in Studio

1. Open `ml4-probe.rbxl` in Studio.
2. **Edit-mode check (claim 6):** before pressing Play, paste this into the command bar:

   ```luau
   local t = os.clock(); local ML = require(game.ReplicatedStorage.Packages.ModuleLoader); print("[probe edit]", typeof(ML), string.format("%.3fs", os.clock() - t), "LoadedEvent:", game.ReplicatedStorage.Packages.ModuleLoader:FindFirstChild("LoadedEvent"))
   ```

   It should print `table`, a near-zero time and `LoadedEvent: nil` right away, without hanging.
3. **Play (F5).** In the Output window, look for `[probe server]` and `[probe client]` lines, each ending with `done: 0 failure(s)`.
4. Also expect these loader warnings:
   - verbose phase banners (`=== LOADING MODULES ===` and so on), which are on by default in 4.0.0;
   - `FailInit`'s deliberate Init error;
   - `>> Skipping :Start() for module FailInit because its :Init() failed`.

## Results

Not run yet.

## What building it found

The v4.0.0 `ModuleLoader.rbxm` release asset contains:
- `UngroupInReplicatedStorage/ModuleLoader`, the actual module;
- `UngroupInServerScriptService/Start` and `UngroupInStarterPlayerScripts/Start`, upstream's starter bootstrap scripts;
- a `README` ModuleScript.

v3.0.4's asset has the same layout. The SSA contract had said to map the asset straight to `ReplicatedStorage/Packages/ModuleLoader`. Under Rojo that gives a `Model` that can't be required, and ungrouping all of it in Studio adds a second set of entry points. The contract now says to keep only the inner module.
