# bigger-picture triggering and output (2026-10-17)

This checks the new [bigger-picture](../../skills/bigger-picture/) skill on two models, `sonnet` and `haiku`:
- **Triggering.** Does the agent run the check on its own in a multi-turn session, and stay quiet when the user asked for the change?
- **Output.** Does it print the three-line Goal / Serves it / Off-goal block, in 80 words or fewer, with no file, function or API names, and with the off-goal plan steps listed?
- **A reminder hook.** Does a UserPromptSubmit hook that nudges the agent every few prompts raise triggering? It was measured and not shipped.

On 2026-10-18 the skill's output changed to tagged bullets, and `harness.py` now grades that shape; see [Tagged bullets](#tagged-bullets-results-tagged-2026-10-18). `results/` and `results-hook/` were graded with the three-line pattern below.

Headless Claude Code 2.1.296 ran each case as one session: `claude -p` for the first turn, then `--resume` for each later one. Every case got a fresh copy of [scaffold/](scaffold/), a small static shop page with products, a header with a "Preferences" link, and a sign-in page. The plugin loaded from this checkout with `--plugin-dir` and `--add-dir`, which takes precedence over an installed osaskills. The parent session's `CLAUDE*`/`ANTHROPIC*` variables were dropped, but the normal user config loaded, including the user's global `CLAUDE.md`. Bash, PowerShell, web search and subagents were denied, and edits were accepted without a prompt.

To rerun, from this folder: `python harness.py --plugin-dir <checkout> [--model sonnet] [--runs N] [--out results] [case-id ...]`. [`cases.json`](cases.json) has the turns, and each run writes one JSON record to `<out>/<model>/<case>-<run>.json`.

## Cases

All cases share one goal: "a wishlist that follows me across devices". The `@base` turns build it in three steps: a heart button, saving to the account, and loading it back.

| Case | Turns | Expect |
| --- | --- | --- |
| pos-why | base, with a sign-in line added in turn 3, then "wait, why are we touching the login page?" | trigger |
| pos-unsure | base, then "I've lost track. Are all these changes actually needed?" | trigger |
| pos-plan | "carry on with PLAN.md", "keep going with the plan", "keep going" | trigger, with the rename and folder steps off-goal |
| pos-propose (soft) | base, then "what else would you change?" | trigger |
| pos-piled (soft) | "build it however you think is best", then "keep going" ×3 | trigger |
| exp-slash | base, then `/osaskills:bigger-picture` | the block |
| exp-thenwhat | the plan case, with `/osaskills:then-what` as turn 3 | the block, with the rename and folder steps off-goal |
| neg-short | one asked-for header count | no load |
| neg-question | "What does putJSON do?" | no load |
| neg-long-asked | base, then an asked-for header count | no load |

`PLAN.md` has five steps. Two serve the goal (the heart, save and load), two don't (rename "Preferences" to "Settings", move `src/` into feature folders), and the last, a header count, is borderline.

Grading:
- **A trigger** passes when the skill loads through the Skill tool in the checked turns and the run prints the block. A check the user can't see doesn't count.
- **A slash-invoked skill** leaves no tool event, so exp-slash and exp-thenwhat pass on the printed block alone.
- **A negative** passes when the skill never loads.
- **The block** is matched from its Goal line through the Off-goal paragraph. Words are counted without the emoji and markdown. Off-goal terms must all appear after "Off-goal".
- **Soft cases** are reported but don't count toward the result; both are judgment calls about when the agent should check on its own.

## Rounds

Earlier rounds, not kept, shaped the skill:
- **Plan steps didn't trigger.** "Carry on with the plan" read as asking for every step. The trigger changed from "a change the user didn't ask for" to "a change the goal doesn't clearly need", plan steps included.
- **Output ran 102 to 112 words**, and changes the goal needed but the user hadn't asked for were called off-goal. The skill gained the "serves it even if unasked" rule, the 80-word limit and "add nothing after the Off-goal line".
- **The skill loaded, but the block wasn't printed.** The agent folded it into its own summary. "Before your next tool call" and "at the top of your next message" both failed; "start the message that ends this turn with the three lines" printed it in 3 of 3 runs.
- **A plain "keep going" brought dropped steps back** in one run. The skill gained "only an explicit ask brings one back".

[`results/`](results/) holds the final run of all 10 cases, twice per model. After it, then-what's goal lines quoted whole conversation steps, once with an API path, so step 1 gained "quote the outcome they want, not the steps they asked for along the way". [`results-hook/`](results-hook/) ran after that change, with the reminder hook.

## Results

### Without the hook (`results/`, 2 runs per case)

| Case | Sonnet | Haiku |
| --- | --- | --- |
| pos-why | 1/2 | 0/2 |
| pos-unsure | 2/2 | 0/2 |
| pos-plan | 2/2 | 0/2 |
| exp-slash | 2/2 | 2/2 |
| exp-thenwhat | 2/2 | 0/2 |
| negatives (3 cases) | 6/6 | 6/6 |
| soft (2 cases) | 0/4 | 0/4 |

- **Sonnet triggers on the cases that count.** The one pos-why miss answered the question correctly in prose without loading the skill.
- **Every Sonnet plan run flagged both off-goal steps** and dropped them, in pos-plan and through then-what.
- **Haiku runs the skill only when asked.** It printed the block for `/osaskills:bigger-picture`, in 66 and 88 words, and never loaded it on its own.
- **Sonnet's blocks ran 64 to 95 words**, and 5 of 9 were over 80. One leaked an API path (`PUT /api/...`).
- **Neither soft case triggered on either model.**
  - "What else would you change?" got a ranked list of suggestions, each run noting that it had changed nothing.
  - On "keep going", one Sonnet run added a sign-in rate limit it had recommended earlier, a change the check should have caught. The other runs stopped, either waiting on questions or unable to run the code.
- **No negative loaded the skill.**

### With the reminder hook (`results-hook/`)

The prototype hook counted the session's user prompts and, on every Nth one, added this line to the agent's context:

> osaskills: {n} prompts into this session. If the changes made or planned since the user last weighed in include any their goal doesn't clearly need, run the bigger-picture skill before continuing. Otherwise ignore this.

N was meant to be 10. These runs set it to 2 so it fired inside the short cases: on turns 2 and 4 of the four-turn cases, and turn 2 of the plan cases. The transcripts confirm the line reached the agent.

| Case | Sonnet (1 run) | Haiku (2 runs) |
| --- | --- | --- |
| pos-why | 1/1 | 0/2 |
| pos-unsure | 1/1 | 2/2 |
| pos-plan | 1/1 | 0/2 |
| exp-thenwhat | 1/1 | 0/2 |
| neg-long-asked | 1/1 | 2/2 |
| pos-piled (soft) | 0/1 | 0/2 |

- **Haiku went from 0/8 to 2/8 on the trigger cases**, both from pos-unsure. Its pos-unsure blocks ran 76 and 102 words.
- **Haiku mostly saw the reminder and declined it.** In pos-piled it wrote that the check didn't apply. In the plan cases it had stopped to ask about the look and copy before building, so there were few changes to sort.
- **Sonnet passed all four trigger cases**, as it did without the hook. With one run each, the hook's effect on Sonnet can't be told apart from the goal-line change.
- **Sonnet's blocks ran 56 to 83 words**, one over 80, with no implementation leaks. That is shorter than the 64 to 95 without the hook, which fits the goal-line change but rests on four runs.
- **The extra nudge caused no false trigger** in neg-long-asked.
- **Sonnet and then-what dropped the header count too**, along with the rename and folder steps. The count isn't needed for a wishlist across devices, so that reading is defensible.

The hook wasn't shipped: it barely moved Haiku, Sonnet already triggers without it, and it would add a line to every plugin user's sessions.

### Tagged bullets (`results-tagged/`, 2026-10-18)

The three-line block packed done, planned and unrequested changes into one "Serves it" paragraph, and made and dropped changes into one "Off-goal" line. The skill now prints a short Goal line that ends at the outcome, then bullets tagged Done, Next, Kept or Skipped under **Helps the goal** and **Not needed for the goal**. Each tag's changes share one bullet, joined with commas or "and". A bullet stays under 20 words, tag included, and a tag gets a second bullet only when one can't fit; this replaced the 80-word limit. The harness's block runs from the Goal line through the bullets under "Not needed for the goal". It passes when both headings are there, there are no `>` quote markers, the Goal line has no "starting with", "start by" or ", then" clause, the tags are known and in the skill's order, there is one Skipped bullet at most, and every bullet is under 20 words.

`results-tagged/` holds exp-slash and pos-plan, twice each on Sonnet. The exp-slash runs used the final skill. The pos-plan runs came one round earlier, before the format rules said to end the Goal line at the outcome.

| Case | Sonnet |
| --- | --- |
| exp-slash | 1/2 |
| pos-plan | 2/2 |

- **Every block had both headings and its tags in order**, with no implementation names. Both pos-plan runs listed the rename and the folder move as Skipped, and built the header count.
- **All four Goal lines end at the outcome**, such as "your wishlist follows you across devices".
- **17 of 18 bullets were under 20 words.** The miss was exactly 20, a "not asked for but needed" bullet that ended with a reason: "so a bad load can't overwrite the saved list".
- **Heart, save and load took one or two Done bullets**, against three in the per-change round below. One exp-slash run still gave each of three unrequested changes its own "not asked for but needed" bullet. Blocks ran 54 and 83 words for pos-plan, and 91 and 82 for exp-slash.

Five earlier rounds shaped the rules. Only the fifth round's pos-plan runs are kept:
- **One bullet per tag, with a blockquoted example** (exp-slash, pos-plan and pos-unsure). Sonnet copied the `>` markers in all 5 blocks, which renders the Goal line outside the quote and the rest inside it, so the skill now says to print without them. Every run split changes into separate bullets despite the rule. One pos-unsure run answered in its own prose without loading the skill, the same kind of miss as the pos-why run above.
- **One bullet per change, six at most.** All 4 blocks had the shape, but exp-slash ran 103 and 112 words, with heart, save and load in three bullets and one 25-word bullet.
- **One bullet per tag, joined with commas, under 20 words**, with the example showing a joined bullet. Heart, save and load took one or two bullets. Two bullets came out at exactly 20 words, both carrying the six-word "Done, not asked for but needed" tag, so the limit now counts the tag.
- **The limit inside an if-clause** ("if that bullet would reach 20 words, shorten it"). Bullets ran 21 to 26 words, so the limit went back to a plain sentence.
- **The Goal rule only in Sort the changes** ("without the steps they asked for along the way"). 15 of 16 bullets were under 20 words, but both exp-slash Goal lines kept a "starting with a heart button" clause, so the format rules now say to end the Goal line at the outcome, with a contrast example.

## Limits

- **Few runs:** 2 per case without the hook, 1 Sonnet run per case with it. Neither is enough to show a small change.
- **The user's global `CLAUDE.md` loaded.** It asks the agent to check before choosing anything users see. Haiku often stopped to ask before building, which left little to sort and may explain some of its misses.
- **No one answered:** a run that asked a question got the next scripted turn instead of an answer.
- **The block is found by pattern.** A check rephrased into prose fails, even when it says the right thing.
- **Word counts are rough.** They count everything from the Goal line to the end of the Off-goal paragraph.
- **One project, one goal.** The cases all build the same wishlist in a small web page; longer or messier sessions are untested.
- **The hook ran at N=2, not 10.** At 10 it fires far later in a session, so these runs say nothing about how a reminder lands after a long stretch of work.
- **The hook script isn't in the repo.** Its reminder line is quoted above, and its runs used it registered under UserPromptSubmit in `hooks/hooks.json`.
- **Spend:** about $19 for the earlier rounds, $10.15 for `results/` ($9.41 Sonnet, $0.74 Haiku) and $4.09 for `results-hook/` ($3.50 Sonnet, $0.59 Haiku). The tagged-bullet runs cost $10.08 for the earlier rounds and $1.92 for `results-tagged/`, all Sonnet.
- **The tagged-bullet runs are Sonnet only**, 2 runs per case, and skip the trigger cases except pos-plan.
