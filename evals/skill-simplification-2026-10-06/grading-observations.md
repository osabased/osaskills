# Blind grading observations

## Descriptive counts

| Batch | Met | Missed | Unclear | Cases with every expectation met |
| --- | ---: | ---: | ---: | ---: |
| A | 58 | 0 | 0 | 18/18 |
| B | 55 | 1 | 2 | 15/18 |
| C | 58 | 0 | 0 | 18/18 |

These are 18 scenarios per condition, with one supplied response per scenario and no repeated trials. The counts describe these fixtures; they do not establish reliability or a general condition ranking. All 174 numbered judgments include exact excerpts in judgments.json.

## Differences that affected grading

- **B, K1 expectation 1 — missed:** “supported pinned invocation” does not supply the required local `pesde run blink -- ...` alias or an equivalent concrete locked invocation. The answer leaves `pesde exec` merely unverified instead of correcting the proposed compiler entry point.
- **B, B1 expectation 2 — unclear:** Phase errors and a fail-fast route are addressed, but load-error handling is absent. With a loaded collection supplied and no load fault reported, this omission is not a demonstrated material failure. The explicitly qualified partial-startup alternative was allowed.
- **B, V1 expectation 4 — unclear:** Throwing callbacks and independent cleanup protection are addressed, but producer-before-consumer order is unstated. The answer does not affirm a harmful order.

## Separate factual and prompt findings

**B/V1 contains an inaccurate or incomplete pinned-API explanation.** It says “step(0) is a scheduling operation.” The permitted exact-target reference says `step(0)` disconnects the package-global stepper. The recommendation against component-level use meets the action expectation; that does not erase the mechanism issue.

No clear prompt violations were found. **A/C1 has a recorded format ambiguity:** decorative Unicode emoji labels accompany a request for plain text. Because the response has no rich-text markup and the prompt does not prohibit emoji, this was not counted as a clear violation. A stricter prose-only interpretation is possible and is disclosed rather than silently deducted.

No extra credit was assigned for procedural labels, longer explanations, exact API details outside the rubric, or unrequested checks. The broad agreement includes bounded evidence collection, preservation of authorized scope, separate runtime evidence, and explicit lifecycle ownership.

## Evidence boundary

All scenario observations were supplied fixtures; no Studio, host, integration, resource, or other runtime checks were performed. The only additional reference read was:

`session-a/skills/roblox-resource-acquisition/children/roblox-vide-0-4-1/references/api-and-lifecycle.md`

That exact cited file was read solely to adjudicate B/V1's `step(0)` explanation. No skill directories, implementation discussion, or expected conclusions were inspected. Other API assertions were not independently source-audited. Mechanical validation confirmed the case/expectation counts and that every quoted answer excerpt is an exact substring.
