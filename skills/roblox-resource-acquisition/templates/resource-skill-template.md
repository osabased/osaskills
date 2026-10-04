---
name: roblox-RESOURCE-SLUG
description: USE-TRIGGER-IN-ONE-SENTENCE; ADD-MATERIAL-ROUTING-EXCLUSION-WHEN-NEEDED
---

# RESOURCE NAME

Use **RESOURCE NAME** for CAPABILITY. Guidance targets **VERSION/COMMIT/STATE** (source reviewed **YYYY-MM-DD**). Resource verification: **VERIFIED/UNVERIFIED/UNAVAILABLE**.

## Use when

- ...

## Do not use when

- ...

## Prerequisites and installation

Resolve the active project and its selected pin/configuration at use time. This child's installation defaults to the resolved project/repository skill scope; an unknown project does not authorize a user/global fallback. Keep task-specific absolute paths and execution history outside this reusable skill. For development tools, name the actual command/configuration, prerequisites and owned generated outputs.

1. ...

## On-demand maintenance

- Promotion guard: At activated use, check `<skill-directory-parent>/.skill-maintenance/<skill-directory-name>.json`; ordinary dependent use waits while it exists. For `required`/`conditional`, the Current-block check below also honors this guard. This presence check still applies to `not-applicable` children. Controlled candidate validation is separate from ordinary operational use.
- Freshness triggers: For a task-relevant current platform/tool claim, acquisition/upgrade or generation/refresh, source drift, reusable defect, or consequential practice decision, invoke `roblox-resource-acquisition` once for the affected scope and read its `references/on-demand-maintenance.md`. Carry the exact target, claim and source/reproduction evidence; an already active maintenance handoff need not recursively invoke itself.
- Target and economy: Resolve the project's adopted target and applicable local compatibility guidance first. Healthy immutable-target use keeps the declared pin/lock/header check, narrow status query and deferred integrity gate; it needs no unrelated latest-release research. Tested factual repairs use the parent's approved policy; dependency versions, architecture/defaults and changed practices return to the user. No scheduled upkeep.

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode when using this guidance requires guessing, bypassing an instruction, repeating a previously discovered workaround, or making an undocumented adjustment likely to recur. A harmless task-local adjustment with no reusable guidance defect is not an interrupt.
- Hard defect: If correctness, security, canonical identity, selected version, or verification is unreliable, stop dependent work and enter the parent reconciliation and repair path before continuing.
- Soft defect: If the workaround is safe and reversible, the immediate task may continue, but invoke the parent repair diagnosis and surface the reproduction, workaround, and durable guidance correction before completion.
- Handoff: Capture the task, installed state, expected behavior, observed behavior, smallest reproduction, workaround, and proposed durable correction. Parent invocation authorizes diagnosis and reporting. Edits require current task authorization or the parent's applicable standing factual-repair grant in `references/on-demand-maintenance.md#approved-authority`; reuse either within its scope without another permission request.

## Common path

Provide the shortest source-grounded setup/use sequence. Derive executable code from the maintained fixture; do not keep a second implementation here. Do not call it runtime-verified unless the recorded resource verification status is `verified`.

```luau
-- Minimal example grounded in the reviewed source/API.
```

## Operational reconciliation

- Policy: REQUIRED/CONDITIONAL/NOT-APPLICABLE — REASON
- Installed-state check: RESOURCE-SPECIFIC CHECK OR IMMUTABLE-INSTALL EXPLANATION
- Expected identity/state: RESOURCE SLUG + CANONICAL URL + PACKAGE ID WHEN APPLICABLE + REVIEWED VERSION/COMMIT/STATE
- Current-block check: For `required` or `conditional`, resolve the installed `roblox-resource-acquisition` parent directory, then before affected use run `python RESOLVED-PARENT-SKILL-DIRECTORY/scripts/check_resource_status.py --pair CHILD-SKILL-DIRECTORY MATCHING-RECORD.yaml`; replace the directory placeholders with the concrete applicable paths while authoring. Proceed only on `HEALTHY` (exit 0), and enter full parent-state reconciliation on `BLOCKED` or `UNKNOWN`. For `not-applicable`, replace this with `not-applicable` plus the exact immutable or version-insensitive reason.
- Integrity gate: CONDITIONAL ONLY — EXACT CANONICAL VERIFIER COMMAND, OBSERVABLE PASS CONDITION, AND BEFORE-COMPLETION TIMING
- Escalation triggers: CONDITIONAL ONLY — MISSING/MISMATCHED PIN OR LOCK/HEADER; ADOPTION/UPGRADE/AUTHORIZED REPAIR; VERIFIER FAILURE/DRIFT; HARD DEFECT; ALREADY-KNOWN BLOCK
- Parent-state check: Resolve the affected Roblox project root. Use any exact authoritative record/learnings locations already supplied by that project; otherwise read the matching schema-version 3 resource record at `.agents/roblox/resources/records/RESOURCE-SLUG.yaml` and resource-bound learnings from `.agents/roblox/resources/learnings/` relative to that root. If this project-scoped child's project cannot be resolved, report unknown state and enter reconciliation; do not silently switch to global records. Only for an explicitly user/global-scoped child, document the no-project fallback at `~/.roblox-resources/records/RESOURCE-SLUG.yaml` and `~/.roblox-resources/learnings/`. Match by resource slug plus canonical identity.
- Mismatch/unknown action: For every state escalation trigger, stop the affected version-sensitive use, perform the Parent-state check, and invoke `roblox-resource-acquisition` in `repair/reconcile` mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff; it is the source of truth for defect evidence and parent activation.

## Client/server placement

State where modules and calls belong on both client and server, what crosses the boundary, and what authority the server must retain. If one side must not use the resource, say so explicitly. For a development tool that does not run in the engine, state that client/server placement is not applicable and describe its actual authoring/build boundary.

## Mental model

Explain the minimum concepts needed to use the resource correctly.

## Lifecycle and cleanup

- Initialization: Name the operation that activates behavior (constructors may register player hooks, persistence, tasks, or listeners even when a top-level bundle require is inert) and identify its owner. Establish that owner and its cleanup path before fallible acquisition.
- Reuse: ...
- Cleanup/destruction: State how partial acquisition rolls back, how pending waits/tasks are cancelled or invalidated, and how repeated/reentrant teardown stays idempotent. For composed libraries, record the pinned cleanup owner's actual ordering/error-continuation behavior and encode producer-before-consumer ordering explicitly when required.
- Ownership boundary: Separate feature/component-owned resources from package/process-global work. Apply the parent integration-proof host-ownership boundary before requiring global finalization.

## API used by this skill

Document only source-grounded public APIs that the agent needs frequently; distinguish source review from runtime verification. For a development tool without a callable API, say so and document its actual command/configuration instead.

## Failure modes

### Symptom

Likely cause -> diagnosis -> repair.

## Limitations

- ...

## Security notes

State the applicable resource-specific trust boundaries and mitigations. If none are special to this resource, say so explicitly. Preserve server authority; never embed secrets in source.

## Verify after installation

Executable fixture: PATH TO THE MAINTAINED REPRESENTATIVE INTEGRATION FIXTURE that is the source for examples and runs against the actual adopted resource/companion pins, or `not-applicable` with the exact non-executable claim boundary.

Run: ...

Pass condition: ...

Evidence boundary: State whether this proves static/strict analysis, construction and owned lifecycle, real runtime input/animation/startup, and/or clean diagnostics. Do not promote an unobserved lane. A clean-console claim additionally requires a red-capable warning/error guard through the complete runtime boundary the harness owns; process exit applies only to a harness-owned disposable process.

Both command and pass condition must be concrete enough for another agent to execute/check; do not use placeholders or generic outcomes such as “check it” or “it works.” Keep advice-only and inert-utility verification proportional; do not add Studio/UI/lifecycle machinery without a corresponding claim.

## Alternatives

Compare against the closest Roblox built-in or credible alternative. If the project-use target is owned by another project contract, keep alternatives informational and hand replacement/upgrade decisions back to that authority. If none is meaningful, state why.

## Provenance

- Resource slug: RESOURCE-SLUG
- Package identity: PACKAGE-ID (or explicitly state that the resource has no package identity)
- DevForum: HTTPS URL (or explicitly state that no DevForum topic is used/applicable)
- Canonical source/docs: HTTPS URL (or explicitly state that no separate canonical source exists when the DevForum topic above is the canonical source)
- Source version/release/commit: IDENTIFIER (immutable version/commit, an explicitly labeled named tag/release/build, or a dated explicit source state; not bare latest/current/main/HEAD)
- Source review date: YYYY-MM-DD
- Resource verification: VERIFIED/UNVERIFIED/UNAVAILABLE

## Version drift

Before using newer upstream versions, check release notes/source for changes affecting the APIs and behavior documented above. Re-review material changes before updating this skill's source state, and rerun runtime proof when the claimed verification status would otherwise become stale. When the target is owned by another project contract, report a newer candidate or incompatibility to that authority instead of advancing the pin independently.
