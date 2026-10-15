# Script Sync

Use when enabling, disabling or changing Script Sync boundaries, resolving sync conflicts, or moving content into, out of or within a synced folder. A routine edit inside a stable boundary doesn't need this.

Script Sync syncs `Script`, `LocalScript`, `ModuleScript` and `Folder` instances between Studio and disk in both directions; other instances inside a synced folder are ignored. Roblox recommends syncing folders, which pick up child creates, renames, moves and deletes, and avoiding folders that mix scripts with other instance types.

## Before changing a boundary

1. Check the Studio settings when you can see them: **Auto resume sync on place open**, **Resume conflicted sync on place open**, **Keep local files/directories after sync**, **File extension**. If you can't and reopen behavior matters, call it an unverified risk.
2. List the affected scripts and folders: type or `RunContext`, attributes, tags, children, package status.
3. Limits: up to 10,000 scripts per top-level synced instance and 128 top-level synced instances. Recheck the current page before relying on them.
4. File names set the type: `name.luau` is a `ModuleScript`; `.server.luau`, `.client.luau`, `.local.luau`, `.legacy.luau` and `.plugin.luau` set the script class and `RunContext`; `name/init.*.luau` is a script with children. These suffixes are Script Sync's own; Rojo reads `.local` and `.legacy` as ModuleScripts. Check for duplicate or filesystem-incompatible names.
5. **Attributes and tags are not synced.** Roblox warns they can be lost when scripts are created or deleted, or when sync starts from older files on disk. Plan how to keep them before changing those scripts.
6. To remove a top-level synced root, use Studio's Stop Sync and delete it there, not on disk. Script Sync deletes only files it manages.
7. In Team Create, people syncing and editing the same script overwrite each other. Packages sync, but `PackageLink` isn't written to disk.
8. When starting or resuming with differences, read the conflict dialog's planned adds, modifications and deletions before choosing **Keep Studio** or **Keep Disk**.

Afterward, check the affected types, `RunContext`s, attributes, tags, children and packages, and that nothing unintended was written on either side.

## Source

- [Script Sync](https://create.roblox.com/docs/scripting/sync)
