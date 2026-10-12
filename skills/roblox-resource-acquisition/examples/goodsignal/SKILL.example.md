---
name: roblox-goodsignal-connections
description: GoodSignal (stravant/goodsignal) for Roblox Luau, pinned commit 99497c8. Use when a feature needs several local subscribers to an in-process event with explicit Connect/Disconnect ownership. Not for one local recipient (call it directly) or client/server messaging (use RemoteEvents).
---

# GoodSignal 99497c8

Pinned target: `99497c8cd6e5b50c5f4f12796d4ebc3e7dbf9d1f` (source reviewed 2026-09-30). [resource.yaml](resource.example.yaml) holds the exact identity. This authoring example carries no executed upstream or host proof.

## Check the pin

If the project vendors or pins GoodSignal, compare its source header and bytes with the pinned commit; a same-named package is not enough. This child uses a custom profile, so the shared checker reports it unavailable and never runs it: follow [setup](references/setup.md) for the exact check. If the `roblox-resource-acquisition` skill is available (two folders up when this skill sits in its `libraries/` folder, otherwise beside this one), also run its record query per [child usage](../../references/child-usage.md). If the parent, Python or a project record is unavailable, read the project's source directly and say which checks were skipped. Stop only on a `FAIL`, `MISMATCH`, `BLOCKED` or `FAILED` result, an observed mismatch, or an explicit block.

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
