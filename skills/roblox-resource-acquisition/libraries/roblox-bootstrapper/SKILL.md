---
name: roblox-bootstrapper
description: Bootstrapper (LDGerrits/Bootstrapper) module loader and scheduler for Roblox Luau, pinned 1.2.2. Use when loading Controller/Service modules with Bootstrapper.loadChildren, loadDescendants, loadSequence or byName, running init/start phases with Bootstrapper.run, runAsync or runConcurrent, or binding modules to Heartbeat, RenderStep, intervals or signals with bindTo*. Not for general project folder layout.
---

# Bootstrapper 1.2.2

Pinned target: commit `ff6700d32875dde5ef9e3625a159436ebd4dc3e9` (tag v1.2.2, source reviewed 2026-10-02). [resource.yaml](resource.yaml) holds the exact identity.

## Check the pin

If the project pins Bootstrapper, confirm it matches the target. If the `roblox-resource-acquisition` skill is available, load it and run the checks its `references/child-usage.md` describes. If the parent or Python is unavailable, read the project's manifest/lock directly and say which checks were skipped. On a `FAIL` result or an observed mismatch, tell the user and keep the project's pin; continue with API you can confirm at the project's version, and stop only where the task depends on version-specific behavior. Stop on a blocked use noted in the project's `CLAUDE.md`.

## Core API

| Call | Returns | Notes |
| --- | --- | --- |
| `byName(pattern)` | predicate | Uses a Lua pattern (`"Controller$"`), not a glob or regex. |
| `loadChildren(parent, predicate?)` | `modules, errors?` | Requires matching child ModuleScripts, sorted by `Name` (ties broken by full path). |
| `loadDescendants(parent, predicate?)` | `modules, errors?` | The same, over all descendants. |
| `loadSequence(list)` | `modules, errors?` | Keeps your order. `list` may hold ModuleScripts, folders, string paths or loaded tables. |
| `run(modules, method, ...)` | `succeeded, errors?` | Sequential and synchronous. Keeps going after a failing module. Returns only the modules that had the method and succeeded. |
| `runAsync(modules, method, ...)` | nothing | The same order, in one background thread. Gives no completion or error result. |
| `runConcurrent(modules, method, ...)` | nothing | One thread per module. Gives no completion or error result. |
| `bindTo(modules, method, signalOrSubscribe)` | cleanup | Takes an `RBXScriptSignal`, a custom signal with `Connect`, or `function(callback) return task end`. |
| `bindToHeartbeat`, `bindToPostSimulation`, `bindToPreAnimation` | cleanup | Connects the method sequence to that `RunService` event. |
| `bindToPreSimulation(m, method, frequency?)` | cleanup | With an `Enum.StepFrequency`, uses `BindToSimulation`. |
| `bindToRenderStep(m, method, priority?)`, `bindToPreRender(m, method)` | cleanup | Client only (asserts). A numeric `priority` uses `BindToRenderStep`. |
| `bindToInterval(m, method, seconds, signal?)` | cleanup | Fires on a fixed schedule without drift, on Heartbeat by default, and passes the elapsed `dt`. |

Method strings: `".init"` calls `module.init(...)`; `":init"` or `"init"` calls `module.init(module, ...)`. Modules without the method are skipped. Each module must return a table.

## Example

```luau
local Bootstrapper = require(ReplicatedStorage.Packages.Bootstrapper) -- use the project's adapter path

local modules, loadErrors = Bootstrapper.loadDescendants(script.Parent.Controllers, Bootstrapper.byName("Controller$"))
assert(not loadErrors, "controller load failed")

-- Pass the ORIGINAL list to each phase, and stop if a phase had errors.
for _, phase in { ":init", ":start" } do
	local _, errors = Bootstrapper.run(modules :: { any }, phase)
	assert(not errors, `startup phase {phase} failed`)
end

local stopUpdate = Bootstrapper.bindToHeartbeat(modules :: { any }, ":update") -- update(self, dt)
-- on shutdown: stopUpdate()
```

## Gotchas

- `run` doesn't stop at errors. A failing `init` still lets later modules run, and `start` would run too if you didn't check `errors`. Check the errors map after every phase.
- `run` returns only the modules that succeeded **and** had the method. Feeding that result into the next phase drops start-only modules, so reuse the original list.
- Loading requires the modules, so their top-level code runs during discovery. Always pass a predicate to `loadDescendants`; an unfiltered scan also requires helpers, stories and nested modules. Keep side effects in `init`/`start`.
- `runAsync`/`runConcurrent` give no completion, error result or cancellation. Use `run` wherever a later step depends on earlier ones.
- Errors are reported twice: they are returned in the map **and** re-thrown asynchronously to Output. Inspecting the map doesn't suppress the Output.
- Under Luau's new solver, a loaded array (`{ LoadedModule }`) doesn't match the `{ Instance | ModulePath | LoadedModule }` parameter, because arrays are invariant. Cast it (`modules :: { any }`) or copy it into an array of the union type.

## Read further

- Binding cleanup, ordering rules, error keys and full signatures: read [API and lifecycle](references/api-and-lifecycle.md).
- Installing, restoring, or the wrapper-casing workaround: read [setup](references/setup.md).
- Modules that don't start, missing modules, or work that runs after teardown: read [troubleshooting](references/troubleshooting.md).
