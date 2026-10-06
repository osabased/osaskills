---
name: roblox-charm-0-11-1
description: Use for littensy Charm 0.11.1 reactive application state, signals, computed values and owned effects; exclude UI rendering, discrete custom events, networking and dependency selection/upgrades.
---

# Charm 0.11.1

Reviewed target: `0.11.1`, source reviewed 2026-10-03. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve the affected project and installed `roblox-resource-acquisition` parent; read its `references/child-usage.md` once per task for commands, guards, first-use checks and repair. This child uses **conditional** reconciliation: require declaration `PASS` and record query `HEALTHY` before ordinary use; check installed integrity before completion. An unknown project/target or `BLOCKED`/`UNKNOWN` stops affected use.

## Common use

- Require the mapped Charm alias. `Charm.signal(initialValue, equals?)` returns separate getter/setter functions. Read with `getter()`; write with `setter(value)` or `setter(function(current) return nextValue end)`. Keep setters with the state owner and pass getters to consumers. `equals(current, incoming)` returning true rejects the value and notification; default equality compares Luau values/references, not deep contents.
- `computed(getter)` is lazy and cached. `effect(callback)` reacts synchronously; `listen(getter, callback)` calls initially and on changes; `subscribe(getter, callback)` skips the initial call. Retain their disposers. `batch` defers effects until the outer batch ends; it does not roll back writes on error.
- Charm and Vide track dependencies separately. Use the project's one-way adapter inside a Vide scope: an owned subscription updates a Vide source, and its disposer belongs to that scope before activation. Passing a raw Charm getter to a Vide property does not establish a Vide dependency.

## Ownership and critical constraints

Retain disposers before later fallible work; an initial callback failure does not guarantee rollback. Keep reactive callbacks synchronous and non-yielding. `listen`/`subscribe` callbacks are untracked, so nested effects require separate ownership.

Client/server runtimes own separate state and require caches. Server Charm state does not replicate itself. Keep privileged rules/server state authoritative and client UI state client-owned. Charm Sync is a separate resource; preserve the project's adopted networking choice.

## Complete and read further

Run the shared installed-integrity check; require exit 0, `status: PASS`, this exact selector and `lane: installed-integrity`. Project source/build checks cover authored consumers and mapping. Runtime, rendering, input and diagnostics claims need separate project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- For additional APIs, cross-library integration or partial-acquisition/teardown recipes, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
