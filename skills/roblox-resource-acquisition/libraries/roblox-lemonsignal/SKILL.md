---
name: roblox-lemonsignal
description: LemonSignal (Data-Oriented-House/LemonSignal) custom signals for Roblox Luau, pinned 2.0.0. Use when creating or typing custom events with LemonSignal.new or LemonSignal.wrap, calling Connect/Once/Wait/Fire/DisconnectAll/Destroy, using connection Disconnect/Reconnect, or debugging signal lifetime and leaks. Not for RemoteEvents or networking.
---

# LemonSignal 2.0.0

Pinned target: `2.0.0` (source reviewed 2026-10-03). [resource.yaml](resource.yaml) holds the exact identity.

## Check the pin

If the project pins LemonSignal, confirm it matches the target. If the `roblox-resource-acquisition` skill is available (two folders up when this skill sits in its `libraries/` folder, otherwise beside this one), run its checks per [child usage](../../references/child-usage.md). If the parent or Python is unavailable, read the project's manifest/lock directly and say which checks were skipped. On a `FAIL` result or an observed mismatch, tell the user and keep the project's pin; continue with API you can confirm at the project's version, and stop only where the task depends on version-specific behavior. Stop on a blocked use noted in the project's `CLAUDE.md`.

## Core API

| Call | Returns | Notes |
| --- | --- | --- |
| `LemonSignal.new()` | `Signal<T...>` | An inert custom signal. The module exports only `new` and `wrap`. |
| `LemonSignal.wrap(rbxSignal)` | `Signal<T...>` | Connects to an engine signal and re-fires it. The native connection is stored in `signal.RBXScriptConnection`. |
| `signal:Connect(fn)` | `Connection` | Takes only the callback. 2.0.0 dropped extra bound arguments; capture context in a closure. |
| `signal:Once(fn)` | `Connection` | Disconnects itself before calling `fn`. |
| `signal:Wait()` | fired values | Yields the current thread until the next `Fire`. |
| `signal:Fire(...)` | nothing | Runs each listener with `task.spawn` on a pooled thread. Listeners may yield. |
| `signal:DisconnectAll()` | nothing | Disconnects every listener. |
| `signal:Destroy()` | nothing | `DisconnectAll`, plus disconnecting the wrapped engine connection. The signal stays usable. |
| `conn.Connected` | boolean | |
| `conn:Disconnect()` | nothing | Safe to call repeatedly. |
| `conn:Reconnect()` | nothing | Re-attaches the same callback. Does nothing if already connected. |

Types: `LemonSignal.Signal<T...>` and `LemonSignal.Connection`, when the project's wrapper re-exports them.

## Example

```luau
local LemonSignal = require(ReplicatedStorage.Packages.LemonSignal) -- use the project's mapped path

local damaged: LemonSignal.Signal<number, Player?> = LemonSignal.new()
local conn = damaged:Connect(function(amount, attacker) print("hit", amount, attacker) end)
damaged:Once(function(amount) print("first hit", amount) end)

damaged:Fire(10, nil) -- "first hit 10" prints before "hit 10 nil": newest listener first
conn:Disconnect()
damaged:Fire(5, nil) -- nothing listens now
conn:Reconnect() -- same callback, moved to the front

local heartbeat = LemonSignal.wrap(RunService.Heartbeat) -- owns a native connection
heartbeat:Destroy() -- drops listeners and the native connection
```

## Gotchas

- Listeners fire **newest first**, because `Connect` and `Reconnect` insert at the head. Don't rely on order. A listener connected during `Fire` is not called by that `Fire`.
- `Destroy` is not a close. It disconnects current listeners, but `Connect`, `Fire` and `Reconnect` keep working afterwards. Drop your references, and don't `Reconnect` old handles after teardown.
- `Destroy` does not resume a thread blocked in `Wait()`: it stays suspended forever. Cancel the waiting thread yourself, or use a `Connect` handle you can disconnect.
- Disconnecting doesn't stop a callback that is already running (for example one that yielded). Check a `disposed` flag before applying late results.
- In Janitor, add connections with `"Disconnect"` and signals you created with `"Destroy"`. A connection added with the default method silently leaks.
- `Fire` stays within one runtime. It is not networking, and client-fired events are not trusted facts on the server.

## Read further

- Wait/cancellation patterns, wrapping engine signals, ownership and the thread pool: read [API and lifecycle](references/api-and-lifecycle.md).
- Installing, restoring or mapping the package: read [setup](references/setup.md).
- Unexpected arguments, a stuck `Wait`, or events that keep firing: read [troubleshooting](references/troubleshooting.md).
