---
name: roblox-bootstrapper-1-2-2
description: Use for LDGerrits Bootstrapper 1.2.2 module discovery, lifecycle dispatch and owned scheduler bindings at the adopted commit; exclude generic project structure, UI components, dependency selection/upgrades and simple direct require calls.
---

# Bootstrapper 1.2.2

Reviewed target: `ff6700d32875dde5ef9e3625a159436ebd4dc3e9`, source reviewed 2026-10-02. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve `PROJECT` to the affected project root, `CHILD` to this installed directory, and `PARENT` from the available `roblox-resource-acquisition` skill location. Read its `references/child-usage.md` once per task and apply first-use freshness, guard and repair rules. Project resolution failure is unknown state and enters parent reconciliation.

Policy is conditional: declared identity and the narrow block query precede ordinary use; installed source integrity is checked before completion. Run:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/bootstrapper.yaml"
```

Only `HEALTHY` permits ordinary use. `BLOCKED`/`UNKNOWN`, mismatched pins, verifier drift, hard defects or invalidated repair evidence enter the parent's reconciliation path. A recurring safe workaround still activates parent repair diagnosis.

## Common use

- Resolve the package require and the startup root. Use a suffix predicate such as `Bootstrapper.byName("Controller$")`; keep helpers outside that discovery set.
- `loadDescendants(root, predicate)` returns a name-sorted module-table array and optional errors. Require each discovered ModuleScript to return a table. Check returned load errors before running phases.
- Use synchronous `run(modules, ".init", context)` then `run(modules, ".start", context)`, checking each returned error map. Prefix `.` means no self; `:` or an unprefixed name injects the module table. Context/other arguments follow it.
- Retain the original loaded array between phases. `run` returns only modules with that method that succeeded: chaining its init result can incorrectly drop a start-only module. Missing methods are skipped.

Strict Luau array types are invariant here: copy the returned LoadedModules into an array
typed `{ Instance | Bootstrapper.LoadedModule | Bootstrapper.ModulePath }` for dispatch.
Use the same widened list for both phases; preserve its module order and do not replace it
with run's filtered return. The project-owned adapter may re-export the needed upstream types.

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

Retain the original loaded array across phases: `run` returns a filtered success list. Inspect each returned error map and enforce the caller's phase barrier. Async/concurrent dispatch supplies no completion or cancellation handle. Discovery requires modules and can activate their top-level code; own partial acquisition and binding teardown explicitly.

The shared package can be replicated, but each runtime has its own require cache and module state.
Discover client controllers on clients and server services in ServerScriptService on servers.
Do not include packages, helpers, stories or every replicated module in a blanket startup scan.
Render-step/PreRender bindings are client-only. Keep privileged rules, persistence and client validation server-owned.

## Complete and read further

Run `python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT"`; require exit 0 and JSON `status: PASS` with this exact resource selector and the installed-integrity lane. Use the project's source/build checks for authored consumers and generated placement. These checks establish identity/static integration; runtime, rendering, input and clean-diagnostics claims require their own project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- When changing API usage, activation, partial acquisition or teardown, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
