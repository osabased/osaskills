# scriptsync-client

Question asked:

> We're using Roblox Studio's Script Sync. I'm putting our client controller at `client/Controller.client.luau`, with the `client/` folder synced to `StarterPlayer.StarterPlayerScripts.Client`. It should run once per player. Anything wrong with this setup?

## R1

## Think tank: Script Sync client controller in StarterPlayerScripts
opus, sonnet, sonnet · session effort · identical brief · debate skipped at 3–0

### Recommendation (3–0)
Yes, this setup is wrong. Studio's Script Sync does not follow Rojo's naming. A file ending in `.client.luau` becomes a **`Script` with `RunContext = Client`**, not a `LocalScript`. Inside `StarterPlayerScripts`, a Client-context `Script` runs twice for each player:
- the copy cloned into `Players.<name>.PlayerScripts` runs;
- the original left in `StarterPlayer.StarterPlayerScripts` also runs, because StarterPlayer replicates to the client.

That means two controllers per player: input bound twice, remote listeners firing twice, duplicate UI.

You can fix it either way:
1. **Keep the location** and rename the file to `Controller.local.luau`. That makes it a `LocalScript`, which only runs from the per-player copy.
2. **Keep `.client.luau`** and sync `client/` to `ReplicatedStorage` instead. A single Client-context `Script` there runs once per client, and that is the pattern Roblox's docs recommend.

All three put a `Player`-ancestor guard in the script last, as a hacky fallback.

Checked:
- [Script Sync docs](https://create.roblox.com/docs/en-us/scripting/sync): `name.client.luau` gives a "Script with Client Script.RunContext", `name.local.luau` gives a "LocalScript", and a directory gives a "Folder". Confirmed.
- [Script locations docs](https://create.roblox.com/docs/scripting/locations): for Client-context Scripts in starter containers, "the original script and the copy run, which isn't desirable". The same page recommends "a single Script with a RunContext of Client into ReplicatedStorage". Confirmed.

### Panel
- **A** (opus): "Yes, the setup has a bug. Under Script Sync, `Controller.client.luau` becomes a `Script` with `RunContext = Client`, not a `LocalScript`. Inside StarterPlayerScripts that kind of script runs twice for each player. Rename the file to `Controller.local.luau` so it becomes a `LocalScript`, which runs once." High.
- **B** (sonnet): "Yes, there is a problem. `Controller.client.luau` becomes a `Script` with `RunContext = Client`, not a `LocalScript`. Under `StarterPlayerScripts` it will run twice per player. Rename it to `Controller.local.luau`, or sync the folder somewhere like `ReplicatedStorage` instead." High on the mapping and the double run; medium on the exact path.
- **C** (sonnet): "The setup is wrong. `Controller.client.luau` becomes a Client-RunContext Script, which runs twice per player in StarterPlayerScripts. Use `.local.luau`, or put it in ReplicatedStorage." Medium-high.

Points they raised beyond the main bug:
- **Don't put attributes or tags on synced scripts.** Script Sync ignores them, which can lose data. (A, B, C)
- **A script with children needs `init.*.luau`,** not a folder and a file with the same name. (C)

### Where they split
- **Does `.legacy.luau` also work?** C listed it as an alternative. A said not to use it. The docs back A: a Legacy Script "is a server-side script and only runs if it is in a server container, such as ServerScriptService or Workspace." So a `.legacy.luau` controller in StarterPlayerScripts would never run on the client. C is wrong on this point.

### My take
I launched suspecting exactly this trap, and the panel plus the docs confirmed it, so I didn't move. The docs settle both the class mapping and the double run. The one thing not tested is a live Studio session. A `print(script:GetFullName())` during playtest would show it directly: you should see two lines, one under `StarterPlayer` and one under `PlayerScripts`.

Which fix to pick depends on how you structure client code:
- If you want one client entry point that requires ModuleScripts, sync `client/` to `ReplicatedStorage` and keep `.client.luau`. That matches the docs and you avoid the cloning entirely.
- If you'd rather keep the StarterPlayerScripts layout, rename the file to `Controller.local.luau`.

Either way, don't use `.legacy.luau`.

## R2

**Position:** The setup is fine. `client/Controller.client.luau` becomes a Script with `RunContext = Client` inside a Folder in StarterPlayerScripts, and it runs once per player on that player's client. I found no real defect, only a few things to check.

**Checked against the docs** ([Script Sync](https://create.roblox.com/docs/en-us/scripting/sync.md), [Script locations](https://create.roblox.com/docs/en-us/scripting/locations)):
- `name.client.luau` becomes a **Script with `RunContext = Client`**. It is not a LocalScript. LocalScript is `name.local.luau`. This is the same convention as Rojo's `.client.lua`, which produces a LocalScript or a Client-context Script, so the Rojo mapping is not a safe guide here.
- A directory becomes a **Folder**, and `init.*.luau` makes a script with children. `client/` has no init file, so `Client` is a Folder, and `Controller` is a child Script with `RunContext = Client`.
- The locations page lists StarterPlayerScripts as a place where Client-context Scripts run. Scripts in those containers "clone to player containers rather than running from one location", for example `Players.<Name>.PlayerScripts`. The original under StarterPlayerScripts does not run itself. Each player therefore gets one copy and one execution.
- The sync mapping and the lists of supported classes and limits come from the Script Sync page. The class-level reference page I fetched had nothing on RunContext, so the RunContext behavior comes from the locations page above.

**Points to check, none of them blocking:**
1. **The Client target must already be an instance in Studio.** The docs say you pick a directory when setting up sync, but they don't describe mapping a folder onto an existing instance. My understanding, from memory and not confirmed in the docs, is that you start sync from an instance in the Explorer. Create `StarterPlayerScripts.Client` as a Folder first, then right-click it and sync it to `client/`. If it doesn't exist, you get no script and nothing runs (zero runs).
2. **Don't make the synced root itself a script.** If you add `client/init.client.luau`, `Client` becomes a Script with children. That script would also run, and so would `Controller`, so you would get double execution. Keep the root a plain Folder.
3. **Script Sync ignores attributes and tags, and the docs warn this can cause data loss.** Don't rely on attributes, tags, or other non-synced instances such as a RemoteEvent or a Value under `Client`. Only Script, LocalScript, ModuleScript and Folder sync.
4. **Avoid a second copy elsewhere.** Don't also put the controller in ReplicatedStorage, ReplicatedFirst or StarterCharacterScripts, because each of those would run it again. Also, `StarterPlayerScripts` is copied once at join. A Client script in StarterCharacterScripts would run on every respawn.
5. **Sync housekeeping.** Script Sync is a Studio beta, so it must be enabled under File > Beta Features. Stop sync before deleting a top-level synced instance on disk. In Team Create, simultaneous edits of the same script can overwrite each other.
6. **Optional style point.** If `Controller` is meant to be a library for other scripts, `.luau` would make it a ModuleScript. As a top-level entry point, `.client.luau` is correct. `.local.luau` would also work and gives an old-style LocalScript, but it isn't needed.

**Confidence:** High that the setup is correct and runs once per player. Medium on the exact "create the target first" workflow.

**What the answer depends on most:**
- The `.client.luau` mapping to a Script with `RunContext = Client` (verified).
- Client-context Scripts running from StarterPlayerScripts through the usual clone to PlayerScripts (verified for the clone and the allowed location).
- Whether nested Folders are cloned into PlayerScripts with their descendants. The page I fetched doesn't say, and I'm relying on memory that they are. If a Studio test shows the script not running from the folder, or running more than once, this assumption is wrong.

## R3

**Position:** Yes, there is a problem. `Controller.client.luau` becomes a `Script` with `RunContext = Client`, not a `LocalScript`. Under `StarterPlayerScripts` it will run twice per player. Rename it to `Controller.local.luau`, or sync the folder somewhere like `ReplicatedStorage` instead.

**Reasoning**

*Confirmed from docs*
- **What Studio creates.** The [Script Sync docs](https://create.roblox.com/docs/en-us/scripting/sync.md) have a suffix table.
  - `name.client.luau` becomes a `Script` with `RunContext = Client`.
  - `name.local.luau` becomes a `LocalScript`.
  - `name.luau` becomes a `ModuleScript`.
  - `name.server.luau` becomes a `Script` with `RunContext = Server`.
  - A directory becomes a `Folder`.
  - So `client/Controller.client.luau` gives a `Script` named `Controller`, `RunContext = Client`. It sits under whatever instance you synced `client/` to. I assume that instance is a Folder named `Client`, so the path is `StarterPlayer.StarterPlayerScripts.Client.Controller`.
- **Why it runs twice.** The [script locations doc](https://create.roblox.com/docs/en-us/scripting/locations.md) says a Client-context `Script` can run from `StarterPlayerScripts`, but "the original script and the copy run, which isn't desirable." Starter containers are cloned to each client. The copy lands in `Players.<Name>.PlayerScripts`. The original, still in `StarterPlayerScripts`, also executes. The result is two executions per player, which breaks the "exactly once" requirement.
- **Doc-recommended fixes.** The same page says to put a single Client-context `Script` in `ReplicatedStorage`. If you need a `LocalScript`, put it in `StarterPlayerScripts` and similar containers. The [RunContext reference](https://create.roblox.com/docs/en-us/reference/engine/enums/RunContext.md) says only `Script` supports non-Legacy values, and `LocalScript` does not.
- **Same-behavior reports.** A web search turned up a DevForum thread, "[Live] Script RunContext", that I did not open. Per the search summary, developers there report the same double run. The workaround suggested was an ancestor check.

*Inferred*
- **Once per player.** A `LocalScript` in `StarterPlayerScripts` runs once per join, not per respawn. The docs say these scripts run "when the player joins" and tie respawn behavior to `StarterCharacterScripts`. They don't state it outright.
- **Nesting.** I assume a Folder nested inside `StarterPlayerScripts` is cloned whole, so the nested script is affected the same way. I did not verify this.
- **Existing instance.** I assume `Client` already exists as a Folder in the place, and that Script Sync only populates its children.

**What to do instead (pick one)**
1. Rename the file to `Controller.local.luau`. It becomes a `LocalScript` and keeps the `StarterPlayerScripts.Client` mapping. This is the smallest change.
2. Keep `.client.luau` and sync `client/` to `ReplicatedStorage` (for example `ReplicatedStorage.Client`). This is the docs' recommended modern pattern. A Client-context script there runs once per client, with no copy.
3. If it must stay under `StarterPlayerScripts`, add a guard such as exiting when the script has no `Player` ancestor. This is hacky.

**Other layout notes**
- Script Sync syncs only `Script`, `LocalScript`, `ModuleScript` and `Folder`. Other instances in the synced folder are ignored.
- Attributes and tags on synced scripts can cause data loss.
- Names must be valid on the filesystem.
- Sync is a Studio beta feature that you enable under Beta Features.
- Don't assume Rojo's mapping. Some Rojo versions treat `.client.luau` as a `LocalScript`, but Script Sync does not.

**Risks and unknowns**
- I could only read the English sync page through a summarizing fetch tool. Its table matched the localized pages, but I didn't see the raw page.
- I did not run this in Studio. If Roblox has changed double-execution for Client-context scripts in starter containers since the docs were written, option 1 is still safe.
- The sync page doesn't mention `StarterPlayerScripts`.
- Evidence that would change my mind: a Studio test that shows a single print.

**Confidence:** High on the instance mapping and the double run, because both come directly from the docs. Medium on the exact path and the respawn detail.

## R4

## Think tank: Script Sync client controller in StarterPlayerScripts
opus, sonnet, sonnet · session effort · identical brief · debate

### Recommendation (3–0; 2–1 before debate, with Opus and one Sonnet against the other Sonnet)
Yes, there is a bug. The controller will run **twice per player**, not once. Rename the file to `client/Controller.local.luau`.

- **Why it runs twice:** Script Sync turns `.client.luau` into a `Script` with `RunContext = Client`, not a `LocalScript`. A Client-context Script inside a Starter container runs as the original in `StarterPlayer.StarterPlayerScripts` and again as the copy in `Player.PlayerScripts`. That gives you duplicate connections, RemoteEvent handlers and UI setup.
- **Why the rename works:** `.local.luau` gives a `LocalScript`, and only its `PlayerScripts` copy runs.
- **Rojo:** in Rojo, `.client` means a LocalScript. That meaning doesn't carry over to Script Sync.

Alternatives:
- **Move the sync target:** keep `.client.luau` and sync `client/` to a Folder in ReplicatedFirst or ReplicatedStorage instead. Nothing there gets cloned, so it runs once.
- **Don't use `.legacy.luau`:** a legacy Script never runs on the client, so the controller would run zero times.

Secondary points the panel agreed on:
- Create the `StarterPlayerScripts.Client` Folder in Explorer before you start syncing.
- Don't put an `init.*.luau` file at the folder root. It would turn `Client` itself into a script. (B → A, C)
- Script Sync ignores attributes and tags, so they can be lost.

Checked:
- **Script Sync naming table** (create.roblox.com/docs/en-us/scripting/sync): `name.client.luau` is a "Script with Client RunContext" and `name.local.luau` is a "LocalScript". Sync starts from Explorer: select a folder, then "Sync to…". Confirmed.
- **Script locations page** (create.roblox.com/docs/en-us/scripting/locations): "Starter containers are copied to clients, though, so the original script and the copy run, which isn't desirable." The caption says "Starter[] containers should use LocalScripts." Confirmed.
- Neither page was tested at runtime. The panel didn't run Studio, and neither did I.

### Panel
- **A** (opus): "The setup has a real bug. Script Sync turns `Controller.client.luau` into a `Script` with `RunContext = Client`. In `StarterPlayerScripts`, the original and its `PlayerScripts` copy both run, so the controller runs twice on each client instead of once. Rename the file to `Controller.local.luau`, or sync the folder into `ReplicatedStorage` or `ReplicatedFirst` instead." High confidence.
- **B** (sonnet): "The setup has a real bug, and I'm reversing my earlier answer. `Controller.client.luau` becomes a Script with `RunContext = Client`, and in `StarterPlayerScripts` it runs twice per player: once as the original and once as the copy in `PlayerScripts`. Rename it to `Controller.local.luau`." High confidence on the facts, medium-high on current runtime behaviour. It changed its answer after re-reading the locations page itself. In round 1 it had taken "clone to player containers" to mean the original doesn't run, and missed the "original script and the copy run" sentence.
- **C** (sonnet): "The setup has a real bug. `Controller.client.luau` becomes a `Script` with `RunContext = Client`. In `StarterPlayerScripts` that script runs twice per player, once as the original and once as the copy in `PlayerScripts`. Rename it to `Controller.local.luau`, or sync the folder somewhere that isn't cloned." High confidence.

### Where they split
In round 1 the only disagreement was whether the original copy under `StarterPlayerScripts` runs. B read the docs as saying only the clone runs. The docs say both run, and I confirmed that above. Everyone has the same remaining caveat: the sources date from 2022–docs era, and the engine could have changed since. A one-line test settles it. Put `print(script:GetFullName())` in the controller and Play Solo. Two lines (one from `StarterPlayer…`, one from `Players.<you>.PlayerScripts…`) means the bug is real. Either way, the rename is safe.

### My take
I agree with the panel. At launch I flagged the `.client` mapping as the thing to check but couldn't remember whether originals in Starter containers run. The docs settled it, and they say the panel is right. Your intent of "once per player, from StarterPlayerScripts" is exactly what a `LocalScript` is for, so I'd use `.local.luau` and keep the layout.

## R5

Yes, there's one real problem: with this setup the controller will run **twice per player**, not once.

**Why:** In Script Sync, the file suffix decides what kind of script you get. A `.client.luau` file doesn't become a `LocalScript`. It becomes a `Script` with `RunContext = Client`. Scripts like that run anywhere in the place, and that includes the Starter containers themselves. When a player joins, StarterPlayerScripts copies its contents into that player's `PlayerScripts`. Roblox's RunContext announcement says that in this case "both the original scripts and their copies will run." So the copy in `StarterPlayerScripts.Client` runs, and so does the copy in `PlayerScripts.Client`. That gives you duplicate connections, duplicate UI, and so on.

**Fix (choose one):**
- **Rename it to `client/Controller.local.luau`.** The `.local.luau` suffix creates a real `LocalScript`, and LocalScripts only run from the per-player copy. This is what Roblox recommends for Starter containers. It's the smallest change and leaves your folder mapping as it is.
- **Or keep `.client.luau` but sync the folder somewhere that isn't a Starter container,** such as `ReplicatedFirst` or `ReplicatedStorage`. A Client-RunContext script there runs once on each client. Use this if you'd rather standardize on RunContext scripts.

Don't use `.legacy.luau` either. A Legacy-context `Script` in StarterPlayerScripts behaves like a server script and won't run on the client at all.

The rest of the setup is fine:
- StarterPlayerScripts is the right container for "once per player." Its contents are copied when the player joins, not each time they respawn. StarterCharacterScripts is the one that re-runs on every spawn.
- The `client/` directory will sync as a plain `Folder` named `Client`, which is fine. Just make sure there's no `init*.luau` file directly inside `client/`. If there is, the folder becomes a script instead of a Folder.

Sources:
- [Script Sync – Roblox Creator Docs](https://create.roblox.com/docs/scripting/sync)
- [creator-docs sync.md on GitHub](https://github.com/Roblox/creator-docs/blob/main/content/en-us/scripting/sync.md)
- [[Live] Script RunContext – DevForum](https://devforum.roblox.com/t/live-script-runcontext/1938784)
- [Script RunContext vs LocalScript – DevForum](https://devforum.roblox.com/t/2507053)
- [roblox-core reference](https://skillsmp.com/creators/nonlooped/roblox-suite/roblox-core)

## R6

Yes, there's one problem: the file suffix. In Studio's Script Sync, `.client.luau` doesn't make a LocalScript.

According to the Script Sync docs, the suffixes map like this:

| File | Instance |
|---|---|
| `name.luau` | ModuleScript |
| `name.server.luau` | Script, RunContext = Server |
| `name.client.luau` | **Script, RunContext = Client** |
| `name.local.luau` | **LocalScript** |
| `name.legacy.luau` | Script, RunContext = Legacy |

This is different from Rojo's default, where `.client.luau` gives you a LocalScript. That's probably where the expectation comes from.

**Why it matters here:** A Script with RunContext = Client runs wherever the client can see it, not only in the usual LocalScript containers. StarterPlayerScripts replicates to the client, and its contents are also copied into each player's `PlayerScripts`. So your controller will likely run twice on each client: once from `StarterPlayerScripts.Client` and once from the copy in `PlayerScripts.Client`. That means duplicate connections, duplicate UI, and so on. The docs page doesn't spell out this double-run, but it's a known gotcha with Client-RunContext scripts in Starter containers. You can confirm it quickly with a `print` in a play test.

**Fix:** Rename the file to `client/Controller.local.luau`. It becomes a LocalScript, which only runs from `PlayerScripts`, so it runs once per player.

The rest of the setup is fine. A Folder named `Client` under StarterPlayerScripts is normal, and LocalScripts inside it run after it's copied to `PlayerScripts`. Keep in mind Script Sync is still a Studio beta (File → Beta Features → Script Sync), so check the suffix table again if it changes later.

Sources:
- [Script Sync – Roblox Creator Docs](https://create.roblox.com/docs/scripting/sync)
- [[Live] Script RunContext – DevForum](https://devforum.roblox.com/t/1938784)

## R7

**Position:** Yes, there's a problem. Studio turns `Controller.client.luau` into a `Script` with `RunContext = Client`, not a `LocalScript`. In `StarterPlayerScripts` that script runs twice per player. Use `Controller.local.luau` in that folder, or move the single client entry point to `ReplicatedStorage`. Confidence is medium-high.

**Reasoning**

*Confirmed from sources:*
- **Mapping:** The [Script Sync docs](https://create.roblox.com/docs/en-us/scripting/sync.md) map `name.client.luau` to a `Script` with `Client` RunContext. They map `name.local.luau` to a `LocalScript`, `name.luau` to a `ModuleScript`, and a directory to a `Folder`. So `.client.luau` is not a LocalScript here, and Rojo-style assumptions don't carry over.
- **What Studio creates:** A `Folder` named `Client` under `StarterPlayerScripts`, containing a `Script` named `Controller` with `RunContext = Client`. The folder-to-Folder and file-to-Script mappings are documented. That the sync root becomes a Folder named `Client` is my reading of the docs.
- **Double execution:** The [Script types and locations docs](https://create.roblox.com/docs/scripting/locations) say a `Client` Script can sit in `StarterPlayerScripts` or `StarterCharacterScripts`. They add that starter containers are copied to clients, so "the original script and the copy run, which isn't desirable."
- **DevForum:** The [RunContext announcement](https://devforum.roblox.com/t/live-script-runcontext/1938784) says the same thing. With Client or Server RunContext both the original and the copy run, so those containers should keep `Legacy` scripts or LocalScripts. Users report `print` firing twice.
- **Recommendation:** The docs recommend one `Script` with `Client` RunContext in `ReplicatedStorage`. They suggest LocalScripts in starter containers only where needed.

*Inferred:*
- The "original" is the instance under `StarterPlayer.StarterPlayerScripts`, and the copy is the one cloned into `Players.<Name>.PlayerScripts`. The docs say both run but don't spell out the mechanism. The forum reports match this.
- Because the folder is nested, the script is still a descendant of `StarterPlayerScripts`. It is still cloned and still runs twice.
- StarterPlayerScripts clones once per join, not per respawn. That is standard behavior, and the docs only say it runs "when the player joins."

**What to do instead** (any one of these)
1. **Keep the location:** rename the file to `Controller.local.luau`. That gives a `LocalScript`, which runs once per player from the cloned `PlayerScripts` copy. The `.legacy.luau` suffix also works.
2. **Follow the docs' recommendation:** sync `client/` to `ReplicatedStorage` (for example `ReplicatedStorage.Client`). Keep `Controller.client.luau` as the only `Client` Script. Put everything else in plain `.luau` ModuleScripts that it requires. This gives a stable location in Output and no cloning.
3. **Weakest option:** keep the `.client.luau` file in `StarterPlayerScripts` and add a guard so the copy exits unless it has a `Player` ancestor (`script:FindFirstAncestorOfClass("Player")`). The forum workaround only checks for the Player ancestor. I'd treat it as a fallback.

**Other layout notes**
- Script Sync ignores scripts that have attributes or tags, so don't rely on those for config.
- Script names must be valid file names on disk.
- Don't have several people syncing and editing the same script at once.
- If `client/` later needs a script with children, use `init.*.luau` rather than a same-named folder and file.

**Risks and unknowns**
- The double-run behavior comes from the 2022 announcement, current docs, and forum reports. I did not test it in Studio today. If Roblox has since changed how starter containers treat Client-context scripts, the problem would go away. The current docs still carry the warning.
- I couldn't fetch the older `/studio/script-sync` URL, which returned 404. The mapping comes from the `/scripting/sync` page.
- How the sync root's instance class and name are chosen depends on how the team sets up the sync in Studio. If they sync `client/` onto an existing Folder, my description holds. A different setup could change it.
- I'd change my mind if a Studio test shows only one execution.

**Position:** The setup is wrong. `Controller.client.luau` becomes a Client-RunContext Script, which runs twice per player in StarterPlayerScripts. Use `.local.luau`, or put it in ReplicatedStorage. Confidence is medium-high.

## R8

**Position:** The setup has one real problem. `Controller.client.luau` becomes a `Script` with `RunContext = Client`, not a `LocalScript`. Roblox's docs say a Client-context Script in `StarterPlayerScripts` runs twice. Rename it to `Controller.local.luau`, or move the synced folder out of the starter containers.

**Reasoning**

All of these were checked against the official docs, not recalled from memory.

- **File type:** The Script Sync page (create.roblox.com/docs/en-us/scripting/sync) maps `name.client.luau` to a `Script` with `Client` RunContext. It maps `name.local.luau` to a `LocalScript`, and `name.luau` to a `ModuleScript`. This is Script Sync's own table, so it shouldn't be assumed to match Rojo's conventions.
- **Folder type:** `name/` becomes a `Folder`. Only `Script`, `LocalScript`, `ModuleScript` and `Folder` instances sync.
- **Double run:** The Script locations page (create.roblox.com/docs/en-us/scripting/locations) covers Client-context Scripts. It says they "can also run in `StarterCharacterScripts` and `StarterPlayerScripts`. Starter containers are copied to clients, though, so the original script **and** the copy run, which isn't desirable." Its caption adds that the `Starter[]` containers "should use `LocalScripts`." So your controller would execute twice per player: once as the original under `StarterPlayer`, and once as the copy in `PlayerScripts`. This contradicts your "exactly once" intent.
- **RunContext semantics:** The RunContext enum page says `Client` "runs on the client no matter where it is placed." That is why the original is not inert the way a legacy Script is.

**Fixes**

1. Rename the file to `client/Controller.local.luau`. It becomes a `LocalScript`, and the starter container then behaves as usual. This is the smallest change and keeps your layout. I would pick it.
2. Alternatively, sync `client/` to a `Folder` in `ReplicatedStorage` or `ReplicatedFirst`, and keep the `.client.luau` name. The docs recommend a Client-context Script there. It runs once per client and is not cloned.

**Secondary points**

- **Set-up order:** Script Sync starts from an instance that already exists in Explorer. You choose "Sync to…" and pick a directory. So `StarterPlayerScripts.Client` should exist as a `Folder` first. I didn't find a documented "create target from disk" path. Only the Explorer-to-disk direction is documented.
- **Naming:** The instance name comes from the Studio instance, so a disk folder called `client/` and an instance called `Client` is fine.
- **Attributes and tags:** The docs say not to sync scripts that have attributes or tags, because they are ignored and can be lost.
- **Feature status:** The docs call it a beta feature, enabled in File > Beta Features. I have not re-checked whether that is still current as of 2026-10.
- **Team Create:** Avoid several people syncing the same scripts at once.

**Risks and unknowns:** The double-run claim rests on the Roblox docs wording. I did not run it in Studio. If the engine has since changed so the original no longer runs, the `.client.luau` setup would work, and the `.local.luau` rename would still be harmless. A quick test settles it. Put a `print` in the controller and count the lines in Play mode. I couldn't confirm whether the sync root must be a `Folder` or could be some other class.

**Confidence:** High that `.client.luau` becomes a Client-context `Script` and that the docs warn about double-running. Medium on the exact runtime behavior, since I haven't tested it.

Sources:
- https://create.roblox.com/docs/en-us/scripting/sync
- https://create.roblox.com/docs/en-us/scripting/locations
- https://create.roblox.com/docs/en-us/reference/engine/enums/RunContext

## R9

**Position:** The setup has a real bug. Under Script Sync, `Controller.client.luau` becomes a `Script` with `RunContext = Client`, not a `LocalScript`. In a Starter container a script like that runs twice on each client: once as the original in `StarterPlayerScripts` and once as the copy cloned into `PlayerScripts`. The fix is to rename it `Controller.local.luau`.

**Reasoning:**

1. **What the file becomes (checked against the source).** The official Script Sync naming table (create.roblox.com/docs/scripting/sync) maps:
   - `name.client.luau` to a `Script` with the `Client` RunContext
   - `name.local.luau` to a `LocalScript`
   - a plain directory to a `Folder`

   Rojo uses a different rule: it turns `.client.luau` into a `LocalScript`. The team is probably assuming the Rojo meaning, and it doesn't carry over to Script Sync.

2. **Why it runs twice (checked against the source).** The official DevForum announcement "[Live] Script RunContext" (devforum.roblox.com/t/1938784) has an FAQ on Starter containers. It says Starter containers "make a copy of any scripts contained in them," and that with the Client or Server RunContexts "both the original scripts and their copies will run." Its advice is to "continue to use the Legacy RunContext or LocalScripts in these containers."
   - The mechanism (from memory, but consistent with that FAQ): `StarterPlayer` replicates to every client, so a Client-RunContext script under `StarterPlayerScripts` runs there. The engine also clones the script into `Player.PlayerScripts`, and the clone runs too.
   - Result: two copies of the controller per client. That means duplicate connections, duplicate RemoteEvent handlers, double initialisation, and possibly two sets of UI.
   - It never runs on the server, because the Client RunContext doesn't. So the context is right and the count is wrong.

3. **Fixes, in order of preference:**
   - Rename the file to `client/Controller.local.luau`. It becomes a `LocalScript`, which runs only in the `PlayerScripts` copy, so once per player.
   - Alternatively, keep `.client.luau` but sync the folder somewhere that isn't cloned, such as `ReplicatedFirst` or `ReplicatedStorage`. A Client-RunContext script there runs once per client.
   - Don't use `.legacy.luau`. A Legacy `Script` doesn't run on the client at all, so the controller would run zero times.

4. **The sync target (partly checked).** The docs describe Script Sync as: select instances in the Explorer, then choose a directory on disk. So `StarterPlayerScripts.Client` has to exist (as a `Folder`) and be selected for syncing. The disk folder maps to a `Folder`, which is fine and doesn't cause anything to run. The docs also say:
   - Only `Script`, `LocalScript`, `ModuleScript` and `Folder` instances sync.
   - Scripts with attributes or tags are ignored and risk data loss.
   - Deleting a synced root on disk can cause a Studio error, so use **Stop Sync** first.

**Risks and unknowns:**
- My position rests on two documented facts: the naming table (`.client` becomes a Client-RunContext Script) and the RunContext FAQ (originals and clones both run in Starter containers). Both come from official Roblox sources I read today. The FAQ talks about "Starter containers" in general without naming `StarterPlayerScripts`, but a DevForum user report says Client scripts there run twice.
- Two things would change my mind: Script Sync changing its mapping (it's still beta), or the engine starting to skip originals in Starter containers. A quick test settles it: put `print(script:GetFullName())` in the controller and play solo. If it's broken you'll see two lines, one from `StarterPlayer.StarterPlayerScripts…` and one from `Players.<name>.PlayerScripts…`.
- I haven't checked how Script Sync behaves if the `Client` Folder is missing. That part comes from the UI flow described in the docs.

**Confidence:** High. Both facts my position depends on come from official Roblox sources and agree with each other.

Sources: [Script Sync docs](https://create.roblox.com/docs/scripting/sync), [[Live] Script RunContext](https://devforum.roblox.com/t/1938784), [LocalScript is running twice?](https://devforum.roblox.com/t/localscript-is-running-twice/1564369)

## R10

Yes, there's one real problem, and it breaks your "once per player" requirement: the controller will run twice per player.

**Why:** Script Sync's naming rules differ from Rojo's.

| File | What Studio creates |
|---|---|
| `name.luau` | ModuleScript |
| `name.server.luau` | Script, RunContext = Server |
| `name.client.luau` | **Script, RunContext = Client** (not a LocalScript) |
| `name.local.luau` | **LocalScript** |

So `Controller.client.luau` becomes a `Script` with `RunContext = Client`. StarterPlayerScripts copies its contents into each player's `PlayerScripts`. With a Client-RunContext Script, both the original in StarterPlayerScripts and the copy in PlayerScripts run. Roblox staff have confirmed this happens on purpose, and the usual advice is to use a LocalScript (or Legacy RunContext) inside Starter containers.

**Fix:** Rename the file to `client/Controller.local.luau`. Studio will then create a LocalScript, and only the copy in `PlayerScripts` runs.

The rest of the setup is fine:
- A LocalScript inside a `Client` Folder in StarterPlayerScripts still runs, because it doesn't have to be a direct child.
- StarterPlayerScripts copies its contents once, when the player joins, so it's the right place for a once-per-player controller. StarterCharacterScripts would run it again on every respawn.

Two caveats:
- The only places I found this mapping were the translated versions of the Script Sync docs page. The English page's table didn't come through in my search. After syncing, check the Explorer: you want the class icon to show **LocalScript**, not Script.
- Script Sync is still a Studio beta feature (File → Beta Features → Script Sync), so these conventions could change.

Sources:
- [Script Sync (Roblox docs)](https://create.roblox.com/docs/scripting/sync)
- [Script Sync, Spanish](https://create.roblox.com/docs/es-es/scripting/sync) / [French](https://create.roblox.com/docs/fr-fr/scripting/sync) / [Vietnamese](https://create.roblox.com/docs/vi-vn/scripting/sync)
- [[Live] Script RunContext (DevForum)](https://devforum.roblox.com/t/live-script-runcontext/1938784)
- [[Live] Script RunContext, page 5](https://devforum.roblox.com/t/live-script-runcontext/1938784?page=5)
- [Local script running twice (DevForum)](https://devforum.roblox.com/t/local-script-running-twice/2134741)

## R11

**Position:** Yes, the setup has a bug. Under Script Sync, `Controller.client.luau` becomes a `Script` with `RunContext = Client`, not a `LocalScript`. Inside StarterPlayerScripts that kind of script runs twice for each player. Rename the file to `Controller.local.luau` so it becomes a `LocalScript`, which runs once.

**Reasoning:**

Confirmed from sources:
- **The suffix decides the class.** The [Script Sync docs](https://create.roblox.com/docs/en-us/scripting/sync) map `.client.luau` to a Script with the Client RunContext and `.local.luau` to a LocalScript. Other mappings: `.server` gives a Server Script, `.legacy` a Legacy Script, a plain `.luau` a ModuleScript, and a directory a Folder. This is where Rojo habits mislead people: in Rojo, `.client.luau` means a LocalScript.
- **Client-context scripts run twice in Starter containers.** The [Script types and locations docs](https://create.roblox.com/docs/en-us/scripting/locations) say a Client-RunContext Script "can also run in StarterCharacterScripts and StarterPlayerScripts. Starter containers are copied to clients, though, so the original script and the copy run, which isn't desirable." Roblox staff said the same in the [RunContext announcement thread](https://devforum.roblox.com/t/1938784): both the original and the clone run, so keep LocalScripts or Legacy in Starter containers.
- **LocalScripts run once.** The same locations page says StarterPlayerScripts "Contains LocalScripts that run when the player joins." A LocalScript only runs from the per-player copy, so it runs once.

What Studio creates (inferred from the mapping, not checked in Studio):
- `StarterPlayer.StarterPlayerScripts.Client`, a Folder for the synced `client/` directory.
- `Controller` inside it, a Script with `RunContext = Client`. I'm assuming the suffix is stripped from the name, which the docs imply but I haven't verified.
- On each client it executes twice:
  1. The original at `StarterPlayer.StarterPlayerScripts.Client.Controller`, because StarterPlayer replicates to clients and Client-context scripts run wherever the client can see them.
  2. The clone at `Players.LocalPlayer.PlayerScripts.Client.Controller`, made when the player joins.
- It doesn't run on the server. It isn't re-cloned on respawn, because StarterPlayerScripts copies only once at join, so the count stays at two. The result is two controllers: input handlers bound twice, RemoteEvent listeners firing twice, duplicate UI, and so on.

What to do:
1. Rename the file to `client/Controller.local.luau` and keep syncing to `StarterPlayerScripts.Client`. The Folder wrapper is fine, since LocalScripts inside folders under PlayerScripts still run.
2. Alternatively, keep `.client.luau` but sync the folder somewhere that isn't cloned per player, such as ReplicatedFirst or ReplicatedStorage, where Client-context scripts run once per client. The LocalScript route is the more conventional one.
3. Don't use `.legacy.luau` here. A Legacy Script is a server-side script and won't act as a client controller.
4. Since this is a sync setup, also make sure the scripts carry no attributes or tags: the sync docs say such scripts are ignored, which can cause data loss.

**Risks and unknowns:**
- Script Sync is still a beta and has changed before. If Roblox remaps `.client.luau` to LocalScript (to match Rojo), or adds a special case so Client scripts don't run from inside StarterPlayer, the problem goes away. I checked the current docs, not a live Studio session.
- I haven't checked how the root Folder is named (`client` vs `Client`) or whether the suffix is stripped from instance names. Neither affects the main conclusion.
- Seeing `print(script:GetFullName())` output once per client from Studio playtesting would change my mind.

**Confidence:** High. Both the file-to-class mapping and the run-twice behaviour are stated directly in official Roblox docs and by staff. The exact instance names are inferred.
