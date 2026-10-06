# API and lifecycle

## Mental model

Typed events and reconnectable subscriptions within one luau runtime; the application retains lifetime and authority decisions.

## API used by this skill

`new`, `wrap(RBXScriptSignal)`, `Connect`, `Once`, `Wait`, `Fire`, `DisconnectAll`, `Destroy`; exported `Signal<T...>` and `Connection` types. Connections expose Connected, Disconnect and Reconnect. Destroy removes listeners and a wrapped RBXScriptConnection; it does not permanently close the signal or prevent a retained connection from reconnecting.

`connection:Reconnect()` relinks the retained connection to its original signal with the same stored callback/closure. It is a no-op while already connected and accepts no replacement callback or bound arguments. Version 2.0.0 stores only the callback at Connect; each Fire supplies its current payload, and reconnect does not replay earlier payloads. Use a new connection when replacing the callback; captured context follows ordinary closure semantics.

## Lifecycle and cleanup

Initialization: the feature owner invokes the Roblox require path, which temporarily creates and destroys a BindableEvent to cache native connection methods. `new()` is inert; `wrap()` activates a native subscription and the wrapper owns it. Establish feature cleanup before wrapping/subscribing and register each acquisition immediately; rollback partial acquisition on failure.

Reuse: Fire uses task.spawn and a module-shared coroutine pool. Callbacks may yield. Disconnect/Destroy prevents later delivery to disconnected listeners but does not cancel an already running callback; invalidate results with the feature’s disposed flag or cancel separately owned tasks.

Cleanup/destruction: Disconnect is idempotent and a connection can Reconnect. Signal Destroy is reusable, not a lifetime close flag. Drop handles after disposal to avoid accidental resurrection. Wait connects an internal resume callback then yields; destroying the signal disconnects that callback without resuming or cancelling the waiting task. Own and cancel that suspended task explicitly, then dispose the signal. A disposed flag suppresses stale callback results but cannot resume or cancel a waiter. Producers must stop before consumers; isolate cleanup phases rather than assuming Janitor’s iteration order or continuation.

On a borrowed long-lived signal, cancelling the Wait thread does not remove its hidden subscription, and the borrower must not destroy the provider's signal. When independent cancellation/teardown is needed, use a retained `Connect` handle with an application-owned waiter/cancellation design, and disconnect that handle during disposal. Keep any resumed task and its stale-result guard under the same owner.

Ownership boundary: destroy a feature-created signal/wrapper and disconnect its borrowed subscriptions. Never cancel or finalize the package’s shared coroutine pool. Do not destroy another feature’s signal or a wrapped engine service.

## Client/server placement

Shared package, independent client/server require state. Custom Fire delivers only in the current runtime; use client signals for menus and server signals for privileged rules. Never replicate a signal table as transport or trust a client-emitted event as a server-authoritative fact.

## Limitations

- No cross-client/server transport, producer authority, callback cancellation or closed-signal state. Destroy can leave a waiter suspended. No Connect-time bound arguments in 2.0.0. The Roblox task branch requires Instance; Lune is not a substitute engine host for this require path. No runtime dependencies. Performance claims from benchmarks are not established here.
