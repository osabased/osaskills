---
name: roblox-janitor-1-18-3
description: Use for Janitor 1.18.3 owned resource cleanup, indexed replacement and lifecycle diagnosis; exclude package selection/upgrades, Vide reactive scopes, generic project structure and trivial native disconnects.
---

# Janitor 1.18.3

Reviewed target: `1.18.3`, source reviewed 2026-10-03. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve the affected project and installed `roblox-resource-acquisition` parent; read its `references/child-usage.md` once per task for commands, guards, first-use checks and repair. This child uses **conditional** reconciliation: require declaration `PASS` and record query `HEALTHY` before ordinary use; check installed integrity before completion. An unknown project/target or `BLOCKED`/`UNKNOWN` stops affected use.

## Common use

Create `Janitor.new()` before fallible acquisition and register resources immediately: `owner:Add(connection, "Disconnect", optionalIndex)` for native/LemonSignal connections, explicit `"Destroy"` for owned objects, and `true` for callbacks. Index replacement cleans the previous resource synchronously. `Remove(index)` cleans; `RemoveNoClean(index)` transfers ownership without cleanup.

## Ownership and critical constraints

Entry order is unspecified. A throwing entry can abort cleanup and leave `CurrentlyCleaning` set; retry is not a recovery guarantee. Disconnect producers and destroy consumers in separate protected phases so one failure cannot skip the next phase. Detach the owner and set a disposed flag before teardown. Call raw `Destroy()` at most once: success clears the table and metatable.

Client/server cleanup owners are separate. A server Janitor cannot clean client UI. Use client feature owners for UI and server owners for privileged gameplay; Janitor creates no remote channel.

## Complete and read further

Run the shared installed-integrity check; require exit 0, `status: PASS`, this exact selector and `lane: installed-integrity`. Project source/build checks cover authored consumers and mapping. Runtime, rendering, input and diagnostics claims need separate project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- For additional APIs, cross-library integration or partial-acquisition/teardown recipes, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
