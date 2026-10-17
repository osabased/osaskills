# Studio-only places

Use when a project's code lives only in Studio, with no Script Sync or Rojo, and an agent works on it through the Studio MCP.

## What an agent can't do

The agent reads and edits the open place through Studio MCP tools such as `script_read`, `script_grep`, `search_game_tree`, `inspect_instance`, `multi_edit` and `execute_luau`, so everything it knows comes from live reads of a place that can change under it. Roblox warns that MCP clients can read and modify content in your open places. Without files there is:

- no diff to review and no Git to revert with; recovery goes through Studio's version history;
- no check command, formatter, linter, CLI type check or CI, since they all read files, and the documented MCP tools don't expose Studio's Script Analysis window;
- no guard to fail an edit before it lands.

## Smallest step: Script Sync

Recommend Script Sync first. Roblox describes it as an extra feature for existing places rather than a change in how the project is managed, and the agent-ready pieces then apply to the synced code ([Script Sync](script-sync.md)). The user sets it up in Studio: check scripts for attributes and tags first ([before changing a boundary](script-sync.md#before-changing-a-boundary)), sync the code folders to new, empty directories inside one Git repository, and commit. Moving to Rojo is a larger [migration](migration.md).

## Working without files

When the user keeps the place Studio-only:

- **Guide:** keep `CLAUDE.md` and the [project guide](project-guide.md) in a local folder the agent starts in. A session that doesn't load this skill still reads `CLAUDE.md`, so write the rules it needs there:
  - the place's name and ID, and that every call passes the `studio_id` that `list_roblox_studios` reports for that ID, since two Studio windows can share a name;
  - whether the place is in Team Create and whether Drafts mode is on, as the user confirms them;
  - the checkpoint, edit and play-test rules below;
  - that the static checks can't run, so a report names them as not run.
- **Checkpoints:** before a structural change, such as moving, deleting or adding scripts, ask the user to save with notes (**File** > **Save to Roblox with Notes**) and wait, so there is a version to return to. Restoring a version creates a new one and doesn't publish it. An edit inside existing scripts, such as a rename, can go ahead, and the report says how to undo it. In Team Create, **View Script History** on a script lists its saved versions. With Drafts mode off, a script is saved every 5 minutes or on **Ctrl+S**, so the history can miss the last few minutes before an edit.
- **Drafts mode:** off by default, and Live Scripting puts each edit in every collaborator's session at once; in a test, an MCP `multi_edit` reached another session of the place within seconds. In Drafts mode edits stay local until committed. The MCP can't read the Drafts state (`DraftsService` needs a capability MCP code lacks), and how MCP edits interact with drafts is undocumented and untested, so ask the user before relying on one.
- **Edits:** `multi_edit` creates a script when the path doesn't exist, so a wrong path adds a stray script; check the path first. Edit in Edit mode, since changes made during a play-test are discarded when it stops.
- **Tests:** Lest's studio backend can run specs kept in the local folder against the published place; an Instance require in a spec reaches the place's own module. In Team Create that is the live session, with the [costs](verification.md#test-runner-facts) that brings. Otherwise Roblox's command-line docs don't say whether a run sees the latest save or the latest publish, so ask the user to save first and confirm a run sees the current edit, for example with a spec that reads the edited module's `Source`.
- **Play-tests:** with no static checks, a play-test is the lowest rung that can observe an edit. After an edit, play-test the paths it changed and read the console, unless the user has said not to, then stop the play-test. Run it as in [verification](verification.md#play-tests-with-studio-mcp).
- **Report** the static rung as not run, and why, and name the changed paths the play-test didn't reach.

## Sources

- [Studio MCP server](https://create.roblox.com/docs/studio/mcp), [Script Sync](https://create.roblox.com/docs/scripting/sync)
- [Version History](https://create.roblox.com/docs/projects/version-history), [collaboration](https://create.roblox.com/docs/projects/collaboration), [Studio command line](https://create.roblox.com/docs/studio/command-line-interface)
- Lest [Studio backend](https://github.com/lest-luau/lest/blob/main/docs/studio.md)
