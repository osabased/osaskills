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

- **Guide:** keep `CLAUDE.md` and the [project guide](project-guide.md) in a local folder the agent starts in, with the place's name and ID. Two Studio windows can share a name; pass the `studio_id` that `list_roblox_studios` reports for that place ID.
- **Checkpoints:** before an edit that spans several scripts, ask the user to save with notes (**File** > **Save to Roblox with Notes**) so there is a version to return to. Restoring a version creates a new one and doesn't publish it. In Team Create, **View Script History** on a script lists and opens its earlier versions.
- **Drafts mode:** edits stay local until committed. Roblox doesn't document how MCP edits interact with drafts, so ask the user before relying on one.
- **Edits:** `multi_edit` creates a script when the path doesn't exist, so a wrong path adds a stray script; check the path first. Edit in Edit mode, since changes made during a play-test are discarded when it stops.
- **Tests:** Lest's studio backend can run specs kept in the local folder against the place as stored on Roblox, never the session open in Studio; an Instance require in a spec reaches the place's own module. Roblox's command-line docs don't say whether that is the latest save or the latest publish, so ask the user to save first and confirm a run sees the current edit, for example with a spec that reads the edited module's `Source`.
- **Play-tests:** as in [verification](verification.md#play-tests-with-studio-mcp).
- **Report** the static rung as not run, and why.

## Sources

- [Studio MCP server](https://create.roblox.com/docs/studio/mcp), [Script Sync](https://create.roblox.com/docs/scripting/sync)
- [Version History](https://create.roblox.com/docs/projects/version-history), [collaboration](https://create.roblox.com/docs/projects/collaboration), [Studio command line](https://create.roblox.com/docs/studio/command-line-interface)
- Lest [Studio backend](https://github.com/lest-luau/lest/blob/main/docs/studio.md)
