---
name: roblox-goodsignal-connections
description: GoodSignal (stravant/goodsignal) for Roblox Luau, pinned commit 99497c8. Use when a feature needs several local subscribers to an in-process event with explicit Connect/Disconnect ownership. Not for one local recipient (call it directly) or client/server messaging (use RemoteEvents).
---

# GoodSignal 99497c8

Pinned target: `99497c8cd6e5b50c5f4f12796d4ebc3e7dbf9d1f` (source reviewed 2026-09-30). [resource.yaml](resource.example.yaml) holds the exact identity. This authoring example carries no executed upstream or host proof.

## Check the pin

If the project vendors GoodSignal, its header or the project guide names commit `99497c8cd6e5b50c5f4f12796d4ebc3e7dbf9d1f`, and the vendored source matches that commit's `src/init.lua`; a same-named package is not enough. [Setup](references/setup.md) has the exact comparison.

If it shows another source, tell the user, keep the project's pin, use only API you can confirm at that version, and stop where the task depends on behavior that may differ. If the user wants this skill's version instead, upgrade through the `roblox-resource-acquisition` skill. If the project doesn't vendor GoodSignal, this skill is advice only. Stop on a blocked use noted in the project's `CLAUDE.md`. Say what you checked; comparing source is not a runtime test.

## Core API

| Call | Returns | Notes |
| --- | --- | --- |
| `Signal.new()` | signal | Inert until something connects. |
| `signal:Connect(callback)` | connection | Retain it under the feature owner immediately. |
| `signal:Fire(...)` | nothing | Dispatches through the task scheduler. |
| `connection:Disconnect()` | nothing | Stops future dispatch only. |
| `signal:DisconnectAll()` | nothing | Only when the feature owns the whole signal. |

There is no `Destroy()` method. Do not infer cancellation from another signal library.

## Example

The maintained fixture `scripts/smoke_signal.luau` is the source for this pattern; keep behavior in that file.

```luau
local signal = Signal.new()
local active = true
local connection = signal:Connect(function(payload)
	if not active then return end
	-- update feature state with payload
end)

local function cleanup()
	if not active then return end
	active = false
	connection:Disconnect()
	signal:DisconnectAll()
end
```

## Gotchas

- `Disconnect` cannot undo a callback that is already running or yielded; check the owner's active flag inside the callback.
- Create the cleanup function before `Connect` so a failed setup can roll back.
- The shared coroutine cache belongs to the package; local teardown does not finalize it.
- GoodSignal is local to one Luau environment. It does not replicate, and a client signal is never authorization; validate network input on the server.

## Read further

- Installing or changing the project binding, and the Studio fixture run: read [setup](references/setup.md).
- A matching failure symptom or a security question: read [troubleshooting](references/troubleshooting.md).
