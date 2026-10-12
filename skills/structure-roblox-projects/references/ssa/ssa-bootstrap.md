# ModuleLoader 4.0.0 SSA compatibility

> **Version check:** before answering, once per session, run this skill's [`scripts/check_updates.py`](../../scripts/check_updates.py) with `python` (cached for a day). A newer ModuleLoader release means this contract needs the [upgrade review](#migration-and-upgrade) through [keeping current](../core/keeping-current.md); existing SSA projects keep their pin.

Use this contract to create canonical Single Script Architecture (SSA), explicitly migrate a project to it, or change its loader, entrypoints, discovery, configuration, acquisition, or upgrade behavior. Read [`ssa.md`](ssa.md) for the feature contract that the infrastructure must expose.

This reference is a fixed-target compatibility contract for projects that deliberately adopted the target below. It is not a greenfield default or a claim about the current recommended release. Research new startup choices through the setup/evidence workflow; preserve an existing project target unless a reviewed change selects another.

Preserve a coherent established startup architecture unless redesign or migration is explicit.

## Loader identity and acquisition

Canonical SSA pins:

| Field | Value |
| --- | --- |
| Repository | [`ActualFire-Games/module-loader`](https://github.com/ActualFire-Games/module-loader) |
| Wally package | `crusherfire/module-loader` |
| Version | `4.0.0` |
| Commit | `1f7e2db67b7922b98f6d3bf9b14e32185ebed2a8` |
| License | MIT |
| `ModuleLoader.rbxm` SHA-256 | `f8b0de4fe3754158b73c4cd783a6f6cb76bc1b92ee461e2216bf0db3907359e7` |

In an SSA project the loader is part of the architecture, not an ordinary library choice. Its identity, pin, acquisition form and placement change only through the [migration and upgrade](#migration-and-upgrade) steps below, never as a side effect of a dependency refresh.

When the project already uses or deliberately selects Wally, declare `ModuleLoader = "crusherfire/module-loader@4.0.0"` and map the resulting package alias to `ReplicatedStorage/Packages/ModuleLoader`. Otherwise acquire the exact [`v4.0.0` `ModuleLoader.rbxm` release asset](https://github.com/ActualFire-Games/module-loader/releases/tag/v4.0.0).

Download the exact release asset or Wally version and check the SHA-256 above. The [`roblox-resource-acquisition`](../../../roblox-resource-acquisition/SKILL.md) skill, when installed, can do this with the pin above as a fixed target. Verification may block the target, but it does not authorize a substitute or upgrade. If the target cannot be acquired or verified well enough, report the block here. Preserve the MIT notice when copying or vendoring the source or a substantial portion of it.

For existing projects, keep any exact `Structural dependencies` target recorded in the project guide or a legacy `AGENT_DIR/roblox/structure.md` profile ([agent directory](../conventions/project-guide.md#agent-directory)), at its stated scope. For a newly selected target, keep identity, version, and acquisition in the project's manifests, and explain placement, lifecycle, and upgrade ownership in the project guide by reference. Save guide changes through the [project guide](../conventions/project-guide.md#save-it) workflow.

## Resulting DataModel

Studio, Script Sync, and Rojo may use different source representations, but they must produce this DataModel:

```text
ReplicatedStorage/
  Packages/
    ModuleLoader
  ClientMain                 Script, RunContext = Client
  Client/
    <Feature>                lifecycle root ModuleScript
  Shared/
    <Feature>/               shared code/data when needed
  Remotes/
    <Feature>/               structurally owned communication instances

ServerScriptService/
  ServerMain                 Script, RunContext = Server
  Server/
    <Feature>                lifecycle root ModuleScript

ServerStorage/
  Assets/
```

Not every feature needs a root or subtree in every boundary. Use [`script-sync.md`](../workflows/script-sync.md) or [`rojo.md`](../workflows/rojo.md) for the active source-of-truth mechanics while preserving these resulting locations and instance types.

## Direct bootstrap

Keep both entrypoints limited to a direct upstream loader call. Add no wrapper or feature registry.

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

Both entrypoints must require the same replicated ModuleLoader instance. In v4.0.0 the client-side require waits for the server-created `LoadedEvent` and `RelocationRepairEvent` children, so the server bootstrap must require that loader instance for client startup to proceed. Outside a running game (command bar, plugins, specs, UI Labs stories), requiring the loader creates, connects and waits on nothing, so modules that require it can load there.

Adapt only lookup syntax required by the active source-of-truth representation. Preserve the resulting locations and direct `ModuleLoader.Start(...)` calls.

## Baseline configuration

Keep the effective loader-wide baseline at:

- `ClientWaitForServer = false`; and
- ordinary default loading with no parallel loading, CollectionService discovery, relocation, custom predicate, or custom start.

Discovery: `Start(Server)` or `Start(Client)` loads every ModuleScript whose path back to that root is only Folders, at any depth. A ModuleScript nested under another ModuleScript belongs to that module and is never loaded on its own. The lifecycle roots are therefore the ModuleScripts under `Server/` and `Client/` that no other ModuleScript contains; a plain Folder does not hide the modules inside it. `IgnoreLoader`, set on a module or cascading from a Folder, keeps a module from being required. A concrete loader-wide requirement may open an infrastructure/design decision; feature code does not change these settings locally.

`VerboseLoading` is on by default. It logs each phase, then a timing line after `=== LOADING FINISHED ===`. Keep it on unless the project turns it off deliberately; the phase banners help startup validation. Loader warnings start with `[S]` or `[C]`.

Cross-runtime readiness belongs to each feature protocol. `ClientWaitForServer` remains off, so client startup does not wait for the server's full load/Init/Start completion. The client still waits for the server's relocation manifest and checks the relocated tree right before discovery; that bootstrap gate is separate from feature readiness.

## Failure semantics

Version 4.0.0 catches require, Init, and Start errors, emits warnings, and continues with other modules before setting loaded state. A module that fails to require gets no Init or Start. A module whose Init errors gets no Start: the loader logs `>> Skipping :Start() for module <Name> because its :Init() failed`. A lifecycle callback that never returns is different: the current phase waits for it, so startup cannot complete merely by emitting slow-callback warnings. In particular:

- `ServerLoaded` or client-loaded state does not prove that every lifecycle method succeeded;
- a module found through overlapping containers runs Init and Start once; and
- startup validation must inspect attributable loader warnings and direct feature behavior.

An Init or Start that a module only inherits through its metatable is skipped when another loaded module defines it (for example, a Client service inheriting its Shared service's Init). The defining module runs it once, with itself as `self`.

Treat a loader load, Init, or Start warning attributable to changed work as a validation failure even when loaded state is set.

## Migration and upgrade

For an explicit migration, follow [`migration.md`](../workflows/migration.md) and account for every old entrypoint and registration path, duplicate-start risk, the resulting source-of-truth mapping, and a recovery boundary. Remove or redirect old startup only inside the authorized migration write set.

Changing the ModuleLoader identity, version/commit, acquisition form, or placement is an SSA infrastructure change; a resource refresh does not advance it. Before changing the pin, re-verify the target release's API, discovery defaults, lifecycle ordering and failure behavior, release integrity, license, and project-specific configuration. Change the applicable project compatibility contract only after the new target preserves or deliberately revises each affected public rule in [`ssa.md`](ssa.md), and propose the affected project-guide changes before saving them. A project-specific upgrade does not automatically rewrite this shared fixed-target reference.

### From 3.0.4 to 4.0.0

Existing SSA projects keep 3.0.4 until someone decides to upgrade. Version 3.0.4 differs from this contract in four ways:

- It loads only the direct children of `Server/` and `Client/` (`FolderSearchDepth = 1`).
- It still attempts Start after a failed Init.
- Verbose loading is off by default.
- A client require in edit mode can wait.

To upgrade a project:

1. **Find helpers that will start loading.** Find every ModuleScript under `Server/` and `Client/` that sits below a plain Folder; in Rojo, that's a directory without `init.luau`. Version 4.0.0 loads each of these as a lifecycle root. Move each helper under its owning lifecycle-root ModuleScript or into `Shared/`, or mark it `IgnoreLoader` when it must stay where it is.
2. **Remove the depth setting.** Delete any `FolderSearchDepth` attribute or `FOLDER_SEARCH_DEPTH` setting; 4.0.0 no longer reads them.
3. **Check failing Inits.** Find modules whose Init can fail but whose Start was relied on anyway; Start is now skipped.
4. **Check inherited lifecycle methods.** Find services that inherit Init or Start through a metatable; the inherited method now runs once, on the defining module.
5. **Decide on logging.** Choose whether to keep verbose loading on, and update any log filters for the `[S]`/`[C]` prefix.
6. **Swap the pin and validate.** Replace the asset or Wally pin, check the SHA-256 above, and rerun the [validation](#validation) below in Studio.

## Validation

For creation or bootstrap changes, verify:

- the effective DataModel and instance `RunContext` values;
- the direct server and client startup calls, including both requiring the same replicated ModuleLoader instance;
- the exact loader identity/pin, selected acquisition form, package/asset location, and disabled global wait;
- that no helper ModuleScript under `Server/` or `Client/` sits below only Folders, since each would load as a lifecycle root;
- one representative lifecycle root per affected runtime;
- the full load → Init → Start phase barrier; and
- warning inspection plus direct feature behavior rather than loaded-state attributes alone.

Use an in-scope feature root for the lifecycle check when one exists. Otherwise use an isolated disposable probe and remove it from the delivered project after validation.

Use the active source-of-truth reference for build or mapping checks. Run a relevant Studio server/client startup when runtime execution evidence is available. Report an unavailable Studio check as unavailable rather than passed.

Infrastructure work is complete when a fresh feature agent can use [`ssa.md`](ssa.md) without selecting a loader, editing an entrypoint, registering a feature, configuring discovery, or reconstructing startup.

## Pinned evidence

- [`src/init.luau` at the pinned commit](https://github.com/ActualFire-Games/module-loader/blob/1f7e2db67b7922b98f6d3bf9b14e32185ebed2a8/src/init.luau): discovery defaults, startup phases, failure handling, and loaded state.
- [`wally.toml` at the pinned commit](https://github.com/ActualFire-Games/module-loader/blob/1f7e2db67b7922b98f6d3bf9b14e32185ebed2a8/wally.toml): package identity, version, realm, and license.
- [`v4.0.0` release](https://github.com/ActualFire-Games/module-loader/releases/tag/v4.0.0): release notes, asset and digest.
- Roblox Creator Hub: [script types and locations](https://create.roblox.com/docs/scripting/locations), [ModuleScripts](https://create.roblox.com/docs/scripting/module), and [client-server runtime](https://create.roblox.com/docs/projects/client-server).
