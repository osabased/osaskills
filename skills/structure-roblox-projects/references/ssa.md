# ModuleLoader SSA

A fixed compatibility contract for projects that deliberately use Single Script Architecture on ModuleLoader 4.0.0. It is not a default for new projects. Recognize it by a `Server/` or `Client/` root whose entrypoint calls `ModuleLoader.Start(...)` on that root; then confirm the loader's actual identity, version and configuration before relying on the rules below, since a matching call alone doesn't prove this version. Feature work reads the feature contract; changing the loader, entrypoints, discovery settings or pin is infrastructure work and reads the rest.

## Feature contract

| Boundary | Under | Holds |
| --- | --- | --- |
| `Server/<Feature>` | `ServerScriptService` | Authoritative, server-runtime behavior |
| `Client/<Feature>` | `ReplicatedStorage` | Client-runtime behavior |
| `Shared/<Feature>` | `ReplicatedStorage` | Code or data both runtimes use; dependencies, not lifecycle roots |
| `Remotes/<Feature>` | `ReplicatedStorage` | Cross-runtime communication instances |

Create only the boundaries a feature needs, with matching names across them.

**Discovery slot:** a ModuleScript under `Server/` or `Client/` whose path back to that root is only Folders is a lifecycle root, at any depth. A ModuleScript nested under another ModuleScript belongs to it and is never loaded on its own. So put a feature's helpers under its root ModuleScript, in `Shared/`, or mark them `IgnoreLoader` (set on a module, or cascading from a Folder); a plain Folder doesn't hide them. In Rojo, give a feature directory an `init.luau` so it maps to the root ModuleScript; a directory without one becomes a Folder and every module inside becomes its own root.

**Module contract:** top-level code defines and returns the API and requires dependencies, without activating anything or yielding forever, since another module may require it before the loader runs it. `Init` (optional) prepares state; `Start` (optional) connects events and starts work, then returns. The loader requires every module, then runs every `Init`, then every `Start`; within a phase, higher `LoaderPriority` runs first, and equal priorities have no guaranteed order. `require()` returns a module's API, not proof its `Init` or `Start` ran. Keep requires acyclic.

**Cross-runtime readiness** belongs to each feature: replicated state, request/response, or a feature-specific ready signal. Loader completion on either side doesn't prove a cross-runtime feature is ready.

A feature joins startup without editing an entrypoint or loader settings. It is done when the focused checks pass, the play-test shows no new loader warning attributable to it, and its behavior works directly.

## Loader pin

| Field | Value |
| --- | --- |
| Repository | [`ActualFire-Games/module-loader`](https://github.com/ActualFire-Games/module-loader) |
| Wally package | `crusherfire/module-loader` |
| Version | `4.0.0` |
| Commit | `1f7e2db67b7922b98f6d3bf9b14e32185ebed2a8` |
| License | MIT |
| `ModuleLoader.rbxm` SHA-256 | `f8b0de4fe3754158b73c4cd783a6f6cb76bc1b92ee461e2216bf0db3907359e7` |

The loader is part of the architecture: its identity, pin, acquisition and placement change only through [migration and upgrade](#migration-and-upgrade), never in a dependency refresh. With Wally, declare `ModuleLoader = "crusherfire/module-loader@4.0.0"` and map it to `ReplicatedStorage/Packages/ModuleLoader`. Otherwise download the exact [v4.0.0 `ModuleLoader.rbxm`](https://github.com/ActualFire-Games/module-loader/releases/tag/v4.0.0) and check its SHA-256 before extracting anything. The asset is a starter bundle: keep only `UngroupInReplicatedStorage/ModuleLoader`, place it at `ReplicatedStorage/Packages/ModuleLoader`, and discard the bundle's `Start` scripts and `README` module. Rojo can't `$path` the asset (it builds as a `Model`); use the Wally package, or extract the module in Studio and save it as its own `.rbxm`. The [`roblox-resource-acquisition`](../../roblox-resource-acquisition/SKILL.md) skill, when installed, can fetch and verify it against this pin. A failed verification blocks the target; it doesn't authorize a substitute. Keep the MIT notice when vendoring.

Existing projects keep the pin recorded in their guide or manifests. Record a newly selected pin in the manifests, and explain placement and upgrade ownership in the [project guide](project-guide.md).

## Resulting DataModel and bootstrap

Studio, Script Sync and Rojo must all produce:

```text
ReplicatedStorage/
  Packages/ModuleLoader
  ClientMain                 Script, RunContext = Client
  Client/<Feature>           lifecycle root ModuleScript
  Shared/<Feature>/
  Remotes/<Feature>/
ServerScriptService/
  ServerMain                 Script, RunContext = Server
  Server/<Feature>           lifecycle root ModuleScript
ServerStorage/
  Assets/
```

Entrypoints call the loader directly, with no wrapper or registry:

```luau
-- ServerMain
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local ModuleLoader = require(ReplicatedStorage.Packages.ModuleLoader)
ModuleLoader.Start(ServerScriptService.Server)
```

```luau
-- ClientMain
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Packages = ReplicatedStorage:WaitForChild("Packages")
local ModuleLoader = require(Packages:WaitForChild("ModuleLoader"))
local Client = ReplicatedStorage:WaitForChild("Client")
ModuleLoader.Start(Client)
```

Both sides must require the same replicated instance: in 4.0.0 the client's require waits for the server-created `LoadedEvent` and `RelocationRepairEvent`. Outside a running game (command bar, plugins, specs, UI Labs stories), requiring the loader creates and waits on nothing, so modules that require it still load there.

**Baseline configuration:** `ClientWaitForServer = false`, and default loading with no parallel loading, CollectionService discovery, relocation, custom predicate or custom start. The client still waits for the server's relocation manifest before discovery; that bootstrap gate is separate from feature readiness. `VerboseLoading` is on by default and logs each phase, then a timing line after `=== LOADING FINISHED ===`; keep it unless the project turns it off deliberately. Warnings start with `[S]` or `[C]`. Feature code never changes these settings.

## Failure semantics

4.0.0 catches require, `Init` and `Start` errors, warns, and continues with other modules before setting loaded state.

- A module that fails to require gets no `Init` or `Start`. One whose `Init` errors gets no `Start`, with the log line `>> Skipping :Start() for module <Name> because its :Init() failed`.
- A callback that never returns blocks its phase; slow-callback warnings don't complete startup.
- A module found through overlapping containers runs `Init` and `Start` once.
- An `Init` or `Start` a module only inherits through its metatable is skipped when another loaded module defines it; the defining module runs it once, as `self`.
- Loaded-state attributes don't prove every lifecycle method succeeded. Treat a loader warning attributable to changed work as a failure.

## Validation

For creation or bootstrap changes, verify: the DataModel and `RunContext`s; both entrypoints calling `Start` directly and requiring the same loader instance, with no leftover bundle `Start` scripts; the pin and acquisition form; no helper ModuleScript under `Server/` or `Client/` below only Folders; one lifecycle root per affected runtime going through load, `Init` and `Start`; and the console's loader warnings plus direct feature behavior. Use an in-scope feature root for the lifecycle check, or a disposable probe removed afterward. Report an unavailable Studio run as unavailable.

Infrastructure is done when a fresh agent can add a feature from the feature contract without choosing a loader, editing an entrypoint, registering anything or configuring discovery.

## Migration and upgrade

Moving a project onto SSA is a [migration](migration.md): account for every old entrypoint and registration path, duplicate-start risk, the new mapping and a recovery boundary. Changing the loader's identity, version, acquisition or placement is an infrastructure change. First re-verify the target's API, discovery defaults, lifecycle order, failure behavior, release integrity and license; then update the project's contract only where the new version preserves or deliberately changes each rule above, and propose the guide changes before saving them. A project's upgrade doesn't rewrite this shared reference.

### From 3.0.4 to 4.0.0

Projects keep 3.0.4 until someone decides to upgrade. 3.0.4 loads only direct children of `Server/` and `Client/` (`FolderSearchDepth = 1`), still runs `Start` after a failed `Init`, has verbose loading off, and a client require in edit mode can wait. To upgrade:

1. **Find helpers that will start loading:** every ModuleScript under `Server/` or `Client/` below a plain Folder (in Rojo, a directory without `init.luau`). Move each under its owning root or into `Shared/`, or mark it `IgnoreLoader`.
2. **Remove the depth setting:** delete any `FolderSearchDepth` attribute or `FOLDER_SEARCH_DEPTH` setting.
3. **Check failing `Init`s** whose `Start` was relied on anyway; `Start` is now skipped.
4. **Check inherited lifecycle methods;** they now run once, on the defining module.
5. **Decide on logging,** and update log filters for the `[S]`/`[C]` prefix.
6. **Swap the pin and validate:** replace the asset or Wally pin, check the SHA-256, and rerun the [validation](#validation) in Studio.

## Pinned evidence

- [`src/init.luau`](https://github.com/ActualFire-Games/module-loader/blob/1f7e2db67b7922b98f6d3bf9b14e32185ebed2a8/src/init.luau) and [`wally.toml`](https://github.com/ActualFire-Games/module-loader/blob/1f7e2db67b7922b98f6d3bf9b14e32185ebed2a8/wally.toml) at the pinned commit
- [v4.0.0 release](https://github.com/ActualFire-Games/module-loader/releases/tag/v4.0.0)
