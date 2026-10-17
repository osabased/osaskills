===== R1 =====
**What I think you want:** rename `GiveCoins` to `AwardCoins` in `ServerScriptService.Rewards`, and update every caller so nothing still calls the old name. I'm assuming this is a pure rename with no behavior change, and that `GiveCoins` shouldn't stay as an alias. Tell me if you want an alias kept for a while.

I couldn't call the MCP from here, so none of this has been run. The tool names come from the project's Studio-only guidance. I'd list the server's tools first and adjust if any name differs.

## Plan

**0. Setup and safety**
1. `list_roblox_studios`: find the window for place ID 1234567890 and use its `studio_id` for every later call. Two windows can share a name.
2. Ask you to save a version first (**File > Save to Roblox with Notes**). The place has no Git, and Team Create's Live Scripting pushes each edit to your two collaborators within seconds. That version is the only way back.
3. Ask you to tell your collaborators about the rename. Their open scripts could reintroduce the old name.
4. Make sure Studio is in Edit mode, not a play-test, because edits made during a play-test are discarded.

**1. Find the definition**
5. `search_game_tree` for `ServerScriptService.Rewards`, to confirm its path and class.
6. `script_read` on it. I'd check how `GiveCoins` is defined (`function Rewards.GiveCoins`, `Rewards:GiveCoins` or `Rewards.GiveCoins = ...`) and what else the module does with the name. That covers its own internal calls, exported type annotations and comments.

**2. Find every caller**
7. `script_grep` across the whole place for `GiveCoins`, case-sensitive, with no path filter. This is the caller list.
8. Look for references a plain name search can miss:
   - String or dynamic access, such as `Rewards["GiveCoins"]`, `require(...)[name]` or a table of handler names.
   - Aliases that copy the function, such as `local give = Rewards.GiveCoins`. The grep finds these, but I'd follow where the alias is used.
   - A RemoteEvent, RemoteFunction or BindableEvent that happens to be named `GiveCoins`. `search_game_tree` finds these, since grep reads only script source. They are separate from the function, so I'd leave them alone unless you say otherwise.
   - Attributes or tags holding the name, via `inspect_instance` on suspicious instances.
   - Other scripts that `require` Rewards under a different local name. I'd grep for `require(...Rewards)` to catch these.
9. Sort the hits into real callers, comments or strings, and unrelated matches such as a different module's `GiveCoins`. I'd show you that list before editing.

**3. Edit**
10. For each script, `script_read` just before the edit, because collaborators may have changed it. Then `multi_edit` with exact old and new strings, which fails if the text doesn't match.
11. Edit the definition in `Rewards` and every real caller, batched per script. I'd check each path before editing, since `multi_edit` creates a script if the path doesn't exist and a typo would add a stray one.
12. Leave unrelated matches and any separate Remote names alone.

**4. Confirm it worked**
1. **Static check:** `script_grep` for `GiveCoins` again. The expected result is zero hits, except any I deliberately left, which I'd list. Then `script_grep` for `AwardCoins` and compare the count with the definition plus caller list.
2. **Live source check:** `execute_luau` in Edit mode to read `Rewards.Source` and confirm Studio holds the new name. This also proves I'm editing the live place, not a stale copy.
3. **Runtime check:** `execute_luau` in Edit mode to check that `require(Rewards).AwardCoins` is a function and `GiveCoins` is `nil`.
4. **Play-test:** `start_stop_play`, then trigger the path that awards coins, such as a kill or pickup. I'd use `user_mouse_input` if it goes through UI, or whatever the game does naturally. Then `get_console_output` on the Server and Client. I'd look for "attempt to call a nil value" or an unknown-member error mentioning `GiveCoins`. I wouldn't `require` the game's modules from `execute_luau` during Play, since that creates a second copy with its own state. I'd stop only the session I started.
5. **Report:** I'd say exactly which of these ran. The place has no check command, linter or Script Analysis through the MCP, so the static type-check rung would be reported as not run. If a caller sits on a path I couldn't trigger, such as a rare event, I'd name it as untested instead of calling the rename verified.

**Rollback:** if something breaks and can't be fixed forward, restore the version you saved in step 2. Restoring creates a new version and doesn't publish it.

Do you want any of these handled differently: keep a temporary `GiveCoins` alias, include a same-named Remote in the rename, or skip the play-test?

===== R2 =====
**What I think you want:** rename `GiveCoins` to `AwardCoins` in the `Rewards` script in ServerScriptService, change every place that calls it, and leave the rest of the place working. This is a rename only, so I don't see any end-user behavior, look, or copy changing.

I can't call the Studio MCP tools from here, so this plan is what I'd run once you give me the go-ahead from a session that has them. I haven't checked the exact MCP tool names or their schemas. I'd confirm those from the tool list before the first call.

## Plan

**1. Tell the other two editors.** This is Team Create, so I'd ask them to hold edits to `Rewards` and any caller scripts until I finish. Otherwise a concurrent edit could overwrite the rename or leave a caller pointing at a name that no longer exists.

**2. Find every reference.** I'd search the whole DataModel, not just the obvious folders, for `GiveCoins`. That covers ServerScriptService, ServerStorage, ReplicatedStorage, StarterPlayer (StarterPlayerScripts and StarterCharacterScripts), StarterGui, Workspace, and ReplicatedFirst. I'd search for:
- `GiveCoins` as a plain identifier and as a method call (`:GiveCoins(`)
- string forms like `"GiveCoins"`, which could be a `:FindFirstChild` lookup, a remote name, or a table key
- `require` chains that reach `Rewards`, since those callers may use `.GiveCoins` on the returned table

I'd list each hit with its script path and line before editing anything.

**3. Read the current state.** I'd read `Rewards` in full and each caller, so I know the function's exact definition, its signature, and how it's exported. I'd also check whether `AwardCoins` already exists anywhere, so the rename can't collide with it.

**4. Edit `Rewards`.** I'd rename the function definition and its export to `AwardCoins`, keeping the signature and body the same. I wouldn't keep a `GiveCoins` alias unless you want one, since you asked for a rename.

**5. Edit each caller.** I'd update each call site to `AwardCoins`, changing only the identifier. If a caller passes the name as a string, I'd change that too only when it refers to this function, not to an unrelated remote or child with the same name.

**6. Confirm the rename worked:**
- Search the DataModel for `GiveCoins` again. The expected result is zero hits. Any remaining hit gets reviewed by hand.
- Search for `AwardCoins` and check the count matches the number of definition and call sites from step 2.
- Read `Rewards` and every edited script back and check for syntax problems and leftover references.
- Run a Play test through the MCP and trigger a coin award. Then check the Output window for `attempt to call nil` or other errors from the renamed call.

**7. Report back.** I'd list every file changed, the before and after names, anything I skipped or was unsure about, and the result of each check. Then I'd tell the other editors they can resume.

## Questions before I start

1. **Old name kept as an alias?** My recommendation is no. Keeping `GiveCoins` as a forwarding alias would make the rename safer for anything I miss, but it leaves the old name in the code.
2. **Are string references in scope?** My recommendation is yes, but only where they point to this function. Remotes or children that happen to share the name stay as they are.

Once you answer those and confirm the other editors are paused, I can start from step 1.

===== R3 =====
**What I think you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, and update every place that calls or references it, so nothing still uses the old name. I'm assuming no `GiveCoins` alias stays behind. Tell me if you want a temporary one for the other two editors' in-flight work.

I can't see the Studio MCP server's tool list from here, so I'm describing tools by capability. In the session I'd list the server's tools first and use whatever it calls its script-read, script-search, script-edit, Luau-execute, play-mode and console-output tools. I wouldn't guess names. I'd use a script-edit tool for the edits, not blanket `Source` rewrites. In Team Create, a targeted edit is less likely to overwrite a teammate's concurrent change.

**Plan**

1. **Read the definition.**
   - Read the source of `ServerScriptService.Rewards`.
   - Note how `GiveCoins` is defined: `function Rewards.GiveCoins`, `Rewards.GiveCoins = function`, a `:` method, or a local that is exported.
   - Note any internal calls inside the module.

2. **Find every reference across the whole DataModel, not just ServerScriptService.**
   - Run a text search for `GiveCoins` across all Script, LocalScript and ModuleScript sources in ServerScriptService, ServerStorage, ReplicatedStorage, StarterPlayer, StarterGui, StarterPack and Workspace.
   - Also search for instances named `GiveCoins`, such as a RemoteEvent, BindableFunction or attribute.
   - Look for indirect uses: string-indexed access like `Rewards["GiveCoins"]`, `GiveCoins` built from concatenated strings, and `pcall(Rewards.GiveCoins, ...)`.
   - Find the scripts that `require` Rewards, so I catch aliases like `local R = require(...)` and destructuring.

3. **Triage and report before editing.**
   - Sort the hits into real calls, definition, comments or strings, and same-named things unrelated to this function.
   - Anything ambiguous goes to you, such as a Remote named `GiveCoins` that shares a name but isn't this function.
   - Match whole words only, so something like `GiveCoinsToTeam` isn't touched.

4. **Check for concurrent edits.**
   - Because two others are editing, I'd re-read each script immediately before changing it.
   - I'd keep the original text of every changed line so I can restore it by hand, since the MCP server gives me no undo.

5. **Edit, with minimal diffs.**
   - Rename the definition in `Rewards`.
   - Update each caller's exact occurrence.
   - Do this in one quick pass so teammates don't see a half-renamed state for long.

6. **Verify.**
   - **Search again.** `GiveCoins` should return only the hits I deliberately left, and `AwardCoins` should return the definition plus the expected number of callers.
   - **Re-read.** Read back each edited script and compare it to the original to confirm only the name changed.
   - **Static check.** Pull script diagnostics or analysis for the edited scripts, if the server offers them, and look for "unknown member" warnings.
   - **Runtime check.** Start Play mode and read the console output for errors, such as `attempt to call a nil value`. I'd run a short Luau snippet in play mode that requires Rewards and asserts `type(Rewards.AwardCoins) == "function"` and `Rewards.GiveCoins == nil`. Then I'd exercise one real caller path, such as a coin pickup, if it can be triggered safely. Stop Play mode afterward.
   - **Confirm.** I'd report the exact before and after counts and the console result.

7. **Don't publish.** I'd leave the place unsaved and unpublished, and ask you before doing either. Team Create syncs edits live, so teammates will see the rename right away.

**Questions for you, recommended answer first:**
- Should I leave no alias, so any stale caller errors loudly? Or keep a temporary `GiveCoins = AwardCoins` alias?
- Is the play-mode check OK? It could touch DataStore-backed coins if the caller path saves data. If that's a risk, I'd limit it to the static checks plus the `type()` assertion.

===== R4 =====
**What I think you want:** rename `GiveCoins` to `AwardCoins` in `ServerScriptService.Rewards`, update every reference to it, and leave behavior unchanged, all in the live place through Studio MCP.

I haven't made any changes. Here is the plan I'd follow once the MCP server is reachable from my session.

## Plan

1. **Check the target.** Read `ServerScriptService.Rewards`. Confirm it's a ModuleScript (a plain `Script` can't be required, so callers would look different) and find the `GiveCoins` definition, including whether it's a field on a table, a `function Rewards.GiveCoins`, or a `Rewards:GiveCoins` method.

2. **Find every reference across the whole place.** Search all containers, not just ServerScriptService: ServerScriptService, ServerStorage, ReplicatedStorage, StarterPlayer, StarterPlayerScripts, StarterCharacterScripts, StarterGui, ReplicatedFirst, and Workspace. Search for:
   - `GiveCoins` as plain text (calls, method calls, and string references)
   - the `Rewards` module's require sites, so I can check each caller's use of the returned table
   - BindableEvent/BindableFunction/RemoteEvent/RemoteFunction names that might wrap it

   Build a list of file, line, and context before editing anything.

3. **Check for Team Create conflicts.** Two other people are editing this place. Before writing, I'd ask you to confirm that nobody is currently editing those scripts. Otherwise we risk overwriting each other.

4. **Edit the definition first, then the callers.** Rename the function in `Rewards` and update each caller to `AwardCoins`. I'd make each edit as a targeted replacement of the exact text, not a full-source rewrite, so the diff stays small and nothing else changes.

5. **Don't add an alias.** I'd leave out a `GiveCoins = AwardCoins` shim, since it hides missed callers. Keeping it would be a decision for you, though, so I'm flagging it rather than assuming.

6. **Use the Studio undo history if something goes wrong.** Each edit is recorded in Studio's ChangeHistory, so a bad rename can be reverted, though with two other editors in Team Create, undo may not be clean. Re-reading the source after each edit is how I'd catch mistakes early.

## Confirming it worked

- **Static check:** search the whole place again for `GiveCoins`. The only acceptable hits are none at all. Search for `AwardCoins` and confirm it matches the definition plus exactly the caller list from step 2, with no extras.
- **Read-back:** re-read each edited script and confirm the function name, the call sites, and the module's return table are consistent.
- **Runtime check:** run a play test and trigger the coin-awarding path. Check the Output window for "attempt to call nil" or "attempt to index nil" errors, and confirm coins are granted as before.
- **Caller coverage:** exercise each caller path from step 2, not just one. Any path I missed would show up here as a nil-call error.

## Questions for you

1. **Alias:** should I leave `GiveCoins` as a deprecated alias for other code outside this place, or remove it entirely? My recommendation is to remove it, since every caller is in this place.
2. **Team Create:** can you confirm that nobody is editing `Rewards` or its callers right now? If someone is, I'll wait for them to finish.
3. **Scope:** should I rename only the function, or also any variables and comments that say "GiveCoins"? My recommendation is to rename the function and its references, and leave unrelated names alone.

I'd confirm the exact MCP tool names from the server's tool list at the start of the session, since I can't see them from here.

===== R5 =====
**What I think you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, with no alias left behind, and update every reference so nothing still calls the old name. Tell me if you want a deprecated alias kept, or if a `GiveCoins` remote or bindable should be renamed too.

I can't call the Studio MCP from this session, so the tool names below are descriptions of what each step needs. I'll confirm the exact names against the server's tool list before running anything.

## Plan

1. **Check the target.** Read `Rewards` to see whether it's a Script or a ModuleScript and how `GiveCoins` is exported (a `function Rewards.GiveCoins` field, a local function, or a `return` table). The export shape determines which callers need changing.

2. **Find every reference.** Search the whole DataModel, not just ServerScriptService, for `GiveCoins`. Cover:
   - Direct calls: `Rewards.GiveCoins(`, `:GiveCoins(`
   - Destructured requires: `local GiveCoins = require(...).GiveCoins`
   - Strings: `"GiveCoins"` in remotes, bindables, attributes, or `:FindFirstChild` lookups
   - Other scripts that happen to define a same-named local, which must not be renamed

   Use a read-only search tool or an `execute_luau` scan that reads `.Source` on every script. Save the list of hits with file and line before editing.

3. **Check for collisions.** Confirm `AwardCoins` doesn't already exist in `Rewards` or in any module that gets renamed. In Team Create, ask the two other editors to avoid these scripts until the change is done, or check whether they have them open.

4. **Edit the definition.** Rename the function in `Rewards` and update any internal self-references.

5. **Edit each caller.** Use exact-match replacements on each reference from step 2. Skip any hit that turns out to be a different symbol. Keep comments and strings unchanged unless they name the function itself.

6. **Verify statically.** Re-run the whole-game search. It should return zero `GiveCoins` hits except intentional ones, and every `AwardCoins` hit should be one of the edits. Read each edited script once more to confirm it parses.

7. **Verify at runtime.** Start a play session on the server. Trigger a coin award path, check that the coin balance changes, and read the Output window for `attempt to call nil value` or `is not a valid member` errors. Stop the session and check the Output again.

8. **Save and report.** Save the place if the Team Create workflow needs it, and report the list of files and lines changed, plus anything I couldn't verify.

## Risks

- Editing a script that another person has open in Team Create can overwrite their in-progress work. Step 3 covers this.
- If `GiveCoins` is called from a client through a remote, the server-side rename will break that call. Step 2 catches it, but you should know it's a possibility.
- If nothing in the play test awards coins, the runtime check proves nothing. In that case I'd report that step as unverified rather than passed.

===== R6 =====
**What I think you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, and change every reference to it across the place so nothing still calls the old name. Nothing is edited until you approve.

I can't see the Studio MCP tools from this session, so the tool names below are placeholders. I'd confirm the real names with ToolSearch once the server is reachable.

## Plan

1. **Read the definition.** Use the MCP script-read tool to get `Rewards`' Source. Check whether it's a ModuleScript returning a table with a `GiveCoins` field, or a standalone function, and whether it's exported under other names too.

2. **Find every reference.** Run a Luau query through the MCP execute tool that walks `game:GetDescendants()` in ServerScriptService, ServerStorage, ReplicatedStorage, StarterPlayer, StarterPlayerScripts, StarterCharacterScripts, and Workspace. For each Script, LocalScript, and ModuleScript, it checks `Source` for the plain string `GiveCoins` and returns path, line number, and the matching line. Also check attributes and remote or bindable names, since a string like `"GiveCoins"` can be a caller too.

3. **Check for collisions.** Before editing, ask the two Team Create collaborators to avoid those scripts for the duration. Team Create edits go live for everyone immediately, so this matters.

4. **Show the diff, then edit.** Present the full list of hits and the exact before/after lines. After approval:
   - Rename the definition to `AwardCoins`.
   - Rewrite callers with whole-word matching only (for example `%f[%w_]GiveCoins%f[^%w_]`), so names like `GiveCoinsButton` are left alone.
   - Apply each change with the MCP script-write tool, one script at a time.

5. **Confirm it worked.**
   - Re-run the step 2 query. It should return zero `GiveCoins` hits, except any string you chose to keep.
   - Re-read each edited script and confirm the new name is there.
   - Start a playtest with the MCP playtest tool. Check that the output window has no errors from `Rewards` or its callers, then trigger a caller path (for example, a kill or a purchase) and confirm coins change as before.
   - Report the changed files with line numbers, plus any hits I left alone and why.

## Questions for you

1. **Keep a `GiveCoins` alias?** I recommend no. All callers are updated in this pass, so an alias just hides anything missed. Keeping one only helps if something outside the place calls it.
2. **Check with teammates first, or edit immediately?** I recommend asking them first, since Team Create changes are live for everyone.

===== R7 =====
**What I understand you want:** rename `GiveCoins` to `AwardCoins` in `ServerScriptService.Rewards` and update every caller, with no behavior change. I can't call the Studio MCP server from this session, so this is the plan I'd run once it's available. The tool names below are from memory of Roblox's Studio MCP. I'd check them against the live tool list first and substitute the real names if they differ.

**Questions before I start** (my recommendation first):
1. Should the rename be clean, with no `GiveCoins` alias left behind? Two teammates are editing in Team Create, so an alias would only help if one of them has unpublished code that still calls the old name. If you'd rather keep one, I'd add a one-line `GiveCoins = AwardCoins` alias and remove it later.
2. If a RemoteEvent, attribute, or DataStore key is also named `GiveCoins`, should I leave it alone? I'd leave it alone, because renaming those changes client or saved-data behavior, not just code.

**Plan**
1. **Check the target.** Use the instance-inspection or game-tree search tool to confirm `ServerScriptService.Rewards` exists and what class it is. Read its source with the script-read tool. Confirm that `GiveCoins` is defined once and see how it's exposed, for example `function Rewards.GiveCoins`, `Rewards:GiveCoins`, or a local function in a returned table.
2. **Find every reference.** Run the script-search or grep tool, or `execute_luau` over `game:GetDescendants()`, for `GiveCoins` in all `LuaSourceContainer`s. That covers ServerScriptService, ReplicatedStorage, StarterPlayerScripts, StarterGui, ServerStorage, Workspace and the rest. The search needs to catch:
   - direct calls (`Rewards.GiveCoins(...)`, `Rewards:GiveCoins(...)`)
   - aliases (`local give = Rewards.GiveCoins`)
   - string access (`Rewards["GiveCoins"]`, `:GetAttribute("GiveCoins")`)
   - pcall or task.spawn passing the function by reference
   - comments and docs
   
   I'd write the result as a list of script path, line, and match, and show it to you before editing anything.
3. **Classify each hit.** Sort the hits into real callers, string or Remote/attribute uses, and comments. I'd handle the string and Remote hits per your answer to question 2.
4. **Reduce edit conflicts.** Since two people share this place, I'd record each script's `Source` hash or length before editing. Immediately before each write I'd re-read the script and edit only if it's unchanged. If a teammate changed it, I'd re-read and re-apply.
5. **Edit.** Use the multi-edit or script-edit tool with exact-string replacements. Rename the definition first, then each caller, with one edit per script. I wouldn't use a blind global find-and-replace, so `GiveCoinsToTeam` and similar names stay untouched.
6. **Verify statically.** Re-run the step 2 search. Expected result: zero `GiveCoins` hits except any I deliberately left (Remote names and so on), and `AwardCoins` hits matching the definition plus the callers I counted. I'd also check that script-analysis or diagnostics tools report no new errors on the edited scripts.
7. **Verify at runtime.** Read the console output tool first to get a clean baseline. Then start a play session with the play-mode tool and trigger a real reward path, or call `require(Rewards).AwardCoins` from the play-mode script runner. Read the console and stop play. Passing means:
   - `AwardCoins` runs and the player's coins change as expected.
   - There are no "attempt to call a nil value" errors or `GiveCoins is not a valid member` warnings.
8. **Report.** I'd give you the list of scripts changed with before and after line counts, anything deliberately left unchanged, and what I couldn't verify. Callers in code paths I couldn't trigger would go in that last group.

**Limits:** Studio edits aren't in git and there's no Script Sync. I'd save the step 2 list and the original sources somewhere outside the place before editing. Studio's undo history or Team Create version history is then the only other way back.

===== R8 =====
**What I understand you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, and change every place that calls or references it, so nothing still uses the old name. I'm assuming Rewards is a ModuleScript and that this is only a rename with no behavior change.

**One question before I start (my recommendation first):**
- Should the rename be clean, with no `GiveCoins` alias left behind? I recommend clean, because it's the only way to prove no callers were missed. The alternative is to keep `Rewards.GiveCoins = Rewards.AwardCoins` temporarily. That's safer if your two collaborators have unpublished edits that still call the old name.

I haven't verified the exact tool names. I'm going from memory of Roblox's built-in Studio MCP server, and I'd check them against the tool list the server reports when I connect. By name, the tools are `list_roblox_studios`, `set_active_studio`, `search_game_tree`, `script_read`, `script_grep`, `multi_edit`, `execute_luau`, `get_console_output` and `start_stop_play`. If a name differs, I'd use the closest equivalent and tell you.

## Plan

1. **Connect to the right Studio.**
   - Use `list_roblox_studios`, then `set_active_studio` on the one with Sword Arena (place ID 1234567890). This matters if you have several Studio windows open.

2. **Read the target.**
   - Use `search_game_tree` to find `ServerScriptService.Rewards`, and `script_read` to read its full source.
   - Confirm that it's a ModuleScript and how `GiveCoins` is defined (`function Rewards.GiveCoins`, `Rewards.GiveCoins = function`, or a table field).
   - I'd save the original source in my notes, because there's no git or Rojo to restore from.

3. **Find every reference, not just direct calls.**
   - Run `script_grep` across the whole place for `GiveCoins`. This also catches uses that aren't direct calls: `["GiveCoins"]`, `:GiveCoins(`, local aliases like `local give = Rewards.GiveCoins`, destructuring, comments, and strings.
   - Also search the instance tree (`search_game_tree` or `execute_luau` over `game:GetDescendants()`) for non-script uses: RemoteEvents, BindableFunctions or Attributes named `GiveCoins`. A RemoteEvent with that name is a separate API, so I'd list it for you rather than rename it.
   - Sort the hits into definition, direct callers, indirect references (aliases and string lookups) and unrelated matches.
   - Show you the list before editing.

4. **Check for Team Create conflicts.**
   - Re-read each script that will change immediately before editing it, so I don't overwrite a collaborator's edit made since step 2.
   - Use `multi_edit` for each script, with exact-match replacements that only touch real references. Do the definition and all callers in one batch, so the game isn't left half-renamed for the other two editors.
   - Leave unrelated matches alone, such as a different module's own `GiveCoins`.

5. **Verify it worked.**
   - **Static check:** rerun the `script_grep` for `GiveCoins`. The expected result is zero hits, apart from anything I deliberately left, which I'd report. Run another for `AwardCoins`, and confirm the hit count equals the definition plus the callers I edited.
   - **Syntax and load check:** use `execute_luau` to `require` the Rewards module and assert that `type(m.AwardCoins) == "function"` and `m.GiveCoins == nil`. I'd also load each edited script with `loadstring` or a source check to catch typos.
   - **Runtime check:** run `get_console_output` before and after a `start_stop_play` playtest. Trigger a coin award through the normal path if one is easy to reach, and look for "attempt to call a nil value" or "GiveCoins is not a valid member" errors. I can only test paths the playtest actually reaches, so I'd flag callers I couldn't exercise.

6. **Report back.**
   - List every script and line changed, the verification results, and anything skipped or uncertain. Examples are string-built lookups, remotes with the same name, and callers that only run in specific game states.
   - Tell you to publish or save so the other two editors get the change, and to warn them. I wouldn't publish on my own.

**Limits:**
- There's no source control, so the rollback is the original text I saved in step 2 plus Studio's version history.
- If another editor adds a new `GiveCoins` call after my final grep, the rename will miss it. Once the change is published, it's worth asking them to use `AwardCoins`.

===== R9 =====
**What I understand you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, and change every call site so nothing still references the old name. Nothing else should change.

I can't call the MCP server from here, so I haven't checked the tool names below. I'm going from memory of Roblox's Studio MCP, and step 0 is to confirm them against what the server actually lists.

**Questions for you first** (my recommendation is first in each):
1. Should I rename outright with no `GiveCoins` alias? An alias would hide missed callers, and the other two editors may have unpushed code that still uses the old name. The alternative is a temporary `Rewards.GiveCoins = Rewards.AwardCoins` shim.
2. Can I message the other two Team Create editors before I start? Edits to scripts they have open can conflict or get overwritten.

**Plan**

0. **Discover tools.** List the server's tools and use their real names and schemas. I expect roughly: search the DataModel tree, read a script, grep scripts, edit a script, run Luau in the edit DataModel, read the console, and start or stop playtest. I would not use a Bash or PowerShell workaround, because the code exists only in Studio.
1. **Read `ServerScriptService.Rewards`** with the script-read tool. Note how `GiveCoins` is defined: `function Rewards.GiveCoins`, `Rewards:GiveCoins`, a local function that is then exported, or a table field. Also check whether it is a ModuleScript and who requires it.
2. **Find every reference.** Run a script-grep across the whole place for `GiveCoins`, case-insensitive and plain-text, not only `Rewards.GiveCoins`. Cover:
   - `Rewards.GiveCoins(` and `Rewards:GiveCoins(`
   - destructured or aliased uses (`local give = Rewards.GiveCoins`)
   - string lookups (`Rewards["GiveCoins"]`, `require(...)[name]`)
   - RemoteEvent, BindableEvent or attribute names that contain the string
   - comments and docs
3. **Check non-script references.** Use the tree-search tool, or a read-only `execute_luau` that loops over `game:GetDescendants()`. Look for Instances named `GiveCoins` and attributes or string values that mention it. I need this because the grep only sees script source.
4. **Report the hit list to you** (script path, line, and the kind of use). I'd flag any dynamic or string-based hit, because those need a judgment call rather than a mechanical rename.
5. **Edit.** Use the script-edit tool with exact-string replacements, one script at a time:
   - Rename the definition in `Rewards`.
   - Update each caller.
   - Leave a name alone if it is a remote or an Instance that is not this function, and ask you about it.
   - Avoid whole-script rewrites, so I don't clobber the other editors' changes.
6. **Verify.**
   - Re-run the same grep for `GiveCoins`. The expected result is zero hits, or only hits you have approved.
   - Grep `AwardCoins` and check the count equals the definition plus the callers.
   - Use `execute_luau` to `require` the `Rewards` module and assert that `AwardCoins` is a function and `GiveCoins` is nil.
   - Start a playtest, trigger a coin award, and read the console. It should show no "attempt to call a nil value" or "GiveCoins is not a valid member" errors, and coins should actually increase. Then stop the playtest.
7. **Report** the files changed, the before and after grep counts, the playtest result, and anything I skipped. Studio has no git here, so the report is the only change record. Team Create's version history is the rollback path.

**Not covered:** I can't check scripts the other editors haven't published yet, or callers in other places that use this module.

I wouldn't spawn subagents for this. It's a small sequential task, so I'd do it in the main session.

===== R10 =====
**What I think you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, change every reference to it so nothing still uses the old name, and confirm the game still awards coins. I haven't edited anything.

I can't call the Studio MCP server from this session, so I haven't checked its tool names or the place's contents. The plan below uses the tool roles I'd expect, and I'd confirm the exact names against the live tool list before the first call.

## Plan

**1. Read the definition.** Open `ServerScriptService.Rewards` and check how `GiveCoins` is exposed: a local function, a field on a returned module table (`Rewards.GiveCoins`), or a remote/bindable wrapper. The rename changes only what the definition is called. If it's a module field, the key itself changes too.

**2. Find every reference.** Search the whole place, not just the scripts I expect:
- All `Script`, `LocalScript`, and `ModuleScript` instances in `ServerScriptService`, `ServerStorage`, `ReplicatedStorage`, `StarterPlayer`, `StarterGui`, `StarterPack`, and `Workspace`. Sword tools often carry their own scripts, so check inside them too.
- Direct calls, `require` chains, and string or dynamic access such as `Rewards["GiveCoins"]`, `:FindFirstChild("GiveCoins")`, or remote and bindable names.

The likely tools are a game-tree search, a children or properties read, and a script-source read for each match. I'd then record a list of `script path → line → snippet`.

**3. Check for collisions and coordinate.** Search for `AwardCoins` to make sure it isn't already used. Because this is a Team Create place with two other editors, I'd ask them to avoid those scripts until the rename is done, since a concurrent edit to the same script could overwrite mine.

**4. Edit.** For each script, use the script-source edit tool to replace the old name with `AwardCoins` in the definition and every call site. I'd make no other changes and add no comments. I'd not keep a `GiveCoins` alias unless you want one, since you asked to update every caller. I'd do this while the place is not in Play mode.

**5. Verify.**
- Search for `GiveCoins` across the place. It should return zero matches. Any remaining match is a bug or a string I still need to handle.
- Search for `AwardCoins`. The results should match the list from step 2, one for one.
- Check each edited script for syntax errors using the Studio console or script analysis.
- Start a play session, trigger a path that awards coins (such as a kill or a pickup), and read the console output. Expect no `attempt to call a nil value` or missing-member errors, and confirm the coin total in leaderstats goes up. If play mode touches DataStores, use a test session.

**6. Report.** List each file changed, the before-and-after line for each edit, anything I couldn't check (such as dynamic lookups or places outside Studio), and the verification results.

## Questions before I start

1. **Alias:** Should I leave a `GiveCoins` alias that forwards to `AwardCoins`, or remove the old name completely? My recommendation is to remove it completely, since you asked to update every caller.
2. **Teammates:** Should I ask the other two editors to pause on those scripts, or will you tell them? My recommendation is that you tell them, since I can't message them from here.
3. **Play test:** Is a play-session test acceptable for verification? My recommendation is yes, as long as it doesn't write to live DataStores.

===== R11 =====
**What I understand you want:** rename `GiveCoins` to `AwardCoins` in `ServerScriptService.Rewards`, update every caller, and confirm that nothing still references the old name. No alias or compatibility shim is planned unless you want one.

**Caveat on tool names:** I can't see the MCP tool list from here. The names below are the ones I expect from Roblox's Studio MCP server, and I'd check them against the real list before the first call.

## Plan

1. **Confirm the tools.** List the server's tools and map each step below to the real name. I expect something like a Luau runner (`execute_luau`), a script reader, a script editor (`multi_edit` or `set_script_source`), a tree search, a console reader, and play-mode control.

2. **Read `Rewards`.** Read its full source. Check whether it is a ModuleScript and how `GiveCoins` is defined: `function Rewards.GiveCoins`, `Rewards:GiveCoins`, a local function that gets exported, or a table field.

3. **Find every reference, read-only.** Run Luau through the MCP that walks `game` and scans `.Source` for scripts. This covers ServerScriptService, ReplicatedStorage, StarterPlayer, StarterGui, ServerStorage and Workspace. It searches for the literal `GiveCoins` and reports the script's full path, line number and line text. It is read-only.
   - The search is deliberately broad, not just `Rewards.GiveCoins(`. It also catches destructured imports (`local GiveCoins = Rewards.GiveCoins`), string lookups (`Rewards["GiveCoins"]`), RemoteEvent or BindableEvent names, attributes, and comments.
   - I'd also search for `require(...Rewards)` so I know which scripts use the module even if they alias it.

4. **Triage the hits.** Sort them into (a) the definition, (b) real callers, and (c) lookalikes, such as an unrelated `GiveCoins` on another module or a remote with that name. I'd only rename (a) and (b). If any hit is a remote or string key that crosses the client/server boundary, I'd stop and show you before touching it.

5. **Check for collisions and live editors.** Confirm `AwardCoins` doesn't already exist in `Rewards`. Team Create has two other editors, so I'd re-read each target script immediately before editing it. If a script's source differs from what step 3 saw, I'd stop for that script.

6. **Edit.** Change the definition first, then each caller. These are minimal exact-string edits, one script per call, with no whole-source rewrites, so concurrent edits by others are less likely to be clobbered.

7. **Verify.**
   - **Static:** rerun the step 3 scan. Expect zero `GiveCoins` hits except the lookalikes I deliberately left, and the expected `AwardCoins` count (the definition plus every caller).
   - **Per-script:** re-read each edited script and check that only the intended lines changed.
   - **Runtime:** start a play session. Run Luau in play mode that requires `Rewards` and asserts `type(Rewards.AwardCoins) == "function"` and `Rewards.GiveCoins == nil`. Trigger one real caller path if there's an easy one, such as a kill or pickup. Then read the console output and look for "attempt to call a nil value" or "is not a valid member" errors. Stop the play session afterwards.

8. **Report.** List each script changed, the before and after count of references, the play-test result, and anything I left alone and why.

## Questions

1. Should the old `GiveCoins` name be removed completely (my recommendation, since you asked for a rename and the scan catches the callers), or kept briefly as a deprecated alias so a teammate's unsaved or in-progress script doesn't break?
2. Are any of the others currently editing scripts that call it? If so, a heads-up before I edit is probably worth it.

===== R12 =====
**What I think you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, and change every reference so nothing still calls the old name. I'll treat this as a pure rename with no alias left behind and no behavior change.

I can't reach the Studio MCP server from this session, so the tool names below are the operations I'd need. I'll confirm the exact names against the server's tool list when I can call it.

## Plan

1. **Locate the definition.** Read `ServerScriptService.Rewards` and check how `GiveCoins` is defined: a local function, a field on a returned module table (`Rewards.GiveCoins`), or a method (`function Rewards:GiveCoins`). The definition and the call syntax depend on this.

2. **Find every reference across the whole DataModel.** Search the source of all Scripts, LocalScripts and ModuleScripts, not only the Rewards script. Look in ServerScriptService, ServerStorage, ReplicatedStorage, StarterPlayer, StarterPlayerScripts, StarterGui, and Workspace. Match these forms:
   - `GiveCoins(`
   - `.GiveCoins` and `:GiveCoins(`, including through a `require` result stored in a local
   - the bare name in comments or strings

   Record each hit as script path, line, and context. Hits in strings or remote names need a decision: a RemoteEvent named `"GiveCoins"` is a network contract, not the function, so I would leave it alone and tell you.

3. **Coordinate before editing.** This place is Team Create with two other editors, so changes go live for them immediately. Before I edit, I'd ask you to tell the two of them I'm touching these scripts, or to confirm they aren't editing them now.

4. **Edit the definition, then each caller.** Re-read each script's source immediately before changing it, so I don't overwrite a teammate's newer edit. Use targeted find-and-replace on the specific lines, not a whole-source rewrite. Don't add a `GiveCoins = AwardCoins` alias, since that would leave the old name in use.

5. **Update comments only where they name the function.** Don't add a comment about the rename.

## How I'd confirm it worked

- **Search again:** a search of every script for `GiveCoins` should return zero hits, except any string or remote name you chose to keep. A search for `AwardCoins` should return the definition plus the same call sites found in step 2.
- **Read back:** re-read each edited script and check the syntax by eye. If the Studio tooling offers script analysis or diagnostics, run it too.
- **Playtest:** start a Play session, trigger a path that awards coins, and check the Output window for `attempt to call nil` or similar errors and confirm the coin balance changes.
- **Report:** list every file I changed, the hits I left alone, and the playtest result. I won't publish the place without your confirmation.

## Decisions for you

- Should a string or RemoteEvent named `"GiveCoins"` be renamed too, or kept as a network contract? I'd keep it.
- Should I coordinate with your two teammates first, or do you want me to go ahead and check for conflicts as I edit?

===== R13 =====
**What I think you want:** rename `GiveCoins` to `AwardCoins` in `ServerScriptService.Rewards`, with no behavior change, and update every reference so nothing still calls the old name.

I can't call the Studio MCP server from this session, so I haven't checked its exact tool names. Each step below names the kind of tool I'd use. I'd confirm the real names against the connected server's tool list before running anything.

## Plan

**1. Read the definition.** Open `ServerScriptService.Rewards` in full. Note whether it's a `Script` or a `ModuleScript`, and how `GiveCoins` is defined: `local function`, `function M.GiveCoins`, `function M:GiveCoins`, or a table field. The definition form determines what the callers look like.

**2. Find every reference.** Search the whole DataModel for `GiveCoins`, not just the usual service folders. Cover:
- `Rewards.GiveCoins(` and `Rewards:GiveCoins(`, in any script type
- `require` aliases, where the module is stored in a local under a different name
- string references such as `"GiveCoins"` in Remotes, BindableFunctions, Attributes, or name lookups
- `ServerStorage`, `Workspace`, `StarterPlayer`, and `ReplicatedStorage`, not just `ServerScriptService`

Record the full list of file paths and line numbers before editing. This is the checklist for step 5 and the rollback reference.

**3. Check for concurrent edits.** Team Create means two other people may have unsaved edits in these scripts. Before writing, confirm with them that none of the affected scripts are being edited. Otherwise an edit from me could overwrite their work.

**4. Rename the definition.** Change only the identifier. Keep the signature, body, and return values the same. Update a comment only if it names the function.

**5. Update each caller.** Edit each file from the step 2 list, changing only the identifier, and re-read each edited region afterward to confirm it. Keep method-call vs. dot-call syntax intact, since `:` passes `self` and `.` doesn't.

**6. Verify.**
- Search the DataModel for `GiveCoins`. It should return zero hits.
- Search for `AwardCoins`. It should match exactly the list from step 2, plus the definition.
- Run a short Luau check in Studio: `require` the module (if it's a ModuleScript), confirm `typeof(Rewards.AwardCoins) == "function"` and `Rewards.GiveCoins == nil`.
- Play-test once and trigger a reward path. Confirm the coin balance changes and the output log has no errors about nil or missing functions.

**7. Report.** List each changed script with its path, the lines changed, and the verification results. If anything from the step 2 list was skipped, say so.

## Decisions for you

1. **Keep a `GiveCoins` alias that forwards to `AwardCoins`?** I'd recommend **no**. We're updating every caller in one pass, so an alias only hides a missed caller. Say yes if something outside this place depends on the old name.
2. **Proceed now or coordinate with the two editors first?** I'd recommend **coordinate first**, because of the overwrite risk in step 3. Tell me when it's clear and I'll start.

===== R14 =====
**What I think you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, and change every reference to it in the place so nothing still calls the old name. Nothing is edited yet.

I can't confirm the exact Studio MCP tool names from this session because they aren't loaded here. The names below are what I'd expect, and I'd check them against the connected server's tool list before the first call.

## Plan

**0. Coordinate with the two other editors.** Team Create has no lock, so ask them to avoid editing `Rewards` and its callers until the rename is done, and to confirm they have no unsaved script changes.

**1. Confirm what `Rewards` is.** Read its source and class (Script or ModuleScript). This decides whether `GiveCoins` is a module export (`Rewards.GiveCoins`) or a local function, and that changes which callers to look for.

**2. Inventory every reference.** Search the whole DataModel for `GiveCoins` as text, in all script sources. Cover:
- `ServerScriptService`, `ServerStorage`, `ReplicatedStorage`, `StarterPlayer`, `StarterGui`, `Workspace`, `ReplicatedFirst`, and any Tool or Part containing scripts.
- String references too: RemoteEvent/BindableEvent names, attributes, and `Rewards[name]` lookups, which a plain name search can miss.

Record the results as a table of script path, line, and snippet, and keep a copy of each original source for rollback.

**3. Edit the definition first.** Use a targeted find-and-replace on the exact old text, not a full-source overwrite. A full overwrite could wipe a teammate's concurrent edit. Each replacement must match exactly once.

**4. Edit each caller** the same way, using the table from step 2.

**5. Decide on a backward-compatible alias.** My recommendation is no alias, so a later search for `GiveCoins` comes back clean. This is a code decision, not end-user behavior, so I'll follow it unless you want a temporary alias.

**6. Verify.**
- Re-search the place for `GiveCoins`. Expect zero hits, apart from anything intentionally left and listed.
- Search for `AwardCoins`. Expect the definition plus every caller from step 2.
- Re-read each edited script to check the syntax and that it reads cleanly. Check the Studio script analysis or error output for new errors.
- Run an edit-mode check that `Rewards.AwardCoins` is a function and `Rewards.GiveCoins` is nil, if `Rewards` is a ModuleScript. Confirm this doesn't have side effects first.
- Play-test the coin-award path. Read the console output for errors, and confirm the coin total changes as expected.

**7. Report back** with the list of changed scripts and line numbers, the verification results, and anything I couldn't check. Ask your teammates to confirm their Studio sees the new names.

## Risks and open items
- Callers in other places in the same universe, or in server-side data that stores the function name, won't appear in this place's search. Tell me if any exist.
- Studio MCP edits can't be rolled back atomically. If something breaks partway, I'd restore from the step 2 copies.
- Publishing the place is outward-facing, so I won't publish without your explicit go-ahead.

**Questions before I start:**
1. Is `Rewards` a Script or a ModuleScript? (I can find this in step 1 if you'd rather I check.)
2. Do you want no alias for `GiveCoins`? I recommend none.
3. Should I wait for your teammates to confirm they've paused, or proceed once you've told them?

===== R15 =====
**What I think you want:** rename the `GiveCoins` function in `ServerScriptService.Rewards` to `AwardCoins`, and update every place that calls or references it. You want no leftover references and no behavior change.

**Questions (my recommendation first):**
1. Should I remove `GiveCoins` outright, or leave a temporary `GiveCoins = AwardCoins` alias? I recommend removing it, so nothing stale remains. The catch is that a teammate's unsaved or unseen caller would then break.
2. Are your two teammates editing scripts right now? I recommend you tell them first, because Team Create edits merge live and I can't see their open work.

**Caveat on tool names:** I can't call the MCP server from here, so these names come from memory of Roblox's Studio MCP. Step 0 confirms them.

**Plan**

0. **Confirm the tools.** List the server's available tools. I expect script reading, grep and search, multi-edit, `execute_luau`, play-mode control and console output. If a name differs, I'd use the closest equivalent.
1. **Read the module.** Use the script-read tool on `ServerScriptService.Rewards`. This confirms it's a ModuleScript and shows how `GiveCoins` is defined (`function Rewards.GiveCoins`, `Rewards:GiveCoins`, or a table field). It also shows whether the module calls itself internally.
2. **Find every reference.** Run script grep across the whole place, including ServerStorage, ReplicatedStorage, StarterPlayer, StarterGui and Workspace. I'd search for `GiveCoins` as a plain string, not just `.GiveCoins(`. Then I'd run a second search with `execute_luau` that walks every `LuaSourceContainer` and records the script path, line number and line text. That covers anything the grep misses. The string search also catches:
   - `Rewards["GiveCoins"]`
   - `:FindFirstChild("GiveCoins")`
   - RemoteEvent, BindableEvent or attribute names containing `GiveCoins`
   - comments and docs
3. **Classify the hits.**
   - Real callers of the Rewards function.
   - Unrelated same-named things, such as a different module's `GiveCoins` or a RemoteEvent name. I'd list these and leave them alone unless you say otherwise.
   - Callers that import the module under another variable name, found by checking which scripts `require` Rewards.
4. **Show you the hit list** with paths and lines before editing, since this touches shared code.
5. **Save a rollback point.** There's no git or file copy for this place. I'd print the original source of each affected script into the chat, and you'd publish or save a Studio version-history point.
6. **Edit.**
   - Use the multi-edit tool with exact-string replacements per script, starting with the definition in Rewards and then each caller.
   - Replace only whole-word matches of the Rewards function. Don't do a blind global replace.
   - Re-read each script right before editing it, in case a teammate changed it.
7. **Verify statically.**
   - Re-run the grep and the `execute_luau` scan. `GiveCoins` should have zero hits, apart from any unrelated ones I left on purpose.
   - Grep for `AwardCoins` and check that the count equals the definition plus all callers.
   - Re-read each edited script to check the syntax is intact.
8. **Verify at runtime.**
   - Start a play session, then read the console output.
   - Look for errors such as `attempt to call a nil value` or `GiveCoins is not a valid member`.
   - Trigger a coin award through the normal path, either by playing it or by calling `require(Rewards).AwardCoins(...)` from `execute_luau` in play mode. Check that the player's coin value changes.
   - Stop the session.
9. **Report back.** I'd list the files and lines changed, the unrelated `GiveCoins` hits I skipped, the verification results, and anything I couldn't check. For example, a caller that only runs in some game state would need a manual test.

**What would count as done:** zero remaining references to the old name, a clean console during a play test, and a coin award that works.

===== R16 =====
**What I think you want:** rename `GiveCoins` to `AwardCoins` in the `Rewards` module under `ServerScriptService`, and update every caller in the place. The old name should be gone afterward, and behavior should be unchanged.

**Caveat on tool names:** I can't see the MCP server's tool list from here, so the names below are the ones I expect. Step 1 is to list the real tools and map each step onto them. If the server has no script-search tool, I'd do the search in step 2 by running Luau through its generic code-execution tool.

**Questions for you (my recommendation first):**
1. Should I remove `GiveCoins` outright, or leave a temporary `GiveCoins = AwardCoins` alias? I recommend removing it, since the search in step 2 should find every caller. The catch is that your two collaborators may have callers I can't see yet. If you're unsure, keep the alias for now and I'll remove it in a follow-up.
2. Have the other two editors been told, and should I wait for them to publish or save? I recommend a heads-up first, because Team Create merges script edits and a concurrent edit to the same script could conflict.

**Plan**

1. **Discover tools and check state.** Run the server's tool listing. Then read the Studio mode and confirm it's edit mode, not Play, and that the open place is Sword Arena (1234567890).
2. **Find everything that references the name.**
   - Use script search or grep for `GiveCoins` across every script container: `ServerScriptService`, `ServerStorage`, `ReplicatedStorage`, `StarterPlayerScripts`, `StarterGui`, `StarterPack`, `Workspace`, and `ReplicatedFirst`.
   - Search for the module path (`require(...Rewards)`) so I find callers that alias the module and call it under a different local name.
   - Search for string-based uses: `["GiveCoins"]`, `:FindFirstChild("GiveCoins")`, `GetAttribute`, and `RemoteEvent`/`BindableFunction` instances named `GiveCoins`. These are the usual way a plain rename breaks something.
   - Search for `AwardCoins` too, to make sure the new name doesn't already exist or collide.
3. **Read and record.** Read the full source of `Rewards` and each caller. Save the list of script paths and line numbers, plus the original text of each line I'll change, so I can revert by hand. There's no git or Script Sync, so this record is the only undo besides Studio's own history.
4. **Decide on any instances named `GiveCoins`.** If a RemoteEvent or similar is named `GiveCoins`, I'd stop and ask you before renaming it. That's a wire-level change and would also touch client code.
5. **Edit the definition.** In `Rewards`, change the definition (`function Rewards.GiveCoins(...)` or `Rewards.GiveCoins = function`) and any internal self-references to `AwardCoins`. I'd use a precise line-range or multi-edit tool, not a whole-script overwrite, so a collaborator's concurrent edits elsewhere in the script aren't clobbered.
6. **Edit each caller.** Apply the same targeted edit, one script at a time. Only change real references to this module's function. I'd skip any unrelated `GiveCoins` in comments, in other modules, or in other tables.
7. **Verify statically.**
   - Re-run the step 2 searches. `GiveCoins` should return zero hits, or exactly the alias line if you chose to keep one.
   - Search for `AwardCoins` and check that the hit count equals the definition plus the callers I changed.
   - Read back each edited script and compare it against the saved originals. The only differences should be the renamed identifier.
   - Check script editor diagnostics, if the server exposes them, for new "unknown member" warnings.
8. **Verify at runtime.**
   - Read the console output first so I can tell which errors are new.
   - Start a Play session and trigger a coin award by running the actual code path, such as the in-game action that grants coins. Alternatively, run a small Luau snippet in play mode that requires `Rewards` and calls `AwardCoins`.
   - Read the console output again. I'm looking for no `attempt to call a nil value` or `GiveCoins is not a valid member` errors, and for the coin total to change as before.
   - Stop the Play session so Studio is back in edit mode.
9. **Report.** I'd give you the list of scripts changed with line numbers, the before and after search counts, the runtime result, and anything I couldn't check. For example, a caller that only runs on a rarely hit path would be flagged as unexercised, not called verified.

I wouldn't publish or save to Roblox, since that's outward-facing and affects your collaborators. I'd leave that to you.
