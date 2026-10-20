# local-md-agents

Question asked:

> Our repo keeps its agent instructions in AGENTS.md and has no CLAUDE.md, and Claude Code picks AGENTS.md up fine. I want some personal instructions I don't commit, so I'm going to add a CLAUDE.local.md at the repo root and gitignore it. Any downside to doing that?

## R1

## Think tank (solo): CLAUDE.local.md alongside AGENTS.md
opus · session effort · one panelist

### Recommendation
Yes, there's a real downside. Under the default setting (`claude-md-or-agents-md`), Claude Code reads `AGENTS.md` only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it. Adding a root `CLAUDE.local.md` would quietly stop the team's `AGENTS.md` from loading in your sessions. You'd get your personal notes and lose the shared instructions. There are two fixes:

- **Import it (preferred for one repo):** start the gitignored `CLAUDE.local.md` with `@AGENTS.md`, then add your notes. This works under the default mode, needs no global setting, and still works in sessions where `AGENTS.md` support isn't active.
- **Change the setting:** set **Project instructions** to `claude-md-and-agents-md` in `/config`, or under `pluginConfigs."cc-plugin-agents-md@builtin".options.instructionFiles` in `~/.claude/settings.json`. Claude Code ignores this entry in project or local settings files. This is the better fix if the repo has nested `AGENTS.md` files. But it applies to every repo you work in, so repos with both a `CLAUDE.md` and an `AGENTS.md` will start loading both.

Two smaller points. `CLAUDE.local.md` isn't deprecated. A gitignored one exists only in the worktree where you created it, so if you use several worktrees, import a file from `~/.claude/` instead. Afterwards, run `/context` or `/memory` to confirm `AGENTS.md` is loading.

Checked: I read https://code.claude.com/docs/en/memory today and it confirms the panelist on every point:
- **Default rule:** `AGENTS.md` loads only "when you have no `CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it."
- **Your exact case:** the docs say, "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you."
- **Fix and setting location:** the docs give `claude-md-and-agents-md` as the fix and say the setting is read only from `~/.claude/settings.json`, a `--settings` file or managed settings.
- **No double loading:** an `AGENTS.md` that has already been loaded is skipped, so importing it won't load it twice.
- **Worktrees:** the caveat is documented.
- **Not checked:** the docs don't explicitly say that `@` imports work inside `CLAUDE.local.md`. They only say it is "treated the same way" as `CLAUDE.md`. The panelist also flagged this.

### Panelist
"Yes, there is a concrete downside, and it's documented. Under the default setting, any `CLAUDE.local.md` in the working directory or above it makes Claude Code stop reading `AGENTS.md` at all. Adding the file as planned would quietly drop the team's instructions from every session. The plan works if the user either (a) starts `CLAUDE.local.md` with an `@AGENTS.md` import, or (b) sets **Project instructions** to `claude-md-and-agents-md` in their user settings." High confidence on the downside, medium on which alternative is better.

### My take
This matches my leaning at launch about the fallback, so the panelist didn't move me there, and the docs settle it. It did correct my other guess: `CLAUDE.local.md` isn't deprecated. I'd go with the `@AGENTS.md` import. It keeps the change inside the one repo where you need it, and it doesn't depend on a global setting you might forget you changed. Either way, check `/context` once afterwards. The failure is silent: nothing errors, Claude just stops following the team's rules. I haven't changed any settings or files.

## R2

Yes, there's one real downside: **adding a `CLAUDE.local.md` makes Claude Code stop reading your `AGENTS.md`.** By default it reads `AGENTS.md` only when there's no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in your working directory or any folder above it. A `CLAUDE.local.md` counts for that check, even though it's gitignored. So you'd get your personal notes and lose the team instructions. The docs warn about this exact case: "adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you."

**Fixes (pick one):**

1. **Import it.** Put `@AGENTS.md` on the first line of `CLAUDE.local.md`, then your personal notes below it. This works per-repo and also covers sessions that can't read `AGENTS.md` directly.
2. **Change the setting.** Set **Project instructions** to `claude-md-and-agents-md` in `/config`, or add this to `~/.claude/settings.json`:
   ```json
   { "pluginConfigs": { "cc-plugin-agents-md@builtin": { "options": { "instructionFiles": "claude-md-and-agents-md" } } } }
   ```
   It's only read from user, `--settings` or managed settings, not project settings, so it applies to every repo you open. Before v2.1.285 the key was `agents-md@builtin`. If you also do option 1, `AGENTS.md` still won't load twice.

**Smaller points:**
- **Worktrees:** a gitignored `CLAUDE.local.md` only exists in the worktree where you created it. If you use several worktrees, keep your notes in a file in your home directory and import that instead.
- **Load order:** `CLAUDE.local.md` is added after the other instructions for that folder, so Claude reads your notes last there. That's usually what you want.
- **To check it worked:** run `/memory` and look for `AGENTS.md` in the list. Run `/context` to see which instruction files loaded.

**What I verified** against the current official page (code.claude.com/docs/en/memory, fetched today):
- `CLAUDE.local.md` at the project root is supported, documented for personal per-project preferences, and the docs say to gitignore it.
- `CLAUDE.local.md` counts toward the "no CLAUDE.md" check, so it turns off `AGENTS.md` loading. This includes the quoted warning and the fix through the setting.
- The setting's values, the JSON key, which settings files it's read from, and the plugin ID change at v2.1.285.
- Reading `AGENTS.md` directly needs v2.1.277 or later. Before v2.1.281 some sessions, such as Bedrock or telemetry disabled, couldn't read it at all.
- The worktree caveat, the load order, and how to check with `/memory` and `/context`.

**Not verified directly:** the docs show the `@AGENTS.md` import inside a `CLAUDE.md`, not inside `CLAUDE.local.md`. They do say `CLAUDE.local.md` "is treated the same way" as `CLAUDE.md`, so option 1 should work, but that's my inference. Check with `/memory` after you set it up. I also didn't look at your repo, since it isn't in this directory.

## R3

Yes, there's one real downside. With default settings, adding `CLAUDE.local.md` makes Claude Code stop reading your `AGENTS.md`. Your personal file would load and the team's instructions would quietly drop out of context.

**Why:** The default **Project instructions** mode is `claude-md-or-agents-md`. In that mode Claude reads `AGENTS.md` only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in your working directory or any directory above it. A `CLAUDE.local.md` counts. The docs warn about exactly your setup: adding one "stops Claude from reading `AGENTS.md` for you."

**Fixes (pick one):**
1. **Change the mode to read both.** Run `/config` and set **Project instructions** to `claude-md-and-agents-md`. You can also set it in `~/.claude/settings.json` under `pluginConfigs` → `cc-plugin-agents-md@builtin`. It's ignored in project and local settings files, so it has to go in your user settings, which is fine for a personal preference. In this mode each directory's CLAUDE files load first, then its `AGENTS.md`, and a file already loaded isn't read twice.
2. **Import `AGENTS.md` from your local file.** Put `@AGENTS.md` at the top of `CLAUDE.local.md`, then your own notes below it. This works under any mode, including sessions where direct `AGENTS.md` support is unavailable.

**Smaller things to know:**
- **Worktrees:** a gitignored `CLAUDE.local.md` only exists in the worktree where you created it. If you use several worktrees, the docs suggest importing a file from your home directory instead, e.g. `@~/.claude/my-project-instructions.md`. The first time, Claude Code asks you to approve that external import.
- **Order:** within a directory, `CLAUDE.local.md` loads after `CLAUDE.md`, so your notes are the last thing Claude reads at that level.
- **Gitignore:** Claude Code doesn't add it to `.gitignore` for you unless you use `/init`'s personal option with `CLAUDE_CODE_NEW_INIT=1` set, so add the line yourself as you planned.
- **Checking:** run `/memory` and confirm both `CLAUDE.local.md` and `AGENTS.md` are listed.

**What I verified:** everything above comes from the current official page, https://code.claude.com/docs/en/memory, fetched today. That includes the default mode and what counts toward the `AGENTS.md` check, the explicit warning about `CLAUDE.local.md`, the `claude-md-and-agents-md` setting and where it can be set, the `@AGENTS.md` import, the worktree caveat and home-directory alternative, the load order, and the `/init` gitignore behavior. The docs also say reading `AGENTS.md` directly needs v2.1.277 or later.

**Not verified:** the docs don't say whether `@AGENTS.md` inside `CLAUDE.local.md` behaves exactly like an import from `CLAUDE.md`. They do say `CLAUDE.local.md` is "treated the same way" as `CLAUDE.md`, so I'd expect it to work, but check with `/memory`. I also didn't test anything against your repo, since it isn't in this directory.

## R4

**Position:** Yes, there is a concrete downside, and it's documented. Under the default setting, any `CLAUDE.local.md` in the working directory or above it makes Claude Code stop reading `AGENTS.md` at all. Adding the file as planned would quietly drop the team's instructions from every session. The plan works if the user either (a) starts `CLAUDE.local.md` with an `@AGENTS.md` import, or (b) sets **Project instructions** to `claude-md-and-agents-md` in their user settings.

**Reasoning (verified in the current docs at https://code.claude.com/docs/en/memory, fetched 2026-10-20):**
- Since v2.1.277, a built-in plugin (`cc-plugin-agents-md@builtin`) reads `AGENTS.md` directly. That's why the user's repo works today with no `CLAUDE.md`.
- The default mode is `claude-md-or-agents-md`. The docs say `AGENTS.md` loads "when you have no `CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it." A `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` all count for that check. `~/.claude/CLAUDE.md`, the managed `CLAUDE.md` and `.claude/rules/` files do not.
- The docs warn about exactly this plan: "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you." Their fix is to set **Project instructions** to `claude-md-and-agents-md`. You can do that in `/config`, or in `~/.claude/settings.json` under `pluginConfigs."cc-plugin-agents-md@builtin".options.instructionFiles`. Project and local settings files ignore this entry. Before v2.1.285 the plugin ID was `agents-md@builtin`.
- `CLAUDE.local.md` is not deprecated. It is documented as the "Local instructions" tier and is appended after `CLAUDE.md` in each directory. One more caveat from the docs: a gitignored `CLAUDE.local.md` exists only in the worktree where you created it. To share personal notes across worktrees, import a file from `~/.claude/` instead.
- In sessions where `AGENTS.md` support is unavailable, Claude reads only `CLAUDE.md` files. That covers versions before v2.1.277, the plugin being disabled, and sometimes the first session after upgrading from v2.1.276 or earlier. In those sessions an import is the only thing that works.

**Recommendation (my inference, not stated in the docs):** For this one repo, the most robust option is a gitignored `CLAUDE.local.md` that begins with `@AGENTS.md` and then adds the personal notes. It works under the default mode, needs no global setting, and still works in sessions without the plugin. The docs say an `AGENTS.md` that has already been loaded is skipped, so it isn't read twice if the user later switches modes.

The settings change is cleaner if the repo has nested `AGENTS.md` files in subdirectories, because a root import covers only the root file. The trade-off is that it applies to every repo the user works in, so repos that have both a `CLAUDE.md` and an `AGENTS.md` will start loading both.

**Risks and unknowns:**
- The docs don't explicitly confirm that `@` imports inside `CLAUDE.local.md` work. They say it is "treated the same way" as `CLAUDE.md`, so I expect they do.
- I'm also inferring that a root `CLAUDE.local.md` suppresses subdirectory `AGENTS.md` loading under the default mode.
- My position depends on the user's version being v2.1.277 or later, which I take as given since `AGENTS.md` loads today. This behaviour has changed several times (v2.1.277, 2.1.280, 2.1.281, 2.1.285), so it could change again.
- After the change, verify it: `/memory` should list `AGENTS.md`, or `/context` should show the imported content.

**Confidence:** High on the downside, which the docs describe almost word for word for this scenario. Medium on which alternative is better, since that depends on the repo's layout and how the user works.

## R5

Yes, there's a real downside. **By default, adding a `CLAUDE.local.md` makes Claude Code stop reading your `AGENTS.md`.** You'd get only your personal notes and lose the team instructions, and nothing warns you about it.

**Why:** Claude Code reads `AGENTS.md` only when there's no `CLAUDE.md` file in your working directory or any folder above it. `CLAUDE.local.md` counts as one of those files, along with `CLAUDE.md` and `.claude/CLAUDE.md`. The docs call out your exact case: adding a `CLAUDE.local.md` "in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you."

**Fixes (pick one):**

1. **Import `AGENTS.md` from your local file.** Put this at the top of `CLAUDE.local.md`:
   ```
   @AGENTS.md

   # My personal notes
   ...
   ```
   This affects only this repo and changes no settings. Because the path stays inside the repo, you shouldn't get the approval prompt that imports from outside the project trigger.
2. **Change the "Project instructions" setting to `claude-md-and-agents-md`.** You can do this in `/config`, or in `~/.claude/settings.json` under `pluginConfigs` → `cc-plugin-agents-md@builtin` → `options.instructionFiles`. Claude Code ignores this entry in project and local settings files, so it can only be set per user, and it then applies to every repo you work in. Any repo that has both a `CLAUDE.md` and an `AGENTS.md` will then load both, which may not be what you want there.

I'd go with option 1. Either way, run `/memory` or `/context` afterwards to confirm `AGENTS.md` still loads.

**Smaller things to know:**
- A gitignored `CLAUDE.local.md` exists only in the worktree where you created it. If you use several git worktrees, the docs suggest importing a file from your home folder (e.g. `@~/.claude/my-project-instructions.md`). That import triggers a one-time approval prompt.
- Within each folder, `CLAUDE.local.md` loads after `CLAUDE.md`, so your notes are the last thing Claude reads at that level.

**What I checked in the current docs (code.claude.com/docs/en/memory):**
- `CLAUDE.local.md` at the repo root is supported and is the recommended place for personal, gitignored instructions.
- It counts against reading `AGENTS.md`, under the default setting `claude-md-or-agents-md`. The docs include an explicit note about this.
- The `claude-md-and-agents-md` value exists, along with its settings key, and it's ignored in project and local settings files.
- The worktree caveat, the home-folder import alternative, and the approval prompt for outside imports.
- Reading `AGENTS.md` directly requires v2.1.277 or later, which matches what you're seeing.

**Not checked directly:** the docs show `@AGENTS.md` imports inside a `CLAUDE.md`, not a `CLAUDE.local.md`. I'm relying on the docs saying `CLAUDE.local.md` is "treated the same way" as `CLAUDE.md`. I also haven't looked at your repo, since it isn't in this directory, so `/memory` is the way to confirm.

Source: [How Claude remembers your project](https://code.claude.com/docs/en/memory)

## R6

## Think tank (solo): CLAUDE.local.md in an AGENTS.md repo
opus · session effort · one panelist

### Recommendation
There is a downside, and it matters. Under the default setting, Claude Code reads `AGENTS.md` only when there's no `CLAUDE.md` or `CLAUDE.local.md` in your working directory or any directory above it. Adding a `CLAUDE.local.md` would therefore make Claude stop reading the team's `AGENTS.md`, without any warning, and read only your personal file. You can still add the file, but you need one of these alongside it:

1. **Global setting:** in `/config`, set **Project instructions** to `claude-md-and-agents-md`. This is the fix the docs give. It can only be set in `~/.claude/settings.json` (under `pluginConfigs` → `cc-plugin-agents-md@builtin`), a `--settings` file, or managed settings. Project and local settings files ignore it, so it applies to every repo you open.
2. **Per repo:** make `@AGENTS.md` the first line of your `CLAUDE.local.md`. `CLAUDE.local.md` is "treated the same way" as `CLAUDE.md`, so the import should work there too.
3. **Avoid the trigger:** keep the notes in `~/.claude/CLAUDE.md`, which doesn't count toward the check. This only fits if the notes aren't specific to this repo.

The panelist also raised two smaller points:
- Committing a `.gitignore` entry is visible to the team. `.git/info/exclude` keeps it completely private.
- A gitignored `CLAUDE.local.md` exists only in the worktree where you created it.

To confirm the fix worked, check that `AGENTS.md` appears under Memory files in `/context`.

Checked:
- **The fallback rule:** the official memory page (code.claude.com/docs/en/memory) states it exactly that way. It even warns about this plan: "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you." It gives `claude-md-and-agents-md` as the fix.
- **Not gitignored automatically:** confirmed. You add `CLAUDE.local.md` to `.gitignore` yourself, unless you run `/init` with `CLAUDE_CODE_NEW_INIT=1` and choose the personal option.
- **Where the setting is read:** confirmed. One extra detail: before v2.1.285 the plugin ID was `agents-md@builtin`.
- **Nested `AGENTS.md` with the import approach:** the panelist wasn't sure about this. The docs answer it: a subdirectory's `AGENTS.md` loads on demand only "when none count", meaning no `CLAUDE.md`-type file on the path. A root `CLAUDE.local.md` would probably stop nested `AGENTS.md` files from loading even with `@AGENTS.md` in it.

### Panelist
"Do something else, or at least add one more step. Under the default setting, a `CLAUDE.local.md` anywhere in the working directory or above it makes Claude Code stop reading `AGENTS.md`. The user's personal file would quietly replace the team's instructions instead of adding to them. Add the file, but either make `@AGENTS.md` its first line or change the **Project instructions** setting to `claude-md-and-agents-md`." High confidence. The only medium-confidence point was how nested `AGENTS.md` files behave with the import approach.

### My take
At launch I leaned toward "probably fine, but check the fallback rule". The fallback rule turned out to be the whole story, so the panelist confirmed my concern rather than changing my view. Where I differ is the order of the fixes. I'd use the global `claude-md-and-agents-md` setting rather than the `@AGENTS.md` import:
- The import probably doesn't bring back nested `AGENTS.md` files.
- The import puts a manual step in each repo, which is easy to forget.
- The global setting does exactly what you want, which is both files together. Its only cost is that it also applies to repos that have both files, which is usually what you'd want anyway.

All of this rests on the fallback rule I confirmed in the docs, so I'm confident in the conclusion. One note: the panelist's report suggests editing `~/.claude/settings.json`. That's advice for you to apply if you choose to; I haven't changed anything.

## R7

## Think tank (solo): CLAUDE.local.md next to AGENTS.md
opus · session effort · one panelist

### Recommendation
Yes, there's a real downside. By default, Claude Code reads `AGENTS.md` only when there's no `CLAUDE.md` or `CLAUDE.local.md` in the working directory or any directory above it. A `CLAUDE.local.md` counts for that check. So as soon as you add one, Claude reads your personal notes but stops reading the team's `AGENTS.md`, and nothing warns you.

There are two fixes:
- **Import it in your local file:** make `@AGENTS.md` the first line of `CLAUDE.local.md`, then put your personal notes below it. This works on any version or setting, including sessions where Claude can't read `AGENTS.md` directly.
- **Change the setting:** set **Project instructions** to `claude-md-and-agents-md` through `/config`, or in `~/.claude/settings.json` under `pluginConfigs."cc-plugin-agents-md@builtin".options.instructionFiles`. This setting is ignored in project and local settings files, so it applies to all your projects. Choose this one if the repo also has `AGENTS.md` files in subdirectories.

Other points it raised:
- A gitignored `CLAUDE.local.md` only exists in the worktree where you created it. If you use several worktrees, keep your notes in a file under `~/.claude/` and import that file from `CLAUDE.local.md`.
- Adding `CLAUDE.local.md` to `.gitignore` is itself a change that gets committed. To keep even that private, list it in `.git/info/exclude` instead.
- Afterwards, run `/context` and check that both files appear under Memory files.

Checked: I read the official docs at code.claude.com/docs/en/memory today.
- **The default fallback rule:** confirmed. The docs say `CLAUDE.local.md` is one of the files that count, and they describe your exact case: "adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you." Their suggested fix is the `claude-md-and-agents-md` setting.
- **The import fix:** confirmed. The docs list "a `CLAUDE.md` that imports `AGENTS.md`" as a supported setup, and the "and" mode skips an `AGENTS.md` that's already loaded, so it won't load twice.
- **Settings location:** confirmed. The setting is read from `~/.claude/settings.json`, a `--settings` file or managed settings, and ignored in project and local settings files.
- **Subdirectory `AGENTS.md` files (the panelist didn't verify this):** the docs back it up. They load only when none of the counting files exist, so a root `CLAUDE.local.md` blocks them too.

### Panelist
"Yes, the plan has a real downside. With default settings, adding `CLAUDE.local.md` makes Claude Code stop loading `AGENTS.md`. The user would get their personal notes but lose the team's instructions, and nothing warns them. The fix is small: put `@AGENTS.md` as the first line of `CLAUDE.local.md`, or switch the "Project instructions" setting to `claude-md-and-agents-md`." High confidence.

### My take
Before the panelist answered, I suspected this fallback problem but wasn't sure. The panelist's answer and the docs confirm it, so my view didn't change; I'm now more confident. I'd go with `@AGENTS.md` at the top of `CLAUDE.local.md`. It keeps the fix inside the one file you were going to add anyway, and it works whatever the setting or version. Use the user-level setting instead if the repo has `AGENTS.md` files in subdirectories, since the import only brings back the root file. Either way, it's quick to check with `/context`.

## R8

**Position:** Yes, the plan has a real downside. With default settings, adding `CLAUDE.local.md` makes Claude Code stop loading `AGENTS.md`. The user would get their personal notes but lose the team's instructions, and nothing warns them. The fix is small: put `@AGENTS.md` as the first line of `CLAUDE.local.md`, or switch the "Project instructions" setting to `claude-md-and-agents-md`.

**Reasoning (checked against https://code.claude.com/docs/en/memory, fetched today):**
- **How `AGENTS.md` loads now.** Since v2.1.277, a built-in plugin reads `AGENTS.md` directly. The default mode is `claude-md-or-agents-md`. That is why the user's current setup works: the repo has no `CLAUDE.md`.
- **Why it breaks.** That default is a fallback, used only when there is "no `CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it." The docs list `CLAUDE.local.md` as a file that counts, so Claude "reads them instead of `AGENTS.md`." The docs even describe this exact case: "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you." Only `~/.claude/CLAUDE.md`, the managed `CLAUDE.md` and `.claude/rules/` files don't count.
- **`CLAUDE.local.md` is still supported.** It is listed as "Local instructions," loads alongside `CLAUDE.md`, and the docs tell you to add it to `.gitignore`. Mechanisms 1 and 3 in the brief hold; mechanism 2 does not.
- **Fix A: import inside the local file.** Start `CLAUDE.local.md` with `@AGENTS.md`, then add personal notes below it. This works on any version and setting, including sessions where direct `AGENTS.md` loading isn't available (older than v2.1.277, plugin disabled, the first session after an upgrade). The import is inside the repo, so there is no approval prompt for external imports, and a later switch to the "and" mode won't load it twice.
- **Fix B: change the setting.** Set Project instructions to `claude-md-and-agents-md` via `/config`, or in `~/.claude/settings.json` under `pluginConfigs."cc-plugin-agents-md@builtin".options.instructionFiles`. The docs say project and local settings files ignore this entry, so it applies to all of the user's projects. Choose this if the repo has `AGENTS.md` files in subdirectories. My inference (not verified): a root `CLAUDE.local.md` also stops those from loading by default, and Fix A only brings back the root file.

**Practical issues:**
- **Worktrees and other clones.** The docs confirm a gitignored `CLAUDE.local.md` exists only in the worktree where you created it. If the user works across worktrees, keep the notes in `~/.claude/my-project.md` and make `CLAUDE.local.md` just `@AGENTS.md` plus `@~/.claude/my-project.md`. The home-directory import triggers a one-time approval dialog. If you decline it, it stays disabled.
- **Gitignore.** Adding `CLAUDE.local.md` to `.gitignore` is itself a change you commit. To keep it fully private, use `.git/info/exclude`, which is per clone.
- **`~/.claude/CLAUDE.md`.** It doesn't block `AGENTS.md`, but it applies to every project, so it only suits instructions that aren't specific to this repo.

**Recommended setup:** gitignored (or excluded) `CLAUDE.local.md` containing `@AGENTS.md`, then personal notes. Add the user-level `claude-md-and-agents-md` setting if there are nested `AGENTS.md` files. Then run `/memory` or `/context` and confirm both files are listed.

**Risks and unknowns:** Everything depends on the current docs' fallback rule. The quoted behaviour is new (v2.1.277–2.1.285) and may change. If the user is on an older version, `AGENTS.md` loading comes from something else, such as a SessionStart hook, and the conflict may not happen; but then their "it works" observation needs explaining. I did not test the nested-`AGENTS.md` behaviour.

**Confidence:** High. The official docs state this exact scenario and its fix almost word for word.

## R9

**Position:** Do something else, or at least add one more step. Under the default setting, a `CLAUDE.local.md` anywhere in the working directory or above it makes Claude Code stop reading `AGENTS.md`. The user's personal file would quietly replace the team's instructions instead of adding to them. Add the file, but either make `@AGENTS.md` its first line or change the **Project instructions** setting to `claude-md-and-agents-md`.

**Reasoning:**
- The official memory page (https://code.claude.com/docs/en/memory, "AGENTS.md" section) says Claude Code reads `AGENTS.md` itself through a built-in plugin (`cc-plugin-agents-md@builtin`, v2.1.277 or later). That's why the user's setup works with no `CLAUDE.md`.
- The default mode, `claude-md-or-agents-md`, reads `AGENTS.md` only "when you have no `CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it." The page says `CLAUDE.local.md` counts for that check. `~/.claude/CLAUDE.md`, managed `CLAUDE.md` and `.claude/rules/` don't.
- The docs warn about this exact plan: "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you." The troubleshooting section "My AGENTS.md isn't loading" names a stray `CLAUDE.md`/`CLAUDE.local.md` as the usual cause.
- `CLAUDE.local.md` itself is fully supported and not deprecated. It loads after `CLAUDE.md` in the same directory. It is **not** gitignored automatically: you add it to `.gitignore` yourself, unless you use `/init` with `CLAUDE_CODE_NEW_INIT=1` and pick the personal option. So the plan is sound apart from the `AGENTS.md` problem.

**What to do (pick one):**
1. **Per repo:** put `@AGENTS.md` at the top of `CLAUDE.local.md`, with the personal notes below it. The docs say `CLAUDE.local.md` is "treated the same way" as `CLAUDE.md`, and imports work there, so the shared instructions come back through the import.
2. **Globally:** set **Project instructions** to `claude-md-and-agents-md` in `/config`, or under `pluginConfigs` in `~/.claude/settings.json`. Claude Code ignores this setting in project and local settings files, so it applies to every repo. Repos that have both files would then load both.
3. **Avoid the trigger entirely:** keep the personal notes in a file under the home directory. That fits only if they apply everywhere or can be written generally.

**Smaller caveats:**
- Adding `CLAUDE.local.md` to `.gitignore` is itself a change the team sees when committed. `.git/info/exclude` keeps it fully private.
- A gitignored `CLAUDE.local.md` exists only in the worktree where it was created. The docs suggest importing a file from the home directory to share it across worktrees.
- To check it worked, run `/memory` or `/context` and look for the `AGENTS.md` path. Once a `CLAUDE.local.md` exists, the startup line "no CLAUDE.md found; AGENTS.md loaded" will no longer appear.

**Risks and unknowns:**
- My position rests on the documented default (`claude-md-or-agents-md`) and on `CLAUDE.local.md` counting toward the check. Both are stated plainly in current docs. A future version could change either.
- If the user has already changed **Project instructions**, or is on a version or session type where `AGENTS.md` isn't read directly, the details differ. In the second case it would have to be working through an import already.
- With the per-repo import, I haven't confirmed whether nested `AGENTS.md` files in subdirectories still load on demand. The docs tie that to the same "no `CLAUDE.md`" condition, so they may stop. If the repo has nested `AGENTS.md` files, the global setting is safer.

**Confidence:** High. The official docs describe this exact situation and give the same fix. The only medium-confidence point is how nested `AGENTS.md` files behave with the import approach.
