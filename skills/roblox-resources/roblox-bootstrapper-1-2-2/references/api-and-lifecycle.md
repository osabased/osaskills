# API and lifecycle

## Mental model

Discover module tables once; the caller chooses the method names, execution mode and phase barriers.

## API used by this skill

- `loadChildren`, `loadDescendants`: filtered ModuleScript discovery sorted by Name, with full-path tie break.
- `loadSequence`: retains manual input order. Loaded tables and ModuleScript instances are supported inputs.
- `byName`: Lua pattern, not a regex/glob. Unique discovered names keep diagnostics unambiguous.
- `run`: synchronous sequential dispatch; catches callback errors, continues the current sequence and returns successful invoked modules plus errors. Application policy must stop later phases if required.
- `runAsync`: starts an ordered background sequence; `runConcurrent` starts separate tasks. They return no completion/error receipt and no cancellation handle. Use run when startup dependencies need a barrier.
- `bindTo`: binds an owned method sequence to a Roblox/custom signal or subscription function and returns cleanup. Frame/interval binding APIs are source-reviewed; only claim execution for the specific tested binding.

## Lifecycle and cleanup

- Initialization: The caller/bootstrap owns and activates discovery with loadDescendants and method execution with run. Requiring the bundle gets RunService but creates no subscription or startup task; feature owners retain acquired binding cleanup for their lifetime.
Discovery requires modules, so their top-level code can activate behavior. Keep fallible
activation in owned lifecycle methods, establish cleanup ownership first, and make explicit
partial acquisition roll back before raising. Bootstrapper supplies no dependency graph,
automatic init/start names, module teardown or rollback for module side effects.

- Reuse: `run` calls are activated and owned by the caller. Synchronous calls can yield indefinitely
if a module never returns. Missing methods are skipped. Callback/require failures also emit
an asynchronous error diagnostic; inspecting returned errors does not suppress that output.

- Cleanup/destruction: The feature owner detaches and calls its binding disposer to disconnect subscriptions before destroying consumers. Synchronous use spawns no pending task; async/concurrent work has no cancellation handle. Retain the returned disposer; detach before invoking
it, disconnect producers before destroying consumers, and make the owner's wrapper idempotent.
Bootstrapper does not own or destroy your module tables. An async/concurrent sequence has no
supported cancellation handle: do not use it for a startup barrier or claim its pending
work is cancelled by binding cleanup. No global finalizer is required for ordinary synchronous use.

## Client/server placement

The shared package can be replicated, but each runtime has its own require cache and module state.
Discover client controllers on clients and server services in ServerScriptService on servers.
Do not include packages, helpers, stories or every replicated module in a blanket startup scan.
Render-step/PreRender bindings are client-only. Keep privileged rules, persistence and client validation server-owned.

## Limitations

- No dependency resolution, cycle detection, readiness flags, automatic lifecycle names or universal destructor.
Alphabetical order is deterministic, not dependency ordering. For required dependencies, select a
manual sequence or explicit requires within init. Errors are keyed by module name for ModuleScripts;
avoid duplicate names. No comprehensive scheduler, animation or clean-console proof is implied.
