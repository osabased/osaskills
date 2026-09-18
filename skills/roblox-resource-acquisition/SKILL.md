---
name: roblox-resource-acquisition
description: Find, evaluate, adopt, refresh, or repair Roblox community resources and their reusable guidance; also activate when child instructions are stale or defective, a recurring workaround is undocumented, verification fails, or installed and recorded state disagree.
---

# Roblox Resource Acquisition

Use community resources only when the task actually requires a resource decision or existing resource-lifecycle work. Keep project-use authority, resource trust, runtime verification, generated-skill validation, installation, and operational host adoption distinct.

## Core rule

Choose a community resource only when task fit and qualification justify it. A plausible search result or mere dependency availability is not qualification. When another durable project contract supplies the resource identity, pin, role, or replacement policy, preserve that target and authority rather than reopening selection.

## Repair interrupt

Activate this skill in `repair/reconcile` mode when using a resource or generated child exposes reusable friction, even if a local workaround succeeds and the immediate task can continue.

A workaround is defect evidence when following the reusable guidance requires guessing, bypassing an instruction, rediscovering the same adjustment, or making an undocumented correction likely to recur. A harmless task-local adjustment that does not reveal a reusable instruction, resource, identity, version, or verification problem is not a repair interrupt.

- **Hard defect:** Correctness, security, canonical identity, selected version, or verification is unreliable. Stop the dependent work, preserve the smallest reproduction, and enter state reconciliation plus the repair loop before continuing.
- **Soft defect:** The workaround is safe, reversible, and does not weaken correctness or a trust boundary. The immediate task may continue, but invoke this repair diagnosis and surface the reproduction, workaround, and durable guidance correction before completion. Do not silently absorb the defect as task-local friction.
- **Authority:** Invocation authorizes diagnosis and reporting. Edit this package, a generated child, lifecycle state, or another artifact only when the current request authorizes that mutation. Otherwise propose the precise durable correction and leave the affected artifact unchanged.

A soft instruction defect does not by itself require unrelated pin, provenance, record, or learning reconciliation. Escalate into full state reconciliation only when the classification is hard, state is missing or mismatched, a current block exists, verification fails or drifts, or an authorized repair invalidates lifecycle evidence.

## Route the operating mode

Choose the narrowest mode that satisfies the request, then read only the references required by that mode.

### `evaluate/compare`

Use when the task is to inspect, evaluate, compare, or select a resource without using/integrating it or creating/operationally adopting reusable child guidance.

1. Read [references/qualification-workflow.md](references/qualification-workflow.md).
2. Read [references/state-policy.md](references/state-policy.md) for truthful trust/verification status and output discipline.
3. Stop after the requested evidence and decision. Do not integrate the resource or generate a child skill as extra scope.

### `acquire/adopt`

Use when the task requires selecting, using, installing, or integrating a resource beyond evaluation. Reusable child guidance and operational host adoption are optional subscopes, not prerequisites for this mode.

1. Read [references/qualification-workflow.md](references/qualification-workflow.md).
2. When the resource is or becomes a durable project-standard dependency, or another project contract supplies a fixed resource target, read [references/project-adoption.md](references/project-adoption.md) before mutation.
3. Integrate or use the resource only to the authorized task/project scope after its applicable qualification and verification requirements are satisfied. Preserve externally owned identity/pin/role decisions exactly; a verification block returns to that authority rather than authorizing substitution.
4. When reusable child guidance is in scope, read [references/generation-validation.md](references/generation-validation.md).
5. When operational host adoption of generated guidance is requested, read [references/operational-lifecycle.md](references/operational-lifecycle.md) for the adoption gate.
6. Read [references/state-policy.md](references/state-policy.md) before recording state or reporting completion.

### `refresh`

Use for an existing resource skill whose canonical identity is known and whose source/version facts or generated guidance may have drifted.

1. Confirm canonical identity, project-use authority, and installed/recorded state first; restart broad discovery only when current evidence makes a resource-acquisition-owned target materially unsuitable or alternatives were requested. An externally owned target returns evidence to its authority instead of being independently replaced or upgraded.
2. Read only the affected parts of [references/qualification-workflow.md](references/qualification-workflow.md) needed to refresh volatile source/version/API facts. Prior runtime proof remains bound to its recorded target.
3. Read [references/project-adoption.md](references/project-adoption.md) when project-use state, authority, onboarding, or project-local child placement is affected.
4. Read [references/generation-validation.md](references/generation-validation.md) to patch and rerun the structural and behavioral checks invalidated by the refresh.
5. If installed/source/host-adoption state, a hard post-adoption defect, or an authorized child repair is implicated, read [references/operational-lifecycle.md](references/operational-lifecycle.md).
6. If the refresh exposes a proof, test, or generated-child defect that needs iterative repair, read [references/repair-loop.md](references/repair-loop.md).
7. Read [references/state-policy.md](references/state-policy.md) before updating records or status.

### `repair/reconcile`

Use for a stale or defective generated child, recurring undocumented workaround, failed verification, installed/source-state mismatch, adverse current observation, resource-record contract mismatch, or a newer parent-side block. The user need not name this skill: the Repair interrupt above is an implicit activation rule.

1. Classify the interrupt as hard, soft, or harmless task-local adjustment and capture the task, installed state, expected behavior, observed behavior, smallest reproduction, and any workaround.
2. For a soft instruction defect, diagnose the reusable guidance gap and state the durable correction. Continue safe reversible immediate work when useful, but do not force unrelated provenance or lifecycle reads merely because repair diagnosis activated.
3. For a hard defect, installed/source/host-adoption mismatch, failed verifier, current block, or authorized child repair, read [references/operational-lifecycle.md](references/operational-lifecycle.md) to reconcile affected state and host lifecycle.
4. For project-use authority, onboarding, resource replacement/removal, or project-local child-placement repair, read [references/project-adoption.md](references/project-adoption.md).
5. For a proof, test, or generated-child defect that needs iterative repair, read [references/repair-loop.md](references/repair-loop.md).
6. Read [references/qualification-workflow.md](references/qualification-workflow.md) only when upstream identity, source facts, qualification, or trust are themselves in question.
7. Read [references/generation-validation.md](references/generation-validation.md) only for child validation surfaces invalidated by the repair, and only after the child edit is authorized.
8. Read [references/state-policy.md](references/state-policy.md) before recording the outcome or proposing an unauthorized package change.

## Shared invariants

Hold these across every mode:

- Preserve positive resource targets, their roles, selectors, requested scope, and project-use authority; do not silently substitute an alternative or advance an externally owned pin.
- Treat project-use authority, technical fit, trust, verification, generated-skill validation, installation, and operational host adoption as separate states.
- Bind trust and evidence to canonical identity plus any material selector/version; same-named forks, mirrors, modified vendored copies, and re-uploads do not inherit it automatically.
- Prefer primary/canonical sources for resource behavior and current Roblox Creator Hub documentation for platform behavior when material.
- Never invent an API from naming conventions or analogous libraries.
- Never label an unexecuted runtime check as passing. Use `unverified`, `unavailable`, or `failed` truthfully.
- Keep resource proof proportional to the intended use and use isolated/reversible verification where practical.
- Preserve Roblox server authority, validate client-controlled inputs, and never expose credentials or secrets merely to validate a resource.
- Do not publish, spend money, or perform irreversible project mutations merely to prove a resource works.
- Generate reusable child guidance only when that lifecycle scope is requested or required by the task; evaluation or ordinary resource integration alone grants no generation or host-adoption authority.

## Completion

A mode is complete only when its requested decision or lifecycle action is finished, every applicable project-use/verification/validation status is truthful, the project onboarding index matches any durable adopted state in scope, and any blocked use, unavailable proof, owner action, authority conflict, or reconciliation mismatch is explicit. Use [references/state-policy.md](references/state-policy.md) for the final reporting contract.
