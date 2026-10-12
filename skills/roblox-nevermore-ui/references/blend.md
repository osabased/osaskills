# Blend 12.50.2

Checked against `src/blend/src/Shared/Blend/Blend.lua` at commit `3286fd3`.

## Props table rules (`Blend.mount`, also used by `Blend.New`)

| Key | Value | Effect |
| --- | --- | --- |
| `"Name"` | a plain value | Set once. |
| `"Name"` | an Observable, `ValueObject`/`Blend.State`, Promise, `ValueBase` (e.g. `IntValue`), or anything with `:Observe()` | Subscribed; the property updates on each value. |
| `"Parent"` | any of the above | Applied after the other props. |
| `Blend.OnEvent "Event"` | function, `ValueObject`, `ValueBase` or signal | `Rx.fromSignal(instance.Event)`; each firing is passed to the handler. |
| `Blend.OnChange "Prop"` | handler, as above | Fires with the current value immediately, then on every change. |
| `Blend.Attached(fn(instance) -> cleanup?)` | `true` | Runs `fn` once on mount; a returned Maid task is cleaned up on unmount. |
| `Blend.Tags` | a list or observable of tags | Adds CollectionService tags. |
| a number, or `Blend.Children` | child values | See below. |

Children (`Blend.Children` docstring): an Instance, an array of them, an `Observable<Instance>`, a `ValueObject<Instance>`, a Signal or Promise of an Instance, a `Brio<Instance>` (lives as long as the Brio), an `Observable<Brio<Instance>>`, or a function `fn(parent)` whose result follows the same rules. Children created through Blend are cleaned up on unsubscribe.

## Building blocks

- `Blend.New "Class" { ... }` returns an Observable. Each subscription runs `Instance.new`, applies the class defaults from `BlendDefaultProps`, then `Blend.mount`s your props. Destroying the subscription destroys the Instance.
- `Blend.mount(existing, props)` returns a Maid. Destroying it releases the bindings and the children Blend created, but not `existing`.
- `Blend.State(default, checkType?)` is `ValueObject.new`. Use `.Value`, `:Observe()` and `:Destroy()`.
- `Blend.Computed(...states, fn)` uses `Rx.combineLatest` over the convertible arguments and maps them through `fn`. With a single argument it is `Rx.map(fn)`, and `Blend.Computed(fn)` alone emits `fn()` once.
- `Blend.Dynamic(...)` is like `Computed`, but `fn` may return an Observable or Promise, which is switched into.
- `Blend.Spring(source, speed, damper)` and `Blend.AccelTween(source, acceleration)` return animated Observables.
- `Blend.ComputedPairs(source, fn(key, value, innerMaid))` maps a table to `Observable<Brio<Instance>>` with cached per-key lifetimes.
- `Blend.Find "Class" { Name = "X", ... }` (`Name` is required) mounts props onto every existing child that matches the name and class, as they appear.
- `Blend.Single(observable)` keeps only one live Instance at a time. `Blend.Throttled` and `Blend.Shared` are optimization helpers.

## Ownership

- `Subscribe` activates immediately, so the subscription can't be stored until the call returns. Create and register caller-owned state and roots first.
- If a property assignment or a custom props function throws, `Blend.mount` never returns its Maid. Caller rollback can't reach those internal acquisitions; see [troubleshooting](troubleshooting.md).
- A mounted view borrows state supplied by its owner. Destroy the subscriptions or Maids first, then the feature-owned state. Never destroy a borrowed story target or the shared loader during mount cleanup.

## Stories (UI Labs)

A plain function story receives `target` and returns a cleanup:

```luau
local require = require(path.to.loader).bootstrapStory(script) -- or the project's shared adapter
local Blend = require("Blend")
local Maid = require("Maid")

return function(target)
	local maid = Maid.new()
	local state = maid:Add(Blend.State("hi"))
	maid:GiveTask(Blend.New "TextLabel" { Parent = target, Text = state }:Subscribe())
	return function() maid:DoCleaning() end
end
```

`loader.bootstrapStory(script)` is upstream's route for story files: it finds the enclosing `node_modules` root and returns a loader whose `require("Name")` resolves packages. If the project already has a shared edit-mode adapter, use that instead. A story can't return its cleanup after a construction error, so clean up partial work before rethrowing. For controls, use a UI Labs generic story (`render(props)` with `props.target`, `props.controls`, `props.subscribe`), and dispose both the control subscription and the UI subscription on unmount.

## Sources

- [Blend API](https://quenty.github.io/NevermoreEngine/api/Blend/)
- [Blend implementation at the reviewed commit](https://github.com/Quenty/NevermoreEngine/blob/3286fd397c9c42e7f29c8a881ac7dde12887e783/src/blend/src/Shared/Blend/Blend.lua)
- [UI Labs function stories](https://ui-labs.luau.page/docs/stories/function) and [generic stories](https://ui-labs.luau.page/docs/stories/advanced/generic)
