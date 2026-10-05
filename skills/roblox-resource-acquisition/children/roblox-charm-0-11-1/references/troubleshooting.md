# Troubleshooting

### Value or UI does not update

Comparator returned true -> the incoming value was rejected; inspect comparator arguments. Same table mutated in place -> default reference equality sees no replacement; use a new table. Vide property reads a Charm getter directly -> the graphs are separate; use the project's owned bridge. subscribe did not initialize the view -> seed it or use listen. Missing system module or @self require failure -> verify actual mapped class/source and Roblox host support before proposing a compatibility change.

### Effect survives teardown or construction fails

Lost disposer or detached/untracked inner effect -> restore explicit ownership. Effect created in a subscription callback -> callbacks are untracked, own it separately. Initial constructor callback threw -> retain an outer scope via an internal protected acquisition and roll it back. Cleanup threw -> stopEffect detached before cleanup, but errors can interrupt wider traversal; do not assert total error-continuation. Yield error in Studio -> move asynchronous work outside critical reactive callbacks and own/invalidate it explicitly.

## Security boundary

Charm has no special network, HTTP or persistence trust boundary. Signal values on a client are client-controlled; replication of the package does not grant server authority or synchronize state. Validate requests and permissions at the actual server transport. Getters/effects/comparators execute trusted application code, not client-supplied functions. Keep secrets and privileged state out of replicated modules.

## Alternatives

- Vide sources suffice for component-local view state. Native variables/callbacks can handle trivial state. Reflex and Fusion state are informational alternatives. The user selected Charm; preserve its canonical identity and project pin rather than substituting.
