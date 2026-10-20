# live-scripting

Question asked:

> Our Roblox place is in Team Create with two other people editing, and we haven't touched the collaborative editing settings. I'm going to have Claude rename a function across several scripts through the Studio MCP. Will my collaborators see those script edits right away, or only after I commit them?

## R1

**It depends on which script-editing mode the place is in, and leaving the settings alone doesn't tell you which one that is.**

Team Create has two modes:

- **Drafts mode** (the older "Collaborative Editing"): Your script edits stay as private drafts on your machine. Collaborators only see them after you **commit**. Until then they keep seeing the server version, and Team Test runs that version too. Play Solo uses your drafts.
- **Live Scripting**: Edits sync to everyone in real time, a bit like Google Docs, and there's nothing to commit. Roblox's beta announcement said Live Scripting would become the default for Team Create. I couldn't find an official source confirming that it's the default now, so a place you never configured could be in either mode.

**How to check before running the rename:**
- Open the **Drafts** window (View tab → Drafts). If you edit a script and it shows up there as an uncommitted draft, you're in Drafts mode.
- Or select **Workspace** and look in the Properties panel under Scripting. If the Live Scripting property (`EditorLiveScript`) is on, you're in live mode.

**Why it matters for this rename:**
- **Live mode:** Your collaborators will see each script change as the MCP makes it. The rename touches several scripts one after another, so for a moment some scripts will call the new name while others still use the old one. Anyone who playtests during that window could hit errors. Warn them first or pick a quiet time.
- **Drafts mode:** Nobody sees anything until you commit, so commit all the edited scripts together. Committing only some of them leaves the shared version with mismatched names. Also, if a collaborator commits a change to one of those scripts in the meantime, you'll have to merge it. I'm also not sure whether edits made through the MCP (a plugin changing script source) become drafts the way manual typing does. Do a test edit on one script and check that it appears in the Drafts window before running the whole rename.

The DevForum also has recent reports of drafts failing to commit or getting stuck. If you're in Drafts mode, check that the commit actually goes through before you close Studio.

Sources:
- [Live Scripting Beta – Roblox DevForum](https://devforum.roblox.com/t/live-scripting-beta/2640607)
- [Live Scripting Beta (page 5) – Roblox DevForum](https://devforum.roblox.com/t/live-scripting-beta/2640607?page=5)
- [Roblox Studio Team Create guide – obby.fun](https://www.obby.fun/blog/roblox-studio-team-create)
- [Disabling Team Create Wipes "uncommitted" scripts – DevForum](https://devforum.roblox.com/t/disabling-team-create-wipes-uncommitted-scripts/3801771)
- [drafts-versioning-script-history-bug tag – DevForum](https://devforum.roblox.com/tag/drafts-versioning-script-history-bug)
- [Team Create – Roblox Wiki](https://roblox.fandom.com/wiki/Team_Create)

## R2

You probably can't assume either one. It depends on which script-editing mode your place is in, and Roblox's own sources disagree about what the default is right now.

**The two modes:**

- **Live scripting:** your collaborators see edits in real time as they're made. Nothing gets committed. Changes auto-save about every 5 minutes, or when someone presses Ctrl+S.
- **Drafts (the older collaborative editing):** edits stay in a local draft on your machine. Nobody else sees them until you commit, which you do by selecting the scripts in the Drafts window and clicking Commit. You can also right-click a draft and choose "Compare with server" to check it before committing.

**Which one you're in:** older Roblox posts say collaborative editing (Drafts) was turned on by default in Team Create. The later Live Scripting beta announcement says Live Scripting would become the new default. Since you haven't changed anything, your place is on whichever default applied when it was set up, plus any later rollout changes. If you're on a current Studio version, Live Scripting is the more likely answer, but I couldn't confirm it. The quickest check is to make a trivial edit to a script. If it shows up in a Drafts window waiting to be committed, you're in Drafts mode. If it doesn't, and a collaborator sees the change on their screen, you're in Live mode.

**What this means for a rename across several scripts:**

- **In Live mode,** your collaborators will watch the rename happen one script at a time. Partway through, some scripts will call the new name and others the old one. Anyone who playtests during that gap could hit errors. Someone typing in one of those scripts at the same moment could also clash with the edits. Tell them before you start, or ask them to stay out of those scripts until it's finished.
- **In Drafts mode,** nothing reaches them until you commit. Commit all the edited scripts together so the shared version never contains a half-finished rename.

Either way, have Claude list every script it changed so you can check the list before you share or commit anything.

Sources:
- [Roblox Docs – Collaboration](https://create.roblox.com/docs/studio/collaboration)
- [Live Scripting Beta (DevForum)](https://devforum.roblox.com/t/live-scripting-beta/2640607)
- [Collaborative Editing updates (DevForum)](https://devforum.roblox.com/t/collaborative-editing-updates/504014)
- [Team Create (legacy docs)](https://developer.roblox.com/articles/Team-Create)
- [Roblox Studio Team Create guide – obby.fun](https://www.obby.fun/blog/roblox-studio-team-create)

## R3

**Position:** At current defaults, collaborators should see the edits right away, with no commit step. Live Scripting is on by default in Team Create, and Drafts mode (the one with Commit) is off by default. The exception is that a raw `Script.Source` write may lag for a collaborator who has that script open.

**Reasoning:**
- The Creator Hub collaboration docs say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." Drafts mode is turned on in File > Experience Settings, and Commit exists only in Drafts mode. Source: https://create.roblox.com/docs/projects/collaboration
- History: Live Scripting started as an opt-in beta on 2023-10-10 (`EditorLiveScript`). https://devforum.roblox.com/t/live-scripting-beta/2640607
- It became the Team Create default on 2024-01-30 (the "Live Scripting Full Release" post). The old Collaborative Editing mode was renamed Drafts and made opt-in. https://devforum.roblox.com/t/live-scripting-full-release/2816335
- Older advice that collaborative scripting (drafts and commit) is the default is out of date.
- Mechanism: Live Scripting is built on `ScriptEditorService:UpdateSourceAsync`. A script's text is shared live, and the server autosaves it every 5 minutes and on close. Collaborators see the changes as they are applied. Autosave only matters for version history and persistence.
- Studio MCP: Roblox's official server (https://create.roblox.com/docs/studio/mcp) provides `multi_edit`, `script_read` and `script_grep`. Its docs don't say how edits are applied or mention Team Create. I'm inferring that it works like any other plugin, so the Live Scripting path applies.
- Per-script and per-collaborator differences:
  - **Script.Source:** The Live Scripting post warns that plugins writing `Script.Source` "may show discrepancies." `UpdateSourceAsync` is the recommended path. If the plugin uses raw `Source`, a collaborator with the script open might see a stale or odd buffer.
  - **Open scripts:** Scripts nobody has open are simply updated. For open scripts, the editor buffer is what is shared.
  - **Drafts mode:** If any collaborator has turned Drafts mode on, the setting is place-wide. In that case nothing would go live until committed, and the Drafts window would show pending changes.

**Practical steps:**
1. Check File > Experience Settings and confirm "Enable Drafts Mode" is off. Check that no one has pending drafts.
2. Tell the collaborators, and ask them to avoid the affected scripts, or close them, during the rename.
3. Run `script_grep` first to list every call site, including `require` users and string-based references such as RemoteEvent names or `:Invoke` strings.
4. Make the edits in one `multi_edit` batch per script, then run `script_grep` again to confirm no old names are left.
5. Press Ctrl+S, or wait for autosave, so the changes are saved. Script Version History is the undo for other people's view.
6. Don't rely on Ctrl+Z. Undo history is local to one user.
7. Consider a published or local backup first.

**Risks and unknowns:**
- I could not confirm whether the official MCP plugin uses `UpdateSourceAsync` or `Script.Source`. This is the biggest unknown.
- Roblox's docs don't spell out how plugin writes are broadcast. I'm inferring that they follow the Live Scripting path.
- A July 2026 DevForum request (https://devforum.roblox.com/t/make-draftsservice-pluginsecurity/4730729) describes agent edits in Drafts-mode places. It says the committed `.Source` can lag the editor buffer there. That confirms the "different if Drafts is on" case, but it doesn't settle plain Live Scripting.
- A team could have set Drafts mode on without the user knowing. That would flip the answer to "only after each collaborator commits."
- I couldn't see anything newer than mid-2026 that changes the default. A default change since then would change my answer.

**Confidence:** Medium-high that the default is "right away" (official docs, and two Roblox announcements agree). Medium on plugin-write behaviour, because it rests on inference.

## R4

**Position:** Under Studio's current defaults, collaborators see the edits right away, with no commit step. Live Scripting is on by default and Drafts Mode is off by default, so no drafts are created. This holds for plugin and MCP edits as well as typing, as long as the writes go through `ScriptEditorService:UpdateSourceAsync`.

**Reasoning:**
- The official collaboration docs (create.roblox.com/docs/studio/collaboration) say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." Drafts Mode is enabled under File > Experience Settings > Enable Drafts Mode, and all collaborators must leave the session for it to apply. The older "Collaborative Editing" mode, where you commit drafts, was renamed "Drafts."
- The Live Scripting beta thread (devforum.roblox.com/t/live-scripting-beta/2640607) says edits reach collaborators right away, with no change-applying step and no locking. It also says Live Scripting is built on `ScriptEditorService:UpdateSourceAsync`, which it calls the recommended way to edit source.

By sense of "see":
- **Live in an open script editor:** Yes, right away. Collaborators with the same script open see the change in real time, with cursors in each person's collaborator color. This is the case I'm most sure of.
- **Committed version:** Doesn't apply by default. Live Scripting has no draft or commit layer, so the live script is the shared version. A commit step exists only if the owner turns on Drafts Mode. In that case, edits made through the editor, including by plugins, are local drafts until committed. I'm less sure of that last point. It rests on the general rule that Drafts stay isolated until committed, not on a plugin-specific source.
- **Playtesting:** Yes, with a caveat. Playtests run on the live state, so a collaborator who presses Play after a half-finished rename will run it. Collaborative testing of a committed version is a Drafts Mode feature. The beta thread doesn't confirm how playtests pick up live script edits, so that is my inference.
- **Published or saved place:** Not instantly. Live script edits autosave about every 5 minutes, on closing, and on Ctrl+S. Studio saves the project to the cloud about every 4 minutes. The live game only changes when someone publishes. Publishing sends whatever the live state is at that moment.

**Does the write method matter?** Yes. The beta announcement warns that plugins assigning `Script.Source` directly can cause "discrepancies in script values" under Live Scripting. `UpdateSourceAsync` goes through the collaborative text system and merges cleanly with other people's keystrokes. A direct `.Source` write can replace the whole text and clobber a collaborator's concurrent edits. Check which one your MCP server uses. A DevForum commenter also reported `UpdateSourceAsync` misbehaving in one shared game, which Roblox called a bug.

**Practical advice:**
- Tell collaborators about the rename before you start, or ask them to stay out of the affected scripts.
- Check that the MCP uses `UpdateSourceAsync`.
- Do a trial run on one script.
- Don't publish mid-rename.
- Search for leftover references afterward (string-based `require`, remotes, `FindFirstChild` names).
- Use Script History as the rollback path, since script recovery is removed under Live Scripting.

**Risks and unknowns:**
- The docs are what I could reach. I couldn't verify that the October 2026 defaults are unchanged, and the beta thread is from 2023.
- A place could have Drafts Mode enabled in its Experience Settings without the owner having "changed" anything recently. Check it.
- I found no official statement on how Drafts Mode treats plugin writes, or on exact playtest semantics.
- I'd change my view if the current docs show Drafts as the default, or if the MCP writes through `.Source` in a way that bypasses live sync.

**Confidence:** Medium-high for live visibility under the defaults, since the docs state the defaults directly. Medium for the playtest, plugin-in-Drafts and `.Source` details.

Sources:
- https://create.roblox.com/docs/studio/collaboration
- https://devforum.roblox.com/t/live-scripting-beta/2640607

## R5

**Position:** Almost certainly right away. Live Scripting has been the Team Create default since January 2024, and the Drafts "commit" step only exists if someone has turned on Drafts mode. The one real caveat is how the MCP server writes the source, which I could not confirm.

**Reasoning:**
- **Current default.** Roblox's collaboration docs say "Live Scripting is enabled by default" and "Drafts mode (off by default)" ([docs](https://create.roblox.com/docs/studio/collaboration)). Collaborators edit in real time with colored cursors. Drafts mode is the one where you commit scripts to a shared repository. It is enabled in File > Experience Settings > Enable Drafts Mode, and all collaborators must exit and rejoin for it to take effect.
- **History.** The older "Collaborative Editing" drafts and commit model, from about 2019 to 2020, was renamed Drafts. Live Scripting was in beta from 2023-10-10 ([beta thread](https://devforum.roblox.com/t/live-scripting-beta/2640607)). It became the default with Team Create on 2024-01-30, and the old script-lock mode was phased out ([full release](https://devforum.roblox.com/t/live-scripting-full-release/2816335)). Older guides that mention commits are out of date unless Drafts is on.
- **MCP edits.** Roblox's Studio MCP docs say scripts are edited with `multi_edit`, and `execute_luau` can also run code ([MCP docs](https://create.roblox.com/docs/en-us/studio/mcp.md)). It runs inside your Studio via a plugin, so it is a plugin edit, not something done on a collaborator's machine.
- **Which API the edits go through.** Live Scripting is built on `ScriptEditorService:UpdateSourceAsync`, which Roblox calls "our recommended method". The same post warns that plugins using the deprecated `Script.Source` "will face discrepancies in script values". My inference, not documented, is that a `Source` write to a script someone has open could conflict with that open document instead of merging cleanly.
- **Per script.** The docs don't distinguish open from closed scripts. In theory, a script a collaborator has open is the riskiest case, because their editor is a live document being merged into.
- **Saving is separate from visibility.** Edits show up for collaborators immediately, but autosave runs only every 5 minutes or on close. Ctrl+S forces a save to Script Version History. Edits are also not live in published servers until someone publishes.

**Practical steps:**
1. Check File > Experience Settings to confirm Drafts mode is off. If it is on, the edits stay in your local drafts and collaborators see nothing until you commit. Use the Drafts window to commit, and watch for collaborator commits that need Merge From Server.
2. Tell the two collaborators what you're doing, and ask them to close the affected scripts or avoid editing them.
3. Use `script_grep` first to list every call site and confirm the rename covers them all, including calls from other scripts and string references like `require` paths or remote names.
4. Do one script first and check that your collaborators see it. Then do the rest.
5. Save with Ctrl+S, and check Script Version History so you can roll back. Don't count on Ctrl+Z, because Roblox's MCP docs don't say whether these edits are undoable.
6. Don't publish until the rename has been checked as a whole.

**Risks and unknowns:**
- I could not find documentation on whether `multi_edit` uses `UpdateSourceAsync` or `Script.Source`. This is the fact my answer depends most on. If it uses `Source`, results with open scripts could be inconsistent.
- Roblox could have changed defaults after my sources. The Drafts bug reports I saw look unofficial, but the Drafts versus Live distinction should still be right.
- Someone on the team may have enabled Drafts mode without your knowing. The brief says nobody changed settings, but it's worth checking.
- A bandwidth-starved session can turn the editor read-only, which could make edits fail.
- I would change my mind if I found official text saying plugin or MCP edits skip Live Scripting, or that they need a manual save to propagate.

**Confidence:** Medium-high that the answer is "right away" under default settings. Medium on the plugin and MCP edge cases, because they are inferred.

Sources: [Collaboration docs](https://create.roblox.com/docs/studio/collaboration), [Live Scripting Full Release](https://devforum.roblox.com/t/live-scripting-full-release/2816335), [Live Scripting Beta](https://devforum.roblox.com/t/live-scripting-beta/2640607), [Studio MCP docs](https://create.roblox.com/docs/en-us/studio/mcp.md), [ScriptEditorService reference](https://create.roblox.com/docs/reference/engine/classes/ScriptEditorService).

## R6

## Think tank: Do Team Create collaborators see MCP script edits before a commit?
opus, sonnet, sonnet · session effort · identical brief · debate skipped at 3–0

### Recommendation (3–0)
Your collaborators will see the edits right away. You don't need to commit anything, because under the default settings there is no commit step. Since January 2024, Studio's default in Team Create has been **Live Scripting**: everyone edits the same shared copy of each script in real time. The draft-and-commit workflow now belongs to **Drafts Mode**, which is off by default.

- **Same script open in their editor:** they see the edits as they happen, with collaborator cursors.
- **Committed version:** doesn't exist under the defaults. Studio saves script versions automatically about every 5 minutes, when a script is closed, or when you press Ctrl+S. Those saves appear in Script Version History.
- **Their playtests:** they get your changes right away. If someone presses Play while the rename is half done across scripts, they run broken code.
- **Live game:** players see nothing until someone publishes.
- **How the MCP writes matters:**
  - Live Scripting is built on `ScriptEditorService:UpdateSourceAsync`.
  - Roblox warns that plugins assigning the deprecated `Script.Source` "will face discrepancies in script values". That can overwrite a collaborator's typing or leave an open editor out of sync.
  - Edits through the built-in MCP's `multi_edit` tool are the safer route. Setting `.Source` from `execute_luau` is the risky one.
  - Neither route creates a private draft.

Checked:
- The [collaboration docs](https://create.roblox.com/docs/projects/collaboration) currently say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default". Drafts Mode is turned on in File ⟩ Experience Settings.
- The [full-release post](https://devforum.roblox.com/t/live-scripting-full-release/2816335) says Live Scripting "is now the default scripting experience in Studio when Team Create is enabled". It also confirms the `Script.Source` warning and that `UpdateSourceAsync` is the recommended method.
- Not checked: which API `multi_edit` uses internally. None of the panelists could confirm it either.

### Panel
- **A** (opus): "Under default settings the collaborators see the edits almost immediately. Since January 2024, Live Scripting has been Studio's default in Team Create and Drafts mode is off by default. In Live Scripting there is no commit step, so "only after the user commits" doesn't apply. The edits are not live for players, though: that still needs an explicit Publish." High confidence on the core answer, medium on how `Source` assignment behaves.
- **B** (sonnet): "Under Studio's current defaults, collaborators see the edits right away, with no commit step. Live Scripting is on by default and Drafts Mode is off by default, so no drafts are created. This holds for plugin and MCP edits as well as typing, as long as the writes go through `ScriptEditorService:UpdateSourceAsync`." Medium-high confidence.
- **C** (sonnet): "With the defaults (Team Create on, Live Scripting on, Drafts Mode off), collaborators see the edits right away. They see them live in the editor and in their own playtests, with no commit step. Nothing reaches the published game until someone publishes. I'm assuming the Studio defaults haven't changed since the docs I could read." Medium-high confidence.

### Where they split
They didn't split on the answer. All three hedged on the same unknowns: which API the MCP uses to write, and how a direct `.Source` write interacts with an editor someone has open.

### My take
The panel changed my mind. At launch I expected that the committed version only changes when you commit. That's the old Collaborative Editing model, and the sources show it hasn't been the default since early 2024. "Commit" is now a Drafts Mode idea only.

The one way your premise could still be wrong is if someone turned Drafts Mode on for this place earlier. Check File ⟩ Experience Settings before you start.

Before the rename:
1. Tell your two collaborators. Ask them to stay out of the affected scripts and not to playtest until you're done.
2. Press Ctrl+S so you have a version to roll back to.
3. Ask Claude to make the edits with the MCP's script-editing tool (`multi_edit`), not by assigning `.Source` in `execute_luau`.

After the rename:
1. Search for the old name to catch anything missed, including string-based references.
2. Save again, playtest, and publish only when it's clean.

## R7

**Short answer: if you've left the defaults alone, they'll only see the changes after you commit.**

New Team Create places have **Collaborative Editing** turned on by default. With it on:

- Script edits are **drafts** that stay local to your Studio session. The shared copy of the script, which collaborators run in playtests and which gets published, doesn't change until you commit.
- To commit, open **View → Drafts**, select the scripts, and choose **Commit**. You can also right-click a script in the Explorer. Commit all the renamed scripts together. If you commit some and not others, collaborators can end up with call sites that point to a function name that no longer exists.
- Collaborators can still see that a script is being edited from the presence indicators. If someone opens the same script while you have an uncommitted draft, they could get a merge conflict when one of you commits.

**What I'm unsure about: how the Studio MCP writes the code.** The draft system is built around edits in the Script Editor. Plugin-based tools, which is what the MCP uses, can write code in different ways. One is `ScriptEditorService:UpdateSourceAsync`, which works with drafts. Another is setting `.Source` directly, and I can't confirm from here how that interacts with drafts in your Studio version. Before the full rename, I'd run a quick test:

1. Have Claude make a trivial edit to one script, like adding a comment.
2. Check whether that script appears in your Drafts window as uncommitted.
3. Ask a collaborator whether they can see the change before you commit.

If it shows up as a draft and they can't see it, you're fine. If it bypasses drafts, warn your collaborators before the rename so nobody runs or edits those scripts halfway through.

I couldn't check your actual settings or the MCP's write method because the project isn't in this directory. To confirm Collaborative Editing is on, look in **File → Game Settings** (the Team Create / Collaborative Editing option, depending on your Studio version).

## R8

**Position:** The collaborators will see the edits right away. At current defaults, Team Create uses Live Scripting, where script changes sync in real time and there is no commit step at all. Committing only exists in Drafts mode, which is off by default. The main exception is an edit path that writes `Script.Source` directly. Those writes can fall out of sync with what collaborators have open.

**Reasoning:**
- **Default mode.** Roblox's "Live Scripting Full Release" post (DevForum, 30 Jan 2024, https://devforum.roblox.com/t/live-scripting-full-release/2816335) says "Live Scripting is now the default scripting experience in Studio when Team Create is enabled". The current collaboration docs (https://create.roblox.com/docs/projects/collaboration) say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." The history matters: Collaborative Editing, later renamed Drafts, used to hold edits back until you committed them. Live Scripting arrived as a beta in October 2023 and replaced it as the default in January 2024. I found nothing from 2025 or 2026 reversing that.
- **Saving is not committing.** Live Scripting autosaves every 5 minutes, when a script is closed, and on Ctrl/Cmd+S. That only creates entries in Script History. It does not decide when others see the changes, which happens live.
- **The edit path matters.** Live Scripting "is based on the new ScriptEditorService:UpdateSourceAsync API, our recommended method for editing script source". The same post warns that "Plugins that use the now deprecated Script.Source will face discrepancies in script values." So an edit made through `UpdateSourceAsync` behaves like typing in the editor and shows up live. A raw `Script.Source =` write, for example from Luau run through `execute_luau`, may not match what a collaborator sees in an open editor. It can also be overwritten when their editor later saves. That's my inference from Roblox's warning; I found no documentation of the exact behaviour.
- **The MCP tools.** The built-in Studio MCP server (https://create.roblox.com/docs/studio/mcp) has a dedicated `multi_edit` script tool. The docs don't say which API it uses, but a first-party tool is very likely to use `UpdateSourceAsync`. The older archived `studio-rust-mcp-server` only had `run_code`, so any edit went through whatever Luau the agent wrote.

**Practical steps before the rename:**
1. In File > Experience Settings, check that Drafts Mode is off. If it's on, the answer flips: edits stay local until committed, and you get merge prompts.
2. Tell Claude to use `multi_edit`, or `ScriptEditorService:UpdateSourceAsync` if it writes Luau. It should not assign `Script.Source`.
3. Warn the collaborators. Each script changes as it's edited, so partway through the rename some callers will use the new name and others the old one. Their playtests could break, and their cursors may jump in scripts they have open. Ideally they close the affected scripts or pause playtesting.
4. Before starting, save or publish a version, or press Ctrl+S on each affected script, so Script History has a rollback point.
5. Afterwards, search all scripts for the old name to confirm nothing was missed.

**Risks and unknowns:**
- My answer depends most on Drafts Mode really being off in this place. "Nobody changed settings" might not guarantee that for an old place. Collaborative Editing used to be the default, and I couldn't confirm that the 2024 rollout switched existing places that already had it on. Checking the setting takes ten seconds and settles it.
- I haven't confirmed which API `multi_edit` uses internally.
- How a raw `Source` write behaves when a collaborator has the script open is inferred from Roblox's "discrepancies" warning, not documented.

**Confidence:** High that the default is real-time with no commit step, since two current first-party sources agree. Medium on the plugin and MCP edit path and on the old-place caveat.

## R9

**Position:** With the defaults (Team Create on, Live Scripting on, Drafts Mode off), collaborators see the edits right away. They see them live in the editor and in their own playtests, with no commit step. Nothing reaches the published game until someone publishes. I'm assuming the Studio defaults haven't changed since the docs I could read.

**Reasoning:**
- The [Roblox collaboration docs](https://create.roblox.com/docs/studio/collaboration) say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default". Drafts is turned on in File > Experience Settings, and all collaborators must leave the session for the change to apply.
- The [Live Scripting beta announcement](https://devforum.roblox.com/t/live-scripting-beta/2640607) says Live Scripting became the default mode. The old Collaborative Editing mode was renamed "Drafts".
- The commit workflow (Drafts window, Commit, green ⊕ icon, Merge From Server) applies only when Drafts Mode is on.

Taking each sense of "see":
- **Live in the script editor:** Yes, if the change goes through Live Scripting's path. Edits sync in real time, and collaborators who have the script open see them with colored cursors.
- **Committed version:** Mostly not applicable, because Live Scripting has no per-user draft or commit step. Edits go straight into the shared script. Saved versions appear in Script Version History, and scripts autosave every 5 minutes, on close, or on Ctrl+S.
- **Playtest:**
  - Each collaborator's Studio holds the live shared source, so their F5/Run playtest picks up your renamed function immediately.
  - The beta thread notes that teammates' unfinished code appears in your playtests too.
  - If someone has Drafts Mode on, their playtest uses their local draft, so it wouldn't match.
  - Drafts docs mention "collaborative testing" of committed versions, which is the Drafts-only equivalent.
- **Published place:** No. Team Create autosave keeps the Studio cloud copy current, but the live game changes only when someone publishes.

**Does the write method matter?** Probably yes, though the evidence is thinner here.
- The beta post says Live Scripting is built on `ScriptEditorService:UpdateSourceAsync`. It recommends that API and warns that plugins using `script.Source` "will face discrepancies in script values".
- `UpdateSourceAsync` (or `EditScript`-style edits) merges as a normal live edit and keeps open editors and cursors consistent.
- A direct `Source` assignment replaces the whole text. It can clobber a collaborator's in-flight typing, and it may behave oddly if the script is open.
- Plugin edits are not a separate draft channel. In Live Scripting they are just edits to the shared document. In Drafts Mode, a plugin write would land in the local user's draft and need a commit, the same as typing.
- One commenter reported `UpdateSourceAsync` failing under live editing. An engineer called it a likely bug and couldn't reproduce it outside that game.
- I couldn't find documentation on how the official Roblox Studio MCP writes scripts. Which API it uses is unverified.

**Practical advice:**
- Tell your two collaborators before you start.
- Check that Drafts Mode is actually off (Experience Settings).
- Ask them to save and avoid editing the affected scripts during the rename.
- Rename every caller in one pass. A half-finished rename shows up live and breaks their playtests.
- Afterward, grep for the old name and check Script Version History. It is your undo, since Script Recovery is removed in Live Scripting mode.
- Press Ctrl+S, then publish deliberately.

**Risks and unknowns:**
- The docs' default statements may be stale for October 2026. I didn't find a newer release note.
- Direct `Source` writes might behave differently under Live Scripting today than the 2023 beta post describes.
- The playtest conclusion is inferred from the shared-source design. The docs don't state it.
- What would change my mind: Drafts Mode actually being on, or a note that plugin writes bypass the live document.

**Confidence:** Medium-high on the default and live behavior, because the docs state the defaults explicitly. Medium-low on the details of how the MCP writes and how `Source` assignment interacts with live documents.

Sources:
- [Roblox collaboration docs](https://create.roblox.com/docs/studio/collaboration)
- [Live Scripting Beta (DevForum)](https://devforum.roblox.com/t/live-scripting-beta/2640607)

## R10

**Position:** Under default settings the collaborators see the edits almost immediately. Since January 2024, Live Scripting has been Studio's default in Team Create and Drafts mode is off by default. In Live Scripting there is no commit step, so "only after the user commits" doesn't apply. The edits are not live for players, though: that still needs an explicit Publish.

**Reasoning:**
- **The defaults:** Roblox's full-release post (Jan 30, 2024, devforum.roblox.com/t/live-scripting-full-release/2816335) says: "Live Scripting is now the default scripting experience in Studio when Team Create is enabled." Drafts is opt-in. The collaboration docs (create.roblox.com/docs/projects/collaboration) say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." Committing is a Drafts-only idea.
- **Live in the editor if they have the script open:** Yes, if the MCP writes through `ScriptEditorService:UpdateSourceAsync`. Live Scripting is built on that API, which Roblox calls "our recommended method for editing script source." Roblox's built-in MCP edits scripts with a `multi_edit` tool (create.roblox.com/docs/studio/mcp). Its docs don't say which API it uses, but I'd expect `UpdateSourceAsync`. Some community MCPs say they use it, for example el4cteo/rbx-studio-mcp.
- **It does matter how the MCP writes:** Direct `Script.Source =` (for example via `execute_luau`) still changes the shared DataModel. But Roblox warns that "Plugins that use the now deprecated `Script.Source` will face discrepancies in script values." An open editor document can then disagree with the property, or overwrite it. So plugin edits are not held back like private drafts. They go into the shared live state, and the `Source` route is the unreliable one.
- **"Committed version":** There isn't one under the defaults. The nearest thing is a saved version. Live Scripting autosaves every 5 minutes and on close, and Ctrl/Cmd+S saves by hand. Saved versions show up in Script Version History.
- **Playtesting:** Yes, as soon as the change has reached a collaborator's session, because their playtest runs their synced copy of the place. The danger is timing. If someone playtests halfway through a multi-script rename, they run broken code.
- **Published place:** Autosave updates the Team Create cloud copy. Live servers only get the change after someone publishes.
- **If Drafts were on (not the default):** Then commits would apply, and how plugin writes interact with drafts is less well documented. I wouldn't count on it.

**Practical advice:**
1. Before starting, check that Drafts is really off (Experience Settings / Workspace `EditorLiveScript`).
2. Tell the two collaborators. Ask them to stay out of the affected scripts and not to playtest until you say it's done.
3. Press Ctrl+S first to save a version you can roll back to.
4. Make the edits with `multi_edit` / `UpdateSourceAsync`, not `execute_luau` assigning `.Source`.
5. Run `script_grep` to confirm the old name is gone everywhere, including callers in other scripts.
6. Save again, playtest, and publish only when it's clean.

**Risks and unknowns:** Everything rests on Live Scripting still being the default in October 2026. The current docs say it is, but I can't see this particular place's settings. I haven't confirmed which API the built-in `multi_edit` uses underneath. The exact behaviour of `Source` assignment with an editor open is described only vaguely ("discrepancies"). A 2023 beta comment reported a bug with `UpdateSourceAsync` under live editing. I'd change my view if the place has Drafts enabled, or if Roblox has since changed the default.

**Confidence:** High that there's no commit step and changes show up live for collaborators but not for players. Medium on the exact behaviour of `Source` assignment.

Sources: [Live Scripting Beta](https://devforum.roblox.com/t/live-scripting-beta/2640607), [Live Scripting Full Release](https://devforum.roblox.com/t/live-scripting-full-release/2816335), [Collaboration docs](https://create.roblox.com/docs/projects/collaboration), [Studio MCP docs](https://create.roblox.com/docs/en-us/studio/mcp.md), [rbx-studio-mcp](https://mcpservers.org/servers/el4cteo/rbx-studio-mcp)

## R11

## Think tank: Team Create MCP edits, live or after commit?
opus, sonnet, sonnet · session effort · identical brief · debate skipped at 3–0

### Recommendation (3–0)
**Your collaborators will see the edits right away, and there's nothing to commit.** Since January 2024, Team Create uses Live Scripting by default. Script edits sync to everyone in real time. Committing only exists in Drafts mode, which is off unless someone turns it on. Saving (autosave every 5 minutes, or Ctrl+S) doesn't control when people see changes. It only adds entries to Script History.

The one caveat all three raised is how the MCP edits get written. Live Scripting is built on `ScriptEditorService:UpdateSourceAsync`. Roblox warns that plugins writing the deprecated `Script.Source` "will face discrepancies in script values." None of the panelists could confirm which of the two the MCP `multi_edit` tool uses.

The steps they agree on:
1. Check File › Experience Settings › Enable Drafts Mode is off.
2. Warn your collaborators. Halfway through the rename, some scripts will use the new name and others the old one, so their playtests can break. Ask them to close the affected scripts while it runs.
3. Have Claude `script_grep` for the old name before and after the rename.
4. Press Ctrl+S first so Script History has a rollback point. Don't rely on Ctrl+Z.

Checked:
- **The default.** The [collaboration docs](https://create.roblox.com/docs/projects/collaboration) say, word for word, "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." Commit appears only in the Drafts section. Confirmed.
- **When it changed.** The [Live Scripting full release post](https://devforum.roblox.com/t/live-scripting-full-release/2816335) is dated 30 Jan 2024. It says "Live Scripting is now the default scripting experience in Studio when Team Create is enabled," and it carries the `Script.Source` warning. Confirmed. The post doesn't say how existing places that already had the old Collaborative Editing were handled.

### Panel
- **A** (opus): "The collaborators will see the edits right away. At current defaults, Team Create uses Live Scripting, where script changes sync in real time and there is no commit step at all. Committing only exists in Drafts mode, which is off by default. The main exception is an edit path that writes `Script.Source` directly. Those writes can fall out of sync with what collaborators have open." High confidence on the default, medium on the MCP write path and on older places.
- **B** (sonnet): "At current defaults, collaborators should see the edits right away, with no commit step. Live Scripting is on by default in Team Create, and Drafts mode (the one with Commit) is off by default. The exception is that a raw `Script.Source` write may lag for a collaborator who has that script open." Medium-high confidence.
- **C** (sonnet): "Almost certainly right away. Live Scripting has been the Team Create default since January 2024, and the Drafts "commit" step only exists if someone has turned on Drafts mode. The one real caveat is how the MCP server writes the source, which I could not confirm." Medium-high confidence.

### Where they split
They didn't split on the answer. Only A raised one extra point: in a place created before 2024, when Collaborative Editing (drafts and commit) was the default, Drafts mode might still be on even though nobody changed anything. The announcement doesn't say whether older places were switched over. Looking at the setting in Experience Settings settles it.

### My take
I agree with the panel, and the checks made me more sure of the leaning I started with. One point matters more for you than the panel let on. You asked about committing, which suggests you know the older model. If your place dates from before 2024, A's caveat is the one to act on. "We never touched the settings" could mean Drafts mode is still on from back then, and in that case the answer flips: edits stay local until you commit them. Spend ten seconds checking File › Experience Settings before you start.

If Drafts mode is off, assume each script changes for everyone the moment Claude edits it. Tell your collaborators first, and have Claude use `multi_edit`, or `UpdateSourceAsync` if it writes Luau, rather than assigning `.Source`.
