---
name: roblox-vide-0-4-1
description: Use for Vide 0.4.1 Luau UI components, reactive state and scope cleanup at the adopted immutable commit; exclude UI Labs plugin management, dependency selection/upgrades and simple native Instance edits.
---

# Vide 0.4.1

Reviewed target: `5ed4c01940e6bd578fb83253cfbeda0a6c05177c`, source reviewed 2026-10-02. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve `PROJECT` to the affected project root, `CHILD` to this installed directory, and `PARENT` from the available `roblox-resource-acquisition` skill location. Read its `references/child-usage.md` once per task and apply first-use freshness, guard and repair rules. Project resolution failure is unknown state and enters parent reconciliation.

Policy is conditional: declared identity and the narrow block query precede ordinary use; installed source integrity is checked before completion. Run:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/vide.yaml"
```

Only `HEALTHY` permits ordinary use. `BLOCKED`/`UNKNOWN`, mismatched pins, verifier drift, hard defects or invalidated repair evidence enter the parent's reconciliation path. A recurring safe workaround still activates parent repair diagnosis.

## Common use

- Resolve the mapped Vide wrapper and create a component inside a Vide scope. `source(value)` is a getter/setter; function-valued GUI properties react to reads. Use `create("TextLabel")({ Text = label })`, with `label` a typed string getter, rather than guessing overloads.
- Register each owned root Instance with `cleanup(instance)`. Mount gameplay roots with `mount(component, target)` and retain an idempotent owner wrapper. For UI Labs return `{ vide = Vide, controls = ..., story = function(props) ... end }`; its callback returns the component within UI Labs' existing scope.

## Ownership and critical constraints

Register root Instances with `cleanup` immediately. Cleanup runs in insertion order and a throwing callback can prevent later entries. Detach the retained raw disposer before invoking it; keep owner cleanup idempotent. Stop feature-owned producers before consumers. Preserve the package-global stepper; `step(0)` is not component teardown.

Place authored GUI components in the project's client module root and map the package where clients can require it. The client owns PlayerGui mounts and cleanup. Server code must not mount client GUI or treat reactive UI state as authority. Server-side gameplay, purchases, persistence and validation remain server-owned; a shared ModuleScript does not share state across runtimes.

## Complete and read further

Run `python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT"`; require exit 0 and JSON `status: PASS` with this exact resource selector and the installed-integrity lane. Use the project's source/build checks for authored consumers and generated placement. These checks establish identity/static integration; runtime, rendering, input and clean-diagnostics claims require their own project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- When changing API usage, activation, partial acquisition or teardown, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
