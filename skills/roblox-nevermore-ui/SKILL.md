---
name: roblox-nevermore-ui
description: Nevermore (Quenty/NevermoreEngine) Blend, Rx and Brio UI libraries plus the Nevermore loader for Roblox Luau, pinned Blend 12.50.1, Rx 13.34.1, Brio 14.37.1, loader 10.11.2. Use when writing Blend.New, Blend.mount, Blend.State, Blend.Computed, Blend.OnEvent/OnChange/Children/Spring UI, Rx pipelines (Pipe, map, switchMap, combineLatest, fromSignal), Brio lifetimes, Nevermore UI Labs stories, or loader bootstrap and imports. Not for Vide UI or replacing Bootstrapper startup.
---

# Nevermore UI: Blend 12.50.1, Rx 13.34.1, Brio 14.37.1, loader 10.11.2

Pinned target: `@quenty/blend` `12.50.1` from NevermoreEngine commit `7ab0297833aa73c193d8c20dc23332280439af7c` (source reviewed 2026-10-05), with `@quenty/rx` 13.34.1, `@quenty/brio` 14.37.1 and `@quenty/loader` 10.11.2 as checked companions. [resource.yaml](resource.yaml) holds the exact identities. Upstream published patch releases on 2026-10-09; keep the project's pins unless the task is an upgrade.

## Check the pin

If the project pins these npm packages, confirm all four match the target. If the `roblox-resource-acquisition` skill is installed beside this one, run its checks per [child usage](../roblox-resource-acquisition/references/child-usage.md). If the parent, Python, or a project record is unavailable, read `package.json` and `package-lock.json` directly and say which checks were skipped. Stop only on a `FAIL`, `MISMATCH`, `BLOCKED` or `FAILED` result, an observed mismatch, or an explicit block.

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
