# Vide 0.4.1 API and lifecycle

Everything below was checked against `src/` at commit `5ed4c01`. Exports at this pin: `version`, `root`, `mount`, `create`, `apply`, `source`, `effect`, `derive`, `switch`, `show`, `indexes`, `values`, `cleanup`, `untrack`, `read`, `batch`, `context`, `spring`, `action`, `changed`, `step`, plus the flags `strict`, `defaults`, `defer_nested_properties`. There is no `destroy`, `unmount`, `Computed`, or `Value`. Reading or writing any other key on the module errors ("is not a valid member of vide").

## Scopes

- A **stable scope** is created by `root`, `mount`, and each `show`/`switch`/`indexes`/`values` branch. Component bodies run in one. `derive`, `effect`, `show`/`switch`/`indexes`/`values`, `context(value, fn)`, and reactive properties may only be created here.
- A **reactive scope** is the body of an `effect`, a `derive`, or a reactive property function. It re-runs when a Source it read changes. Creating any of the above inside it errors.
- `cleanup(x)` attaches to the current scope. In a stable scope it runs when the scope is destroyed. In a reactive scope it runs before the next re-run and on destroy. Outside any scope it errors.
- Destroying a scope runs its cleanups (in insertion order, stopping at the first error), then destroys the scopes it owns.

## Creating Instances

`create "Class" { props }` (also `create("Class")(props)`, or `create(existingInstance)(props)`, which clones the instance) returns the Instance. Props table rules (`apply.luau`):

| Key / value | Effect |
| --- | --- |
| `Name = value` | Sets the property once. |
| `Name = function` on a normal property | Creates an implicit effect: the property re-evaluates when the Sources it reads change. |
| `Event = function` on an `RBXScriptSignal` property | Connected as a listener after properties are set. |
| `[n] = Instance` | Parents the child. |
| `[n] = { ...props }` | A nested props table, applied to the same instance. |
| `[n] = function` returning an Instance or array | Dynamic children: they are reparented on change, and dropped children are set to `Parent = nil`. |
| `[n] = action(fn, priority?)` | `fn(instance)` runs after events connect and before `Parent`. |
| `Parent = value` or getter | Applied last, so the instance is fully built before it enters the DataModel. |

When `Vide.defaults` is true (the default), common GUI classes get default properties before your props are applied. Strict mode errors on duplicate property keys at the same nesting depth.

`Vide.apply(instance)(props)` applies the same rules to an existing instance.

## Reactive state

```luau
local count = source(0)
local doubled = derive(function() return count() * 2 end) -- inside a stable scope
effect(function()
	print(doubled())
	cleanup(function() print("before next run") end)
end)
count(5)
local snapshot = untrack(doubled) -- read without subscribing
batch(function() count(1); count(2) end) -- effects flush once, after the batch
```

`effect(fn, initial)` also supports an accumulator form: `fn(previous)` returns the next value.

## Dynamic children

- `show(cond, component, fallback?)`. `component(valueSource, present)` runs while `cond()` is truthy. It receives a Source holding the last truthy value, plus a `present` Source that becomes false when the branch is leaving.
- `switch(key) { [k] = function(present) return ... end }` builds the component mapped to the current key.
- `indexes(tbl, function(valueSource, key, present) ... end)` creates one scope per key. Value changes update `valueSource` without rebuilding. Use it for arrays.
- `values(tbl, function(value, keySource, present) ... end)` creates one scope per distinct value. Moving a value updates `keySource`. In strict mode, duplicate values error.
- Exit delay: a component may return `instance, seconds`. The scope then stays alive for that long after removal, with `present()` false, so you can animate out. The delay is driven by Vide's internal stepper; see the `step` gotcha.
- The returned getter yields an array or Instance and is meant for a number key in `create`. Array order is not guaranteed, so set `LayoutOrder` and use a layout's `SortOrder.LayoutOrder`.

## Context

```luau
local Theme = context("dark") -- default value
local function Label() return create "TextLabel" { Text = Theme() } end
local gui = Theme("light", function() return Label() end) -- Label sees "light"
```

`Ctx()` reads the nearest value set by an owning scope, falling back to the default. `Ctx(value, fn)` runs `fn` in a child scope and returns its result. It errors outside a Vide scope.

## Strict mode

`Vide.strict` is on when Vide is first required unless the code runs at `--!optimize 2`, and Roblox production code compiles at O2. In strict mode:

- Every effect, `derive`, and reactive property runs **twice** per update, so keep them pure: no counters, no remote calls, no `print`-driven logic.
- A yield inside a reactive scope errors ("attempt to yield in reactive scope").
- Duplicate property keys at one depth error, and so do duplicate values passed to `values()`.

Set `Vide.strict = false` only deliberately, for example in a benchmark.

## Animation and actions

- `spring(source, period = 1, dampingRatio = 1)` returns a getter that follows `source` with spring motion, plus a settings table. It is updated by Vide's Heartbeat stepper.
- `changed("Property", fn)` is an action. It calls `fn(currentValue)` immediately and on every property change, and disconnects through the scope's cleanup.
- `action(fn, priority?)` runs custom code on the instance during `create`. Use it for things like focus or measuring.

## Lifecycle and teardown

- `mount(component, target)` is `root` plus parenting the result. Its disposer ends the scope but **does not destroy or unparent the result**, so call `cleanup(instance)` on Instances you own. The Vide docs note that Instances only need `Parent = nil` to be freed. A connection from an Instance's event that references that same Instance keeps it alive, so destroy it or `cleanup` the connection.
- If a `root`/`mount` callback errors, its scope is destroyed (running the cleanups registered so far) and the error is rethrown. Register `cleanup` right after each acquisition.
- Calling a disposer twice errors. Use an idempotent owner:

```luau
local stop: (() -> ())? = Vide.mount(App, playerGui)
local function dispose()
	local s = stop
	stop = nil
	if s then s() end
end
```

- Stop producers (tasks, remote listeners) before disposing the UI that consumes them. Disposal detaches effects, so later Source writes no longer reach the destroyed UI.
- Requiring Vide in a running game connects one package-wide `RunService.Heartbeat` handler that drives springs and delayed teardown. `Vide.step(dt)` disconnects it on its first call, so call `step` manually every frame from then on. UI Labs 1.6.1 calls `step(0)` on the sandboxed copy of Vide it gives each story; that is fine there and wrong in gameplay code.

## Combining with other libraries

- **Charm:** Charm getters do not create Vide dependencies. Bridge them with a Vide Source fed by `Charm.subscribe`, and pass the unsubscribe function to `cleanup`. The `roblox-charm` skill has the recipe.
- **Janitor:** add a mount disposer as a callback (`janitor:Add(dispose, true)`), but keep `dispose` idempotent, because Janitor's cleanup order is unspecified.
