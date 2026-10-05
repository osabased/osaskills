# API and lifecycle

## Mental model

Signals store values; computed getters derive values; effects subscribe to reads made during their callback. Charm observes current state changes, while LemonSignal dispatches discrete events. Vide renders the view and owns its own reactive scopes. Prefer immutable replacement of tables; identity-equal mutation will not normally notify.

## API used by this skill

`signal`, `computed`, `effect`, `effectScope`, `listen`, `subscribe`, `batch`, `untracked`, `onCleanup`; exported `Getter<T>`, `Setter<T>`, `Update<T>`, `Equals<T>` and `Cleanup` types. `atom` remains the combined getter/setter API but is not required for the separate signal pattern. `onCleanup` binds to an active effect/scope and warns outside one unless explicitly silenced. A function passed to a setter is an updater: to store a function value, return it from an updater. Updating to nil is supported when the signal's type includes nil.

`flags.strict` and `flags.frozen` default to true in Studio and false outside Studio; `flags.trackInnerEffects` defaults to true. Frozen mode deep-freezes tables that have no metatable, recursively; tables with metatables are skipped. Keep table state immutable in both environments. Do not toggle package-global flags just to silence a failing feature. `trigger`, `observe` and `mapped` exist, but their advanced behavior is outside this child's ordinary proof; inspect exact source and add relevant project proof before making execution claims.

## Lifecycle and cleanup

Initialization: requiring the exact package initializes its reactive graph functions and Studio defaults; it creates no remote channels, engine-event subscriptions, tasks or UI. `signal` creates state. Calling `effect`, `listen`, `subscribe` or `effectScope` activates synchronous reactive ownership immediately; the feature owner retains its disposer for that lifetime.

Reuse: effects run immediately; returned cleanup callbacks run before the next effect evaluation and on disposal. Nested effects are tracked by default (`flags.trackInnerEffects=true`). A scope owns effects created within its tracking context. `effectScope(callback, true)` detaches it from a parent Charm scope. `untracked` also removes inner-effect ownership; retain detached disposers explicitly. listen/subscribe run their callbacks untracked, so inner effects in those callbacks are not automatically disposed with the subscription.

Cleanup/destruction: invoke retained disposers before destroying consumers. Disposal removes dependencies and runs registered cleanup. stopEffect clears subscriptions before cleanup; its repeated successful disposal does not repeat cleared callbacks. A cleanup error is reported after all callbacks in that cleanup list have been attempted; do not infer continuation across the whole reactive graph. Constructors that throw during their initial callback do not provide their disposer or automatically guarantee full rollback. When fallible acquisition creates effects, retain an outer scope by catching construction errors inside its callback, then dispose it and rethrow. Register the consumer owner's cleanup before activating subscriptions. Keep getters, effects, comparators and cleanup synchronous and non-yielding; Cancel separately spawned tasks or invalidate pending work at the feature owner after disposal.

Ownership boundary: a feature owns its effects/subscriptions and any tasks it starts. Never finalize the shared Charm graph or Vide scheduler. Vide owns view scopes; use Janitor for feature-owned disposers with explicit callback cleanup (`true`), but Janitor's resource iteration is unordered and a thrown entry can abort it. Preserve explicit producer-before-consumer phases where needed.

## Client/server placement

The shared package may be replicated and required independently by client and server. Each runtime owns distinct state and require caches. Server Charm state does not replicate by itself; keep privileged rules and authoritative state on the server. Client screen/application state stays client-owned. Charm Sync is a separate resource, not part of this adoption; Blink remains the project networking compiler.

## Limitations

- No UI renderer, automatic networking, persistence, deep default equality or transactional rollback. Constructor failure is not automatic full cleanup. Studio flags differ from published-runtime defaults. No native task cancellation for user-spawned work. Performance claims from benchmarks are not established here.
