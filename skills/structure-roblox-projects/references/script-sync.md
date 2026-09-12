# Script Sync safeguards

Use this reference when enabling Script Sync, changing a sync boundary, resuming or resolving sync conflicts, or moving metadata-bearing scripts into or out of synchronized content.

Script Sync manages `Script`, `LocalScript`, `ModuleScript`, and `Folder` instances as a bidirectional Studio-and-disk synchronization boundary. Other instances inside a synced folder remain Studio-owned. Prefer code-focused sync roots when practical so the filesystem representation does not imply ownership of ignored Studio content.

## Before changing the boundary

1. When Studio settings are accessible, inspect the relevant Script Sync behavior: **Auto resume sync on place open**, **Resume conflicted sync on place open**, **Keep local files/directories after sync**, and **File extension**. Treat unavailable reopen/resume behavior as an unverified risk when it matters to the operation.
2. Inventory affected scripts and folders, including script names, class or RunContext, attributes, tags, children, package status, and modification scope.
3. Narrow the boundary to authorized work when it contains protected content. Use [`modification-scope.md`](modification-scope.md) when a required script, folder, metadata migration, or consumer update crosses that boundary.
4. Check duplicate or filesystem-incompatible names. When a script owns child instances, account for the `init.*` representation using the configured extension and verify that the intended parent/child shape survives synchronization.
5. If removing or replacing a top-level synced root, follow Studio's current Stop Sync/root-deletion workflow rather than treating the root like an ordinary disk child.
6. Identify every affected script with attributes or tags. Script Sync does not carry that metadata, so either keep the script Studio-owned outside the boundary or deliberately migrate the metadata to a reviewed source and update its authorized consumers.
7. With Team Create or multiple local editors, account for overlapping collaborators or sync processes. For packages, account for metadata not represented on disk, including `PackageLink`.
8. Resolve each conflict preview intentionally. If reopen/resume settings automatically prefer Studio or disk, account for that precedence before resuming.

Proceed only when every metadata-bearing script has a preservation strategy and every planned content or metadata write is authorized.

## Validation

After the change, verify affected script types, RunContext values, attributes, tags, children, package behavior, source boundaries, and the absence of unintended writes in Studio and on disk.

Script Sync owns scripts and folders rather than the wider DataModel. When the filesystem must own broader hierarchy, evaluate Rojo instead of stretching the sync boundary.

Re-open current Roblox Script Sync documentation before version- or workflow-sensitive destructive operations.

## Source

- [Script Sync](https://create.roblox.com/docs/scripting/sync)