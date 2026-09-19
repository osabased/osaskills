# Generated Resource Skill Contract

A generated resource skill is ready for validation only if it contains all of the following information.

## Required identity

- stable skill name/slug;
- resource name;
- stable resource slug used by matching external records/learnings;
- canonical resource identity (`canonical_url`, plus `package_id` when applicable);
- one-sentence capability description;
- reviewed source version, release, commit, or explicit dated source state; named non-numeric tags/releases should be labeled explicitly (for example `tag: Spring-2026`); floating labels such as `latest`, `current`, `main`, or `HEAD` are not pins unless paired with an immutable identifier or dated source state;
- explicit resource verification status: `verified`, `unverified`, or `unavailable`; source review/provenance alone must never be presented as runtime verification;
- exact DevForum topic provenance over HTTPS when applicable; if no DevForum topic is used/applicable, state that explicitly rather than inventing one; include a distinct canonical source/docs HTTPS URL when one exists, and if the DevForum thread is itself the only canonical source, say so explicitly instead of duplicating the same URL; at least one concrete HTTPS source URL must remain recoverable;

## Required decision and behavioral purpose

A generated skill is not complete merely because it documents the resource. It must make clear:

- when it should activate/use the resource;
- when not to use it;
- what failure mode or recurring integration problem the guidance prevents;
- what the agent should do differently because this skill exists;
- how that changed behavior can be validated;
- project assumptions/prerequisites;
- an explicit alternatives section naming the closest meaningful alternative or Roblox built-in when relevant; if none is meaningful, state that explicitly with a short reason.

Treat the frontmatter `description` as the child's pre-load routing contract. State the positive trigger there and include any material exclusion whose absence could cause incorrect implicit activation before the body is loaded. Do not copy every `Do not use when` bullet into frontmatter; carry only the boundaries needed to distinguish this skill from simpler tasks, built-ins, adjacent resources, or competing skills.

For an externally owned project dependency, alternatives are informational only: the child must preserve the supplied identity/pin and hand replacement/upgrade decisions back to the owning project authority.

## Required operating knowledge

- installation/placement;
- minimal mental model;
- only the public API surface necessary for common tasks, or an explicit statement that the resource exposes no callable API;
- source-grounded activation ownership and cleanup lifecycle, including constructor/start side effects even when a bundle require is inert, cancellation/invalidation for pending waits or spawned work, ownership established before fallible acquisition, partial-acquisition cleanup, and idempotent teardown;
- for composed libraries, the exact pinned cleanup owner's real ordering/error-continuation behavior and an explicit producer-before-consumer plan when required; never assume separate cleanup entries provide ordering or best-effort continuation;
- a boundary between component/feature-owned resources and package/process-global work, following [Respect host ownership](integration-proof.md#respect-host-ownership) before assigning any global finalizer;
- client/server placement and authority, explicitly covering both sides even when the resource is intentionally one-sided;
- concise working examples derived from source-grounded APIs, with runtime-verification claims only when the resource verification status supports them;
- known limitations;
- common failure modes and diagnosis.

## Required safety guidance

Include a **Security notes** section in every generated skill. When no resource-specific trust boundary exists, state that explicitly and preserve normal Roblox server-authoritative expectations. When applicable, cover:

- remote/client input validation expectations;
- secrets/external HTTP handling;
- dynamic `require`/asset-loading implications;
- auto-update/version drift implications;
- data persistence/destructive behavior.

## Required verification

Provide a small verification recipe an agent can run after installation. It must name the maintained executable fixture that supplies its integration examples and proof, or state a concrete non-executable claim boundary. Executable Luau examples must be strict-analyzed on the canonical project path with the actual adopted resource and material companion libraries. The recipe must include a concrete runnable/checkable step and a specific observable pass condition; placeholders or generic statements such as “check it” / “it works” do not satisfy this contract.

Follow [integration-proof.md](integration-proof.md) for executable integration, composed lifecycle owners, runtime behavior, and diagnostic claims. State which proof lane each command covers. Static analysis, construction, or green CLI assertions do not establish real input, rendered layout, animation, startup, or a clean console. Require Studio/runtime evidence only for claims that need it; advice-only skills and inert utilities retain a fast non-executable or static path.

## Required operational reconciliation

Before the common path, include a **Repair interrupt** section with four explicit behaviors:

- `Trigger`: activate `roblox-resource-acquisition` in `repair/reconcile` mode when reusable guidance requires guessing, bypassing instructions, repeated rediscovery, or a likely-recurring undocumented workaround; distinguish harmless task-local adjustments;
- `Hard defect`: stop dependent work when correctness, security, identity, version, or verification is unreliable;
- `Soft defect`: allow safe reversible immediate work to continue, but require parent repair diagnosis and surface the reproduction, workaround, and durable correction before completion;
- `Handoff`: capture task, installed state, expected/observed behavior, smallest reproduction, workaround, and proposed durable correction, while stating that parent activation authorizes diagnosis/reporting rather than otherwise unauthorized edits.

Place **Repair interrupt** before **Common path**. This is a separate early activation contract, not another name for state reconciliation.

Include an **Operational reconciliation** section containing these labeled fields:

- `Policy`: exactly `required`, `conditional`, or `not-applicable` followed by a concrete reason;
- `Installed-state check`: a resource-specific command, file/manifest inspection, package/asset identity check, or an explicit immutable-install explanation;
- `Expected identity/state`: the canonical identity and reviewed version/commit/source state the guidance targets;
- `Current-block check`: under `required` or `conditional`, run the parent package's read-only `scripts/check_resource_status.py --pair <child> <record>` before affected use, proceed only on `HEALTHY`, and route `BLOCKED`/`UNKNOWN` to full reconciliation; under `not-applicable`, state `not-applicable` and repeat the concrete immutable or version-insensitive reason;
- `Parent-state check`: a deterministic discovery route for matching schema-version 3 resource records and resource-bound learnings, plus the resource slug/canonical-identity match. For a project-local child, name the project-root-relative canonical record/learnings locations or the exact authoritative locations that apply. For a portable/user child, state the project/user fallback resolution rule. An identity-only instruction such as “load matching records and learnings” is insufficient;
- `Mismatch/unknown action`: stop the affected version-sensitive use and invoke `roblox-resource-acquisition` in `repair/reconcile` mode;
- `Defect handoff`: point to the earlier **Repair interrupt** handoff as the source of truth rather than duplicating a weaker evidence list.

Conditional policies additionally require:

- `Integrity gate`: the concrete canonical verifier command, its observable pass condition, and the requirement to run it before task completion. The gate may be deferred until completion and does not block initial ordinary use;
- `Escalation triggers`: the exact conditions that replace the fast path with full parent-state reconciliation. At minimum cover a missing or mismatched installed pin/state, adoption or upgrade, an authorized repair that invalidates evidence, verifier failure or drift, a hard defect, and an already-known block.

Use `required` when every version-sensitive use must consult installed and parent lifecycle state before proceeding. Use `conditional` when a cheap declared-pin plus lock/header check can establish the expected ordinary-use state and a canonical verifier will check installed integrity before completion. Use `not-applicable` only when the install is fixed to the exact immutable reviewed state or the documented behavior is demonstrably insensitive to independent drift. Unknown material state never counts as a match.

Put **Repair interrupt** before **Common path**, and **Common path** before the conditional reconciliation branch, so healthy ordinary use is immediately actionable while reusable defects self-activate repair. Under `conditional`, the ordinary path reads the declared pin and lock/header counterpart, then performs only the narrow query over child provenance labels and matching record identity, version, block, reconciliation, verification, and matching-host status. It does not load package internals, full record proof/skill-validation evidence, or learnings. The integrity gate still runs before completion. If the block query is `BLOCKED`/`UNKNOWN` or another state escalation trigger applies, stop version-sensitive work and execute the full installed-state, parent-state, and mismatch contract before continuing. A soft instruction defect activates repair diagnosis without automatically forcing unrelated parent-state or provenance work.

The child does not bundle the external resource record, project-use state, or learnings store. A conditional child queries only child provenance labels and matching record identity/version/block plus reconciliation, verification, and matching-host status on the healthy path, and loads full record proof/skill-validation evidence plus learnings only after escalation. `HEALTHY` requires a known usable reconciliation state and no adverse verification or matching-host state. A `required` child consults the full lifecycle inputs before version-sensitive direct use. Any nonempty `blocked_use_or_version` on the exact matching record stops the affected use; free text never supplies evidence that the block does not apply. Adverse learnings remain observations to re-check rather than executable policy.

## Prohibited behavior

The skill must not:

- invent undocumented APIs;
- present old examples as current without a version warning;
- reproduce large portions of upstream documentation unnecessarily;
- hide transitive dependencies;
- call a resource "safe" merely because it is popular/open source;
- make auto-update the default for third-party packages without considering supply-chain risk;
- require human confirmation for routine reversible engineering steps unless the surrounding environment requires it;
- silently publish places, expose credentials, spend money, or mutate production data;
- call a validated artifact operational merely because it exists in a filesystem location;
- continue version-sensitive guidance through an unresolved identity/version mismatch or matching current block;
- replace, retarget, or upgrade an externally owned project dependency merely because an alternative appears preferable.

## Context economy

The skill should make the common path obvious in the first screenful or two, with deeper edge cases below or in references. A generated skill that forces an agent to reread an upstream manual for basic use has failed its purpose.
