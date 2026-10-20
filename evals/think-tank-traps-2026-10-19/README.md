# think-tank against a single session, on trap questions (2026-10-19)

This checks whether [think-tank](../../skills/think-tank/) reaches the right call more often than asking one Opus session the same question, and what that costs. It runs the skill as changed in [#89](https://github.com/osabased/osaskills/pull/89). A second round on 2026-10-20 added two cheaper arms, to test whether checking sources alone closes the gap.

Each case in [cases.json](cases.json) is a decision with a verified answer. A **trap** is one whose confident answer is wrong. A **control** is one whose obvious answer is right, so a panel that is merely cautious doesn't score well.

## Setup

Four arms, all on Opus at `--effort high`, with headless Claude Code 2.1.296. The first round ran single and panel, and the second round ran verify and solo.
- **single:** the question, as typed, in one session.
- **verify:** the same, with one more line: "Before answering, check the current official documentation, and say which claims you verified."
- **solo:** `/think-tank-solo <question>`, a variant of the skill kept in [think-tank-solo](think-tank-solo/SKILL.md). It writes the brief as think-tank does and asks one Opus `think-tank-member`, with no debate. Then it checks the facts the answer rests on and reports with a `Checked:` line.
- **panel:** `/think-tank <question>`, so the skill uses its default `opus,sonnet,sonnet` panel at session effort.

Every run gets a fresh temporary project holding this checkout's think-tank skill and panelist agent, and in the second round the solo variant too. [harness.py](harness.py) runs it there.

Isolation:
- `--setting-sources project,local` keeps the installed osaskills plugin and the user's saved advisor out. No panelist had the advisor attached.
- `claudeMdExcludes` keeps the user's `~/.claude/CLAUDE.md` out, which `--setting-sources` doesn't.
- Permission deny rules stop reads of:
  - this repository, which holds the answer key;
  - this project's past session transcripts;
  - installed plugins and skills;
  - transcripts of other runs of the same case.

  A Haiku probe confirmed that Read, Glob and Grep are blocked there, and that a broad Grep of `~/.claude` skips those folders.
- Edits, shell commands and MCP servers were denied. Web search and fetch were allowed in every arm.
- By the second round the answer key was public on GitHub. Other GitHub pages hold sources the runs used, so a hook, [block_key.py](block_key.py), blocks fetches of the repo's URLs instead of a deny rule on the whole domain. The harness also flags any lookup whose input or result names the repo.
  - A Haiku probe confirmed the hook blocks a fetch in the session and in a panelist, and lets other pages through.
  - No second-round run touched the repo.
- Each prompt ends "The project I'm describing isn't in this directory." Without it, the first round's runs hunted for files the question names.

Panel and solo runs also record each panelist's answer to every message it got, from the run's subagent transcripts. The harness deletes those transcripts afterwards.

## Rounds

- **Pilot** (`results/pilot`): one trap and one control, one run per arm. It ran before the deny rules and the prompt suffix existed, so it is kept only as a record. Cost $2.53.
- **Calibration 1** (`results/calibration-1`): one single run per case. It cost $1.09. Its prompt suffix ended "so answer from what I've said", which likely discouraged lookups: 7 of 10 runs looked nothing up.
- **Calibration 2** (`results/calibration-2`): the same, with the neutral suffix. It cost $1.63, and 6 of 10 runs looked something up.
  - Across both calibrations, the single session never got `fork-wait` right.
  - It hedged on `local-md-agents` both times.
  - It got `scriptsync-client` and `live-scripting` right once each.
  - It got `advisor-disallow`, `advisor-sonnet` (on the decision), `rojo-sourcemap` and `pesde-sync` right both times, so those four were dropped.
- **Full** (`results/full`): those 4 traps and both controls, with 3 single and 2 panel runs per case. All 30 are fresh runs, not the calibration ones. Cost $12.98.
- **Pilot 2** (`results/pilot-verify-solo`): `fork-wait` and `control-tools`, one verify and one solo run each, to check the new arms ran as meant. It cost $1.24 and wasn't graded.
- **Full verify and solo** (`results/full-verify-solo`): the same 6 cases, with 3 verify and 3 solo runs per case. All 36 are fresh runs. Cost $9.93.

## Grading

[blind.py](blind.py) wrote one file per case to `grading/`, holding:
- the question;
- 11 shuffled, unlabelled answers: 3 single answers, 2 panel syntheses and 6 panelist round-1 answers.

Run directory names, which name the arm, were masked. The key stayed outside the folder until grading ended.

One Opus grader at high effort read only [rubrics.md](grading/rubrics.md) and the six case files. For each answer it gave:
- a verdict: `right`, `trap` or `hedge`;
- whether the answer stated the deciding fact.

`grading/key.json` maps labels to runs, and `grading/grades.json` holds the grades. [tally.py](tally.py) joins them.

The second round was graded the same way in its own pass, in `grading/verify-solo/`. Each case file held 9 answers: 3 verify answers, 3 solo reports and the 3 solo panelists' answers. A fresh Opus grader at high effort read only the same rubrics and those six files.

## Results

| Case | Single (3 runs) | Verify (3 runs) | Solo (3 runs) | Panel final (2 runs) | Panelists' round 1 (6 answers) |
| --- | --- | --- | --- | --- | --- |
| fork-wait (trap) | trap, trap, trap | right ×3 | right ×3 | right, right | 6 right |
| live-scripting (trap) | hedge, hedge, trap | right ×3 | right ×3 | right, right | 6 right |
| local-md-agents (trap) | hedge, right, right | right ×3 | right ×3 | right, right | 6 right |
| scriptsync-client (trap) | right, right, right | right ×3 | right ×3 | right, right | 5 right, 1 trap |
| control-tools | right ×3 | right ×3 | right ×3 | right ×2 | 6 right |
| control-sort | right ×3 | right ×3 | right ×3 | right ×2 | 6 right |

| | Traps right | Controls right | Mean cost | Mean time | Web lookups per trap run |
| --- | --- | --- | --- | --- | --- |
| Single | 5 of 12 (4 trap, 3 hedge) | 6 of 6 | $0.11 | 0.4 min | 1.0 |
| Verify | 12 of 12 | 6 of 6 | $0.19 | 0.9 min | 4.4 |
| Solo | 12 of 12 | 6 of 6 | $0.36 | 2.0 min | 8.7 (6.9 by the panelist) |
| Panel | 8 of 8 | 4 of 4 | $0.92 | 3.1 min | 21.9 (20.0 by panelists) |

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
- **One line asking for the docs matched the panel, at a fifth of its cost.** Verify got all 12 trap answers right, as solo and the panel did.
  - It cost $0.19 a run, against $0.11 for single, $0.36 for solo and $0.92 for the panel.
  - The line changed what the session did. Every verify run looked something up, 4.4 times per trap run on average. Single runs averaged 1.0, and 5 of their 12 trap runs looked nothing up.
  - On `fork-wait`, all 3 verify runs fetched the sub-agents docs and said fork mode stops Claude from waiting. The verify line doesn't point at that mechanism. The solo briefs did (see Limits).
  - One verify `fork-wait` answer made the right call, but its main fix was to make the skill a `context: fork` skill rather than wait for the notifications. The rubric grades the call, so it counts as right.
- **One panelist was enough.** All 18 solo panelist answers were right before the orchestrator checked them, and its check changed no call.
- **No over-caution on the controls.** All 22 final control answers, across the four arms, were right.
  - The pilot's one control-tools panel had leaned toward "not enough on its own". It wasn't graded.
  - In both rounds the grader noted control-tools answers that said "enough" while suggesting a backstop. It graded them on their stated call.
- **Every panel and solo report had a `Checked:` line**, and no panelist called the advisor.
- **Cost:** a panel run cost about 8 times a single run and took about 8 times as long. About three quarters of its cost was Opus: the orchestrator plus one panelist. A solo run cost about two fifths of a panel run, and a verify run about a fifth.

## Limits

- **Few runs:** 2 panel runs and 3 runs of each other arm per case, on 4 traps. The results show a direction, not a rate.
- **Traps were picked because a single session failed them in calibration.** So this shows checking sources helps where a session's memory is wrong. It doesn't show how often that happens. On the four dropped traps, a single session was already right.
- **These traps can't separate the arms that look things up.** Each one is settled by one docs page, and verify, solo and the panel got every one right. Questions the docs don't settle were not tested: thin or conflicting sources, or judgement calls. There, the panel's independent views and debate may count for more.
- **Brief framing:** the orchestrator wrote each brief after reading the question. The panel's `fork-wait` brief asked panelists to establish "whether results can arrive later as notifications", and all 3 solo briefs asked much the same. That points at the mechanism without stating the answer. The verify line has no such hint and got `fork-wait` right 3 times.
- **The solo panelist's instructions still say it is one of three panelists**, since the eval used `think-tank-member` unchanged.
- **Headless only:** `claude -p` can wait for subagents, so this doesn't test round 1 collecting answers in the background.
- **Partial blinding:** a panel or solo report looks different from a single or verify answer, so the grader could tell them apart. Most verdicts turn on a stated yes or no.
- **Two passes, one grader each:** the second pass held only verify and solo answers, and it graded all 54 right, so no answer in it stood in contrast. Neither pass was checked by a second grader.
- **The answer key is public:** the hook blocks fetching it, but search results can't be filtered that way, so the harness only flags them. None named the repo.
- **Isolation differs from real use:** the user's CLAUDE.md and advisor were off.

## Spend

| Step | Runs | Cost |
| --- | --- | --- |
| Smoke test and access probes (Haiku, Sonnet) | 6 | $0.04 |
| Pilot | 4 | $2.53 |
| Calibration 1 | 10 | $1.09 |
| Calibration 2 | 10 | $1.63 |
| Full | 30 | $12.98 |
| Hook probe and smoke test of the new arms (Haiku) | 4 | $0.02 |
| Pilot 2 | 4 | $1.24 |
| Full verify and solo | 36 | $9.93 |
| **Total** | 104 | **$29.46** |

The Opus graders used about 160k and 137k tokens on top, not metered here.

To rerun the full step from this folder:
1. `python harness.py --arms panel --reps 2 --effort high --out results/full <case ids>`
2. The same with `--arms single --reps 3`.
3. `python blind.py --results results/full --key <path outside this folder>`
4. Grade the files in `grading/`.
5. `python tally.py --results results/full --key <key> --grades grading/grades.json`

To rerun the second round:
1. `python harness.py --arms verify,solo --reps 3 --effort high --out results/full-verify-solo <case ids>`
2. `python blind.py --results results/full-verify-solo --key <path outside this folder> --out grading/verify-solo`
3. Grade the files in `grading/verify-solo/`.
4. `python tally.py --results results/full-verify-solo --key <key> --grades grading/verify-solo/grades.json`

A smoke test that costs about $0.02: `--model haiku --effort low --panel-args "haiku low"`.
