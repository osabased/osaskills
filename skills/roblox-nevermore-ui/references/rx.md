# Rx 13.34.1

Checked against `src/rx/src/Shared/Rx.lua`, `Observable.lua` and `Subscription.lua` at commit `7ab0297`.

## Observables and subscriptions

- `Observable.new(function(sub) sub:Fire(v); return cleanup end)` creates a source. `cleanup` may be a function, a Maid, an Instance or a connection.
- `obs:Subscribe(onFire?, onFail?, onComplete?)` runs the source **immediately** and returns a `Subscription`. `sub:Destroy()` (alias `Disconnect`) cancels it and runs the source's cleanup.
- `obs:Pipe({ op1, op2, ... })` applies operators in order. Every operator is a function from Observable to Observable.

## Operators that exist at this pin

- Create: `of`, `from`, `failed`, `defer`, `timer`, `interval`, `fromSignal`, `fromPromise`, `EMPTY`, `NEVER`.
- Transform: `map`, `mapTo`, `scan`, `reduce`, `packed`, `unpacked`.
- Filter: `where` (there is no `filter`), `distinct`, `first`, `take`, `skip`, `takeUntil`, `takeWhile`, `skipUntil`, `skipWhile`.
- Combine: `combineLatest` (a table of observables or values, emitting a table), `combineLatestAll`, `combineLatestDefer`, `merge`, `mergeAll`, `withLatestFrom`.
- Flatten: `switchMap`, `switchAll`, `flatMap`, `switchScan`, `mergeScan`.
- Start or default: `startWith`, `startFrom`, `defaultsTo`, `endWith`.
- Timing: `delay`, `delayed`, `throttleTime`, `throttleDefer`, `throttle`, `onlyAfterDefer`.
- Sharing: `share`, `shareReplay`, `cache`.
- Side effects: `tap`, `finalize`, `catchError`, `using`, `toPromise`.

```luau
local sub = state:Observe():Pipe({
	Rx.where(function(v) return v ~= nil end),
	Rx.distinct(),
	Rx.switchMap(function(id) return Rx.fromPromise(fetchProfile(id)) end), -- Nevermore Promise only
}):Subscribe(function(profile) render(profile) end)
-- later: sub:Destroy()
```

## Adapters

- `Rx.fromSignal(signal)` accepts an `RBXScriptSignal` or any signal with `Connect`, including LemonSignal. Destroying the subscription disconnects only your connection; the signal stays with its owner.
- `Rx.fromPromise(promise)` asserts `Promise.isPromise`, which means a Nevermore Promise. Janitor's transitive `evaera/promise` doesn't qualify.

## Lifetime rules

- `Subscribe` runs the source before returning its handle. A source that throws before returning its cleanup leaves internal work unreachable, so write sources that are safe when they throw.
- Destroying a subscription stops future deliveries. Callbacks that are already running, and outside operations (server requests, tasks), still need their own cancellation or a disposed check.
- `switchMap` disposes the previous inner subscription when a new value arrives. It does not cancel requests that inner subscription already started.

## Sources

- [Rx API](https://quenty.github.io/NevermoreEngine/api/Rx/)
- [Rx implementation at the reviewed commit](https://github.com/Quenty/NevermoreEngine/blob/7ab0297833aa73c193d8c20dc23332280439af7c/src/rx/src/Shared/Rx.lua)
- [Observable.Subscribe at the reviewed commit](https://github.com/Quenty/NevermoreEngine/blob/7ab0297833aa73c193d8c20dc23332280439af7c/src/rx/src/Shared/Observable.lua)
