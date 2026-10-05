# Diagnose Nevermore integration failures

Use for a matching symptom. Follow the [entrypoint](../SKILL.md) and installed parent's shared repair contract; preserve the four npm pins and current project ownership.

| Symptom | Check and correction |
| --- | --- |
| Declaration or source-integrity mismatch | Inspect package.json, the root/direct package-lock entries, npm aliases, exact archive URL/integrity and the actual source directory. Restore through the project preparation route; do not upgrade a pin or edit generated source to make the checker pass. |
| `script.Parent.loader` missing or a named package cannot be found | Inspect the root adapter, mapped package topology and loader population. Require the shared adapter rather than raw Blend.lua; bootstrap belongs to the root owner. Read [setup](setup.md). |
| Server-only packages visible in a Studio client | Inspect bootstrap options and mappings. The default Studio fast path differs from production filtering; preserve the project's `skipStudioFastPath = true` boundary and test replication in both contexts when claiming it. |
| Duplicate UI or callbacks after remount | Locate unowned subscriptions, states and loader roots. Each view mount owns its own subscriptions/state and borrows shared infrastructure. Teardown must stop producers before consumers and be safe under repeated feature disposal. |
| Construction throws before cleanup is returned | Dispose reachable caller-owned acquisitions and retain the smallest reproduction. Blend.mount and Observable.Subscribe can acquire internal work before a throwing property/function prevents a handle from returning. Do not claim caller rollback reaches those hidden resources. Validate risky inputs first; inspect/fix the exact package boundary under parent repair or choose an explicitly owned construction path whose failure behavior is tested. |
| Dead Brio access or stale async result | Check `IsDead` before value access and again after each yield; own cancellation/cleanup separately. A retained Lua value does not extend a Brio lifetime. Read [Brio](brio.md). |
| Rx promise type assertion | Rx.fromPromise requires Nevermore Promise's identity. Read [Rx](rx.md); do not pass Janitor's transitive evaera Promise as an interchangeable type. |
| UI Labs mount has no cleanup after an error | A story cannot return its cleanup on a failed construction path. Dispose reachable feature resources before rethrowing; preserve the borrowed story target and shared loader. Apply the pinned UI Labs child when changing its story API. |

An unknown/missing matching resource record enters parent reconciliation. Known blocks, changed selectors, hard ownership/security defects or failed identity checks stop dependent use. A recurring safe local workaround still needs durable parent repair diagnosis.

## Verify the affected claim

Run declaration and installed-integrity checks at the actual project. The four direct npm packages and reviewed Lua aggregates are checked; transitive lock resolution and generated mapping are project integration responsibilities. Run the project's authored-source analysis, adapter/mapping and build checks (`scripts/check.ps1` was the original project's route). Dependency scripts remain disabled during locked restoration unless separately reviewed and authorized.

Studio/MCP is required for mount/update/unmount, rendered state, actual input, client/server replication, late emissions and diagnostics claims. Source review, checker fixtures and instruction-response tasks do not execute those lanes. Preserve existing exact-target proof in its own record; bundle installation alone is installed state.
