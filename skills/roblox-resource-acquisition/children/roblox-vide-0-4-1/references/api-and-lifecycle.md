# API and lifecycle

## Mental model

A root establishes a reactive lifetime. Sources store values; property getter functions establish dependencies. A component constructs Instances while the scope is active, and the mount attaches returned roots to its target. Scope disposal removes effects and explicitly registered cleanup resources. Parenting children under one owned Instance gives a concrete destruction boundary.

## API used by this skill

This minimal Source excerpt is derived from the active project's strict reactive-state fixture; it is an API illustration within the advice-only boundary:

```luau
local title = Vide.source("Preview")
title("Updated")
assert(title() == "Updated")
```

Source-grounded exports used here are `version.major/minor/patch`, `source(initial)`, `create(className)(properties)`, `cleanup(Instance-or-callback)`, `mount(component, target?)`, `root(callback)`, `effect(callback)`, `read(value-or-getter)` and `step(dt)`. The root/mount disposer ends that scope; do not invent `Vide.destroy` or `unmount` exports. Keep Source props typed and scalar/getter semantics explicit.

## Lifecycle and cleanup

Initialization: Require in a running engine activates a package-global Heartbeat connection for stepping. This belongs to the package/host, not each component. `mount` establishes a root and returns its disposer; the feature owner stores it before later fallible work. Construction errors dispose resources already registered in that scope, so register cleanup immediately after creating an Instance.

Reuse: Render the same factory for each mount with that scope's state; keep external Sources owned by their caller. Do not share one mounted Instance between independent roots.

Cleanup/destruction: Vide 0.4.1 cleanup entries run in insertion order and a throwing entry can prevent later entries. Do not assume best-effort continuation or reverse order. Keep callbacks nonthrowing; orchestrate independent top-level teardown phases with protected calls and explicit producer-before-consumer order when needed. Raw disposal is not idempotent: detach the retained disposer before calling it so repeated/reentrant owner cleanup calls it once. Stop owned async producers first and use cancellation/invalidation for their pending callbacks; then dispose the UI scope. Disposal detaches effects, so subsequent external source writes cannot reach the disposed consumer.

`create` does not automatically own Instances. Register root cleanup and parent helpers/children under it. Avoid `step(0)` on component disposal: it disconnects the package-global stepper. UI Labs 1.6.1 applies that finalizer to its own sandboxed Vide instance during story teardown.

## Client/server placement

Place authored GUI components in the project's client module root and map the package where clients can require it. The client owns PlayerGui mounts and cleanup. Server code must not mount client GUI or treat reactive UI state as authority. Server-side gameplay, purchases, persistence and validation remain server-owned; a shared ModuleScript does not share state across runtimes.

## Limitations

- 0.4.1 is a GitHub prerelease with a stale pesde manifest version. Construction proof does not establish real device layout, actual input/focus, animation, startup or clean diagnostics. Current Luau LSP can report internal vendor diagnostics; authored strict checks and installed source integrity must remain enforced.
