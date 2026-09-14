# Script Sync safeguards

Use this reference when reviewing, designing, planning, enabling, disabling, or changing Script Sync behavior or boundaries; resuming or resolving sync conflicts; or moving/renaming content into, out of, or within Script Sync management where sync representation, metadata, child shape, packages, or conflict behavior can matter. A routine source edit inside a stable sync boundary does not require this reference.

Script Sync synchronizes `Script`, `LocalScript`, `ModuleScript`, and `Folder` instances between Studio and local disk. Changes made to Luau files on disk are applied to scripts in Studio, and changes made in Studio are applied to disk. Other instances inside a synced folder are ignored by Script Sync.

Use Script Sync when the project should use an external text editor or code version control while continuing to use Studio for everything else. If the entire project, not just code, should be checked into version control or the filesystem should be the source of truth, Roblox identifies third-party tools such as Rojo as the better choice.

Roblox highly recommends syncing folders rather than individual scripts. Folder sync automatically includes child folders and scripts and synchronizes create, rename, move, and delete operations on managed children. Avoid syncing folders that contain scripts alongside other instance types because Script Sync ignores those other instances.

## Before changing the boundary or managed topology

1. When Studio settings are accessible, inspect the relevant Script Sync behavior: **Auto resume sync on place open**, **Resume conflicted sync on place open**, **Keep local files/directories after sync**, and **File extension**. Treat unavailable reopen/resume behavior as an unverified risk when it matters to the operation.
2. Inventory affected scripts and folders, including script names, class or RunContext, attributes, tags, children, package status, and modification scope.
3. Narrow the boundary to authorized work when it contains protected content. Use [`modification-scope.md`](modification-scope.md) when a required script, folder, metadata migration, or consumer update crosses that boundary.
4. Check duplicate or filesystem-incompatible names. Preserve Script Sync's documented on-disk type conventions: `name.luau` represents a `ModuleScript`; `name.server.luau`, `name.client.luau`, `name.local.luau`, `name.legacy.luau`, and `name.plugin.luau` represent the corresponding documented script types and RunContext values; `name/init.*.luau` represents a script instance with children. Verify that the intended script type, RunContext, and parent/child shape survive synchronization.
5. If removing or replacing a top-level synced root, follow Studio's current Stop Sync/root-deletion workflow rather than treating the root like an ordinary disk child.
6. Identify every affected script with attributes or tags. Script Sync does not carry that metadata, so either keep the script Studio-owned outside the boundary or deliberately migrate the metadata to a reviewed source and update its authorized consumers.
7. With Team Create or multiple local editors, account for overlapping collaborators or sync processes. Avoid simultaneous editing of the same synced script when possible because collaborators can overwrite one another. For packages, account for metadata not represented on disk, including `PackageLink`.
8. Resolve each conflict preview intentionally. If reopen/resume settings automatically prefer Studio or disk, account for that precedence before resuming.

Proceed with a topology change only when every metadata-bearing script has a preservation strategy and every planned content or metadata write is authorized.

## Review

For a read-only Script Sync review, apply the same representation and metadata checks that are material to the review question, but do not require a mutation plan when no change is proposed. Report unavailable Studio settings or conflict behavior only when they can affect the conclusion.

## Validation

After a change, verify affected script types, RunContext values, attributes, tags, children, package behavior, source boundaries, and the absence of unintended writes in Studio and on disk.

Script Sync manages scripts and folders rather than the wider DataModel. When the entire project must live in version control or the filesystem must be the project's source of truth, evaluate a filesystem-first tool such as Rojo instead.

Re-open current Roblox Script Sync documentation before version- or workflow-sensitive destructive operations.

## Source

- [Script Sync](https://create.roblox.com/docs/scripting/sync)
