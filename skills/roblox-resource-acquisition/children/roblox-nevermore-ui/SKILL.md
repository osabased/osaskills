---
name: roblox-nevermore-ui
description: Use the active project's exact pinned Blend, Rx, Brio, and Nevermore loader for declarative Luau UI, reactive flow, lifetime cleanup, and package imports. Preserve Bootstrapper application startup; exclude framework selection and dependency upgrades.
---

# Nevermore UI

Reviewed npm targets: Blend **12.50.1**, Rx **13.34.1**, Brio **14.37.1**, and loader **10.11.2**, from NevermoreEngine commit `7ab0297833aa73c193d8c20dc23332280439af7c`. Source reviewed 2026-10-05. The [resource contract](resource.yaml) owns identity and check profiles. This is advice-only guidance; the affected project's record owns current execution evidence.

## Before use

Resolve `PROJECT`, this installed `CHILD`, and the installed `roblox-resource-acquisition` `PARENT`. Read its `references/child-usage.md` once per task. Apply its guards, first-use freshness and repair rules; unresolved project identity is unknown state. Preserve the project's exact pins, import adapter and startup roles.

Reconciliation is conditional. Before ordinary use, require declaration `PASS` and the narrow record query `HEALTHY`:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/nevermore-ui.yaml"
```

`BLOCKED`/`UNKNOWN`, mismatched pins, verifier drift or hard defects enter parent reconciliation. A recurring safe workaround still activates parent repair diagnosis. A missing matching record requires adoption/reconciliation; bundle availability supplies no project trust or runtime proof.

## Common use and ownership

Require the project's shared Nevermore adapter, then select `Blend`, `Rx`, or `Brio`. Read [setup and imports](references/setup.md) when the mapping/adapter is unfamiliar. Package loading and replication belong to one root owner per runtime; Bootstrapper retains application Controller/Service init/start ownership. Component mounts borrow that loader.

`Blend.New(className)(props)` returns an observable; `:Subscribe(...)` activates an instance and returns a subscription owned with explicit `Destroy`. `Blend.mount(existingInstance, props)` returns a Maid for bindings and children; the caller still owns the existing root. `Blend.State(initial)` returns an owned ValueObject whose `.Value` is updated and whose `Destroy` releases it. For pipelines, use `observable:Pipe({ Rx.map(...), ... })`; explicitly own the resulting subscription.

Establish cleanup before activation. Keep producers, mounted views and owned state in separate phases when order matters: stop producers, dispose views, then release state. Janitor has no guaranteed entry order or best-effort continuation. Keep partial acquisitions reachable for rollback, set disposal guards before teardown, and re-check them after yields. A package subscription/mount call can throw before returning a cleanup handle; caller rollback does not prove cleanup of hidden package acquisitions.

Borrowed signals, promises, target frames and shared loader roots retain their provider's owner. `Rx.switchMap` disposes the previous inner subscription; it does not cancel unrelated work or a server request. A dead Brio cannot be reused: check `IsDead` before `GetValue`/`ToMaid`, and again after yielding. Register lifetime work on `brio:ToMaid()`.

## Security and completion

Keep privileged packages on the server. Preserve the root adapter's filtered replication (`skipStudioFastPath = true` when production-equivalent filtering is required in Studio); do not treat UI state or client events as server authority. Never bootstrap or destroy the shared loader per component.

Before completion, run the shared checker without `--declared`; require exit 0, JSON `status: PASS`, selector `12.50.1` and `lane: installed-integrity`. It checks the four exact reviewed direct npm packages; the project harness owns transitive resolution, adapter/mapping, analysis and builds. Mount/update/unmount, late callbacks, rendering and diagnostics require their own Studio evidence.

- For composition and preview mounts, read [Blend](references/blend.md).
- For pipelines, promises or signal adapters, read [Rx](references/rx.md).
- For value-owned work, read [Brio](references/brio.md).
- For loader failures, partial activation or stale callbacks, read [troubleshooting](references/troubleshooting.md).
