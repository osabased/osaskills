# scriptsync-client

Question asked:

> We're using Roblox Studio's Script Sync. I'm putting our client controller at `client/Controller.client.luau`, with the `client/` folder synced to `StarterPlayer.StarterPlayerScripts.Client`. It should run once per player. Anything wrong with this setup?

## R1

## Think tank (solo): Script Sync client controller setup
opus · session effort · one panelist

### Recommendation
Yes, there's a problem. Script Sync doesn't follow Rojo's naming convention. A `.client.luau` file becomes a **`Script` with `RunContext = Client`**, not a `LocalScript`. Client-context Scripts run anywhere that replicates to the client, and that includes `StarterPlayerScripts` itself. That copy runs, and so does the clone the player gets in `Player.PlayerScripts`. Your controller would run **twice per player**.

Fixes, best first:
1. **Rename the file to `Controller.local.luau`.** That makes a `LocalScript`, and a LocalScript only runs from the PlayerScripts copy, so it runs once.
2. Or keep `.client.luau` and sync the folder to a container that isn't cloned per player, such as `ReplicatedStorage` or `ReplicatedFirst`.
3. Don't use `.legacy.luau` here. A Legacy Script in StarterPlayerScripts never runs.
4. As a last resort, add a guard at the top: `if not script:FindFirstAncestorOfClass("Player") then return end`.

Smaller points:
- In Script Sync you link an existing Studio instance to a folder on disk. Create the `Client` Folder first, and give it exactly the same name as the disk folder (`client` vs `Client`).
- Don't put attributes or tags on synced scripts.
- Script Sync is still a beta, so these mapping rules could change.

To confirm in a playtest, put `print(script:GetFullName())` in the controller and run Play Solo. If it prints twice, the double run is real.

Checked:
- **Mapping:** the Script Sync docs page says `name.client.luau` gives a "Script with `Client` RunContext" and `name.local.luau` gives a "`LocalScript`". Confirmed.
- **Double run:** Roblox's RunContext announcement (DevForum 1938784) says that in Starter containers "both the original scripts and their copies will run". It recommends Legacy RunContext or LocalScripts in those containers. I found no later edit reversing this. Confirmed.
- **Not checked:** how a name mismatch like `client` vs `Client` is handled. The docs don't say.

### Panelist
"The file becomes a `Script` named `Controller` with `RunContext = Client`, which runs twice per player (once from StarterPlayerScripts, once from PlayerScripts). Rename it to `Controller.local.luau` (LocalScript) or move the synced folder out of StarterPlayerScripts." Confidence: high on the mapping and the double run, since both come from Roblox sources. Medium on the naming and path details.

### My take
I agree, and the panelist settled the question I had at launch. I suspected the layout was fine but wasn't sure which instance type `.client.luau` produces. The docs answer it: a RunContext=Client Script. In StarterPlayerScripts that's exactly the double-run case Roblox warns about. Renaming to `Controller.local.luau` is the simplest fix and leaves your folder layout as it is. I'd keep the case of the folder names consistent as well, though the docs don't say whether a mismatch causes problems.

## R2

**Position:** Yes, the setup is broken. In Studio's native Script Sync, `Controller.client.luau` does not create a LocalScript. It creates a `Script` with `RunContext = Client`. A Client-RunContext Script inside StarterPlayerScripts runs twice on each player's client: once as the original in the Starter container and once as the copy placed in the player's PlayerScripts. The fix is to rename the file to `Controller.local.luau` so it becomes a real LocalScript. The other option is to keep `.client.luau` and move the folder out of every Starter container, for example to ReplicatedStorage.

**Reasoning:**
- **The suffix sets the class, and it differs from Rojo.** The official Script Sync page (https://create.roblox.com/docs/en-us/scripting/sync) has this naming table:
  - `name.luau` → ModuleScript
  - `name.server.luau` → Script, Server RunContext
  - `name.client.luau` → Script, Client RunContext
  - `name.local.luau` → LocalScript
  - `name.legacy.luau` → Script, Legacy RunContext
  - `name.plugin.luau` → Script, Plugin RunContext
  - `name/` → Folder
  - `name/init.*.luau` → script with children

  The German, Italian and Spanish versions of the page have the same table. In Rojo, `.client.luau` means LocalScript. The team has almost certainly carried that convention over, and it doesn't apply here.
- **Client RunContext in a Starter container runs twice.** The official "[Live] Script RunContext" announcement (https://devforum.roblox.com/t/live-script-runcontext/1938784) says Client-context scripts "run anywhere in the place including services such as ReplicatedStorage but only on the client." It also says "Starter containers work by cloning their contents locally therefore they will make a copy of any scripts contained in them… both the original scripts and their copies will run," and advises using "the Legacy RunContext or LocalScripts in these containers." Putting the script in a subfolder (`StarterPlayerScripts.Client`) doesn't help, because the whole subtree is cloned. Each player therefore gets two controller instances: doubled event connections, doubled UI, and possibly conflicting state.
- **A LocalScript runs once.** A LocalScript only runs from a client-owned location such as PlayerScripts, so the original copy in StarterPlayerScripts stays inactive. With `Controller.local.luau`, each player's client runs it exactly once.
- **Names and folders are fine.** The instance name is the file name minus the suffix, so you get `Controller`. The `client/` directory maps to a Folder. Script Sync only syncs Script, LocalScript, ModuleScript and Folder instances.

**Fixes:**
1. Rename the file to `client/Controller.local.luau`. This is the simplest fix. If the controller already exists in Studio as the wrong class, stop syncing first and check that the class actually changes when you re-sync.
2. Or keep `.client.luau` and sync the folder to ReplicatedStorage (or ReplicatedFirst). It then runs once per client and isn't cloned.

**Other sync caveats:**
- Script Sync is a Studio beta (File > Beta Features).
- The `client/` directory is lowercase but the instance is `Client`. If you sync from the Studio side, the directory name follows the instance name, so pick one form to avoid confusion. Windows file names ignore case.
- Don't keep non-script instances (RemoteEvents, attributes, tags) inside the synced folder. They are ignored, and the docs warn about data loss.
- In Team Create, two people syncing the same files can overwrite each other's changes.

**Risks and unknowns:**
- The whole position rests on two facts. First, the official table maps `.client.luau` to a Client-RunContext Script. I'm highly confident of this; it is quoted directly from the docs in several languages. Second, Client RunContext still runs twice inside Starter containers. That comes from the 2022 announcement plus later forum reports. If Roblox has since changed the engine to skip originals in Starter containers, the setup would work, but I found nothing saying so.
- I haven't checked whether Studio prompts you or silently converts the class when a suffix changes on an existing synced script.
- A quick test settles it: put `print(script:GetFullName())` in the controller and play-test. Two lines per client (one under StarterPlayerScripts, one under PlayerScripts) confirms the double run.

**Confidence:** High on the suffix-to-class mapping (official table). Medium-high on running twice (official announcement, older but not reversed as far as I found). High that renaming to `.local.luau` fixes it.

Position: The setup is wrong. `.client.luau` gives a Client-RunContext Script that runs twice per player under StarterPlayerScripts. Rename it to `Controller.local.luau`, or move it to ReplicatedStorage. Confidence: high.

## R3

**Position:** Yes, there's a problem. `Controller.client.luau` becomes a `Script` with `RunContext = Client`, not a `LocalScript`. Under `StarterPlayerScripts` it runs twice per player. Rename the file to `Controller.local.luau`.

**Reasoning:**

What I checked against sources:
- **What gets created.** The Script Sync docs ([create.roblox.com/docs/scripting/sync](https://create.roblox.com/docs/en-us/scripting/sync.md)) give this file-to-instance mapping:
  - `name.client.luau` becomes a **Script** with RunContext **Client**.
  - `name.local.luau` becomes a **LocalScript**.
  - `name.server.luau` becomes a Script with RunContext Server, and `name.legacy.luau` a Script with RunContext Legacy.
  - `name.luau` becomes a ModuleScript, and a directory becomes a **Folder**.

  So you get a Folder (`Client`) containing a Script with RunContext=Client. This is not Rojo's convention, where `.client.luau` gives a LocalScript.
- **Why it runs twice.** Roblox's RunContext announcement ([DevForum 1938784](https://devforum.roblox.com/t/1938784)) says Client-context scripts run "anywhere in the place… but only on the client." It also says Starter containers clone their contents to each player, so "both the original scripts and their copies will run," and it recommends LocalScripts or Legacy RunContext there. Each client therefore runs one copy in `StarterPlayer.StarterPlayerScripts.Client` and another in `Player.PlayerScripts.Client`. That's **two runs per player**. Community reports confirm the same double-run ([DevForum 2134741](https://devforum.roblox.com/t/local-script-running-twice/2134741)).

What I'm inferring:
- **Instance name.** It should be `Controller`, with the `.client` suffix stripped. The docs' table implies this but never says it outright.
- **Respawns.** It should be exactly two runs, not more, because PlayerScripts is filled once per session, not on each respawn. Under `StarterCharacterScripts` you'd get one run per spawn plus the original.
- **Every client, not just the owner.** Each client runs its own two copies. Players don't trigger runs in each other's sessions; the count is per client.

Other issues with the mapping and target path:
- Script Sync isn't driven by a project file like Rojo. You right-click an **existing** instance in Explorer and choose "Sync with…" to point it at a disk folder. So the `Client` Folder has to exist under StarterPlayerScripts first. I haven't verified how a name mismatch is handled (disk `client` versus instance `Client`, on a case-insensitive Windows filesystem). The safe move is to make the names identical.
- Script Sync ignores instances that aren't scripts or folders, and scripts that carry attributes or tags. The docs warn this can lose data, so keep tags and attributes off synced scripts.
- Script Sync is still a Studio beta (File > Beta Features). The mapping rules could change.

Fixes, best first:
1. Rename the file to **`Controller.local.luau`**. This makes a LocalScript, which runs only from the PlayerScripts copy, so once per player.
2. Or keep `.client.luau` but sync the folder to a container that isn't cloned, such as `ReplicatedStorage` or `ReplicatedFirst`. There it runs once per client.
3. Don't use `.legacy.luau` here. A Legacy Script in StarterPlayerScripts never runs.
4. As a last resort, keep the file and add a guard at the top, `if not script:FindFirstAncestorOfClass("Player") then return end`.

**Risks and unknowns:** My position rests mainly on two things: that Script Sync really does map `.client.luau` to RunContext=Client (the docs state this), and that the "Starter containers run both original and copy" behaviour still holds (it's in the announcement, but I didn't find an official fix). If Roblox changed either, the double run would go away. I didn't test the name-derivation and case-sensitivity details. A quick check settles it: run Play Solo with a `print(script:GetFullName())` in the controller. Two lines means my position holds.

**Confidence:** High on the class/RunContext mapping and the double run, since both come from Roblox sources. Medium on the minor details about names and path setup.

Position: The file becomes a `Script` named `Controller` with `RunContext = Client`, which runs twice per player (once from StarterPlayerScripts, once from PlayerScripts). Rename it to `Controller.local.luau` (LocalScript) or move the synced folder out of StarterPlayerScripts. Confidence is high. This depends on the documented `.client.luau` → RunContext Client mapping and the documented rule that Client-context scripts in Starter containers run both the original and the copy.

## R4

Yes, there's one real problem: with Studio's Script Sync, the `.client.luau` suffix creates the wrong kind of script. You want `.local.luau`.

**The problem**

Script Sync's naming rules are not the same as Rojo's:

| File on disk | What Studio creates |
|---|---|
| `name.client.luau` | **Script** with `RunContext = Client` |
| `name.local.luau` | **LocalScript** |
| `name.server.luau` | Script with `RunContext = Server` |
| `name.luau` | ModuleScript |

So `client/Controller.client.luau` becomes a Script with RunContext Client, not a LocalScript. Roblox's "Script locations" page warns that a Client-RunContext Script placed in a starter container runs twice. The container is copied to each client, "so the original script and the copy run, which isn't desirable." In your case the controller would run from `StarterPlayerScripts.Client` and again from the player's `PlayerScripts`. DevForum reports describe exactly this happening under StarterPlayerScripts.

**Fix:** rename it to `client/Controller.local.luau`. It becomes a LocalScript, which runs once from the player's copy.

**What's fine**

- **StarterPlayerScripts is the right place.** The docs say it "contains LocalScripts that run when the player joins the game." StarterCharacterScripts is the one that runs on each spawn.
- **Syncing the `client/` folder works.** A directory syncs as a Folder, and Script Sync handles Folder, Script, LocalScript and ModuleScript instances.

**Two smaller points**

- Script Sync is still a Beta Feature (File ▸ Beta Features).
- The docs say not to sync scripts that have attributes or tags. Those aren't kept on disk and can be lost.

**What I checked**

- **Confirmed in the official Script Sync docs:** the suffix table above, that a directory becomes a Folder, which instance types sync, the beta status, and the attributes/tags warning.
- **Confirmed in the official "Script locations" page:** the warning about Client-RunContext Scripts in starter containers, and the join-vs-spawn descriptions of StarterPlayerScripts and StarterCharacterScripts.
- **Not confirmed in official docs:**
  - The pages I read don't say outright that StarterPlayerScripts is copied only on join and not again on respawn. "Run when the player joins" strongly suggests it, and it matches long-standing engine behavior.
  - The class reference pages for Script, BaseScript and RunContext don't explain how RunContext behaves, so the double-run comes from the locations guide plus DevForum reports, not an API page.
  - I couldn't check your actual project because it isn't in this directory.

Sources:
- [Script Sync (Roblox docs)](https://create.roblox.com/docs/scripting/sync)
- [Script locations (Roblox docs)](https://create.roblox.com/docs/scripting/locations)
- [[Live] Script RunContext (DevForum)](https://devforum.roblox.com/t/live-script-runcontext/1938784)
- [Rojo sync details](https://rojo.space/docs/v7/sync-details) (for comparison only, it uses the other naming convention)

## R5

## Think tank (solo): Script Sync client controller setup
opus · session effort · one panelist

### Recommendation
The setup is wrong, and the file suffix is the cause. In Studio's own Script Sync, `Controller.client.luau` doesn't create a LocalScript. It creates a `Script` with `RunContext = Client`. That differs from Rojo, where `.client.luau` does mean LocalScript.

Scripts in StarterPlayerScripts get copied into each player's PlayerScripts. A Client-RunContext script runs from both places: the original in StarterPlayerScripts and the copy. So the controller runs **twice per player**, which doubles event connections and UI and can make state conflict. Putting it in the `Client` subfolder makes no difference, because the whole folder gets copied.

There are two fixes:
1. Rename the file to `client/Controller.local.luau` so it becomes a real LocalScript, which runs once from PlayerScripts. This is the simplest fix. If the script already exists in Studio, check that its class actually changes after you rename it.
2. Or keep `.client.luau` and sync the folder to ReplicatedStorage or ReplicatedFirst instead. Nothing copies it there, so it runs once on each client.

The rest of the setup is fine. The script will be named `Controller` and the `client/` directory becomes a Folder. A few smaller cautions:
- Script Sync is still a beta feature.
- The directory is lowercase `client` but the instance is `Client`, so settle on one spelling.
- Script Sync ignores anything that isn't a script or folder, such as RemoteEvents or attributes, so don't keep those inside the synced folder.
- In Team Create, two people syncing the same files can overwrite each other.

To confirm the double run, put `print(script:GetFullName())` in the controller and play-test. Two lines per client means it's running twice.

Checked:
- **Suffix mapping:** confirmed on the official Script Sync page (create.roblox.com/docs/scripting/sync). It lists `name.client.luau` as "Script with Client Script.RunContext" and `name.local.luau` as "LocalScript".
- **Running twice in Starter containers:** confirmed in Roblox's "[Live] Script RunContext" announcement on the DevForum. It says Starter containers copy their scripts and that "both the original scripts and their copies will run". It also advises using "the Legacy RunContext or LocalScripts in these containers." That post is from 2022. I found nothing saying Roblox has changed this, but the print test above would show it either way.

### Panelist
"The setup is wrong. `.client.luau` gives a Client-RunContext Script that runs twice per player under StarterPlayerScripts. Rename it to `Controller.local.luau`, or move it to ReplicatedStorage. Confidence: high." High confidence.

### My take
The panelist changed my mind. Before launching, I thought the setup was fine, with only a vague doubt about the suffix. I was right that the suffix was the weak point, but I underestimated what follows from it. Getting a Client-RunContext Script instead of a LocalScript doesn't just change the class: it makes the script run twice. I agree with the panelist, and I'd take fix 1 and rename the file to `.local.luau`. It keeps your folder where it is and is the usual pattern for StarterPlayerScripts. Choose fix 2 only if you specifically want RunContext scripts throughout. If anyone on the team also uses Rojo, write down that the two tools read `.client.luau` differently, because this mistake is easy to repeat.

## R6

Yes, there's one real problem. With Script Sync, the `.client.luau` suffix doesn't create a LocalScript, and in StarterPlayerScripts that causes the controller to run twice on each client.

**What the official docs say:**

1. **Verified:** In the [Script Sync docs](https://create.roblox.com/docs/scripting/sync), the file-name table maps `name.client.luau` to a **Script with RunContext set to Client**. `name.local.luau` is what becomes a **LocalScript**. This is different from Rojo, where `.client.lua` becomes a LocalScript ([Rojo sync details](https://rojo.space/docs/v6/sync-details/)), so habits from Rojo will catch you out here.
2. **Verified:** The [Script types and locations](https://create.roblox.com/docs/scripting/locations) page says Client-RunContext Scripts can run in StarterPlayerScripts, but "Starter containers are copied to clients, though, so the original script and the copy run, which isn't desirable." It recommends ReplicatedStorage for Client-RunContext Scripts.
3. **Verified (wording differs slightly):** The same page says StarterPlayerScripts "contains LocalScripts that run when the player joins the game," and that scripts there are copied into player containers rather than run from one place. It doesn't use the words "once per player." But a LocalScript there running once on each player's client when they join is the documented behaviour.

So as it stands, `Controller.client.luau` becomes a Client Script that runs twice for each player: once as the original under `StarterPlayer.StarterPlayerScripts.Client`, and once as the copy in `PlayerScripts`.

**Fix (pick one):**
- **Rename it to `client/Controller.local.luau`.** It becomes a LocalScript, and StarterPlayerScripts is the standard place for those. This is the smallest change and matches what you're after.
- Or keep `.client.luau` but sync the folder into `ReplicatedStorage` instead. Note that this changes when and where it runs compared with the per-player copy.

**Other things from the Script Sync docs (verified) worth knowing:**
- You set up syncing from Studio: select the folder in the Explorer, right-click, choose **Sync to…**, then pick the directory. The docs recommend syncing folders rather than single scripts.
- Child folders and scripts sync automatically, and Studio syncs creates, renames, moves and deletes. Any other instance types inside the synced folder are ignored.
- Don't sync scripts that have attributes or tags. Script Sync ignores them, which the docs warn can lose data.
- Avoid having several people sync and edit the same script at the same time.

**Not verified:** The API reference pages for `RunContext`, `BaseScript` and `Script` had no descriptive text when I fetched them. The double-run claim rests on the Script types and locations guide. DevForum threads report the same behaviour, but I'm treating those as supporting evidence, not documentation.

Sources:
- [Script Sync – Roblox Creator Docs](https://create.roblox.com/docs/scripting/sync)
- [Script types and locations – Roblox Creator Docs](https://create.roblox.com/docs/scripting/locations)
- [Rojo sync details](https://rojo.space/docs/v6/sync-details/)
- [DevForum: [Live] Script RunContext](https://devforum.roblox.com/t/live-script-runcontext/1938784?page=5)
- [DevForum: Local script running twice](https://devforum.roblox.com/t/local-script-running-twice/2134741)

## R7

## Think tank (solo): Script Sync client controller in StarterPlayerScripts
opus · session effort · one panelist

### Recommendation
The setup is wrong: the controller will run **twice per player**, not once. Script Sync turns `Controller.client.luau` into a `Script` with `RunContext = Client`, not a `LocalScript`. Starter containers copy their contents to each player, and a Client-context script runs anywhere the client can see it. So both the original in `StarterPlayerScripts` and the copy in `PlayerScripts` will run. You'd get doubled event connections, doubled UI and doubled remote calls. The two copies also have different `script.Parent` chains, so path-based lookups would behave differently in each.

The fix is to **rename the file to `client/Controller.local.luau`**. Script Sync then creates a `LocalScript`, which only runs from the `PlayerScripts` copy. Other options:
- Keep `.client.luau` but move it somewhere that isn't copied per player, such as `ReplicatedStorage`.
- Add a guard at the top of the script: `if not script:FindFirstAncestorWhichIsA("Player") then return end`.

Don't use `.legacy.luau`: the controller would never run on the client.

Checked:
- **How Script Sync maps file names.** The Creator Docs Script Sync page shows `name.client.luau` → "Script with Client RunContext" and `name.local.luau` → "LocalScript". This is the opposite of what Rojo users expect, since Rojo makes `.client.luau` a LocalScript. Confirmed.
- **Both copies run.** The DevForum "[Live] Script RunContext" post says Starter containers "make a copy of any scripts contained in them" and that with Client/Server RunContext "both the original scripts and their copies will run." It recommends Legacy or LocalScripts in those containers. Confirmed, though the post is from 2022–23.

### Panelist
"Yes, this setup is wrong: the controller will run twice per player, not once. Script Sync turns `Controller.client.luau` into a `Script` with `RunContext = Client`, not a `LocalScript`. Client-context scripts run wherever they replicate to the client, so both the original in `StarterPlayerScripts` and the copy placed in `PlayerScripts` will run. The fix is to rename the file `Controller.local.luau`." High confidence. Both key facts come from official Roblox sources; the remaining doubt is whether the engine has changed since.

### My take
I agree, and the panelist confirmed my suspicion rather than changing my mind. My leaning at launch was that this depended on what `.client.luau` becomes, and the docs settle it: it becomes a Client-context Script, so the code runs twice. Renaming to `.local.luau` is the simplest fix and keeps your folder layout as it is.

Before you commit to it, try the panelist's quick check in Play Solo: put `print(script:GetFullName())` in the controller and look for two lines printed. That confirms the double run on your current Studio version, since the RunContext post is a few years old. If your team is used to Rojo, check any other `.client.luau` files in Starter containers too, because they'll have the same problem.

## R8

Yes, there's a problem: **with this setup the controller will run twice per player.**

**Why.** In Studio's built-in Script Sync, `.client.luau` doesn't create a LocalScript. The official naming table says:

| On disk | In Studio |
|---|---|
| `name.client.luau` | `Script` with `RunContext = Client` |
| `name.local.luau` | `LocalScript` |

So `Controller.client.luau` becomes a Client-context Script. Roblox's "Script types and locations" page says that when a Client-context Script is in `StarterPlayerScripts` or `StarterCharacterScripts`, "Starter containers are copied to clients, though, so the original script and the copy run, which isn't desirable." Each client would run one copy from `StarterPlayer.StarterPlayerScripts` and another from its own `PlayerScripts`.

This is a common trap because Rojo uses `.client.lua(u)` for LocalScripts. Studio's Script Sync uses the same suffix differently.

**Two fixes, either one works:**
1. **Keep the folder and rename the file** to `client/Controller.local.luau`. It becomes a LocalScript, which the docs say is what Starter containers should use.
2. **Keep `.client.luau` and move the sync target** to somewhere like `ReplicatedStorage.Client`. The docs recommend "a single Script with a RunContext of Client" in ReplicatedStorage, where it runs once per client. If the controller is meant to own all client startup, this is the more current pattern.

**What I checked against official docs:**
- `.client.luau` → Script with Client RunContext, and `.local.luau` → LocalScript: confirmed in the naming table on the [Script Sync page](https://create.roblox.com/docs/en-us/scripting/sync.md).
- Syncing a folder also syncs the scripts and subfolders inside it, so `client/` maps as you expect: confirmed on the same page.
- Client-context Scripts in Starter containers run twice, Starter containers should use LocalScripts, and ReplicatedStorage can hold a Client-context Script: confirmed in [Script types and locations](https://create.roblox.com/docs/en-us/scripting/locations.md).

**What I didn't check:**
- Whether `StarterPlayerScripts` can be the target of a folder sync. The Script Sync page doesn't mention it, and I'm assuming it works.
- The [DevForum RunContext thread](https://devforum.roblox.com/t/live-script-runcontext/1938784) has staff and community reports of the same double-run behavior. It's unofficial and only backs up what the docs already say.
- I didn't test anything in Studio. Your project isn't in this directory, so all of this comes from your description and the docs.

Sources:
- [Script Sync – Roblox Creator Docs](https://create.roblox.com/docs/en-us/scripting/sync)
- [Script types and locations – Roblox Creator Docs](https://create.roblox.com/docs/en-us/scripting/locations)
- [[Live] Script RunContext – DevForum](https://devforum.roblox.com/t/live-script-runcontext/1938784)
- [Rojo sync details](https://rojo.space/docs/v6/sync-details/)

## R9

**Position:** Yes, this setup is wrong: the controller will run twice per player, not once. Script Sync turns `Controller.client.luau` into a `Script` with `RunContext = Client`, not a `LocalScript`. Client-context scripts run wherever they replicate to the client, so both the original in `StarterPlayerScripts` and the copy placed in `PlayerScripts` will run. The fix is to rename the file `Controller.local.luau`.

**Reasoning:**

What the documentation confirms:
- **How Script Sync names map to instances.** The Creator Docs page for Script Sync (create.roblox.com/docs/scripting/sync, English and localized versions) gives this table:
  - `name.luau` becomes a ModuleScript.
  - `name.server.luau` becomes a Script with RunContext Server.
  - `name.client.luau` becomes a Script with RunContext Client.
  - `name.local.luau` becomes a LocalScript.
  - `name.legacy.luau` and `name.plugin.luau` become Scripts with the Legacy and Plugin RunContexts.

  Script Sync is not Rojo, which maps `.client.luau` to a `LocalScript`. A team used to Rojo would expect a LocalScript and get a Client-context Script instead.
- **Why that runs twice.** The DevForum "[Live] Script RunContext" announcement (devforum.roblox.com/t/live-script-runcontext/1938784) says Client scripts "will run anywhere in the place including services such as ReplicatedStorage but only on the client." Its FAQ adds that Starter containers clone their contents to each player, and with the Client or Server RunContext "both the original scripts and their copies will run." It recommends LocalScripts or the Legacy RunContext in Starter containers. DevForum threads report the duplicate execution in StarterPlayerScripts, StarterCharacterScripts and StarterGui.

What I'm inferring:
- Each client sees two copies: the replicated original at `StarterPlayer.StarterPlayerScripts.Client.Controller`, and the copy at `Players.LocalPlayer.PlayerScripts.Client.Controller`.
- Both copies run on every client, so you get double event connections, double UI and double remote calls. The server never runs it.
- It won't run zero times. Respawning doesn't re-run it, because PlayerScripts is only filled once per player (unlike StarterCharacterScripts).
- The original copy's `script.Parent` chain sits under StarterPlayer, not PlayerScripts. Any path-based `require`s or lookups will therefore behave differently between the two copies.

Fixes, in order of preference:
1. **Rename the file to `client/Controller.local.luau`.** Script Sync then creates a LocalScript. LocalScripts only run from containers like PlayerScripts, so the original in StarterPlayerScripts stays inert and the code runs once.
2. **Or keep `.client.luau` but move it** to a location that isn't cloned per player, such as `ReplicatedStorage` or `ReplicatedFirst`. Those replicate once to each client, so the script runs once. Note that ReplicatedFirst code runs earlier, before the game has fully loaded.
3. **As a backstop, add a guard** at the top of the script: `if not script:FindFirstAncestorWhichIsA("Player") then return end`.

Don't use `.legacy.luau` here. A Legacy Script doesn't run in PlayerScripts on the client, so the controller would run zero times.

**Risks and unknowns:**
- My conclusion depends most on two facts:
  - Script Sync maps `.client.luau` to a Client-context Script. I confirmed this from the current docs table.
  - Roblox still runs both the original and the clone of Client-context scripts in Starter containers. I confirmed this from the RunContext announcement FAQ, which is from 2022–23. The current engine API pages (BaseScript, Enum.RunContext) describe neither point.
- If Roblox has since stopped Client scripts running inside Starter containers, or changed what the Script Sync suffixes mean, the setup would be fine. Script Sync is still evolving (I couldn't confirm its current beta status), so this mapping could change.
- I haven't run this in Studio. A two-line `print(script:GetFullName())` test in Play Solo would settle it: two lines printed means the bug is present.

**Confidence:** High. Both key facts come from official Roblox sources, and community reports agree. The remaining doubt is whether the behaviour has changed since then.

Sources: [Script Sync docs](https://create.roblox.com/docs/scripting/sync), [Script Sync (vi-vn)](https://create.roblox.com/docs/vi-vn/scripting/sync), [[Live] Script RunContext](https://devforum.roblox.com/t/live-script-runcontext/1938784), [Local script running twice](https://devforum.roblox.com/t/local-script-running-twice/2134741), [Enum.RunContext](https://create.roblox.com/docs/reference/engine/enums/RunContext)
