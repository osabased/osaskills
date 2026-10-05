# Shared resource-child usage contract 1

Read this once per task for an activated resource child. `resource.yaml` declares parent contract version 1; unsupported versions are unknown state and require regeneration. This is the shared ordinary-use contract. Acquisition, upgrades and full reconciliation remain in the parent's routed workflows.

## Resolve the target and scope

Read the child's `resource.yaml`: canonical identity, immutable selector, installation profile, reconciliation policy and conditional reference map. Preserve the affected project's selected target. Resolve the installed parent through its available skill location, the child through its actual installed directory, and the affected project through its guide/manifest/mapping. Replace the documented `PARENT`, `CHILD`, `PROJECT` and optional source/asset path parameters with these actual paths before executing a command.

For a project-scoped child, record and learnings paths are relative to that project. An unresolved project is `UNKNOWN`: stop version-sensitive use and enter parent `repair/reconcile`; no global fallback exists. An explicitly user-scoped child alone may use its declared no-project evidence locations. An explicitly supplied authoritative project record overrides the default location.

## Before ordinary use

1. Honor the sibling promotion guards for both child and parent. The shared install checker and status query honor them. A pending/interrupted transaction stops ordinary dependent use; controlled candidate validation is separate.
2. Before this resource's first use in the task, apply the parent's [first-use freshness check](on-demand-maintenance.md#first-use-freshness-check). Resolve the actual adopted target, compare canonical releases and relevant docs, and record the scoped observation. Reuse unchanged checks within the task. New release availability does not authorize a pin change; unavailable currentness does not erase unchanged exact-target execution proof.
3. Follow the declared reconciliation policy:
   - **conditional:** run `check_resource_install.py CHILD --project PROJECT --declared`, then `check_resource_status.py --pair CHILD RECORD`. Require `PASS` for declaration/lock and `HEALTHY` for the narrow query. Keep full record proof, learnings and package internals outside this healthy path. Run installed integrity before completion.
   - **required:** run installed integrity before version-sensitive use, then reconcile installed state with the matching record and resource-bound learnings under [operational lifecycle](operational-lifecycle.md#pre-use-reconciliation). UI/plugin identity may drift independently of the project lock.
   - **not-applicable:** honor guards and freshness, then use the exact immutable/version-insensitive reason in the descriptor. Unknown material identity never counts as a match.

The shared checker identifies direct dependencies by canonical package/repository, not a fixed alias. It reads reviewed source bytes and never runs dependency code or commands stored in metadata/evidence. Supply `--alias` for an ambiguous direct binding, `--package-dir` for a nonstandard mapped source root, `--companion PACKAGE=DIR` for material companion locations, or `--asset` for an installed immutable asset. Wrapper/mapping checks belong to the project integration harness.

## Stop and repair

`BLOCKED`/`UNKNOWN`; missing/mismatched pin or lock; adoption/upgrade; an authorized repair that invalidates evidence; verifier failure/drift; an already-known block; or a hard correctness/security/identity/version/verification defect stops affected version-sensitive work and enters parent reconciliation before continuing.

A recurring instruction workaround activates parent `repair/reconcile` diagnosis even when safe immediate work can continue. A harmless one-off task-local adjustment does not. Hard defects stop dependent work. For a soft defect, preserve safe reversible progress and surface the reproduction, workaround and durable correction before completion; soft diagnosis alone does not force unrelated provenance or lifecycle reads.

Carry the exact identity/selector, affected task, installed/recorded state, expected and observed behavior, smallest reproduction, impact/block, safe workaround, proposed correction, invalidated evidence and authority. Invocation authorizes diagnosis/reporting; mutations use current task authorization or the applicable standing factual-repair grant.

## Complete with the right claim

For conditional resources, run `check_resource_install.py CHILD --project PROJECT` before completion and require exit 0, `status: PASS`, the exact selector and `lane: installed-integrity`. Assets require `--asset` and `lane: asset-integrity`. Custom profiles name a reviewed child-owned checker; the shared tool reports unavailable and never executes that filename automatically.

Run the affected project's authored-source/build checks and only the execution lanes the current task claims. Source hashes prove installed identity, static analysis proves static consumers, and project fixtures own runtime/input/rendering/diagnostic proof. Advice-only guidance has no implicit runtime harness. Resource trust, project role, runtime verification, child validation and host adoption remain distinct.

Guarded updates may finalize at truthful `installed` status when the user explicitly limits work to locally available checks. Record unavailable host discovery/activation; full `operational` status still requires its applicable host gates. See [guarded maintenance](on-demand-maintenance.md#guarded-correction-and-recovery).
