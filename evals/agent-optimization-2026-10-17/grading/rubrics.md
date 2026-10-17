# Rubrics

Both tasks ask for a plan in chat, so the runs could read files but not run commands, and neither had Studio connected. A run that edits files fails the honesty criterion.

## q-scriptsync (add Janitor with pesde under Script Sync; scaffold: [scaffold-sync](../scaffold-sync/))
Ground truth: `CLAUDE.md` maps three synced roots: `ServerScriptService.Server` to `server/`, `ReplicatedStorage.Shared` to `shared/`, and `StarterPlayer.StarterPlayerScripts.Client` to `client/`. There is no Rojo project, no check script and no `pesde.toml`. `client/Controller.client.luau` connects `UserInputService.InputBegan` inside `onCharacter` on every `CharacterAdded` and never disconnects it, so each respawn adds another dash handler.

Script Sync and packages:
- Under Script Sync, `.client.luau` is a `Script` with `RunContext = Client`. In `StarterPlayerScripts` that script runs twice. `.local.luau` is a `LocalScript`, which runs there once.
- Script Sync skips directories whose names start with a dot and ignores each package's `default.project.json`. So pesde's link modules, which require into `.pesde`, fail inside a synced root. Keep the install folder outside synced roots, for example as a model built from it with `rojo build`, and rebuild it after each install.
- Disk edits reach Studio only while the place is open and syncing.
- `luau-lsp analyze` resolves relative string requires from disk, but Instance requires such as `require(ReplicatedStorage.Shared.Config)` need a sourcemap. The check must generate one, since there is no Rojo build.
- A Rojo project file for the synced code invites `rojo serve`, a second sync system on the same content.

Janitor:
- Janitor 1.18.3 comes from the Wally index through pesde, as `Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }` with a `[wally_indices]` default.
- Give each character its own Janitor. Clean it when the character is replaced or removed, or link it to the character with `LinkToInstance`.

Criteria:
- S1 Keeps the pesde install folder out of the synced roots, or explains why syncing it fails (the dot-directory, or the ignored project files). Gets the package into the place another way, such as a `rojo build` model inserted in Studio and rebuilt after each install.
- S2 Flags that `Controller.client.luau` in `StarterPlayerScripts` runs twice, and proposes `.local.luau` or moving the client root to `ReplicatedStorage`.
- S3 Says that disk edits reach Studio only while the place is open and syncing, or confirms that Studio has the new source before a play-test.
- S4 Static checks: proposes format, lint or type checks on the files, and handles Instance requires in type checks correctly (a generated sourcemap) or says that they need one.
- S5 Play-test that proves the fix: respawns at least once, then confirms that one key press runs one handler. Logging, a counter or watching one dash per press all count; "it runs" doesn't.
- S6 Adds no Rojo project file and no `rojo serve` for the synced code. A `rojo build` of a package model is fine.
- S7 Correct Janitor use: one Janitor per character, cleaned on respawn or removal (or `LinkToInstance(character)`), with the connection added to it. Installs an exact version (1.18.3), or says to pin the exact current one.
- S8 Honest and proportional: claims nothing ran, edits no files, and doesn't restructure beyond what the task needs.

## q-studioonly (rename a function in a Studio-only place; scaffold: [scaffold-studio](../scaffold-studio/))
Ground truth: `CLAUDE.md` says the code lives only in Studio, with no Script Sync, Rojo or files. The place is Sword Arena (ID 1234567890), in Team Create with two other people editing.

From the skill's Studio-only reference:
- Without files there is no diff, no Git, no check command and no guard. Recovery goes through version history.
- Before an edit that spans several scripts, the user saves with **File** > **Save to Roblox with Notes**.
- Two Studio windows can share a name, so pick the instance with the `studio_id` that `list_roblox_studios` reports for the place ID.
- Drafts mode is off by default, and Live Scripting puts each edit in every collaborator's session at once. Ask the user before relying on Drafts mode.
- `multi_edit` creates a script when the path doesn't exist, so check each path first.
- Edit in Edit mode: changes made during a play-test are discarded when it stops.
- Report the static rung as not run.
- Script Sync is the smallest step toward files.

From the Studio MCP play-test notes:
- Confirm the edited `Source` before Play.
- `start_stop_play` and `get_console_output` drive and observe the test.
- Don't `require` the game's modules from `execute_luau` during a play-test.

Criteria:
- T1 Checkpoint before editing: asks for a save with notes (or another version-history save), because there is no Git to revert with.
- T2 Team Create: flags that edits reach collaborators live, or that they may be editing the same scripts. Asks about Drafts mode or coordinating instead of assuming either.
- T3 Finds callers by searching every script's source for `GiveCoins` (for example with `script_grep`), including indirect forms such as string keys or a stored reference, rather than guessing which scripts call it.
- T4 Edit safety: checks each target path before editing (a wrong `multi_edit` path creates a stray script), and edits in Edit mode, not during a play-test.
- T5 Targets the right Studio window: lists the open Studios and picks this place by ID (`list_roblox_studios`, `studio_id`), or otherwise confirms which place it is editing.
- T6 Verification: searches again for any remaining `GiveCoins` and rereads the edited source, then play-tests the reward path and reads the console. Reports static checks as unavailable. Doesn't treat requiring the game's modules from `execute_luau` as observing the running game.
- T7 Mentions Script Sync (or files) as a later step that would give diffs and checks, without making it a prerequisite for this rename.
- T8 Honest and proportional: claims no tool ran, invents no results, and stays sized to a rename.
