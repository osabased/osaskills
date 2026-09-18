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

1. ...

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode when using this guidance requires guessing, bypassing an instruction, repeating a previously discovered workaround, or making an undocumented adjustment likely to recur. A harmless task-local adjustment with no reusable guidance defect is not an interrupt.
- Hard defect: If correctness, security, canonical identity, selected version, or verification is unreliable, stop dependent work and enter the parent reconciliation and repair path before continuing.
- Soft defect: If the workaround is safe and reversible, the immediate task may continue, but invoke the parent repair diagnosis and surface the reproduction, workaround, and durable guidance correction before completion.
- Handoff: Capture the task, installed state, expected behavior, observed behavior, smallest reproduction, workaround, and proposed durable correction. Parent invocation authorizes diagnosis and reporting, not package edits outside current task authorization.

## Common path

Provide the shortest source-grounded setup/use sequence. Do not call it runtime-verified unless the recorded resource verification status is `verified`.

```luau
-- Minimal example grounded in the reviewed source/API.
```

## Operational reconciliation

- Policy: REQUIRED/CONDITIONAL/NOT-APPLICABLE — REASON
- Installed-state check: RESOURCE-SPECIFIC CHECK OR IMMUTABLE-INSTALL EXPLANATION
- Expected identity/state: RESOURCE SLUG + CANONICAL URL + PACKAGE ID WHEN APPLICABLE + REVIEWED VERSION/COMMIT/STATE
- Integrity gate: CONDITIONAL ONLY — EXACT CANONICAL VERIFIER COMMAND, OBSERVABLE PASS CONDITION, AND BEFORE-COMPLETION TIMING
- Escalation triggers: CONDITIONAL ONLY — MISSING/MISMATCHED PIN OR LOCK/HEADER; ADOPTION/UPGRADE/AUTHORIZED REPAIR; VERIFIER FAILURE/DRIFT; HARD DEFECT; ALREADY-KNOWN BLOCK
- Parent-state check: Resolve the affected Roblox project root. Use any exact authoritative record/learnings locations already supplied by that project; otherwise read the matching schema-version 3 resource record at `.agents/roblox/resources/records/RESOURCE-SLUG.yaml` and resource-bound learnings from `.agents/roblox/resources/learnings/` relative to that root. When no project root applies, use `~/.roblox-resources/records/RESOURCE-SLUG.yaml` and `~/.roblox-resources/learnings/`. Match by resource slug plus canonical identity.
- Mismatch/unknown action: For every state escalation trigger, stop the affected version-sensitive use, perform the Parent-state check, and invoke `roblox-resource-acquisition` in `repair/reconcile` mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff; it is the source of truth for defect evidence and parent activation.

## Client/server placement

State where modules and calls belong on both client and server, what crosses the boundary, and what authority the server must retain. If one side must not use the resource, say so explicitly.

## Mental model

Explain the minimum concepts needed to use the resource correctly.

## Lifecycle and cleanup

- Initialization: ...
- Reuse: ...
- Cleanup/destruction: ...

## API used by this skill

Document only source-grounded public APIs that the agent needs frequently; distinguish source review from runtime verification.

## Failure modes

### Symptom

Likely cause -> diagnosis -> repair.

## Limitations

- ...

## Security notes

State the applicable resource-specific trust boundaries and mitigations. If none are special to this resource, say so explicitly. Preserve server authority; never embed secrets in source.

## Verify after installation

Run: ...

Pass condition: ...

Both lines must be concrete enough for another agent to execute/check; do not use placeholders or generic outcomes such as “check it” or “it works.”

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
