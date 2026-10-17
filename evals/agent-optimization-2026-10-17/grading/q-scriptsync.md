===== R1 =====
**What I think you want:** add Janitor through pesde, then change `client/Controller.client.luau` so the `InputBegan` dash connection is disconnected when the character respawns. Right now each `CharacterAdded` adds another connection, and the old ones keep firing against stale humanoids. Correct me if that's wrong.

**What I found**
- `rokit.toml` pins only stylua and selene. There is no pesde, no `pesde.toml` and no lockfile.
- There is no Rojo project, and Script Sync only carries `server/`, `shared/` and `client/` into Studio. A package installed to a default `luau_packages/` folder would never reach Studio.
- pesde's Roblox target normally generates its requires from a Rojo sourcemap. I haven't verified how it behaves without a Rojo project, so that is the main risk.

**Install**
1. Add `pesde` to `rokit.toml` and run `rokit install`. I'd look up the current pesde release then, not guess the version.
2. Run `pesde init` with the roblox target. Add `Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }` and `[wally_indices] default = "https://github.com/UpliftGames/wally-index"`, as in the skill's setup notes.
3. Point the packages directory at a synced folder, such as `shared/Packages`. Then it reaches Studio as `ReplicatedStorage.Shared.Packages`, and the client can require it.
4. Run `pesde install`. Check that `pesde.lock` resolves `wally#howmanysmall/janitor@1.18.3`, with typed-promise 4.0.6 and evaera/promise 4.0.0.
5. If pesde insists on a sourcemap, the fallback is a minimal `default.project.json` used only to generate it. It would not be used for syncing. This needs your approval because it adds Rojo to a project that deliberately has none.

**Wire in** (`client/Controller.client.luau`)
- Require Janitor from `ReplicatedStorage.Shared.Packages`. Check the generated wrapper path before writing it, because the package's own project name is lowercase `janitor`.
- Create one `Janitor.new()` at the top of the file.
- At the start of `onCharacter`, call `janitor:Cleanup()` so the previous character's connection is gone. Then `janitor:Add(UserInputService.InputBegan:Connect(...))`. A connection defaults to `"Disconnect"`, so no method argument is needed.
- Alternatively, use a fixed index: `janitor:Add(conn, "Disconnect", "Dash")`. Re-adding under the same index cleans up the old one, so no explicit `Cleanup` is needed. I prefer this because it is a single line, but it ties cleanup to the next spawn, not the death.
- Optionally add `janitor:Add(humanoid.Died:Once(...))` or `LinkToInstance(character)`. Cleanup would then happen when the character is destroyed, not only at the next spawn. `LinkToInstance` fires on `Destroying`, which is what `LoadCharacter` does to the old character.

**Check it works**
- Static: `stylua --check` and `selene` on the changed file. There's no check script yet, and selene may need a Roblox standard-library config. I'd flag that if it complains.
- Install: confirm the lock versions above, and that the package files appear under `shared/Packages` and show up in Studio's Explorer after a sync.
- Runtime in Studio Play:
  1. Press the dash key and confirm one dash per press.
  2. Reset the character several times.
  3. Press the dash key again. Without the fix, each respawn adds another handler. With it, the dash behaves the same after any number of respawns.
  4. For a hard check, temporarily add `print` calls and confirm exactly one handler fires. Remove them afterwards.
- I can't run Studio from here, so the runtime check is yours unless a Studio tool is connected. Static checks and lock inspection I can do.

**Questions, recommended answer first**
1. Package location: `shared/Packages`? (Recommended. The alternative is `client/Packages`, which keeps it client-only.)
2. If pesde needs a sourcemap, may I add a minimal `default.project.json` for that purpose only? (Recommended: yes, kept out of syncing.)
3. Cleanup trigger: indexed `Add` plus `LinkToInstance(character)`, or just the next-spawn cleanup?
4. Should I commit `pesde.lock` and the package folder, or gitignore the packages? There's no git repo here yet, so this only matters if you plan to add one.

===== R2 =====
I haven't edited anything. Here's the plan.

**What I think you want:** add Janitor as a pinned pesde dependency, then use it in `client/Controller.client.luau` so the dash `InputBegan` connection is disconnected when the character respawns.

**What I found**

- The project has no `pesde.toml` or `pesde.lock`. `rokit.toml` pins only StyLua and Selene.
- The current code adds a new `InputBegan` connection on every `CharacterAdded` and never disconnects the old ones. Connections fire in the order they were made, so the oldest one runs first. It captures the old `humanoid`, sets `lastDash`, and calls `Move` on a destroyed humanoid. The newer connections then hit the cooldown and return. If `Config.DASH_COOLDOWN` is above 0 (I haven't checked `shared/Config.luau`), dash may do nothing after the first respawn. The Janitor change should fix that, so I'll confirm it in testing.

**1. Install**

- Run `pesde init`, then add `Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }` with the Wally index in `[wally_indices]`. Run `pesde install`, then commit `pesde.lock`.
- Confirm the lock resolves `wally#howmanysmall/janitor@1.18.3`. It should also pull in `typed-promise` 4.0.6 and `evaera/promise` 4.0.0.
- Add pesde to `rokit.toml` so everyone uses the same version. That's a `rokit add` with the pesde release I pick, which I'll confirm before running it.
- Open question: pesde writes packages to disk, but Script Sync only maps the three roots in CLAUDE.md. Before I choose a require path, I need to know how `Janitor` gets under `ReplicatedStorage` in Studio. Either a synced root covers the package output, or it gets placed by hand. I'll check the structure skill's guidance for this before writing the require.

**2. Wire it in**

Use one Janitor for the character and clean it on each respawn. This is the change I'd make:

```luau
local Janitor = require(<path to package>)

local characterJanitor = Janitor.new()

local function onCharacter(character: Model)
	characterJanitor:Cleanup()
	local humanoid = character:WaitForChild("Humanoid") :: Humanoid
	characterJanitor:Add(UserInputService.InputBegan:Connect(function(input, processed)
		-- same body as now
	end))
end
```

- `Add` defaults to `"Disconnect"` for an `RBXScriptConnection`, so the method argument can be omitted.
- Alternative: `characterJanitor:LinkToInstance(character)` cleans up on `Destroying` instead of on `CharacterAdded`. I prefer the explicit `Cleanup()`. It ties cleanup to the respawn event you named, and it doesn't rely on `Destroying` firing.
- `lastDash` and the dash logic stay the same.

**3. Verify**

- Static: run `stylua --check client shared server` and `selene client shared server`. There's no check script yet, so these run by hand.
- Studio play test: dash once and confirm the character moves. Reset the character a few times, dash again, and confirm the new character moves. Before the change, I expect the dash to fail after the first reset. Use a temporary print or a Studio command-bar check, then remove it.
- Janitor check: after several resets, the Janitor should hold one connection. If `Janitor` isn't exposed, I'll count with a temporary print.
- Confirm `pesde.lock` shows 1.18.3 and that `pesde install --locked` restores it on a clean checkout.

**Behavior change:** this is a bug fix. Dash after a respawn should work where it currently may not. It doesn't change the dash look, the copy, or the cooldown, so I didn't need to ask about it.

**Needs your call**

1. Janitor placement: should I wire it so pesde output lands under `ReplicatedStorage` (requires a Script Sync mapping change), or place it by hand in Studio?
2. Cleanup style: explicit `Cleanup()` on `CharacterAdded` (my recommendation) or `LinkToInstance(character)`?

===== R3 =====
**What I understand you want:** add Janitor (pinned 1.18.3) through pesde, and use it in `client/Controller.client.luau` so each character's `InputBegan` dash connection is disconnected when the player respawns. At the moment every respawn adds another connection, and each one keeps its own dead `humanoid` alive. This is a plan only, and I haven't edited any files.

## What I found

- The project has no `pesde.toml`, no lockfile and no `Packages` folder. `rokit.toml` pins only StyLua and selene, so pesde isn't pinned either.
- Script Sync can't sync pesde's install folder. It skips dot-directories, which is where `.pesde` lives, and pesde's link modules require into `.pesde`. So the packages can't go under `shared/` or `client/`.
- The install folder has to stay outside the synced roots and reach Studio as a built model. That needs `rojo build`, and Rojo isn't pinned either. It would be used only to build the model, not as a second sync system.

## Decisions I need from you

1. **Tooling pins (recommended: add them).** Add `pesde` and `rojo` to `rokit.toml`, pinned to versions I'll look up. The skill reviewed pesde 0.7.4.
2. **How the packages reach Studio (recommended: a built model).** Run `rojo build` on the install folder to produce `Packages.rbxm`, which you insert once into `ReplicatedStorage.Packages` in Studio. You'd rebuild and re-insert it after each install. The alternative is to copy the Janitor module into Studio by hand, which is worse. This choice affects how the place is set up, so it's yours to make.
3. **Where to keep the package files.** I'd put `pesde.toml`, `pesde.lock` and `Packages/` at the repo root, outside the synced directories. I'd also keep `Packages.rbxm` outside them, since it is inserted into Studio by hand.

## Install

1. Pin the tools in `rokit.toml`, then run `rokit install`.
2. Run `pesde init` for a Roblox target, then add Janitor:
   ```toml
   [dependencies]
   Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }

   [wally_indices]
   default = "https://github.com/UpliftGames/wally-index"
   ```
3. Run `pesde install`, which writes `pesde.lock`. Later restores use `pesde install --locked`.
4. Check that the lock resolves `howmanysmall/janitor@1.18.3`, `howmanysmall/typed-promise` 4.0.6 and `evaera/promise` 4.0.0.
5. Build `Packages.rbxm` from the install folder with `rojo build`. Insert it into `ReplicatedStorage` in Studio, and confirm the Janitor module and its Promise companions are present. The package's own Rojo project is named `janitor` in lowercase, so I'd check the built tree before writing the require path.

## Wire-in

The change in `Controller.client.luau` is small:

- Add `local Janitor = require(ReplicatedStorage.Packages.Janitor)`, using the path the built model actually has.
- Create one `Janitor.new()` at the top of the script.
- In `onCharacter`, add the `InputBegan` connection with `janitor:Add(connection, "Disconnect", "Dash")`. Reusing the index `"Dash"` cleans up the previous character's connection right before the new one is stored. That means no explicit `Cleanup` call is needed. I'd also consider `janitor:LinkToInstance(character)`, so the connection goes as soon as the character is destroyed.
- Leave `lastDash` and the dash logic as they are. The cooldown stays shared across respawns, as it is today.

For a single connection, a plain `local dashConnection` that you disconnect before reconnecting would work. I'll use Janitor as you asked.

## Checks

There is no check script yet, so I'd run the tools directly:

1. `stylua --check` and `selene` on `client/`. `rokit.toml` pins both.
2. A play-test in Studio. The shared cooldown hides duplicate connections, because extra handlers return early. So you can't see the leak by pressing dash. Instead, I'd add a temporary `print` at the top of the `InputBegan` handler, before the cooldown check. Respawn three times and press dash once. It should print one line, where the unfixed code prints four. Then remove the print.
3. Confirm the dash still works after a respawn, and that there are no "doesn't have method" warnings or errors from Janitor or Promise in the output.
4. Confirm Studio runs the bytes on disk: Studio must be open with sync running when the file changes.

## Risks

- This is a `.client.luau` under `StarterPlayerScripts`, so it's a `Script` with `RunContext = Client`. Per the skill, such scripts run twice there, once as the original and once as a clone. If that happens here, the current code already double-connects, and the print test would show two lines even after the fix. I'd check this during the play-test and raise it with you rather than guess.
- The built model is a manual step. If it's missing in Studio, the require fails at startup, so the guide should record it.

Which options do you want for 1–3? Once you answer, I'll start with the install.

===== R4 =====
**What I understand you want:** add Janitor 1.18.3 as a pesde dependency. In `client/Controller.client.luau`, the `InputBegan` connection made for each character should be disconnected when that character goes away. Nothing gets edited until you answer the questions below.

## What's there now

- The repo has no `pesde.toml`, no lock and no package folder. `rokit.toml` pins only StyLua and Selene, so pesde isn't installed either. There's also no `selene.toml` or `stylua.toml`.
- `onCharacter` (`client/Controller.client.luau:11`) connects `UserInputService.InputBegan` on every spawn and never disconnects it. After N respawns there are N live handlers, each holding an old `humanoid`.
- You can't see this in play. All the handlers share `lastDash` and the cooldown, so only the first one to run moves the character. Verification has to count handlers, not watch dashing (see Check below).

## The packaging problem

Script Sync can't sync pesde's install folder. It skips dot-folders, so `.pesde` is skipped, and it ignores each package's `default.project.json`, so the link modules fail. Janitor therefore can't live under `client/`, `shared/` or `server/`. The workaround from the Script Sync reference is:

1. Run `pesde install` in a directory outside the three synced roots.
2. Build the installed packages into a model with `rojo build`.
3. Insert the model into Studio by hand as `ReplicatedStorage.Packages`, so it isn't under a synced root. Rebuild and reinsert it after each install.

The code would then do `require(ReplicatedStorage.Packages.Janitor)`. The skill says to check the sourcemap for the real path, because the package's own Rojo project is named lowercase `janitor`. The generated wrapper handles that, but I'd confirm the path in the built model.

## Install steps

1. Add `pesde` and `rojo` to `rokit.toml`, pinned. I'd look up the current releases when installing. The Janitor skill was reviewed against pesde 0.7.4.
2. Create `pesde.toml` with a roblox target and this dependency, plus the Wally index the skill documents:
   ```toml
   [dependencies]
   Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }

   [wally_indices]
   default = "https://github.com/UpliftGames/wally-index"
   ```
3. Run `pesde install`, which writes `pesde.lock`. Janitor pulls in `howmanysmall/typed-promise` 4.0.6 and `evaera/promise` 4.0.0, and the lock should show both.
4. Build the model and insert it into `ReplicatedStorage.Packages`.

## Wiring in `Controller.client.luau`

- Keep one top-level `Janitor` for the script.
- On each `CharacterAdded`, create a per-character Janitor and store it with `janitor:Add(Janitor.new(), "Destroy", "Character")`. Passing an index makes Janitor clean up the previous character's Janitor immediately, so respawns can't stack handlers even if `CharacterRemoving` is late or missing.
- Add the `InputBegan` connection to that per-character Janitor. `RBXScriptConnection` defaults to `"Disconnect"`, so no method name is needed.
- Call `characterJanitor:LinkToInstance(character)` so the connection also drops when the character is destroyed.
- The initial `if player.Character` call and the `CharacterAdded` connection go through the same function, so no other paths change.

Janitor's cleanup stops at the first callback that throws, and a failed cleanup leaves it unusable. That doesn't matter here because the only entry is a plain disconnect.

## Check

There's no check script, so this is the sequence I'd run and what each step can show:

1. **Restore.** `pesde install --locked`, then confirm `pesde.lock` resolves Janitor to 1.18.3 and the two Promise packages to the versions above. This reads the manifest only and proves nothing at runtime.
2. **Format and lint.** `stylua --check client` and `selene client`. Selene has no config here, so it may need one for Roblox globals. I'd tell you rather than add it silently.
3. **Types.** `luau-lsp analyze` can't resolve an instance require to a Studio-only package, and the file is `--!strict`. I'd report that as a named gap rather than call it passed. The fix would be a generated sourcemap in CI, which is more than this task needs.
4. **Studio play-test.** This is the only step that observes the change. First confirm Studio is running the on-disk bytes. Then:
   - Add a temporary `print` at the top of the `InputBegan` handler, before the cooldown check, and remove it afterward.
   - Reset the character 3 times and press the dash key once. Before the change you'd expect 4 prints. After it you'd expect 1 per press.
   - A temporary `janitor:Add(function() print("character cleaned") end)` on the per-character Janitor should print once per respawn.

One thing to watch in that test: with Script Sync, a `.client.luau` file under `StarterPlayerScripts` runs twice (original and clone). If you see 2 prints per press after the fix, that's a separate double-run bug that Janitor won't fix. I haven't confirmed it happens here.

## Questions

Answer these and I'll go ahead:

1. **Where should the built Janitor model come from?**
   - (a) Recommended: a small package directory outside the synced roots (e.g. `packages/`), built with `rojo build` and inserted by hand.
   - (b) Skip Rojo and vendor Janitor straight into Studio.
2. **Should I add a check script** that runs steps 1–3 as one command? I'd recommend it, but it's more than you asked for.
3. **Should the temporary print test be part of your sign-off?** It's the only way to see the leak, but it needs a Studio session with the MCP connected.

===== R5 =====
**What I think you want:** Add Janitor as a pesde-managed dependency, then use it in `client/Controller.client.luau` so each character's dash `InputBegan` connection is cleaned up when that character is removed. I'm reading "pesde" as the package manager that installs Janitor from the Wally index. I'm not planning any change to dash behavior beyond the cleanup.

## What I found

- The repo has no `pesde.toml`, `pesde.lock`, `wally.toml`, or `*.project.json`. `rokit.toml` pins only `stylua` 2.3.1 and `selene` 0.29.0.
- `onCharacter` connects `UserInputService.InputBegan` and never disconnects it. Every respawn adds another live handler that still points at the old humanoid.
- Bash is disabled in this session, so I couldn't check whether pesde or rokit are installed, and I couldn't run anything. I relied on the Janitor skill (pinned 1.18.3) and didn't read Janitor's source.
- The leak may be worse than wasted work. Handlers run in connection order, so the oldest handler runs first on each press. It sets the shared `lastDash` cooldown and calls `Move` on the dead humanoid, which blocks the live character's dash. This is my reading, not a tested result. The verification below checks it.

## Install

1. Add a `pesde.toml` at the repo root. It needs the package name, version, and a Roblox target, plus:
   - `[dependencies]`: `Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }`
   - `[wally_indices]`: `default = "https://github.com/UpliftGames/wally-index"`
2. Run `pesde install` and commit `pesde.lock`. Check that the lock resolves Janitor 1.18.3, `howmanysmall/typed-promise` 4.0.6, and `evaera/promise` 4.0.0. Those are the versions the skill recorded.
3. Pin pesde itself in `rokit.toml` next to stylua and selene, if you want it managed the same way. I need the pesde version you use.
4. **Blocker:** pesde writes packages to a folder that Script Sync doesn't sync. CLAUDE.md maps only `server/`, `shared/`, and `client/`. See question 1.

## Wire-in

Use one Janitor per character and link it to the character's destruction:

```luau
local Janitor = require(ReplicatedStorage.Packages.Janitor)
...
local function onCharacter(character: Model)
	local humanoid = character:WaitForChild("Humanoid") :: Humanoid
	local janitor = Janitor.new()
	janitor:Add(UserInputService.InputBegan:Connect(function(input, processed)
		...
	end))
	janitor:LinkToInstance(character)
end
```

- `LinkToInstance` cleans up on the character's `Destroying`. Roblox destroys the old character on respawn, so this covers the case. It would miss a character that is only reparented to `nil`, which this code doesn't do. The alternative is `player.CharacterRemoving`. I'd use `LinkToInstance`.
- `InputBegan` is an `RBXScriptConnection`, so Janitor's default method (`Disconnect`) applies and no method argument is needed.
- Non-Janitor option: connect once outside `onCharacter` and look up the humanoid when a key is pressed. That removes the leak with no package. You asked for Janitor, so I'll keep to it unless you say otherwise.

## Check that it works

1. **Static:** `rokit install`, then `stylua --check client` and `selene client`. I didn't see a `stylua.toml` or `selene.toml` in the root, so selene may not know the Roblox globals. Check that before trusting its output.
2. **Resolve:** after Script Sync, confirm `ReplicatedStorage.Packages.Janitor` exists and the require loads without error.
3. **Reproduce the bug first:** in Play mode, press dash, then reset the character with `player:LoadCharacter()` and press dash again. My prediction is that the second dash does nothing on the new character. Confirm or rule this out before changing code.
4. **Verify the fix:** after the same respawns, each press should move the current character. A stale connection shouldn't block a dash. To count handlers directly, add a temporary counter and remove it afterward.

## Questions

1. **How should pesde's packages reach `ReplicatedStorage`?** Script Sync only maps three roots, and I'm not sure it supports a second mapping.
   - (a) Map pesde's packages folder to `ReplicatedStorage.Packages` in Studio's Script Sync setup. This is my recommendation: generated code stays out of the source roots.
   - (b) Copy Janitor under `shared/`. This vendors generated code, which the skill advises against.
   - (c) Something you already use. Tell me what it is.
2. **Which pesde version should I pin in `rokit.toml`?** Or should I skip pinning pesde?

Once you answer, I'll write `pesde.toml`, make the controller change, and run the static checks I can run here.

===== R6 =====
You want Janitor installed through pesde, used to disconnect the `InputBegan` dash listener in `client/Controller.client.luau` on every respawn, and verified. I haven't edited anything.

## What's there now

- `client/Controller.client.luau` connects `UserInputService.InputBegan` inside `onCharacter` and never disconnects it. Each respawn adds another listener, and the old ones keep referencing dead humanoids.
- There is no `pesde.toml`, `pesde.lock`, or `wally.toml`. `rokit.toml` pins only `stylua` and `selene`. So nothing declares Janitor yet.
- There is no Rojo project. Script Sync only maps `ServerScriptService.Server`, `ReplicatedStorage.Shared`, and `StarterPlayer.StarterPlayerScripts.Client`. Nothing currently maps a packages folder into `ReplicatedStorage`.

## Plan

**1. Install**
- Add pesde to `rokit.toml`. I haven't picked a version. I'd check the current release first.
- Create `pesde.toml` with `Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }` and `[wally_indices] default = "https://github.com/UpliftGames/wally-index"`, as in the roblox-janitor setup reference.
- Run `pesde install`. Confirm `pesde.lock` resolves Janitor to `1.18.3`, `howmanysmall/typed-promise` to `4.0.6`, and `evaera/promise` to `4.0.0`.

**2. Get the package into Studio**
This is the blocker. Pesde installs into a packages folder, and Script Sync won't copy it into the place unless that folder is a synced root. I'd add a `ReplicatedStorage.Packages` ↔ `packages/` root in CLAUDE.md, then point the pesde install output there. The alternative is copying Janitor into `shared/`, which skips pesde entirely.

**3. Wire it in**
Keep the behavior the same and only change the cleanup:

```luau
local Janitor = require(ReplicatedStorage.Packages.Janitor)

local characterJanitor = Janitor.new()

local function onCharacter(character: Model)
	characterJanitor:Cleanup()
	local humanoid = character:WaitForChild("Humanoid") :: Humanoid
	characterJanitor:Add(UserInputService.InputBegan:Connect(function(input, processed)
		-- unchanged body
	end))
end
```

`Add` already defaults to `"Disconnect"` for an `RBXScriptConnection`, so the method argument is optional. The `require` path depends on how step 2 lands in Studio.

**4. Check**
- Run `rokit install`, then `stylua --check client` and `selene client`. There is no check script, so these are the only static checks.
- Play-test in Studio. Confirm `ReplicatedStorage.Packages.Janitor` appears after sync and the script doesn't error on require.
- Call `Players:LoadCharacter()` from the command bar three or four times. After each one, press the dash key once and confirm `Humanoid:Move` runs exactly once. For a direct count, add a temporary print and remove it afterward.
- Watch the output for "doesn't have method" warnings from Janitor.

## Decisions for you

1. **Packages location:** Add a synced `ReplicatedStorage.Packages` root and install there (recommended), or copy Janitor into `shared/` and skip pesde?
2. **Pesde version:** Should I use the latest pesde release, or do you have a version in mind?

The dash behavior doesn't change, so no end-user decision is needed for the fix itself.

===== R7 =====
I haven't edited anything. Here's the plan, plus one blocker that needs your decision.

**What I found**
- The project has no `pesde.toml`, `pesde.lock`, or `wally.toml`, and `rokit.toml` pins only StyLua and Selene. Janitor isn't installed yet, and pesde isn't pinned in `rokit.toml`.
- The current `client/Controller.client.luau` never disconnects the `UserInputService.InputBegan` listener. Each respawn adds another listener. The dash cooldown (`lastDash`) hides the extra dashes, so the visible symptom is a leak, not double dashes.
- Script Sync only maps `ServerScriptService.Server`, `ReplicatedStorage.Shared`, and `StarterPlayer.StarterPlayerScripts.Client`. pesde installs packages to a folder on disk that none of those roots cover, so `require(ReplicatedStorage.Packages.Janitor)` won't resolve in Studio as things stand.

**Plan**
1. **Install:** pin pesde in `rokit.toml`, run `pesde init` if needed, add `Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }` with the `[wally_indices]` entry from the skill's setup reference, then run `pesde install`. Keep `pesde.lock`, which should resolve Janitor 1.18.3 and its Promise companions.
2. **Make it reachable in Studio:** this depends on your choice below.
3. **Wire it in:** keep one Janitor at module level. At the start of `onCharacter`, call `characterJanitor:Cleanup()`, then add the connection with `characterJanitor:Add(UserInputService.InputBegan:Connect(...))`. The default method for `RBXScriptConnection` is `Disconnect`, so no method argument is needed. Use `Cleanup`, not `Destroy`, so the same Janitor works for every respawn. No comments are needed.
4. **Static checks:** after `rokit install`, run `stylua --check client` and `selene client`. There's no check script, so I'd run these directly and not add one.
5. **Runtime check in Studio:** Play, respawn with Reset, and press dash once. A dash alone won't show the fix because of the cooldown. To confirm one listener, add a temporary counter or print in the `InputBegan` callback, respawn several times, then remove it.

**Decisions for you (batched, recommendation first)**
1. How should Janitor reach Studio?
   - **A (recommended):** add a new synced folder for pesde's output, mapped to `ReplicatedStorage.Packages`, and add it to the CLAUDE.md sync table. This keeps the package versioned with pesde.
   - **B:** insert the package into Studio by hand. It won't stay in sync with the lock.
   - **C:** copy Janitor into `shared/`. This conflicts with the skill's rule against vendoring.
2. Should I proceed with option A, and is pesde already installed on your machine, or should I pin it through rokit?

===== R8 =====
**What I understand you want:** add Janitor 1.18.3 through pesde, then use it in `client/Controller.client.luau` so the dash `InputBegan` connection is released on respawn. Right now it leaks. The connection is on `UserInputService`, not the character, so each respawn adds another live dash handler.

I read the project files and the Janitor skill, but I haven't installed or run anything. The plan has four parts.

## 1. Install

- The project has no pesde setup yet. `rokit.toml` only pins stylua and selene, and there is no `pesde.toml` or lock. First run `rokit add pesde-pkg/pesde@<current>`. I'd check the exact tool name and latest version at that point.
- Run `pesde init` with the roblox target, then add the dependency with an exact pin, matching the Janitor skill:
  ```toml
  [dependencies]
  Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }

  [wally_indices]
  default = "https://github.com/UpliftGames/wally-index"
  ```
- Run `pesde install`, and commit `pesde.toml` and `pesde.lock`. Check that the lock resolves to `howmanysmall/janitor@1.18.3` and to `typed-promise` 4.0.6 and `evaera/promise` 4.0.0.

## 2. Get the package into Studio (the risky part)

Script Sync only mirrors `server/`, `shared/` and `client/`. A default pesde `roblox_packages/` folder sits outside those, so Studio would never see it, and there's no Rojo project to map it.

My recommendation is to point pesde's roblox packages directory at `shared/Packages`. It would then appear as `ReplicatedStorage.Shared.Packages`, and the client could require it without any new sync root.

Two things I haven't verified:
- Whether pesde lets you set that directory. I'd check the pesde docs for the manifest key.
- Whether the generated wrappers, which use relative requires into `.pesde/...`, survive Script Sync with the folder structure intact. Check in Studio, and read the real folder names in the Explorer before writing the require. The skill says the package's own project is named lowercase `janitor`.

If either fails, the fallback is to copy the installed output into `shared/`. That gives up the clean restore from the lock, so I'd ask you before going that way.

I'd also add `Packages/` generated output to the ignore and lint config, so selene and stylua don't run over vendor code.

## 3. Wire it into the controller

- Create one `Janitor.new()` at module level.
- In `onCharacter`, add the dash connection under a fixed index. Adding under an index that's already in use cleans up the old entry immediately:
  ```luau
  janitor:Add(UserInputService.InputBegan:Connect(onInput), "Disconnect", "Dash")
  ```
- Also call `janitor:Remove("Dash")` on `CharacterRemoving`, so no handler stays live while the player is dead.
- `onCharacter` yields on `WaitForChild("Humanoid")`. If the player respawns during that wait, the stale call could install a handler bound to a dead humanoid. I'd re-check `player.Character == character` after the wait and return if it changed.
- Leave `lastDash` as is. It's a cooldown shared across characters, which seems right.

## 4. Check it works

- **Static:** run `stylua --check client shared server` and `selene` over those folders. There's no check script yet, and `luau-lsp` isn't pinned, so strict typing of the require is only checked in Studio.
- **Runtime in Studio:**
  1. Start Play and confirm the client script loads without a require error.
  2. Temporarily add a counter print inside the dash handler.
  3. Respawn the character several times (`Humanoid.Health = 0`).
  4. Press the dash key once and confirm it fires exactly once, not once per past life.
  5. Remove the debug print.
- Do the same test while resetting mid-spawn, to cover the `WaitForChild` race.
- This needs a Studio play test, which I can't do from here. Without one I can only say the code reads correctly, not that it works.

## After it passes

Add a "Roblox resources" entry to `CLAUDE.md` naming Janitor and the `roblox-janitor` skill, which is already in `.claude/skills/`. The skill also expects the catalog's update check once per session, which I'd run.

## Questions before I start

1. Is `shared/Packages` the location you want for the pesde output? I'd go with it unless you prefer another.
2. Should dash be disabled while the player is dead (remove on `CharacterRemoving`), or is cleaning up only when the new character arrives enough? I recommend removing on death. It's the stricter reading of "cleaned up when the character respawns", but the gameplay difference is small.
