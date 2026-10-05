# Rx flow and subscription lifetime

Use for observable pipelines, state/event flow, or signal/promise adapters.
The parent [Nevermore skill](../SKILL.md) owns the exact pins, imports, shared
cleanup rules, and verification boundary.

Reviewed API: `@quenty/rx` 13.34.1 at NevermoreEngine commit `7ab0297833aa73c193d8c20dc23332280439af7c`.

## Pipelines and adapters

- Compose pipelines with observable:Pipe({ Rx.map(...), ... }). Own the returned subscriptions explicitly and dispose them with Destroy.
- switchMap replaces and disposes the previous inner subscription. It does not cancel unrelated tasks or requests already sent to a server.
- Rx.fromSignal adapts an engine/custom signal exposing Connect. Destroying a subscription detaches its connection; the borrowed signal retains its owner. LemonSignal remains the project's discrete event primitive.
- Rx.fromPromise expects Nevermore Promise. Do not assume Janitor's transitive evaera Promise is interchangeable.

`Subscribe` invokes the source's subscription function immediately before returning its cleanup handle. A source that throws before returning cleanup needs an exception-safe source implementation; a feature cannot clean an inaccessible internal handle. `Destroy` suppresses future subscription delivery, but already running callback work and external operations still need their own cancellation/disposal checks. Keep a borrowed signal or Promise alive for its provider; destroying the derived subscription does not transfer ownership of that provider.

When observable values drive UI, read [Blend](blend.md) for bindings and mount
ownership. When work belongs to an alive/dead value, read [Brio](brio.md).

## Sources

- [Rx API](https://quenty.github.io/NevermoreEngine/api/Rx/)
- [Exact Rx implementation](https://github.com/Quenty/NevermoreEngine/blob/7ab0297833aa73c193d8c20dc23332280439af7c/src/rx/src/Shared/Rx.lua)
- [Immediate Subscribe boundary](https://github.com/Quenty/NevermoreEngine/blob/7ab0297833aa73c193d8c20dc23332280439af7c/src/rx/src/Shared/Observable.lua)
