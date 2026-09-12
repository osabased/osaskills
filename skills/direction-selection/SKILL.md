---
name: direction-selection
description: Choose or reassess consequential directions when the choice, framing, candidate space, or supporting evidence is unresolved.
---

# Direction Selection

Choose the direction best supported for the current goal and commitment. This skill owns comparison, not general research, project planning, implementation, persistence, or correction propagation. Claim only the degree of optimality the evidence supports.

## Applicability router

Resolve whether a live direction problem exists before comparing:

- **`exit`**: no meaningful direction choice remains. Routine naming, established placement conventions, and cheaply reversible details normally belong to the current task.
- **`handoff`**: a directly routable fact, behavior, project-state unknown, constraint, or user preference needs its fitting owner first. Give the reason and next route; consequential uncertainty alone does not justify comparison.
- **`full`**: an [authoritative full-mode trigger](#authoritative-full-mode-triggers) applies. Read [FULL.md](references/FULL.md).
- **`lightweight`**: a meaningful bounded choice remains, its framing, criteria, and candidate space are adequate, and no full-mode trigger applies. Read [LIGHTWEIGHT.md](references/LIGHTWEIGHT.md).

With a caller/controller, hand non-directional unknowns back rather than starting a research loop. In standalone use, if applicability depends on one resolvable fact, use the bounded applicability probe in [DISCOVERY.md](references/DISCOVERY.md), then return here. An unresolved probe returns `handoff`, not a comparison result.

### Authority and preference semantics

An explicit mandate is a hard boundary unless impossible, unsafe, contradictory, or explicitly under evaluation. A suggested favorite is a candidate, not evidence. Ask for a consequential user-owned preference when it is cheaply resolvable; delegated choice authority is not evidence of that preference.

## Continuation invariant

Reuse applicable boundaries, authorities, constraints, evidence and provenance, assumptions, candidates, and completed results across calls, escalation, handoffs, and reopening. Revisit only work invalidated by new evidence, conflict, freshness, or scope mismatch. An inherited diagnosis can be established input without making an inherited ranking authoritative.

## Support threshold

A direction is sufficiently supported for the **governed commitment** when it:

- satisfies every known hard constraint and invariant;
- has applicable, proportionate evidence for its decisive comparative claims;
- has no unresolved material assumption whose plausible outcomes could overturn it at this commitment level;
- has no credible surviving alternative with a better-supported case under the ordered criteria; and
- resolves any material tie through applicable ordered tie-breakers, rather than claiming a nominal winner.

Scale evidence to impact and reversibility. Seek enough support to decide, not certainty; neither extra candidates nor extra investigation are quotas.

### Close comparisons

Distinguish a supported advantage, supported practical equivalence, and an unresolved difference. Use requirement-backed tolerances or evidence-backed ranges; retain explicit optimization priorities. Practical equivalence permits moving to the next criterion. A potentially decisive unresolved difference remains uncertainty. For supported ties, use ease of validation, reversal, exit, or extension as applicable. Investigate a choice's switch point only when the smallest credible change could matter and resolving it is worthwhile.

## Deciding-evidence applicability

Decisive evidence must represent the property at risk and its relevant version/interface, environment, workload or population, operating conditions, and integration effects. Identify the source and separate observation from inference. Repeated reports of one result remain one evidentiary basis. Distinguish demonstrated constraint failure, unverified satisfaction, and inapplicable evidence; informative but mismatched evidence cannot decide the comparison.

## Authoritative full-mode triggers

1. Materially different directions remain genuinely competitive for a consequential or hard-to-reverse commitment.
2. Framing ambiguity can materially change the solution space.
3. A credible omitted-direction or shared-premise signal exists.
4. A consequential direction has weak comparative justification.
5. The user requests the best or ideal direction and the inherited candidate space is inadequately justified.
6. Material new evidence challenges the current direction.

Record the active triggers. Triggers 3–5 require one bounded candidate-space examination before `PASS`. Trigger 6 requires distinguishing a ranking change from a framing or candidate-space change. Known competition alone does not require searching for another class.

## Direction Gate scope

`Direction Gate: PASS` means the Support threshold holds for the recorded commitment, not that the whole project is authorized. Production commitment materially dependent on the unresolved direction waits for that support.

Otherwise-authorized unrelated work, already-supported increments, inspection, evidence tests, prototypes, and safely reversible work may continue when they do not prejudice the choice. Pre-gate work must remain outside the governed consequential commitment and avoid de facto lock-in.

Assess **future-horizon reversibility** at the likely correction point after dependent work accumulates, including material migration, compatibility, external commitments, and ecosystem lock-in. Use that horizon for evidence work, mode choice, tie-breakers, and adaptive commitments.

## Conditional references

- A specific unknown blocks comparison and no direction meets the Support threshold: read [DISCOVERY.md](references/DISCOVERY.md). Apply its entry test and return to the interrupted owner, not the start of the protocol.
- Important uncertainty is structurally unstable after worthwhile investigation, so an overall winner would be false certainty: read the [Adaptive Direction contract](references/OUTCOMES.md#adaptive-direction) before considering a bounded commitment.
- Another agent/controller needs a structured record, or the user requests it: read [OUTCOMES.md](references/OUTCOMES.md).
- This skill is being applied to itself or another decision protocol: read [SELF-APPLICATION.md](references/SELF-APPLICATION.md) before applying full comparison.

## Output contracts

Return an `Applicability Result` for `exit`/`handoff`; after comparison, return a supported `Direction Decision`, an exact `Direction Blocker`, or a justified `Adaptive Direction`. The complete schemas live in [OUTCOMES.md](references/OUTCOMES.md), not in every user response.

Return the local result and commitment-scoped gate status to any caller/controller, which retains execution and persistence ownership. In standalone use, continue through work already authorized by the request; deciding alone grants no additional scope.

### User-facing presentation

Present the result once, normally in 100–200 words: **recommendation and scope**, deciding evidence, the strongest alternative's material tradeoff when useful, uncertainty and a concrete reopen condition, then the authorized next action or completed result. Use a small table only when it clarifies real tradeoffs. Omit empty sections and process narration.

For a blocker, state what cannot proceed, the missing evidence/preference/constraint, its decision effect, owner, next action, and resume condition; say when no justified next action remains. For `exit`/`handoff`, the result, reason, and next route usually need only one or two sentences. Adaptive outcomes retain the bounded commitment, rationale, exposure limit, preserved options, and adaptation trigger from their contract.

## Reopening a direction

Reopen when verified facts, tests, changed requirements, or a recorded reopen condition materially invalidate a load-bearing premise. Mark the direction reopened and identify the premise and triggering evidence. Apply the Continuation invariant.

Give the caller/controller the known affected downstream commitments or artifacts already in context; broader impact discovery remains its responsibility. In standalone use, identify known commitments needing reconsideration. Keep unaffected branches intact.

**Complete when:** the local outcome, governed scope, applicable evidence, material caveats, gate status, and next action or its absence are clear. Continue authorized work without inserting an extra review stop.
