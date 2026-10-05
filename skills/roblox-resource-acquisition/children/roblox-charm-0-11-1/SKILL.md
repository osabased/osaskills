---
name: roblox-charm-0-11-1
description: Use for littensy Charm 0.11.1 reactive application state, signals, computed values and owned effects; exclude UI rendering, discrete custom events, networking and dependency selection/upgrades.
---

# Charm 0.11.1

Reviewed target: `0.11.1`, source reviewed 2026-10-03. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve `PROJECT` to the affected project root, `CHILD` to this installed directory, and `PARENT` from the available `roblox-resource-acquisition` skill location. Read its `references/child-usage.md` once per task and apply first-use freshness, guard and repair rules. Project resolution failure is unknown state and enters parent reconciliation.

Policy is conditional: declared identity and the narrow block query precede ordinary use; installed source integrity is checked before completion. Run:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/charm.yaml"
```

Only `HEALTHY` permits ordinary use. `BLOCKED`/`UNKNOWN`, mismatched pins, verifier drift, hard defects or invalidated repair evidence enter the parent's reconciliation path. A recurring safe workaround still activates parent repair diagnosis.

## Common use

- Require the mapped Charm alias. `Charm.signal(initialValue, equals?)` returns separate getter and setter functions. Read with `getter()`; write with `setter(value)` or `setter(function(current) return nextValue end)`. Keep setters with the state owner and pass getters to consumers. `equals(current, incoming)` returning true rejects the new value and suppresses notification. Default equality is Luau value/reference inequality, not deep comparison.
- Derive read-only values with `computed(getter)`; it is lazy and cached. Use `effect(callback)` for synchronous reactions, or `listen(getter, callback)` for an initial callback plus changes. `subscribe(getter, callback)` skips the initial callback. Retain every returned disposer. Group related writes with `batch`; it defers effects until the outer batch ends and does not roll back writes on error.
- Vide and Charm have separate dependency tracking. Use an owned subscription to update a Vide source, with its disposer registered in the Vide scope before activation. Resolve the project's existing adapter when supplied. Call it inside a Vide scope and keep the bridge one-way. A raw Charm getter passed to a Vide property does not itself establish a Vide dependency. Nested effects created in listen/subscribe callbacks are untracked and require their own ownership.

## Ownership and critical constraints

Retain effect/subscription disposers before later fallible work. Initial callback failure does not guarantee full rollback. `listen`/`subscribe` callbacks are untracked, so nested effects require separate ownership. Keep reactive callbacks synchronous and non-yielding. Charm and Vide have separate tracking graphs; use the project's owned bridge inside a Vide scope.

The shared package may be replicated and required independently by client and server. Each runtime owns distinct state and require caches. Server Charm state does not replicate by itself; keep privileged rules and authoritative state on the server. Client screen/application state stays client-owned. Charm Sync is a separate resource, not part of this adoption; Blink remains the project networking compiler.

## Complete and read further

Run `python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT"`; require exit 0 and JSON `status: PASS` with this exact resource selector and the installed-integrity lane. Use the project's source/build checks for authored consumers and generated placement. These checks establish identity/static integration; runtime, rendering, input and clean-diagnostics claims require their own project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- When changing API usage, activation, partial acquisition or teardown, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
