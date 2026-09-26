# Preference-discovery behavioral cases

These fictional, closed-world cases test preference interpretation, scope, authority, useful exploration, and stopping. They are not runtime instructions, an automatic grader, or evidence of improved model performance. Ordinary skill use does not load this directory.

## Compare behavior

Use [cases.json](cases.json). Each case has a self-contained `prompt`, a behavior `family`, grader-only `accept` and `reject` expectations, and optional `follow_up` or `related` case IDs. For a multi-turn case, send `follow_up` verbatim after the first response and judge the entire exchange. Do not adapt the follow-up to rescue a failed run. Keep expectations, related cases, this README, and implementation discussions out of the evaluated agent's context.

Run fresh, isolated sessions with the same model, reasoning setting, tool availability, and per-case budget under three conditions:

1. No preference-discovery skill or equivalent injected instructions.
2. Baseline `skills/ui-direction-discovery/SKILL.md` at `3060aae885ed60c54e3b41ad62eac1e7025333f6`.
3. Revised `skills/preference-discovery/SKILL.md` at the exact candidate commit.

For the two skill conditions, explicitly ask the agent to use that version's skill before supplying the prompt. Load only that version's runtime instructions. Case-stated tool limits apply in every condition; do not quietly give one condition playback, browsing, or rendering capabilities absent from another. The supplied facts and described references are fixtures, not actual inspected media or claims about real tools.

This comparison tests behavior after invocation, not automatic triggering. Test triggering separately in a skill-aware runtime: register only the target version normally, omit explicit skill invocation, and use positive requests such as `ambiguous-tone`, `unknown-not-consent`, and `reconsider-alternatives`, alongside false-positive checks such as `explicit-writing`, `indifferent-format`, and `factual-not-preference`. Measure invocation only when exposed by the runtime; plausible response text alone does not prove which skill was loaded. The baseline's UI-only scope is a known limitation, not an expectation to hide when reporting the broadened scope.

For example, from the repository root, this standard-library command emits only one case's initial prompt:

```sh
python -c "import json; from pathlib import Path; cases=json.loads(Path('skills/preference-discovery/evals/cases.json').read_text(encoding='utf-8')); print(next(c['prompt'] for c in cases if c['id']=='ambiguous-tone'))"
```

## Judge outcomes, not ceremony

Fix the rubric before reading outputs. Record each acceptance expectation as met, missed, or unclear, supported by an excerpt or tool trace. Record rejected behavior separately. Equivalent wording and explicitly allowed alternatives are valid. A response does not pass just because it prints an Interpretation heading, evidence labels, or the revised skill's terminology. Do not punish baseline or no-skill responses for omitting that vocabulary.

Check invented preferences, violations of authorization, missed explicit requirements, and false validation claims first. Track unnecessary questions, redundant confirmations, excessive samples, premature specification, and failure to finish the requested work separately. Record tools, tokens, and elapsed time only when those metrics are available. A new instruction is not an efficiency gain merely because it sounds concise.

Use paired safeguards: `indifferent-format` with `unknown-not-consent`, `authorized-code-probe` with `restricted-experiment`, and `local-preference-scope` with `explicit-broad-scope`. Changes should not fix one side by breaking the other. Include the UI and motion cases when testing generalized coverage so that non-UI gains do not conceal UI regressions.

Repeat consequential or inconsistent cases with a repeat count chosen before reviewing results. Useful additional checks reverse option order while preserving the actual content-to-label mapping, or change a material permission or preference to verify that behavior changes accordingly. Record these as transformed runs, not independent evidence. Keep genuinely new cases from real failures separate from cases repeatedly used to tune the skill.

## Record limitations

Retain the case ID, condition, exact commit, model/settings, response or trace, judgments, and available cost measurements outside the evaluated agent's context. Record unavailable metrics and checks not run. The repository CI validates case structure and rename consistency only. It does not run these prompts against a model; do not add model calls or interpret a green static check as behavioral success.

A schema check or author walkthrough can catch malformed fixtures and conflicting instructions. It is not an independent agent evaluation or a measured before/after improvement. Scripted cases cannot establish whether real users find discovery helpful or prefer the resulting work; that requires actual interaction and, where relevant, the rendered, playable, or audible artifact.

## Rename checks

The baseline path above is intentionally historical. For a full checkout, search active references after a rename:

```sh
git grep -n -E 'ui-direction-discovery|ui-discovery|UI Direction Discovery|UI Discovery' -- . ':!skills/preference-discovery/evals/README.md'
```

No matches are expected. Check the catalogue link and the new front-matter name as well. Repository checks do not establish that external prompts, installed copies, or links have been migrated; use `preference-discovery` when updating those references. There is no duplicate legacy skill to compete for invocation.
