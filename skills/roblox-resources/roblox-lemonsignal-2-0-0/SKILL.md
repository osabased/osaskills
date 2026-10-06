---
name: roblox-lemonsignal-2-0-0
description: Use for Data-Oriented-House LemonSignal 2.0.0 typed custom events, reconnectable subscriptions and owned callback lifecycle; exclude networking, signal selection/upgrades, Vide reactive state and simple native Roblox event subscriptions.
---

# LemonSignal 2.0.0

Reviewed target: `2.0.0`, source reviewed 2026-10-03. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve the affected project and installed `roblox-resource-acquisition` parent; read its `references/child-usage.md` once per task for commands, guards, first-use checks and repair. This child uses **conditional** reconciliation: require declaration `PASS` and record query `HEALTHY` before ordinary use; check installed integrity before completion. An unknown project/target or `BLOCKED`/`UNKNOWN` stops affected use.

## Common use

Require the mapped LemonSignal wrapper. `LemonSignal.new()` creates a custom signal; `LemonSignal.Signal<PayloadType>` supplies its type. `signal:Connect(callback)` returns a Connection; `signal:Fire(...)` emits payloads. Version 2 accepts only the callback in `Connect`; capture context with a closure instead of older bound-argument APIs.

Use `Once` for one callback, `Disconnect`/`Reconnect` for a retained handle, and `Destroy` to disconnect an owned signal and its wrapped engine producer. Destroy is reusable; it does not permanently close the signal.

## Ownership and critical constraints

Own subscriptions with explicit `"Disconnect"` when adding them to Janitor. Destroy only signals/wrappers this feature created. Disconnect producers before consumers; Janitor 1.18.3 provides neither entry order nor best-effort continuation. Detach feature ownership and guard late callback results after disposal: disconnection does not cancel a callback already running.

Destroy can leave `Wait` suspended. Own/cancel the waiting task; a disposed flag alone cannot release it. For cancellable borrowing of a long-lived signal, prefer an owned `Connect` subscription because `Wait` hides its connection. Preserve the shared coroutine pool.

`Fire` delivers within the current runtime; client/server require state is independent. Signal tables are not network transport, and client events are not server-authoritative facts.

## Complete and read further

Run the shared installed-integrity check; require exit 0, `status: PASS`, this exact selector and `lane: installed-integrity`. Project source/build checks cover authored consumers and mapping. Runtime, rendering, input and diagnostics claims need separate project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- For additional APIs, cross-library integration or partial-acquisition/teardown recipes, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
