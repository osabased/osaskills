---
name: roblox-janitor-1-18-3
description: Use for Janitor 1.18.3 owned resource cleanup, indexed replacement and lifecycle diagnosis; exclude package selection/upgrades, Vide reactive scopes, generic project structure and trivial native disconnects.
---

# Janitor 1.18.3

Reviewed target: `1.18.3`, source reviewed 2026-10-03. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve `PROJECT` to the affected project root, `CHILD` to this installed directory, and `PARENT` from the available `roblox-resource-acquisition` skill location. Read its `references/child-usage.md` once per task and apply first-use freshness, guard and repair rules. Project resolution failure is unknown state and enters parent reconciliation.

Policy is conditional: declared identity and the narrow block query precede ordinary use; installed source integrity is checked before completion. Run:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/janitor.yaml"
```

Only `HEALTHY` permits ordinary use. `BLOCKED`/`UNKNOWN`, mismatched pins, verifier drift, hard defects or invalidated repair evidence enter the parent's reconciliation path. A recurring safe workaround still activates parent repair diagnosis.

## Common use

- Create `Janitor.new()` before fallible acquisition. Register native or LemonSignal connections with `owner:Add(connection, "Disconnect", optionalIndex)` immediately after acquisition. Register owned objects with their explicit `"Destroy"` method and callbacks with `true`. Replacing an index cleans its previous resource synchronously. Use `Remove(index)` for cleanup; `RemoveNoClean(index)` transfers ownership without cleanup.

Keep producer connections and consumer destruction in separate explicit phases. Detach the owner and set a disposed flag before teardown. Protect each top-level phase so a failed phase cannot skip the next one. Do not rely on order among entries in a Janitor or on retry after a throwing entry. Call a raw Janitor's `Destroy()` at most once; its successful implementation clears the table and metatable.

## Ownership and critical constraints

Create cleanup ownership before fallible acquisition and register resources immediately. Entry order is unspecified; a throwing entry can abort cleanup and leave `CurrentlyCleaning` set. Split producer disconnection and consumer destruction into explicit protected phases. Detach the owner and mark disposal before teardown; raw successful `Destroy` runs at most once.

The shared package can be replicated. Client and server require caches and cleanup owners are separate; a server Janitor cannot clean client UI. Use a client feature owner for UI and a server owner for privileged gameplay. Janitor creates no remote channel.

## Complete and read further

Run `python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT"`; require exit 0 and JSON `status: PASS` with this exact resource selector and the installed-integrity lane. Use the project's source/build checks for authored consumers and generated placement. These checks establish identity/static integration; runtime, rendering, input and clean-diagnostics claims require their own project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- When changing API usage, activation, partial acquisition or teardown, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
