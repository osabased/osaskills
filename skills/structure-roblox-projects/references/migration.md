# Roblox structural migration

Use this reference for moves, renames, topology changes, source-of-truth migrations, or multi-step restructuring where identity, mappings, consumers, or rollback can be affected.

## Account for the migration

1. Inventory the current and target hierarchies, effective authoring mappings, entrypoints, and every proposed move or rename.
2. Trace every affected reference and assumption, including:
   - `require` calls and string paths;
   - loader and discovery conventions;
   - Remote or Bindable lookups;
   - callers and test references;
   - script attributes and tags;
   - effective Rojo project/meta/model mappings when applicable;
   - `script.Parent` and other ancestry or sibling traversal;
   - `script.Name`, `GetFullName()`, and name- or path-derived registrations; and
   - topology- or identity-sensitive discovery behavior.
3. When required writes cross an unclear or protected boundary, read [`modification-scope.md`](modification-scope.md) and classify those writes before planning an executable slice.
4. Load every specialist reference whose trigger is present: [`server-authority.md`](server-authority.md), [`script-capabilities.md`](script-capabilities.md), [`script-sync.md`](script-sync.md), or [`rojo.md`](rojo.md).

## Slice and recovery

Define minimum coherent slices: each slice should move a concept once and update the references needed for that slice to work.

Give a slice an explicit recovery boundary when it is destructive, topology-sensitive, non-version-controlled, externally stateful, or otherwise difficult to reverse. Version control is sufficient recovery for routine reversible filesystem edits when the affected writes are fully captured there.

A slice is blocked when coherent completion requires a protected write that is not authorized. State the minimum owner action instead of applying a partial topology that cannot work.

## Structural checks

For every affected branch, check the relevant failure modes:

- cyclic or newly invalid dependency direction;
- accidental replication of authoritative-only logic or data;
- broken startup, discovery, registration, or identity assumptions;
- changed Script Sync metadata or conflict behavior;
- changed Rojo effective mapping;
- changed Server Authority prediction/rollback boundaries; and
- changed Script Capabilities sandbox semantics.

After topology- or identity-sensitive moves, exercise affected discovery or registration behavior when a representative runtime is available. When entrypoints, Remotes, networking behavior, or replicated modules/state change, validate the applicable server/client or multi-client path. Server Authority simulation changes use the network validation in `server-authority.md`.

Migration planning is complete when every move, affected reference, material topology/identity assumption, required owner action, specialist boundary, verification step, and necessary recovery boundary is accounted for.