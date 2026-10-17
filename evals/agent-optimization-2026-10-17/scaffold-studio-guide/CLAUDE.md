# sword-arena

Roblox sword game. Its code lives only in Studio: there is no Script Sync, Rojo project or source folder. Work on it through Roblox's Studio MCP server.

- Place: Sword Arena, place ID 1234567890. Two Studio windows can share a name, so call `list_roblox_studios` first and pass the `studio_id` it reports for place 1234567890 on every call.
- Team Create, with two other people editing. Drafts mode is off, so each script edit reaches their sessions at once.

## Working rules

- **Checkpoints:** before moving, deleting or adding scripts, ask the user to save with notes (**File** > **Save to Roblox with Notes**) and wait. An edit inside existing scripts, such as a rename, can go ahead, and the report says how to undo it. **View Script History** on a script lists its saved versions; scripts save every 5 minutes or on **Ctrl+S**, so the history can miss the last few minutes before an edit.
- **Edits:** `multi_edit` creates a script when the path doesn't exist, so check each path first. Edit in Edit mode, since changes made during a play-test are discarded when it stops.
- **Play-tests:** confirm the edited `Source` in Edit mode before Play. `start_stop_play` starts and stops a play-test; read `get_console_output`. Don't `require` the game's own modules from `execute_luau` during a play-test: it builds a second copy with its own state. Stop only play sessions you started.
- **Reports:** name each check you ran and the ones you couldn't. The static checks (format, lint, type check) need files, so they can't run here; report them as not run.
