# Trimmed descriptions and non-Rojo routes, old vs new (2026-10-17)

This checks two things on two models, `sonnet` and `haiku`:
- **Trimmed descriptions.** Both descriptions were shortened to leave room under the 1,024-character limit.
- **Non-Rojo routes.** structure-roblox-projects added Script Sync and Studio-only guidance in [#59](https://github.com/osabased/osaskills/pull/59).

"Old" is the skills on `main` (a9a66e0) and "new" is this branch. Headless Claude Code 2.1.296 ran with `claude -p`. Every run got a fresh copy of a scaffold, with one version's skills in its `.claude/skills/`.

Isolation:
- The parent session's `CLAUDE*`/`ANTHROPIC*` variables were dropped.
- `--setting-sources project,local` kept the installed osaskills plugin out.
- `--strict-mcp-config` dropped connectors.
- Bash, PowerShell, web search and subagents were denied, so no run could execute a command. Trigger runs also couldn't write files. Quality runs could, so an unwanted edit would show.

Installs:
- **structure-roblox-projects ("srp") triggers:** installed as [structure-revamp](../structure-revamp-2026-10-15/) installed them, with every top-level skill and every library skill flat.
- **roblox-resource-acquisition ("rra") triggers:** installed as [resource-revamp](../resource-revamp-2026-10-15/) installed them, with every top-level skill but only the case's library clones, plus that eval's SessionStart hook.
- **Quality runs:** installed like the srp triggers. "Bare" runs leave out structure-roblox-projects.

Scaffolds:
- **Trigger cases:** reuse those two evals' prompts and scaffolds, one of which comes from the [Sonnet comparison](../sonnet-ab-2026-10-11/). Two new prompts cover Script Sync and Studio-only places.
- **q-scriptsync:** uses [scaffold-sync](scaffold-sync/). Its `CLAUDE.md` maps three Script Sync roots, and there is no Rojo project or `pesde.toml`. The client controller reconnects input on every respawn.
- **q-studioonly:** uses [scaffold-studio](scaffold-studio/). Its `CLAUDE.md` describes a Studio-only place in Team Create.

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

Results are in `results/round1` and `results/round2`, one JSON file per run. Round 1's Haiku trigger runs are split across two folders: the first run is in `trigger`, and the other four are in `trigger-haiku`, numbered 1 to 4.

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
- **Misses on every version.**
  - The signal library prompt missed in all 18 runs.
  - The skill pin mismatch prompt missed in all 17.
  - "Janitor or Trove" passed in 2 of 17.
  - On Haiku only: the DataStore guard prompt passed 0 of 15 times, the skill-fix prompt 0 of 15 and the entrypoint prompt 1 of 15. Sonnet passed all three every time.
- **Negatives stayed clean** in every round on both models. Library prompts loaded their own library skill, which is correct.

## Quality

Graders saw shuffled, unlabelled responses, plus any files each run changed. They graded against the verified ground truth in [rubrics.md](grading/rubrics.md). Opus graded both tasks.

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

## Limits

- **Few Sonnet runs:** one per trigger prompt, and round 2 reran only the prompts the changes touch, plus the negatives.
- **Haiku noise:** about 2 of 5 per prompt between identical runs, so these runs can't show small trigger changes on Haiku.
- **Skills inside the project:**
  - A project-wide Glob or Grep can find skill files, which a plugin install keeps outside the project.
  - 83 of 390 Haiku trigger runs read a skill's files without loading that skill, against 2 of 65 Sonnet runs.
  - 8 of Haiku's positive passes came from such a read rather than the Skill tool.
  - The Blink prompt's round-1 drop is one example.
- **Short trigger runs:** a skill loaded after the turn limit counts as a miss.
- **Quality prompts discouraged tool use:** "reply in chat only", plus an MCP the run couldn't call, led most q-studioonly runs to answer without opening anything. A prompt that lets the run look around may load the skill more often.
- **No commands:** with Bash denied, no run executed a check, a sync or a play-test.
- **Grader:**
  - In round 1, Opus used read-only shell commands, though it was told to only read files. The q-studioonly regrade was limited to file tools.
  - On T4, it counted reading each target script before editing as checking its path.
- **Blinding was partial:** responses can name a skill or quote its references.
- **Spend:** 479 runs cost $7.05, not counting grading. Round 1 cost $5.42 and round 2 $1.63. `grading/key.json` maps blind labels to run ids, and `grading/grades.json` holds the per-criterion grades.
