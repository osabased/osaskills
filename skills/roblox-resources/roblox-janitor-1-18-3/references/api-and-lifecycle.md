# API and lifecycle

## Mental model

Owned connection/object cleanup and indexed resource replacement; the application retains lifetime and authority decisions.

## API used by this skill

`new`, `Add`, `AddObject`, `Remove`, `RemoveNoClean`, `Get`, `GetAll`, `Cleanup`, `Destroy`, `LinkToInstance`, `LinkToInstances`. `AddPromise` exists but is outside this child’s proof and ordinary connection role. `Cleanup` keeps a successfully cleaned owner reusable. `Destroy` invalidates it. `LinkToInstance` subscribes to Instance.Destroying; it does not detect reparenting/removal by itself.

## Lifecycle and cleanup

Initialization: requiring Janitor loads FastDefer and its Promise companion modules; `new()` creates an inert cleanup table. `Add` registers ownership and an indexed replacement can immediately invoke prior cleanup. `LinkToInstance` activates an owned Destroying subscription.

Reuse: on successful Cleanup the owner can accept new resources. Set ownership before construction, add each acquisition immediately, and explicitly roll back registered resources if later construction fails. Use an outer disposed/detached wrapper for reentrant and repeated teardown.

Cleanup/destruction: disconnect producers and cancel registered tasks explicitly; cleanup uses table iteration with no deterministic resource ordering. User callbacks and object methods are called directly; a thrown entry aborts the remaining entries and may leave CurrentlyCleaning set. Do not claim best-effort continuation or a reliable retry. Isolate failure-prone entries in protected callbacks or separate top-level owners. Disconnect producers before destroying their consumers. Threads use task.cancel with the resource's protected/deferred fallback; independently running async work still needs cancellation or invalidation at its owner.

Ownership boundary: a feature may own its connections, objects and tasks; it must not finalize shared engine services, Vide package work, LemonSignal’s shared coroutine pool or other package/global schedulers. A module-level owner-removal listener may be needed when connections made from a LocalScript disappear with that script.

## Client/server placement

The shared package can be replicated. Client and server require caches and cleanup owners are separate; a server Janitor cannot clean client UI. Use a client feature owner for UI and a server owner for privileged gameplay. Janitor creates no remote channel.

## Limitations

- No resource order or error-continuation guarantee. Raw successful Destroy is not repeatable. LinkToInstance covers destruction, not all removal lifecycles. No automatic cancellation of unregistered tasks. Janitor 1.18.3 brings howmanysmall/typed-promise 4.0.6 and evaera/promise 4.0.0 in the reviewed pesde lock; their promise APIs are not tested by this cleanup guidance.
