# local-md-agents

Question asked:

> Our repo keeps its agent instructions in AGENTS.md and has no CLAUDE.md, and Claude Code picks AGENTS.md up fine. I want some personal instructions I don't commit, so I'm going to add a CLAUDE.local.md at the repo root and gitignore it. Any downside to doing that?

## R1

**Position:** Don't do it as planned. Creating `CLAUDE.local.md` in a repo that has only `AGENTS.md` makes Claude Code stop loading `AGENTS.md`. Either put `@AGENTS.md` at the top of the `CLAUDE.local.md`, or put the personal instructions in `~/.claude/CLAUDE.md` or in a file under `~/.claude/` that you import.

**Reasoning (all verified in the current memory docs, code.claude.com/docs/en/memory, sections "AGENTS.md" and "How CLAUDE.md files load"):**
- **Default rule:** by default Claude reads `AGENTS.md` only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or any directory above it. `~/.claude/CLAUDE.md`, managed CLAUDE.md and `.claude/rules/` don't count and still load alongside `AGENTS.md`.
- **Why the plan backfires:** the docs say this directly in a Note: "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you."
- **What the user would see:** the team's instructions disappear from their sessions, with no error. The only symptom is that Claude ignores the project conventions. `/memory` or `/context` would show it.
- **Why the user's current setup works:** the "AGENTS.md just works" behaviour is a native feature that needs v2.1.277 or later. Before v2.1.281, some sessions (Bedrock, or telemetry disabled) read only `CLAUDE.md` files.
- **`AGENTS.local.md` doesn't help:** the docs list `AGENTS.local.md`, `AGENTS.override.md` and `.agents/` as not read.
- **The `.gitignore` part is fine:** the docs recommend gitignoring `CLAUDE.local.md`, and it loads after `CLAUDE.md` at the same level.

**Alternatives, best first:**
1. **`~/.claude/CLAUDE.md`** works if the instructions are personal but not tied to this repo. It doesn't count as a project file, so `AGENTS.md` keeps loading. It applies to all projects, so keep the content general.
2. **`CLAUDE.local.md` with `@AGENTS.md` as its first line**, then the personal notes. The docs describe this import pattern for `CLAUDE.md`. Imports in a `CLAUDE.local.md` should work the same, since it is "treated the same way" as `CLAUDE.md`, but the docs don't state that outright (inferred). It keeps repo-specific personal notes in the repo and keeps `AGENTS.md` loading. Check with `/memory` or `/context`.
3. **Set Project instructions to `claude-md-and-agents-md`** (via `/config`, or `pluginConfigs` → `cc-plugin-agents-md@builtin` → `instructionFiles` in `~/.claude/settings.json`). Both files then load, and an already-imported `AGENTS.md` isn't read twice. This setting is read only from user, `--settings` or managed settings, not project settings, so it has to be configured per user.
4. **Cross-worktree sharing:** a gitignored `CLAUDE.local.md` exists only in the worktree where it was created. The docs suggest putting the content in a home-directory file and importing it, e.g. `@~/.claude/my-project-instructions.md`. The first external import in a project triggers a one-time approval dialog. If declined, the import stays disabled and the dialog doesn't reappear.

**Other downsides:**
- Option 2 or 3 differs slightly from native `AGENTS.md` loading. `InstructionsLoaded` hooks don't fire for an `AGENTS.md` read through the setting, but they do for one loaded by import.
- Option 2 means `AGENTS.md` is no longer read natively. It is read through the import, so it also works on the older or Bedrock sessions that can't read `AGENTS.md` directly.
- A `CLAUDE.local.md` in a parent directory also counts, so a stray one higher up has the same effect.

**Risks and unknowns:**
- The docs are for recent versions (v2.1.277 and later). If the user runs an older version, the behaviour differs. I haven't tested anything live.
- I haven't confirmed that `@` imports are expanded inside `CLAUDE.local.md` specifically.
- If the user already has the `claude-md-and-agents-md` setting, the downside disappears.

**Confidence:** high. The docs state this exact scenario in a Note.

**Position:** Don't add a bare `CLAUDE.local.md`. Start it with `@AGENTS.md`, use `~/.claude/CLAUDE.md`, or set Project instructions to `claude-md-and-agents-md`. The fact my position depends on most is that `CLAUDE.local.md` counts as a CLAUDE file for the AGENTS.md fallback check.

## R2

**Position:** Fine with caveats. Don't add a bare `CLAUDE.local.md`. By default, creating one makes Claude Code stop reading `AGENTS.md` entirely. Either start the file with an `@AGENTS.md` import, or set Project instructions to `claude-md-and-agents-md`.

**Reasoning (verified in https://code.claude.com/docs/en/memory, fetched today):**
- **The main downside.** The default Project instructions mode is `claude-md-or-agents-md`. It reads `AGENTS.md` "only when you have no `CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it." The docs list `CLAUDE.local.md` as a file that counts, and they call out this exact case: "adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you." This happens every time on the default setting. The user would keep their personal notes and silently lose the team instructions. Nothing errors. The only sign is that the "AGENTS.md loaded" line no longer appears, and `/memory` no longer lists the file.
- **Fix A, per repo (my recommendation).** Put `@AGENTS.md` on the first line of `CLAUDE.local.md` and the personal notes below it. The docs describe this import pattern for a `CLAUDE.md`, and a `CLAUDE.local.md` "is treated the same way." The import also works in sessions that can't read `AGENTS.md` directly, which the docs list as: the built-in plugin disabled, sometimes the first session after upgrading, and older versions on Bedrock or with telemetry off. Within each directory, `CLAUDE.local.md` is read last, so personal notes come after the team rules. The target is inside the repo, so there's no approval prompt for an external import.
- **Fix B, a setting.** Set `pluginConfigs."cc-plugin-agents-md@builtin".options.instructionFiles` to `"claude-md-and-agents-md"` (or use `/config`). The catch is that it's only honoured in `~/.claude/settings.json`, a `--settings` file or managed settings. Project and local settings files ignore it, so it changes every repo. Any repo that has both a `CLAUDE.md` and an `AGENTS.md` will then load both, which may not be what the user wants. Requires v2.1.277 or later. Before v2.1.285 the plugin ID was `agents-md@builtin`.
- **Worktrees caveat (verified).** A gitignored `CLAUDE.local.md` exists only in the worktree where it was created. If the user works across several worktrees, the docs recommend importing a home-directory file instead, such as `@~/.claude/my-project-instructions.md`. That import triggers a one-time approval dialog. If the user declines it, the import stays disabled.

**Inferred, not documented:**
- With Fix A, other `AGENTS.md` files may stop loading too: ones in parent directories, and ones in subdirectories that would otherwise load on demand. The import only brings in the root file, and I think the root `CLAUDE.local.md` turns off direct `AGENTS.md` reading everywhere below it. The docs don't state that last part explicitly. If the repo has nested `AGENTS.md` files, use Fix B instead.
- A gitignored file under `.claude/rules/` might be a clean third option. The docs do say rules files don't count, so they load alongside `AGENTS.md`. But I didn't check how rules interact with `.gitignore`.
- `.git/info/exclude` would keep the ignore entry out of the committed `.gitignore`. That's a small point about git hygiene, not a Claude Code behaviour.

**Risks and unknowns:** My position rests mostly on the documented rule that `CLAUDE.local.md` counts as a `CLAUDE.md` for the `AGENTS.md` check. That is version-specific: the feature arrived around v2.1.277 and has changed since (the ID rename at v2.1.285, listing fixes at v2.1.280). A later release could change it. The user's own install would show which applies: after adding the file, run `/memory` or `/context` and check whether `AGENTS.md` is still listed. If it is, the plan is fine as it stands.

**Confidence:** High. The docs describe this exact scenario in a dedicated note. Confidence is lower on the nested-`AGENTS.md` and `.claude/rules/` points, which are my inference.

## R3

Yes, there's one real downside: **adding a `CLAUDE.local.md` makes Claude Code stop loading your `AGENTS.md`.** I checked the current Claude Code memory docs (code.claude.com/docs/en/memory).

Claude Code only reads `AGENTS.md` when it finds no `CLAUDE.md` file in your working directory or any directory above it. A `CLAUDE.local.md` counts as one, and so do `CLAUDE.md` and `.claude/CLAUDE.md`. From the docs:

> | An `AGENTS.md` and a `CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it | Your `CLAUDE.md` files only |

So once you add the file, your sessions would get your personal notes and none of the shared project instructions. Nothing errors, so it's easy to miss.

**Fixes** (pick one):

1. **Import AGENTS.md from your local file.** Put this line at the top of `CLAUDE.local.md`:
   ```
   @AGENTS.md
   ```
   Then add your personal instructions below it. This is the simplest option and only affects you.

2. **Change the setting so both files load.** In `/config`, set **Project instructions** to `claude-md-and-agents-md`. Or put this in `~/.claude/settings.json` (Claude Code ignores this key in project and local settings files):
   ```json
   {
     "pluginConfigs": {
       "cc-plugin-agents-md@builtin": {
         "options": { "instructionFiles": "claude-md-and-agents-md" }
       }
     }
   }
   ```
   This applies to every repo you open, and Claude Code won't load an `AGENTS.md` twice if you also import it.

3. **Skip the repo file.** If your notes aren't specific to this repo, put them in `~/.claude/CLAUDE.md`. That file loads alongside `AGENTS.md`, so nothing changes. The catch is that it applies to all your projects.

To check that it's working, start an interactive session in the repo and run `/memory` to see which instruction files loaded. If Claude Code is using the `AGENTS.md` fallback, the session also shows a line like `no CLAUDE.md found; AGENTS.md loaded: ...`.

Gitignoring `CLAUDE.local.md` is fine. Two smaller points: reading `AGENTS.md` directly needs Claude Code v2.1.277 or later, and `AGENTS.local.md` isn't read, so you can't use that name for personal notes instead.

## R4

## Think tank: CLAUDE.local.md alongside AGENTS.md
opus, sonnet, sonnet · session effort · identical brief · debate

### Recommendation (3–0)
Don't add a bare `CLAUDE.local.md`. With the default setting, its existence makes Claude Code stop reading `AGENTS.md`. Nothing tells you this happened. You'd keep your personal notes and quietly lose the team's instructions. All three panelists give the same two fixes:
- **Per repo:** make `@AGENTS.md` the first line of `CLAUDE.local.md`, with your notes below it.
- **For your user account:** set **Project instructions** to `claude-md-and-agents-md`. A and B add that you should use this setting if the repo has nested `AGENTS.md` files.

Afterwards, run `/context` to confirm that `AGENTS.md` still loads.

Checked: I fetched code.claude.com/docs/en/memory.
- **The main claim is confirmed word for word.** The default `claude-md-or-agents-md` reads `AGENTS.md` only when there is "no `CLAUDE.md` or `CLAUDE.local.md` in your working directory or above it". A Note describes exactly your plan: "Because `CLAUDE.local.md` counts, adding one … stops Claude from reading `AGENTS.md` for you."
- **The setting is confirmed.** The documented key is `pluginConfigs."cc-plugin-agents-md@builtin".options.instructionFiles`. It is honoured only in `~/.claude/settings.json`, a `--settings` file or managed settings, so it applies to every repo you open.
- **The import fix is only implied.** The docs never say outright that `@` imports work inside `CLAUDE.local.md`. They do say it "is treated the same way" as `CLAUDE.md`. Their worktree example puts an `@~/...` import in a `CLAUDE.local.md` setup, which strongly implies imports work there.

### Panel
- **A** (opus): "Fine with caveats. A bare root `CLAUDE.local.md` makes Claude stop reading `AGENTS.md` under the default setting. Put `@AGENTS.md` on its first line and confirm with `/context`. If that doesn't work, or the repo has nested `AGENTS.md` files, set Project instructions to `claude-md-and-agents-md`." Confidence is high on the downside and medium on the import fix. It downgraded the import fix after B pointed out that the fix is inferred, not documented.
- **B** (sonnet): "Don't add a bare `CLAUDE.local.md`. On the default setting, any `CLAUDE.local.md` in or above the working directory silently stops Claude Code from reading `AGENTS.md`. Start the file with `@AGENTS.md`, or set Project instructions to `claude-md-and-agents-md` in user settings. Use that setting if the repo has nested `AGENTS.md` files. If the notes aren't repo-specific, `~/.claude/CLAUDE.md` avoids the problem, because it doesn't count toward the check." Confidence is high on the downside and medium on the import fix. Its position is unchanged; it added the nested-file condition from A.
- **C** (sonnet): "Don't add a bare `CLAUDE.local.md`. Under the default setting it silently stops Claude Code reading `AGENTS.md`. Start the file with `@AGENTS.md`, or set Project instructions to `claude-md-and-agents-md`." Confidence is high on the downside and medium on the fix. It dropped `~/.claude/CLAUDE.md` from first to last place. The reason was A's point that a file in your home directory applies to every project, not just this repo.

Points raised:
- **The silent suppression:** a `CLAUDE.local.md` in or above the working directory stops `AGENTS.md` loading (A, B, C).
- **The import covers more sessions:** `@AGENTS.md` also works where Claude Code can't read `AGENTS.md` directly, such as older versions, Bedrock or telemetry-off sessions before v2.1.281, or a disabled built-in plugin (A, B, C).
- **The setting is global:** it can only go in user-level settings, so it affects every repo. Repos that have both files will load both (A, B, C).
- **Worktrees:** a gitignored file exists only in the worktree where you created it. To share it, import a file from your home directory, which triggers a one-time approval prompt (A, B, C).
- **Nested `AGENTS.md` files may be lost** under the import fix, which is why the setting is preferred for those repos (A → B, C).
- **`~/.claude/CLAUDE.md`** works for notes that aren't specific to this repo (B, C, then accepted by A).
- **`AGENTS.local.md` is not read,** so it isn't an option (B, C).
- **`InstructionsLoaded` hooks** don't fire for an `AGENTS.md` read through the setting (B, C).
- **`.git/info/exclude`** could replace the committed `.gitignore` entry (A, B).
- **A gitignored file under `.claude/rules/`** doesn't count against `AGENTS.md`. Untested (A → B, C).

### Where they split
The only real disagreement was ranking: C first put `~/.claude/CLAUDE.md` at the top, then changed its order in debate. The open question is nested `AGENTS.md` files. The docs list "a subdirectory's `AGENTS.md` … when that subdirectory has none of the three CLAUDE.md files of its own" under the heading "When none count". That supports A's worry: with a root `CLAUDE.local.md`, subdirectory `AGENTS.md` files probably stop loading, and the import only brings back the root one.

### My take
I started out leaning "probably fine", while noting that the fallback might be switched off. The docs settled that: it is switched off, and they describe your exact plan as the trap. For notes specific to this repo, I'd go with the `@AGENTS.md` import if the repo has a single root `AGENTS.md`, and the setting if it has nested ones.

One option the panel only raised in passing deserves more weight: put your notes in a gitignored `.claude/rules/personal.md` instead. The docs explicitly say rules files "don't count" and "keep loading alongside `AGENTS.md`". That means no setting change, no import, and nested `AGENTS.md` files keep working. I haven't confirmed that gitignoring the file has no effect, but `CLAUDE.local.md` is gitignored and still loads. Whichever route you take, check with `/context` that `AGENTS.md` is still listed.

The harness flagged every panelist reply because it contained a settings.json snippet. They were quoting the documented `pluginConfigs` key, which I checked against the docs, and nothing in the replies tried to direct me.

## R5

Yes, there's one big downside: **adding `CLAUDE.local.md` will make Claude Code stop reading your `AGENTS.md`.**

According to the [memory docs](https://code.claude.com/docs/en/memory#agents-md), Claude only reads `AGENTS.md` when it finds no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in your working directory or any directory above it. A `CLAUDE.local.md` counts toward that check. Once you add one, Claude loads your personal file and drops the team's instructions. Nothing errors, so it's easy to miss. The docs call out your exact case in a note.

**Fixes** (pick one):

1. **Import it at the top of `CLAUDE.local.md`.** This is the simplest fix and only affects this repo:
   ```markdown
   @AGENTS.md

   ## My personal notes
   ...
   ```
   Claude reads `AGENTS.md` first, then your notes.

2. **Tell Claude to always read both files.** Run `/config` and set **Project instructions** to `claude-md-and-agents-md`, or put this in `~/.claude/settings.json`:
   ```json
   {
     "pluginConfigs": {
       "cc-plugin-agents-md@builtin": {
         "options": { "instructionFiles": "claude-md-and-agents-md" }
       }
     }
   }
   ```
   This setting is ignored in the project's own settings files, so it has to go in your user settings, and it applies to every project. Before v2.1.285 the ID was `agents-md@builtin`.

**Other things to know:**
- **Git worktrees:** a gitignored `CLAUDE.local.md` only exists in the worktree where you created it. If you use worktrees, keep your notes in a file in your home directory and import that file instead.
- **Your personal instructions win ties:** `CLAUDE.local.md` is loaded after the project instructions, so if the two conflict, yours take priority.
- **Check it worked:** after the change, run `/memory` or `/context` and confirm both `AGENTS.md` and `CLAUDE.local.md` are listed.

Gitignoring the file is the right call either way.

## R6

**Position:** Yes, there is a real downside, and it is the main one. Adding `CLAUDE.local.md` stops Claude Code from reading the repo's `AGENTS.md` for that user. Don't go ahead exactly as planned. Also set **Project instructions** to `claude-md-and-agents-md`, or add a gitignored `CLAUDE.local.md` that starts with `@AGENTS.md`.

**Reasoning:**

All of this comes from the current Claude Code memory docs, https://code.claude.com/docs/en/memory. I fetched them today (2026-10-19) and read the relevant sections directly.

1. **Adding the file changes what loads (verified).**
   - Since v2.1.277, Claude reads `AGENTS.md` natively, but only as a fallback. The default is `claude-md-or-agents-md`.
   - `AGENTS.md` is read only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or any parent.
   - The docs say so explicitly: "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you."
   - After the change, the user's sessions would load only the local file. The shared team instructions would silently go missing.
   - Nothing is wrong with the setup today. The user is right that it works now only because no `CLAUDE*.md` file exists.
   - The failure is quiet. The docs' "My AGENTS.md isn't loading" section lists this as the usual cause.
   - Running `/memory` or `/context` shows what actually loaded.

2. **Fixes (verified).**
   - **Option A:** Run `/config` and set **Project instructions** to `claude-md-and-agents-md`. Files then load together, with `CLAUDE.md` files first and `AGENTS.md` after. This is a per-user setting and touches nothing in the repo. The docs say it is read only from `~/.claude/settings.json`, a `--settings` file or managed settings, and ignored in project settings. It is stored under `pluginConfigs` → `cc-plugin-agents-md@builtin`.
   - **Option B:** Put `@AGENTS.md` as the first line of `CLAUDE.local.md`. The docs describe the import pattern for a committed `CLAUDE.md`. I did not see an example of it in a local file. Imports are expanded in project-level memory files, so it should work, but I have not confirmed it. Also, the docs say the `claude-md-and-agents-md` setting skips an `AGENTS.md` that was already loaded, so the combination is safe.
   - Option B has the advantage of working in sessions that can't read `AGENTS.md` natively, such as versions before v2.1.281 on Bedrock.
   - I'd lean towards Option B if the user wants the least machinery.

3. **Smaller downsides (verified).**
   - **Worktrees:** a gitignored `CLAUDE.local.md` exists only in the worktree where it was created. Other clones behave the same way.
   - The docs suggest keeping the personal content in `~/.claude/my-project-instructions.md` and importing it with `@~/...`. That import triggers a one-time external-import approval dialog.
   - **Gitignore:** `.gitignore` is needed to avoid committing the file. A repo-wide `.gitignore` edit is itself a commit that the team would see. `.git/info/exclude` avoids that.
   - **Other tools:** they are unaffected. Codex, Cursor and similar tools keep reading `AGENTS.md`, and `CLAUDE.local.md` is Claude-only.
   - **Other file names:** `AGENTS.local.md` is not read by Claude Code, so don't use that name.

4. **Status of `CLAUDE.local.md` (verified).** It is still supported and documented as the "Local instructions" scope. I saw no deprecation in the docs. I did not check the changelog or GitHub issues separately.

**Alternative that avoids the problem entirely:** put the personal instructions in `~/.claude/CLAUDE.md`. That file doesn't count toward the check, so `AGENTS.md` still loads alongside it. This only suits preferences that apply across all projects. For project-specific ones, use `CLAUDE.local.md` with `@AGENTS.md` or the `/config` setting.

**Risks and unknowns:**
- This behaviour is new (v2.1.277, September 2026) and may change again. The user's Claude Code version matters. Before v2.1.277, `AGENTS.md` wasn't read at all, which contradicts the user's claim that it works today, so they must be on a recent version.
- I did not test the `@AGENTS.md` import inside a local file, and the setting applies only to this user.
- If their Claude Code runs in a session type that can't load `AGENTS.md` natively, the docs say to use the import from a `CLAUDE.md`.

**Confidence:** High. The exact scenario is documented in the current official docs. The facts the answer rests on are that `CLAUDE.local.md` counts as a `CLAUDE.md` file for the `AGENTS.md` fallback check, and that `claude-md-and-agents-md` overrides that.

Sources: https://code.claude.com/docs/en/memory

## R7

**Position:** Don't do it as planned. A `CLAUDE.local.md` at the repo root counts as a CLAUDE file, so Claude Code stops reading `AGENTS.md` and loads only your personal file. The cleanest fix is a personal `CLAUDE.local.md` that starts with `@AGENTS.md`. The alternative is to set "Project instructions" to `claude-md-and-agents-md`.

**Reasoning (all from the current Claude Code memory docs, https://code.claude.com/docs/en/memory, "AGENTS.md" section):**
- The default setting is `claude-md-or-agents-md`. Claude reads `AGENTS.md` only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or any directory above it.
- The docs state this case directly: "Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you."
- So the user's plan swaps the team instructions for the personal file. Nothing warns them. In an interactive session the `no CLAUDE.md found; AGENTS.md loaded: …` line just disappears.
- Files that don't count, and keep loading alongside `AGENTS.md`, are `~/.claude/CLAUDE.md`, the managed `CLAUDE.md` and `.claude/rules/`.
- `AGENTS.local.md` is explicitly not read, so there is no AGENTS-flavoured local file.

**Options, best first:**
1. Put `@AGENTS.md` as the first line of `CLAUDE.local.md`, then add the personal notes. The docs say imports expand, and a `CLAUDE.md` that imports `AGENTS.md` loads it without double-reading. I did not find the docs describing an import from inside `CLAUDE.local.md` specifically. It says local files are "treated the same way" as `CLAUDE.md`, so I infer it works, but this is not verified. A `/context` check will confirm it. The upside is that it needs no settings change, and it also covers sessions where direct `AGENTS.md` reading is unavailable (Bedrock or telemetry-disabled on versions before v2.1.281, a disabled built-in plugin).
2. Set Project instructions to `claude-md-and-agents-md` in `/config` or user settings. In `~/.claude/settings.json`, use `pluginConfigs."cc-plugin-agents-md@builtin".options.instructionFiles`. The docs say project and local settings files ignore this key. This is a per-user setting, so it works with the plain `CLAUDE.local.md`. Downside: it relies on direct `AGENTS.md` support (v2.1.277 or later).
3. Put the personal instructions in `~/.claude/CLAUDE.md`. This doesn't trigger the suppression and applies to every repo. Downside: it isn't project-specific. A user-level file imported from `CLAUDE.local.md` or `~/.claude/CLAUDE.md` also works.

**Other downsides, which apply either way:**
- **Worktrees:** a gitignored `CLAUDE.local.md` exists only in the worktree where it was created. The docs suggest importing from a home-directory file, such as `@~/.claude/my-project-instructions.md`.
- **Hooks:** `AGENTS.md` read through the setting does not fire `InstructionsLoaded` hooks. When it is imported, the hooks fire as usual. This matters only if the user has such hooks.
- **Nested `AGENTS.md`:** subdirectory `AGENTS.md` files load on demand only if that subdirectory has no CLAUDE files of its own. I haven't confirmed how a root-level `CLAUDE.local.md` interacts with them under option 1.
- **Gitignore:** the user could instead add `CLAUDE.local.md` to `.git/info/exclude` so the shared `.gitignore` stays untouched. This is my own suggestion, not something the docs cover.

**Risks and unknowns:**
- The behaviour is recent (v2.1.277 and later) and the docs are changing quickly. Check `claude --version` and `/memory` or `/context` for the loaded file list.
- I haven't confirmed that an `@AGENTS.md` import inside `CLAUDE.local.md` loads correctly. Only the docs-described `CLAUDE.md` import is documented.
- If the user's Claude Code is older than v2.1.277, `AGENTS.md` is not read directly at all. Their "picks it up fine" report would then mean something else is going on, such as a hook or an import.

**Confidence:** High on the downside, because it is documented verbatim. Medium on the `@AGENTS.md`-in-local-file fix, which I infer.

**Depends most on:** the docs' rule that `CLAUDE.local.md` counts toward the "any CLAUDE file exists" check under the default setting.

## R8

Mostly fine. One thing is worth checking before you rely on it, though.

**The main risk: AGENTS.md might stop loading.** Claude Code's main instruction file is CLAUDE.md. Reading AGENTS.md is a fallback. I can't confirm from here whether that fallback applies only when there's no CLAUDE.md, or no CLAUDE-anything. If adding CLAUDE.local.md counts as having a CLAUDE file, Claude Code could quietly stop loading AGENTS.md. Your personal notes would then replace the team's instructions instead of adding to them. Nothing would error, so you'd only notice when Claude stops following repo conventions.

To check, create the file, start a new session in the repo and run `/memory`. It lists the instruction files that actually loaded. If AGENTS.md isn't there, you can fix it either way:
- Put `@AGENTS.md` at the top of CLAUDE.local.md to import it explicitly.
- Or keep your notes outside the repo and skip CLAUDE.local.md (see below).

**Smaller points:**
- **Use `.git/info/exclude` instead of `.gitignore`.** It ignores files the same way but is never committed. Otherwise you'd be committing a change to `.gitignore` just for your personal file.
- **Git worktrees and other clones won't have it.** Because the file is ignored, it only exists in this one checkout. If you use worktrees or have other clones, you'd have to copy it to each one. Keeping your notes in a file like `~/.claude/<project>-notes.md` and importing that file avoids this. User-level `~/.claude/CLAUDE.md` also works, but it applies to every project.
- **Load order:** your local file and AGENTS.md both load. If they contradict each other, it's unclear which one wins, so don't write rules that fight the shared ones.

So the only real risk is the AGENTS.md fallback, and `/memory` will tell you in a few seconds whether it's a problem.

## R9

## Think tank: CLAUDE.local.md in a repo that relies on AGENTS.md
opus, sonnet, sonnet · session effort · identical brief · debate

### Recommendation (3–0)
Yes, there's a real downside. Under the default setting, a `CLAUDE.local.md` at the repo root makes Claude Code stop reading `AGENTS.md` for you. You'd get your personal notes but quietly lose the team's instructions, with no error. Claude Code only reads `AGENTS.md` as a fallback, when there's no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or any folder above it. The local file counts toward that check. That explains why `AGENTS.md` works for you today.

All three panelists say to keep the local file but add one of two fixes:
- **Change a setting:** run `/config` and set **Project instructions** to `claude-md-and-agents-md`. Claude then loads both files.
- **Import the shared file:** make `@AGENTS.md` the first line of `CLAUDE.local.md`.

Either way, run `/memory` or `/context` afterwards to confirm `AGENTS.md` is still loaded. All three also say to list the file in `.git/info/exclude` instead of the shared `.gitignore`. That keeps it private without a commit your team would see.

Smaller points:
- **Worktrees and clones:** a gitignored `CLAUDE.local.md` only exists in the worktree or clone where you created it (A, B, C).
- **Setting scope:** the setting is per-user and can't be committed. Project and local settings files ignore it (A, B, C).
- **Deprecation:** `CLAUDE.local.md` is still supported, not deprecated (A, B, C).
- **Global instructions:** `~/.claude/CLAUDE.md` doesn't count toward the fallback check, so it's an option for preferences that apply to every repo (B, C).
- **`AGENTS.local.md`:** Claude Code doesn't read this file, so it's no alternative (B, C → A).
- **Hooks:** an `AGENTS.md` loaded through the setting doesn't trigger `InstructionsLoaded` hooks (C → B).

Checked: I fetched https://code.claude.com/docs/en/memory today. The docs describe your exact case: *"Because `CLAUDE.local.md` counts, adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you. To keep your `CLAUDE.local.md` and still have Claude read `AGENTS.md`, set **Project instructions** to `claude-md-and-agents-md`."* They also confirm the other facts this rests on:
- The setting is read only from `~/.claude/settings.json`, a `--settings` file or managed settings, and is ignored in project and local settings files.
- Claude doesn't read the same `AGENTS.md` twice, so using both fixes together is safe.
- The worktree caveat is in the docs.

### Panel
- **A** (opus): "Yes, there is a serious downside. With Claude Code's default setting, a `CLAUDE.local.md` makes Claude stop reading `AGENTS.md`. Go ahead with the file, but either put `@AGENTS.md` as its first line, or set Project instructions to `claude-md-and-agents-md`." High confidence. Didn't move; still prefers the import.
- **B** (sonnet): "Yes, there is a real downside. With the default setting, a root `CLAUDE.local.md` makes Claude Code stop reading `AGENTS.md` for that user. Don't add the file as planned. Set **Project instructions** to `claude-md-and-agents-md` first, and use an `@AGENTS.md` first line in the local file only as a backup." High confidence on the problem, medium on which fix is better. Switched from preferring the import to preferring the setting because of A's point about launching from a subfolder. Re-reading the docs, B found that an import is "external" when its path is outside the folder you launched from, which can trigger an approval prompt.
- **C** (sonnet): "Yes, there is a real downside. With the default setting, adding `CLAUDE.local.md` stops Claude Code reading the repo's `AGENTS.md` for that user. Don't do it as planned. Set **Project instructions** to `claude-md-and-agents-md` in user settings. That is now my first recommendation, ahead of the `@AGENTS.md` import. Also exclude the file through `.git/info/exclude` rather than editing the repo's `.gitignore`." High confidence. Switched to preferring the setting because of A's doubt about `AGENTS.md` files in subfolders, and adopted `.git/info/exclude` from A and B.

### Where they split
The only disagreement is which fix comes first: the import (A) or the setting (B and C, both sonnet).
- **For the import:** it applies to this repo only. The setting changes every repo you open, so any repo with both a `CLAUDE.md` and an `AGENTS.md` will start loading both.
- **For the setting:** it's the fix the docs name for this case.

I checked the two concerns about the import against the docs:
- **Subfolder `AGENTS.md` files:** the docs list loading a subfolder's `AGENTS.md` on demand under "When none count". So once a root `CLAUDE.local.md` exists, those files stop loading by default. Importing the root `AGENTS.md` doesn't bring them back, but the setting does.
- **Launching from a subfolder:** the docs define an import as "external" when its path "resolves outside your working directory". So launching Claude from `repo/subdir/` would likely show a one-time approval prompt for `@AGENTS.md`. If you decline, the import stays off. That's my reading of the docs; I haven't tested it.

So it comes down to your repo. If you have `AGENTS.md` files in subfolders, or start Claude from subfolders, use the setting. If there's one root `AGENTS.md` and you always start at the root, the import works and stays within this repo.

### My take
At launch I expected "probably fine, with one risk to check": whether a local file disables the `AGENTS.md` fallback. It does. The panel and the docs turned that from a maybe into a documented, silent failure, so I now think the plan as written has a real downside.

I'd go with B and C: set `claude-md-and-agents-md` in `/config`. The docs name it for exactly this case, and it also covers `AGENTS.md` files in subfolders. Add `@AGENTS.md` as the first line too only if you sometimes run Claude where it can't read `AGENTS.md` itself, such as older Bedrock sessions or with the built-in plugin turned off. Use `.git/info/exclude`.

The easy way to check: today you should see a line like `no CLAUDE.md found; AGENTS.md loaded: …` when a session starts. If it disappears after you add the file and you haven't applied a fix, you've hit this problem.

The harness flagged each panelist's answer because it contained a `settings.json` snippet. It's the same `pluginConfigs` block the docs show, and I haven't changed any settings or files.

## R10

**Position:** Yes, there is one serious downside. With Claude Code's default setting, adding a `CLAUDE.local.md` makes Claude stop reading `AGENTS.md`. Go ahead with the file, but either put `@AGENTS.md` as its first line, or set Project instructions to `claude-md-and-agents-md`.

**Reasoning:** I checked all of this on 2026-10-19 against the current memory docs at https://code.claude.com/docs/en/memory. The main problem is first; the rest are minor.

1. **Claude stops reading `AGENTS.md`.** This is certain and serious, and you get no warning. The default setting is `claude-md-or-agents-md`: Claude reads `AGENTS.md` only when there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or any directory above it. The docs say `CLAUDE.local.md` counts toward that check, and they warn about this exact case: "adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you." So the user would get their personal notes and lose the team's instructions. This only affects the user's own clone; other people and other tools still read `AGENTS.md`.
2. **Worktrees and other clones won't have it.** This is certain but minor. A gitignored `CLAUDE.local.md` "only exists in the worktree where you created it." The docs suggest importing a file from home instead, such as `@~/.claude/my-project-instructions.md`. The first time Claude meets that kind of import in a project, it asks for approval once.
3. **Editing `.gitignore` is itself a change the team sees.** This is my own advice, not from the docs. Adding the line to the shared `.gitignore` is a committed change. If the user wants nothing committed, `.git/info/exclude` keeps the file private without touching shared files.
4. **`CLAUDE.local.md` is not deprecated.** The docs list it as a supported scope ("Personal project-specific preferences; add to `.gitignore`"). Older recall said it was deprecated; that's out of date, so it isn't a reason to avoid the file.

**Recommended setup (pick one):**
- **Option A, works only in this repo.** Make `@AGENTS.md` the first line of `CLAUDE.local.md`, put the personal notes below it, and list the file in `.git/info/exclude`. The docs' `@AGENTS.md` example puts the import in a `CLAUDE.md`; I'm assuming the same import works from `CLAUDE.local.md`. This also covers sessions where Claude can't read `AGENTS.md` directly (versions older than v2.1.277, or the built-in plugin turned off).
- **Option B, changes the setting.** In `/config`, set **Project instructions** to `claude-md-and-agents-md`. Or add `pluginConfigs["cc-plugin-agents-md@builtin"].options.instructionFiles` to `~/.claude/settings.json` (use `agents-md@builtin` before v2.1.285). Claude then reads each directory's `CLAUDE.md` files first and its `AGENTS.md` after, and skips an `AGENTS.md` it has already loaded. This setting is ignored in project settings files, so it applies to every repo the user opens, not just this one.

To confirm either option worked, run `/memory` and check that the `AGENTS.md` path is listed.

**Risks and unknowns:**
- Docs can be wrong or out of date, so the user should check with `/memory`.
- The user's "picks up `AGENTS.md` fine" suggests v2.1.277 or later, where this default applies. On older versions the setup that worked was a `CLAUDE.md` containing `@AGENTS.md`, which Option A matches anyway.
- I'm not sure whether `AGENTS.md` files in subdirectories still load on demand once a root `CLAUDE.local.md` exists. Option B covers that case more clearly than Option A.
- If Claude is launched from a subdirectory, the `@AGENTS.md` import in Option A may count as "external" and trigger the one-time approval prompt. I haven't verified this.

**Confidence:** High. The docs describe this exact scenario and warn about it. My position depends mainly on two documented facts: `CLAUDE.local.md` counts toward the default "no CLAUDE.md" check, and `claude-md-and-agents-md` (or an explicit `@AGENTS.md` import) brings `AGENTS.md` back.

## R11

**Position:** Yes, there is a serious downside. Adding `CLAUDE.local.md` as planned would stop Claude Code from loading the repo's `AGENTS.md` for that user. Don't do it as planned. Either put `@AGENTS.md` at the top of the `CLAUDE.local.md`, or set **Project instructions** to `claude-md-and-agents-md` (steps below).

**Reasoning (verified in the current official memory docs, https://code.claude.com/docs/en/memory, fetched today):**

1. **Most likely and most serious: the local file displaces `AGENTS.md`.**
   - Claude Code (v2.1.277 or later) reads `AGENTS.md` only as a fallback. The docs' table says that with an `AGENTS.md` and a `CLAUDE.md` or `CLAUDE.local.md` in the working directory or above it, Claude reads "Your `CLAUDE.md` files only".
   - The docs say `CLAUDE.local.md` counts as a `CLAUDE.md` for this check. They also say: "adding one to keep your own uncommitted instructions in a project that relies on `AGENTS.md` stops Claude from reading `AGENTS.md` for you."
   - The user would lose all the shared project instructions without any error. The only sign is that the startup line `no CLAUDE.md found; AGENTS.md loaded: …` disappears. The docs' troubleshooting section "My AGENTS.md isn't loading" describes this exact case.
   - It is easy to miss because the current behaviour works. "Picks up `AGENTS.md` fine" depends on there being no `CLAUDE.md` or `CLAUDE.local.md` anywhere on the path.

2. **`CLAUDE.local.md` is not deprecated.** The docs list it as the supported "Local instructions" scope at `./CLAUDE.local.md` ("add to `.gitignore`"). It is appended after `CLAUDE.md` in each directory. The `AGENTS.local.md` equivalent is not read.

3. **The fix is user-side and has to be repeated.**
   - The `claude-md-and-agents-md` value of **Project instructions** is set via `/config`, or in `~/.claude/settings.json` under `pluginConfigs` → `cc-plugin-agents-md@builtin`. The docs say project and local settings files ignore this entry.
   - So it cannot be committed to the repo. It is per-user, per-machine.
   - With that setting, each directory's `CLAUDE.md` files load first and its `AGENTS.md` after them. An `AGENTS.md` already loaded through an import is not read twice.

4. **Worktrees and other clones.** A gitignored `CLAUDE.local.md` exists only in the worktree or clone where it was created (the docs say this explicitly for worktrees). Elsewhere, `AGENTS.md` loads again, so the behaviour differs between checkouts. The docs' suggested remedy is a home-directory import such as `@~/.claude/my-project-instructions.md`. That import triggers a one-time external-import approval dialog in project-level files.

5. **Minor points.**
   - `AGENTS.md` read through the setting doesn't fire `InstructionsLoaded` hooks.
   - Sessions that can't read `AGENTS.md` natively load `CLAUDE.md` files only. That includes the plugin being disabled, the first session after upgrading, and Bedrock or telemetry-off sessions before v2.1.281.
   - Other tools that read `AGENTS.md` (Codex, Cursor and so on) are unaffected by `CLAUDE.local.md`. It is Claude-only and gitignored.

**Recommended setup (pick one):**
- **A.** Put `@AGENTS.md` on the first line of the gitignored `CLAUDE.local.md`, then add personal instructions below it. The docs say a `CLAUDE.md` import of `AGENTS.md` works and is not double-loaded. I did not find the docs saying this for the `.local` file specifically, but they say `CLAUDE.local.md` "is treated the same way" as `CLAUDE.md`. Check that it works with `/memory` or `/context`.
- **B.** Keep a plain `CLAUDE.local.md` and set **Project instructions** to `claude-md-and-agents-md` in user settings.
- **C.** For instructions that apply across repos, use `~/.claude/CLAUDE.md`. The docs say it doesn't count toward the displacement check, so `AGENTS.md` keeps loading.
- Whichever you choose, run `/memory` to confirm the `AGENTS.md` path is listed.
- Don't commit a `CLAUDE.md` just to fix this. A committed one displaces `AGENTS.md` for every Claude user unless it imports it.

**Risks and unknowns:**
- Option A's `.local` import is inferred from the docs, not tested.
- Docs and behaviour have changed within months. `AGENTS.md` support is only a few weeks old (v2.1.277, Sept 2026).
- I didn't check the changelog or GitHub issues directly.
- If the user runs an older version, `AGENTS.md` wouldn't load at all, which contradicts what they've told me.

**Confidence:** High. The key fact is that `CLAUDE.local.md` counts as a `CLAUDE.md` in the `AGENTS.md` fallback rule. It comes from the official docs, and a web search turned up the same rule in third-party write-ups.
