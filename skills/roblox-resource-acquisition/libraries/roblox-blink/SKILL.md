---
name: roblox-blink
description: Blink (1Axen/blink) networking IDL compiler for Roblox Luau, pinned 0.18.9. Use when editing .blink schema files (event, function, struct, enum, map, options such as ServerOutput/ClientOutput/RemoteScope), running the blink CLI through pesde, placing the generated Client/Server/Types modules, or calling the generated Fire/FireAll/On/Invoke APIs. Not for choosing a networking library.
---

# Blink 0.18.9

Pinned target: `0.18.9` (source reviewed 2026-10-03). [resource.yaml](resource.yaml) holds the exact identity. 1.0.0 pre-releases exist upstream; they are a rewrite, so don't mix their syntax or docs with 0.18.9.

## Check the pin

If the project pins Blink, confirm it matches the target (`pesde run blink -- --version` prints `0.18.9`). If the `roblox-resource-acquisition` skill is available (two folders up when this skill sits in its `libraries/` folder, otherwise beside this one), run its checks per [child usage](../../references/child-usage.md). If the parent or Python is unavailable, read the project's manifest/lock directly and say which checks were skipped. On a `FAIL` result or an observed mismatch, tell the user and keep the project's pin; continue with API you can confirm at the project's version, and stop only where the task depends on version-specific behavior. Stop on a blocked use noted in the project's `CLAUDE.md`.

## Core API

| Piece | Form | Notes |
| --- | --- | --- |
| Compile | `pesde run blink -- network/main` | Finds `network/main.blink` (or `.txt`). Add `--watch` to recompile on changes. `pesde exec` runs the registry copy, not the locked one. |
| Options | `option ServerOutput = "../src/server/Network/Server.luau"` | Also `ClientOutput`, `TypesOutput`, `RemoteScope`, `Casing`, `Typescript`, `UsePolling`, `ManualReplication`, `WriteValidations`, `SyncValidation`, `FutureLibrary`, `PromiseLibrary`. Output paths are relative to the schema file. |
| Event | `event Name { From: Client\|Server, Type: Reliable\|Unreliable, Call: SingleSync\|ManySync\|SingleAsync\|ManyAsync\|Polling, Data: T }` | `Data` is optional; `(A, B)` sends several values. Unreliable payloads are limited to 1000 bytes. |
| Function | `function Name { Yield: Coroutine\|Future\|Promise, Data: T, Return: T }` | The client invokes; the server answers. `Data` and `Return` are optional. |
| Types | `u8..u32`, `i8..i32`, `f16/f32/f64`, `string`, `boolean`, `buffer`, `vector`, `CFrame`, `Color3`, `Instance(Class)`, `unknown` | Bound with ranges: `u8(0..100)`, `string(3..20)`, `T[1..50]`. Make optional with a trailing `?`. |
| Declarations | `type`, `struct`, `enum`, `map`, `set`, `scope`, `import` | See [schema](references/schema.md). |
| Generated server API | `E.Fire(player, ...)`, `E.FireAll(...)`, `E.FireList(players, ...)`, `E.FireExcept(player, ...)`, `E.On(fn(player, ...)) -> disconnect`, `F.On(fn(player, ...) return value end)` | Names follow `option Casing` (default `Pascal`; `Camel` gives `fireAll`, `Snake` gives `fire_all`). |
| Generated client API | `E.Fire(...)`, `E.On(fn(...)) -> disconnect`, `E.Iter()` (Polling events), `F.Invoke(...)` | |

## Example

```blink
-- network/main.blink   (comments use --, not #)
option ServerOutput = "../src/server/Network/Server.luau"
option ClientOutput = "../src/client/Network/Client.luau"
option TypesOutput = "../src/shared/Network/Types.luau"
option RemoteScope = "MyGame"

struct Purchase { ItemId: string(1..32), Quantity: u8(1..10) }
event BuyItem { From: Client, Type: Reliable, Call: SingleAsync, Data: Purchase }
event CoinsChanged { From: Server, Type: Reliable, Call: ManySync, Data: u32 }
function GetPrice { Yield: Coroutine, Data: string(1..32), Return: u32 }
```

```luau
-- server (after `pesde run blink -- network/main`)
local Net = require(ServerScriptService.Network.Server)
Net.BuyItem.On(function(player, purchase) --[[ validate, then apply ]] end)
Net.GetPrice.On(function(player, itemId) return 100 end)
Net.CoinsChanged.Fire(player, 150)
-- client: local Net = require(...Network.Client); Net.BuyItem.Fire({ ItemId = "sword", Quantity = 1 })
```

## Gotchas

- **Receive-side DoS ([issue #45](https://github.com/1Axen/blink/issues/45)).** 0.18.9's generated server parses the whole incoming buffer before any handler runs, so a client can send a huge buffer. Schema bounds and handler throttling don't protect the parser. Before enabling untrusted client-to-server events in production, put a tested pre-decode byte and rate budget in the actual receive path, or report the risk to the owner. Don't patch generated code silently.
- Requiring a generated module starts networking: the server creates remotes and connects `OnServerEvent`, `PlayerRemoving` and Heartbeat, even for an empty schema, and the client waits for the remotes. Keep generated modules unrequired until networking is meant to be live. There is no global `Destroy`.
- Regenerate all outputs from the same schema and CLI version, and never edit generated files. Generation is not transactional, so a failed compile may leave old outputs in place.
- Give each separate Blink setup a unique `RemoteScope`. Generated code registers `_G._BLINK[RemoteScope]`, so duplicate or re-required transports collide.
- Types are serialization, not authorization. Validate every client request on the server (ownership, cost, cooldown). A non-optional `Instance` that arrives `nil` (for example because of streaming) drops the rest of the packet, so mark such fields `?`.
- `Sync` call modes run handlers without yielding; yielding or erroring in them is undefined behavior. Prefer `SingleAsync`/`ManyAsync` unless profiling says otherwise.

## Read further

- Full schema syntax (structs, enums, maps, sets, scopes, imports, generics, exports): read [schema](references/schema.md).
- Generated runtime behavior, polling, functions, placement and lifecycle: read [API and lifecycle](references/api-and-lifecycle.md).
- Installing or restoring the pesde CLI: read [setup](references/setup.md).
- A compiler error, missing outputs, a client that waits forever, or the security boundary: read [troubleshooting](references/troubleshooting.md).
