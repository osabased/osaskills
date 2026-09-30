---
name: roblox-goodsignal-connections
description: Use pinned GoodSignal for feature-owned in-process event callbacks and explicit disconnection; prefer direct calls for a single local recipient.
---

# GoodSignal connections

Use GoodSignal for feature-owned in-process callbacks. Guidance targets commit **99497c8cd6e5b50c5f4f12796d4ebc3e7dbf9d1f** in `stravant/goodsignal` (source reviewed **2026-09-30**). Resource verification: **unverified**. This worked example has no independent child behavioral or Studio claim.

## Use when

- An authorized project needs multiple local subscribers with explicit connection ownership.

## Do not use when

- A direct call suffices, or communication must cross the client/server network boundary.

## Prerequisites and installation

1. Resolve the project-owned target and installation before using the common path.

Resolve the active project first. Its owner must select the canonical commit; this example supplies no adoption authority. Preserve the upstream MIT license. For this fixture, place the inspected `src/init.lua` as `ReplicatedStorage.Packages.GoodSignal`, with a project manifest/header naming the exact commit. A package version with the same name is not automatically the same source state. Adapt the fixture's require path to the project's selected installation and rerun checks after that adaptation.

## On-demand maintenance

- Promotion guard: Check the sibling `.skill-maintenance/<skill-directory-name>.json`; ordinary use waits while it exists.
- Freshness triggers: For a relevant current claim, adoption/upgrade, source drift, recurring workaround or reusable defect, invoke `roblox-resource-acquisition` for the affected target and read its `references/on-demand-maintenance.md`.
- Target and economy: Preserve the project's selected commit and owner authority. Healthy immutable-target use needs no unrelated latest-release survey. Changed pins or practices return to the owner.

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode for guessing, bypassed instructions, repeated rediscovery or an undocumented workaround likely to recur; a harmless task-local adjustment is not an interrupt.
- Hard defect: Stop dependent work when correctness, security, canonical identity, selected version or verification is unreliable, and enter parent reconciliation and repair.
- Soft defect: If a workaround is safe and reversible, immediate work may continue, but invoke parent repair diagnosis and surface the reproduction, workaround and durable correction before completion.
- Handoff: Record the task, installed state, expected and observed behavior, smallest reproduction, workaround and proposed durable correction. Parent activation authorizes diagnosis and reporting, not edits without current authorization.

## Common path

Use the maintained `scripts/smoke_signal.luau` fixture as the source for the connection example. It creates one signal, activates a listener with `signal:Connect`, fires a payload and disconnects through an idempotent feature cleanup function. For the active project, preserve the same ownership pattern and use its actual require path. No companion cleanup library is assumed.

```luau
-- API excerpt from scripts/smoke_signal.luau; keep behavior in that fixture.
local signal = Signal.new()
```

## Operational reconciliation

- Policy: required — project source headers/manifests can select a different commit independently from this guidance.
- Installed-state check: Read the active project's manifest/header and compare its GoodSignal canonical URL and commit to this target before require; inspect source differences when the recorded commit does not match the installed bytes.
- Expected identity/state: stravant-goodsignal + https://github.com/stravant/goodsignal + stravant/goodsignal + 99497c8cd6e5b50c5f4f12796d4ebc3e7dbf9d1f.
- Current-block check: Before affected use, run `python ~/.agents/skills/roblox-resource-acquisition/scripts/check_resource_status.py --pair ~/.agents/skills/roblox-goodsignal-connections .agents/roblox/resources/records/stravant-goodsignal.yaml` from the resolved project root; require HEALTHY, and enter full reconciliation on BLOCKED or UNKNOWN. Resolve another child/record location from authoritative project configuration when supplied.
- Parent-state check: Resolve the affected project root, then read the matching schema-version 3 resource record and learnings at authoritative locations, otherwise `.agents/roblox/resources/records/stravant-goodsignal.yaml` and `.agents/roblox/resources/learnings/`; without a project root use `~/.roblox-resources/records/stravant-goodsignal.yaml` and `~/.roblox-resources/learnings/`. Match slug plus canonical identity.
- Mismatch/unknown action: Stop affected use and invoke `roblox-resource-acquisition` in `repair/reconcile` mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth for defect evidence and parent activation.

## Client/server placement

GoodSignal is local to the current Luau environment; it does not replicate callbacks. A server may use it internally while retaining authority over game state. A client may use it for local presentation; validate network input on the server rather than treating a local signal as authorization.

## Mental model

A signal owns a linked list of subscriptions. Connect registers a callback; Fire uses the task scheduler to dispatch eligible listeners. Disconnect prevents future dispatch, but it cannot undo an already running or yielded callback.

## Lifecycle and cleanup

- Initialization: `Signal.new()` allocates an inert signal. Establish the feature owner's cleanup function before `Connect` activates the listener; immediately retain the returned connection under that owner.
- Reuse: Reuse the signal during the feature lifetime; callbacks check the owner's active flag before changing feature state.
- Cleanup/destruction: Mark the owner inactive, call `connection:Disconnect()` once, then `signal:DisconnectAll()` when the owner owns the whole signal. The fixture's guard makes repeated cleanup idempotent and rolls back on a failed assertion. It creates no pending waits or spawned feature tasks. For already dispatched/yielding callbacks, use feature invalidation and explicit cancellation for any separately owned task; disconnection alone cannot cancel them.
- Ownership boundary: Connections and feature callbacks belong to the feature; the module's shared coroutine cache belongs to the package. Do not claim package-global finalization from local teardown. `Wait()` cancellation and yielding callbacks are outside this fixture's proof.

## API used by this skill

Source-reviewed APIs: `Signal.new()`, `signal:Connect(callback)`, `signal:Fire(payload)`, `connection:Disconnect()` and `signal:DisconnectAll()`. Do not invent a `Destroy()` method or infer cancellation from another signal library.

## Failure modes

### No callback arrives

A missing package or wrong require path prevents setup. Check the installed source coordinate and ModuleScript placement before reconnecting; inspect whether the connection was already disconnected.

### State changes after cleanup

An already dispatched callback can outlive disconnection. Check ownership/invalidation and cancel separately owned work; do not repair this by assuming DisconnectAll cancels tasks.

## Limitations

- The fixture covers one non-yielding listener, payload delivery and repeated cleanup. It does not establish network behavior, callback error continuation, Wait cancellation, engine startup or diagnostics cleanliness.

## Security notes

No special resource-specific security boundary is introduced by local callback dispatch. Preserve server authority, validate client inputs and pin inspected source; never load a same-named unreviewed replacement dynamically.

## Verify after installation

Executable fixture: scripts/smoke_signal.luau

Run: In an isolated Studio test place with the exact source installed, copy `scripts/smoke_signal.luau` into a server Script under ServerScriptService and run Play. Use the project's strict-analysis path for that authored fixture first.

Pass condition: Output contains `goodsignal-ready`; the callback count equals `1` after the first fire and remains `1` after disconnect and a second fire. A failed assertion reports an error after rolling back the connection.

Evidence boundary: Source review and structural validation are separate from this proposed Studio recipe. Record execution against the actual installed commit before claiming runtime proof; a Lune task adapter covers only the observed non-engine scheduler behavior.

## Alternatives

- Prefer a direct function call for one recipient. A Roblox BindableEvent can supply local events with engine instance ownership. Keep alternatives informational when a project contract already owns the GoodSignal target.

## Provenance

- Resource slug: stravant-goodsignal
- Package identity: stravant/goodsignal
- DevForum: No DevForum topic is used/applicable
- Canonical source/docs: https://github.com/stravant/goodsignal
- Source version/release/commit: 99497c8cd6e5b50c5f4f12796d4ebc3e7dbf9d1f
- Source review date: 2026-09-30
- Resource verification: unverified

## Version drift

Before changing the commit, inspect canonical source for subscription, dispatch and cleanup changes and rerun affected proof. Do not advance the project's pin without its owner's authorization.
