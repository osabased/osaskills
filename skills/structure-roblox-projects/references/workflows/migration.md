# Roblox structural migration

This reference has two uses:

- **Explicit migration workflow:** use the full workflow only when the user explicitly requests a migration, conversion, transition, or migration plan. Migration intent comes from the request, not from the technical operations the work happens to require.
- **Structural-change safeguards:** ordinary Review, Design, or Implementation work may use only the applicable tracing, recovery, specialist-boundary, or validation guidance below when moves, renames, topology/identity changes, source-of-truth-sensitive edits, or multi-step restructuring create those failure modes. Consulting these safeguards does not activate the Migration route or its exhaustive completion criterion.

## Account for an explicit migration

For the full Migration route:

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
3. When required writes cross an unclear or protected boundary, read [`modification-scope.md`](../core/modification-scope.md) and classify those writes before planning an executable slice.
4. Load specialist guidance when either the current structure or requested target structure can exercise that boundary:
   - [`server-authority.md`](../platform/server-authority.md) for migration that preserves, introduces, removes, or changes Server Authority prediction/rollback or shared deterministic simulation;
   - [`script-capabilities.md`](../platform/script-capabilities.md) for migration that preserves, introduces, removes, or changes an active or requested Script Capabilities boundary;
   - [`script-sync.md`](script-sync.md) when moving or renaming content into, out of, or within Script Sync management can change sync representation, metadata, child shape, packages, or conflict behavior; and
   - [`rojo.md`](rojo.md) when moving or renaming content into, out of, or within Rojo mapping can change the resulting DataModel through path, filename, `init.*`, suffix, nested-project, metadata, or mapping semantics.

Express the plan as concrete migration slices, not only phases. For each slice record: current item/path and target item/path; affected callers, `require`s, Remotes, mappings, configuration, and tests; the authoritative source before and after; the exact cutover step that prevents dual ownership; required owner actions; the recovery boundary; and the focused verification that closes the slice. Items that do not move but need reference or topology updates still belong in a slice. If any field is unknown, name the evidence needed rather than replacing it with a generic “update references” step.

When the prompt supplies only artifact names or hierarchy categories, treat those as the planning inventory. Produce one provisional slice per material category (entrypoints, shared/server/client roots, packages, metadata-sensitive children, and mapping/configuration as applicable), use explicit placeholders only for unresolved leaf paths, and attach the relevant reference traces and verification to each slice. Missing contents lower path-level confidence; they do not justify returning only a plan-to-plan.

For an ordinary structural change, apply only the items above that are needed to keep the requested change coherent and safe. Do not inventory an unrelated target architecture or satisfy migration-wide accounting merely because one safeguard applies.

## Slice and recovery

For an explicit migration, define minimum coherent slices: each slice should move a concept once and update the references needed for that slice to work.

For ordinary structural work, use a coherent slice only when the change is multi-step or a partial application would leave the affected behavior broken.

Give a slice an explicit recovery boundary when it is destructive, topology-sensitive, non-version-controlled, externally stateful, or otherwise difficult to reverse. Version control is sufficient recovery for routine reversible filesystem edits when the affected writes are fully captured there.

For a source-of-truth migration, name when writes freeze in the old owner, how the final state is captured, which side wins any conflict, when the new owner becomes authoritative, and how to return to the old owner without split-brain edits. A tool installation or first successful sync is not itself the cutover.

A slice is blocked when coherent completion requires a protected write that is not authorized. State the minimum owner action instead of applying a partial topology that cannot work.

## Structural checks

Check only the failure modes the affected change can exercise:

- cyclic or newly invalid dependency direction;
- accidental replication of authoritative-only logic or data;
- broken startup, discovery, registration, or identity assumptions;
- changed Script Sync representation, metadata, package, or conflict behavior;
- changed Rojo effective mapping or resulting DataModel topology;
- changed Server Authority prediction/rollback boundaries; and
- changed Script Capabilities sandbox semantics.

After topology- or identity-sensitive moves, exercise affected discovery or registration behavior when a representative runtime is available. When entrypoints, Remotes, networking behavior, or replicated modules/state change, validate the applicable server/client or multi-client path. Server Authority simulation changes use the network validation in `../platform/server-authority.md`.

The exhaustive migration completion criterion applies only to the explicit Migration route: migration planning is complete when every move, affected reference, material topology/identity assumption, required owner action, specialist boundary, verification step, and necessary recovery boundary is accounted for. Ordinary structural work finishes according to its selected Review, Design, or Implementation route after the applicable safeguards and focused validation are satisfied.
