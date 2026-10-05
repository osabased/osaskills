---
name: roblox-blink-0-18-9
description: Use for Blink 0.18.9 pesde CLI schema compilation, generated client/server/types placement and compiler diagnosis; exclude networking library selection/upgrades, UI events/previews and production receive activation without a validated size/rate budget.
---

# Blink 0.18.9

Reviewed target: `0.18.9`, source reviewed 2026-10-03. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve `PROJECT` to the affected project root, `CHILD` to this installed directory, and `PARENT` from the available `roblox-resource-acquisition` skill location. Read its `references/child-usage.md` once per task and apply first-use freshness, guard and repair rules. Project resolution failure is unknown state and enters parent reconciliation.

Policy is conditional: declared identity and the narrow block query precede ordinary use; installed source integrity is checked before completion. Run:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/blink.yaml"
```

Only `HEALTHY` permits ordinary use. `BLOCKED`/`UNKNOWN`, mismatched pins, verifier drift, hard defects or invalidated repair evidence enter the parent's reconciliation path. A recurring safe workaround still activates parent repair diagnosis.

## Common use

- Read the adopted schema and output placement. Execute the project-pinned alias with `pesde run blink -- --version`; expect Blink 0.18.9. Compile with `pesde run blink -- network/main` for a network/main.blink source, or substitute the adopted source basename. `pesde exec` is a different registry-execution command and is not the locked local alias.

Use option ServerOutput, ClientOutput and TypesOutput with quoted paths relative to the schema’s directory. Use a unique quoted RemoteScope per generated transport. Regenerate all outputs from the same schema/CLI; do not hand-edit generated modules. Example configuration: ServerOutput="../src/server/Network/Server.luau", ClientOutput="../src/client/Network/Client.luau", TypesOutput="../src/shared/Network/Types.luau", RemoteScope="GameName" (each line prefixed by `option `).

Keep an empty starter schema until server contracts are defined. Do not require generated Client/Server modules merely to verify generation: even an empty running server module starts remote listeners and Heartbeat work. For future endpoints, inspect the generated predecode receive path and establish byte/rate budgets before activation; handler-only validation cannot stop parser work.

## Ownership and critical constraints

This adoption owns compilation and generated placement. Keep generated Client/Server modules unrequired until runtime activation is authorized. Requiring even an empty server module activates listeners and scheduler work. Before untrusted receive activation, resolve the actual predecode byte/rate boundary; application-handler throttling cannot protect parsing.

The pesde CLI runs in the authoring/build environment with Lune, not in the engine. Generated Server belongs under ServerScriptService, Client in client-required replicated modules, and shared type output in the project’s shared module root. Replication alone does not execute a ModuleScript. Server remains authoritative for client requests; the compiler’s type serialization is not authorization.

## Complete and read further

Run `python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT"`; require exit 0 and JSON `status: PASS` with this exact resource selector and the installed-integrity lane. Use the project's source/build checks for authored consumers and generated placement. These checks establish identity/static integration; runtime, rendering, input and clean-diagnostics claims require their own project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- When changing API usage, activation, partial acquisition or teardown, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
