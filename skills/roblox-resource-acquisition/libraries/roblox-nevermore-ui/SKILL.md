---
name: roblox-nevermore-ui
description: Nevermore (Quenty/NevermoreEngine) Blend, Rx and Brio UI libraries plus the Nevermore loader for Roblox Luau, pinned Blend 12.50.2, Rx 13.34.2, Brio 14.37.2, loader 10.11.3. Use when writing Blend.New, Blend.mount, Blend.State, Blend.Computed, Blend.OnEvent/OnChange/Children/Spring UI, Rx pipelines (Pipe, map, switchMap, combineLatest, fromSignal), Brio lifetimes, Nevermore UI Labs stories, or loader bootstrap and imports. Not for Vide UI or replacing Bootstrapper startup.
---

# Nevermore UI: Blend 12.50.2, Rx 13.34.2, Brio 14.37.2, loader 10.11.3

Pinned target: `@quenty/blend` `12.50.2` from NevermoreEngine commit `3286fd397c9c42e7f29c8a881ac7dde12887e783` (source reviewed 2026-10-11), with `@quenty/rx` 13.34.2, `@quenty/brio` 14.37.2 and `@quenty/loader` 10.11.3 as checked companions. [resource.yaml](resource.yaml) holds the exact identities. Upstream published patch releases on 2026-10-09; keep the project's pins unless the task is an upgrade.

## Check the pin

Before relying on version-specific guidance, read the project's manifest and lock:

- `package.json` declares `@quenty/blend` `12.50.2`, `@quenty/rx` `13.34.2`, `@quenty/brio` `14.37.2` and `@quenty/loader` `10.11.3` as exact versions under `dependencies` (an alias such as `"npm:@quenty/blend@12.50.2"` counts).
- `package-lock.json` has a `node_modules/<name>` entry for each, at the same version and resolved from `https://registry.npmjs.org`.

If they show another version, tell the user, keep the project's pin, use only API you can confirm at that version, and stop where the task depends on behavior that may differ. If the user wants this skill's version instead, upgrade through the `roblox-resource-acquisition` skill. If the project doesn't declare these packages, this skill is advice only. Stop on a blocked use noted in the project's `CLAUDE.md`. Say what you checked; reading the manifest is not a runtime test.

## Core API

| Call | Returns | Notes |
| --- | --- | --- |
| `Blend.New "Class" { props }` | `Observable<Instance>` | Nothing is created until you `:Subscribe()`. Each subscription creates an Instance, and destroying that subscription destroys the Instance. |
| `Blend.mount(instance, props)` | `Maid` | Applies props to an existing Instance. Destroying the Maid removes the bindings and children but keeps the root. |
| `Blend.State(initial)` | `ValueObject` | Read or write `.Value`; call `:Destroy()` when done. Can be passed directly as a property. |
| `Blend.Computed(a, b, ..., fn)` | Observable | Recomputes from any mix of states, observables and plain values. |
| `[Blend.OnEvent "Activated"] = fn` | | Connects an event. The handler can also be a `ValueObject`, `ValueBase` or signal. |
| `[Blend.OnChange "Text"] = fn` | | Fires immediately and on every property change. |
| Number keys or `[Blend.Children] = {...}` | | Children: Instances, `Blend.New` observables, states, Brios or arrays. |
| `Blend.Spring(source, speed, damper)` | Observable | Animates a numeric source. |
| `obs:Pipe({ Rx.map(f), Rx.where(p), Rx.switchMap(g) })` | Observable | Rx uses `where`; there is no `filter`. |
| `obs:Subscribe(onNext?, onFail?, onComplete?)` | `Subscription` | Runs immediately. `:Destroy()` (or `:Disconnect()`) stops it. |
| `Brio.new(...)`, `brio:IsDead()`, `brio:GetValue()`, `brio:ToMaid()`, `brio:Destroy()`/`Kill()` | | A value with a lifetime. `GetValue` and `ToMaid` error once the Brio is dead. |

## Example

```luau
local Blend = Nevermore.Blend -- from the project's shared adapter (see setup)

local clicks = Blend.State(0)
local subscription = Blend.New "ScreenGui" {
	Parent = Players.LocalPlayer.PlayerGui,
	Blend.New "TextButton" {
		Size = UDim2.fromOffset(200, 50),
		Text = Blend.Computed(clicks, function(n) return `Clicks: {n}` end),
		[Blend.OnEvent "Activated"] = function() clicks.Value += 1 end,
		[Blend.OnChange "AbsoluteSize"] = function(size) print("size", size) end,
	},
}:Subscribe()

-- teardown: views first, then the state they borrow
subscription:Destroy()
clicks:Destroy()
```

## Gotchas

- `Blend.New` is lazy: forget `:Subscribe()` and nothing appears. Keep every subscription and Maid, and destroy each exactly once.
- `Subscribe` and `Blend.mount` run immediately. If a property or callback throws partway, you get no handle, and anything already created inside can't be reached. Create and register your own state first, and validate risky inputs before mounting.
- `Rx.switchMap` disposes the previous inner subscription. It doesn't cancel work already sent elsewhere (a server request, a spawned task). Guard late results.
- A Brio is dead forever after `Destroy`. Check `IsDead()` before `GetValue`/`ToMaid` and again after every yield. Each `ToMaid()` call creates a new Maid.
- `Rx.fromPromise` requires a Nevermore Promise. Janitor's transitive `evaera/promise` is a different implementation.
- Bootstrap the loader once per package root and runtime, in the root owner. Components borrow it. Don't call `bootstrapGame` or destroy the loader per component. `Loader:Destroy()` removes the metatable, so call it once.

## Read further

- Blend composition, children rules, `Attached`, `Find`, `ComputedPairs`, `Spring` and story mounts: read [Blend](references/blend.md).
- Rx operators, subscription lifetime, and signal or Promise adapters: read [Rx](references/rx.md).
- Brio lifetimes and value-owned work: read [Brio](references/brio.md).
- npm restore, the shared adapter, `bootstrapGame`/`bootstrapPlugin`/`bootstrapStory` and replication: read [setup](references/setup.md).
- Missing loader links, server packages visible on the client, duplicate UI or construction failures: read [troubleshooting](references/troubleshooting.md).
- Wrong or missing guidance at this pin: report it with the smallest reproduction and the exact proposed fix. Fix it in the `roblox-resource-acquisition` catalog, not here, because re-cloning overwrites local edits.
