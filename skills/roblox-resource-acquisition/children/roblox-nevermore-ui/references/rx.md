# Rx flow and subscription lifetime

Use for observable pipelines, state/event flow, or signal/promise adapters.
The parent [Nevermore skill](../SKILL.md) owns the exact pins, imports, shared
cleanup rules, and verification boundary.

## Pipelines and adapters

- Compose pipelines with observable:Pipe({ Rx.map(...), ... }). Own the returned subscriptions explicitly and dispose them with Destroy.
- switchMap replaces and disposes the previous inner subscription. It does not cancel unrelated tasks or requests already sent to a server.
- Rx.fromSignal adapts an engine/custom signal exposing Connect. Destroying a subscription detaches its connection; the borrowed signal retains its owner. LemonSignal remains the project's discrete event primitive.
- Rx.fromPromise expects Nevermore Promise. Do not assume Janitor's transitive evaera Promise is interchangeable.

When observable values drive UI, read [Blend](blend.md) for bindings and mount
ownership. When work belongs to an alive/dead value, read [Brio](brio.md).

## Sources

- [Rx API](https://quenty.github.io/NevermoreEngine/api/Rx/)
