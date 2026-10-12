# Blink 0.18.9 generated API and lifecycle

Checked against `docs/pages/language/5-events.mdx`, `6-functions.mdx` and `src/Generator/init.luau` / `src/Settings.luau` at `v0.18.9`. Method names below use the default `Casing = Pascal`. With `Camel` they become `fire`, `fireAll`, `on`, `invoke`, `iter`; with `Snake`, `fire_all`, `fire_list`, `fire_except`.

## Generated modules

| Output | Require from | API |
| --- | --- | --- |
| Server | server code only (`ServerScriptService`) | `Event.Fire(player, ...)`, `FireAll(...)`, `FireList({players}, ...)`, `FireExcept(player, ...)` for `From: Server`; `Event.On(function(player, ...) end)` for `From: Client`; `Function.On(function(player, ...) return ... end)` |
| Client | client code only (a module the client can require) | `Event.Fire(...)` for `From: Client`; `Event.On(function(...) end)` for `From: Server`; `Function.Invoke(...)` |
| Types | both | Luau types for your declarations |

- `On` returns a disconnect function.
- Polling events (`Call: Polling`, or `option UsePolling = true`) are read with `for i, ... in Event.Iter() do`, and the server version yields `player` first.
- With `Yield: Coroutine`, `Invoke` returns the value. With `Future`/`Promise`, it returns that object (`:Await()` or `:await()`).
- Scopes and imports nest: `Net.Combat.Hit.Fire(...)`, `Net.Shared.Event.FireAll(...)`.
- With `ManualReplication = true`, call `StepReplication()` yourself, for example once per frame.

## Lifecycle

- **Compiling** (`pesde run blink -- file`) reads the schema and its imports, writes the outputs and exits. A schema error prints a diagnostic and exits nonzero. Outputs aren't written transactionally, so check that all outputs share the same header and content after a failed run.
- **`--watch`** keeps a process running. Stop only a watcher your task started.
- **Requiring Server** creates or finds the remotes and connects `OnServerEvent`, `PlayerRemoving` and a Heartbeat sender. Requiring **Client** waits for those remotes. This happens even for an empty schema. It is process-wide, registered in `_G._BLINK[RemoteScope]`, and there is no teardown API.
- **Handlers:** the code that calls `On` owns the returned disconnect. Pending `Invoke` calls are not cancellable; guard late results with a disposed flag.
- UI stories and previews should use a mock transport, not require the generated modules.

## Placement

The CLI runs at build time under Lune (through pesde), never in the game. Put the Server output under `ServerScriptService`, the Client output where client code can require it, and Types in the shared module root. A module only runs when something requires it; replication alone does nothing.

## Trust boundary

The server is authoritative. Schema types guarantee shape (when decoding succeeds), not permission. Validate ownership, prices, cooldowns and rates in the handler, and see the receive-side DoS gotcha in [SKILL.md](../SKILL.md#gotchas) for what handlers cannot protect.
