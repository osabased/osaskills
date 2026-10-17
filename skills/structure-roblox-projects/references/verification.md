# Verification ladder

Use when choosing how to verify a change, setting up tests, or running a Studio play-test. Each rung proves what the ones below it can't. Run the lowest rung that can observe the change, report each rung you ran, and name the ones you couldn't. A build or a loader's "loaded" flag proves nothing about runtime behavior.

| Rung | Proves | How | In CI |
| --- | --- | --- | --- |
| Static | Syntax, types, lint, format, mapping topology | The [check command](checks.md#one-check-command) | Yes |
| Native tests | Pure logic | Lest native backend | Yes |
| Lune tests | Modules that need `task`, file or place processing | Lest Lune backend | Yes |
| Studio engine tests | Instances, services, UI libraries | Lest Studio backend against a place file or published place | No, it launches Studio. Lest's cloud backend can run the same suites on a game server through Open Cloud |
| Play-test | Startup, replication, rendering, input | Studio Play with the current code in the place (the Rojo dev build served, Script Sync running, or edited in Studio), by hand or through Studio MCP | No |
| Multiplayer | Several clients, ordering, latency, Server Authority rollback | Studio's multi-client test with network simulation | No |

Design for the low rungs: split pure logic out of modules that touch Roblox APIs and keep the Roblox-facing shell thin, so most behavior is covered offline and in CI.

## Test runner facts

- **Lest exit codes:** 0 pass, 1 test failure, 2 tool error. Use JSON or JUnit output for machine-readable results.
- **Native backend:** no `game`, `script` or Roblox types, so the module under test can't touch them.
- **Lune backend:** `task` exists only as a library (`require("@lune/task")`), so a module the spec loads doesn't see it unless passed in. An error inside a `task.spawn` thread exits Lune and fails the whole run.
- **Studio backend:** runs in edit mode. Place scripts don't run, physics doesn't step, and `RunService:IsClient()` and `IsServer()` are both true. Startup, interaction and multiplayer still need a play-test.
- **Studio backend on a Team Create place:** Lest's Studio joins the live session under the user's account, so it sees edits made seconds earlier, before any save. Joining disconnects the user's own Studio from that place ("you have joined a game from another device"), and anything a spec creates or changes stays in the shared place. Warn the user before a run, and run specs that change the place against a place file. Observed with Lest 0.6.1 and Studio 0.743 in October 2026.

## Play-tests with Studio MCP

Observed with Roblox's Studio MCP server in October 2026. Tool names and behavior change, so list the server's tools first and recheck anything that doesn't match.

- **Confirm Studio runs your bytes** before Play: in Edit mode, read a changed module's `Source` with `execute_luau` (or `script_read`). A commit hash doesn't identify uncommitted edits.
- `start_stop_play` starts and stops a play-test. Changes made during one are discarded when it stops.
- `search_game_tree`, `inspect_instance` and `get_console_output` work on the Client and Server datamodels.
- **Real input:** `user_mouse_input` with an `instance_path` such as `LocalPlayer.PlayerGui.<Gui>.<Button>` and a click fires the button's `Activated`. Calling the handler directly proves only the handler.
- **Timing:** the first `execute_luau` after Play returns 7 to 15 s in, and each call takes seconds, so short-lived UI is gone before you look. Record instead: a dev-only module, or one `execute_luau` that connects the signals (connections outlive the call), appends timestamped lines to a `StringValue` under `LocalPlayer`; read it afterward.
- `screen_capture` works in edit mode only.
- **Don't `require` the game's own modules from `execute_luau` during a play-test.** It builds a second copy with its own state, such as a second data-library instance or duplicate network setup, and its errors look like game bugs. Observe through the UI, the console and the Instance tree.
- Expect some console noise in Studio (mocked DataStores, unavailable APIs); the project guide should list what is expected.
- Stop only play sessions you started.

## Previews

To prove rendered UI or real input, run it through the normal client startup path; a dev-only module is fine when it can't ship or run in live servers ([Rojo](rojo.md#dev-and-release-builds), [Script Sync](script-sync.md#dev-content-and-publishing)). Don't widen Script Capabilities, inject code through a privileged tool, or replace startup to make a preview run. UI Labs stories complement this for isolated states and variants.

## Sources

- [Lest](https://github.com/lest-luau/lest), [Lune](https://github.com/lune-org/lune)
- [Studio testing modes](https://create.roblox.com/docs/studio/testing-modes)
