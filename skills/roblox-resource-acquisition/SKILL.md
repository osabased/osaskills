---
name: roblox-resource-acquisition
description: Roblox resource lifecycle for finding, evaluating, adopting, refreshing, or repairing community resources and reusable guidance around them.
compatibility: Bundled validator scripts require Python 3.10+ and dependencies from requirements.txt.
---

# Roblox Resource Acquisition

Use community resources only when the task actually requires a resource decision or existing resource-lifecycle work. Keep project-use authority, resource trust, runtime verification, generated-skill validation, installation, and operational host adoption distinct.

## Core rule

Choose a community resource only when task fit and qualification justify it. A plausible search result or mere dependency availability is not qualification. When another durable project contract supplies the resource identity, pin, role, or replacement policy, preserve that target and authority rather than reopening selection.

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
5. If installed/source/host-adoption state or a post-adoption defect is implicated, read [references/operational-lifecycle.md](references/operational-lifecycle.md).
6. If the refresh exposes a proof, test, or generated-child defect that needs iterative repair, read [references/repair-loop.md](references/repair-loop.md).
7. Read [references/state-policy.md](references/state-policy.md) before updating records or status.

### `repair/reconcile`

Use for a generated child defect, installed/source-state mismatch, adverse current observation, resource-record contract mismatch, or a newer parent-side block.

1. For installed/source/host-adoption mismatch or a post-adoption defect, read [references/operational-lifecycle.md](references/operational-lifecycle.md) to reconcile current state and host lifecycle.
2. For project-use authority, onboarding, resource replacement/removal, or project-local child-placement repair, read [references/project-adoption.md](references/project-adoption.md).
3. For a proof, test, or generated-child defect that needs iterative repair, read [references/repair-loop.md](references/repair-loop.md).
4. Read [references/qualification-workflow.md](references/qualification-workflow.md) only when upstream identity, source facts, qualification, or trust are themselves in question.
5. Read [references/generation-validation.md](references/generation-validation.md) only for child validation surfaces invalidated by the repair.
6. Read [references/state-policy.md](references/state-policy.md) before recording the outcome.

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
