---
name: roblox-janitor
description: Janitor (howmanysmall/Janitor) cleanup library for Roblox Luau, pinned 1.18.3. Use when code calls Janitor.new, janitor:Add, AddObject, Remove, RemoveNoClean, Get, Cleanup, Destroy or LinkToInstance, or when fixing leaked connections, instances, threads or callbacks in a Janitor-based project. Not for Vide scope cleanup.
---

# Janitor 1.18.3

Pinned target: `1.18.3` (source reviewed 2026-10-03). [resource.yaml](resource.yaml) holds the exact identity.

## Check the pin

If the project pins Janitor, confirm it matches the target. If the `roblox-resource-acquisition` skill is available (two folders up when this skill sits in its `libraries/` folder, otherwise beside this one), run its checks per [child usage](../../references/child-usage.md). If the parent or Python is unavailable, read the project's manifest/lock directly and say which checks were skipped. On a `FAIL` result or an observed mismatch, tell the user and keep the project's pin; continue with API you can confirm at the project's version, and stop only where the task depends on version-specific behavior. Stop on a blocked use noted in the project's `CLAUDE.md`.

## Core API

| Call | Returns | Notes |
| --- | --- | --- |
| `Janitor.new()` | Janitor | An empty cleanup table. |
| `j:Add(object, method?, index?)` | `object` | Default `method`: `true` (call it) for functions and threads, `"Disconnect"` for `RBXScriptConnection`, `"Destroy"` for everything else. A string names the method to call. |
| `j:Add(..., index)` | `object` | If `index` is already used, the previous object is cleaned up **immediately**, then replaced. |
| `j:AddObject(Class, method?, index?, ...)` | instance | `Add(Class.new(...), method, index)`. |
| `j:Get(index)` / `j:GetAll()` | object / table | Looks up indexed objects. |
| `j:Remove(index)` | `j` | Cleans up the indexed object and forgets it. `RemoveList(...)` does the same for several. |
| `j:RemoveNoClean(index)` | `j` | Forgets it without cleaning up. `RemoveListNoClean(...)` does the same for several. |
| `j:Cleanup()` or `j()` | nothing | Cleans up everything. The Janitor stays usable. |
| `j:Destroy()` | nothing | `Cleanup`, then clears the table and removes its metatable, so the Janitor is unusable afterwards. |
| `j:LinkToInstance(inst, allowMultiple?)` | `RBXScriptConnection` | Calls `Cleanup` when `inst.Destroying` fires. Disconnect the returned connection to unlink. |
| `j:LinkToInstances(...)` | new Janitor | Links several Instances. Clean the returned Janitor to unlink them. |

`AddPromise(promise, index?)` also exists; it cancels a pending Promise on cleanup.

## Example

```luau
local Janitor = require(ReplicatedStorage.Packages.Janitor) -- use the project's mapped path

local janitor = Janitor.new()
local part = janitor:Add(Instance.new("Part")) -- "Destroy"; Add returns the object
janitor:Add(part.Touched:Connect(onTouched)) -- RBXScriptConnection -> "Disconnect"
janitor:Add(function() print("cleaned") end) -- function -> called
janitor:Add(customSignal:Connect(onFired), "Disconnect") -- custom objects: name the method
janitor:Add(task.delay(5, respawn), true, "Respawn") -- thread, indexed
janitor:Add(task.delay(10, respawn), true, "Respawn") -- cancels the 5 s thread first
janitor:LinkToInstance(character) -- cleanup runs when the character is destroyed

janitor:Cleanup() -- or janitor(); still reusable afterwards
janitor:Destroy() -- final: no method works after this
```

## Gotchas

- Name the method for custom objects. A LemonSignal or other custom connection is a table, so it defaults to `"Destroy"`. `Add` only warns ("doesn't have method"), and cleanup then **silently skips it**. Use `janitor:Add(conn, "Disconnect")`.
- Cleanup order is unspecified (`next()` order). If one entry throws, the rest are skipped, and the Janitor stays marked as cleaning: every later `Cleanup()` and `Destroy()` call silently does nothing. Keep callbacks nonthrowing, and `pcall` risky ones.
- When order matters (stop producers, then destroy consumers), use separate Janitors or explicit steps rather than one Janitor.
- `Destroy()` is single-use; after it, any method call errors. Guard your own teardown with a `disposed` flag if it can run twice.
- `LinkToInstance` reacts to `Destroying` only, not to reparenting to `nil`.
- Janitor doesn't cancel work it doesn't own. Add threads you spawn (`janitor:Add(task.spawn(...), true)`), or check a disposed flag in their callbacks.

## Read further

- Ownership patterns, partial setup rollback, threads and Promises: read [API and lifecycle](references/api-and-lifecycle.md).
- Installing, restoring or mapping the package: read [setup](references/setup.md).
- A leak, a "doesn't have method" warning, or cleanup that stopped working: read [troubleshooting](references/troubleshooting.md).
