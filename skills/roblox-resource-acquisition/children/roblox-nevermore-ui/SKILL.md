---
name: roblox-nevermore-ui
description: Use the active project's exact pinned Blend, Rx, Brio, and Nevermore loader for declarative Luau UI, reactive flow, lifetime cleanup, and package imports. Preserve Bootstrapper application startup; exclude framework selection and dependency upgrades.
---

# Nevermore UI

Reviewed npm targets: Blend **12.50.1**, Rx **13.34.1**, Brio **14.37.1**, and loader **10.11.2**, from NevermoreEngine commit `7ab0297833aa73c193d8c20dc23332280439af7c`. Source reviewed 2026-10-05. The [resource contract](resource.yaml) owns identity and check profiles. This is advice-only guidance; the affected project's record owns current execution evidence.

## Before use

Resolve the affected project and installed `roblox-resource-acquisition` parent; read its `references/child-usage.md` once per task for commands, guards, first-use checks and repair. This child uses **conditional** reconciliation: require declaration `PASS` and record query `HEALTHY` before ordinary use; check installed integrity before completion. An unknown project/target or `BLOCKED`/`UNKNOWN` stops affected use.

## Common use and ownership

Require the project's shared Nevermore adapter, then select `Blend`, `Rx` or `Brio`. Read [setup and imports](references/setup.md) for an unfamiliar mapping/adapter. One root owner per runtime handles loading and replication; Bootstrapper retains Controller/Service init/start ownership. Components borrow that loader.

`Blend.New(className)(props)` returns an observable; `:Subscribe(...)` activates the instance and returns an explicitly owned `Destroy` subscription. `Blend.mount(existingInstance, props)` returns a Maid for bindings/children; the caller still owns the root. `Blend.State(initial)` returns an owned ValueObject: update `.Value`, release with `Destroy`. Compose with `observable:Pipe({ Rx.map(...), ... })` and own the resulting subscription.

Establish cleanup before activation. Where order matters, stop producers, dispose views, then release state in separate phases; Janitor provides neither entry order nor best-effort continuation. Keep partial acquisitions reachable, set disposal guards before teardown and re-check after yields. Activation can throw before returning a handle; caller rollback does not prove cleanup of hidden package acquisitions.

Borrowed signals, promises, frames and loader roots retain their provider's owner. `Rx.switchMap` disposes its previous inner subscription; it does not cancel unrelated work/server requests. A dead Brio cannot be reused. Check `IsDead` before `GetValue`/`ToMaid` and after yields; register lifetime work on `brio:ToMaid()`.

## Security and completion

Keep privileged packages server-side and preserve the root adapter's filtered replication (`skipStudioFastPath = true` for production-equivalent Studio filtering). Client UI state/events are not server authority. Never bootstrap or destroy the shared loader per component.

Before completion, run the shared installed-integrity check; require exit 0, `status: PASS`, selector `12.50.1` and `lane: installed-integrity`. It checks the four reviewed direct npm packages; the project harness owns transitive resolution, adapter/mapping, analysis and builds. Mount/update/unmount, late callbacks, rendering and diagnostics need Studio evidence.

- For composition and preview mounts, read [Blend](references/blend.md).
- For pipelines, promises or signal adapters, read [Rx](references/rx.md).
- For value-owned work, read [Brio](references/brio.md).
- For loader failures, partial activation or stale callbacks, read [troubleshooting](references/troubleshooting.md).
