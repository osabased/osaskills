# Canonical SSA feature contract

Use this reference for ordinary feature work inside canonical greenfield SSA. It should be enough to place, integrate, and validate a feature without inspecting bootstrap entrypoints, loader internals, loader attributes, acquisition details, or registration lists.

## Canonical structure

Conceptually:

```text
ReplicatedStorage/
  Client/
    <Feature>
  Shared/
    <Feature>
  Remotes/
    <Feature>

ServerScriptService/
  Server/
    <Feature>
```

Use matching feature names across runtime boundaries when one feature spans more than one boundary. A feature needs only the boundaries its behavior actually requires. The exact filesystem representation follows the project's source-of-truth workflow; when Rojo is active, use [`rojo.md`](rojo.md) for mapping details.

## Feature roots and discovery

A direct-child `ModuleScript` under canonical `Server/` or `Client/` is a loader-owned lifecycle feature root.

That invariant makes ordinary integration mechanical:

- create the feature root directly under the applicable canonical runtime container;
- place implementation/helper modules beneath the owning feature root instead of beside it;
- add no feature-registration list and make no entrypoint edit for an ordinary feature.

In Rojo-style filesystem projects, an `init.luau` feature root can map a feature directory to a `ModuleScript` while retaining child implementation modules.

## Runtime ownership

- `Server/` owns authoritative/server runtime lifecycle feature roots.
- `Client/` owns client runtime lifecycle feature roots.
- `Shared/` owns dependencies intentionally consumed by both sides; it is not a loader-owned lifecycle container.
- `Remotes/<Feature>` is the canonical greenfield grouping for fixed cross-runtime communication instances needed by the feature.

Keep authoritative state, privileged rules, validation, persistence, purchases, and other trusted behavior on the server. Treat client-visible code and data as inspectable.

## Lifecycle

The loader processes discovered modules in phases:

```text
discover
→ require/load
→ Init
→ Start
→ loaded state
```

`Init` and `Start` are optional.

### Top-level execution

At module load time:

- define and export the feature;
- acquire explicit dependencies;
- keep activation out of top-level execution;
- leave long-running work for `Start`.

### Init

Use `Init` only when feature-local initialization is needed. Establish feature-local state and dependencies there.

All discovered modules are loaded before the Init phase begins, but sibling `Init` order is not a dependency guarantee. Do not make one feature's `Init` depend on another same-priority feature's `Init` having already run, and do not wait for another feature's `Start` from `Init`.

### Start

Use `Start` only when runtime activation is needed. Connect events, start long-running work, and activate runtime behavior there, then return after activation.

The Start phase begins after the Init phase has been attempted. Sibling `Start` order is not a dependency guarantee.

## Dependencies

Dependencies are explicit. Feature code should depend on stable feature or shared modules rather than on `ServerMain` or `ClientMain`.

Lifecycle ordering is not dependency injection. When Feature A needs Feature B's API, require or otherwise express that dependency directly through the project's established module conventions instead of manufacturing lifecycle coupling.

## Ordinary feature write boundary

Ordinary feature work may normally create or modify:

- the feature root;
- nested implementation modules owned by the feature;
- applicable shared dependencies;
- applicable fixed remotes;
- focused tests or validation artifacts already supported by the project.

Ordinary feature work should leave bootstrap and discovery infrastructure alone. If the feature genuinely requires a change to `ServerMain`, `ClientMain`, ModuleLoader internals, loader-wide settings, the selected loader, or discovery machinery, route the task through [`ssa-bootstrap.md`](ssa-bootstrap.md) as infrastructure work.

## Failure and validation

The upstream loader logs lifecycle failures instead of turning every lifecycle failure into one global startup failure. Therefore loaded-state attributes do not prove that every lifecycle method succeeded, and a failed `Init` does not by itself imply that that module's `Start` was skipped.

Treat loader load/init/start warnings as validation failures.

For lifecycle or startup-affecting feature work, use the smallest applicable checks plus runtime evidence:

```text
static/type/lint/build checks as applicable
→ Studio server/client startup
→ no loader load/init/start failure warnings
→ validate the changed feature behavior
```

The ordinary feature path is complete when a fresh agent can add a typical feature without inspecting bootstrap entrypoints, loader source, loader attributes, acquisition details, or registration machinery.
