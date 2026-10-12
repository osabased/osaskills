# Charm troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| A setter call doesn't notify | `equals(current, incoming)` returned true, or the same table was set again (the default comparison is `~=`). Set a new table. |
| `attempt to modify a readonly table` in Studio only | `flags.frozen` deep-froze the value. Replace the table instead of mutating it. |
| `Attempted to yield in an effect or scope` in Studio only | `flags.strict` caught a yield inside an effect, computed, or updater. Move async work out, then write the result with a setter. |
| A Vide property shows the first value and never updates | The property reads a Charm getter, which Vide doesn't track. Use the [Vide bridge](api-and-lifecycle.md#bridge-charm-into-vide). |
| `subscribe` never shows the initial value | That's by design. Seed the view yourself, or use `listen`. |
| An effect keeps running after teardown | The disposer was lost, or the effect was created inside a `listen`/`subscribe` callback or in `untracked`, which doesn't adopt it. Keep the disposer, or wrap the creation in `effectScope`. |
| Setup threw halfway through and left effects running | The first run of a constructor threw, so no disposer came back. Build inside `effectScope`, and dispose it if setup fails. |
| `onCleanup() can only be called inside an effect or a scope.` | It was called outside an effect or scope. Return a cleanup from the effect instead. |
| `require("@self/system")` fails | Check the mapped class and source of the package (see [setup](setup.md)). Don't patch vendor source. |
