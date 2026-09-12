---
name: roblox-resource-acquisition
description: Find, qualify, adopt, refresh, or repair Roblox community resources and their reusable resource guidance.
compatibility: Bundled validator scripts require Python 3.10+ and dependencies from requirements.txt.
---

# Roblox Resource Acquisition

Use for an actual community-resource decision or existing resource-lifecycle task, not merely because a dependency is present.

## Core rule

Task fit and qualification justify a resource choice; a plausible search result does not. Keep resource trust, runtime verification, generated-skill validation, installation, and operational host adoption distinct.

## Route the operating mode

Choose the narrowest mode satisfying the request. Read only its active references and finish the authorized decision or lifecycle action rather than adding another mode as extra scope.

### `evaluate/compare`

Inspect, evaluate, compare, or select without integration or reusable child/host adoption.

Read [qualification-workflow.md](references/qualification-workflow.md) for qualification and [state-policy.md](references/state-policy.md) for truthful status and reporting. Stop after the requested evidence and decision. Do not integrate the resource or generate a child skill as extra scope.

### `acquire/adopt`

Use or integrate a resource beyond evaluation, after applicable qualification and verification from [qualification-workflow.md](references/qualification-workflow.md) are satisfied and within authorized project scope.

Reusable child guidance and operational host adoption are **optional subscopes**, not prerequisites. When reusable child guidance is in scope, read [generation-validation.md](references/generation-validation.md). When operational host adoption of generated guidance is requested, read [operational-lifecycle.md](references/operational-lifecycle.md) and apply its adoption gate.

### `refresh`

For an existing resource skill with known canonical identity, confirm recorded/installed state and refresh only affected source/version/API facts using [qualification-workflow.md](references/qualification-workflow.md); restart broad discovery only when current evidence makes the resource materially unsuitable or alternatives were requested. Prior runtime proof remains bound to its recorded target.

Use [generation-validation.md](references/generation-validation.md) to update guidance and rerun invalidated structural/behavioral checks. Read [operational-lifecycle.md](references/operational-lifecycle.md) when installed/source/legacy/host state or a post-adoption defect is implicated, and [repair-loop.md](references/repair-loop.md) when a proof, test, or generated-child defect needs iterative repair.

### `repair/reconcile`

For a child defect, installed/source mismatch, adverse current observation, legacy state, or newer parent-side block, load only the affected repair branch. Read [operational-lifecycle.md](references/operational-lifecycle.md) for installed/source/legacy/host mismatch or post-adoption defects, and [repair-loop.md](references/repair-loop.md) when proof, test, or generated-child defects require iterative repair.

Read [qualification-workflow.md](references/qualification-workflow.md) only when upstream identity, source facts, qualification, or trust are themselves in question. Read [generation-validation.md](references/generation-validation.md) only for child validation surfaces invalidated by the repair.

## Shared invariants

- Preserve requested resource targets, roles, selectors, and scope; substitution needs authority.
- Keep technical fit, trust, verification, generated-skill validation, installation, and host adoption as separate states.
- Bind trust/evidence to canonical identity and material selector/version. Same-named forks, mirrors, modified vendored copies, and re-uploads do not inherit it.
- Use primary/canonical sources for resource behavior and current Roblox Creator Hub documentation for material platform behavior. Verify APIs rather than inventing them from names or analogous libraries.
- An unexecuted runtime check is `unverified` or `unavailable`, not passing; an observed failure remains `failed`.
- Keep proof proportional to intended use and isolated/reversible where practical. Preserve server authority, validate client-controlled inputs, and protect credentials/secrets.
- Do not publish, spend money, or perform irreversible project mutations merely to prove a resource works.
- Evaluation or ordinary integration grants no child-generation or host-adoption authority; those scopes must be requested or required by the task.

## Completion

Read [state-policy.md](references/state-policy.md) before recording or updating state and reporting completion in any mode. Finish the requested decision/action with truthful applicable verification/validation statuses and explicit blocked use, unavailable proof, owner actions, or reconciliation mismatches. Continue permitted work within that mode; an intermediate qualification result is not completion of authorized adoption.
