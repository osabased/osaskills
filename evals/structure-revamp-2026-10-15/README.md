# structure-roblox-projects revamp, old vs new (2026-10-15)

This compares the skill on `main` (650725d, "old") with the revamped skill on this branch ("new"). Headless Claude Code ran with `claude -p` and model `sonnet`. Every run got a fresh copy of a scaffold, with one version's skills in its `.claude/skills/`.

Isolation:
- The parent session's `CLAUDE*`/`ANTHROPIC*` variables were dropped.
- `--setting-sources project,local` kept the installed osaskills plugin out.
- `--strict-mcp-config` dropped connectors.
- Bash, PowerShell, web search and subagents were denied, so no run could execute a command.

Scaffolds:
- q-entry and q-glob use the [Sonnet comparison's](../sonnet-ab-2026-10-11/) scaffold and rubrics.
- q-ready, q-guard and q-verify use this eval's [scaffold](scaffold/): a small Rojo game with a check script, a DataStore and a shop remote.

To rerun, extract the old skills with `git archive 650725d skills | tar -x -C <dir>`. Then, from this folder, run `python harness.py --old-skills <dir>/skills [--reps N] [--conds old,new] [--out results/roundN] [case-id ...]`.

## Triggering (12 prompts, 1 run each)

Round 1 compared old with new under its first description. Round 2 reran new under the final description, which names guards, play-tests, the Studio MCP and `globIgnorePaths` and says to use the skill even when the answer seems familiar.

| Prompt | Old | New, first description | New, final description |
| --- | --- | --- | --- |
| Client entrypoint placement | Skill | Skill | Skill |
| `globIgnorePaths` not excluding Preview | read `rojo.md` after a Grep | read `rojo.md` after a Grep | Skill |
| Overview and agent guide | Skill | Skill | Skill |
| Shop RemoteEvents and validation | Skill | Skill | Skill |
| "Make this repo easier for Claude": check script and hooks | none | Skill | Skill |
| CI for a Rojo project | Skill | Skill | Skill |
| Shop button in a Studio play-test with the MCP | none | read `verification.md` after a Grep | Skill |
| Guard against a DataStore rename | none | read `checks.md` after a Grep | Skill |
| 4 negatives (tween, Luau types, typo, Vide component) | none | none | none |

Totals:
- **Loaded through the Skill tool on the 8 positive prompts:** old 4, first new description 5, final description 8.
- **Final description:** every run read exactly one reference, the one its task routes to.
- **Negatives:** stayed clean in every round. The Vide prompt loaded `roblox-vide`, which is correct.

## Quality (5 tasks × old/new × 2 runs, graded blind by Sonnet)

Graders saw four shuffled responses per task, plus any files each run changed. They graded against the verified ground truth in [rubrics.md](grading/rubrics.md).

Which description the "new" runs used:
- q-entry and q-ready: the first description. Both runs loaded the skill under it.
- q-glob, q-guard and q-verify: the final description.

| Task | Rubric old | Rubric new | Overall old | Overall new | Cost old | Cost new | Skill loaded old / new |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Client entrypoint placement | 9/10 | 10/10 | 7.0 | 8.5 | $0.07 | $0.09 | 2/2, 2/2 |
| Rojo `globIgnorePaths` | 12/12 | 12/12 | 7.5 | 8.5 | $0.05 | $0.08 | 0/2, 2/2 |
| Agent-readiness proposal | 5/14 | 11/14 | 3.5 | 7.5 | $0.14 | $0.16 | 0/2, 2/2 |
| DataStore name guard | 9/12 | 11/12 | 6.5 | 7.5 | $0.08 | $0.10 | 0/2, 2/2 |
| Play-test verification plan | 10/16 | 16/16 | 5.5 | 8.5 | $0.10 | $0.11 | 0/2, 2/2 |
| **Total** | **45/64 (70%)** | **60/64 (94%)** | **6.0** | **8.1** | $0.09 | $0.11 | 2/10, 10/10 |

What the revamp changed:
- **The old skill loaded only for the placement question.** The other old results are the model on its own. Both old agent-readiness runs read `motion-studies` instead.
- **Agent readiness.**
  - Old runs proposed a format hook and a `CLAUDE.md`. They had no Stop hook, no DataStore identity guard and no play-test rung, and one said the project had no check command.
  - New runs proposed the identity guards, a Stop hook, pre-push and CI on one command, and a Studio rung.
  - One new run was complete. The other missed the existing `check.sh` and left out the Stop hook's loop guard.
- **Play-test plan.**
  - Both new runs ran a static check before Play.
  - Both avoided requiring the game's modules from `execute_luau`, and one explained the separate module instance.
  - Both named what the plan doesn't prove.
  - Neither old run did the first two. One old run expected the client entry to be a `LocalScript`, although the scaffold sets `emitLegacyScripts: false`.
- **Guard.**
  - Both new runs gave break-test steps; neither old run did.
  - One new run went past the request: it guarded every DataStore kind, in a new script file.
- **Entrypoint and globs:** both versions were correct. One old run gave a wrong reason against `StarterPlayerScripts`.
- **Cost:** new runs cost about 25% more, because they load the skill and read one 4–6 KB reference.

Fixed after this run (these fixes weren't rerun):
- **Missed check command:** one new readiness run and one new verification run didn't find `scripts/check.sh`. The work loop now says where to look when no guide names a check command. `checks.md` says to extend an existing one rather than add a second.
- **Stop-hook loop guard:** `checks.md` now opens the Stop row with the `stop_hook_active` early exit, instead of leaving it in the notes column.

## Size

| | Old | New |
| --- | --- | --- |
| Description | 819 characters | 969 characters |
| SKILL.md body | 910 words | 1,033 words |
| References | 15 files in 5 folders, 11,672 words | 12 flat files, 8,667 words |

SKILL.md grew by the agent-ready table and the routing table. Each new quality run read one reference, except one readiness run that read two.

## Limits

- **Few runs:** one run per trigger prompt and two per quality cell, all on one model.
- **Grader:** Sonnet graded this eval, while the earlier comparison used Opus. q-entry and q-glob scores compare with that eval only roughly.
- **Blinding was partial:** some responses mention the skill or its `check_updates.py`.
- **Grep could reach the skills:** they sit inside the project, so a Grep can find reference files. That is how four round-1 runs reached content without the Skill tool. A plugin install sits outside the project.
- **Duplicate skills:** the harness installs library skills both flat and under `roblox-resource-acquisition/libraries/`. One run noticed the duplicates.
- **Short trigger runs:** they stop after 3 turns, so a skill loaded after longer exploration counts as a miss.
- **No commands:** with Bash denied, no run executed a check or break-tested a guard.
- **Not rerun:** the final description's effect on q-entry and q-ready, and the two fixes above.
- **Spend:** 62 runs cost $4.86, not counting grading. `grading/key.json` maps blind labels to run ids, and `grading/grades.json` holds the per-criterion grades.
