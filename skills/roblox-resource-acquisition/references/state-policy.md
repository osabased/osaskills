# Resource state and lifecycle policy

Apply this reference whenever the workflow records project use, trust or verification, writes portable records or learnings, records a child install, or reports a final acquisition result.

Before creating or updating persistent lifecycle state, use the project/environment's authoritative registry or storage location when one exists; otherwise use the portable fallback defined here. Do not duplicate resource identity, version, project-use, adoption, or validation state across competing locations.

## Portable resource-record location

When the environment has no authoritative resource-record format or storage location, resolve portable schema-version 3 resource records in this order:

1. an explicit record path supplied by the user, project, or environment;
2. `<project-root>/AGENT_DIR/roblox/resources/records/<slug>.yaml` when a project root is in scope;
3. `~/.claude/roblox/resources/records/<slug>.yaml` otherwise (the same rule applied to the home directory, so `~/.agents/roblox/resources/` when only that exists).

`AGENT_DIR` is the project's `.claude/` if it exists; otherwise `.agents/` if it exists; otherwise create `.claude/`. If both exist, use the one that already contains `roblox/`; if neither or both do, use `.claude/`. All project resource data lives under `AGENT_DIR/roblox/resources/`: `records/`, `learnings/`, `curated/`, `artifacts/` and `maintenance/`. A child's `resource.yaml` names its record relative to `AGENT_DIR` (`roblox/resources/records/<slug>.yaml`), and `check_resource_status.py --child CHILD --project PROJECT` resolves it by this rule. If a legacy `~/.roblox-resources/` exists, read it and suggest moving it to `~/.claude/roblox/resources/`.

Use the first applicable location in that order for a new portable record, and use the same precedence when resolving an existing portable record. This location rule does not itself authorize creating or updating persistent state; it only selects the destination when the surrounding task or environment already authorizes that lifecycle write.

For separately maintained global version variants without a project root, select an explicit selector-qualified record path, such as `~/.claude/roblox/resources/records/<slug>--<selector>.yaml`, and write that exact discovery route into the variant child. Keep the resource slug/canonical identity unchanged and bind each record to its actual target and generated child. Do not overwrite an existing target's singleton fallback record to register a different variant. With a project root, that project's authoritative record still wins.

## Record project use separately

Every current portable record contains `project_use` with `status`, `role`, `scope`, and `authority`.

- **`adopted`** — the resource is a durable project-standard choice for the recorded role and scope. `role`, `scope`, and `authority` must all be concrete.
- **`retired`** — the resource was a durable project-standard choice but is no longer active. Preserve its former role/scope/authority so the transition remains auditable.
- **`not-applicable`** — the record is not an active or former project-standard choice. Leave role/scope/authority empty.

An adopted project use requires a trusted canonical resource identity, but trust does not itself imply adoption. Before finalizing a new adoption, satisfy [adoption-policy.md](adoption-policy.md#required-proof-and-completion), including the child gates when a child was requested. Keep incomplete new work as candidate evidence or staged integration with `project_use.status: not-applicable`, not a fictitious `pending` schema value. This does not erase an existing adopted choice when its proof or child later becomes blocked. Installation, transitive presence, successful verification, or a generated child likewise do not imply adoption.

`project_use.authority` identifies the durable project contract that owns the choice. `roblox-resource-acquisition` may change identity/pin/replacement state autonomously only when it owns that decision within the authorized task. When another authority owns it — for example `structure-roblox-projects` for Canonical SSA's ModuleLoader — preserve the supplied target and return contradictions/blocks to that authority instead of silently substituting or upgrading it. Use [project-adoption.md](project-adoption.md) for the CLAUDE.md resource list and project-local child placement.

Keep project-use state independent from verification and generated-child state. A child failure does not retire an adopted upstream resource. A resource verification/reconciliation block does not silently change the project choice; it blocks the affected use until repaired or the owning authority changes the decision.

## Record trust and verification separately

Do not overload one status word with two meanings. Track **trust** (who/what authorizes normal use) separately from **verification** (what has actually been proven).

### Trust

For resources this workflow actively acquires, trust normally comes from:

- **curated** — valid explicit user/project catalog membership. Trust is immediate for the canonical identity named by the entry and does not require this workflow to re-prove the library;
- **verified-acquisition** — a previously untrusted candidate completed all applicable upstream resource-proof gates required to establish verified resource acquisition. Generated-child validation is separate and is required only when a child exists/is in scope.

An explicitly project-approved dependency may arrive with inherited `project` trust. A user direction that authorizes use/adoption of the established canonical identity may supply `explicit-user` trust. Preserve the declared basis rather than pretending this workflow established it. Installation alone, transitive presence, evaluation/comparison targeting, or a child-generation request alone supplies no trust; without another valid basis the resource remains untrusted candidate/cache research.

### Verification

Resource verification describes proof of the selected upstream resource identity/version only. Executed `resource_proof` must record the exact `target_version_or_commit` it exercised, and `verified` is valid only when that target exactly matches `verification.version_or_commit`. A refresh to a materially different selector/version/source state invalidates proof tied to the old target; never relabel old execution evidence as proof of the new state. Track generated-skill structural and behavioral validation separately under `skill_validation`; neither layer upgrades the other automatically.

Record resource verification as one of:

- **verified** — all applicable resource/runtime proof required for the intended use actually executed and passed;
- **unverified** — verification has not yet been established; checks may be unattempted or incomplete, but no decisive failure or known execution blocker has been recorded;
- **unavailable** — a material required execution check cannot be performed in the available environment;
- **failed** — relevant executable proof failed or current evidence directly contradicts the intended use.

Thus a resource can legitimately be **trusted + unverified** through a policy trust basis. Never rewrite that as `verified`. An untrusted resource remains **untrusted + unverified** while proof is incomplete, with partial evidence recorded in `resource_proof`, until it completes enough gates for verified-acquisition trust.

### Candidate/cache

Keep non-trusted candidate research here when it may be useful later but has not earned verified-acquisition trust. Do not let candidate state masquerade as trusted guidance.

### Rejected / blocked

For untrusted candidates, record enough information to avoid wasteful repeat investigation:

- resource and source URL;
- validation date;
- rejected version/state;
- concise reason;
- evidence that would justify reconsideration.

For trusted resources, every `failed` verification state must preserve the exact affected version/use in `blocked_use_or_version` without silently changing identity, project-use authority, or policy trust. This applies regardless of whether trust came from curated, project, explicit-user, or another policy basis. For curated resources specifically, leave catalog membership and canonical identity unchanged until explicitly modified.

Use the mandatory schema-version 3 `../templates/resource-record.yaml` for a portable evidence record when the environment has no registry format of its own. The record model separates selection provenance, project use, and trust: use `discovery_origin: other` for a direct user target and state its exact role/scope in `selection_reason`; use `project` only for a capability found through project reconnaissance. Neither value determines `trust.basis` or `project_use.authority`. Carry the established `slug`, `canonical_url`, `package_id`, and material selector/version into the record so evidence cannot drift onto a same-named or differently selected resource. Record installed/parent reconciliation separately from upstream verification, and record artifact state separately from each host adoption. An empty `host_adoptions` list means artifact only; host adoption entries and completed/unavailable/failed catalog-routing evidence are invalid unless `generated_skill` identifies the child they describe. `operational` requires an observed skill listing plus a successful explicit `/<name>` invocation.

Every trusted portable record must bind trust to a stable `slug` plus at least one concrete canonical identity coordinate (`canonical_url` or `package_id`); stricter bases may require more. A record whose trust basis is `verified-acquisition` requires `verification.status: verified`, which in turn requires executed/passing applicable upstream resource proof, a dated immutable/named source state, no material unavailable claims, and a proof target that exactly matches the verified source state. It does **not** require a generated child. Generated-child structural/behavioral state remains under `skill_validation` and may fail independently without revoking otherwise-valid resource trust or project use. A record whose trust basis is `curated` likewise does not require child gates to be trusted, but every verification field must still be truthful. When refreshing a verified-acquisition record to a materially different selector/version, do not transfer the prior trust/proof claim onto that new target: keep the old record state until the new target completes the acquisition gates, or represent the new target as candidate state until it does. For an externally owned adopted target, do not create a replacement candidate as a substitute unless that authority or the user explicitly opens replacement/upgrade selection.

Whenever this workflow writes or updates a portable resource record, run `scripts/validate_resource_record.py <resource-record.yaml>` when Python is available. Its PASS establishes only structural/state consistency; it does not prove the recorded evidence is true. When a portable record and generated child are both finalized together, also run `scripts/validate_resource_bundle.py <resource-record.yaml> <generated-skill-directory>` to prove their recorded identities/source state agree. Record reconciliation and install evidence per [installing children](operational-lifecycle.md).

Schema-version 3 records may contain legacy aggregate skill-validation booleans and prose. Preserve them as historical claims, but never promote them to current integration proof. New current claims set `claim_scope` and use structured `skill_validation.checks` with honest check kind/execution mode, exact tested target, scoped input hashes, command/result/artifact when applicable, and a routing check bound to the current catalog fingerprint plus recomputed activation-metadata fingerprints for every declared member of the tested set. `advice-only` requires independent instruction-response evidence without inventing a runtime gate. `executable-integration` also requires current executable integration plus proportionate lifecycle-failure/cleanup evidence backed by a maintained fixture: exercise applicable failure and teardown behavior, or prove the explicit absence of owned lifecycle work for an inert utility rather than inventing cancellation behavior. `validate_resource_record.py --current-skill <child>` and bundle finalization verify current inputs without executing any recorded command. Removed or superseded fixtures make the claim stale until its entry is marked `historical` or fresh evidence is recorded. Historical entries retain their original tested target after an upgrade. No migration fabricates evidence or rewrites external records.

## Self-growth boundaries

Activating repair is permission to diagnose and report a defect, not to edit. A safe workaround does not erase the defect, and finishing the immediate task does not remove the duty to report its reproduction, workaround and proposed fix. Hard defects stop dependent work; soft defects may let immediate work continue.

Durable learning has two destinations with different rules.

**External learnings store** — user- or project-owned observations outside this package, governed by [learnings-store.md](learnings-store.md). Appending a new entry is autonomous. Editing, retargeting or deleting an existing entry needs explicit user permission in chat every time. Never bundle accumulated entries into this package or a child.

**This skill package and its children** (`SKILL.md`, `references/`, `scripts/`, `templates/`, and the roblox-* children) — edit only when the current task authorizes it or the user's own instructions grant standing permission for that kind of fix (see [on-demand maintenance](on-demand-maintenance.md#authority)). When authorized, carry that authorization through reversible edits within its scope without asking per diff. Otherwise state the evidence, propose the exact diff (file, current text, replacement) and wait. A change that goes beyond the authorized scope needs new authorization.

## Scope expansion proposals

Propose, never implement unprompted, expansions of this skill's own scope: new operating modes, new resource classes, or changes to a description or other activation surface. State what would newly activate, what could regress and what new failure modes it adds. Nothing is written until the user says yes, and each yes covers only the proposal it answered.

## Source hygiene

Community Resources is discovery evidence, not authority over Roblox engine behavior. For Roblox APIs, security behavior, package behavior, and platform constraints, verify against current Roblox Creator Hub documentation when material.

When a DevForum resource links to a canonical repository/docs site, use that source to understand the resource rather than relying on third-party summaries.

Re-check volatile facts such as current versions, maintenance status, APIs, and deprecation before generating or refreshing a skill.

## Security defaults

For unfamiliar packages/models/modules:

- inspect scripts before allowing them into a real project;
- avoid opaque or dynamically fetched executable code without strong justification and inspection;
- never place secrets/API keys directly in source;
- preserve server authority and validate client-controlled inputs;
- treat auto-updating third-party packages as a supply-chain decision, not a convenience default;
- prefer isolated testing and reversible changes before project integration.

Do not publish, spend money, expose credentials, or perform irreversible project mutations merely to validate a resource.

## Output discipline

Keep research proportional to the task. The final acquisition result should make the decision auditable without dumping the entire research process.

For a no-acquisition outcome, report the local choice and applicable validation without opening a resource lifecycle. For evaluation-only, report criteria, hard-gate findings, the decision, material evidence/uncertainty and the evaluation-only boundary. Omit unused child and host statuses; still surface relevant supplied trust/verification state, owner conflicts, learnings and current blocks. The fuller fields below apply when their lifecycle stages are in scope.

Report only applicable fields:

- selected canonical resource identity plus material selector/version and why it fits; compare alternatives only when comparison was required or explicitly requested;
- trust basis for that exact identity/selector;
- project-use role/authority and whether the CLAUDE.md resource list changed, when applicable;
- resource/runtime verification performed and result, or explicitly `unverified`/`unavailable`, naming the same exact identity/selector;
- when a child was requested: its name, location and scope (project by default, user-wide only on request); otherwise say a child was offered or not applicable;
- skill validation performed and result, or `not applicable` when no child was in scope;
- reconciliation status and any blocked use/version;
- child install state (`artifact`, `installed` or `operational`) with the evidence for `operational`, when a child was in scope;
- catalog fingerprint, static result, and independent routing result when applicable;
- important limitations/version pin;
- learning entries appended to the external store during the run, when any;
- rejected alternatives only when their rejection materially explains the decision.

Do not bundle user/project curated registry data, resource records, research transcripts, caches, temporary test fixtures, accumulated learnings, or unrelated artifacts into a generated runtime skill package. Keep only the instructions, references, templates, and helper scripts the skill actually needs.

If no permitted existing or targeted resource resolves the need and no curated/discovered candidate clears the required acquisition gates, say so and implement locally or return the unresolved need instead of manufacturing a recommendation. For externally owned project targets, report the unresolved/blocking evidence to the owning authority rather than manufacturing an alternative.
