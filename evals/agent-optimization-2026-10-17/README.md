# Trimmed descriptions and non-Rojo routes, old vs new (2026-10-17)

This checks three things on two models, `sonnet` and `haiku`:
- **Trimmed descriptions.** Both descriptions were shortened to leave room under the 1,024-character limit.
- **Non-Rojo routes.** structure-roblox-projects added Script Sync and Studio-only guidance in [#59](https://github.com/osabased/osaskills/pull/59).
- **Studio-only rules in `CLAUDE.md`.** [#63](https://github.com/osabased/osaskills/pull/63) moved the Studio-only working rules into the place's `CLAUDE.md`, asks for a save only before structural changes, and play-tests an edit by default.

"Old" is the skills on `main` (a9a66e0). "New" is [#62](https://github.com/osabased/osaskills/pull/62)'s skills in rounds 1 to 3, and #63's in rounds 4 and 5. Headless Claude Code 2.1.296 ran with `claude -p`. Every run got a fresh copy of a scaffold, with one version's skills in its `.claude/skills/`.

Isolation:
- The parent session's `CLAUDE*`/`ANTHROPIC*` variables were dropped.
- `--setting-sources project,local` kept the installed osaskills plugin out.
- `--strict-mcp-config` dropped connectors. The q-studio-mcp cases' only MCP server was [studio_stub.py](studio_stub.py), with its tools allowed.
- Bash, PowerShell, web search and subagents were denied, so no run could execute a command. Trigger runs also couldn't write files. Quality runs could, so an unwanted edit would show.

Installs:
- **structure-roblox-projects ("srp") triggers:** installed as [structure-revamp](../structure-revamp-2026-10-15/) installed them, with every top-level skill and every library skill flat.
- **roblox-resource-acquisition ("rra") triggers:** installed as [resource-revamp](../resource-revamp-2026-10-15/) installed them, with every top-level skill but only the case's library clones, plus that eval's SessionStart hook.
- **Quality runs:** installed like the srp triggers. "Bare" runs leave out structure-roblox-projects.

Scaffolds:
- **Trigger cases:** reuse those two evals' prompts and scaffolds, one of which comes from the [Sonnet comparison](../sonnet-ab-2026-10-11/). Two new prompts cover Script Sync and Studio-only places.
- **q-scriptsync:** uses [scaffold-sync](scaffold-sync/). Its `CLAUDE.md` maps three Script Sync roots, and there is no Rojo project or `pesde.toml`. The client controller reconnects input on every respawn.
- **q-studioonly:** uses [scaffold-studio](scaffold-studio/). Its `CLAUDE.md` describes a Studio-only place in Team Create.
- **q-studio-mcp:** uses scaffold-studio too, with [studio_stub.py](studio_stub.py) standing in for Roblox's Studio MCP server.
  - Its tools have the real server's names and parameters.
  - It reports two open windows: the place `CLAUDE.md` names, and a test copy with a similar name.
  - The place holds a `Rewards` module whose `GiveCoins` four scripts use: two direct calls, a stored reference and a string key.
  - A play-test runs a daily-bonus script that prints a line or fails on a missing function.
- **q-studio-mcp-guide:** the same task and stub, with [scaffold-studio-guide](scaffold-studio-guide/). Its `CLAUDE.md` adds the rules the changed `studio-only.md` says to write there: the `studio_id` to use, Drafts mode off, and the checkpoint, edit, play-test and report rules.
- **q-studio-mcp-guide2:** the same again, with [scaffold-studio-guide2](scaffold-studio-guide2/). Its `CLAUDE.md` adds that an edit is play-tested unless the user has said not to, and that the report names the paths the play-test didn't reach.

To rerun, extract the old plugin with `git archive a9a66e0 skills hooks | tar -x -C <dir>`. Then, from this folder, run `python harness.py --old-root <dir> [--models sonnet,haiku] [--reps N] [--conds old,new,bare] [--out results/roundN] [case-id ...]`.

Rounds:
- **Round 1** ran the first trimmed descriptions:
  - all 26 trigger prompts, old and new, once on Sonnet and five times on Haiku;
  - both quality tasks, new and bare, twice per model.
- **Between rounds**, two clauses changed:
  - roblox-resource-acquisition's package clause regained "or setting up", after Haiku's Blink prompt fell from 3/5 to 0/5.
  - structure-roblox-projects' MCP clause widened from testing to "editing or testing", after q-studioonly loaded the skill in none of its 4 new runs.
- **Round 2** ran the final descriptions, new only:
  - Haiku, five times on all 26 trigger prompts;
  - Sonnet, once on the 5 prompts the changes touch and the 8 negatives;
  - q-studioonly again.
- **Round 3** ran q-studio-mcp, new and bare, six times per model.
- **Between rounds 3 and 4**, `studio-only.md` changed (see [Size](#size)).
- **Round 4** ran q-studio-mcp-guide, new only, six times per model.
- **Between rounds 4 and 5**, `studio-only.md` gained the play-test rule.
- **Round 5** ran q-studio-mcp-guide2, new only, six times per model.

Results are in `results/round1` to `results/round5`, one JSON file per run. Round 1's Haiku trigger runs are split across two folders: the first run is in `trigger`, and the other four are in `trigger-haiku`, numbered 1 to 4.

## Triggering

A positive prompt passes when the run loads the suite's skill, through the Skill tool or by reading its `SKILL.md`. A negative prompt passes when the run doesn't load it.

| Model | Suite | Positives old | Positives new, round 1 | Positives new, round 2 | Negatives |
| --- | --- | --- | --- | --- | --- |
| Sonnet | srp, 10 prompts × 1 | 10/10 | 10/10 | 3/3 rerun | all clean |
| Sonnet | rra, 8 prompts × 1 | 4/8 | 5/8 | 1/2 rerun | all clean |
| Haiku | srp, 10 prompts × 5 | 26/50 | 25/50 | 30/50 | all clean |
| Haiku | rra, 8 prompts × 5 | 12/40 | 9/40 | 12/40 | all clean |

Positive prompts. The Haiku columns count passes out of 5, and the Sonnet columns are old then new, round 1:

| Prompt | Suite | Haiku old | Haiku new, r1 | Haiku new, r2 | Sonnet old / new |
| --- | --- | --- | --- | --- | --- |
| Client entrypoint placement | srp | 0 | 1 | 0 | pass / pass |
| `globIgnorePaths` not excluding Preview | srp | 4 | 2 | 3 | pass / pass |
| Overview and agent guide | srp | 2 | 3 | 3 | pass / pass |
| Shop RemoteEvents and validation | srp | 3 | 2 | 3 | pass / pass |
| "Make this repo easier for Claude" | srp | 2 | 1 | 5 | pass / pass |
| CI for a Rojo project | srp | 2 | 3 | 4 | pass / pass |
| Play-test with the Studio MCP | srp | 5 | 5 | 5 | pass / pass |
| Guard against a DataStore rename | srp | 0 | 0 | 0 | pass / pass |
| Sync a pesde folder with Script Sync | srp | 3 | 3 | 2 | pass / pass |
| Studio-only scripts through the MCP | srp | 5 | 5 | 5 | pass / pass |
| Add a signal library | rra | 0 | 0 | 0 | miss / miss |
| Janitor or Trove | rra | 1 | 1 | 0 | miss / miss |
| Hitbox module search | rra | 5 | 5 | 5 | pass / pass |
| Set up Blink | rra | 3 | 0 | 3 | pass / pass |
| Upgrade a pinned library | rra | 2 | 1 | 3 | pass / pass |
| Skill pin doesn't match `pesde.lock` | rra | 0 | 0 | 0 | miss / miss |
| Write a library skill | rra | 1 | 2 | 1 | miss / pass |
| Fix a library skill's wrong guidance | rra | 0 | 0 | 0 | pass / pass |

In round 2, Sonnet passed the Play-test, Script Sync, Studio-only and Blink prompts and missed the signal library prompt again.

What the results show:
- **On Sonnet the trimmed descriptions trigger as the old ones did.** The one change is that "write" in roblox-resource-acquisition's description now catches the skill-writing prompt.
- **On Haiku, old and new are within noise.**
  - The agent-guide prompt went from 1/5 to 5/5 between rounds, though no wording it touches changed.
  - So Haiku's per-prompt counts swing by about 2 of 5 from run to run, and none of the Haiku differences between old and new is larger than that.
- **The Blink prompt.**
  - The five round-1 new runs never loaded roblox-resource-acquisition. Each found the `roblox-blink` library skill through a project-wide Glob and read it directly, which a plugin install wouldn't allow.
  - In round 2, three of five loaded the skill through the Skill tool.
  - Restoring "or setting up" may have done that, but a swing of 3 is within Haiku's noise.
- **Misses on every version were right answers or turn-limit stops.** Every run that answered these prompts answered correctly. The rest ran out of turns.
  - **Signal library, 0 of 18.**
    - Every run found and read the scaffold's vendored `src/shared/Signal.luau`.
    - The 4 that answered said the project already has a signal module and changed nothing.
    - The other 14, all Haiku, hit the 3-turn limit first.
  - **"Janitor or Trove", 2 of 17.** All 17 answered Janitor, citing the scaffold's `CLAUDE.md`, which names it.
  - **Skill pin mismatch, 0 of 17.**
    - All 13 runs that answered said to keep the project's 1.17.0 pin. Six of them cited `roblox-janitor`'s own pin check, which covers this case without roblox-resource-acquisition.
    - The other 4, all Haiku, hit the turn limit.
  - [resource-revamp](../resource-revamp-2026-10-15/) reached the same conclusion. It called the signal and Janitor misses arguably right, and noted that its session note can answer the pin prompt. So these three prompts test the scaffold more than the description.
  - **On Haiku only**, three prompts rarely passed. Sonnet passed all three every time.
    - **DataStore guard, 0 of 15.** 14 runs read the skill's `checks.md` through a project-wide search instead of loading the skill. The 6 that answered asked for the DataStore name, which the scaffold doesn't have. The other 9 hit the turn limit.
    - **Skill fix, 0 of 15.** Every run read `roblox-vide`'s `SKILL.md` and its API reference, then hit the turn limit before reaching roblox-resource-acquisition.
    - **Entrypoint, 1 of 15.**
      - 9 runs answered correctly from `default.project.json` without the skill: `src/client` maps into ReplicatedStorage, where a LocalScript never runs.
      - The run that passed and the other 5 hit the turn limit.
- **Negatives stayed clean** in every round on both models. Library prompts loaded their own library skill, which is correct.

## Quality

Graders saw shuffled, unlabelled responses, plus any files each run changed. For the q-studio-mcp cases they also saw each run's earlier messages and its MCP calls, but not its skill loads or `CLAUDE.md`. They graded against the verified ground truth in [rubrics.md](grading/rubrics.md). Opus graded all three tasks.

### q-scriptsync (round 1, 2 runs per cell)

| Model | Condition | Rubric | Overall | Cost | structure-roblox-projects loaded |
| --- | --- | --- | --- | --- | --- |
| Sonnet | new | 12/16 | 7.5 | $0.14 | 2/2 |
| Sonnet | bare | 4/16 | 4.0 | $0.11 | 0/2 |
| Haiku | new | 5/16 | 3.0 | $0.01 | 0/2 |
| Haiku | bare | 6/16 | 3.5 | $0.01 | 0/2 |

- **With the skill, Sonnet got the Script Sync rules right.**
  - Both new runs read `script-sync.md`. They kept the pesde install out of the synced roots and inserted a `rojo build` model of it, rebuilt after each install (S1).
  - Both tied the play-test to Studio running the files on disk (S3).
  - One handled Instance requires with a generated sourcemap (S4).
  - No bare run met S1, S3 or S4.
- **Haiku never loaded structure-roblox-projects.** Every Haiku run loaded `roblox-janitor` and stopped there, so both Haiku cells measure the model on its own.
- **No run met S2.**
  - Both Sonnet new runs noticed that `Controller.client.luau` runs twice from `StarterPlayerScripts`. One called it a separate bug, and the other a risk to watch for in the play-test.
  - Neither proposed a change. Flagging it may be the proportional answer to a Janitor task, so S2 may ask too much.
- **S7 understates Janitor use.** Every run pinned `=1.18.3`. Six runs reused one Janitor and cleaned it on each respawn, which works, but the rubric's "one Janitor per character" failed them.

### q-studioonly (rounds 1 and 2, 4 runs per cell)

All 16 responses were graded together, so both rounds share one scale. The new runs used the first description in round 1 and the final one in round 2.

| Model | Condition | Rubric | Overall | Cost | structure-roblox-projects loaded |
| --- | --- | --- | --- | --- | --- |
| Sonnet | new | 16/32 | 5.8 | $0.06 | 1/4 |
| Sonnet | bare | 13/32 | 4.8 | $0.05 | 0/4 |
| Haiku | new | 12/32 | 3.8 | under $0.01 | 0/4 |
| Haiku | bare | 13/32 | 4.2 | under $0.01 | 0/4 |

- **The skill loaded in only 1 of 8 new runs**, a round-2 Sonnet run.
  - The other 15 runs answered in one turn, without loading a skill or reading a file.
  - The trigger prompt on the same topic loaded the skill in all 18 of its runs. That prompt asks how to let Claude edit a Studio-only place safely.
  - This task instead says the MCP can't be called from here, and asks for a rename plan in chat. The models planned from memory.
- **The run with the skill scored highest: 7 of 8 criteria, overall 9.**
  - It read `studio-only.md`, `migration.md` and `verification.md`.
  - It was the only run to:
    - report the static checks as unavailable;
    - pick the Studio window by `studio_id`;
    - warn that a wrong `multi_edit` path creates a stray script.
  - The 15 runs without the skill met 2 to 5 criteria (3.1 on average), with an overall average of 4.3.
- **Common gaps:**
  - Five runs without the skill required the game's modules from `execute_luau` during a play-test.
  - Only two runs asked for a version-history save before editing, and only three edited in Edit mode.
- **No run met T7, including the run with the skill.** Several said the place has no Script Sync, but none offered it as a later step.

### q-studio-mcp and its guided variants (rounds 3 to 5, 6 runs per cell)

The q-studioonly rename, asked plainly: "Rename the GiveCoins function in ServerScriptService.Rewards to AwardCoins and update every caller." Each run could call the stub's Studio tools. Rounds 3 and 4 were graded together, after M1 and M2 changed to the new checkpoint rule. That regrade replaced round 3's first grades. The same grader then graded round 5 on the same scale. "Guide" is round 4's `CLAUDE.md`, and "guide + play-test" round 5's.

| Model | Condition | Rubric | Overall | Cost | structure-roblox-projects loaded |
| --- | --- | --- | --- | --- | --- |
| Sonnet | guide + play-test | 42/48 | 9.0 | $0.11 | 0/6 |
| Sonnet | guide | 36/48 | 7.0 | $0.10 | 0/6 |
| Sonnet | new | 27/48 | 5.5 | $0.09 | 1/6 |
| Sonnet | bare | 26/48 | 5.3 | $0.08 | 0/6 |
| Haiku | guide + play-test | 38/48 | 8.0 | under $0.01 | 0/6 |
| Haiku | guide | 33/48 | 6.5 | under $0.01 | 0/6 |
| Haiku | new | 25/48 | 5.7 | under $0.01 | 0/6 |
| Haiku | bare | 26/48 | 5.7 | under $0.01 | 0/6 |

- **Every run did the rename correctly.**
  - Each listed the open Studios and found all four users with one `script_grep` (M3).
  - Each edited all five scripts in Edit mode, including the stored reference in `DailyBonus` and the string key in `AdminCommands` (M4).
  - Each searched again afterwards and found no `GiveCoins`.
  - No run created a stray script or touched the test copy.
- **The guide carried the rules the skill didn't.**
  - No guided run loaded the skill. In round 3 it loaded in 1 of 12 new runs.
  - Every guided run said how to undo the rename (M1), against 1 of 24 round-3 runs. Nine named **View Script History**.
  - All 12 reported the static checks as not run, against one round-3 run.
  - Every Sonnet guided run said the edit had already reached the collaborators (M2), and so did 3 of 6 Haiku guided runs. In round 3, 13 of 24 runs passed M2, and four said collaborators get the edit when they next sync, though Live Scripting applies it at once.
  - No guided run sent a call without the right `studio_id` (M5). In round 3, 6 of 12 Haiku runs sent one call with a missing or invented id, which the stub rejected.
  - Guided runs didn't stop to ask for a save, and several said none was needed because no script was added, moved or deleted.
- **Without the play-test rule, no run play-tested, though the stub allowed it** (M6).
  - Round 4's guide says how to play-test but not that a change needs one.
  - Every round-4 run listed the play-test as not run, and 9 named the reward paths left untested. Two Sonnet runs offered to run one.
- **With the rule, every round-5 run play-tested.**
  - Each started a play-test after its edits, read the console (`[DailyBonus] Player1 +50 coins`) and stopped the play-test.
  - Each said the kill, refund and `/coins` paths weren't reached.
  - Ten of 12 passed M6. Two Haiku runs searched again only for `GiveCoins` and didn't reread the edited source.
  - Two Haiku runs didn't mention the collaborators (M2), against three in round 4.
  - It cost $0.11 a Sonnet run, against $0.10 without the rule.
- **No run mentioned Script Sync** (M7). The guide doesn't, and a user who has chosen to stay Studio-only may not need it, so M7 may ask too much.
- **The round-3 run with the skill** read `studio-only.md` and edited first. It pointed to script history for recovery and left a test plan, which earned it overall 7 and 6 of 8, the top round-3 scores.
- **Overall scores ranged from 4 to 9.** Every Sonnet run scored 7 in round 4 and 9 in round 5.

## Size

| | Old | New |
| --- | --- | --- |
| roblox-resource-acquisition description | 1,021 characters | 924 characters |
| structure-roblox-projects description | 990 characters | 971 characters |
| SKILL.md bodies | 872 and 1,069 words | unchanged |

roblox-resource-acquisition's description dropped:
- the tool-setup clause (Rojo, Rokit, Selene, StyLua, Lune), so setting up a tool routes to structure-roblox-projects;
- two signal library names and the verb "pin", which "refreshing a pinned version" still covers.

It gained "write" and "or setting up".

structure-roblox-projects' description dropped `ServerStorage` from its service list and shortened the guard example. Its MCP clause now covers editing as well as testing.

`ssa.md` gained a table of contents. It was the only structure-roblox-projects reference over 100 lines without one.

`studio-only.md` grew from 559 to 721 words:
- Before round 4, its guide bullet began listing the rules to write into the place's `CLAUDE.md`, since a session that doesn't load the skill still reads that file.
- Also before round 4, its checkpoint bullet began asking for a save only before moving, deleting or adding scripts. An edit inside existing scripts goes ahead, and the report says how to undo it, with **View Script History** in Team Create.
- Before round 5, its play-test bullet began asking for a play-test after an edit, unless the user has said not to, and its report bullet began naming the paths the play-test didn't reach.

## Limits

- **Few Sonnet runs:** one per trigger prompt, and round 2 reran only the prompts the changes touch, plus the negatives.
- **Haiku noise:** about 2 of 5 per prompt between identical runs, so these runs can't show small trigger changes on Haiku.
- **Skills inside the project:**
  - A project-wide Glob or Grep can find skill files, which a plugin install keeps outside the project.
  - 83 of 390 Haiku trigger runs read a skill's files without loading that skill, against 2 of 65 Sonnet runs.
  - 8 of Haiku's positive passes came from such a read rather than the Skill tool.
  - The Blink prompt's round-1 drop is one example.
- **Short trigger runs:** a skill loaded after the turn limit counts as a miss.
- **q-studioonly discouraged tool use:** "reply in chat only", plus an MCP the run couldn't call, led most runs to answer without opening anything. q-studio-mcp asked for the same rename plainly, with an MCP the run could call.
- **No commands:** with Bash denied, no run executed a check or a sync. q-studio-mcp runs could play-test through the stub.
- **The stub is not Studio:**
  - `execute_luau` runs nothing and returns no output.
  - A play-test runs only the daily-bonus script.
  - Team Create collaborators, Drafts mode and version history aren't simulated.
  - Its tools were allowed without a permission prompt.
  - It has 11 of the real server's 28 tools, with shorter descriptions. The 17 left out include asset, generation, input and screenshot tools, `skill` and `subagent`.
- **No one answered:** a headless run that wanted a checkpoint could only end its turn with a question. With a person in the session, runs might stop to ask more often; this eval can't tell.
- **One guide per round:** rounds 4 and 5 each tested one `CLAUDE.md`, written by hand from the changed reference, not one an agent wrote with the skill.
- **Play-tests in a shared place:** Play takes over the user's own Studio window while it runs. Roblox's testing docs call it solo playtesting but don't say outright that it leaves collaborators alone, and the stub can't show it.
- **Grader:**
  - In round 1, Opus used read-only shell commands, though it was told to only read files. The q-studioonly regrade was limited to file tools.
  - On T4, it counted reading each target script before editing as checking its path.
  - In the joint q-studio-mcp regrade, its context reset partway through. Reasons for the runs it read before then cite no call numbers.
  - It graded round 5 as a separate later batch, so it knew those runs came after the first 36. It said it scored a run that met every criterion but M7 at 9, and earlier runs topped out at 7 because they also failed M6.
- **Blinding was partial:** responses can name a skill or quote its references.
- **Spend:** 527 runs cost $9.55, not counting grading. Round 1 cost $5.42, round 2 $1.63, round 3 $1.14, round 4 $0.63 and round 5 $0.73. A two-run q-studio-mcp pilot, not kept, cost $0.09 more. `grading/key.json` maps blind labels to run ids, and `grading/grades.json` holds the per-criterion grades.
