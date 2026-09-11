---
name: astra-workflow
description: Route coding and project work so GPT-5.6 Sol owns the task, GPT-5.6 Luna handles bounded reconnaissance, and GPT-6 Astra is invoked only for prepared consequential decisions.
---

# Astra Workflow

Protect expensive reasoning by separating discovery, judgment, and execution. Run the task under a **GPT-5.6 Sol** controller whenever the harness permits model selection. Sol owns the lifecycle from user request through implementation and verification.

Astra is a temporary decision specialist, not the persistent parent. Luna is an evidence scout, not the decision maker.

## 1. Choose the cheapest sufficient route

Classify only far enough to select one route:

- **Direct** — Sol already has enough context and can reliably solve or implement the task.
- **Reconnaissance** — missing repository or system evidence materially limits Sol, but the remaining judgment does not yet require Astra.
- **Astra** — after relevant evidence is available, a consequential decision remains where materially stronger reasoning is worth the cost.

Use `$reconnaissance` when discovery would otherwise consume substantial controller context, when several independent regions need inspection, or when omission risk justifies parallel evidence gathering. Do not invoke it for one cheap lookup.

Astra is not justified merely because a task is large. Implementation volume, repository size, debugging effort, test failures, or unfamiliar code normally remain Sol/Luna work.

**Complete when:** Sol has either selected a direct route, identified the exact missing evidence, or isolated a prepared consequential decision.

## 2. Prepare the decision before Astra

Invoke **GPT-6 Astra** only when all of these are true:

1. a consequential architecture, solution, specification, or direction decision remains;
2. stronger reasoning could materially improve that decision relative to Sol;
3. relevant discovery has already been completed to the degree practical;
4. the input can be expressed as a compact decision packet rather than a request to explore broadly; and
5. Astra's requested deliverable is a decision or design artifact, not implementation, routine review, or debugging.

If these conditions are not met, continue with Sol or gather the missing evidence first.

Give Astra only the context needed to reason about the decision:

### Decision Packet

- **Objective:** outcome the task must achieve
- **Decision required:** exact consequential question Astra owns
- **Relevant system state:** architecture and behavior that materially constrain the choice
- **Established evidence:** verified or traceable facts
- **Constraints / invariants:** requirements that must remain true
- **Material unknowns:** unresolved facts that could affect the decision
- **Competing considerations:** credible tradeoffs or directions, when known
- **Requested artifact:** exact decision, architecture, solution, or specification needed from Astra

Prefer pointers, summarized evidence, and the smallest decisive excerpts over raw exploration history, shell output, scout transcripts, or broad file dumps.

**Complete when:** Astra can begin consequential reasoning immediately without first reconstructing the repository or task history.

## 3. Bound Astra's work

Astra owns the prepared decision surface only. Ask it to return:

### Astra Decision

- **Decision:** selected direction or solution
- **Architecture / solution:** enough structure for Sol to execute faithfully
- **Rationale:** decisive reasoning and tradeoffs
- **Required invariants:** conditions implementation must preserve
- **Implementation guidance:** boundaries and sequencing that materially affect correctness
- **Risks to verify:** assumptions or failure modes Sol must test
- **Reopen if:** concrete new evidence that would invalidate the decision

When the packet lacks decision-critical evidence, Astra returns:

### NEEDS_EVIDENCE

- **Missing evidence:** smallest unresolved fact set
- **Decision effect:** how plausible answers could change the decision
- **Suggested probe:** narrowest useful investigation

On `NEEDS_EVIDENCE`, Sol resumes ownership, gathers only that evidence, and may resubmit the same decision. Astra does not broaden into repository reconnaissance itself.

One Astra call should normally settle one prepared decision surface. Do not spawn Astra subagents or create an Astra review swarm. Additional Astra work requires a distinct consequential decision or material evidence that reopens the prior one.

**Complete when:** Astra returns an executable decision artifact or a bounded evidence request.

## 4. Return execution to Sol

After an Astra decision, Sol immediately resumes ownership. Sol translates the decision into implementation, performs source edits, runs tests and diagnostics, fixes ordinary defects, and completes verification. Luna may be used for bounded inspection or mechanical verification when that reduces Sol context or parallelizes independent checks.

Routine implementation friction does not reopen Astra. Compiler failures, test failures, missed call sites, local bugs, formatting, lint, and ordinary design adjustments remain Sol/Luna work when the Astra decision still holds.

Re-enter Astra only when new evidence materially weakens a load-bearing premise, violates a `Reopen if` condition, or creates a genuinely new consequential decision. Package the new evidence and affected premise; do not replay the full development history.

**Complete when:** the decision is implemented and verified, or a concrete premise invalidation has been repackaged for Astra.

## Controller rules

- Keep Sol as the long-lived controller. If the current root is not Sol and the harness supports handoff or model switching, move control to Sol before ordinary orchestration.
- Preserve user constraints and authoritative project decisions across every handoff.
- Prefer no delegation over low-value delegation.
- Reuse evidence already present in controller context.
- Keep delegated work bounded and independently checkable.
- Spend Astra on judgment, not token-heavy context acquisition.
- Stop routing once the task is complete; successful verification is not a trigger for another review cycle.

## User-facing result

Do not narrate routing mechanics unless they materially affect the result or the user asks. Present the completed task, decision, verification, and any material residuals. If a required model assignment could not be enforced, disclose that limitation briefly.