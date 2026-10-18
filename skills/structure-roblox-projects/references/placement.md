# Placement

Use to choose an open layout, container, entrypoint, Remote or grouping, or to judge one in a review. During ordinary work, keep a coherent existing structure instead of normalizing it toward these defaults. A project on ModuleLoader SSA follows [ssa.md](ssa.md) for feature placement and lifecycle; one on another loader or framework follows that tool's discovery and lifecycle rules, worked out as in [unfamiliar stacks](unfamiliar-stack.md).

## Source of truth

| Workflow | What it owns | Good fit |
| --- | --- | --- |
| Keep the detected one | The project's working authoring and sync boundaries | Established projects |
| Studio-native | The whole DataModel, script source included, lives in Studio | One editor, no filesystem build |
| Script Sync | `Script`, `LocalScript`, `ModuleScript` and `Folder` instances sync both ways with local files; everything else stays in Studio | External editor and Git for code while Studio owns the rest |
| Rojo | Local files and project files define the DataModel and sync into Studio | The filesystem as source of truth |
| Custom | Another sync model with its own explicit rules | Projects none of the above describes |

Roblox recommends Script Sync for external editing and versioned code, and tools such as Rojo when the filesystem should own the project. For agents, a filesystem source of truth matters: what an agent can read, diff and check is what it can verify, and anything that only exists in Studio needs a Studio connection to inspect. Never run two sync systems on the same content. Details: [Rojo](rojo.md), [Script Sync](script-sync.md), [Studio-only](studio-only.md).

## Containers

| Content | Home |
| --- | --- |
| Authoritative rules and state, secrets, DataStores, receipts, validation | `ServerScriptService` (code), `ServerStorage` (assets, templates) |
| Server entrypoint | `Script` (or `RunContext = Server`) in `ServerScriptService` |
| Client entrypoint | `Script` with `RunContext = Client` in `ReplicatedStorage`; a `LocalScript` if it must live in `StarterPlayerScripts` or `StarterCharacterScripts` |
| Client-only modules: input, camera, UI | A client folder in `ReplicatedStorage` (or under `StarterPlayerScripts`) |
| Types, constants, pure logic both sides run | `ReplicatedStorage/Shared` or similar |
| `RemoteEvent`, `UnreliableRemoteEvent`, `RemoteFunction` | `ReplicatedStorage/Remotes` or similar, or created by a networking library |
| Assets both sides need | `ReplicatedStorage` |
| The earliest loading-screen subset | `ReplicatedFirst` |

Replicated means client-readable, including module source. A server asset can be server-only without being executable.

## Entrypoints

Prefer one startup owner per runtime: one server `Script` and one client `Script` that require feature modules explicitly or through a loader. Agents and reviewers can then find what starts and in what order.

```text
ReplicatedStorage/
  ClientMain        Script, RunContext = Client
  Client/           client-only modules
  Shared/           modules both sides use
ServerScriptService/
  ServerMain        Script, RunContext = Server
  Server/           server-only modules
ServerStorage/
  Assets/
```

Independent scripts are fine where lifetime or isolation makes them simpler: a tool, a character script, an `Actor`, a self-contained `Workspace` model. Their order is nondeterministic, so name which one owns startup per runtime, or state how they stay independent. Never let two scripts appear to start the same feature.

- Without a lifecycle loader, require feature roots explicitly from the entrypoint.
- Add separate `Init`/`Start` phases only when ordering or cross-feature readiness actually matters.
- Point dependencies at stable domain or shared modules, never back at entrypoints.

**Proposing an entrypoint:** give its DataModel path, file path when mapped, class or `RunContext`, who starts it, its direct dependencies, and a check that observes it starting. A shared ModuleScript is a dependency, not an entrypoint.

**Proposing a Remote:** give its instance path and class (or the networking library's declaration), direction, caller and handler, payload shape, the server-side validation, and a test with accepted and rejected input. A folder name is not a contract. Client-to-server entries are attack surface: the server checks type, range, ownership and rate on every one.

## Grouping and naming

- **Feature-first** (`Server/Combat`, `Client/Combat`, `Shared/Combat`) when work happens by gameplay capability.
- **Runtime layers** (a flat list per side) when feature folders would add navigation without clarity.
- **Services and controllers** when the project uses that vocabulary or has long-lived server APIs and client orchestration.
- **Components and systems (ECS)** when behavior is data processed by systems.

They combine. Prefer the smallest organization that makes runtime ownership and dependencies obvious, and one predictable pattern over several clever ones: an agent repeats whatever pattern it finds, so make the common case the easy one to copy. Keep existing names and casing; with no convention, use PascalCase for folders, scripts and module tables, camelCase for functions and locals, UPPER_SNAKE_CASE for constants. Split modules by responsibility, not line count. Keep a working framework's discovery, naming and lifecycle.

## Sources

- [Script types and locations](https://create.roblox.com/docs/scripting/locations), [Data model](https://create.roblox.com/docs/projects/data-model), [Plant reference project](https://create.roblox.com/docs/resources/plant-reference-project)
- [ModuleScript](https://create.roblox.com/docs/reference/engine/classes/ModuleScript), [Reuse code](https://create.roblox.com/docs/scripting/module), [Parallel Luau](https://create.roblox.com/docs/scripting/multithreading)
- [Client-server runtime](https://create.roblox.com/docs/projects/client-server), [Client-server boundary](https://create.roblox.com/docs/scripting/security/client-server-boundary), [Access control](https://create.roblox.com/docs/scripting/security/access-control)
- [Script Sync](https://create.roblox.com/docs/scripting/sync), [Third-party tools](https://create.roblox.com/docs/projects/external-tools)
