# Modification scope

Use this reference when a proposed write may cross an unclear, shared, generated, or protected boundary; when a dirty worktree makes ownership ambiguous; or when a broad tool can write outside the immediately requested files or instances.

## Classify only the affected boundary

Classify the relevant content, not the whole project:

- **Authorized work:** assigned content and new artifacts clearly belonging to the deliverable; these may change.
- **Inspectable context:** surrounding content needed to understand conventions, compatibility, dependencies, or integration; keep it read-only unless separately authorized.
- **Protected content:** user-, maintainer-, developer-, or other owner-controlled content outside the assigned work; keep it read-only.
- **Integration-required content:** protected content whose change may be required for a coherent integration; keep it read-only until authority expands or its owner takes the change.

Access, architectural preference, project conventions, profiles, dependency reach, source-of-truth ownership, validation failures, and technical necessity are context, not permission.

## Before mutation

1. Identify the complete intended write set for the risky operation, including mappings, manifests, package pins, lockfiles, generated files, snapshots, profiles, formatter output, and other indirect writes.
2. Keep incidental cleanup and unrelated fixes outside that set.
3. In a version-controlled worktree, inspect relevant status and existing diffs when pre-existing changes or broad writes could overlap the operation. Preserve unrelated modifications; do not reset, clean, revert, checkout, or rewrite them to obtain a clean state.
4. Constrain generators, formatters, dependency operations, sync tools, and snapshot updates to authorized outputs when the tool permits it.

## Boundary crossing

When coherent integration needs a protected edit:

1. Prefer an adapter, configuration, compatibility seam, or extension point inside authorized work when it is the smallest maintainable solution.
2. Avoid lasting compatibility machinery whose only purpose is to evade a simpler protected edit.
3. If no coherent in-scope solution exists, leave the protected write unapplied and state the minimum required change, why it is needed, the practical alternatives, the validation impact, and whether approval or an owner handoff is required.

Scope resolution is complete when every proposed write is either authorized or explicitly blocked as integration-required.