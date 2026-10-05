---
name: roblox-goodsignal-connections
description: Use pinned GoodSignal for feature-owned in-process event callbacks and explicit disconnection; prefer direct calls for a single local recipient.
---

# GoodSignal connections

Reviewed target: `99497c8cd6e5b50c5f4f12796d4ebc3e7dbf9d1f`, source reviewed 2026-09-30. The [resource contract](resource.example.yaml) owns static identity; project records own current execution evidence. This authoring example carries no executed upstream or host proof.

## Choose the task

- An authorized project needs multiple local subscribers with explicit connection ownership.

- A direct call suffices, or communication must cross the client/server network boundary.

## Before use

Resolve the affected project, this child and the available installed parent. Read the parent's references/child-usage.md once per task for freshness, guards, reconciliation and repair. Project resolution failure is unknown state with no global fallback. This required custom profile needs its documented exact-target check before version-sensitive use. The shared checker reports custom checks unavailable and never executes metadata-supplied commands.

Compare the project source manifest/header and inspected bytes to this exact canonical commit; a same-named package is insufficient. Read [setup](references/setup.md) for the installation and fixture binding.

Run `python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/stravant-goodsignal.yaml"`; require HEALTHY. BLOCKED/UNKNOWN or mismatched identity enters parent repair/reconcile before affected use.

## Common use and ownership

Use the maintained `scripts/smoke_signal.luau` fixture as the source for the connection example. It creates one signal, activates a listener with `signal:Connect`, fires a payload and disconnects through an idempotent feature cleanup function. For the active project, preserve the same ownership pattern and use its actual require path. No companion cleanup library is assumed.

```luau
-- API excerpt from scripts/smoke_signal.luau; keep behavior in that fixture.
local signal = Signal.new()
```

A signal owns a linked list of subscriptions. Connect registers a callback; Fire uses the task scheduler to dispatch eligible listeners. Disconnect prevents future dispatch, but it cannot undo an already running or yielded callback.

- Initialization: `Signal.new()` allocates an inert signal. Establish the feature owner's cleanup function before `Connect` activates the listener; immediately retain the returned connection under that owner.
- Reuse: Reuse the signal during the feature lifetime; callbacks check the owner's active flag before changing feature state.
- Cleanup/destruction: Mark the owner inactive, call `connection:Disconnect()` once, then `signal:DisconnectAll()` when the owner owns the whole signal. The fixture's guard makes repeated cleanup idempotent and rolls back on a failed assertion. It creates no pending waits or spawned feature tasks. For already dispatched/yielding callbacks, use feature invalidation and explicit cancellation for any separately owned task; disconnection alone cannot cancel them.
- Ownership boundary: Connections and feature callbacks belong to the feature; the module's shared coroutine cache belongs to the package. Do not claim package-global finalization from local teardown. `Wait()` cancellation and yielding callbacks are outside this fixture's proof.

Source-reviewed APIs: `Signal.new()`, `signal:Connect(callback)`, `signal:Fire(payload)`, `connection:Disconnect()` and `signal:DisconnectAll()`. Do not invent a `Destroy()` method or infer cancellation from another signal library.

GoodSignal is local to the current Luau environment; it does not replicate callbacks. A server may use it internally while retaining authority over game state. A client may use it for local presentation; validate network input on the server rather than treating a local signal as authorization.

## Complete and read further

Executable fixture: scripts/smoke_signal.luau

Run: In an isolated Studio test place with the exact source installed, copy `scripts/smoke_signal.luau` into a server Script under ServerScriptService and run Play. Use the project's strict-analysis path for that authored fixture first.

Pass condition: Output contains `goodsignal-ready`; the callback count equals `1` after the first fire and remains `1` after disconnect and a second fire. A failed assertion reports an error after rolling back the connection.

Evidence boundary: Source review and structural validation are separate from this proposed Studio recipe. Record execution against the actual installed commit before claiming runtime proof; a Lune task adapter covers only the observed non-engine scheduler behavior.

- For installation/configuration, read [setup](references/setup.md).
- For the named failure symptoms and security constraints, read [troubleshooting](references/troubleshooting.md).
