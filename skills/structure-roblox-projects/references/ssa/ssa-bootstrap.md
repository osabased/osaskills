# Canonical SSA infrastructure

Use this contract to create canonical Single Script Architecture (SSA), explicitly migrate a project to it, or change its loader, entrypoints, discovery, configuration, acquisition, or upgrade behavior. Read [`ssa.md`](ssa.md) for the feature contract that the infrastructure must expose.

Preserve a coherent established startup architecture unless redesign or migration is explicit.

## Loader identity and acquisition

Canonical SSA pins:

| Field | Value |
| --- | --- |
| Repository | [`ActualFire-Games/module-loader`](https://github.com/ActualFire-Games/module-loader) |
| Wally package | `crusherfire/module-loader` |
| Version | `3.0.4` |
| Commit | `b427a3e03fe9368a26e344b5e37f7466fe2ca878` |
| License | MIT |
| `ModuleLoader.rbxm` SHA-256 | `79ebdaa4e8291402d565e5318775c2208e554ccb36770db20be5978f15b30521` |

`structure-roblox-projects` owns this dependency as part of Canonical SSA infrastructure: its canonical identity, exact pin, acquisition form, DataModel placement, expected behavior, and upgrade/replacement decision are structural architecture. Another workflow may acquire, verify, or document this exact target, but it must not select a substitute, advance the pin, or redefine the dependency independently.

When the project already uses or deliberately selects Wally, declare `ModuleLoader = "crusherfire/module-loader@3.0.4"` and map the resulting package alias to `ReplicatedStorage/Packages/ModuleLoader`. Otherwise acquire the exact [`v3.0.4` `ModuleLoader.rbxm` release asset](https://github.com/ActualFire-Games/module-loader/releases/tag/v3.0.4).

When acquisition or integration is part of the task, invoke [`roblox-resource-acquisition`](../../../roblox-resource-acquisition/SKILL.md) in `acquire/adopt` mode with `structure-roblox-projects` as the project-use authority and the identity/pin above as a fixed positive target. Qualification and verification may block that target, but they do not authorize rediscovery, substitution, or upgrade. If the target cannot be acquired or verified sufficiently for the intended use, surface the block back to this structural workflow. Preserve the MIT notice when copying or vendoring the source or a substantial portion of it.

When Canonical SSA is durably persisted, record the exact selected acquisition form together with the identity, version, commit, and `ReplicatedStorage/Packages/ModuleLoader` placement under `Structural dependencies` in `.agents/roblox/structure.md`. That project profile is the durable project authority for the ModuleLoader target.

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

Adapt only lookup syntax required by the active source-of-truth representation. Preserve the resulting locations and direct `ModuleLoader.Start(...)` calls.

## Baseline configuration

Keep the effective loader-wide baseline at:

- `FolderSearchDepth = 1`;
- `ClientWaitForServer = false`; and
- ordinary default loading with no parallel loading, CollectionService discovery, relocation, custom predicate, or custom start.

This makes direct-child ModuleScripts under `Server/` and `Client/` the discovery surface. A concrete loader-wide requirement may open an infrastructure/design decision; feature code does not change these settings locally.

Cross-runtime readiness belongs to each feature protocol. Global client/server waiting remains off.

## Failure semantics

Version 3.0.4 catches load, Init, and Start failures, emits warnings, and continues later lifecycle work before setting loaded state. In particular:

- `ServerLoaded` or client-loaded state does not prove that every lifecycle method succeeded;
- an Init failure does not automatically prevent that module's Start attempt; and
- startup validation must inspect attributable loader warnings and direct feature behavior.

Treat a loader load, Init, or Start warning attributable to changed work as a validation failure even when loaded state is set.

## Migration and upgrade

For an explicit migration, follow [`migration.md`](../workflows/migration.md) and account for every old entrypoint and registration path, duplicate-start risk, the resulting source-of-truth mapping, and a recovery boundary. Remove or redirect old startup only inside the authorized migration write set.

Changing the ModuleLoader canonical identity, version/commit, acquisition form, or placement is Canonical SSA infrastructure work owned by `structure-roblox-projects`; do not let resource refresh independently advance it. Before changing the pin, re-verify the target release's API, discovery defaults, lifecycle ordering and failure behavior, release integrity, license, and project-specific configuration. Update this contract and the affected project's `Structural dependencies` decision only after the new target preserves or deliberately revises each affected public rule in [`ssa.md`](ssa.md).

## Validation

For creation or bootstrap changes, verify:

- the effective DataModel and instance `RunContext` values;
- the direct server and client startup calls;
- the exact loader identity/pin, selected acquisition form, package/asset location, depth, and disabled global wait;
- one representative lifecycle root per affected runtime;
- the full load → Init → Start phase barrier; and
- warning inspection plus direct feature behavior rather than loaded-state attributes alone.

Use an in-scope feature root for the lifecycle check when one exists. Otherwise use an isolated disposable probe and remove it from the delivered project after validation.

Use the active source-of-truth reference for build or mapping checks. Run a relevant Studio server/client startup when runtime execution evidence is available. Report an unavailable Studio check as unavailable rather than passed.

Infrastructure work is complete when a fresh feature agent can use [`ssa.md`](ssa.md) without selecting a loader, editing an entrypoint, registering a feature, configuring discovery, or reconstructing startup.

## Pinned evidence

- [`src/init.luau` at the pinned commit](https://github.com/ActualFire-Games/module-loader/blob/b427a3e03fe9368a26e344b5e37f7466fe2ca878/src/init.luau): discovery defaults, startup phases, failure handling, and loaded state.
- [`wally.toml` at the pinned commit](https://github.com/ActualFire-Games/module-loader/blob/b427a3e03fe9368a26e344b5e37f7466fe2ca878/wally.toml): package identity, version, realm, and license.
- [`v3.0.4` release](https://github.com/ActualFire-Games/module-loader/releases/tag/v3.0.4): release asset and digest.
- Roblox Creator Hub: [script types and locations](https://create.roblox.com/docs/scripting/locations), [ModuleScripts](https://create.roblox.com/docs/scripting/module), and [client-server runtime](https://create.roblox.com/docs/projects/client-server).
