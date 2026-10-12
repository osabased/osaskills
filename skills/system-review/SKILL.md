---
name: system-review
description: Reviews how multiple components, services, or stages behave together and returns a scoped verdict (CHANGES REQUIRED, INSUFFICIENT EVIDENCE, PASS WITH RISKS, or PASS) backed by traced failure scenarios and closure evidence. Use when correctness depends on interactions rather than one file - end-to-end or integration bugs, retries, crashes and partial failures, idempotency or double-charging, ordering and race conditions, cache/queue/database consistency, client-server or service handoffs - or when asked "will this hold up?", "review this flow end to end", or "what happens if X fails midway?". Not for single-function code review, style feedback, or choosing between designs.
---

# System Review

Decide whether a system achieves its required outcome across its interacting parts. Follow the smallest evidence path that answers the review question.

## Frame the review

- State the required outcome and the review question.
- Review only the components the outcome passes through. Add more only when a dependency matters or the user asks.
- Record what the conclusion depends on: environment (dev/staging/prod), exact version or commit, configuration, and load.
- If one component alone answers the question, say a system review isn't needed and review that component directly.
- Report defects and the constraints a fix must respect. Leave broader design choices to the user unless they asked for a comparison.

## Trace the behavior

Inspect both sides of each interaction that matters: who owns the state or control, what each side promises, and what the caller can observe. Follow identity, units, ordering, acknowledgements, and recovery where they affect the outcome.

Write discriminating scenarios as **setup → event → intermediate state → expected observable result**. For interruption or retry, separate the last committed effect from the first unconfirmed one. Example: the payment debit has committed, the receipt row is not yet written, the process crashes, and the client retries — what does the retry see?

Trace the consequence through the boundary instead of inferring it from one component. Resolve unknowns you can inspect. Use runtime evidence for runtime claims, structural evidence for structural claims, and current primary documentation for version-sensitive external facts. Scope every claim to the target and conditions its evidence covers. Run probes only within your authorization, and name checks you could not run.

## Decide what is a finding

A defect needs all three: **applicable evidence, a violated requirement or failed control, and a material consequence.** Before keeping one, test the strongest counterevidence: upstream guarantees, caller obligations, guards, recovery, or a wrong scope assumption. Preferences and generic best practices alone are not defects.

Group symptoms of the same failed control; keep independent failures separate. Give each finding one next step:

- **Correction:** the smallest coherent fix, when cause and effect are established and neighboring requirements stay intact.
- **Diagnostic handoff:** when the cause or fix is unresolved, the missing evidence, the next safe check, and who runs it.
- **Design choice:** when competing fixes trade off, the constraints, options, evidence, and deciding tradeoff. Compare them only if the user asked you to choose.

Every open defect gets **Close when:** the exact scenario and positive observable evidence that would close it. A plausible patch, or a failure that stops reproducing, is not enough unless it meets that condition.

Separate a **visibility gap** (missing evidence that could change a conclusion) from a **residual risk** (an understood, evidence-backed exposure accepted at the operating bar). Neither cancels a demonstrated defect.

Use independent perspectives (for example parallel subagents) only when different expertise or evidence could change a conclusion. When independent passes already exist and sharing evidence between them could matter, read [cross-agent synthesis](references/cross-agent-synthesis.md).

## Return the verdict

Use the first verdict that applies:

| Verdict | Condition |
|---|---|
| `CHANGES REQUIRED` | A demonstrated material defect remains. |
| `INSUFFICIENT EVIDENCE` | No defect requires changes, but a deciding evidence gap remains. |
| `PASS WITH RISKS` | No defect or blocking gap remains; an understood residual risk is accepted. |
| `PASS` | Evidence supports the outcome at the recorded environment and version, with no open defect, blocking gap, or residual risk. |

Output shape (omit empty sections):

```
**Verdict:** <VERDICT> — scope: <components/boundary>; <environment, version>
**Findings**
- <ID>: <requirement violated>. Scenario: setup → event → state → result. Evidence: … Consequence: … Next: <correction | diagnostic check + owner | design choice>. Close when: …
**Evidence gaps that could change the verdict:** …
**Accepted risks:** …
**Checked and passing / checks run:** …
```

On re-review, keep finding IDs, reuse unaffected evidence, and rerun only scenarios a change could affect. Retry blocked checks when their prerequisites change. Keep defects open until fresh evidence meets `Close when`. Evidence invalidated by a change cannot support a new PASS.

**Done when:** the evidence answers the review question, or names its exact blocker, and supports the verdict at the requested scope.
