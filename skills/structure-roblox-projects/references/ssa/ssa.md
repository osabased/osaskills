# Canonical SSA feature integration

Use this contract for structural and lifecycle work in recognized canonical Single Script Architecture (SSA). A canonical SSA area has the applicable `Server/` or `Client/` root, its entrypoint directly calls the pinned `ModuleLoader.Start(...)` on that root, and no conflicting startup convention is evident in the affected area.

Treat this signature as a fast, defeasible recognition check. Inspect bootstrap infrastructure only when evidence conflicts or the task changes it; then read [`ssa-bootstrap.md`](ssa-bootstrap.md). An internal edit inside an already placed feature that changes no placement, lifecycle, or structural integration remains on the established-project fast path.

## 1. Choose runtime ownership

Create only the boundaries the feature needs. Use matching feature names across boundaries when one capability spans them.

| Boundary | Ownership |
| --- | --- |
| `Server/<Feature>` | Authoritative or server-runtime behavior |
| `Client/<Feature>` | Client-runtime behavior |
| `Shared/<Feature>` | Client-visible code or data genuinely consumed by both runtimes |
| `Remotes/<Feature>` | Structurally defined cross-runtime communication instances |

These paths are relative to `ServerScriptService` for `Server/` and `ReplicatedStorage` for `Client/`, `Shared/`, and `Remotes/`. Shared ModuleScripts share source and visibility, not mutable runtime state; server and client execute them independently.

Represent the resulting DataModel through the active source-of-truth workflow. For Rojo, a feature directory can use `init.luau` so the directory maps to the lifecycle-root ModuleScript while retaining child implementation modules. Read [`rojo.md`](../workflows/rojo.md) or [`script-sync.md`](../workflows/script-sync.md) when that specialist branch is active.

## 2. Fill the discovery slot

> **Discovery slot:** A direct-child ModuleScript under `Server/` or `Client/` is a loader-owned lifecycle root.

Put child implementation modules beneath their owning feature root. Every ModuleScript in a discovery slot must intentionally participate as a lifecycle root; place helpers, APIs, and domain modules below that root or in an applicable Shared subtree.

`Shared/` modules are dependency modules, not loader-owned lifecycle roots.

## 3. Define the module contract

Top-level execution defines and returns the API and acquires explicit dependencies. Keep it safe when another module requires it before loader discovery: complete without activation or permanent yielding, and make no assumption that lifecycle methods already ran.

Lifecycle methods are optional:

- `Init` prepares feature-local state and dependencies.
- `Start` activates behavior such as event connections or long-running work, then returns after activation.

The loader attempts every successful load before it attempts any `Init`, then attempts `Start` after the Init phase. Within each phase, upstream honors `LoaderPriority` (higher first). Do not rely on incidental order among equal-priority siblings; use priority ordering only when it is an explicit startup contract.

A direct dependency on another lifecycle root is valid when it makes ownership clearer, but `require()` returns that module's API; it does not imply that the dependency's `Init` or `Start` has run. Keep requires acyclic. Move lifecycle-independent access into a nested API/domain module or an applicable Shared module when that makes the dependency explicit.

## 4. Define cross-runtime readiness

Place structural communication instances under `ReplicatedStorage/Remotes/<Feature>` through the active source-of-truth workflow. When one runtime must wait for feature state from the other, define that contract with replicated state, request/response, or a feature-specific ready signal.

Server or client loader completion is startup progress, not proof that a cross-runtime feature protocol is ready.

## 5. Keep ownership local

A feature change owns its lifecycle roots, their descendants, required Shared and Remotes structure, explicit dependencies, lifecycle methods, protocol, and focused validation.

Loader acquisition, entrypoints, discovery settings, loader-wide configuration, and upgrades are infrastructure work. Route those requirements to [`ssa-bootstrap.md`](ssa-bootstrap.md) instead of configuring the loader from an ordinary feature.

## 6. Validate the feature

Run the available focused static, type, lint, and build checks that cover the changed surface. When runtime behavior changed, run the smallest relevant Studio server/client startup.

Completion requires all of the following:

- no new loader load, Init, or Start warning attributable to the changed feature;
- direct evidence that the changed feature behavior works; and
- every new helper is nested outside a discovery slot and every lifecycle dependency remains acyclic.

Loader loaded-state attributes alone do not establish lifecycle success. Report unrelated pre-existing failures without expanding the write set to repair them.

Feature integration is complete when the required server-only, client-only, or cross-runtime behavior has an unambiguous home and protocol, joins startup without an entrypoint or loader edit, and passes the focused checks above.
