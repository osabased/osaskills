# LemonSignal 2.0.0 API and lifecycle

Everything below was checked against `src/LemonSignal.lua` at tag `v2.0.0`.

## Internals that affect your code

- Connections form a doubly linked list headed at `signal._head`. `Connect` and `Reconnect` insert at the head, and `Fire` walks from the head, so listeners run newest first.
- `Fire` captures the current head, then for each connection takes a free pooled coroutine (or creates one) and runs `task.spawn(thread, callback, thread, ...)`. A callback that finishes returns its thread to the pool. A callback that yields keeps the thread until it finishes.
- An error in one callback is reported by `task.spawn` and does not stop the other listeners.
- `Disconnect` unlinks the connection but leaves its `_next` pointer intact, so disconnecting during `Fire` is safe.
- At require time, the module creates and destroys one `BindableEvent` to cache the native `Connect`/`Disconnect` methods. Outside Roblox (no `task`), `Fire` uses `coroutine.resume` instead, and `wrap` is unusable.

## Wait and cancellation

`Wait` connects an internal callback that disconnects itself and resumes the waiting thread. `Destroy`/`DisconnectAll` remove that callback **without** resuming the thread, so it stays suspended forever.

For a cancellable wait, own the connection and the thread:

```luau
local function waitFor(signal, timeout: number)
	local thread = coroutine.running()
	local conn
	local timer = task.delay(timeout, function()
		conn:Disconnect()
		task.spawn(thread, false)
	end)
	conn = signal:Once(function(...)
		task.cancel(timer)
		task.spawn(thread, true, ...)
	end)
	return coroutine.yield() -- (true, ...) on fire, false on timeout
end
```

On a long-lived signal that another feature owns, never `Destroy` it to free your waiter; disconnect your own connection instead.

## Ownership

- Destroy only signals and wrappers your feature created. `wrap` holds a live engine connection until `Destroy`.
- Disconnect the subscriptions your feature made on signals it borrowed.
- Never touch the module's shared coroutine pool.
- Setup order: create the owner (for example a Janitor) first, then register each connection as you make it. If setup fails partway, clean the owner up before rethrowing.
- Late callbacks: set a `disposed` flag in teardown and check it after every yield in a callback.

## Choosing between signals and state

LemonSignal is for discrete events ("player damaged", "menu closed"). For state that views read continuously, use a state library (Charm) or Vide sources. Native `RBXScriptSignal`s can be connected to directly; wrap them only when you need a `Signal` interface or one owner that disconnects everything.
