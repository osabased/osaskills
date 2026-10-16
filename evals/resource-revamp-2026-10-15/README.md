# roblox-resource-acquisition revamp, old vs new (2026-10-15)

This compares `roblox-resource-acquisition` (RRA) and the plugin's session hook on `main` (20d318a, "old") with the revamped versions on this branch ("new"). Headless Claude Code ran with `claude -p` and model `sonnet`. Every run got a fresh copy of the [scaffold](scaffold/) with one version's top-level skills and two cloned library skills (`roblox-vide`, `roblox-janitor`) in `.claude/skills/`. [`session_hook.py`](session_hook.py) ran that version's library note as a SessionStart hook, standing in for the plugin's hook.

The scaffold is "coin-run", a small Rojo + pesde game:
- **Dependencies:** `pesde.toml` and `pesde.lock` declare Charm 0.11.1, Janitor 1.17.0 and Vide. The catalog's Janitor skill targets 1.18.3, so the session note reports a pin mismatch.
- **Code:** a vendored `src/shared/Signal.luau`, coin, round and UI modules, and `scripts/check_guards.py` holding the project's guards.

Isolation:
- The parent session's `CLAUDE*`/`ANTHROPIC*` variables were dropped.
- `--setting-sources project,local` kept the installed osaskills plugin out.
- `--strict-mcp-config` dropped connectors.
- **Trigger runs:** Bash, PowerShell, edits, web search and subagents were denied, with a 3-turn limit.
- **Quality runs:** PowerShell, web search and subagents were denied, with a 30-turn limit. `python`, `python3` and `uv` were allowed, so the pin check, the clone script and guard break-tests could run. Read-only shell commands also ran. Anything else was refused, including `bash scripts/check.sh`, `pesde install` and writes through the shell.

To rerun, extract the old plugin tree with `git archive 20d318a skills hooks | tar -x -C <dir>`. Then, from this folder, run `python harness.py --old-root <dir> [--reps N] [--conds old,new] [--out results/quality] [case-id ...]`. The trigger results used `--reps 1 --out results/trigger`.

## Triggering (12 prompts, 1 run each)

| Prompt | Old | New |
| --- | --- | --- |
| Add a signal library (the project vendors one) | none: found `Signal.luau` and asked | none: same |
| Janitor or Trove for UI cleanup | none: answered Janitor from `CLAUDE.md` | none: same |
| Hitbox module or raycast | Skill, 9.0 KB read | Skill, 5.5 KB read |
| Set up Blink | Skill, 19.4 KB read | Skill, 16.1 KB read |
| Bump the pinned Vide | Skill, 8.8 KB read | Skill, 5.0 KB read |
| Janitor pin mismatch | Skill: read 2 references (9.1 KB), ran the old pin checker, hit the turn limit with no answer | none: one Grep, then a correct answer from the session note in 2 turns ($0.04 vs $0.07) |
| Write a Fusion library skill | read `child-authoring.md` after a Grep, then asked questions | read `writing-library-skills.md` and the Vide skill, then hit the turn limit with no answer |
| Fix the Vide skill's `show()` advice | read the Vide skill only | Skill |
| 4 negatives (Janitor tween cleanup, folder layout, tween, Luau types) | correct | correct |

Totals:
- **Loaded through the Skill tool on the 8 positive prompts:** old 4, new 4. Counting reference reads reached through a Grep, 5 each.
- **The two misses shared by both versions are arguably right.** The project already has a signal module, and its `CLAUDE.md` already picks Janitor; the skill's first step says to stop there.
- **Less to read per load:** each prompt that loaded the skill in both versions read 17–43% less.
- **Negatives stayed clean.** The Janitor prompt loaded `roblox-janitor` and the folder prompt loaded `structure-roblox-projects`, both correct.

## Quality (5 tasks × old/new × 2 runs, graded blind by Sonnet)

Graders saw four shuffled responses per task: each run's final message, the commands it ran, the commands permissions refused, the skills it added and the full text of every file it changed. They graded against the ground truth in [rubrics.md](grading/rubrics.md). [`grading/key.json`](grading/key.json) maps the labels back to runs, and [`grading/grades.json`](grading/grades.json) holds the per-criterion grades. Costs are means per run.

| Task | Rubric old | Rubric new | Overall old | Overall new | Cost old | Cost new |
| --- | --- | --- | --- | --- | --- | --- |
| "Add a library" for coin events (`q-existing`) | 10/10 | 10/10 | 8.5 | 8.0 | $0.11 | $0.12 |
| Blink vs RemoteEvents, recommendation only (`q-evaluate`) | 10/10 | 10/10 | 7.5 | 7.5 | $0.12 | $0.09 |
| Janitor edit with the 1.17.0 pin (`q-mismatch`) | 10/10 | 10/10 | 7.5 | 8.0 | $0.09 | $0.11 |
| Charm atom in a Vide label (`q-clone`) | 10/10 | 9/10 | 7.5 | 7.0 | $0.10 | $0.10 |
| Add Blink with a client-to-server ban (`q-adopt-guard`) | 7/12 | 6/12 | 6.0 | 3.5 | $0.31 | $0.22 |
| **Total** | **47/52 (90%)** | **45/52 (87%)** | **7.4** | **6.8** | $0.15 | $0.13 |

The first-round new version scored slightly lower. Almost all of the gap is two runs, and [two fixes](#after-two-fixes) target them:
- **One new Blink run stopped at a plan** after `pesde install` was refused. It added only the dependency line, and left the schema, guard and code as next steps, though none of them needed the install. The other new run and both old runs wrote a schema and a guard. One run of each version pinned its guard to the Blink version in `pesde.lock`.
- **One new Charm run read the catalog copy of `roblox-charm` in place** instead of cloning it, although the session note named the clone as due. Its code was still correct.

Elsewhere the versions matched:
- **Existing signal module:** all four runs used the vendored `Signal.luau` and added no dependency.
- **Blink evaluation:** all four loaded RRA and the Blink skill, and raised the receive-side risk (issue #45). New runs read 11.9 KB of skill text against 15.2 KB.
- **Pin mismatch:** all four noticed 1.17.0 vs 1.18.3, kept the pin and used only API both versions have.

What no first-round run did on the Blink task, in either version: clone `roblox-blink` or write a complete `CLAUDE.md` entry. Both gaps follow from the skill's own rules in this environment. The clone script refuses until the lock has the library, and the lock needs `pesde install`. Both versions also said not to list a pending adoption in `CLAUDE.md`.

### After two fixes

Two changes followed the first round:
- **Pending adoptions:** SKILL.md and `adopting.md` now say a blocked install doesn't stop the steps that don't depend on it. A pending adoption whose use the project bans gets its `CLAUDE.md` entry right away, marked pending. Until the lock has the library, the agent follows the catalog copy and clones later.
- **Clone, then read the clone:** the session note now says to read each clone's `SKILL.md` after cloning, not the catalog copy in place.

The new version was rerun twice on each of the two tasks, with `--conds new --reps 2 --out results/quality-fixed q-clone q-adopt-guard` ([results](results/quality-fixed/)). A fresh blind grader per task saw those two runs shuffled with the same two old runs. `grades.json` holds these grades under `q-clone-fixed` and `q-adopt-guard-fixed`.

| | Old | New, first round | New, after fixes |
| --- | --- | --- | --- |
| `q-clone` rubric | 10/10 | 9/10 | 10/10 |
| `q-clone` overall | 7.5 | 7.0 | 8.0 |
| `q-clone` cost per run | $0.10 | $0.10 | $0.13 |
| `q-adopt-guard` rubric | 7/12 | 6/12 | 11/12 |
| `q-adopt-guard` overall | 6.5 (6.0 in the first round) | 3.5 | 6.5 |
| `q-adopt-guard` cost per run | $0.31 | $0.22 | $0.33 |

With the rerun cells in place, the rubric totals are old 47/52 and new 51/52. Mean cost per run across the five tasks is $0.15 for old and $0.16 for new.

- **Charm:** both new runs cloned `roblox-charm` with the clone script and then read the clone (16–18 turns).
- **Blink:** both new runs wrote the schema, a guard pinned to the lockfile's Blink version, and a `CLAUDE.md` entry naming the skill, the ban and the guard. Both left the clone until the lock has Blink. One also fired `CoinsChanged` from `Coins.add` and break-tested the guard on a scratch copy (35 turns, $0.38). The other left the fire and the break-test as next steps (24 turns, $0.28).
- **Still missed:** no run in either version wired the client listener. The grader still credited G2 to the run that fired the event and explained the deferred clone; read strictly, G2 needs the listener, which makes the new totals 10/12 and 50/52. One new entry has no "Pending" note though the install hadn't run. Both name `roblox-blink` before it's cloned, which `adopting.md` reserves for a cloned skill; G5 asks for the skill's name, so it didn't count against them.
- **Grader consistency:** the regrade gave the four old runs the same per-criterion grades as the first round. Its overall scores matched on Charm and were one point higher for one old Blink run.

### Pin-check cost

The old skill had a library skill load RRA and run `check_resource_install.py` before using the library. The new hook compares the pins at session start and names any mismatch, and a library skill reads the manifest and lock itself.

- **Trigger prompt about the mismatch:** old loaded RRA, read 9.1 KB, ran the checker and ran out of turns. New answered from the session note in 2 turns at 57% of the cost.
- **Janitor edit (`q-mismatch`):** neither old run followed the prescribed check. Both loaded `roblox-janitor` and read `pesde.toml` directly (9–12 turns, $0.09). One new run read no skill and relied on the note (8 turns, $0.09). The other also read the Janitor skill and its setup reference (13 turns, $0.12).

## Size

| | Old | New |
| --- | --- | --- |
| Description | 1,017 characters | 1,021 characters |
| SKILL.md body | 800 words | 872 words |
| References | 6 files, 5,629 words | 5 files, 5,182 words |
| Pin-check script | `check_resource_install.py`, 2,494 words | `_pins.py`, 1,672 words |

SKILL.md grew by the library-skill section and the agent-ready adoption steps. The references shrank: `choosing.md` went from 1,323 to 823 words, and the two library-skill usage references merged into one.

## Limits

- **Few runs:** one run per trigger prompt and two per quality cell, all on one model, graded by Sonnet.
- **Partial rerun:** after the fixes, only the new version was rerun, and only on the two tasks they target. The other three tasks weren't rerun.
- **The session note can answer a trigger prompt without a load,** as on the pin-mismatch prompt. That counts as a miss here, though the answer was right.
- **Simulated hook:** `session_hook.py` stands in for the plugin's hook, and its note's interpreter path is rewritten to `python`. Its absolute path to the clone script means a cloning run used the plugin's copy, not the project's.
- **Refused commands:** `bash scripts/check.sh`, `pesde install` and shell writes were refused, which hit the Blink adoption task hardest. No run could install, generate code or run the project's full check.
- **No web access:** no run could check a current release.
- **Rubric changed after the runs:** criterion G2 (clone `roblox-blink`) gained "or explains why it couldn't", to match K1. No first-round run met it either way.
- **Partial blinding:** responses name reference files, such as `library-skills.md`, that exist in only one version.
- **Grep could reach the skills:** they sit inside the project. A plugin install sits outside it.
- **Spend:** the trigger runs cost $1.59, the quality runs $2.77 and the rerun $0.90, $5.26 in all, not counting grading.
