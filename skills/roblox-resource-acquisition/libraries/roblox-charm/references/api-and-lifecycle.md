# Charm 0.11.1 API and lifecycle

Everything below was checked against `packages/charm/src/init.luau` at tag `charm-v0.11.1`.

## Mental model

Signals hold values. Computed getters derive values lazily. Effects subscribe to whatever they read while running, and re-run synchronously when it changes. Charm models *state*. Use a signal library (e.g. LemonSignal) for one-off events and a renderer (e.g. Vide) for views.

## More API

- `computed(function(previous) ... end)` receives its previous value, which is useful for incremental results.
- `trigger(fn)` notifies dependents of every signal read inside `fn`. Use it only when a value was mutated without its setter, which you should avoid.
- `observe(tableGetter, function(value, key) ... return cleanup end)` runs once per key. The cleanup runs when that key disappears or the observer is disposed. Effects created in the callback are bound to that key's lifetime.
- `mapped(tableGetter, function(value, key) return newValue, newKey? end)` returns a getter for the mapped table. It only calls the transform for new or changed entries, and copies the output table on write.
- `untracked(fn, ...)` reads without subscribing **and** stops the surrounding effect from adopting effects created in `fn`. To skip tracking while still adopting inner effects, use `effectScope`.
- `effectScope(fn, detached?)` collects the effects and cleanups created in `fn` under one disposer. `fn` may return a cleanup.
- `onCleanup(fn, failSilently?)` adds a cleanup to the running effect or scope. Outside one, it warns (or stays silent) and does nothing.

## Flags

| Flag | Default | Effect |
| --- | --- | --- |
| `flags.strict` | `RunService:IsStudio()` | Wraps user callbacks in coroutines; a yield raises "Attempted to yield in an effect or scope". |
| `flags.frozen` | `RunService:IsStudio()` | Deep-freezes values passed to signals (tables without metatables, recursively). |
| `flags.trackInnerEffects` | `true` | Effects created inside an effect are disposed when the outer effect re-runs. |

Don't flip these flags to silence an error; fix the yield or mutation instead.

## Ownership and teardown

- Calling `effect`, `listen`, `subscribe`, `observe` or `effectScope` activates it immediately. Store the returned disposer before doing anything that can fail.
- If the first run throws, the call errors and returns no disposer, and anything it acquired is not guaranteed to be rolled back. For fallible setup, wrap it in an outer scope:

```luau
local dispose = Charm.effectScope(function()
	Charm.effect(function() ... end)
	Charm.listen(getter, onChange)
end)
-- later: dispose() stops every effect created inside
```

- Effect cleanups run before the next run and on dispose. If several cleanups error, all of them still run, then one combined error is raised.
- Disposing twice is harmless: cleanup lists are cleared on the first dispose.
- Work you spawn yourself (`task.spawn`, `task.delay`) is not cancelled by Charm. Cancel it in a cleanup, or check a disposed flag before applying its result.
- Never "finalize" Charm globally. A feature owns only its own disposers.
- When putting Charm disposers into a Janitor, add them as callbacks (`janitor:Add(dispose, true)`). Janitor's cleanup order is unspecified, so if order matters, stop producers in a separate step first.

## Bridge Charm into Vide

Charm and Vide track dependencies separately. Inside a Vide component, mirror a Charm getter into a Vide Source:

```luau
local function fromCharm<T>(getter: () -> T): Vide.Source<T>
	local value = Vide.source(Charm.untracked(getter))
	Vide.cleanup(Charm.subscribe(getter, function(state) value(state) end))
	return value
end

-- in a component: Text = fromCharm(getCoinsLabel)
```

The subscription ends when the Vide scope is destroyed. This recipe is advice only; it has not been run here.

## Client and server

Each runtime has its own Charm state and require cache. Server signals do not replicate. Keep authoritative state on the server and validate client requests there. Charm Sync (`littensy/charm-sync`) is a separate package with its own pin.
