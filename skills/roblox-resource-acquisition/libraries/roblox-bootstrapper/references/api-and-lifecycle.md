# Bootstrapper 1.2.2 API and lifecycle

Everything below was checked against `src/init.luau` at commit `ff6700d` (header `--v1.2.2`).

## Loading

- `loadChildren(parent, predicate?)` and `loadDescendants(parent, predicate?)` pass `parent:GetChildren()` or `parent:GetDescendants()` to the same loader. A non-ModuleScript Instance in the list (for example a Folder) has its direct ModuleScript children added too. Duplicates are skipped.
- Modules are sorted by `Name`; equal names are sorted by `GetFullName()`. Alphabetical order is deterministic, but it is not a dependency order. When `B` needs `A` first, use `loadSequence` or require `A` explicitly inside `B.init`.
- Each module is `require`d inside `pcall`. A require error, or a module that doesn't return a table, goes into `errors[name]` and is re-thrown asynchronously (`task.spawn(error, ...)`), so it shows in Output even though you handled the map.
- The errors map is keyed by ModuleScript `Name` (or the string path). Duplicate names overwrite each other, so keep startup module names unique.
- `loadSequence(list)` keeps the list's order and accepts ModuleScripts, Folders (children sorted by name), string paths for `require`, and already-loaded tables.

## Dispatch

| Mode | Runs | Result |
| --- | --- | --- |
| `run` | In order, on the calling thread. A yielding method delays the rest. | Succeeded modules, plus an errors map keyed by name. |
| `runAsync` | In order, in one spawned thread. | Nothing. |
| `runConcurrent` | Every module in its own `task.spawn`. | Nothing. |

Every call is wrapped in `xpcall`. A failing module is recorded and the sequence continues. Bootstrapper has no dependency graph, readiness flags, or automatic `init`/`start` names, and does no teardown or rollback of a module's side effects.

## Bindings

- `bindTo(modules, method, event)` filters the modules that have `method`, then connects one runner that calls them in order with the event's arguments. `event` can be an `RBXScriptSignal`, a custom signal with `Connect`/`connect`, or a subscribe function that returns a task. The returned cleanup disconnects the connection, or destroys, disconnects or calls the task.
- If no module has the method, the cleanup is a no-op.
- A runner error in one module is reported and does not stop the others for that frame.
- `bindToInterval(m, method, seconds, signal?)` checks `os.clock()` on each `signal` (Heartbeat by default) and fires on the `start + n * seconds` schedule, passing the real elapsed `dt`. `RunService.Stepped` is rejected; use `PreSimulation`.
- Cleanups only disconnect. They don't cancel work your methods spawned. Store each cleanup with its feature owner, call it once, and stop producers before destroying what they feed.

## Placement

Each runtime has its own require cache. Load client controllers on the client and server services from `ServerScriptService` on the server. `bindToRenderStep` and `bindToPreRender` assert `RunService:IsClient()`.
