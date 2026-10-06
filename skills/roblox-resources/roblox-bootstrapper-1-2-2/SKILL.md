---
name: roblox-bootstrapper-1-2-2
description: Use for LDGerrits Bootstrapper 1.2.2 module discovery, lifecycle dispatch and owned scheduler bindings at the adopted commit; exclude generic project structure, UI components, dependency selection/upgrades and simple direct require calls.
---

# Bootstrapper 1.2.2

Reviewed target: `ff6700d32875dde5ef9e3625a159436ebd4dc3e9`, source reviewed 2026-10-02. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve the affected project and installed `roblox-resource-acquisition` parent; read its `references/child-usage.md` once per task for commands, guards, first-use checks and repair. This child uses **conditional** reconciliation: require declaration `PASS` and record query `HEALTHY` before ordinary use; check installed integrity before completion. An unknown project/target or `BLOCKED`/`UNKNOWN` stops affected use.

## Common use

Resolve the package require and startup root. Discover only intended startup modules, e.g. `Bootstrapper.byName("Controller$")`, excluding helpers/packages/stories. `loadDescendants(root, predicate)` returns a name-sorted array of module tables plus optional errors. Each discovered ModuleScript must return a table; check load errors before dispatch.

Use synchronous `.init` then `.start`, checking each error map to enforce phase barriers. Prefix `.` omits self; `:` or an unprefixed name injects the module table before other arguments. Missing methods are skipped. `run` returns only successful modules with that method: retain the original loaded array so a start-only module survives init.

Luau arrays are invariant here. Widen LoadedModules into the dispatch union without changing order; the project adapter may re-export upstream types:

```luau
local modules, loadErrors = Bootstrapper.loadDescendants(root, Bootstrapper.byName("Controller$"))
assert(not loadErrors, "Module loading failed")
local dispatchModules: { Instance | Bootstrapper.LoadedModule | Bootstrapper.ModulePath } = {}
for _, module in modules do
	table.insert(dispatchModules, module)
end
for _, phase in { ".init", ".start" } do
	local _, errors = Bootstrapper.run(dispatchModules, phase, owner)
	assert(not errors, "Startup phase failed")
end
```

## Ownership and critical constraints

Discovery requires modules and can activate top-level code: own partial acquisition and binding teardown. Async/concurrent dispatch supplies no completion or cancellation handle.

Client/server require caches and module state are independent. Discover client controllers on clients and server services in ServerScriptService. Render-step/PreRender bindings are client-only. Keep privileged rules, persistence and client validation server-owned.

## Complete and read further

Run the shared installed-integrity check; require exit 0, `status: PASS`, this exact selector and `lane: installed-integrity`. Project source/build checks cover authored consumers and mapping. Runtime, rendering, input and diagnostics claims need separate project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- For additional APIs, cross-library integration or partial-acquisition/teardown recipes, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
