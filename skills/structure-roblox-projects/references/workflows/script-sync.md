# Script Sync safeguards

Use when reviewing, designing, enabling, disabling, or changing Script Sync behavior or boundaries; resuming or resolving sync conflicts; or moving or renaming content into, out of, or within Script Sync management where representation, attributes/tags, child shape, packages, or conflicts can matter. A routine source edit inside a stable sync boundary doesn't need this reference. For when to choose Script Sync over Rojo, see [source of truth](../core/practices.md#source-of-truth).

Script Sync syncs `Script`, `LocalScript`, `ModuleScript`, and `Folder` instances between Studio and local disk in both directions. Other instances inside a synced folder are ignored.

Roblox highly recommends syncing folders rather than individual scripts: a synced folder automatically includes child folders and scripts and syncs create, rename, move, and delete operations. Avoid syncing folders that mix scripts with other instance types, because those other instances are ignored.

## Before changing the boundary or managed topology

1. When Studio settings are accessible, check **Auto resume sync on place open**, **Resume conflicted sync on place open**, **Keep local files/directories after sync**, and **File extension**. If you can't see them and reopen/resume behavior matters, treat it as an unverified risk.
2. List affected scripts and folders: names, script type or RunContext, attributes, tags, children, package status, and edit permission.
3. If the boundary could approach platform limits, check it. Roblox documents up to **10,000 scripts per top-level synced instance** and **128 top-level synced instances**; re-check the current page before relying on exact limits.
4. Narrow the boundary to authorized work when it contains protected content. Use [`modification-scope.md`](../core/modification-scope.md) when a required script, folder, attribute/tag step, or consumer update crosses that boundary.
5. Check for duplicate or filesystem-incompatible names. Keep the on-disk type conventions: `name.luau` is a `ModuleScript`; `name.server.luau`, `name.client.luau`, `name.local.luau`, `name.legacy.luau`, and `name.plugin.luau` are the corresponding script types and RunContexts; `name/init.*.luau` is a script with children. Confirm the intended type, RunContext, and parent/child shape survive syncing.
6. To remove or replace a top-level synced root, use Studio's Stop Sync and delete workflow; don't delete the root on disk like an ordinary child. Script Sync deletes only the files it manages: unmanaged files and non-script assets remain. Inspect both sides afterwards.
7. Find affected scripts with attributes or tags. Script Sync ignores them, and Roblox warns this can lose data when scripts are created or deleted or when syncing starts from older disk files. Have an explicit preservation plan before changing those scripts through sync.
8. With Team Create, avoid several people syncing and editing the same script at once; collaborators can overwrite each other. Packages can be synced, but `PackageLink` itself is not written to disk.
9. When starting or resuming sync with differences between Studio and disk, inspect the conflict dialog's planned adds, modifications, and deletions before choosing **Keep Studio** or **Keep Disk**. Account for any configured **Resume conflicted sync on place open** preference.

Proceed with a topology change only when every affected attribute/tag-bearing script has a preservation plan, every planned write is authorized, and limits are respected.

## Review

For a read-only review, apply the representation, attributes/tags, package, naming, limit, and conflict checks the question needs. No mutation plan is needed when no change is proposed. Mention unavailable Studio settings only when they could change the conclusion.

## Validation

After a change, check affected script types, RunContexts, attributes, tags, children, package behavior (including `PackageLink` where relevant), source boundaries, and that nothing unintended was written in Studio or on disk. If limits mattered, confirm the resulting counts.

## Source

- [Script Sync](https://create.roblox.com/docs/scripting/sync): sync direction, use cases, folder sync, limits, conflict resolution, Team Create, supported instance types, packages, attributes/tags, naming rules, root deletion, settings.
