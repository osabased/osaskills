# System Review Outcomes

Use for agent/controller continuation or a user-requested full record. The parent's [Verdict](../SKILL.md#verdict) rules determine the result; its [Output](../SKILL.md#output) section governs ordinary user answers.

## System Review

- **Scope:** system boundary and review question
- **Stage and target:** applicable stage, revision, configuration, environment, workload, and time window
- **Operating bar:** applicable bar
- **Verdict:** `PASS` | `PASS WITH RISKS` | `CHANGES REQUIRED` | `INSUFFICIENT EVIDENCE`

## Findings

For each demonstrated defect, retain its stable **[S-NN] Title** and:

- **Evidence:** decisive normative, structural, behavioral, or external evidence
- **Scenario:** exposing behavior or failure path
- **Failure:** violated contract or failed control
- **Consequence:** material effect
- **Correction:** smallest coherent supported correction
- **Close when:** scenario and positive observable evidence required for closure

Replace `Correction` when needed:

- **Diagnostic handoff:** unresolved causal/correction boundary, missing discriminating evidence, smallest safe next check, and owner
- **Direction handoff:** decision boundary, hard constraints/invariants, established evidence, and options without ranking

## Visibility Gaps

Only gaps capable of changing a conclusion. For each **[V-NN] Gap**, record:

- **Missing evidence:** what cannot be established
- **Decision effect:** verdict, finding, cause, or correction it could change
- **Next check / owner:** smallest safe evidence route and fitting owner

## Residual Risks

Only understood, evidence-backed exposures accepted at the current operating bar. For each **[R-NN] Risk**, record:

- **Evidence:** what establishes the exposure
- **Exposure:** what may happen and under which conditions
- **Why accepted:** why correction is not required at this bar
- **Reopen if:** observable condition invalidating acceptance

## Validated Areas

Material contracts and scenarios supported without a demonstrated defect. State evidence type and reach without implying broader correctness.

## Verification

Scenarios, tests, inspections, observations, and authorities actually used. Include blocked checks and invalidated re-review coverage that was rerun. Preserve identifiers and still-valid evidence for continuation; missing or invalidated proof cannot silently become a pass.
