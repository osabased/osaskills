---
name: system-review
description: Review cross-part contracts and operational failure paths for changed behavior, an end-to-end failure, or a system assurance question.
---

# System Review

Determine whether a defined system achieves its required outcome across interactions. Start from the review question, not a system inventory. A defect requires a demonstrated failed contract or control and a material consequence; missing deciding evidence is a visibility gap.

## Scope and authority

If one component can answer the question without cross-part contracts or failure propagation, return `System Review Applicability: HANDOFF` with the reason and fitting owner. Local implementation, domain organization, resource qualification, and preferences remain with their owners. This skill diagnoses defined scenarios; `direction-selection` compares open consequential corrections.

Establish the exact changed behavior, observed failure, or assurance claim, and the smallest end-to-end boundary that can answer it. Expand when evidence reveals relevant dependencies, propagation paths, or authority. Preserve an explicitly requested broad/whole-system boundary and qualify conclusions rather than silently narrowing it.

Keep the outcome, scope, review stage, target identity, operating bar, normative authority, and decision-sensitive unknowns clear enough to evaluate the question. Target identity includes the material revision/version, configuration, environment, workload, and time window. Reuse applicable caller context and evidence; re-check it for freshness, conflicts, scope mismatch, or other deciding uncertainty.

Normative evidence defines required behavior; structural evidence shows what exists; behavioral evidence shows what happens; external authority establishes platform/dependency behavior. Conclusions cannot exceed their evidence's stage, target, or operating conditions.

## Contracts and scenarios

Trace interactions capable of affecting the outcome, including relevant components, tools, stores, dependencies, human steps, and trust boundaries. For each material boundary, understand the exchanged state/control, meaning and authoritative owner, success/failure semantics, side-effect/acknowledgement boundary, and observable result.

Compare semantics on both sides: identity, units, ordering, state ownership, compatibility, and other relevant guarantees. Pay particular attention to a committed side effect whose acknowledgement or record is missing.

Use the smallest scenario set covering every material contract and credible failure transition; equivalent contracts can share a scenario. Tie each to a requirement, boundary, or credible operating condition:

`setup → action/event → material intermediate states → observable expected outcome`

Include applicable normal flow, unauthorized/invalid input, dependency slowdown/partial failure, retry/duplication/reordering/concurrency, interruption/restart/recovery, deploy/rollback/migration/version skew, credible resource pressure, and operator detection/recovery. These are conditional failure families, not a mandatory test suite. For interruption/retry/recovery, identify the last committed effect and first unconfirmed state.

Compare expected outcomes with the safest applicable evidence through:

`trigger → required contract/control → actual transitions → propagation → consequence → detection/recovery`

Resolve inspectable unknowns before declaring gaps. Prefer behavioral execution when it can establish the property and structural inspection for structural requirements; keep active probes within authorization and acceptable blast radius. Use current primary documentation for version-sensitive external facts. A blocked or unavailable check remains explicit, not a pass.

When technology choice carries a scenario, assess workload fit, known weaknesses, current operational cost, and replaceability at the likely future correction point. A named pattern matters only when its problem is present.

Read [cross-agent-synthesis.md](references/cross-agent-synthesis.md) only when distinct independent perspectives could materially change a finding, causal attribution, disposition, or visibility gap; preserve their first passes. Otherwise synthesize directly.

## Findings and counterevidence

Retain a candidate only when the chain `trigger → failed contract/control → propagation → material consequence` is supported and survives its strongest plausible counterexplanation. Check relevant guards, caller obligations, upstream guarantees, recovery behavior, and scope assumptions. Counterevidence must apply to the failing scenario.

Group symptoms of one failed contract; keep independently material failed controls separate even when one trigger exposed them. Preferences, fashionable patterns, generic best practices, and unsupported future scale are not findings.

Give each demonstrated defect one supported disposition:

- **Correction:** the smallest coherent correction supported by evidence, preserving neighboring requirements and guarantees.
- **Diagnostic handoff:** the defect is known but its cause/correction is not; give the unresolved boundary, missing discriminating evidence, smallest safe check, and owner.
- **Direction handoff:** the defect and constraints are known but consequential corrections compete; give the decision boundary, hard constraints, evidence, and established options without ranking. Invoke `direction-selection` only when the surrounding task includes choosing the correction.

An uncertain correction or visibility gap does not erase a demonstrated defect. Record **Close when**: the exact scenario and positive observable evidence needed to establish correction on the current target.

## Re-review continuation

Preserve still-valid scope, contract maps, scenario/finding identifiers, authority, provenance, findings, and passing coverage. Revisit only material invalidated by changes to code, configuration, workload, assumptions, target, or evidence freshness. Rerun failed and previously passing scenarios affected by a correction. Retry blocked checks only when their prerequisites or evidence route change; carry unchanged blockers explicitly.

Keep an uncorrected demonstrated defect open. Close it only with fresh positive evidence satisfying its recorded closure condition. Invalidated evidence cannot support a fresh `PASS`.

## Verdict

A **visibility gap** is missing evidence that could change the verdict, a finding, its cause, or its correction. A **residual risk** is an evidence-backed exposure sufficiently understood and accepted at the current operating bar; it needs a reason for acceptance and an observable reopen condition. Unverified uncertainty is not an accepted risk.

Apply this precedence:

1. **`CHANGES REQUIRED`**: a demonstrated material defect remains, even with visibility gaps.
2. **`INSUFFICIENT EVIDENCE`**: no demonstrated defect requires changes, but a deciding gap prevents assessing the operating bar.
3. **`PASS WITH RISKS`**: no required correction or verdict-blocking gap remains, and at least one accepted residual risk is recorded.
4. **`PASS`**: applicable scenarios support the required outcome within the recorded stage/target, with no defect, verdict-blocking gap, or residual risk.

## Output

Lead with **verdict and scope**, then findings in descending consequence. Keep decisive evidence, consequence, supported disposition/next action, and **Close when** beside each finding. Include material gaps, accepted risks, and coverage limits; omit empty sections and process narration. A clean focused review may be a few lines.

Read [OUTCOMES.md](references/OUTCOMES.md) for agent/controller handoffs or user-requested full records.

**Complete when:** every material scenario has applicable evidence or an explicit blocked check, findings have supported dispositions and closure conditions, and the verdict follows from the recorded evidence and limits. A preferable alternative architecture is not a reason to keep reviewing. Return the diagnosis to the caller; review alone does not authorize implementation.
