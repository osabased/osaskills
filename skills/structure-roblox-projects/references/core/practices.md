# Roblox organization practices

Use this reference to choose an unresolved layout, placement, entrypoint, grouping, module style, or source of truth, or to judge an existing structure in a review. During ordinary implementation, keep a coherent established structure instead of normalizing it toward these defaults.

When the project uses the ModuleLoader SSA contract, [`ssa.md`](../ssa/ssa.md) owns feature placement, discovery, and lifecycle. Use this file only for choices that contract leaves open.

The game layouts below are examples. Plugins, packages/models, compiler pipelines, multi-place experiences, and custom workflows keep their own host and consumer contracts; map them with the [project guide](../conventions/project-guide.md).

## Source of truth

This is the one place this skill compares the authoring workflows. Other references link here.

| Choice | Meaning | Good fit |
| --- | --- | --- |
| Keep the detected workflow | Keep the project's working authoring and sync boundaries. | Established projects. |
| Studio-native | The DataModel, including script source, lives in Studio. | One native editor, no filesystem build. |
| Script Sync | Studio syncs `Script`, `LocalScript`, `ModuleScript`, and `Folder` instances with local files in both directions; everything else stays in Studio. | An external editor or Git for code while Studio owns everything else. |
| Rojo | Filesystem-first: local files and project files define the DataModel and sync into Studio. | The whole project, not only code, in version control, or the filesystem as source of truth. |
| Custom or other established workflow | Another authoring or sync model with its own explicit rules. | Projects that none of the above describes accurately. |

Roblox recommends Script Sync for external editing and code version control, and third-party tools such as Rojo when the whole project or the filesystem should be the source of truth. Don't enable two sync systems on the same content.

## Placement model

Use the dimensions that can change the decision:

| Dimension | Values | Question |
| --- | --- | --- |
| Runtime / consumer | Server, client, both | Which Luau environments execute or consume it? |
| Replication | Server-only, client-visible | Can clients receive and inspect it? |
| Authoring | Studio, Script Sync, Rojo, other | Which workflow owns this instance? |

A shared ModuleScript is normally both-runtime and client-visible. A server asset can be server-only without being executable. Decide edit permission separately from these dimensions.

Server Authority prediction/rollback and Script Capabilities sandboxes are specialist cases; see the routing table in [`SKILL.md`](../../SKILL.md#boundary-references).

## Runtime rules

- Put server-only code in server containers, client-only code in supported client locations, and code that both sides run in a client-visible shared container such as `ReplicatedStorage`.
- Prefer a `Script` with `RunContext = Client` in `ReplicatedStorage` for client entrypoints (Roblox's current recommendation). If an entrypoint must live in `StarterPlayerScripts` or `StarterCharacterScripts`, use a `LocalScript` there. A Client-RunContext `Script` in those containers runs both the original and its clone, causing duplicate startup. A `LocalScript` in `ReplicatedStorage` does not run.
- A ModuleScript executes separately in each Luau environment that requires it. Don't treat mutable module state as shared across client/server or across `Actor` boundaries.
- Treat replicated code and data as visible to clients. Keep privileged authority and validation on the server.
- Don't call `require()` in a desynchronized parallel phase; require modules first in serial context.

## Entrypoints

### Single client/server pair

Use one server bootstrap and one client bootstrap when controlled initialization or explicit dependency assembly helps.

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

This is an option, not a universal recommendation. For the SSA form of this topology, follow [`ssa.md`](../ssa/ssa.md).

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

Their execution order is nondeterministic unless the project adds explicit coordination. When one runtime has several entrypoints, name one startup owner or state how they stay independent. Don't propose two scripts that both appear to start the same feature.

### Entrypoint rules

- Without SSA or another reliable lifecycle loader, require feature roots explicitly.
- Treat shared entrypoints and discovery loaders as integration boundaries.
- Without an established lifecycle contract, add separate `Init` / `Start` phases only when ordering or cross-system readiness actually matters.
- Point dependencies toward stable domain/shared modules, not back toward entrypoints.
- Split modules by cohesive responsibility, not line count.

When a design proposes a new executable entrypoint, give its exact DataModel path, filesystem path when mapped, class or `RunContext`, who starts it, its direct dependencies, and a check that can observe it starting. A shared ModuleScript in `ReplicatedStorage` is a dependency, not a client entrypoint.

When a design proposes a new Remote, give its instance path and class, direction, caller and handler, payload shape, the server-side validation rule, and a test for accepted and rejected input. A folder name alone is not a contract.

## Module grouping

### Feature-first

For growing projects where work usually happens by gameplay capability.

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

A shallow list per execution side, when feature folders would add more navigation than clarity.

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

When the project already uses this vocabulary, or systems naturally form long-lived server APIs and client orchestration.

```text
Server/Services/
  InventoryService
  RoundService
Client/Controllers/
  InventoryController
  RoundController
```

### Components or ECS

When repeated behavior and data are naturally components processed by systems.

```text
Components/
  Health
  Damageable
Systems/
  DamageSystem
```

These can combine. Prefer the smallest organization that makes runtime ownership, navigation, and dependencies clear.

## Module style

| Choice | Meaning | Good fit |
| --- | --- | --- |
| Plain Luau | Focused ModuleScripts with explicit dependencies and lifecycle only where needed. | Greenfield work without framework requirements. |
| Existing framework | Keep its discovery, naming, and lifecycle. | Working framework-based projects. |
| Named framework or custom lifecycle | Define framework, discovery, and lifecycle rules deliberately. | Requirements that justify team-wide lifecycle machinery. |

## Naming

Keep coherent existing names and casing. For a new project with no convention, use PascalCase for folders, scripts, and module tables; camelCase for functions and locals; UPPER_SNAKE_CASE for constants.

## Common placement

| Content | Typical home |
| --- | --- |
| Authoritative rules/state, secrets, DataStores, receipts, validation | Server-only code container |
| Client input, camera, local UI behavior | Client-only code container |
| Types, constants, pure utilities used on both sides | `ReplicatedStorage/Shared` or similar |
| RemoteEvents, UnreliableRemoteEvents, RemoteFunctions | `ReplicatedStorage/Remotes` or similar |
| Server-only models and templates | `ServerStorage` |
| Assets both sides need before cloning | `ReplicatedStorage` |
| Earliest loading-screen subset | `ReplicatedFirst` |

These are defaults for open choices and review criteria, not reasons to migrate a working project.

## Sources

- Roblox architecture: [Script types and locations](https://create.roblox.com/docs/scripting/locations), [Plant reference project](https://create.roblox.com/docs/resources/plant-reference-project), [Data model](https://create.roblox.com/docs/projects/data-model)
- Roblox modules: [ModuleScript](https://create.roblox.com/docs/reference/engine/classes/ModuleScript), [Reuse code](https://create.roblox.com/docs/scripting/module), [Parallel Luau](https://create.roblox.com/docs/scripting/multithreading)
- Roblox runtime/security: [Client-server runtime](https://create.roblox.com/docs/projects/client-server), [Client-server boundary](https://create.roblox.com/docs/scripting/security/client-server-boundary), [Access control and confidentiality](https://create.roblox.com/docs/scripting/security/access-control)
- Roblox workflows: [Script Sync](https://create.roblox.com/docs/scripting/sync), [Studio testing modes](https://create.roblox.com/docs/studio/testing-modes), [Third-party tools](https://create.roblox.com/docs/projects/external-tools)
