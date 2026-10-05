---
name: roblox-lemonsignal-2-0-0
description: Use for Data-Oriented-House LemonSignal 2.0.0 typed custom events, reconnectable subscriptions and owned callback lifecycle; exclude networking, signal selection/upgrades, Vide reactive state and simple native Roblox event subscriptions.
---

# LemonSignal 2.0.0

Reviewed target: `2.0.0`, source reviewed 2026-10-03. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve `PROJECT` to the affected project root, `CHILD` to this installed directory, and `PARENT` from the available `roblox-resource-acquisition` skill location. Read its `references/child-usage.md` once per task and apply first-use freshness, guard and repair rules. Project resolution failure is unknown state and enters parent reconciliation.

Policy is conditional: declared identity and the narrow block query precede ordinary use; installed source integrity is checked before completion. Run:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/lemonsignal.yaml"
```

Only `HEALTHY` permits ordinary use. `BLOCKED`/`UNKNOWN`, mismatched pins, verifier drift, hard defects or invalidated repair evidence enter the parent's reconciliation path. A recurring safe workaround still activates parent repair diagnosis.

## Common use

- Require the mapped LemonSignal wrapper. `LemonSignal.new()` creates a custom signal; annotate it as `LemonSignal.Signal<PayloadType>` when useful. `signal:Connect(callback)` returns a Connection; fire payloads through `signal:Fire(...)`. v2.0 accepts only the callback in Connect: older documentation’s extra bound arguments belong to older APIs. Use a closure for captured context.

Own each subscription with explicit `"Disconnect"` when adding it to Janitor. A borrowed signal belongs to its provider; destroy only signals this feature creates. Disconnect producers before consumer teardown; Janitor 1.18.3 has no entry order or best-effort continuation. Detach feature ownership and guard asynchronous callback results after disposal. Use `Once` for one callback, `Disconnect`/`Reconnect` for a retained handle, and `Destroy` for disconnecting the owned signal and its wrapped engine producer.

## Ownership and critical constraints

Own subscriptions with explicit `Disconnect`. Destroy only signals/wrappers the feature creates. Disconnect/Destroy does not cancel a callback already running. Destroy is reusable and does not permanently close the signal. A destroyed signal can leave `Wait` suspended: own and cancel the waiting task; a disposed flag suppresses stale results but does not release the suspended waiter. For a borrowed long-lived signal needing cancellation, use an explicitly owned `Connect` subscription; `Wait` hides its connection. Preserve the package's shared coroutine pool.

Shared package, independent client/server require state. Custom Fire delivers only in the current runtime; use client signals for menus and server signals for privileged rules. Never replicate a signal table as transport or trust a client-emitted event as a server-authoritative fact.

## Complete and read further

Run `python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT"`; require exit 0 and JSON `status: PASS` with this exact resource selector and the installed-integrity lane. Use the project's source/build checks for authored consumers and generated placement. These checks establish identity/static integration; runtime, rendering, input and clean-diagnostics claims require their own project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- When changing API usage, activation, partial acquisition or teardown, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
