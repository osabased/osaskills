---
name: roblox-vide
description: Vide (centau/vide) reactive UI library for Roblox Luau, pinned 0.4.1. Use when writing or debugging Vide components and state - vide.create, source, derive, effect, show, switch, indexes, values, mount, root, cleanup, context, spring, action/changed - or a Vide story for UI Labs. Not for React, Fusion or Nevermore Blend UI.
---

# Vide 0.4.1

Pinned target: commit `5ed4c01940e6bd578fb83253cfbeda0a6c05177c` (tag 0.4.1, source reviewed 2026-10-02). [resource.yaml](resource.yaml) holds the exact identity. 0.4.1 is a GitHub pre-release, and its `pesde.toml`/`wally.toml` still say 0.4.0, so the commit identifies it.

## Check the pin

If the project pins Vide, confirm it matches the target. If the `roblox-resource-acquisition` skill is available (two folders up when this skill sits in its `libraries/` folder, otherwise beside this one), run its checks per [child usage](../../references/child-usage.md). If the parent or Python is unavailable, read the project's manifest/lock directly and say which checks were skipped. On a `FAIL` result or an observed mismatch, tell the user and keep the project's pin; continue with API you can confirm at the project's version, and stop only where the task depends on version-specific behavior. Stop on a blocked use noted in the project's `CLAUDE.md`.

## Core API

| Call | Returns | Notes |
| --- | --- | --- |
| `source(initial)` | `Source<T>` | `s()` reads (and tracks inside effects); `s(v)` writes. Rewriting the same non-table value or the same frozen table does nothing. |
| `derive(fn)` | getter | Memoised computed value. |
| `effect(fn)` | nothing | Runs now, then again whenever a source it read changes. |
| `create "Class" { ... }` | Instance | String key: property. Function value: reactive property, or a listener if the property is an event. Number key: child. `Parent` is set last. |
| `show(cond, fn, fallback?)` | getter of child | Builds `fn()` while `cond()` is truthy and destroys its scope otherwise. |
| `switch(src) { [key] = fn }` | getter of child | Builds the component mapped to `src()`. |
| `indexes(tbl, fn(valueSrc, key, present))` | getter of `{Instance}` | One scope per key; the value arrives as a Source. |
| `values(tbl, fn(value, keySrc, present))` | getter of `{Instance}` | One scope per value; duplicate values error in strict mode. |
| `mount(fn, target?)` | disposer | Runs `fn` in a new root and parents its result to `target`. |
| `root(fn)` | disposer, results of `fn` | `fn` receives the same disposer. |
| `cleanup(x)` | nothing | Accepts a function, Instance, connection, thread, or an object with `destroy`/`Destroy`/`disconnect`/`Disconnect`. Runs when the scope is destroyed or the effect re-runs. |
| `untrack(fn)`, `batch(fn)`, `read(v)` | | Read without tracking; defer effects until `fn` returns; `read` unwraps a value or getter. |

Also exported at this pin: `context`, `spring`, `action`, `changed`, `apply`, `step`, `version`. See [API and lifecycle](references/api-and-lifecycle.md).

## Example

```luau
local Vide = require(ReplicatedStorage.Packages.vide) -- use the project's mapped path
local create, source, derive, indexes, cleanup = Vide.create, Vide.source, Vide.derive, Vide.indexes, Vide.cleanup
local items = source({ "Sword", "Shield" })

local function Inventory()
	local open = source(true)
	local gui = create "ScreenGui" {
		create "TextButton" {
			Size = UDim2.fromOffset(200, 40),
			Text = derive(function() return `Bag ({#items()})` end), -- getter: reactive property
			Activated = function() open(not open()) end, -- event property: listener
		},
		create "Frame" {
			Position = UDim2.fromOffset(0, 48), Size = UDim2.fromOffset(200, 200), Visible = open,
			create "UIListLayout" {},
			indexes(items, function(name, i) return create "TextLabel" { Text = name, LayoutOrder = i } end),
		},
	}
	cleanup(gui) -- the mount disposer does not destroy the returned Instance
	return gui
end

local stop = Vide.mount(Inventory, Players.LocalPlayer.PlayerGui)
items({ "Sword", "Shield", "Potion" }) -- the list updates; call stop() to tear down
```

## Gotchas

- `mount`/`root` disposers only destroy the scope. An Instance you returned or created stays parented unless you `cleanup(instance)` it. Calling a disposer twice errors ("root already destroyed"), so clear your reference before you call it.
- `derive`, `effect`, `show`, `switch`, `indexes`, `values`, and reactive properties need a stable scope (a component body, `root`, `mount`, or a `show`/`switch`/`indexes` branch). Calling them inside an `effect`, `derive`, or reactive property function errors: "cannot create a new reactive scope inside another reactive scope".
- In strict mode (on unless compiled at `--!optimize 2`, which Roblox production uses), effects, `derive` and reactive properties run twice per update, and yielding inside them errors. Keep them pure and synchronous.
- Cleanups run in insertion order, and the first error stops the rest. Keep cleanup callbacks nonthrowing.
- Do not call `Vide.step()` on teardown. Its first call permanently disconnects the package-wide Heartbeat that drives `spring` and delayed scope teardown.
- A table Source notifies on every write of an unfrozen table, even the same one: after an in-place mutation, `s(s())` re-renders. Rewriting the same frozen table, or the same primitive, does nothing.
- `create "UIPadding"` and `create "UISizeConstraint"` are type errors only at 0.4.1, because its `Instances` type map omits them. At runtime `create` calls `Instance.new`. Use `Instance.new` under the owned root, or cast the class name. Don't edit vendor source.

## Read further

- More APIs, scope rules, `context`/`spring`/actions, and teardown recipes: read [API and lifecycle](references/api-and-lifecycle.md).
- Installing, restoring, or mapping the package, or Luau LSP setup: read [setup](references/setup.md).
- An analyzer error, a leaked UI, or a disposal error: read [troubleshooting](references/troubleshooting.md).
- A Vide story for UI Labs: use the `roblox-ui-labs` skill if it is installed. In short, the story module returns `{ vide = Vide, controls = {...}, story = function(props) return Component() end }`.
