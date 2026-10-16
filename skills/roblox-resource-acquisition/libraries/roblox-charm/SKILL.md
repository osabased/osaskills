---
name: roblox-charm
description: Charm (littensy/charm) reactive state library for Roblox Luau, pinned 0.11.1. Use when writing or debugging Charm state - Charm.signal getter/setter pairs, atom, computed, effect, listen, subscribe, batch, effectScope, onCleanup, untracked, observe, mapped - or bridging Charm state into Vide UI. Not for Charm Sync networking or custom events.
---

# Charm 0.11.1

Pinned target: `0.11.1` (release commit `af4eb5262d640cf89c56217ab7feb403e939cbd2`, source reviewed 2026-10-03). [resource.yaml](resource.yaml) holds the exact identity.

## Check the pin

Before relying on version-specific guidance, read the project's manifest and lock:

- `pesde.toml` declares `{ wally = "littensy/charm", version = "=0.11.1" }` (under any alias), and `pesde.lock` resolves it to `wally#littensy/charm@0.11.1 roblox`.
- In a Wally project, `wally.toml` declares `"littensy/charm@=0.11.1"`, or a range that `wally.lock` resolves to `0.11.1`.

If they show another version, tell the user, keep the project's pin, use only API you can confirm at that version, and stop where the task depends on behavior that may differ. If the user wants this skill's version instead, upgrade through the `roblox-resource-acquisition` skill. If the project doesn't declare Charm, this skill is advice only. Stop on a blocked use noted in the project's `CLAUDE.md`. Say what you checked; reading the manifest is not a runtime test.

## Core API

| Call | Returns | Notes |
| --- | --- | --- |
| `signal(initial, equals?)` | `getter, setter` | `setter(v)` or `setter(function(current) return next end)`. The setter returns the new value. `equals(current, incoming) == true` skips the update. |
| `atom(initial, equals?)` | `Atom<T>` | One function: `a()` reads, `a(v)` writes. |
| `computed(fn(prev?))` | getter | Lazy and cached. Recomputes only when it is read after a dependency changed. |
| `effect(fn)` | dispose | Runs now and synchronously after each change. `fn` may return a cleanup, which runs before the next run and on dispose. |
| `listen(getter, fn(state, prev?))` | dispose | Calls `fn` immediately (`prev` is nil), then on each change. |
| `subscribe(getter, fn(state, prev))` | dispose | Like `listen`, but skips the immediate call. |
| `batch(fn, ...)` | `fn`'s results | Effects run once, when the outermost batch ends. There is no rollback on error. |
| `effectScope(fn, detached?)` | dispose | Owns the effects created inside `fn`. With `detached = true` it ignores the parent scope. |
| `onCleanup(fn, failSilently?)` | nothing | Registers a cleanup in the running effect or scope. Warns outside one. |
| `untracked(fn, ...)` | `fn`'s results | Reads without subscribing, and doesn't adopt inner effects. |
| `observe(getter, fn(value, key))` | dispose | Calls `fn` once per key of a table. `fn` may return a cleanup, which runs when that key is removed. |
| `mapped(getter, fn(v, k) -> (v2, k2?))` | getter | Maps a table per entry, keeping cached results. |

Also exported: `trigger`, `flags`, `getActiveSub`/`setActiveSub`, `startBatch`/`endBatch`, and the types `Getter<T>`, `Setter<T>`, `Atom<T>`, `Update<T>`, `Equals<T>`, `Cleanup`.

## Example

```luau
local Charm = require(ReplicatedStorage.Packages.Charm) -- use the project's mapped path

local getCoins, setCoins = Charm.signal(0)
local isRich = Charm.computed(function() return getCoins() >= 100 end)

local stopListen = Charm.listen(isRich, function(rich, wasRich)
	print("rich:", rich, "was:", wasRich) -- prints "false nil" now
end)
local stopEffect = Charm.effect(function()
	print("coins:", getCoins())
	return function() print("before next run or dispose") end
end)

setCoins(function(c) return c + 150 end) -- effect re-runs; listen prints "true false"
Charm.batch(function() setCoins(1); setCoins(2) end) -- effect runs once, with 2
stopListen(); stopEffect()
```

## Gotchas

- Default equality is `~=` (reference equality for tables). Mutating a table and setting it again does not notify. Build a new table.
- `flags.frozen` and `flags.strict` default to **on in Studio and off in live servers**. In Studio, values set into signals are deep-frozen (tables without metatables), and a yield inside an effect, computed, or updater errors. Code that mutates state "works" live and breaks in Studio, so never mutate.
- Hold on to every dispose function. If an effect's first run throws, the error propagates and you get no disposer.
- `listen`/`subscribe` callbacks run untracked. Effects created inside them are not owned by the subscription; wrap them in `effectScope` and keep its disposer.
- Charm getters create no Vide dependency. A Charm getter used as a Vide property updates once and then never again. Bridge through a Vide Source (see [API and lifecycle](references/api-and-lifecycle.md#bridge-charm-into-vide)).
- State is per runtime: server signals don't replicate. Charm Sync is a separate package.

## Read further

- `trigger`, `observe`, `mapped`, scope ownership, the Vide bridge, and teardown recipes: read [API and lifecycle](references/api-and-lifecycle.md).
- Installing, restoring or mapping the package: read [setup](references/setup.md).
- A value or UI that doesn't update, or an effect that survives teardown: read [troubleshooting](references/troubleshooting.md).
- Wrong or missing guidance at this pin: report it with the smallest reproduction and the exact proposed fix. Fix it in the `roblox-resource-acquisition` catalog, not here, because re-cloning overwrites local edits.
