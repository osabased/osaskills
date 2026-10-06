---
name: direction-selection
description: Choose or reassess consequential directions when alternatives compete, comparative support is weak, the framing or candidate space is unclear, or new evidence challenges the current choice. Skip routine implementation choices.
---

# Direction Selection

Choose the best-supported next commitment under the user's goal and constraints. Leave later choices open until they matter. A direction decision reports support; the caller retains execution authority.

Honor user mandates unless infeasible, unsafe, contradictory, or explicitly under review.

## Applicability router

Route before comparing:

- **exit:** a routine or cheaply reversible implementation detail needs no substantive comparison, an applicable convention settles it, or an applicable user mandate already settles it.
- **handoff:** only a fact, behavior, project-state check, or user-owned input needs resolution before comparison can own a decision. Return the fitting owner and next evidence route.
- **lightweight:** a meaningful bounded choice is live, with adequate framing, criteria, and candidate coverage. Follow the decision loop below.
- **full:** consequential or hard-to-reverse alternatives remain competitive; framing is ambiguous; a credible omitted direction or shared-premise problem exists; a consequential choice has weak comparative support; a best/ideal request lacks justified candidate coverage; or material evidence challenges the current direction. Read [FULL.md](references/FULL.md) and apply its extensions within the same loop.

Generic uncertainty does not require comparison. When one clear direction exists and only an inspectable fact remains, hand that check back to the caller rather than inventing alternatives. In standalone use, if evidence is needed to determine applicability, use a scoped [discovery probe](references/DISCOVERY.md), then route again. An inconclusive probe returns `handoff`, without a direction outcome or gate.

## Decision loop

### 1. Frame the commitment

Identify the outcome, commitment needed now, hard constraints, and ordered criteria. For any deciding criterion, distinguish a threshold from an objective to optimize, and strict priority from an allowed tradeoff. Preserve explicit priorities; use numerical weights, probabilities, or tradeoff rates only when supplied or supported.

Treat a suggested favorite as a candidate, not evidence. Ask a focused question when an unresolved user-owned preference could change the recommendation. Delegated authority permits choosing; it does not establish the user's risk tolerance or preferences.

### 2. Compare credible options

Compare serious candidates under the same criteria and evidence standard, at comparable depth. Use the current approach, doing less, or avoiding the decision when credible. There is no required candidate count.

Before rejecting a candidate on a remediable weakness, consider one realistic, bounded refinement when it could change the result. Give competitors the same opportunity, count the refinement's costs, and distinguish verified capability from a hypothetical fix. Stop refining when it cannot affect the choice.

Eliminate demonstrated constraint failures, then compare survivors under the ordered objectives and tradeoffs. Count future integration, maintenance, migration, compatibility, and operating costs; exclude sunk effort as a reason to retain an incumbent. Assess reversal at the likely correction point, after probable dependent work has accumulated.

For close comparisons, distinguish a supported advantage, supported practical equivalence, and an unresolved difference. Use applicable tolerances or evidence-backed ranges; an uncertain difference is not automatically a tie. Move to the next ordered criterion when equivalence is supported. When an assumption could switch the result, identify the switch point and investigate it only when plausible and worthwhile. For supported ties, consider validation effort, reversal, exit, or extension where consistent with the user's priorities; otherwise report equivalence without inventing a superior option.

### 3. Check deciding evidence

Link each deciding claim to its underlying source or observation. Confirm reliability and applicability to the relevant version, environment, workload, required outcome, and material integration or recovery conditions. Separate what the evidence establishes from inference. Missing evidence leaves a requirement unverified; it establishes neither compliance nor failure.

Reuse applicable caller evidence with its provenance. A confident summary or agreement among agents is not verification. Repeated reports of one result remain one evidence basis. Resolve material conflicts by examining methods and scope, not counting sources.

For consequential or hard-to-reverse recommendations, examine evidence that could overturn the deciding claims, even when confidence is high. Existing reliable evidence may suffice; an imagined objection alone does not complete this check.

When evidence or domain understanding could affect framing, candidates, ranking, or support, use [DISCOVERY.md](references/DISCOVERY.md). For source research, read [RESEARCH.md](references/RESEARCH.md). Continue justified investigations while material gaps or credible leads remain; their number or cost cannot convert missing deciding evidence into support.

If findings activate a full-mode trigger, apply its extensions at the affected step while preserving valid work.

### 4. Decide and stop

Set `Direction Gate: PASS` only when the proposed commitment:

- satisfies every known hard constraint with applicable evidence;
- rests on reliable deciding claims and adequate candidate coverage, including any required full-mode work;
- has no credible alternative with a better-supported case under the ordered criteria;
- resolves any material tie through an applicable selection rule; and
- remains justified under material uncertainty and the established acceptable downside until safe correction.

A choice need not win in every plausible future. Accept uncertainty consistent with the objective and downside the user has established; retain the conditions that would change the recommendation. Stronger or harder-to-reverse commitments need stronger support.

If support is missing, pursue the next worthwhile evidence step or focused preference question. When further justified work cannot resolve it, return a `Direction Blocker` with the exact gap, owner, next step, and resume condition, including when no justified next step remains. Unavailable research does not justify changing the objective or claiming compliance.

When uncertainty is structurally unstable after worthwhile investigation, a useful bounded commitment may still be supported. Read the adaptive conditions in [OUTPUTS.md](references/OUTPUTS.md) before returning an `Adaptive Direction`; difficulty or missing evidence alone does not qualify.

Stop when support is sufficient and further investigation has no justified decision value, or return the explicit unresolved outcome. Avoid extra candidates, searches, or review rounds once they cannot change the decision.

## Return the outcome

### User-facing presentation

Lead with the recommendation and supported scope, then the deciding evidence, strongest alternative's relevant tradeoff, material caveat, and condition that would change the choice. End with the next authorized action or exact missing input. Omit empty sections and process narration; a normal decision should usually fit in 100–200 words.

For blockers, lead with what is needed and what cannot yet proceed. For adaptive outcomes, lead with the bounded next step and retain its exposure limit and adaptation trigger. An exit or handoff usually needs only one or two sentences.

For an agent/controller handoff or a requested full record, read [OUTPUTS.md](references/OUTPUTS.md) and return the matching contract with gate status. Keep records local unless the caller requires persistence. Continue only into work already authorized by the user.

### Commitment and continuity

A gate covers only the stated direction-dependent commitment. Authorized inspection, evidence gathering, unrelated supported work, and safely reversible increments may proceed while it is unresolved. Exploratory work must remain within its limits and avoid de facto lock-in; it cannot silently become the unsupported production commitment.

When new evidence invalidates a deciding premise, mark that direction reopened. Preserve valid constraints, authority, evidence, assumptions, candidate coverage, and completed work; repeat only affected comparison. Return the invalidated premise, triggering evidence, and already-known affected downstream commitments to the caller. The caller owns broader impact discovery and correction; leave independent decisions intact.

When changing this skill or a protocol that invokes it, read [SELF-APPLICATION.md](references/SELF-APPLICATION.md).
