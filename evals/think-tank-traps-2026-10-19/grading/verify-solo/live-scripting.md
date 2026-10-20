# live-scripting

Question asked:

> Our Roblox place is in Team Create with two other people editing, and we haven't touched the collaborative editing settings. I'm going to have Claude rename a function across several scripts through the Studio MCP. Will my collaborators see those script edits right away, or only after I commit them?

## R1

You'll probably see the edits show up for your collaborators right away. With default settings there's nothing to commit. One part of this I couldn't confirm in the official docs, explained below.

**Confirmed in Roblox's [Collaboration docs](https://create.roblox.com/docs/projects/collaboration):**
- **Live Scripting is the default.** The page says "Live Scripting is enabled by default." Collaborators edit the same scripts in real time, and each person's cursor shows in their own color. Since you haven't changed the settings, this is your mode.
- **Committing only exists in Drafts mode, which is off by default.** In Drafts mode, script edits stay local until you commit them from the Drafts window. You turn it on in File > Experience Settings with "Enable Drafts Mode." Everyone has to leave the session for the switch to apply.
- **Saving is for history, not for sharing.** In Live Scripting, edits auto-save every 5 minutes, or when you press Ctrl+S, into Script History. That records versions; it doesn't control when others see a change.

**Confirmed in Roblox's [Studio MCP server docs](https://create.roblox.com/docs/studio/mcp):**
- The MCP server is built into Studio and edits the scripts in your open session. The editing tool is `multi_edit`, and `script_grep` searches across scripts. A rename across several scripts would use these.

**Not confirmed:**
- Neither page says how MCP edits behave in Team Create, Live Scripting or Drafts. I'm inferring that MCP edits sync live like your own typing, because they change the same scripts in your Live Scripting session. I didn't find a doc that states this.

**What this means for the rename:**
- Your collaborators will see the renamed function appear in their open scripts as it happens, and there's no commit step to review it first.
- If they're working in the same scripts, the edits could collide with their typing. For a short time some scripts may be updated and others not, so if someone runs a playtest then, it could break.
- Tell them before you start, or do it while they're out of those scripts. If you want to review changes before others get them, Drafts mode does that, but everyone has to leave the session to switch.

I also looked at a third-party [Obby.fun blog post](https://www.obby.fun/blog/roblox-studio-team-create) (Oct 6, 2026) that describes the same live vs. Drafts split. I relied on Roblox's own docs above.

Sources:
- [Roblox Creator Docs – Collaboration](https://create.roblox.com/docs/projects/collaboration)
- [Roblox Creator Docs – Studio MCP server](https://create.roblox.com/docs/studio/mcp)
- [Roblox Creator Docs – Studio overview](https://create.roblox.com/docs/studio.md)
- [Obby.fun – Roblox Studio Team Create](https://www.obby.fun/blog/roblox-studio-team-create)

## R2

## Think tank (solo): Team Create, MCP script edits: live or on commit?
opus · session effort · one panelist

### Recommendation
Your collaborators will see the edits right away. Live Scripting has been the Team Create default since January 2024, and it syncs script changes to everyone in the session in real time. There's no commit step. Saving (Ctrl+S, or the 5-minute autosave) only adds an entry to Script History; it doesn't decide who sees the change. Only Drafts Mode, which is off by default, keeps your edits local until you commit them.

How the Studio MCP writes doesn't change that. Its `multi_edit` tool edits one script per call, and `execute_luau` can set `.Source` directly. Either way the change lands in the shared place, so the others get it. The write path only affects how cleanly it lands.

The panelist raised two caveats:
- **Older places.** Drafts was the Team Create default from 2020. A place that had it on before 2024 may never have been switched to Live Scripting, and then edits would wait for a commit. Check File ⟩ Experience Settings for "Enable Drafts Mode".
- **Half-renamed code.** Because the edits land one script at a time, collaborators and any playtest they start can see the function renamed in some scripts while callers elsewhere still use the old name. Someone typing in one of those scripts at the same moment could also clash with the plugin's write.

Before the rename, either:
- turn on Drafts Mode (everyone has to leave the session for it to take effect),
- ask the other two to stay out of the affected scripts and not playtest until it's done, or
- do the rename in a local copy of the place.

Either way, have Claude run `script_grep` first so you can see every script involved.

Checked: Roblox's collaboration docs (create.roblox.com/docs/projects/collaboration) say "Live Scripting is enabled by default," "Drafts Mode is disabled by default," and Live Scripting "lets collaborators code together in real time." Turning on Drafts Mode is under File ⟩ Experience Settings, and "all collaborators will need to exit the session for the change to take effect." All of this matches the panelist. I didn't check the MCP's exact write method; the panelist couldn't confirm it either.

### Panelist
"The collaborators will see the edits right away, not after a commit, because Live Scripting is the Team Create default and has no commit step." Confidence: medium-high.

### My take
The panelist changed my mind. Going in, I thought Drafts was still the default, and that the only question was whether the MCP's writes skipped it. That was out of date: Live Scripting replaced Drafts as the default, so on a place with untouched settings the edits go live as they're made. I agree with the panelist's answer.

The caveat that matters most in practice is the half-renamed state, more than the older-place question. With two people working at the same time, a playtest started partway through could break on calls to the old name. The simplest protection is to tell them before you start and rename all the call sites in one go. A quick look at the Drafts Mode setting will tell you whether the older-place caveat applies to you at all.

## R3

**Short answer: they'll see the edits right away. With default settings there's no commit step.** Team Create starts with Live Scripting on and Drafts mode off. "Commit" only exists in Drafts mode. So as Claude renames the function across your scripts, your two collaborators will see each script change as it's made, including the in-between state where some scripts use the new name and others still use the old one.

**What I checked in Roblox's current docs:**

- **Live Scripting is on by default.** Verified on the collaboration page: "Live Scripting is enabled by default." It "lets collaborators code together in real time."
- **Drafts mode is off by default.** Verified: "Drafts Mode is disabled by default." Drafts are what let you "edit and test scripts without affecting the game for others." They're saved locally until you commit them.
- **Turning on Drafts mode.** Verified: it's under File → Experience Settings → Enable Drafts Mode. All collaborators have to exit the session before the change takes effect.
- **Saving vs. publishing.** Partly verified. The docs say collaborative sessions auto-save to the cloud. They give two different intervals (four minutes in one place, five in another). They don't directly say how this relates to the published game. As far as I know, players only get the changes when you publish, but I didn't find a sentence confirming that.

**What I couldn't verify:**

- **How the Studio MCP server behaves in Team Create.** Roblox's MCP page doesn't mention Team Create, Live Scripting or Drafts. It only says MCP clients "can read and modify content in your open Roblox places." Its only script-editing tool is `multi_edit`. I'm assuming its edits act like normal live edits, which is very likely but not documented.
- **Whether MCP edits go into your drafts if you turn Drafts mode on.** The docs don't say. Test it on one script before relying on it.

**Practical advice:** Since your collaborators will see the rename while it's half done, tell them before you start. If one of them runs a playtest partway through, it could break on calls to the old name. If you'd rather review the whole change before anyone sees it, turn on Drafts mode first (everyone has to rejoin) and check that the MCP edits actually land in your drafts.

Sources:
- [Collaboration (Roblox Creator Docs)](https://create.roblox.com/docs/projects/collaboration)
- [Connect to the Roblox Studio MCP server](https://create.roblox.com/docs/studio/mcp)
- [Studio MCP (markdown version)](https://create.roblox.com/docs/en-us/studio/mcp.md)

## R4

**Position:** Under today's defaults the edits show up right away. Since January 2024, Live Scripting has been the default for Team Create places, and it has no commit step. Script changes sync to everyone in the session in real time, so the other two editors would see the rename as it happens.

**Reasoning:**
1. **Default mode (high confidence).** The official docs (https://create.roblox.com/docs/projects/collaboration) say: "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." The [Live Scripting Full Release](https://devforum.roblox.com/t/live-scripting-full-release/2816335) post (30 Jan 2024) says it "is now the default scripting experience in Studio when Team Create is enabled." Only Drafts mode lets you edit and test "without affecting the game for others" and then commit. In Live Scripting, Ctrl+S and the 5-minute autosave only add entries to Script History. They don't control who sees the change.
2. **How the MCP writes (medium confidence).** The original [Roblox/studio-rust-mcp-server](https://github.com/Roblox/studio-rust-mcp-server) is no longer actively developed and points users to the MCP server built into Studio. That built-in server's tools are documented at https://create.roblox.com/docs/studio/mcp: `script_read`, `script_grep`, `multi_edit` (edits one script per call, Edit DataModel only) and `execute_luau`. The docs don't say whether `multi_edit` calls `ScriptEditorService:UpdateSourceAsync` or sets `Script.Source`, and I couldn't check the source because it ships inside Studio.
3. **How that write path meets Live Scripting.** Roblox says Live Scripting is built on `UpdateSourceAsync` ([beta post](https://devforum.roblox.com/t/live-scripting-beta/2640607)). Changes made through it are live edits that sync to everyone. If the rename instead goes through `execute_luau` setting `.Source` directly, it still changes the shared DataModel, so collaborators still get it. The difference is that Roblox warns `Script.Source` writes can cause "discrepancies in script values," especially in a script someone has open. Neither path holds the change back.

**Caveats and what to do first:**
- **Older places.** Collaborative Editing (Drafts) was turned on by default for Team Create in 2020 ([2020 post](https://devforum.roblox.com/t/collaborative-editing-updates/504014)). I found nothing saying whether places that already had it on were moved to Live Scripting. "Nobody changed the defaults" may therefore still mean Drafts for an old place. Check whether Drafts Mode is on in Game Settings, or whether the Drafts window lists scripts. If Drafts is on, the outcome depends on whether the MCP writes into your draft or straight to the server copy, which I couldn't confirm.
- **Half-finished state.** `multi_edit` changes one script per call. Collaborators, and any playtest they start, could see the function renamed in some scripts but not the callers yet. Someone typing in one of those scripts at the same moment could also collide with the plugin's write.
- **Before running the rename, if you want control:** turn on Drafts Mode, which requires every collaborator to leave the session before it takes effect. Or tell the other two editors to stay out of the affected scripts and not playtest until it's done. Or do the rename in a local copy of the place, outside Team Create, and bring it back afterwards. Either way, ask Claude to run `script_grep` first so you can see the full list of affected scripts.

**Risks and unknowns:** The fact this rests on most is that the place is in Live Scripting mode. A legacy Drafts setting carried over from before 2024 would reverse the answer. The MCP's exact write API is unconfirmed, but it only affects how cleanly the edit lands, not whether others see it straight away.

**Confidence:** High that the default is live, real-time sync. Medium on the exact MCP write mechanism and on how older places are treated.

Position: The collaborators will see the edits right away, not after a commit, because Live Scripting is the Team Create default and has no commit step. Confidence: medium-high.

## R5

## Think tank (solo): Do Team Create collaborators see MCP script edits right away?
opus · session effort · one panelist

### Recommendation
Your collaborators will see the edits right away. You never commit anything. With collaborative editing settings at their defaults, Team Create uses Live Scripting, where script changes reach everyone in the session as they're made. Committing only exists in Drafts Mode, which is off by default and has to be turned on in File > Experience Settings. Saving (Ctrl/Cmd+S, or the 5-minute autosave) just adds a version to Script History; it isn't what makes edits visible to others. Players in the published game see nothing until you publish.

The caveat is about how the MCP server writes the scripts. Live Scripting is built on `ScriptEditorService:UpdateSourceAsync`, and Roblox warns that plugins using the deprecated `Script.Source` "will face discrepancies in script values." If the server writes through `UpdateSourceAsync`, collaborators see the edits live just as if you'd typed them. If it sets `Script.Source` directly (for example from an `execute_luau` snippet), the edits are still not held for a commit, but collaborators' open script windows may fall out of sync or overwrite the change. Roblox's MCP docs don't say which method their tools use.

Before letting the AI do the rename, the panelist suggests:
1. Warn your collaborators and have them close the affected scripts. The rename lands one script at a time, so for a short while their playtests can run a half-renamed codebase that errors.
2. Make a restore point: save the scripts so Script History has a version, or save a copy of the place.
3. If you want to review the changes before anyone sees them, turn on Drafts Mode. Everyone has to leave the session for that switch to take effect, and you then commit the drafts yourself.
4. Find out whether the MCP tool uses `ScriptEditorService` or `Script.Source`, and re-read the scripts afterwards to check nothing was missed.

Checked:
- Default mode: Roblox's collaboration docs (create.roblox.com/docs/projects/collaboration) say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." Live Scripting has no commit step. Confirmed.
- Roblox's January 2024 Live Scripting full-release announcement on the DevForum says Live Scripting "is now the default scripting experience in Studio when Team Create is enabled." It also says Live Scripting is built on `UpdateSourceAsync` and gives the `Script.Source` warning quoted above. Confirmed.
- Not checked: which method Roblox's MCP server uses to write script source. Neither the panelist nor I found a source for that.

### Panelist
"At the current defaults the two collaborators see the edits live, as each change lands. Live Scripting is the default when Team Create is on, and in that mode there is no commit step at all. Committing only exists in Drafts Mode, which is off by default, and the brief says nobody changed it." High confidence on the default behaviour. Medium on exactly how MCP edits behave.

### My take
The panelist moved me. I launched half-expecting drafts and a commit step, which is the older behaviour. The current docs settle it: edits are live, and there's nothing to commit. Since your collaborators are actively working in the place, the practical point is that the AI's rename goes straight into their session as it happens. If you want to review the changes before they see them, turn on Drafts Mode first, while everyone is out of the session. Otherwise, warn them and make the restore point before you start.

## R6

With the default settings, your collaborators will see the edits **right away**. There's no commit step. One caveat: no Roblox page says how edits made through the MCP specifically are handled.

**What I checked in the current docs:**

- **"Live Scripting is enabled by default."** (quoted from the [Collaboration docs](https://create.roblox.com/docs/projects/collaboration)). Collaborators edit the same script in real time and see each other's cursors.
- **"Drafts Mode is disabled by default."** Drafts is the mode where you edit privately and then commit. It's only on if someone turns it on under **File > Experience Settings**.
- **Saving isn't the same as sharing.** Live Scripting autosaves every 5 minutes, and Ctrl+S saves a version to Script History. Those saves only create history entries; they don't control whether collaborators can see your edits.
- **The MCP edits scripts directly.** The [Studio MCP docs](https://create.roblox.com/docs/studio/mcp) list `multi_edit`, which "applies multiple edits to a script in one operation," plus `execute_luau`, both run against the Edit data model. The docs also warn that MCP clients "can read and modify content in your open Roblox places."

**What I couldn't verify:**

- **Whether MCP edits behave like typing.** The MCP page says nothing about Team Create, Live Scripting or Drafts. I'm inferring that MCP edits sync live because they change the same shared place that Live Scripting syncs. That seems very likely, but it isn't documented.
- **Whether your place is really on the defaults.** Not touching the settings doesn't prove Drafts is off. Someone may have turned it on, and I couldn't find anything confirming that older places were moved to the new defaults. The Live Scripting setting was once an opt-in beta (`EditorLiveScript`, per the [DevForum beta post](https://devforum.roblox.com/t/live-scripting-beta/2640607)). Take a quick look under **File > Experience Settings** to confirm Drafts Mode is off.

**What this means for the rename:** each script will update for everyone as Claude edits it. While the rename is part-way done, some scripts will call the new name and others the old one. If a collaborator playtests then, or is editing one of those scripts at the same time, things can break or their edits can collide with Claude's. Tell them before you start, or have Claude do all the edits in one quick pass and then check for any remaining uses of the old name.

Sources:
- [Collaboration – Roblox Creator Docs](https://create.roblox.com/docs/projects/collaboration)
- [Connect to the Roblox Studio MCP server – Roblox Creator Docs](https://create.roblox.com/docs/studio/mcp)
- [Live Scripting Beta – Roblox DevForum](https://devforum.roblox.com/t/live-scripting-beta/2640607)

## R7

**Position:** Under today's defaults the collaborators see the edits live. There is nothing to commit, because Live Scripting is the default for scripts in Team Create and Drafts Mode is off by default. Edits from an MCP server are normal edit-time changes, so they sync the same way typed edits do. The one exception is an older place that is still in Drafts Mode, where a commit is needed.

**Reasoning:**
1. **Current defaults.** Roblox's collaboration docs (https://create.roblox.com/docs/projects/collaboration) say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." Drafts Mode is turned on in File > Experience Settings. Only in that mode do edits stay local until you click Commit.
2. **This has changed over time.** Collaborative Editing (drafts plus commit) was Team Create's default from about 2020–21. The Live Scripting Beta post (https://devforum.roblox.com/t/live-scripting-beta/2640607) says Live Scripting "will be the new default script editing mode for Studio in Team Create." It says Collaborative Editing becomes "Drafts," and it describes changes as shared in real time with nothing to apply. So the familiar "only after commit" behaviour is the old default.
3. **Edits from a plugin or MCP server.** The same post says Live Scripting "is based on the new ScriptEditorService:UpdateSourceAsync API," which it calls the recommended way to edit source. It warns that "plugins that use script.Source there will face discrepancies." Both routes write to the shared copy of the script, not a private draft. `UpdateSourceAsync` goes through the live document. Writing `Script.Source` directly also replicates, but it can clash with what a collaborator has open in their editor. Neither route adds a commit step.
4. **The MCP servers.** Roblox's official server is now built into Studio (https://create.roblox.com/docs/studio/mcp). It has `script_read`, `script_grep` and `multi_edit` tools, plus `execute_luau`. Its docs say nothing about Team Create or drafts, so there's no sign it keeps edits private. The older reference server (https://github.com/Roblox/studio-rust-mcp-server) is archived and only offers `run_code`, so Claude would set `Script.Source` itself. Community servers such as boshyxd/robloxstudio-mcp (set_script_source tool) and EL4CTEO rbx-studio-mcp say they use `UpdateSourceAsync`. None of them adds a commit layer.

**Risks and unknowns:**
- **The fact my answer depends on most is that this place really is in Live Scripting mode.** The setting is stored per place. A place that was set up for Team Create while drafts were the default may still be in Drafts Mode even if nobody touched it. In that case the edits stay in the user's drafts until committed. I'm inferring this from the setting being per place, not from a Roblox statement.
- If `Script.Source` is written directly while a collaborator has the script open, their editor may briefly disagree with the new text. Using `multi_edit` or `UpdateSourceAsync` avoids this.
- The 5-minute autosave only controls Script History versions, not when collaborators see changes. Cloud saves of the place happen every four minutes.
- I found no Roblox doc that explicitly confirms how MCP edits behave in Drafts Mode.

**What to check in Studio:** Open File > Experience Settings and confirm Drafts Mode is off. You can also check that `EditorLiveScript` is enabled in Workspace properties under Scripting. If the Drafts window lists scripts when you edit, you're in Drafts Mode. A quick test: have a collaborator open one of the target scripts, run a trivial MCP edit, and see whether it shows up for them.

**Confidence:** Medium-high. The docs clearly say Live Scripting is on and Drafts is off by default. My doubt is whether this place carries an old Drafts setting, and the fact that no doc covers MCP edits in Team Create directly.

## R8

## Think tank (solo): Do collaborators see MCP script edits live?
opus · session effort · one panelist

### Recommendation
Your collaborators will most likely see the edits right away, and there's nothing to commit. In Team Create today, scripts use **Live Scripting by default and Drafts Mode is off by default**. Edits go into the shared copy of each script as they happen. The "only after you commit" behaviour belongs to Drafts Mode, which used to be called Collaborative Editing and was the default before Live Scripting replaced it.

Edits made through a Studio MCP server don't add a commit step. Roblox's official built-in MCP server (with tools like `multi_edit`) and community servers that use `ScriptEditorService:UpdateSourceAsync` both write to the shared live copy. Writing `Script.Source` directly also syncs, but Roblox warns it can briefly leave a collaborator's open editor out of step with the new text.

The one real exception: the setting is stored per place. **A place set up for Team Create when drafts were the default could still be in Drafts Mode even though nobody changed anything.** In that case the rename stays in your local drafts until you commit.

How to confirm in Studio:
- **File ⟩ Experience Settings:** check that Drafts Mode is off.
- **Workspace ⟩ Scripting:** check that `EditorLiveScript` is on.
- **Quick test:** have a collaborator open one of the target scripts, make a trivial edit through the MCP, and see whether it shows up for them.

Checked:
- **Defaults:** Roblox's collaboration docs (create.roblox.com/docs/projects/collaboration) say "Live Scripting is enabled by default" and "Drafts Mode is disabled by default." Commit is described only as part of Drafts mode. ✔
- **Older places:** the DevForum Live Scripting Beta post says Live Scripting "will be the new default script editing mode" and that Collaborative Editing becomes "Drafts". It also says Live Scripting is turned on per place through `EditorLiveScript` and is built on `UpdateSourceAsync`, with a warning that plugins using `script.Source` "will face discrepancies." That supports the caveat about older places. I did not check which MCP server you use or how it writes edits.

### Panelist
"Under today's defaults the collaborators see the edits live. There is nothing to commit, because Live Scripting is the default for scripts in Team Create and Drafts Mode is off by default. Edits from an MCP server are normal edit-time changes, so they sync the same way typed edits do. The one exception is an older place that is still in Drafts Mode, where a commit is needed." Medium-high confidence.

### My take
I agree with the panelist. Before it answered, I also leaned towards "live", but I wasn't sure how MCP edits behave. The `UpdateSourceAsync` detail settled that for me: Live Scripting is built on the same API that plugins use to edit scripts.

The part that matters for you is the older-place caveat. If this place has been in Team Create since around 2021–2023, it's worth checking `EditorLiveScript` before you start. The practical upshot also matters: with live scripting, your collaborators will see the rename happen script by script. Partway through, some scripts will call the new name while others still use the old one. If either of them is playtesting during that window, they'll hit errors. Tell them before you start, or have Claude make all the edits in one quick batch.

## R9

**Position:** At the current defaults the two collaborators see the edits live, as each change lands. Live Scripting is the default when Team Create is on, and in that mode there is no commit step at all. Committing only exists in Drafts Mode, which is off by default, and the brief says nobody changed it.

**Reasoning:**
- The Creator Hub collaboration page (https://create.roblox.com/docs/projects/collaboration) says "Live Scripting is enabled by default." Drafts Mode is listed as opt-in (File > Experience Settings > Enable Drafts Mode), and switching modes only takes effect after everyone leaves the session. Commit and Merge appear only under Drafts.
- The full-release announcement of 30 Jan 2024 (https://devforum.roblox.com/t/live-scripting-full-release/2816335) says Live Scripting is "now the default scripting experience in Studio when Team Create is enabled." Edits reach collaborators as you type, and nothing has to be applied or committed. Saving (Ctrl/Cmd+S, or autosave every 5 minutes and on close) only adds a version to Script History. It is not what makes edits visible.
- I found no 2025–2026 announcement reversing this default. A July 2026 feature request (https://devforum.roblox.com/t/make-draftsservice-pluginsecurity/4730729) about AI agents producing piles of uncommitted drafts specifically describes places "with Drafts Mode enabled." That supports Drafts still being the non-default path.
- **Programmatic edits:** Live Scripting is built on `ScriptEditorService:UpdateSourceAsync`, which Roblox calls the recommended way to edit script source. The same announcement warns that plugins using the "now deprecated `Script.Source` will face discrepancies in script values." So an MCP server that writes through `UpdateSourceAsync` should spread its edits live just like typing. One that assigns `Script.Source` (for example a raw `execute_luau` snippet) risks collaborators' open editors falling out of sync with what was written, or their own typing overwriting it. The official Studio MCP docs (https://create.roblox.com/docs/en-us/studio/mcp.md) list `multi_edit` and `execute_luau` but don't say which API they use. Some community servers state they use `UpdateSourceAsync`.

**In practice, before letting the AI edit several scripts:**
1. Tell the collaborators, and ask them to close the affected scripts or stay out of them. A rename across several scripts arrives one script at a time, so for a moment they may see, and run in playtests, a half-renamed codebase that errors.
2. Make sure there's a restore point. Save the scripts so they get a version in Script History, or save a copy of the place.
3. If you want to review the changes before anyone sees them, the only built-in way is turning on Drafts Mode. That needs everyone to leave the session, and you then review and commit the AI's drafts by hand.
4. Check that the MCP tool writes through `ScriptEditorService`, not `Script.Source`. Afterwards, re-read the scripts to confirm nothing was missed.

Note that "live" means live inside the Team Create session. Players on the published game see nothing until you publish.

**Risks and unknowns:** My answer rests on the docs and the 2024 announcement still describing today's default, and I found nothing saying otherwise as of October 2026. I don't know how the user's specific MCP server writes source. If it uses `Script.Source`, what collaborators see may be inconsistent rather than cleanly live, though it still won't be held back for a commit. If the place had Drafts Mode turned on at some point, the answer flips to "only after commit," but the brief rules that out.

**Confidence:** High on the default behaviour, since both the official docs and the announcement say it directly. Medium on the exact behaviour of MCP edits, because no Roblox doc describes how `UpdateSourceAsync` or `Script.Source` interact with Live Scripting beyond the deprecation warning.
