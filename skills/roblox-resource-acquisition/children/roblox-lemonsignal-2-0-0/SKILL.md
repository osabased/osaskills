---
name: roblox-lemonsignal-2-0-0
description: "Use for Data-Oriented-House LemonSignal 2.0.0 typed custom events, reconnectable subscriptions and owned callback lifecycle; exclude networking, signal selection/upgrades, Vide reactive state and simple native Roblox event subscriptions."
---

# LemonSignal 2.0.0

Use **LemonSignal** for typed events and reconnectable subscriptions within one Luau runtime. Guidance targets **2.0.0** (source reviewed **2026-10-03**). Resource verification: **verified**.
This child is advice-only: it claims instruction correctness and exact-install checking, not maintained executable Luau examples or a runtime harness. The affected project's matching resource record owns executed proof. Actual Roblox Studio checks exercised typed-style payload delivery, Once, Disconnect/Reconnect, Janitor subscription cleanup, wrapped engine producer teardown and caller-owned Wait cancellation.

## Use when

- Implementing or diagnosing LemonSignal 2.0.0 custom events, wrapped native producers and subscription ownership.

## Do not use when

- Networking or cross-runtime delivery; selecting/upgrading a signal library; Vide reactive state; subscribing directly to an existing Roblox event.
- The project's adopted target differs: preserve its pin and resolve exact-target guidance.

## Prerequisites and installation

Resolve `<project-root>` from the supplied active project and `<child-skill-directory>` from this loaded `SKILL.md`. Resolve `<parent-skill-directory>` from the installed `roblox-resource-acquisition` skill's loaded location; prefer the active project's `.agents/skills` copy when present, otherwise use the host's discovered skill location. Substitute these placeholders with actual paths before executing commands, quote paths containing spaces, and run project commands from `<project-root>`. Checker inputs resolve against that project; never infer it from the shared skill's location. Default adoption of a bundled child is project-local.

Resolve the active Roblox project and its owned pin first. Reviewed pesde 0.7.4 supports this package directly; use pesde rather than introducing Wally as a separate manager. Parent roblox-resource-acquisition must be installed; its scripts need Python and PyYAML. This child's checker needs Python 3.11+ and only the standard library.

1. Add `LemonSignal = { wally = "data-oriented-house/lemonsignal", version = "=2.0.0" }` to `[dependencies]`; keep `[wally_indices].default="https://github.com/UpliftGames/wally-index"`. Map roblox_packages to a shared Packages folder with official pesde/scripts_rojo mapping and sourcemap hooks. The native Wally wrapper maps to a lowercase internal ModuleScript and requires correctly; verify the actual map before using a path.

Initial intentional resolution is `pesde install`; ordinary restoration is `pesde install --locked`. Do not modify package-generated wrappers or vendor source. MIT license. 

## On-demand maintenance

- Promotion guard: Check sibling `.skill-maintenance/roblox-lemonsignal-2-0-0.json` before ordinary use; presence stops dependent use until recovery/completion.
- First-use freshness: Before this resource's first use in a task, read and apply the installed `roblox-resource-acquisition` parent's `references/on-demand-maintenance.md#first-use-freshness-check`. Compare canonical stable releases/maintained source and relevant documentation with the actual installed/project-pinned target, check this guidance's compatibility, reuse unchanged checks within the task, and disclose unavailable lookups. Preserve the selected pin and valid exact-target proof; the comparison alone does not authorize upgrades or full lifecycle reconciliation.
- Freshness triggers: Relevant current claims, acquisition/upgrade, generation/refresh, source drift, consequential practice or reusable defects invoke `roblox-resource-acquisition` once for this scope and its `references/on-demand-maintenance.md`.
- Target and economy: Preserve the project's selected target and local compatibility guidance. Healthy immutable use keeps the cheap declaration/lock query and deferred integrity gate. Dependency/architecture/practice changes return to their authority. No schedule.

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode when this guidance requires guessing, bypassing instructions, repeating a workaround, or an undocumented adjustment likely to recur. A harmless one-off task-local adjustment is not an interrupt.
- Hard defect: Stop affected work for unreliable correctness, security, identity/version or verification; reconcile and repair before continuing.
- Soft defect: Safe reversible work may continue, but invoke parent diagnosis and surface the reproduction, workaround and durable correction before completion; do not force unrelated provenance work.
- Handoff: Capture task, installed state, expected/observed behavior, smallest reproduction, workaround and proposed durable correction. Parent invocation authorizes diagnosis/reporting; edits require current task authorization or the parent's approved on-demand factual-repair grant.


## Common path

1. Run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock --declared` in the affected project.
2. Resolve the matching record below and run the narrow Current-block query. Continue only on HEALTHY without package internals, full proof or learnings.
3. Require the mapped LemonSignal wrapper. `LemonSignal.new()` creates a custom signal; annotate it as `LemonSignal.Signal<PayloadType>` when useful. `signal:Connect(callback)` returns a Connection; fire payloads through `signal:Fire(...)`. v2.0 accepts only the callback in Connect: older documentation’s extra bound arguments belong to older APIs. Use a closure for captured context.

Own each subscription with explicit `"Disconnect"` when adding it to Janitor. A borrowed signal belongs to its provider; destroy only signals this feature creates. Disconnect producers before consumer teardown; Janitor 1.18.3 has no entry order or best-effort continuation. Detach feature ownership and guard asynchronous callback results after disposal. Use `Once` for one callback, `Disconnect`/`Reconnect` for a retained handle, and `Destroy` for disconnecting the owned signal and its wrapped engine producer.

Before completion run the Integrity gate. Any runtime claim requires the project's corresponding execution evidence.

## Operational reconciliation

- Policy: conditional — exact declaration and lock counterpart establish ordinary-use identity; installed integrity is deferred to completion.
- Installed-state check: `scripts/check_install.py` compares the direct alias, canonical registry/package, exact version, target and lock counterpart. Its integrity mode additionally checks this resource's reviewed runtime/compiler source files.
- Expected identity/state: slug `lemonsignal`, package `data-oriented-house/lemonsignal`, https://github.com/Data-Oriented-House/LemonSignal, version 2.0.0.
- Current-block check: Before affected use run `python <parent-skill-directory>/scripts/check_resource_status.py --pair <child-skill-directory> MATCHING-RECORD.yaml`, substituting the resolved record path. Proceed only on HEALTHY (exit 0); BLOCKED or UNKNOWN enters full parent-state reconciliation. This read-only query executes no evidence commands.
- Integrity gate: Before completion run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock`. PASS (exit 0) reports lemonsignal, 2.0.0 and installed-integrity. Package files resolve relative to the manifest directory; reviewed standard pesde layout is required. Run the affected project's source/build check separately.
- Escalation triggers: Missing/mismatched declaration or lock; adoption/upgrade; authorized repair invalidating evidence; verifier failure/drift; hard correctness/security/identity/version/verification defect; known block or BLOCKED/UNKNOWN query. Stop affected version-sensitive use and perform Parent-state check.
- Parent-state check: Use an explicitly supplied authoritative record when present. Otherwise resolve the project root and its schema-version 3 `.agents/roblox/resources/records/lemonsignal.yaml` plus resource-bound learnings under `.agents/roblox/resources/learnings/`. If this project-scoped child's project cannot be resolved, report UNKNOWN state and invoke roblox-resource-acquisition in repair/reconcile mode; do not silently switch to global records. Only for an explicitly user/global-scoped child with no applicable project root, use selector-qualified `~/.roblox-resources/records/lemonsignal--2.0.0.yaml` and `~/.roblox-resources/learnings/`. Match resource slug, canonical URL and package identity. Load full evidence/learnings only after escalation.
- Mismatch/unknown action: For every state escalation trigger, stop the affected use, perform Parent-state check and invoke roblox-resource-acquisition in repair/reconcile mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth.

## Client/server placement

Shared package, independent client/server require state. Custom Fire delivers only in the current runtime; use client signals for menus and server signals for privileged rules. Never replicate a signal table as transport or trust a client-emitted event as a server-authoritative fact.

## Mental model

Typed events and reconnectable subscriptions within one luau runtime; the application retains lifetime and authority decisions.

## Lifecycle and cleanup

Initialization: the feature owner invokes the Roblox require path, which temporarily creates and destroys a BindableEvent to cache native connection methods. `new()` is inert; `wrap()` activates a native subscription and the wrapper owns it. Establish feature cleanup before wrapping/subscribing and register each acquisition immediately; rollback partial acquisition on failure.

Reuse: Fire uses task.spawn and a module-shared coroutine pool. Callbacks may yield. Disconnect/Destroy prevents later delivery to disconnected listeners but does not cancel an already running callback; invalidate results with the feature’s disposed flag or cancel separately owned tasks.

Cleanup/destruction: Disconnect is idempotent and a connection can Reconnect. Signal Destroy is reusable, not a lifetime close flag. Drop handles after disposal to avoid accidental resurrection. Wait connects an internal resume callback then yields; destroying the signal disconnects that callback without resuming or cancelling the waiting task. Own and cancel/invalidate that waiter explicitly. Producers must stop before consumers; isolate cleanup phases rather than assuming Janitor’s iteration order or continuation.

Ownership boundary: destroy a feature-created signal/wrapper and disconnect its borrowed subscriptions. Never cancel or finalize the package’s shared coroutine pool. Do not destroy another feature’s signal or a wrapped engine service.

## API used by this skill

`new`, `wrap(RBXScriptSignal)`, `Connect`, `Once`, `Wait`, `Fire`, `DisconnectAll`, `Destroy`; exported `Signal<T...>` and `Connection` types. Connections expose Connected, Disconnect and Reconnect. Destroy removes listeners and a wrapped RBXScriptConnection; it does not permanently close the signal or prevent a retained connection from reconnecting.

## Failure modes

### Wrong setup, stale API or cleanup ownership

Unexpected callback argument -> check Fire payloads and remove old Connect bound-argument examples. Callback finishes after disposal -> owner invalidation/cancellation, not Destroy alone. Wait never resumes after teardown -> cancel the owned waiter. Engine events continue -> destroy the owned wrap, not just one subscriber. Wrong identity -> preserve Data-Oriented-House/LemonSignal; do not substitute a similarly named fork.

## Limitations

- No cross-client/server transport, producer authority, callback cancellation or closed-signal state. Destroy can leave a waiter suspended. No Connect-time bound arguments in 2.0.0. The Roblox task branch requires Instance; Lune is not a substitute engine host for this require path. No runtime dependencies. Performance claims from benchmarks are not established here.

## Security notes

LemonSignal has no built-in remote, HTTP, persistence or arbitrary asset loading. A local signal cannot authenticate client claims or cross runtime boundaries. Keep server validation at the real network boundary. Preserve exact identity and lock; callbacks execute trusted local application code.

## Verify after installation

Executable fixture: not-applicable — advice-only instructions and a read-only exact-install checker; no embedded executable Luau integration, rendering, network delivery or clean-diagnostics claim. Project resource execution is recorded separately.

Run: `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock` from the affected project.

Pass condition: The command exits 0 and prints status `PASS`, resource `lemonsignal`, version `2.0.0`, lane `installed-integrity`. A modified package source or mismatched manifest/lock exits 1. After setup, run the project's check command for mapped strict consumers and artifacts; that source/build lane still does not prove runtime behavior.

Evidence boundary: helper PASS proves declaration/lock and source identity only. Advice tests verify this instruction interface. Any real lifecycle/input/network claim must name and execute an owned project fixture in its engine host; no process-global finalization or clean-console promise is supplied here.

## Alternatives

- Native RBXScriptSignal for engine events, BindableEvent or Sleitnick Signal for local dispatch are informational alternatives. The user selected LemonSignal; preserve the owner’s package identity and pin.

## Provenance

- Resource slug: lemonsignal
- Package identity: data-oriented-house/lemonsignal
- DevForum: No DevForum topic is used/applicable.
- Canonical source/docs: https://github.com/Data-Oriented-House/LemonSignal
- Source version/release/commit: 2.0.0
- Source review date: 2026-10-03
- Resource verification: verified

## Version drift

Preserve the project's adopted pin. Check source/release changes affecting this API or command before proposing an upgrade. Revalidate changed instructions, exact source checker, project execution and host activation after an authorized update. A newer stable or prerelease announcement is evidence to report, not authority to replace an externally owned dependency.
