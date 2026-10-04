---
name: roblox-charm-0-11-1
description: "Use for littensy Charm 0.11.1 reactive application state, signals, computed values and owned effects; exclude UI rendering, discrete custom events, networking and dependency selection/upgrades."
---

# Charm 0.11.1

Use **Charm** for reactive application state. Guidance targets **0.11.1** (source reviewed **2026-10-03**). Resource verification: **verified**.
This child is advice-only: it claims source-grounded instructions and exact-install checking, not maintained executable Luau examples or a runtime harness. Project records own execution proof. Studio proof for this target covers signal updates/equality, computed batching, effect disposal and an owned bridge to the project's Vide 0.4.1 pin; no rendered pixels, input, network delivery or clean-console claim.

## Use when

- Implementing or diagnosing Charm 0.11.1 application/domain state, reactive getters, derived values, synchronous effects and scoped subscriptions in a project that adopted this pin.

## Do not use when

- A single local variable or native property suffices; implementing UI rendering or Vide-only component state; discrete events that belong to LemonSignal; networking/synchronization; selecting/upgrading dependencies. Preserve a different project pin and resolve matching guidance.

## Prerequisites and installation

Resolve `<project-root>` from the supplied active project and `<child-skill-directory>` from this loaded `SKILL.md`. Resolve `<parent-skill-directory>` from the installed `roblox-resource-acquisition` skill's loaded location; prefer the active project's `.agents/skills` copy when present, otherwise use the host's discovered skill location. Substitute these placeholders with actual paths before executing commands, quote paths containing spaces, and run project commands from `<project-root>`. Checker inputs resolve against that project; never infer it from the shared skill's location. Default adoption of a bundled child is project-local.

Resolve the active Roblox project and its owned pin first. Use pesde (reviewed 0.7.4), not a second package manager. Parent roblox-resource-acquisition must be installed; its scripts need Python and PyYAML. This child's checker needs Python 3.11+ and only the standard library.

1. Add `Charm = { wally = "littensy/charm", version = "=0.11.1" }` in `[dependencies]`, with `[wally_indices].default = "https://github.com/UpliftGames/wally-index"`. Initial authorized resolution is `pesde install`; restoration is `pesde install --locked`. Map roblox_packages with the official pesde/scripts_rojo hooks. Inspect the resulting sourcemap and mapped wrapper before requiring it. The standard alias maps to `Packages.Charm`; the internal `charm` ModuleScript has a `system` child. Source uses `require("@self/system")`; the reviewed Roblox host resolves it without a vendor patch. Do not rewrite generated source or introduce a source-rewriting hook by assumption. MIT license, no runtime package dependencies.

## On-demand maintenance

- Promotion guard: Check sibling `.skill-maintenance/roblox-charm-0-11-1.json` before ordinary use; presence stops dependent use until recovery/completion.
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
3. Require the mapped Charm alias. `Charm.signal(initialValue, equals?)` returns separate getter and setter functions. Read with `getter()`; write with `setter(value)` or `setter(function(current) return nextValue end)`. Keep setters with the state owner and pass getters to consumers. `equals(current, incoming)` returning true rejects the new value and suppresses notification. Default equality is Luau value/reference inequality, not deep comparison.
4. Derive read-only values with `computed(getter)`; it is lazy and cached. Use `effect(callback)` for synchronous reactions, or `listen(getter, callback)` for an initial callback plus changes. `subscribe(getter, callback)` skips the initial callback. Retain every returned disposer. Group related writes with `batch`; it defers effects until the outer batch ends and does not roll back writes on error.
5. Vide and Charm have separate dependency tracking. Use an owned subscription to update a Vide source, with its disposer registered in the Vide scope before activation. Resolve the project's existing adapter when supplied. Call it inside a Vide scope and keep the bridge one-way. A raw Charm getter passed to a Vide property does not itself establish a Vide dependency. Nested effects created in listen/subscribe callbacks are untracked and require their own ownership.

Before completion run the Integrity gate. Runtime claims require the affected project's execution evidence.

## Operational reconciliation

- Policy: conditional — exact declaration and lock counterpart establish ordinary-use identity; installed integrity is deferred to completion.
- Installed-state check: `scripts/check_install.py` compares the direct alias, canonical registry/package, exact version, target and lock counterpart. Its integrity mode additionally checks this resource's reviewed runtime/compiler source files.
- Expected identity/state: slug `charm`, package `littensy/charm`, https://github.com/littensy/charm, version 0.11.1.
- Current-block check: Before affected use run `python <parent-skill-directory>/scripts/check_resource_status.py --pair <child-skill-directory> MATCHING-RECORD.yaml`, substituting the resolved record path. Proceed only on HEALTHY (exit 0); BLOCKED or UNKNOWN enters full parent-state reconciliation. This read-only query executes no evidence commands.
- Integrity gate: Before completion run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock`. PASS (exit 0) reports charm, 0.11.1 and installed-integrity. Package files resolve relative to the manifest directory; reviewed standard pesde layout is required. Run the affected project's source/build check separately.
- Escalation triggers: Missing/mismatched declaration or lock; adoption/upgrade; authorized repair invalidating evidence; verifier failure/drift; hard correctness/security/identity/version/verification defect; known block or BLOCKED/UNKNOWN query. Stop affected version-sensitive use and perform Parent-state check.
- Parent-state check: Use an explicitly supplied authoritative record when present. Otherwise resolve the project root and its schema-version 3 `.agents/roblox/resources/records/charm.yaml` plus resource-bound learnings under `.agents/roblox/resources/learnings/`. If this project-scoped child's project cannot be resolved, report UNKNOWN state and invoke roblox-resource-acquisition in repair/reconcile mode; do not silently switch to global records. Only for an explicitly user/global-scoped child with no applicable project root, use selector-qualified `~/.roblox-resources/records/charm--0.11.1.yaml` and `~/.roblox-resources/learnings/`. Match resource slug, canonical URL and package identity. Load full evidence/learnings only after escalation.
- Mismatch/unknown action: For every state escalation trigger, stop the affected use, perform Parent-state check and invoke roblox-resource-acquisition in repair/reconcile mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth.

## Client/server placement

The shared package may be replicated and required independently by client and server. Each runtime owns distinct state and require caches. Server Charm state does not replicate by itself; keep privileged rules and authoritative state on the server. Client screen/application state stays client-owned. Charm Sync is a separate resource, not part of this adoption; Blink remains the project networking compiler.

## Mental model

Signals store values; computed getters derive values; effects subscribe to reads made during their callback. Charm observes current state changes, while LemonSignal dispatches discrete events. Vide renders the view and owns its own reactive scopes. Prefer immutable replacement of tables; identity-equal mutation will not normally notify.

## Lifecycle and cleanup

Initialization: requiring the exact package initializes its reactive graph functions and Studio defaults; it creates no remote channels, engine-event subscriptions, tasks or UI. `signal` creates state. Calling `effect`, `listen`, `subscribe` or `effectScope` activates synchronous reactive ownership immediately; the feature owner retains its disposer for that lifetime.

Reuse: effects run immediately; returned cleanup callbacks run before the next effect evaluation and on disposal. Nested effects are tracked by default (`flags.trackInnerEffects=true`). A scope owns effects created within its tracking context. `effectScope(callback, true)` detaches it from a parent Charm scope. `untracked` also removes inner-effect ownership; retain detached disposers explicitly. listen/subscribe run their callbacks untracked, so inner effects in those callbacks are not automatically disposed with the subscription.

Cleanup/destruction: invoke retained disposers before destroying consumers. Disposal removes dependencies and runs registered cleanup. stopEffect clears subscriptions before cleanup; its repeated successful disposal does not repeat cleared callbacks. A cleanup error is reported after all callbacks in that cleanup list have been attempted; do not infer continuation across the whole reactive graph. Constructors that throw during their initial callback do not provide their disposer or automatically guarantee full rollback. When fallible acquisition creates effects, retain an outer scope by catching construction errors inside its callback, then dispose it and rethrow. Register the consumer owner's cleanup before activating subscriptions. Keep getters, effects, comparators and cleanup synchronous and non-yielding; Cancel separately spawned tasks or invalidate pending work at the feature owner after disposal.

Ownership boundary: a feature owns its effects/subscriptions and any tasks it starts. Never finalize the shared Charm graph or Vide scheduler. Vide owns view scopes; use Janitor for feature-owned disposers with explicit callback cleanup (`true`), but Janitor's resource iteration is unordered and a thrown entry can abort it. Preserve explicit producer-before-consumer phases where needed.

## API used by this skill

`signal`, `computed`, `effect`, `effectScope`, `listen`, `subscribe`, `batch`, `untracked`, `onCleanup`; exported `Getter<T>`, `Setter<T>`, `Update<T>`, `Equals<T>` and `Cleanup` types. `atom` remains the combined getter/setter API but is not required for the separate signal pattern. `onCleanup` binds to an active effect/scope and warns outside one unless explicitly silenced. A function passed to a setter is an updater: to store a function value, return it from an updater. Updating to nil is supported when the signal's type includes nil.

`flags.strict` and `flags.frozen` default to true in Studio and false outside Studio; `flags.trackInnerEffects` defaults to true. Frozen mode deep-freezes tables that have no metatable, recursively; tables with metatables are skipped. Keep table state immutable in both environments. Do not toggle package-global flags just to silence a failing feature. `trigger`, `observe` and `mapped` exist, but their advanced behavior is outside this child's ordinary proof; inspect exact source and add relevant project proof before making execution claims.

## Failure modes

### Value or UI does not update

Comparator returned true -> the incoming value was rejected; inspect comparator arguments. Same table mutated in place -> default reference equality sees no replacement; use a new table. Vide property reads a Charm getter directly -> the graphs are separate; use the project's owned bridge. subscribe did not initialize the view -> seed it or use listen. Missing system module or @self require failure -> verify actual mapped class/source and Roblox host support before proposing a compatibility change.

### Effect survives teardown or construction fails

Lost disposer or detached/untracked inner effect -> restore explicit ownership. Effect created in a subscription callback -> callbacks are untracked, own it separately. Initial constructor callback threw -> retain an outer scope via an internal protected acquisition and roll it back. Cleanup threw -> stopEffect detached before cleanup, but errors can interrupt wider traversal; do not assert total error-continuation. Yield error in Studio -> move asynchronous work outside critical reactive callbacks and own/invalidate it explicitly.

## Limitations

- No UI renderer, automatic networking, persistence, deep default equality or transactional rollback. Constructor failure is not automatic full cleanup. Studio flags differ from published-runtime defaults. No native task cancellation for user-spawned work. Performance claims from benchmarks are not established here.

## Security notes

Charm has no special network, HTTP or persistence trust boundary. Signal values on a client are client-controlled; replication of the package does not grant server authority or synchronize state. Validate requests and permissions at the actual server transport. Getters/effects/comparators execute trusted application code, not client-supplied functions. Keep secrets and privileged state out of replicated modules.

## Verify after installation

Executable fixture: not-applicable — advice-only instructions and a read-only exact-install checker; no embedded executable Luau integration, rendering, network delivery or clean-diagnostics claim. Project resource execution is recorded separately.

Run: `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock` from the affected project.

Pass condition: The command exits 0 and prints status `PASS`, resource `charm`, version `0.11.1`, lane `installed-integrity`. A modified package source or mismatched manifest/lock exits 1. After setup, run the project's check command for mapped strict consumers and artifacts; that source/build lane still does not prove runtime behavior.

Evidence boundary: helper PASS proves declaration/lock and source identity only. Advice tests verify this instruction interface. Any real lifecycle/input/network claim must name and execute an owned project fixture in its engine host; no process-global finalization or clean-console promise is supplied here.

## Alternatives

- Vide sources suffice for component-local view state. Native variables/callbacks can handle trivial state. Reflex and Fusion state are informational alternatives. The user selected Charm; preserve its canonical identity and project pin rather than substituting.

## Provenance

- Resource slug: charm
- Package identity: littensy/charm
- DevForum: No DevForum topic is used/applicable.
- Canonical source/docs: https://github.com/littensy/charm
- Source version/release/commit: 0.11.1
- Immutable release commit: af4eb5262d640cf89c56217ab7feb403e939cbd2
- Source review date: 2026-10-03
- Resource verification: verified

## Version drift

Preserve the project's adopted pin. Check source/release changes affecting this API or command before proposing an upgrade. Revalidate changed instructions, exact source checker, project execution and host activation after an authorized update. A newer stable or prerelease announcement is evidence to report, not authority to replace an externally owned dependency.
