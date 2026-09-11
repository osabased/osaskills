---
name: system-review
description: Review a defined system when changed cross-part behavior, an observed end-to-end failure, or a material assurance question depends on interactions between parts or operational failure paths.
---

# System Review

Determine whether a defined system achieves its required outcome across interactions. Start from the review question, not an inventory of the system. A defect needs a demonstrated failed contract or control and a material consequence. Missing decision-sensitive evidence is a visibility gap.

## 1. Route and frame the review

System review owns defined cross-part behavior and operational failure paths. If the question can be answered within one component without reasoning about cross-part contracts or failure propagation, return `System Review Applicability: HANDOFF` with the reason and fitting owner, then stop. Local implementation, domain-specific organization or qualification, and preference work remain with their fitting owners unless needed as evidence for the system diagnosis. Comparison among open directions remains with `direction-selection`; system review evaluates choices only as they carry defined scenarios, diagnoses failures, and constrains corrections.

State the **review question**: the exact changed behavior, observed failure, or assurance claim the review must resolve. Select the smallest sufficient end-to-end boundary that can answer it. Expand that boundary only when evidence reveals a relevant dependency, propagation path, or authority outside it. When the user explicitly requests a broad or whole-system review, preserve that requested boundary and qualify conclusions to the evidence available rather than silently shrinking the review.

Reuse applicable caller-provided scope, diagnosis, authority, scenarios, findings, and evidence. Re-check inherited material only when freshness, conflict, scope mismatch, or another decision-sensitive uncertainty makes that necessary.

Capture:

- **Outcome:** the state the system must produce for users or operators.
- **Scope:** the selected boundary, including participating components, modules, agents, tools, stores, dependencies, human steps, trust boundaries, and environments.
- **Review stage:** proposed design, implementation, operation, or a stated combination.
- **Target identity:** applicable revision or version, configuration, environment, workload, and operational time window.
- **Operating bar:** prototype, internal, production, regulated/high-risk, or another constraint that changes what matters.
- **Normative authority:** requirements, invariants, and accepted constraints defining expected behavior.
- **Unknowns:** missing facts whose plausible answers could change a conclusion.

Classify evidence by reach: normative evidence defines what must happen; structural evidence shows what exists; behavioral evidence shows what happens; external authority establishes relevant platform or dependency behavior. A conclusion cannot reach beyond the stage, target, or operating conditions represented by its evidence.

**Complete when:** the task is handed off, or the review question, outcome, boundary, stage, target, operating bar, authority, and decision-sensitive unknowns are explicit enough to map the interactions that can affect the answer.

## 2. Map contracts and derive discriminating scenarios

Build a compact working map for every interaction capable of affecting the outcome:

`source → target | state or control exchanged | meaning and authoritative owner | success and failure semantics | side effect / acknowledgement boundary | observable result`

Compare the meaning of shared data and guarantees on both sides of each material boundary. Check identity, units, ordering, state ownership, compatibility, and other semantics that could differ across the boundary. Identify intermediate states where one side has committed a side effect but another side has not acknowledged, recorded, or incorporated it.

Derive the smallest scenario set that covers every material contract and credible failure transition. One scenario may cover several related contracts; equivalent contracts may share a scenario. Tie each scenario to the contract map, a requirement, a trust boundary, or a credible operating condition.

Consider when applicable:

- normal end-to-end flow;
- invalid or unauthorized input;
- dependency slowdown, partial failure, timeout, and recovery;
- retry, duplication, reordering, interruption, and concurrency;
- restart, deploy, rollback, migration, or version skew;
- credible load growth, resource exhaustion, or backpressure;
- operator detection, diagnosis, and recovery.

Write each scenario as:

`setup → action or event → material intermediate state(s) → observable expected outcome`

For interruption, retry, or recovery scenarios, name the last committed effect and the first unconfirmed or unrecorded state. Connect the expected outcome to the evidence route capable of establishing it at the current review stage.

**Complete when:** every material contract is covered by at least one scenario, every relevant failure transition includes the intermediate state that makes it discriminating, and every scenario has an observable expected outcome with an applicable evidence route.

## 3. Trace scenarios against applicable evidence

For each scenario, trace:

`trigger or condition → required contract or control → actual state transitions → propagation → consequence → detection and recovery`

Inspect only the safest available evidence needed to compare actual behavior with the expected outcome. Resolve directly inspectable unknowns before reporting gaps, and use current primary documentation for version-sensitive external facts. Prefer behavioral execution when it can establish the property and structural inspection when the requirement is inherently structural. Keep active probes within authorization and an acceptable blast radius; otherwise record the check as blocked or unverified.

When a technology choice carries a scenario, judge it by workload fit, mismatch with known weaknesses, operational cost at the current team and scale, and future-horizon replaceability. Named patterns are evidence only when their problem is present.

When genuinely distinct independent perspectives could materially change a finding, causal attribution, disposition, or visibility gap, preserve their first passes and read [references/cross-agent-synthesis.md](references/cross-agent-synthesis.md). Otherwise synthesize directly.

### Re-review continuation

Preserve still-applicable boundaries, contract maps, scenario and finding identifiers, authorities, findings, evidence provenance, and passing coverage. Invalidate only material affected by changed code, configuration, workload, assumptions, target identity, or evidence freshness.

- Rerun a failed scenario when a correction or changed premise could alter its result.
- Rerun previously passing scenarios whose contracts, dependencies, or assumptions are affected by that change.
- Retry a blocked check when its prerequisite, authorization, environment, or available evidence route changes. Carry an unchanged blocker forward explicitly.
- Keep an uncorrected demonstrated defect open. Close it only with fresh positive evidence that satisfies its recorded closure condition.

Evidence invalidated for the current target cannot support a fresh `PASS`.

**Complete when:** every material scenario has applicable evidence or an explicit blocked check, every conclusion is bounded to that evidence, and every scenario invalidated by a changed premise has been rerun while unchanged blockers and coverage are carried forward.

## 4. Challenge and reconcile findings

Trace each candidate finding through:

`trigger → violated contract or failed control → propagation → material consequence`

Before retaining it, test the strongest plausible reason the candidate could be false or inapplicable. Inspect relevant guards, caller obligations, upstream guarantees, recovery behavior, and scope assumptions. Counterevidence counts only when its applicability to the failing scenario is established; a demonstrated failed contract remains established until applicable evidence refutes or corrects it.

A trigger is not automatically a system defect. Group observations when the same violated contract or failed control explains them and attach downstream symptoms as evidence. Preserve independently material failed controls as separate findings, even when one trigger exposed them.

A finding survives only when it has evidence, a material consequence, and one supported disposition:

- **Correction:** one smallest coherent correction is supported and addresses the demonstrated failure while preserving neighboring requirements and guarantees.
- **Diagnostic handoff:** the defect is demonstrated but its causal boundary or correction is not. Include the unresolved boundary, missing discriminating evidence, smallest safe next check, and fitting owner.
- **Direction handoff:** the defect and correction constraints are established but materially different consequential corrections remain credible. Include the defect evidence, hard constraints and invariants, exact decision boundary, and established options without ranking.

Hand comparative correction selection to `direction-selection` when the surrounding task includes choosing the direction. System review preserves the diagnosis and does not search for or rank replacements. An uncertain correction does not weaken an established defect; use a diagnostic or direction handoff instead.

Treat preferences, generic best practices, absent fashionable patterns, and unsupported future scale as non-findings. A visibility gap may affect the verdict, finding qualification, causal attribution, or correction determination. It must not erase a demonstrated defect or force an invented correction.

Record **Close when** for every finding: the exact scenario and observable positive evidence required to establish correction. On re-review, close a finding only when that condition is positively established for the current target.

**Complete when:** every surviving finding has survived an applicable countercheck, is materially distinct and evidence-backed, has one supported disposition and closure condition, and every decision-sensitive gap is explicit.

## 5. Return the review

### Agent / controller handoff

Use the full structured record for callers that must continue the work:

### System Review

- **Scope:** reviewed system boundary and review question
- **Stage and target:** applicable stage, revision, configuration, environment, workload, and time window
- **Operating bar:** applicable bar
- **Verdict:** `PASS` | `PASS WITH RISKS` | `CHANGES REQUIRED` | `INSUFFICIENT EVIDENCE`

### Findings

For each demonstrated defect:

**[S-NN] Title**
- **Evidence:** decisive normative, structural, behavioral, or external evidence
- **Scenario:** exposing behavior or failure path
- **Failure:** violated contract or failed control
- **Consequence:** material effect
- **Correction:** smallest coherent correction
- **Close when:** scenario and observable evidence required to close the finding

Replace `Correction` when another disposition applies:

- **Diagnostic handoff:** unresolved boundary, missing discriminating evidence, smallest safe next check, and owner
- **Direction handoff:** decision boundary, hard constraints, established evidence, and options without ranking

### Visibility Gaps

Only gaps capable of changing a conclusion:

**[V-NN] Gap**
- **Missing evidence:** what cannot be established
- **Decision effect:** what verdict, finding, cause, or correction it could change
- **Next check / owner:** smallest safe evidence route and fitting owner

### Residual Risks

Only known, evidence-backed exposures accepted at the current operating bar:

**[R-NN] Risk**
- **Evidence:** what establishes the exposure
- **Exposure:** what may happen and under what conditions
- **Why accepted:** why no correction is required at the current bar
- **Reopen if:** observable condition that invalidates the acceptance

A residual risk is a sufficiently understood exposure accepted at the current bar. A visibility gap is missing evidence whose plausible answers could materially change a conclusion. Unverified uncertainty is not a residual risk.

### Validated Areas

Material contracts and scenarios supported without a demonstrated defect. State the evidence type and reach; do not imply broader correctness.

### Verification

Scenarios, tests, inspections, observations, and authorities actually used; include blocked checks and invalidated re-review coverage that was rerun.

Apply verdict precedence:

1. `CHANGES REQUIRED` — at least one demonstrated material defect remains, even when visibility gaps also exist.
2. `INSUFFICIENT EVIDENCE` — no demonstrated defect requires changes, but a decision-sensitive gap prevents deciding whether the operating bar is met.
3. `PASS WITH RISKS` — no correction is required, no verdict-blocking gap remains, and at least one residual-risk record is present.
4. `PASS` — within the recorded stage and target, applicable scenarios support the required outcome and no defect, verdict-blocking gap, or residual risk remains.

### User-facing presentation

Present the result once rather than narrating the review process. Lead with **verdict and scope**. Then show findings in descending consequence, keeping the decisive evidence, supported disposition or next action, and **Close when** condition beside each finding. End with only the material coverage limits: decision-sensitive visibility gaps, accepted residual risks, or evidence boundaries that qualify the verdict.

Omit empty sections and repeated information. A clean focused review may be only a few lines. Expand only for meaningful findings, uncertainty, or a user-requested broad review. Provide the full agent/controller handoff when the user requests it or another agent needs it for continuation.

Stop when the applicable scenarios are evaluated and the evidence supports the stage-scoped verdict. A preferable alternative system or architecture is not by itself a reason to continue.

**Complete when:** the verdict follows deterministically from the findings, visibility gaps, residual risks, validated areas, and verification actually recorded; the user can identify the result, consequence, next action, and material limits without reconstructing the process; and any caller receives the full information required to continue.