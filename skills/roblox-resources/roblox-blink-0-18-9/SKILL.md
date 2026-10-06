---
name: roblox-blink-0-18-9
description: Use for Blink 0.18.9 pesde CLI schema compilation, generated client/server/types placement and compiler diagnosis; exclude networking library selection/upgrades, UI events/previews and production receive activation without a validated size/rate budget.
---

# Blink 0.18.9

Reviewed target: `0.18.9`, source reviewed 2026-10-03. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve the affected project and installed `roblox-resource-acquisition` parent; read its `references/child-usage.md` once per task for commands, guards, first-use checks and repair. This child uses **conditional** reconciliation: require declaration `PASS` and record query `HEALTHY` before ordinary use; check installed integrity before completion. An unknown project/target or `BLOCKED`/`UNKNOWN` stops affected use.

## Common use

Read the adopted schema/output placement. Run the pinned alias with `pesde run blink -- --version` (expect `0.18.9`), then `pesde run blink -- network/main` for `network/main.blink`, substituting the adopted basename. `pesde exec` executes from the registry; it is not the locked local alias.

Set quoted output paths relative to the schema directory and a unique `RemoteScope` for each transport:

```text
option ServerOutput="../src/server/Network/Server.luau"
option ClientOutput="../src/client/Network/Client.luau"
option TypesOutput="../src/shared/Network/Types.luau"
option RemoteScope="GameName"
```

Regenerate all outputs from the same schema/CLI instead of editing generated modules. Keep an empty starter schema until server contracts exist.

## Ownership and critical constraints

This adoption owns compilation/placement. Keep generated Client/Server modules unrequired until runtime activation is authorized: even an empty server module starts remote listeners and Heartbeat work. Before untrusted receive activation, inspect the actual predecode path and establish byte/rate budgets. Handler-only validation cannot protect parser work.

The pesde CLI runs with Lune in the build environment. Generated Server belongs in ServerScriptService, Client in client-required replicated modules, and shared types in the shared module root. Replication alone does not execute modules. Server validation remains authoritative; serialization types do not authorize client requests.

## Complete and read further

Run the shared installed-integrity check; require exit 0, `status: PASS`, this exact selector and `lane: installed-integrity`. Project source/build checks cover authored consumers and mapping. Runtime, rendering, input and diagnostics claims need separate project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- For additional APIs, cross-library integration or partial-acquisition/teardown recipes, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
