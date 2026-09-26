---
name: system-review
description: Review a defined system when changed cross-part behavior, an observed end-to-end failure, or a material assurance question depends on interactions between parts or operational failure paths.
---

# System Review

Determine whether a defined system achieves its required outcome across interactions. This skill defines the standard a valid review must satisfy, not a fixed investigation procedure. Use the smallest evidence path that answers the review question.

## Route and frame

Use system review when the answer depends on cross-part contracts, state propagation, or operational failure paths. If one component can answer the question without cross-part reasoning, return `System Review Applicability: HANDOFF` with the reason and fitting owner, then stop.

Comparison among consequential alternatives belongs to `direction-selection`; local implementation, domain qualification, and preference work remain with their fitting owners. System review may establish defects and correction constraints, but it does not rank alternatives.

State the **review question** and select the smallest sufficient end-to-end boundary. Expand it only when evidence reveals a relevant dependency, propagation path, or authority outside it. Preserve broader scope when the user explicitly requests it.

Keep only context that can change a conclusion: required outcome; applicable stage/target/configuration/environment/workload/time window; operating bar; normative requirements or invariants; and decision-sensitive unknowns.

Evidence has bounded reach:

- **Normative:** what must happen.
- **Structural:** what exists.
- **Behavioral:** what happens.
- **External authority:** relevant platform or dependency behavior.

Do not claim beyond the stage, target, conditions, or authority represented by the evidence.

## Establish material contracts and scenarios

Map only interactions capable of affecting the review question:

`source → target | state/control | authoritative owner and meaning | success/failure semantics | committed vs acknowledged effect | observable result`

Check both sides of a material boundary when semantics could diverge, especially identity, units, ordering, state ownership, compatibility, acknowledgement, and retry behavior. Identify intermediate states where one side committed an effect that another side has not acknowledged, recorded, or incorporated.

Use the **smallest discriminating scenario set** needed to answer the question. Add failure transitions only when credible and material; do not build an exhaustive checklist merely because failure modes exist.

A scenario is:

`setup → action/event → material intermediate state(s) → observable expected outcome`

For interruption, retry, or recovery, identify the last committed effect and first unconfirmed or unrecorded state when that distinction matters.

Trace enough evidence to establish:

`trigger/condition → required contract/control → actual state transition → propagation → consequence → detection/recovery`

Prefer behavioral evidence when it directly establishes the property and structural evidence for inherently structural requirements. Resolve directly inspectable unknowns before reporting gaps. Use current primary documentation for version-sensitive external facts. Keep active probes within authorization and acceptable blast radius; otherwise mark the check blocked or unverified.

## Retain only defensible findings

A **defect** requires applicable evidence, a violated contract or failed control, and a material consequence.

Before retaining a finding, test the strongest plausible applicable counterevidence: guards, caller obligations, upstream guarantees, recovery behavior, scope assumptions, or other evidence that could show it is false or inapplicable. Agreement, intuition, a named pattern, or generic best practice is not evidence.

Group symptoms explained by the same failed contract/control. Keep independently material failed controls separate.

Each finding gets one supported disposition:

- **Correction:** the smallest coherent correction is established and preserves neighboring requirements.
- **Diagnostic handoff:** the defect is established but its causal boundary or correction is not. Give the unresolved boundary, missing discriminating evidence, smallest safe next check, and owner.
- **Direction handoff:** the defect and correction constraints are established but materially different consequential corrections remain credible. Give the decision boundary, hard constraints, established options, and evidence without ranking.

An uncertain correction does not weaken an established defect. Do not invent one to complete the format.

Every finding records **Close when**: the exact scenario and observable positive evidence required for closure. A plausible code change, failure that no longer reproduces, or inspection alone does not close the finding unless it satisfies that condition.

Preferences, generic best practices, absent fashionable patterns, and unsupported future scale are non-findings.

A **visibility gap** is missing evidence whose plausible answers could change the verdict, a finding, its cause, or its correction. It may qualify a conclusion but cannot erase an established defect.

A **residual risk** is a sufficiently understood, evidence-backed exposure accepted at the current operating bar. Unverified uncertainty is not a residual risk.

## Re-review

Reuse still-applicable scope, authority, contract/scenario identifiers, evidence, findings, and passing coverage. Invalidate only material affected by changed code, configuration, dependency behavior, workload, assumptions, target identity, or evidence freshness.

- Rerun a failed scenario when a correction or changed premise could alter it.
- Rerun a passing scenario only when its contract, dependency, assumptions, or evidence were affected.
- Retry a blocked check when its prerequisite, authorization, environment, or evidence route changes; otherwise carry the blocker forward.
- Keep an established defect open until fresh positive evidence satisfies its `Close when`.

Invalidated evidence cannot support a fresh `PASS`.

## Independent perspectives

Use independent agents/perspectives only when genuinely different expertise or evidence could materially change a finding, causal attribution, disposition, or visibility gap. Do not add review passes merely to satisfy this skill.

If independent first passes already exist and cross-signals could change their conclusions, use [references/cross-agent-synthesis.md](references/cross-agent-synthesis.md) and preserve those first passes before sharing signals.

## Return the review

Verdict precedence:

1. `CHANGES REQUIRED` — at least one demonstrated material defect remains.
2. `INSUFFICIENT EVIDENCE` — no defect requires changes, but a decision-sensitive gap prevents deciding whether the operating bar is met.
3. `PASS WITH RISKS` — no correction or verdict-blocking gap remains, but an evidence-backed residual risk is accepted.
4. `PASS` — applicable evidence supports the required outcome for the recorded stage and target with no open defect, blocking gap, or residual risk.

Lead with verdict and reviewed scope. For another agent/controller, preserve only the non-empty parts of this record:

- **Scope / stage / target / operating bar**
- **Findings:** ID/title, decisive evidence and reach, exposing scenario, violated contract/control, material consequence, disposition, `Close when`
- **Visibility gaps:** missing evidence, decision effect, smallest safe next check/owner
- **Residual risks:** evidence, exposure, why accepted, reopen condition
- **Validated areas:** material contracts/scenarios supported and evidence reach
- **Verification:** tests, inspections, observations, authorities, blocked checks, and rerun coverage actually used

For user-facing output, present the result once rather than narrating the procedure. Keep decisive evidence, consequence, next action/disposition, and closure condition together; omit empty sections and repetition.

Stop when the evidence answers the review question at the requested scope and supports the stage-scoped verdict. A preferable alternative architecture or implementation is not by itself a reason to continue.
