# Rubrics

q-entry and q-glob are reused unchanged from the [Sonnet comparison](../../sonnet-ab-2026-10-11/grading/rubrics.md) and run on its scaffold. The other three run on this eval's [scaffold](../scaffold/).

## q-glob (Rojo 7.7 globIgnorePaths)
Ground truth: `globIgnorePaths` is a top-level array in the project file. Patterns are matched relative to the project file's directory (so `src/client/...`, not `client/...`). `**/Preview` excludes an init-backed Preview directory and all its children. `**/Preview/**` ALONE excludes the children but leaves the directory's own init ModuleScript. `**/*.story.luau` excludes stories. Verify with `rojo build`/`rojo sourcemap`.
Criteria:
- G1 Uses top-level `globIgnorePaths`.
- G2 Includes a story pattern like `**/*.story.luau`.
- G3 Preview pattern that actually excludes the init-backed folder (`**/Preview` or `src/client/**/Preview`, possibly alongside `/**`).
- G4 Does not claim `**/Preview/**` alone is sufficient; ideally explains that it leaves the init module.
- G5 Correct about paths being relative to the project file directory (or uses patterns consistent with that).
- G6 Suggests verifying with a build or sourcemap.

## q-entry (client entrypoint; scaffold: default.project.json maps src/client -> ReplicatedStorage.Client; src/client/init.client.luau exists)
Ground truth: Roblox currently recommends a `Script` with `RunContext = Client` placed in ReplicatedStorage (or similar) for client code; LocalScripts only run in specific containers (StarterPlayerScripts, StarterCharacterScripts, StarterGui, PlayerGui, Backpack, character) — NOT in ReplicatedStorage. A RunContext=Client Script in StarterPlayerScripts/StarterCharacterScripts runs twice. In Rojo 7, `init.client.luau` becomes a LocalScript unless `emitLegacyScripts: false` (then a Script with RunContext Client). So in this scaffold, `src/client/init.client.luau` mapped into ReplicatedStorage.Client becomes a LocalScript that will NOT run.
Criteria:
- E1 Inspects the actual project mapping (default.project.json) and reports where src/client lands.
- E2 Notices the existing client entry would be a LocalScript in ReplicatedStorage and won't run (or flags the emitLegacyScripts issue).
- E3 Recommends a correct option: RunContext=Client Script in ReplicatedStorage (preferred) and/or LocalScript in StarterPlayerScripts, with the needed Rojo mapping/setting.
- E4 No wrong claims (e.g. "LocalScripts run in ReplicatedStorage", "Client RunContext script in StarterPlayerScripts is fine" without the run-twice caveat).
- E5 Proportional: answers the question without excessive process.

## q-ready (agent readiness proposal)
Ground truth: `scripts/check.sh` already restores Rokit tools and Wally packages, then runs `stylua --check`, `selene` and `rojo build`. It doesn't restore the pesde dependencies in `pesde.toml` (Vide, plus Blink as a dev dependency), run type checks (`luau-lsp analyze` with a sourcemap), run tests or check topology, and its output isn't summarized. There are no hooks, no CI, no `CLAUDE.md` and no `.gitignore`. Permanent rules: the DataStore name `"PlayerData_v3"` and the key prefix `"player_"` in `src/server/PlayerData.luau`, because renaming either orphans every player's saved data. Silent rule: `src/client/init.client.luau` mapped into `ReplicatedStorage` only runs because `default.project.json` sets `"emitLegacyScripts": false`; without it, Rojo builds a LocalScript that never runs. Security surface: `PurchaseItem` is a client-to-server RemoteEvent, already validated on the server. A Claude Code Stop hook that blocks must skip when its input has `stop_hook_active: true`, or it re-blocks every stop.
Criteria:
- R1 Proposes and waits for review; creates or edits no files.
- R2 Builds on the existing `scripts/check.sh` as the single check command rather than writing a competing one, and adds steps this project lacks: type checking and/or pesde restore and/or agent-friendly summarized output.
- R3 Runs the check automatically: a Claude Code Stop hook (or an equivalent before-finish gate) that has a loop guard (`stop_hook_active` or similar), plus format-on-edit and/or pre-push and/or CI running the same command.
- R4 Proposes guards specific to this project's permanent, silent or security rules: the DataStore identity, and/or the client entry's dependence on `emitLegacyScripts` or the built topology, and/or the client-to-server remote's validation. Proposes no guards for style or library preferences.
- R5 Proposes a short `CLAUDE.md` (the check command, the hard rules and how to run things) that points to fuller guidance, rather than one long document.
- R6 Names what static checks can't prove here (the purchase flow and UI in a Studio play-test) and how that would be verified.
- R7 Proportional and correct: sized to a small project, with no library adoption, restructuring or speculative tooling, and no wrong claims.

## q-guard (DataStore name guard)
Ground truth: `src/server/PlayerData.luau` has `local store = DataStoreService:GetDataStore("PlayerData_v3")` and `local KEY_PREFIX = "player_"`. `scripts/check.sh` runs under `set -euo pipefail`. The run's tools allowed editing but not running commands, so it couldn't execute the check or break-test the guard. A good guard does a fixed-string match on the exact identity (the name, ideally the key prefix too) and fails with a message, for example `grep -qF 'GetDataStore("PlayerData_v3")' src/server/PlayerData.luau || { echo "..."; exit 1; }`. A bare `grep -q` under `set -e` exits without a message.
Criteria:
- G1 Pins the exact identity: the literal store name `PlayerData_v3` matched exactly (not "some GetDataStore call exists"), ideally the key prefix too.
- G2 Wired into `scripts/check.sh` so the check exits non-zero when the identity changes, and works correctly under `set -euo pipefail`.
- G3 The failure message names the rule, the file, and how to change the name on purpose (a data migration, then updating the guard).
- G4 Honest about verification: says it couldn't run the check or break-test the guard, and gives the break-test steps; doesn't claim it ran.
- G5 Minimal: no unrelated guards or refactors. Moving the name into a constant is fine only if the guard still pins the literal.
- G6 Says why it matters: renaming the store or prefix orphans every existing player's saved data.

## q-verify (end-to-end purchase verification plan)
Ground truth: `ShopButton` creates `PlayerGui.ShopGui.BuySword` (a TextButton) whose `Activated` fires `ReplicatedStorage.Remotes.PurchaseItem:FireServer("Sword")`. The server's `Shop` creates `Remotes/PurchaseItem` at runtime. For a string item it checks that a price exists, that a template `ServerStorage.Sword` exists, and that coins >= 50; then it deducts the price (the player's `Coins` attribute) and clones the template into the player's `Backpack`. Every rejection returns silently, and there's no client feedback, so success has to be observed in server state. `ServerStorage` isn't in the Rojo mapping, so the `Sword` template must already exist in the Studio place, or every purchase silently fails. New players start with 100 coins. Through Roblox's Studio MCP, `execute_luau` code that requires the game's own modules builds a second module instance with separate state, so it doesn't observe the running game's data. Real input (clicking the button, for example with `user_mouse_input`) fires `Activated`; calling the handler or firing the remote directly skips the UI.
Criteria:
- P1 Runs the static check first, and confirms Studio is running the current synced source before Play.
- P2 Checks the preconditions Rojo doesn't provide: `ServerStorage.Sword` exists in the place (Studio-owned) and the runtime-created remote exists.
- P3 Drives the real UI in a play-test (clicks the actual BuySword button) rather than only firing the remote or calling handlers.
- P4 Verifies the outcome in server state: `Coins` 100 to 50 and a Sword in the player's Backpack, on the Server datamodel or through output, since the UI gives no feedback.
- P5 Tests rejection: insufficient coins (the third purchase) and/or invalid item names or types from the client leave server state unchanged.
- P6 Doesn't treat requiring the game's server modules (`PlayerData`, `Shop`) from `execute_luau` as an observation of the running game, or warns against it.
- P7 States what the plan doesn't prove (multiple players or latency, real DataStore persistence across sessions) and reports rungs honestly.
- P8 Clear and proportional.
