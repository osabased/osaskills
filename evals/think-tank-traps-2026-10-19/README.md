# think-tank against a single session, on trap questions (2026-10-19)

This checks whether [think-tank](../../skills/think-tank/) reaches the right call more often than asking one Opus session the same question, and what that costs. It runs the skill as changed in [#89](https://github.com/osabased/osaskills/pull/89).

Each case in [cases.json](cases.json) is a decision with a verified answer. A **trap** is one whose confident answer is wrong. A **control** is one whose obvious answer is right, so a panel that is merely cautious doesn't score well.

## Setup

Two arms, both on Opus at `--effort high`, with headless Claude Code 2.1.296:
- **single:** the question, as typed, in one session.
- **panel:** `/think-tank <question>`, so the skill uses its default `opus,sonnet,sonnet` panel at session effort.

Every run gets a fresh temporary project holding this checkout's think-tank skill and panelist agent. [harness.py](harness.py) runs it there.

Isolation:
- `--setting-sources project,local` keeps the installed osaskills plugin and the user's saved advisor out. No panelist had the advisor attached.
- `claudeMdExcludes` keeps the user's `~/.claude/CLAUDE.md` out, which `--setting-sources` doesn't.
- Permission deny rules stop reads of:
  - this repository, which holds the answer key;
  - this project's past session transcripts;
  - installed plugins and skills;
  - transcripts of other runs of the same case.

  A Haiku probe confirmed that Read, Glob and Grep are blocked there, and that a broad Grep of `~/.claude` skips those folders.
- Edits, shell commands and MCP servers were denied. Web search and fetch were allowed in both arms.
- Each prompt ends "The project I'm describing isn't in this directory." Without it, both arms hunted for files the question names.

Panel runs also record each panelist's answer to every message it got, from the run's subagent transcripts. The harness deletes those transcripts afterwards.

## Rounds

- **Pilot** (`results/pilot`): one trap and one control, one run per arm. It ran before the deny rules and the prompt suffix existed, so it is kept only as a record. Cost $2.53.
- **Calibration 1** (`results/calibration-1`): one single run per case. It cost $1.09. Its prompt suffix ended "so answer from what I've said", which likely discouraged lookups: 7 of 10 runs looked nothing up.
- **Calibration 2** (`results/calibration-2`): the same, with the neutral suffix. It cost $1.63, and 6 of 10 runs looked something up.
  - Across both calibrations, the single session never got `fork-wait` right.
  - It hedged on `local-md-agents` both times.
  - It got `scriptsync-client` and `live-scripting` right once each.
  - It got `advisor-disallow`, `advisor-sonnet` (on the decision), `rojo-sourcemap` and `pesde-sync` right both times, so those four were dropped.
- **Full** (`results/full`): those 4 traps and both controls, with 3 single and 2 panel runs per case. All 30 are fresh runs, not the calibration ones. Cost $12.98.

## Grading

[blind.py](blind.py) wrote one file per case to `grading/`, holding:
- the question;
- 11 shuffled, unlabelled answers: 3 single answers, 2 panel syntheses and 6 panelist round-1 answers.

Run directory names, which name the arm, were masked. The key stayed outside the folder until grading ended.

One Opus grader at high effort read only [rubrics.md](grading/rubrics.md) and the six case files. For each answer it gave:
- a verdict: `right`, `trap` or `hedge`;
- whether the answer stated the deciding fact.

`grading/key.json` maps labels to runs, and `grading/grades.json` holds the grades. [tally.py](tally.py) joins them.

## Results

| Case | Single (3 runs) | Panel final (2 runs) | Panelists' round 1 (6 answers) |
| --- | --- | --- | --- |
| fork-wait (trap) | trap, trap, trap | right, right | 6 right |
| live-scripting (trap) | hedge, hedge, trap | right, right | 6 right |
| local-md-agents (trap) | hedge, right, right | right, right | 6 right |
| scriptsync-client (trap) | right, right, right | right, right | 5 right, 1 trap |
| control-tools | right ×3 | right ×2 | 6 right |
| control-sort | right ×3 | right ×2 | 6 right |

| | Traps right | Controls right | Mean cost | Mean time |
| --- | --- | --- | --- | --- |
| Single | 5 of 12 (4 trap, 3 hedge) | 6 of 6 | $0.11 | 0.4 min |
| Panel | 8 of 8 | 4 of 4 | $0.92 | 3.1 min |

What the results show:
- **The panel got every trap right; the single session got under half.**
  - `fork-wait` is the clearest case. All 3 single runs answered from memory, with no lookup, that `run_in_background: false` makes Claude wait. Both panels said fork mode stops that from v2.1.232 and cited the docs.
  - On `live-scripting`, two single runs couldn't say which mode is the default, and one said drafts is.
- **The gain came from checking sources, not from the debate.**
  - Round 1 already had a right majority in all 12 panel runs. 23 of 24 round-1 answers on traps were right.
  - The debate changed one panelist, a Sonnet that had concluded `.client.luau` runs once. It moved to the majority, and its panel reported 3–0 with "2–1 before debate".
  - Six of the 12 runs skipped the debate at 3–0.
  - On `fork-wait`, `live-scripting` and `scriptsync-client`, panelists made 4 to 15 web lookups each, and 1 or 2 on `local-md-agents`. The single sessions made none on `fork-wait` and at most 3 elsewhere.
  - The orchestrator's brief turned each question into a research task, for example "Use official Claude Code documentation, changelogs, and release notes where you can find them, and say which claims you verified".
- **No over-caution on the controls.** Both arms got all 10 control answers right.
  - The pilot's one control-tools panel had leaned toward "not enough on its own". It wasn't graded.
  - The grader noted that three control-tools answers in the full run said "enough" while urging extra layers. It graded them on their stated call.
- **Every panel synthesis had a `Checked:` line**, and no panelist called the advisor.
- **Cost:** a panel run cost about 8 times a single run and took about 8 times as long. About three quarters of its cost was Opus: the orchestrator plus one panelist.

## Limits

- **Few runs:** 2 panel runs per case and 4 traps. The results show a direction, not a rate.
- **Traps were picked because a single session failed them in calibration.** So this shows the panel helps where a session's memory is wrong. It doesn't show how often that happens. On the four dropped traps, a single session was already right.
- **The single arm wasn't asked to check sources.** A single session told to verify against the docs, or one panelist given the orchestrator's brief, might close most of the gap at a fraction of the cost. This eval didn't test either.
- **Brief framing:** the orchestrator wrote each brief after reading the question. The `fork-wait` brief asked panelists to establish "whether results can arrive later as notifications". That points at the mechanism without stating the answer.
- **Headless only:** `claude -p` can wait for subagents, so this doesn't test round 1 collecting answers in the background.
- **Partial blinding:** a panel synthesis looks different from a single answer, so the grader could tell them apart. Most verdicts turn on a stated yes or no.
- **One grader:** its grades weren't checked by a second grader.
- **Isolation differs from real use:** the user's CLAUDE.md and advisor were off.

## Spend

| Step | Runs | Cost |
| --- | --- | --- |
| Smoke test and access probes (Haiku, Sonnet) | 6 | $0.04 |
| Pilot | 4 | $2.53 |
| Calibration 1 | 10 | $1.09 |
| Calibration 2 | 10 | $1.63 |
| Full | 30 | $12.98 |
| **Total** | 60 | **$18.27** |

The Opus grader used about 160k tokens on top, not metered here.

To rerun the full step from this folder:
1. `python harness.py --arms panel --reps 2 --effort high --out results/full <case ids>`
2. The same with `--arms single --reps 3`.
3. `python blind.py --results results/full --key <path outside this folder>`
4. Grade the files in `grading/`.
5. `python tally.py --results results/full --key <key> --grades grading/grades.json`

A smoke test that costs about $0.02: `--model haiku --effort low --panel-args "haiku low"`.
