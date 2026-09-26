# Direction-selection behavioral cases

These fictional, closed-world cases test recommendations, evidence use, commitment boundaries, and proportionality. They are not production instructions, an automatic grader, or evidence that a skill revision improves model performance. Ordinary skill invocations do not load this directory.

## Run a comparison

Use [cases.json](cases.json). Each case contains a self-contained `prompt`, grader-only `accept` and `reject` expectations, a behavior `family`, and optional `related` case IDs. Never expose grader fields or other cases to the evaluated agent. The supplied measurements are fixtures, not real-world claims.

Run fresh, isolated sessions with the same model, reasoning setting, available tools, and per-case budget under three conditions:

1. No direction-selection skill or equivalent injected instructions.
2. The baseline skill at `b25f6bdc67ee295be4196f7393a39367bc0f4a0c`.
3. The revised skill at the exact candidate commit.

In the two skill conditions, load that version's `SKILL.md` and make only its own runtime references available for conditional reading. Explicitly ask it to use direction-selection, then supply the case prompt. Do not include this README, answer expectations, implementation discussion, or a previous run's transcript. In the no-skill condition, supply only the case prompt. Treat this as an outcome comparison, not a test of automatic skill triggering.

Most cases permit a reasonable full/lightweight distinction; do not force one unless routing is what the case tests. User-facing responses need not print internal schemas. Baseline/no-skill runs are judged on substantive decisions, not revised vocabulary or output formatting.

For example, from the repository root, this standard-library command emits only one prompt:

```sh
python -c "import json; from pathlib import Path; cases=json.loads(Path('skills/direction-selection/evals/cases.json').read_text(encoding='utf-8')); print(next(c['prompt'] for c in cases if c['id']=='uncertainty-accepted'))"
```

## Judge outcomes, not protocol recitation

Fix the rubric before reading a revised run. Record each acceptance expectation as met, missed, or unclear, with the actual response excerpt supporting that judgment. Record any rejected behavior separately. Equivalent wording and explicitly allowed alternative outcomes are valid. An unsupported recommendation does not pass merely because it contains `Direction Gate: PASS`.

Compare wrong recommendations, missed feasible alternatives, unsupported deciding claims, unjustified blockers, and boundary violations first. Track unnecessary questions, tool calls, tokens, and elapsed time separately. Do not claim efficiency gains when the runtime does not expose the relevant measurement. For open-ended extensions, specify acceptable outcomes or an outcome-based rubric before running the agents rather than grading agreement with the skill author.

Repeat inconsistent or consequential cases with a fixed, predeclared repeat count. Run paired cases in separate sessions: changing a deciding criterion, observation, or refinement cost should produce the specified change in outcome. Also repeat suitable cases after reversing candidate presentation order or adding a nonbinding user favorite; keep the evidence and objectives unchanged. Do not pool transformed runs as independent evidence without identifying the transformation.

`uncertainty-accepted`, `uncertainty-unacceptable`, `uncertainty-preference`, `uncertainty-probability`, and `constraint-unverified` jointly test that accepting outcome uncertainty does not excuse missing evidence, preferences, or constraint compliance. The three `refinement-*` cases test both useful refinement and stopping. `lightweight-known-choice` checks that the shared semantics also apply without full-mode expansion. The remaining safeguard cases exercise authority, ownership, framing, ties, reopening, and bounded adaptation.

## Record limitations and stop

For every run, retain the case ID, condition, exact skill commit, model/settings, response or trace, rubric judgments, and available cost measurements outside the evaluated agent's context. Record unavailable metrics and checks not run explicitly. Do not add model calls to repository CI or assume this suite is automatically executed.

A static walkthrough can identify contradictory rules or bad fixtures; it is not an independent agent run or a measured before/after improvement. Retain a behavioral change after checking its targeted cases and affected safeguards; correct concrete failures rather than adding speculative instructions. A claim of improved agent performance requires actual comparative runs. Do not tune repeatedly to these examples and then treat them as held-out evidence; add new cases from real failures as needed.
