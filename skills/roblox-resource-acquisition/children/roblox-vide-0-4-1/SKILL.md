---
name: roblox-vide-0-4-1
description: Use for Vide 0.4.1 Luau UI components, reactive state and scope cleanup at the adopted immutable commit; exclude UI Labs plugin management, dependency selection/upgrades and simple native Instance edits.
---

# Vide 0.4.1

Reviewed target: `5ed4c01940e6bd578fb83253cfbeda0a6c05177c`, source reviewed 2026-10-02. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve the affected project and installed `roblox-resource-acquisition` parent; read its `references/child-usage.md` once per task for commands, guards, first-use checks and repair. This child uses **conditional** reconciliation: require declaration `PASS` and record query `HEALTHY` before ordinary use; check installed integrity before completion. An unknown project/target or `BLOCKED`/`UNKNOWN` stops affected use.

## Common use

Resolve the mapped Vide wrapper and create components inside a Vide scope. `source(value)` is a getter/setter; function-valued GUI properties react to reads. For example, `create("TextLabel")({ Text = label })` takes a typed string getter `label`.

Mount gameplay roots with `mount(component, target)` and retain an idempotent owner wrapper. For UI Labs, return `{ vide = Vide, controls = ..., story = function(props) ... end }`; its callback returns the component inside UI Labs' existing scope.

## Ownership and critical constraints

Register owned root Instances immediately with `cleanup(instance)`. Cleanup runs in insertion order; a throwing callback can skip later entries. Detach the retained raw disposer before invoking it and keep owner cleanup idempotent. Stop feature producers before consumers. Preserve the package-global stepper: `step(0)` is not component teardown.

Map authored GUI components/package where clients can require them. Clients own PlayerGui mounts and cleanup. Server gameplay, purchases, persistence and client validation remain server-owned; replicated ModuleScripts do not share state between runtimes, and UI state is not authority.

## Complete and read further

Run the shared installed-integrity check; require exit 0, `status: PASS`, this exact selector and `lane: installed-integrity`. Project source/build checks cover authored consumers and mapping. Runtime, rendering, input and diagnostics claims need separate project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- For additional APIs, cross-library integration or partial-acquisition/teardown recipes, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
