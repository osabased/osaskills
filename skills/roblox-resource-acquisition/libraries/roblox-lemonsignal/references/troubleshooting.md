# LemonSignal troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| A callback receives unexpected arguments | It was written for 1.x, where `Connect(fn, ...)` bound extra arguments. 2.0.0 passes only the `Fire` arguments; capture context in a closure. |
| Listeners run in the "wrong" order | They run newest first. Don't depend on order; use explicit phases or a single dispatcher. |
| A thread blocked in `Wait()` never resumes after teardown | `Destroy` doesn't resume waiters. Cancel the thread, or use the cancellable wait in [API and lifecycle](api-and-lifecycle.md#wait-and-cancellation). |
| A callback still acts after disposal | It was already running (it yielded). Check a disposed flag after each yield. |
| Engine events keep arriving | The `wrap` wrapper was never destroyed; disconnecting one listener isn't enough. Call `wrapper:Destroy()`. |
| A connection added to a Janitor leaks | It was added without `"Disconnect"`. See the Janitor gotcha in [SKILL.md](../SKILL.md#gotchas). |
| An old handle starts firing again | Something called `Reconnect` on a stale handle. Drop handles after teardown. |
| `LemonSignal.Signal` type is unknown | The project's wrapper doesn't re-export the types. Require the package module directly for types, or add re-exports to a project-owned adapter. |
