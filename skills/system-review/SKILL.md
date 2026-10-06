---
name: system-review
description: Review a defined system when changed cross-part behavior, an end-to-end failure, or an assurance question depends on interactions or operational failure paths.
---

# System Review

Determine whether a system achieves its required outcome across interactions. Follow the smallest evidence path that answers the review question.

## Frame the review

State the required outcome, review question, and smallest sufficient end-to-end boundary. Retain the stage, target, configuration, workload, and requirements that could change the conclusion. Expand scope only for a relevant dependency or the user's request.

If one component can answer the question without cross-part reasoning, return `System Review Applicability: HANDOFF` with the reason and fitting owner. Review establishes defects and correction constraints; keep broader design choices with the caller unless the user requested that comparison.

## Trace the behavior

Inspect both sides of the material interactions: who owns state or control, what each side promises, and what the caller can observe. Follow identity, units, ordering, acknowledgements, and recovery where they affect the outcome.

Choose discriminating scenarios: **setup → event → intermediate state → expected observable result**. For interruption or retry, distinguish the last committed effect from the first unconfirmed or unrecorded state. Trace the consequence through the boundary rather than inferring it from one component.

Resolve directly inspectable unknowns. Use behavioral evidence for runtime claims, structural evidence for structural requirements, and current primary documentation for version-sensitive external facts. Scope every claim to the target and conditions its evidence covers. Run probes within authorization; identify unavailable or blocked checks precisely.

## Challenge and retain findings

A defect needs **applicable evidence, a violated requirement or failed control, and a material consequence**. Test the strongest applicable counterevidence before retaining it: upstream guarantees, caller obligations, guards, recovery, or a mistaken scope assumption. Preferences and generic best practices alone are not defects.

Group symptoms of the same failed control; preserve independently material failures. For each finding, keep the evidence, exposing scenario, failed contract, consequence, and one supported next step together:

- **Correction:** recommend the smallest coherent correction when its cause and effect are established and neighboring requirements are preserved.
- **Diagnostic handoff:** when the causal boundary or correction is unresolved, name the missing discriminating evidence, next safe check, and owner.
- **Design choice:** when consequential corrections compete, return the constraints, established options, evidence, and deciding tradeoff to the caller. Compare them when the user's request includes choosing a correction.

An unresolved correction leaves an established defect open. Record **Close when**: the exact scenario and positive observable evidence needed for closure. A plausible patch or a failure that disappears does not suffice unless it meets that condition.

Distinguish a **visibility gap**, missing evidence that could change a conclusion, from a **residual risk**, an understood, evidence-backed exposure accepted at the operating bar. Neither erases a demonstrated defect.

Use independent perspectives only when different expertise or evidence could change a conclusion. If independent passes already exist and sharing evidence could matter, read [cross-agent synthesis](references/cross-agent-synthesis.md).

## Return and close

Use the first applicable verdict:

| Verdict | Condition |
|---|---|
| `CHANGES REQUIRED` | A demonstrated material defect remains. |
| `INSUFFICIENT EVIDENCE` | No defect requires changes, but a deciding evidence gap remains. |
| `PASS WITH RISKS` | No defect or blocking gap remains; an understood residual risk is accepted. |
| `PASS` | Evidence supports the required outcome at the recorded stage and target, with no open defect, blocking gap, or residual risk. |

Lead with verdict and scope. Include only material findings, gaps, accepted risks, validated areas, and checks actually performed. Preserve finding identifiers and closure conditions for handoffs; keep each conclusion beside its evidence, limits, and next action. Present the result once.

On re-review, reuse unaffected evidence and passing coverage. Rerun failed or passing scenarios only when a correction or changed input could alter their result; retry blocked checks when their prerequisites change. Keep defects open until fresh evidence satisfies `Close when`. Invalidated evidence cannot support a fresh pass.

**Complete when:** the evidence answers the review question or identifies its precise blocker, and supports the verdict at the requested scope. Alternative designs alone do not extend the review.
