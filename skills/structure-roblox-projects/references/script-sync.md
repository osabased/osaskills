# Script Sync safeguards

Use this reference when reviewing, designing, planning, enabling, disabling, or changing Script Sync behavior or boundaries; resuming or resolving sync conflicts; or moving/renaming content into, out of, or within Script Sync management where sync representation, attributes/tags, child shape, packages, or conflict behavior can matter. A routine source edit inside a stable sync boundary does not require this reference.

Script Sync synchronizes `Script`, `LocalScript`, `ModuleScript`, and `Folder` instances between Studio and local disk. Changes made to Luau files on disk are applied to scripts in Studio, and changes made in Studio are applied to disk. Other instances inside a synced folder are ignored by Script Sync.

Use Script Sync when the project should use an external text editor or code version control while continuing to use Studio for everything else. If the entire project, not just code, should be checked into version control or the filesystem should be the source of truth, Roblox identifies third-party tools such as Rojo as the better choice.

Roblox highly recommends syncing folders rather than individual scripts. Folder sync automatically includes child folders and scripts and synchronizes create, rename, move, and delete operations on managed children. Avoid syncing folders that contain scripts alongside other instance types because Script Sync ignores those other instances.

## Before changing the boundary or managed topology

1. When Studio settings are accessible, inspect the relevant Script Sync behavior: **Auto resume sync on place open**, **Resume conflicted sync on place open**, **Keep local files/directories after sync**, and **File extension**. Treat unavailable reopen/resume behavior as an unverified risk when it matters to the operation.
2. Inventory affected scripts and folders, including script names, script type or RunContext, attributes, tags, children, package status, and modification scope.
3. Narrow the boundary to authorized work when it contains protected content. Use [`modification-scope.md`](modification-scope.md) when a required script, folder, attribute/tag preservation step, or consumer update crosses that boundary.
4. Check duplicate or filesystem-incompatible names. Preserve Script Sync's documented on-disk type conventions: `name.luau` represents a `ModuleScript`; `name.server.luau`, `name.client.luau`, `name.local.luau`, `name.legacy.luau`, and `name.plugin.luau` represent the corresponding documented script types and RunContext values; `name/init.*.luau` represents a script instance with children. Verify that the intended script type, RunContext, and parent/child shape survive synchronization.
5. If removing or replacing a top-level synced root, follow Studio's documented Stop Sync/root-deletion workflow rather than treating the root like an ordinary disk child.
6. Identify affected scripts with attributes or tags. Script Sync ignores attributes and tags, and Roblox warns this can lead to data loss when scripts are created/deleted or when syncing starts with older disk files. Require an explicit preservation strategy before changing those scripts through the sync boundary.
7. With Team Create, avoid workflows where multiple people sync the same script and edit the files at the same time because Roblox documents that collaborators can overwrite each other's changes. Packages can be synced, but `PackageLink` itself is not written to disk.
8. When starting or resuming sync with differences between Studio and disk, inspect the conflict-resolution dialog and its planned adds, modifications, and deletions before choosing **Keep Studio** or **Keep Disk**. If **Resume conflicted sync on place open** is configured to prefer Studio or disk, account for that configured behavior.

Proceed with a topology change only when every affected attribute/tag-bearing script has a preservation strategy and every planned content or metadata write is authorized.

## Review

For a read-only Script Sync review, apply the representation, attributes/tags, package, naming, and conflict checks that are material to the review question, but do not require a mutation plan when no change is proposed. Report unavailable Studio settings or conflict behavior only when they can affect the conclusion.

## Validation

After a change, verify affected script types, RunContext values, attributes, tags, children, package behavior including `PackageLink` where relevant, source boundaries, and the absence of unintended writes in Studio and on disk.

Script Sync only synchronizes `Script`, `LocalScript`, `ModuleScript`, and `Folder` instances; other instances in a synced folder are ignored. When the entire project must live in version control or the filesystem must be the project's source of truth, Roblox identifies third-party tools such as Rojo as the better choice.

Re-open current Roblox Script Sync documentation before version- or workflow-sensitive destructive operations.

## Official evidence

All platform-specific claims in this reference are grounded in Roblox Creator Hub:

- [Script Sync](https://create.roblox.com/docs/scripting/sync): synchronization direction, recommended use cases, folder sync, limits, conflict resolution, Team Create behavior, supported instance types, package behavior, attributes/tags, filesystem naming requirements, root deletion, on-disk naming rules, and settings.
- [Third-party tools](https://create.roblox.com/docs/projects/external-tools): Script Sync for external editing/code version control and Rojo's file system-first workflow.
