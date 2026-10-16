# Nevermore troubleshooting

| Symptom | Check and fix |
| --- | --- |
| Nothing appears | `Blend.New` was never subscribed. Call `:Subscribe()` and keep the subscription. |
| The pin check fails | Inspect `package.json`, the lock's direct entries, the npm aliases, the archive URL and integrity, and the actual package folder. Restore through the project's preparation command. Never upgrade a pin or edit `node_modules` to make the check pass. |
| `script.Parent.loader` is missing, or a named package can't be found | Require the shared adapter, not raw `Blend.lua`. Bootstrapping belongs to the root owner. Check the mapped package topology ([setup](setup.md)). |
| Server-only packages are visible on a Studio client | The Studio fast path is active. Keep `skipStudioFastPath = true`, and test replication in both Studio and a live-like run before claiming it works. |
| Duplicate UI or callbacks after a remount | Subscriptions, states or loaders aren't owned. Give each mount its own subscriptions and state; borrow the shared infrastructure. Tear down producers before consumers, and keep feature teardown safe to repeat. |
| Construction throws and no cleanup comes back | `Subscribe` and `Blend.mount` acquire work before a throwing property or function stops them returning a handle. Clean up the caller-owned parts you can reach, and keep the smallest reproduction. Validate risky inputs before mounting. Don't claim caller rollback reaches the hidden resources. |
| `Brio is dead` | The Brio was used after death. Check `IsDead()` before use and after every yield. |
| `Bad promise` from `Rx.fromPromise` | A non-Nevermore Promise (for example Janitor's `evaera/promise`) was passed in. Use a Nevermore Promise, or adapt with `Observable.new`. |
| `attempt to call a nil value` on a loader | The loader was used after `Loader:Destroy()`, which removes the metatable. Don't destroy a shared loader per component. |
| Studio memory climbs while a story hot-reloads | Each `bootstrapStory` call registers the package root again. Pin loader 10.11.3 or later, which stops re-populating loader links, and route stories through a shared adapter that bootstraps once ([setup](setup.md)). |
| A UI Labs story leaks after an error | A function story can't return its cleanup on a failed construction. Clean up reachable resources before rethrowing; keep the borrowed target and loader. |
| `Rx.filter` is nil | Rx calls it `Rx.where`. |

## Verifying a claim

Check the pin against the actual project, then the project's own analysis, adapter, mapping and build checks (the reviewed project used `scripts/check.ps1`). Mount, update and unmount behavior, rendering, input, replication, late emissions and Output diagnostics all need a run in Studio. Source review and checker fixtures don't exercise them.
