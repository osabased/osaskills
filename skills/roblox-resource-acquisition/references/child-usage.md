# Shared resource-child usage contract 1

Read once per task for an activated child. Its `resource.yaml` declares canonical identity, immutable selector, scope, check profile and conditional references. Unsupported contract versions require regeneration; ordinary use stops on unknown material identity.

## Resolve paths and authority

Resolve `PARENT` from the installed `roblox-resource-acquisition` skill, `CHILD` from this child directory and `PROJECT` from the affected project's guide/manifest/mapping. Preserve its selected target. `RECORD` is the descriptor's project-relative record, unless an explicitly supplied authoritative record overrides it. Replace these command parameters with actual paths.

An unresolved project-scoped child is `UNKNOWN`: stop version-sensitive work and enter parent `repair/reconcile`, without global fallback. Only explicitly user-scoped children may use their declared no-project evidence locations.

## Before ordinary use

1. Honor child and parent sibling `.skill-maintenance/<skill-name>.json` guards. A pending/interrupted promotion blocks dependent use until recovery/completion; controlled candidate validation is separate. Shared checkers honor these guards.
2. For this resource's first use, perform the [first-use check](first-use-check.md). It compares relevant canonical source/docs and records the observation. Reuse unchanged checks within the task; release availability does not authorize a pin change.
3. Apply the descriptor's reconciliation policy:

   - **conditional:** run the commands below; require declaration `PASS` and query `HEALTHY`. A healthy task does not load full record proof, learnings or package internals. Defer installed integrity until completion.
   - **required:** run installed integrity before version-sensitive use, using the child's concrete asset/custom inputs. Run the status query and reconcile matching records plus resource-bound learnings under [pre-use reconciliation](operational-lifecycle.md#pre-use-reconciliation). Plugin identity can drift independently of a project lock.
   - **not-applicable:** honor guards/freshness and the descriptor's concrete immutable or version-insensitive reason. Unknown identity never counts as a match.

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --declared
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "RECORD"
```

The checker matches canonical identity rather than assuming an alias and reads source bytes without executing dependency code or commands from records. For ambiguous/custom bindings, supply `--alias`, `--package-dir`, `--companion PACKAGE=DIR` or `--asset` as applicable. Project fixtures own wrapper/mapping validation.

## Stop and repair

Stop affected version-sensitive work for `BLOCKED`/`UNKNOWN`, missing/mismatched pin/lock, verifier failure/drift, an existing block, hard correctness/security/identity/version/verification defects, or an authorized repair invalidating evidence. Adoption/upgrades also enter the parent's applicable reconciliation path before use resumes.

A recurring instruction workaround activates parent `repair/reconcile` diagnosis. A harmless task-local adjustment does not. For a soft defect, preserve safe reversible progress and report the reproduction, workaround and durable correction before completion; diagnosis alone does not force unrelated lifecycle reads. Carry identity/selector, task, installed/recorded state, expected/observed behavior, reproduction, impact, correction, invalidated evidence and authority. Diagnosis grants no mutation permission beyond the current task or applicable factual-repair grant.

## Complete with the right claim

For conditional resources run installed integrity before completion:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT"
```

Require exit 0, `status: PASS`, the exact selector and `lane: installed-integrity`. Assets add `--asset` and require `lane: asset-integrity`. A custom profile names a reviewed child-owned checker; the shared checker reports unavailable instead of executing it automatically. Reuse unchanged pre-use integrity checks under required policy.

Run the project's authored-source/build checks and execution lanes the task claims. Hashes establish installed identity, static checks establish static integration, and project fixtures own runtime/input/rendering/diagnostic proof. Advice-only guidance implies no runtime harness. Trust, project role, runtime verification, child validation and host adoption remain distinct.

When updating an installed child, use [guarded maintenance](on-demand-maintenance.md#guarded-correction-and-recovery). An explicitly local-only update may finalize truthfully `installed` with unavailable host discovery/activation recorded; `operational` still requires observed applicable host gates.
