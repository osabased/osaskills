# Roblox organization practices

Use this reference when choosing an unresolved layout, placement, entrypoint, grouping, module-style, or source-of-truth decision, or when an architecture Review needs ordinary Roblox placement/runtime/entrypoint/source-of-truth rules to judge an existing structure. Preserve a coherent established structure instead of normalizing it toward these defaults during ordinary implementation.

Modification authority comes from [`SKILL.md`](../SKILL.md). If a proposed write crosses an unclear, shared, generated, or protected boundary, use [`modification-scope.md`](modification-scope.md).

## Source of truth

| Choice | Meaning | Good fit |
| --- | --- | --- |
| Preserve detected workflow | Keep the project's working authoring and sync boundaries. | Established projects. |
| Studio-native | Keep the DataModel, including script source, in Studio. | Projects that want one native editor and no filesystem build workflow. |
| Script Sync | Bidirectionally synchronize selected scripts/folders while Studio owns the wider DataModel. | External editing or Git without filesystem ownership of the wider hierarchy. |
| Rojo | Map filesystem content into the DataModel through project files. | Filesystem-first projects needing reproducible builds, CI, packages, sourcemaps, or broader mapping. |

Treat Script Sync as a bidirectional boundary with explicit conflict resolution; neither physical representation is permanently authoritative for synchronized source. Treat each Rojo-mapped filesystem tree as authoritative for the instances its effective mapping owns.

## Placement model

Use the dimensions that can change the decision:

| Dimension | Values | Question |
| --- | --- | --- |
| Runtime / consumer | Server, client, both | Which Luau environments execute or consume it? |
| Replication | Server-only, client-visible | Can clients receive and inspect it? |
| Authoring | Studio-owned, Script Sync-managed, Rojo-mapped | Which workflow owns this instance? |

A shared ModuleScript is normally both-runtime and client-visible. A server asset can be server-only without being executable. Map modification authority separately from these dimensions.

Simulation and capability boundaries are specialist cases. Follow the routing in `SKILL.md` when the affected structure uses Server Authority prediction/rollback or Script Capabilities.

## Current foundation

Treat platform-specific statements as architectural guidance rather than frozen guarantees. Re-open current official documentation when a task depends on Studio support, runtime behavior, security semantics, release status, or version-sensitive workflow behavior.

- Put server-only code in server containers, client-only code in supported client locations, and code intentionally executed or consumed on both sides in a client-visible shared container such as `ReplicatedStorage`.
- A `Script` with `RunContext = Client` can run from `ReplicatedStorage`; a `LocalScript` cannot run there.
- A ModuleScript executes independently in each Luau environment that requires it. Do not treat mutable module return state as shared across client/server or across `Actor` boundaries.
- Treat replicated code and data as visible to clients. Keep privileged authority and validation on the server.
- Keep requires acyclic and avoid restricted requires from a desynchronized parallel phase.
- Keep `ReplicatedFirst` limited to the earliest loading subset.

## Entrypoints

### Single client/server pair

Use one server bootstrap and one client bootstrap when controlled initialization or explicit dependency assembly is useful.

```text
ReplicatedStorage/
  ClientMain                 Script, RunContext = Client
  Client/                    client-only ModuleScripts
  Shared/                    genuinely shared ModuleScripts and data
  Remotes/                   shared communication instances
ServerScriptService/
  ServerMain                 Script, RunContext = Server
  Server/                    server-only ModuleScripts
ServerStorage/
  Assets/                    server-only templates and assets
ReplicatedFirst/
  LoadingClient              only when early loading behavior is required
```

This is a useful greenfield default, not a universal recommendation. Preserve a coherent established startup topology.

### Multiple entrypoints

Use independently starting scripts when object lifetime, isolation, `Actor` parallelism, character/tool behavior, or a small self-contained system makes that simpler.

```text
ServerScriptService/
  InventoryServer
  RoundServer
StarterPlayerScripts/
  CameraClient
  InputClient
Workspace/Door/
  DoorServer
```

Their execution order is nondeterministic unless the project adds an explicit coordination mechanism.

### Entrypoint rules

- Keep entrypoints focused on dependency assembly and startup.
- Require feature roots explicitly unless the project already owns a reliable discovery loader.
- Treat shared entrypoints and discovery loaders as integration boundaries.
- Add separate `Init` / `Start` phases only when ordering or cross-system readiness is observable.
- Point dependencies toward stable domain/shared modules rather than back toward entrypoints.
- Split modules by cohesive responsibility rather than arbitrary line count.

## Module grouping

### Feature-first

Use for growing projects where work is usually performed by gameplay capability.

```text
Server/Combat/
  DamageService
  HitValidation
Client/Combat/
  CombatController
Shared/Combat/
  Types
  Config
```

### Runtime layers

Use a shallow list per execution side when feature folders would add more navigation than clarity.

```text
Server/
  Combat
  Inventory
Client/
  Input
  UI
Shared/
  Constants
  Types
```

### Service/controller

Use when the project already uses this vocabulary or systems naturally form long-lived server APIs and client orchestration.

```text
Server/Services/
  InventoryService
  RoundService
Client/Controllers/
  InventoryController
  RoundController
```

### Components or ECS

Use when repeated behavior/data is naturally expressed as components processed by systems.

```text
Components/
  Health
  Damageable
Systems/
  DamageSystem
```

Architectures can combine. Prefer the smallest organization that makes runtime ownership, navigation, and dependencies clear. Preserve adjacent established groups unless migration is part of the request.

## Module style

| Choice | Meaning | Good fit |
| --- | --- | --- |
| Plain Luau | Focused ModuleScripts with explicit dependencies and lifecycle only where needed. | Greenfield work without framework requirements. |
| Preserve existing framework | Keep established discovery, naming, and lifecycle. | Working framework-based projects. |
| Named framework or custom lifecycle | Define framework/discovery/lifecycle rules deliberately. | Projects with requirements that justify team-wide lifecycle machinery. |

## Common placement

| Content | Typical home |
| --- | --- |
| Authoritative rules/state, secrets, data stores, receipts, validation | Server-only code container |
| Client input, camera, local UI behavior | Client-only code container |
| Types, constants, pure utilities used on both sides | Client-visible shared container such as `ReplicatedStorage/Shared` |
| RemoteEvents, UnreliableRemoteEvents, RemoteFunctions | Client-visible container such as `ReplicatedStorage/Remotes` |
| Server-only models and templates | `ServerStorage` |
| Assets required by both server and client before cloning | `ReplicatedStorage` |
| Earliest loading-screen subset | `ReplicatedFirst` |

These are defaults for unresolved choices and review criteria for ordinary Roblox structural compatibility, not reasons to migrate a working project without a material finding.

## Sources

- Roblox architecture: [Script types and locations](https://create.roblox.com/docs/scripting/locations), [Plant reference project](https://create.roblox.com/docs/resources/plant-reference-project), [Data model](https://create.roblox.com/docs/projects/data-model)
- Roblox modules: [ModuleScript](https://create.roblox.com/docs/reference/engine/classes/ModuleScript), [Reuse code](https://create.roblox.com/docs/scripting/module)
- Roblox runtime/security: [Client-server runtime](https://create.roblox.com/docs/projects/client-server), [Client-server boundary](https://create.roblox.com/docs/scripting/security/client-server-boundary), [Access control and confidentiality](https://create.roblox.com/docs/scripting/security/access-control)
- Roblox workflows: [Studio testing modes](https://create.roblox.com/docs/studio/testing-modes), [Third-party tools](https://create.roblox.com/docs/projects/external-tools)