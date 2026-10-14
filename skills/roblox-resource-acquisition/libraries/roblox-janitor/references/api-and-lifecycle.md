# Janitor 1.18.3 API and lifecycle

Everything below was checked against `src/init.luau` at commit `b8e562f` ("update version to 1.18.3").

## How cleanup works

A Janitor stores `object -> method` pairs in itself, plus an optional `index -> object` map. On `Cleanup`, for each pair, in `next()` order:

- `true`: call a function; `task.cancel` a thread. If cancelling fails, the cancel is retried with `task.defer`, or with `FastDefer` when `UnsafeThreadCleanup` is true.
- `"Destroy"`: call `object:Destroy()` if it exists. With `SuppressInstanceReDestroy = true`, Instances are destroyed inside `pcall`.
- `"Disconnect"`: call `object:Disconnect()` if it exists.
- Any other string: call that method if it exists.

A missing method is skipped silently at cleanup time. The only signal is the warning `Add` printed earlier.

`Cleanup` sets `CurrentlyCleaning` for its duration and resets it at the end. If an entry throws, the reset never happens. The instance field stays nil and reads fall through to the class default `true`, so later `Cleanup`/`Destroy` calls return immediately. `SuppressInstanceReDestroy` and `UnsafeThreadCleanup` are lost the same way. Treat a throwing cleanup as a bug to fix, not a condition to retry.

## Patterns

**Own everything as you acquire it:**

```luau
local function startFeature(player: Player)
	local janitor = Janitor.new()
	local ok, err = pcall(function()
		local gui = janitor:Add(template:Clone())
		janitor:Add(player.CharacterAdded:Connect(onCharacter))
		gui.Parent = player.PlayerGui
	end)
	if not ok then
		janitor:Destroy() -- roll back whatever was acquired before the error
		error(err)
	end
	return janitor
end
```

**Replace by index** (one active tween, request, or highlight at a time):

```luau
janitor:Add(TweenService:Create(frame, info, goal), "Cancel", "Tween") -- cancels the previous tween
```

**Hand off ownership:** `local obj = janitor:Get("Thing"); janitor:RemoveNoClean("Thing")`. The new owner now cleans it up.

**Idempotent teardown:**

```luau
local disposed = false
local function dispose()
	if disposed then return end
	disposed = true
	janitor:Destroy()
end
```

**Ordered teardown:** use one Janitor for producers (connections, remote listeners, tasks) and one for consumers (UI). Clean the producer Janitor first, in its own `pcall`, then the consumer Janitor.

**Cleanup on Instance death:** `janitor:LinkToInstance(model)` runs `Cleanup` when `model:Destroy()` is called. Pass `allowMultiple = true` to keep earlier links. Without it, a new link replaces the previous one.

## Threads and Promises

- Threads use `true`. Janitor calls `task.cancel`; cancelling the currently running thread is deferred.
- `AddPromise(promise, index?)` requires a Promise (the reviewed lock resolved `howmanysmall/typed-promise` 4.0.6 over `evaera/promise` 4.0.0). It cancels the Promise on cleanup if it is still pending. Nevermore's Promise is a different implementation.

## Other libraries

- Vide scopes clean up their own effects. Add a Vide mount disposer to a Janitor only as an idempotent callback.
- Charm disposers are plain functions: `janitor:Add(dispose, true)`.
- Signal-library connections: `janitor:Add(conn, "Disconnect")`. A signal your feature created: `janitor:Add(signal, "Destroy")`.
- A Janitor only cleans up in its own runtime. A server Janitor cannot clean client UI.
