---
name: roblox-resource-acquisition
description: Proactively evaluate and adopt Roblox libraries/modules and development tools when reuse could reduce development or maintenance effort; compare candidates, create reusable child skills, and refresh or repair resources and guidance when defects, recurring workarounds, verification failures, or state mismatches arise.
---

# Roblox Resource Acquisition

During Roblox implementation, proactively consider libraries/modules and development tools when reuse could reduce total implementation and maintenance effort. First decide whether an external resource is needed. When adoption is warranted, read [adoption policy](references/adoption-policy.md) for the agreed scope, autonomy, selection priorities, and completion gate. Default adoption includes integration, verification, and a validated reusable child installed at user scope; explicit evaluation-only or narrower requests retain their boundary. Keep project-use authority, resource trust, runtime verification, generated-skill validation, installation, and operational host adoption distinct.

## Core rule

Choose a community resource only when task fit and qualification justify it. A plausible search result or mere dependency availability is not qualification. For open-ended selection, establish the actual use before choosing; use the [qualification workflow](references/qualification-workflow.md#0-decide-whether-acquisition-is-warranted) for decision-sensitive intake and supported recommendations, including native/custom acquisition choices when restoration or updating matters. Narrow download-only scope does not remove that decision work. When another durable project contract supplies the resource identity, pin, role, or replacement policy, preserve that target and authority rather than reopening selection.

## On-demand upkeep

At activated use, check for the sibling `.skill-maintenance/roblox-resource-acquisition.json` promotion guard; ordinary dependent use waits while it exists. For a task-relevant current fact, acquisition/upgrade or generation/refresh, source drift, reusable defect, or consequential practice decision, read [on-demand maintenance](references/on-demand-maintenance.md). It holds the user's narrow standing factual-repair grant, source-observation and guarded-promotion rules. Keep a healthy immutable child's conditional fast path; use-time upkeep adds no schedule or unrelated source survey.

## Repair interrupt

Activate this skill in `repair/reconcile` mode when using a resource or generated child exposes reusable friction, even if a local workaround succeeds and the immediate task can continue.

A workaround is defect evidence when following the reusable guidance requires guessing, bypassing an instruction, rediscovering the same adjustment, or making an undocumented correction likely to recur. A harmless task-local adjustment that does not reveal a reusable instruction, resource, identity, version, or verification problem is not a repair interrupt.

Classify the original defect by its demonstrated correctness, ownership, identity, security, or verification impact. A safe workaround alone does not establish that the defect is soft. When the effect of the defective guidance is unknown, state that uncertainty and the smallest check needed to determine it before continuing the affected use.

- **Hard defect:** Correctness, security, canonical identity, selected version, or verification is unreliable. Stop the dependent work, preserve the smallest reproduction, and enter state reconciliation plus the repair loop before continuing.
- **Soft defect:** The workaround is safe, reversible, and does not weaken correctness or a trust boundary. The immediate task may continue, but invoke this repair diagnosis and surface the reproduction, workaround, and durable guidance correction before completion. Do not silently absorb the defect as task-local friction.
- **Authority:** Invocation authorizes diagnosis and reporting. Edit this package, a generated child, lifecycle state, or another artifact only when the current request or the approved on-demand maintenance policy authorizes that mutation. Otherwise propose the precise durable correction and leave the affected artifact unchanged.

A soft instruction defect does not by itself require unrelated pin, provenance, record, or learning reconciliation. Escalate into full state reconciliation only when the classification is hard, state is missing or mismatched, a current block exists, verification fails or drifts, or an authorized repair invalidates lifecycle evidence.

## Route the operating mode

Choose the narrowest mode that satisfies the request, then read only the references required by that mode.

### No acquisition needed

For a capability-directed task without a positive resource target, check whether Roblox built-ins, an adequate authorized project capability, or small local code already solve it cleanly. Use task-relevant supplied constraints, owner decisions, learnings and known blocks; do not open a registry, comparison rubric, or lifecycle ledger just to reject unnecessary acquisition. If local work is sufficient, complete it and briefly report the choice and its validation. No resource record, new child, or host-status ledger is needed for that outcome. A named adoption target or material uncertainty proceeds to the appropriate mode below.

### `evaluate/compare`

Use when the task is to inspect, evaluate, compare, or select a resource without using/integrating it or creating/operationally adopting reusable child guidance.

1. Read [references/qualification-workflow.md](references/qualification-workflow.md). For any comparison or selection among candidates, also read [references/evaluation-rubric.md](references/evaluation-rubric.md) directly.
2. Apply the rubric's hard gates before comparing survivors under the established criteria and priorities. Use the same intended-use criteria and evidence standard for every candidate; popularity is discovery evidence, not a qualification shortcut.
3. Keep source findings and executed proof distinct. Read [references/state-policy.md](references/state-policy.md) when recording resource state, reporting an existing trust/verification claim, or encountering an owner conflict or current block.
4. Stop after the requested evidence and decision. Integration/project mutation, child generation or validation, and operational host adoption are all out of scope unless separately requested.

Give a concise answer containing the task criteria, hard-gate findings, decision and material evidence or uncertainty. State that the result is evaluation-only; omit unused integration, child-validation and host-adoption status fields. Preserve a relevant supplied owner decision, learning or current block rather than hiding it to shorten the answer.

### `acquire/adopt`

Use when a Roblox implementation task benefits from acquiring a library/module or development tool, or the user asks to use, install, integrate, or adopt one. Follow the full adoption scope in [adoption policy](references/adoption-policy.md) unless the current request explicitly narrows it. Ordinary healthy use of an already adopted resource stays on its child's common path.

1. Read [references/qualification-workflow.md](references/qualification-workflow.md).
2. When the resource is or becomes a durable project-standard dependency, or another project contract supplies a fixed resource target, read [references/project-adoption.md](references/project-adoption.md) before mutation.
3. Qualify the exact target, stage reversible integration, and execute the applicable resource and project-integration checks. A missing required check leaves adoption pending; continue independent preparation and name the blocker. Preserve externally owned identity/pin/role decisions exactly; a verification block returns to that authority rather than authorizing substitution.
4. When reusable child guidance is in scope, read [references/generation-validation.md](references/generation-validation.md). It is in scope for every directly adopted library/module or development tool by default; generate or reuse an exact-target child with portable guidance.
5. When operational host adoption of generated guidance is requested, read [references/operational-lifecycle.md](references/operational-lifecycle.md) for the adoption gate. The full adoption default requests this at user scope; install the validated child and prove the applicable host checks without adding a routine confirmation stop.
6. Read [references/state-policy.md](references/state-policy.md) before recording state or reporting completion.
7. Report five statuses separately for the exact adopted target: trust basis; authorized project-use role; resource/runtime verification; generated-child validation; and per-host adoption. Use `not applicable` for child guidance or host adoption only when an explicit narrower request excludes it, rather than silently omitting a required default stage.

Also state technical fit separately from those five lifecycle statuses. The response must contain this status ledger; listing “report statuses” as a future action does not complete adoption reporting.

Use `unverified` when no applicable execution proof has run and no material required check is known to be blocked. Use `unavailable` only when a material required check has been identified and cannot run in the available environment; name that check.

### `refresh`

Use for an existing resource skill whose canonical identity is known and whose source/version facts or generated guidance may have drifted.

1. Before any refresh work, confirm canonical identity and material selector, project-use authority, actual installed state, and recorded state. State mismatches are reconciliation work, not permission for broad rediscovery. Restart broad discovery only when current evidence makes a resource-acquisition-owned target materially unsuitable or alternatives were requested. An externally owned target returns evidence to its authority instead of being independently replaced or upgraded.
2. List the inputs that changed since the recorded evidence—such as selector/source, API surface, intended use, integration path, generated child, or host state—and read only the affected parts of [references/qualification-workflow.md](references/qualification-workflow.md). Rerun only proof invalidated by those changed inputs. Prior runtime proof remains bound to its recorded target and unchanged evidence is reused.
3. Read [references/project-adoption.md](references/project-adoption.md) when project-use state, authority, onboarding, or project-local child placement is affected.
4. Read [references/generation-validation.md](references/generation-validation.md) to patch and rerun the structural and behavioral checks invalidated by the refresh.
5. If installed/source/host-adoption state, a hard post-adoption defect, or an authorized child repair is implicated, read [references/operational-lifecycle.md](references/operational-lifecycle.md).
6. If the refresh exposes a proof, test, or generated-child defect that needs iterative repair, read [references/repair-loop.md](references/repair-loop.md).
7. Read [references/state-policy.md](references/state-policy.md) before updating records or status.

The refresh answer must include a changed-input ledger: changed inputs, unchanged inputs, evidence invalidated by each change, and the exact checks to rerun. A generic request to revalidate the child is incomplete.

### `repair/reconcile`

Use for a stale or defective generated child, recurring undocumented workaround, failed verification, installed/source-state mismatch, adverse current observation, resource-record contract mismatch, or a newer parent-side block. The user need not name this skill: the Repair interrupt above is an implicit activation rule.

1. Classify the interrupt as hard, soft, or harmless task-local adjustment and produce a complete defect handoff: exact canonical identity and selector; affected task/use; installed and recorded state; expected and observed behavior; smallest reproduction; current impact/block; safe workaround if any; proposed durable correction; invalidated evidence; owner/authority; and the verification required to close it.
2. For a soft instruction defect, diagnose the reusable guidance gap and state the durable correction. Continue safe reversible immediate work when useful, but do not force unrelated provenance or lifecycle reads merely because repair diagnosis activated. Read [references/state-policy.md](references/state-policy.md) directly for final status and authority reporting even when no persistent record will change.
3. For a hard identity, selector, or security defect, or when installed and recorded identity cannot be reconciled, directly read [references/operational-lifecycle.md](references/operational-lifecycle.md), [references/repair-loop.md](references/repair-loop.md), [references/qualification-workflow.md](references/qualification-workflow.md), and [references/state-policy.md](references/state-policy.md) before dependent work continues. For other hard defects, installed/source/host-adoption mismatch, failed verifier, current block, or authorized child repair, read [references/operational-lifecycle.md](references/operational-lifecycle.md) to reconcile affected state and host lifecycle.
4. For project-use authority, onboarding, resource replacement/removal, or project-local child-placement repair, read [references/project-adoption.md](references/project-adoption.md).
5. For a proof, test, or generated-child defect that needs iterative repair, read [references/repair-loop.md](references/repair-loop.md).
6. Read [references/qualification-workflow.md](references/qualification-workflow.md) when upstream identity, source facts, qualification, trust, or a hard security boundary is in question.
7. Read [references/generation-validation.md](references/generation-validation.md) only for child validation surfaces invalidated by the repair, and only after the child edit is authorized.
8. Read [references/state-policy.md](references/state-policy.md) before recording the outcome or proposing an unauthorized package change.

Fill the defect handoff from supplied facts in the current answer. When a field is genuinely unknown, label that field unknown and state the minimum evidence needed; do not replace the handoff with an action to capture it later.

Make the handoff auditable with explicit fields or equally clear sentences for expected behavior, observed behavior, and smallest reproduction. Do not rely on the reader to infer them from the workaround or correction.

## Shared invariants

Hold these across every mode:

- Preserve positive resource targets, their roles, selectors, requested scope, and project-use authority; do not silently substitute an alternative or advance an externally owned pin.
- Treat project-use authority, technical fit, trust, verification, generated-skill validation, installation, and operational host adoption as separate states.
- Bind trust and evidence to canonical identity plus any material selector/version; same-named forks, mirrors, modified vendored copies, and re-uploads do not inherit it automatically.
- Name that exact canonical identity and material selector/version in every verification claim, including `verified`, `unverified`, `unavailable`, and `failed`. If either coordinate is unknown, say that verification for the exact target cannot yet be determined.
- Prefer primary/canonical sources for resource behavior and current Roblox Creator Hub documentation for platform behavior when material.
- When a relevant source lookup or intended verification cannot run, use the [bounded evidence-route fallbacks](references/search-playbook.md#when-an-evidence-route-fails) before declaring it unavailable. This conditional route also applies to verification of a no-acquisition result.
- Never invent an API from naming conventions or analogous libraries.
- Never label an unexecuted runtime check as passing. Use `unverified`, `unavailable`, or `failed` truthfully.
- Keep resource proof proportional to the intended use and use isolated/reversible verification where practical.
- Preserve Roblox server authority, validate client-controlled inputs, and never expose credentials or secrets merely to validate a resource.
- Do not publish, spend money, or perform irreversible project mutations merely to prove a resource works.
- Generate or reuse a reusable child for every directly adopted resource under the full adoption default. Explicit evaluation-only or narrower requests exclude the stages they limit; mere transitive presence does not create a child-generation task.

## Completion

Full adoption is pending until all required resource/integration, child-validation, and host checks pass; installed files or a recommendation alone do not finish it. A mode is complete only when its requested decision or lifecycle action is finished, every applicable project-use/verification/validation status is truthful and bound to the named canonical identity plus selector, the project onboarding index matches any durable adopted state in scope, and any blocked use, unavailable proof, owner action, authority conflict, or reconciliation mismatch is explicit. Use [references/state-policy.md](references/state-policy.md) for the final reporting contract.
