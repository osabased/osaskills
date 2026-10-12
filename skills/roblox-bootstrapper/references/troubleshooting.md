# Bootstrapper troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| No module starts | Check the root passed to `load*`, the `byName` pattern (a Lua pattern: escape `.` and `-`), that each module returns a table, and the method's exact name and prefix. |
| A start-only module never starts | The caller passed `run`'s filtered result from `init` into `start`. Reuse the original loaded list. |
| `start` ran even though `init` failed | `run` continues within a phase and returns errors. Your loop must check `errors` and stop. |
| A method receives the module where its first argument should be (or the reverse) | `"."` doesn't pass self; `":"` and an unprefixed name do. |
| Startup hangs | A method yielded forever inside a synchronous `run`. Find it in the stack trace, or move long waits into `task.spawn`. |
| Errors appear in Output after you handled the map | That's by design: errors are also re-thrown asynchronously. |
| Updates continue after teardown | The binding's cleanup wasn't called, or the method spawned its own work, which the binding cleanup doesn't cancel. |
| `bindToRenderStep can only be called on the Client.` | It was called in server code. Use `bindToHeartbeat` or `bindToPostSimulation`. |
| An error map entry was overwritten | Two modules share a `Name`. Rename one. |
| A type error passing loaded modules to `run` | Array invariance under the new solver. Cast with `:: { any }` or copy into a union-typed array. |
| The wrapper or require is missing | See the wrapper-casing note in [setup](setup.md). |
