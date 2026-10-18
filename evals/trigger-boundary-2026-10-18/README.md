# Acquisition and structure boundary, before and after #80 (2026-10-18)

This checks whether [#80](https://github.com/osabased/osaskills/pull/80) improved triggering for `roblox-resource-acquisition` ("acquisition") and `structure-roblox-projects` ("structure"). "Old" is the skills at 3ca1e05, the commit before #80. "New" is 2288538, the merge of #80. Both trees came from `git archive`.

Method, reused from [agent-optimization-2026-10-17](../agent-optimization-2026-10-17/README.md): headless Claude Code 2.1.296 with `claude -p`, a fresh scaffold copy per run, project settings only, no connectors, and Bash, edits, web and subagents denied with a 3-turn limit. [driver.py](driver.py) calls that eval's `run()`, so installs and isolation are identical. A run's route is which of the two skills it loaded, through the Skill tool or by reading its `SKILL.md`: acquisition, structure, both or neither. Models: `sonnet` and `haiku`. Runs per prompt and version: Sonnet 3 and Haiku 5 for the boundary and anchor prompts, Sonnet 1 and Haiku 5 for the structure spot-checks. The 21 prompts are in [cases.json](cases.json); results are one JSON per run in `results/`, with the logs beside them. Spend: $8.25 for 308 runs, not counting grading, and there was no grading.

A run passes when it loads the expected skill. "Both" also passes when a skill is expected, since the second load is noise, not a misroute. For `own-signal-class` and the other negatives, only "neither" passes.

Installs and scaffolds:
- **Boundary and anchor prompts:** installed as [resource-revamp](../resource-revamp-2026-10-15/) installed them (top-level skills, no library clones, its SessionStart hook), on the [structure-revamp](../structure-revamp-2026-10-15/) scaffold. That scaffold already holds `rokit.toml`, `wally.toml`, `pesde.toml` and `selene.toml`, so "set up Wally for a new project" runs in a repo with a `wally.toml`.
- **Structure spot-checks:** installed as the srp suite (every skill and library skill) on the base scaffold.

## Verdict

The boundary routes better on Sonnet and no worse on Haiku, but #80 regressed acquisition's core triggers on Haiku. On Sonnet, 9 of 9 boundary prompts route correctly in the new version against 8 of 9 in the old one: the old version sent `rokit-stylua` to structure 3 of 3 times, and the new one sends it to acquisition 3 of 3. Sonnet is unchanged everywhere else, including all three structure-owned setup prompts and `own-signal-class`. On Haiku the first-time setup prompts held steady or improved (`setup-wally-new-project` went from acquisition-or-both 5 of 5 to structure 4 of 5, `set-up-rokit` from 2 to 3 of 5), and the negatives stayed clean. The regressions are in acquisition's other triggers, and they trace to the dropped wording. `upgrade-pinned-vide` fell from 5/5 to 0/5 and `add-signal-wally` from 4/5 to 1/5, which is more than the 2-of-5 run-to-run noise measured earlier. `write-profilestore-skill` fell from 4/5 to 2/5, which is within noise. The new description no longer says "refreshing a pinned version" or "installing or setting up a Wally, pesde or npm package"; the removed text read as a general trigger, and the replacement ("adding, pinning or upgrading a specific … package or tool") isn't one Haiku matches. The structure trim cost nothing on Sonnet; on Haiku `t-glob` fell from 3/5 to 1/5 (borderline noise), and the other spot-checks matched. Regressed on Haiku: `upgrade-pinned-vide`, `add-signal-wally`, and possibly `write-profilestore-skill` and `t-glob`.

## Boundary prompts

Cells are passes out of runs; "→" shows how the new routes differ when there is a pattern.

| Prompt | Expected | Sonnet old | Sonnet new | Haiku old | Haiku new |
| --- | --- | --- | --- | --- | --- |
| setup-wally-new-project | structure | 3/3 | 3/3 | 3/5 (3 both, 2 acquisition only) | 4/5 |
| first-time-selene-config | structure | 3/3 | 3/3 | 2/5 | 2/5 |
| set-up-rokit | structure | 3/3 | 3/3 | 2/5 | 3/5 |
| profilestore-wally-toml | acquisition | 3/3 | 3/3 | 1/5 | 1/5 |
| selene-pin-bump | acquisition | 3/3 | 3/3 | 0/5 | 0/5 |
| rokit-stylua | acquisition | **0/3** (structure) | **3/3** | 0/5 | 0/5 |
| vide-skill-missing | acquisition | 3/3 | 3/3 | 3/5 | 4/5 |
| write-profilestore-skill | acquisition | 3/3 | 3/3 | 4/5 | 2/5 |
| own-signal-class | neither | 3/3 | 3/3 | 5/5 | 5/5 |

Where a Haiku run fails it almost always loads neither skill: it greps the project and answers directly. The one clear boundary miss in the other direction is `setup-wally-new-project` under the old description, where 2 of 5 Haiku runs loaded only acquisition. The new description never did that.

## Anchors and structure spot-checks

| Prompt | Expected | Sonnet old | Sonnet new | Haiku old | Haiku new |
| --- | --- | --- | --- | --- | --- |
| add-signal-wally | acquisition | 3/3 | 3/3 | 4/5 | **1/5** |
| pesde-install-blink | acquisition | 3/3 | 3/3 | 3/5 | 3/5 |
| upgrade-pinned-vide | acquisition | 3/3 | 3/3 | 5/5 | **0/5** |
| folder-layout | structure | 3/3 | 3/3 | 5/5 | 5/5 |
| write-tween | neither | 3/3 | 3/3 | 5/5 | 5/5 |
| t-entry (placement) | structure | 1/1 | 1/1 | 0/5 | 0/5 |
| t-glob (Rojo config) | structure | 1/1 | 1/1 | 3/5 | 1/5 |
| t-remote | structure | 1/1 | 1/1 | 1/5 | 2/5 |
| t-playtest (Studio MCP) | structure | 1/1 | 1/1 | 5/5 | 5/5 |
| t-guard | structure | 1/1 | 1/1 | 0/5 | 0/5 |
| t-ci | structure | 1/1 | 1/1 | 4/5 | 4/5 |
| t-neg-tween | neither | 1/1 | 1/1 | 5/5 | 5/5 |

Sonnet loads structure on every spot-check in both versions, so the trimmed description still triggers on placement, Rojo config, play-tests and guards. Haiku's 0/5 on `t-entry` and `t-guard` are the same in both versions and match its known weakness at this turn limit.

## Proposed wording

The two failing Haiku cases both lost a phrase in #80. Restoring them in acquisition's package clause, without touching the boundary sentence, would keep the setup routing and recover the triggers:

> adding, installing, pinning or upgrading a specific Wally, pesde, npm (roblox-ts) or Rokit package or tool, including bumping a pinned version;

That is about 40 characters longer. Acquisition's description is now about 986 characters, so it fits under 1,024, but only just. If it does not, shorten "Also use when a task uses Vide, Charm, UI Labs, Bootstrapper, Janitor, LemonSignal, Blink or Nevermore UI and the project lacks its skill" instead of dropping the clause above. Structure's description is at 1,022 and needs no change on this evidence. I did not edit any `SKILL.md` or rerun the proposal.

## Limits

- **Haiku noise:** earlier evals measured about 2 of 5 between identical runs. The `add-signal-wally` and `upgrade-pinned-vide` drops are larger than that; `write-profilestore-skill` and `t-glob` are not.
- **Few Sonnet runs:** 3 per boundary prompt and 1 per spot-check, with no failures in the new version, so a rare Sonnet miss would not show.
- **Prompts are short and context-free.** `profilestore-wally-toml` and `selene-pin-bump` tell the agent which file to look in, which may help or hurt depending on the scaffold. `vide-skill-missing` runs without any Vide skill installed, as the prompt says.
- **A load is not a good answer.** This measures routing only; nobody graded what the runs said.
- **3-turn limit:** a skill loaded after the limit counts as a miss.
- **Description lengths** were taken from the frontmatter lines in each commit, not from the 1,024-character validator.

## Rerun with the proposed wording

The package clause was changed to the proposed wording and the "Also use when" clause was shortened ("or a roblox-* skill's pin or guidance is wrong"), which brings the description to 1,005 characters; the proposal alone came to 1,035. In this rerun's results, "old" is 2288538 (#80) and "new" is the edited description. Same method, 7 prompts, Haiku 5 runs and Sonnet 3 runs each, driver run with `--out results/rerun` ([rerun.log](rerun.log), [results/rerun](results/rerun)). Spend: $3.53.

| Prompt | Expected | Sonnet 2288538 | Sonnet edited | Haiku 2288538 | Haiku edited |
| --- | --- | --- | --- | --- | --- |
| upgrade-pinned-vide | acquisition | 3/3 | 3/3 | 0/5 | **5/5** |
| add-signal-wally | acquisition | 3/3 | 3/3 | 0/5 | **2/5** |
| write-profilestore-skill | acquisition | 3/3 | 3/3 | 4/5 | 5/5 |
| setup-wally-new-project | structure | 3/3 | 3/3 | 5/5 | 5/5 |
| set-up-rokit | structure | 3/3 | 3/3 | 5/5 | 5/5 |
| first-time-selene-config | structure | 3/3 | 3/3 | 3/5 | 3/5 |
| own-signal-class | neither | 3/3 | 3/3 | 5/5 | 5/5 |

`upgrade-pinned-vide` is back to its pre-#80 rate (5/5). `add-signal-wally` recovered only partly: 2/5 against 4/5 before #80, and the failing runs load neither skill. That is inside the roughly 2-of-5 run-to-run noise measured earlier, so it is not clearly recovered or clearly not. The setup prompts still route to structure on both models, with no run sent to acquisition, and `own-signal-class` stays clean. The Haiku baseline differs from the first run (`add-signal-wally` 0/5 against 1/5, `setup-wally-new-project` 5/5 against 4/5), which gives a sense of the noise.
