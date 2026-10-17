# Script Sync

Use when a project's code reaches Studio through Script Sync: editing synced files, changing a boundary, resolving a conflict, setting up checks, or keeping dev content out of a published place.

Script Sync syncs `Script`, `LocalScript`, `ModuleScript` and `Folder` instances between Studio and disk in both directions; other instances inside a synced folder are ignored. Roblox recommends syncing folders, which pick up child creates, renames, moves and deletes, and avoiding folders that mix scripts with other instance types. The files don't show where each synced root sits in the DataModel, so the project guide records each root's DataModel path and directory.

## Agent edits

- Disk edits reach Studio only while Studio has the place open and syncing. Files that change while Studio is closed raise a resolution prompt when the place reopens, and the default **Resume conflicted sync on place open** setting, **Do not resume**, waits for someone to resolve it.
- Anything that rewrites files changes the open place too: `git checkout`, `stash` and `reset`, formatters, generators. A child file deleted on disk deletes its script (deleting a synced root on disk can make Studio throw an error; see step 6 below), and a script recreated from disk is a new instance without its old attributes and tags.
- Before a play-test, [confirm Studio runs your bytes](verification.md#play-tests-with-studio-mcp).
- The suffix sets the class, so choose it for where the script runs ([facts models get wrong](../SKILL.md#facts-models-get-wrong)): `.client.luau` is a `Script` with `RunContext = Client`, which runs from `ReplicatedStorage` and runs twice from `StarterPlayerScripts` or `StarterCharacterScripts`; `.local.luau` is a `LocalScript`, which never runs in `ReplicatedStorage`.
- Studio's debugger can't be controlled from an external editor.

## Before changing a boundary

1. Check the Studio settings when you can see them: **Auto resume sync on place open**, **Resume conflicted sync on place open**, **Keep local files/directories after sync**, **File extension**. If you can't and reopen behavior matters, call it an unverified risk.
2. List the affected scripts and folders: type or `RunContext`, attributes, tags, children, package status.
3. Limits: up to 10,000 scripts per top-level synced instance and 128 top-level synced instances. Recheck the current page before relying on them.
4. File names set the type: `name.luau` is a `ModuleScript`; `.server.luau`, `.client.luau`, `.local.luau`, `.legacy.luau` and `.plugin.luau` set the script class and `RunContext`; `name/` is a `Folder`; `name/init.*.luau` is a script with children. These suffixes are Script Sync's own; Rojo reads `.local` and `.legacy` as ModuleScripts. Check for duplicate or filesystem-incompatible names.
5. **Don't sync scripts that have attributes or tags.** Script Sync ignores both, and Roblox warns they can be lost when scripts are created or deleted, or when sync starts from older files on disk. Move that data off the scripts or leave them out of synced folders.
6. To remove a top-level synced root, use Studio's Stop Sync and delete it there, not on disk. Script Sync deletes only files it manages.
7. In Team Create, people syncing and editing the same script overwrite each other. Packages sync, but `PackageLink` isn't written to disk.
8. When starting or resuming with differences, read the conflict dialog's planned adds, modifications and deletions before choosing **Keep Studio** or **Keep Disk**.

Afterward, check the affected types, `RunContext`s, attributes, tags, children and packages, and that nothing unintended was written on either side.

## Checks

The [check command](checks.md#one-check-command) runs restore, guards, codegen, tests, format, lint and types on the synced files. It has no build or topology step: guards see only the disk side, and what surrounds the synced roots is visible only through Studio.

- **Types without a sourcemap:** `luau-lsp analyze` resolves relative string requires (`require("./Util")`) from disk. They resolve the same way in Studio where the disk layout matches the DataModel, as it does for the synced contents of one root. Instance requires (`require(ReplicatedStorage.Shared.Util)`, `require(script.Parent.Helper)`) and `@game/` paths fail as unknown requires. Verified with luau-lsp 1.70.1.
- **Sourcemap in the editor:** with the companion Studio plugin connected and `luau-lsp.studioPlugin.enabled` set in VS Code (`luau-lsp.plugin.enabled` before 1.66.0), luau-lsp 1.60.0 and later writes `sourcemap.json` from the synced place. Its file paths are absolute and machine-specific, and the file goes stale once Studio disconnects, so CI can't use it.
- **Sourcemap in CI:** generate one in the check under its own file name and pass it with `--sourcemap`, since a connected editor rewrites `sourcemap.json` with absolute paths. Walk each recorded root's directory, apply the naming rules above, and nest the result under the root's DataModel path. A Rojo-style sourcemap with relative file paths type-checks all three require styles (luau-lsp 1.70.1).
- Don't add a Rojo project file only to get a sourcemap: Rojo reads `.local.luau` and `.legacy.luau` as ModuleScripts, and a project file invites `rojo serve`, a second sync system on the same content.
- **Packages:** don't sync an install folder. Script Sync skips directories whose names start with a dot and ignores each package's `default.project.json`. So pesde's link modules, which require into `.pesde`, fail, and so do Wally's, which require each package's root folder, usually a module only through its project file. It also syncs bundled test runners such as `*.server.lua` as Scripts that run. Keep packages outside synced roots, for example as a model built from the install folder with `rojo build`, and rebuild it after each install. Verified in Studio 0.743 with pesde 0.7.4; the Wally case is read from Wally's install code.
- **Engine tests:** Lest's studio and cloud backends bundle the specs and the modules they string-require from disk, so an empty test place works. An Instance require reaches the configured place file or published place; a Team Create place is the live session, with the [costs](verification.md#test-runner-facts) that brings. In a test against a synced Team Create place, Lest's Studio didn't run Script Sync (a file added to the synced folder mid-run never arrived) and no prompt blocked the run. A dedicated test place or a place file keeps tests away from synced roots.

## Dev content and publishing

Studio publishes the place as it stands, synced roots included. With no release build to exclude dev content, decide ship or exclude for each kind, as with [Rojo](rojo.md#dev-and-release-builds):

- Content the place doesn't need, such as specs, fixtures and tooling, stays outside synced roots; Lest bundles specs from disk.
- Content that must be in the place ships with it. Code that runs returns early unless `RunService:IsStudio()`. A ModuleScript runs only when required but still ships, and anything in a replicated container reaches every client, so keep dev-only modules out of `ReplicatedStorage` and `ReplicatedFirst` unless the client needs them.
- A guard can fail on dev file patterns inside synced roots. It can't see instances that exist only in Studio, so before publishing, check the place through the Studio MCP (`search_game_tree`).

## Sources

- [Script Sync](https://create.roblox.com/docs/scripting/sync), [script types and locations](https://create.roblox.com/docs/scripting/locations), [`require`](https://create.roblox.com/docs/reference/engine/globals/LuaGlobals#require)
- luau-lsp [README](https://github.com/JohnnyMorganz/luau-lsp#readme) and [changelog](https://github.com/JohnnyMorganz/luau-lsp/blob/main/CHANGELOG.md)
- Lest [backends](https://github.com/lest-luau/lest/blob/main/docs/backends.md) and [Studio backend](https://github.com/lest-luau/lest/blob/main/docs/studio.md)
