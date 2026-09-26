---
name: system-review
description: Review a defined system when changed cross-part behavior, an observed end-to-end failure, or a material assurance question depends on interactions between parts or operational failure paths.
---

# System Review

Determine whether a defined system achieves its required outcome across interactions. This skill defines the standard a review must satisfy, not a fixed investigation procedure. Use the smallest evidence path that can answer the review question.

## Applicability and boundary

Use system review when the answer depends on cross-part contracts, state propagation, or operational failure paths. If the question can be answered inside one component, return `System Review Applicability: HANDOFF` with the reason and fitting owner, then stop.

Keep neighboring concerns with their fitting owners:

- comparison among materially different directions → `direction-selection`;
- local implementation or domain-specific qualification → the relevant implementation/domain owner;
- preference discovery → the relevant preference owner.

System review may establish defects and correction constraints, but it does not rank alternative solutions.

Start with the **review question**: the exact changed behavior, observed failure, or assurance claim to resolve. Select the smallest sufficient end-to-end boundary and expand it only when evidence reveals a relevant dependency, propagation path, or authority outside it. If the user explicitly requests broad coverage, preserve that boundary.

Record only context that can change the conclusion:

- **Outcome:** required user or operator result.
- **Stage and target:** applicable design/implementation/operation stage plus revision, configuration, environment, workload, and time window when relevant.
- **Operating bar:** prototype, internal, production, regulated/high-risk, or another materially different bar.
- **Normative authority:** requirements, invariants, accepted constraints, or external authority defining expected behavior.
- **Decision-sensitive unknowns:** missing facts whose plausible answers could change the verdict, a finding, its cause, or its correction.

Classify evidence by reach:

- **Normative:** what must happen.
- **Structural:** what exists.
- **Behavioral:** what happens.
- **External authority:** relevant platform or dependency behavior.

A conclusion must not reach beyond the stage, target, conditions, or authority represented by its evidence.

## Material contracts and scenarios

Establish only the cross-part contracts capable of affecting the review question. For each material interaction, determine:

`source → target | state/control exchanged | authoritative owner and meaning | success/failure semantics | committed vs acknowledged effect | observable result`

Compare both sides of a boundary where meaning may diverge: identity, units, ordering, state ownership, compatibility, acknowledgement, retry semantics, or other relevant guarantees. Pay particular attention to intermediate states where one side has committed an effect that another side has not acknowledged, recorded, or incorporated.

Use the **smallest discriminating scenario set** needed to answer the review question. Do not create exhaustive failure-mode checklists when fewer scenarios establish the result. Add timeout, retry, duplication, reordering, concurrency, restart, deploy, rollback, migration, load, resource exhaustion, operator recovery, or trust-boundary scenarios only when they are credible and material to the reviewed outcome.

Write a scenario as:

`setup → action/event → material intermediate state(s) → observable expected outcome`

For interruption, retry, or recovery scenarios, identify the last committed effect and the first unconfirmed or unrecorded state when that distinction is material.

## Evidence and findings

For each scenario, trace enough of the system to establish:

`trigger/condition → required contract/control → actual state transition → propagation → consequence → detection/recovery`

Prefer behavioral evidence when it directly establishes the property and structural evidence when the requirement is inherently structural. Resolve directly inspectable unknowns before reporting gaps. Use current primary documentation for version-sensitive external facts. Keep active probes within authorization and an acceptable blast radius; otherwise mark the check blocked or unverified.

A **defect** requires all of the following:

1. applicable evidence;
2. a violated contract or failed control;
3. a material consequence.

Before retaining a finding, test the strongest plausible applicable counterevidence: guards, caller obligations, upstream guarantees, recovery behavior, scope assumptions, or other evidence that could show the candidate is false or inapplicable. Agreement, intuition, a named pattern, or a generic best practice is not evidence.

Group downstream symptoms when one violated contract or failed control explains them. Keep independently material failed controls separate.

Each surviving finding gets exactly one supported disposition:

- **Correction:** the smallest coherent correction is established by the evidence and preserves neighboring requirements.
- **Diagnostic handoff:** the defect is established, but its causal boundary or correction is not. State the unresolved boundary, missing discriminating evidence, smallest safe next check, and fitting owner.
- **Direction handoff:** the defect and correction constraints are established, but materially different consequential corrections remain credible. State the decision boundary, hard constraints, established options, and evidence without ranking them.

An uncertain correction does not weaken an established defect. Do not invent a correction to complete the format.

For every finding record **Close when**: the exact scenario and observable positive evidence required to establish correction. A plausible code change, absence of a reproduced failure, or inspection alone does not close a defect unless it satisfies that condition.

Treat preferences, generic best practices, absent fashionable patterns, and unsupported future scale as non-findings.

A **visibility gap** is missing decision-sensitive evidence. It may qualify the verdict, cause, or correction, but it does not erase an established defect.

A **residual risk** is a sufficiently understood, evidence-backed exposure accepted at the current operating bar. Unverified uncertainty is not a residual risk.

## Re-review

Reuse still-applicable boundaries, authorities, contract/scenario identifiers, evidence, findings, and passing coverage. Invalidate only material affected by changed code, configuration, dependency behavior, workload, assumptions, target identity, or evidence freshness.

- Rerun a failed scenario when a correction or changed premise could alter it.
- Rerun a previously passing scenario only when its contract, dependency, assumptions, or evidence were affected.
- Retry a blocked check when its prerequisite, authorization, environment, or evidence route changes; otherwise carry the blocker forward.
- Keep an established defect open until fresh positive evidence satisfies its recorded `Close when` condition.

Evidence invalidated for the current target cannot support a fresh `PASS`.

## Independent perspectives

Use independent agents or perspectives only when genuinely different expertise or evidence could materially change a finding, causal attribution, disposition, or visibility gap. Do not create extra review passes merely to satisfy this skill.

When independent first passes already exist and cross-signals could change their conclusions, use [references/cross-agent-synthesis.md](references/cross-agent-synthesis.md). Preserve the independent first passes before sharing signals.

## Return the review

Lead with the verdict and reviewed scope. Use:

- `CHANGES REQUIRED` — at least one demonstrated material defect remains.
- `INSUFFICIENT EVIDENCE` — no demonstrated defect requires changes, but a decision-sensitive gap prevents deciding whether the operating bar is met.
- `PASS WITH RISKS` — no correction is required and no verdict-blocking gap remains, but at least one evidence-backed residual risk is accepted.
- `PASS` — applicable evidence supports the required outcome for the recorded stage and target, with no open defect, verdict-blocking gap, or residual risk.

When another agent/controller must continue the work, preserve this record:

### System Review

- **Scope:** review question and reviewed boundary
- **Stage and target:** applicable identity and conditions
- **Operating bar:** applicable bar
- **Verdict:** one of the four verdicts

### Findings

For each demonstrated defect:

**[S-NN] Title**
- **Evidence:** decisive evidence and its reach
- **Scenario:** exposing behavior or failure path
- **Failure:** violated contract or failed control
- **Consequence:** material effect
- **Disposition:** correction, diagnostic handoff, or direction handoff with the information required above
- **Close when:** scenario and positive evidence required for closure

### Visibility Gaps

Only gaps capable of changing a conclusion:

**[V-NN] Gap**
- **Missing evidence:** what cannot be established
- **Decision effect:** what it could change
- **Next check / owner:** smallest safe evidence route and fitting owner

### Residual Risks

Only accepted, evidence-backed exposures:

**[R-NN] Risk**
- **Evidence:** what establishes the exposure
- **Exposure:** what may happen and under what conditions
- **Why accepted:** why no correction is required at the current bar
- **Reopen if:** observable condition that invalidates the acceptance

### Validated Areas

Material contracts and scenarios supported without a demonstrated defect. State the evidence type and reach; do not imply broader correctness.

### Verification

Tests, inspections, observations, authorities, blocked checks, and re-review coverage actually used.

For user-facing output, present the result once rather than narrating the procedure. Keep decisive evidence, consequence, disposition/next action, and `Close when` together. Omit empty sections and repeated information.

Stop when the applicable evidence answers the review question at the requested scope and supports the stage-scoped verdict. A preferable alternative architecture or implementation is not by itself a reason to continue.
