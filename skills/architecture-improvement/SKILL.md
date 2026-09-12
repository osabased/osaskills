---
name: architecture-improvement
description: Make one justified codebase architecture improvement, or return NO CHANGE.
disable-model-invocation: true
---

# Architecture Improvement

Evaluate one bounded scope and complete one coherent architectural improvement when justified. `NO CHANGE` is a successful outcome. Invocation authorizes code changes after the Intervention Gate passes, subject to narrower user instructions; an evaluation-only request remains read-only.

## Contract

This skill owns module, interface, seam, and dependency structure. A local defect, spec deviation, smell, or preferred design belongs to its fitting owner unless architecture materially causes or obstructs a demonstrated need.

Resolve repository-owned facts through available evidence. Escalate user-owned product intent, compatibility policy, reopening an authoritative decision, irreversible migration, or another material choice the evidence cannot settle. Other observations do not expand this invocation.

## 1. Establish the target

Use the user's bounded module, subsystem, pain point, or change. For a whole-repository request or no named target, use bounded triage of relevant history, current work, recurring fixes, test friction, and repository guidance to select the strongest-supported area. If none warrants inspection, return `NO CHANGE`. Churn is a lead, not intervention evidence.

Read the instructions, requirements, ADRs, tests, and nearby implementation that bear on this target. Before writes, establish its starting revision, pre-existing changes, and the baseline needed to distinguish task-caused failures.

When a large or unfamiliar target, independent mapping work, or controller-context cost makes delegation worthwhile, read [RECONNAISSANCE.md](references/RECONNAISSANCE.md). Otherwise inspect directly. Use `$codebase-design` when available and a concrete architecture-design question needs its guidance, rather than loading it for every assessment. Repository authority remains controlling.

## 2. Build intervention evidence

Connect a demonstrated need to an architectural cause through relevant callers, dependencies, interfaces, tests, and history. Leads include recurring coordinated edits, duplicated caller policy, an obstructed authorized near-term change, interface complexity, inaccessible behavioral tests, recurring seam failures, and pass-through structures that relocate change knowledge.

A credible candidate identifies the need and consequence, supporting provenance, architectural cause, affected behavior/callers/tests, smallest local alternative, expected locality or testability gain, migration/regression/permanent abstraction cost, and observable success evidence. Record only decision-relevant detail.

Distinguish independent problems, symptoms of one shared cause, and style disorder. A delegated claim needs applicable provenance; cross-area inference, conflicting packets, or mainly low-capability scans warrant a focused challenger probe or direct decisive reasoning.

## 3. Apply the Intervention Gate

Architectural change requires support for all seven conditions:

1. **Demonstrated need:** recurring engineering cost, a current material consequence, or an authorized near-term change materially obstructed by the structure.
2. **Architectural causality:** module, interface, seam, or dependency structure materially causes or obstructs that need.
3. **Direct improvement:** the change addresses the need instead of relocating complexity or changing style.
4. **Superiority:** a better-supported outcome than doing nothing or making the smallest local correction.
5. **Proportionality:** benefit exceeds migration work, regression exposure, and permanent structural cost.
6. **Compatibility:** behavior, constraints, and authoritative decisions remain satisfied, or authority exists to revise them.
7. **Verifiability:** observable checks can establish preserved behavior and the claimed architectural benefit.

Test the strongest applicable case for the current design, a local cause/correction, speculative benefit, relocated knowledge, or an ADR-backed constraint. Invocation, unfamiliar organization, hypothetical scale, and cleaner-looking alternatives do not establish need. Keep the threshold fixed when no candidate survives.

## 4. Choose the route

| Route | Evidence-supported condition |
| --- | --- |
| `NO CHANGE` | No credible candidate emerges or none passes the gate. |
| `LOCAL HANDOFF` | A material need exists, but a non-architectural correction is better supported. |
| `EXECUTE` | One bounded objective is justified, safely executable, and verifiable. |
| `PLANNING HANDOFF` | Intervention is justified, but one bounded change would leave an unsafe or incomplete architecture. |
| `BLOCKED` | A user-owned choice, unavailable deciding evidence, or required verification prevents a supported disposition. |

Among independent passing candidates, choose by supported engineering benefit relative to migration, regression, and permanent cost; break material ties with narrower blast radius and simpler verification. Distinct designs for one objective are direction alternatives, not separate improvement candidates.

Resolve ordinary engineering tradeoffs directly. Invoke `$direction-selection` only when materially different consequential designs remain credible with no supported winner; pass the need, constraints, candidates, migration effects, and verification obligations. Its gate must pass for this commitment.

`EXECUTE` requires traceable callers and compatibility obligations, complete retirement or an intentional transition for the old path, runnable verification, and no unresolved material decision. Read [EXECUTION.md](references/EXECUTION.md) and continue through implementation, verification, and cleanup without another approval stop inside existing authorization.

For `PLANNING HANDOFF`, preserve the causal objective, affected behavior, constraints, stabilization, migration order, first executable slice, verification obligations, and retirement conditions for the surrounding planning workflow. Widespread smells do not justify a rewrite.

## Output

Lead with disposition and scope. For `IMPROVED`, state the demonstrated need, change, decisive verification, and material residuals. For `NO CHANGE`, give the decisive reason or strongest rejected candidate when useful. For a handoff or blocker, give the established need, exact boundary, fitting next route, and what would unblock execution. Omit empty fields and gate-by-gate narration.

Read [OUTCOMES.md](references/OUTCOMES.md) when another agent/workflow needs the full record or the user requests it.

**Complete when:** one supported disposition is delivered. Use `IMPROVED` only after the selected objective is implemented, required verification passes, the architectural benefit is observable, and task-created residue is removed. Assessment alone is not completion of an authorized `EXECUTE` route.
