# Generated resource-skill workflow

Use this reference only when reusable child guidance is in scope, or when an existing generated child must be refreshed and revalidated.

## Generate the resource skill when adoption/reuse is in scope

If the user asked only to evaluate, compare, or inspect a resource and the current task does not require adopting it as reusable agent guidance, stop after the requested evaluation/verification result instead of creating a skill as extra scope.

When reusable child generation is in scope, an untrusted resource — whether discovered, already project-present, or directly targeted — may receive a dedicated reusable skill only after the required resource verification passes. A resource trusted through `curated`, `project`, or `explicit-user` may receive one after current-source understanding is sufficient even when runtime verification is unavailable, because its trust came from policy rather than this workflow. In either case, use [resource-skill-template.md](../templates/resource-skill-template.md) and [resource-skill-contract.md](resource-skill-contract.md).

Use this same generation path for an adequate existing dependency or an explicitly targeted resource; do not create a parallel child mechanism. Generate only when reusable guidance is in scope and justified. Child creation or validation does not imply that this workflow installed the upstream resource, grant upstream trust, upgrade upstream verification, change project-use authority, or make either the resource or child operational. Host adoption remains a separate authorized gate.

When a project root is in scope, stage a generated child that is not yet host-adopted under `<project-root>/.agents/roblox/resources/artifacts/skills/<skill-name>/`. Read [project-adoption.md](project-adoption.md) before project-local child placement or host adoption. Do not place a child directly into `.agents/skills` merely to organize it: that path is a host discovery surface and therefore an installation event.

The generated skill must be operational guidance, not a copy of the DevForum post or README. It should teach an agent how to decide, install, use, verify, and troubleshoot the resource with minimal irrelevant context. Include the closest credible alternative or Roblox built-in when relevant; if none is meaningful, say why. Always retain a `Security notes` section: document applicable resource-specific trust boundaries, or explicitly state when there are no special ones beyond normal Roblox server-authoritative expectations.

Ground lifecycle guidance in the reviewed implementation, not in the shape of its public entrypoint. Identify the operation that actually activates behavior and who owns it. A top-level bundle `require` may be inert while a constructor registers player hooks, persistence, listeners, or tasks. When activation spawns waits or background work, document its cancellation/invalidation condition and teardown path. Treat missing ownership or uncancellable pending work as an integration defect, not as an example-writing detail. When the resource is composed with a cleanup owner or another lifecycle library, or the child will claim executable/runtime behavior, read [integration-proof.md](integration-proof.md) and apply only its relevant proof lanes.

For any claim of executable integration validation, keep a representative executable fixture as the maintained source for examples and proof. Put project-authored Luau on the canonical strict-analysis path and execute it against the actual adopted resource and companion-library pins. The fixture must exercise the actual activation path, relevant failure/cleanup behavior, and the project conventions the guidance claims to integrate with. Point examples to that fixture or derive only minimal excerpts from it; do not maintain a second divergent example implementation. Advice- or routing-only guidance may state an explicit non-executable claim boundary instead of inventing a runtime gate.

Every generated child must include the repair-interrupt and operational reconciliation contracts from [resource-skill-contract.md](resource-skill-contract.md): an early trigger for reusable guidance defects, hard/soft classification, parent activation and evidence handoff, stable resource identity, a `required`, `conditional`, or justified `not-applicable` reconciliation policy, a resource-specific installed-state check, and deterministic parent-state discovery. A conditional child must also name its concrete integrity gate and complete state-escalation trigger set. Use [operational-lifecycle.md](operational-lifecycle.md) for the shared lifecycle semantics; do not copy its host-independent rules into multiple references.

Place **Repair interrupt** before **Common path**, and **Common path** before **Operational reconciliation**. The early section must make a recurring workaround activate parent diagnosis even when safe immediate work continues; silently absorbing reusable friction is invalid. For a conditional child, write the cheap declared-pin plus lock/header check as the ordinary path and keep package inspection, provenance review, resource records, and learnings behind state escalation. Records and learnings are lifecycle evidence, not normal setup inputs. `required` retains full pre-use reconciliation; `not-applicable` retains its immutable/version-insensitive meaning.

Resolve the child's `Parent-state check` while generating it. When the project/environment supplies explicit authoritative record or learnings locations, write the concrete applicable route into the child. Otherwise write the project-root-relative `.agents/roblox/resources/` locations, plus the user-global fallback for cases with no project root. An identity-only instruction that says to load matching records/learnings without a location or discovery rule is incomplete.

Every `required` or `conditional` child also names the read-only `scripts/check_resource_status.py --pair <child> <record>` query before affected use; a `not-applicable` child states its exact immutable or version-insensitive reason in that field. `HEALTHY` permits the ordinary path. `BLOCKED` or `UNKNOWN` enters full reconciliation. The query reads child provenance labels and only the matching record's identity, version, block, reconciliation, verification, and matching-host status fields; it never executes commands stored in evidence. For a conditional child, write `Integrity gate` as an exact command plus observable pass condition and completion timing. Write `Escalation triggers` explicitly enough to cover missing/mismatched installed state, adoption/upgrade, authorized repair, verifier failure or drift, hard defects, and already-known blocks. Each state trigger must lead to the deterministic parent-state route. Keep soft instruction defects on the earlier repair-interrupt path unless diagnosis finds state or correctness risk.

Pin claims to the exact source version/release/commit reviewed when possible. If no stable identifier exists, record the exact review date and source state instead of pretending it is version-pinned. In the generated skill, record resource verification separately as `verified`, `unverified`, or `unavailable`; source review is not runtime proof.

For an externally owned project dependency, generated guidance documents the exact target supplied by its authority. It does not gain authority to recommend a replacement or newer pin. If source review or verification contradicts that target, hand the block back through [project-adoption.md](project-adoption.md) instead of silently retargeting the child.

Do not treat trust in the upstream resource as proof that the generated instructions are correct. A generated skill must carry its own validation/verification state and must not claim behavioral validation merely because its resource was curated.

## Validate the generated skill independently

Treat the generated skill as a second product with its own failure modes. Use [testing-protocol.md](testing-protocol.md).

When the harness supports isolated/fresh subagents, give a fresh agent only:

- the generated skill;
- the minimum project context required by the test;
- a task that requires the resource.

Do not expose the research transcript or hidden assumptions used to create the skill.

At minimum validate:

- positive activation: it recognizes an appropriate use;
- negative activation: it stays out of an unrelated or simpler task;
- clean setup from the documented prerequisites;
- correct happy-path implementation;
- a realistic integration task;
- a meaningful edge/failure case;
- troubleshooting without invented APIs;
- version/provenance visibility and truthful resource-verification status;
- security guidance when applicable.

If no fresh-agent mechanism exists, run the same protocol as an explicit contract audit and mark behavioral execution as unavailable rather than pretending independence. The audit can find instruction defects, but it does **not** establish independent behavioral verification of the generated skill.

Run `scripts/validate_skill.py <generated-skill-directory>` as a structural gate when Python is available. Treat its PASS as structural evidence only, never as proof that the prose, upstream claims, or runtime behavior are correct.

When the child is associated with a portable resource record, update the record's `generated_skill` and current structural result, then run `scripts/validate_resource_bundle.py <resource-record.yaml> <generated-skill-directory>`. This coupled gate verifies that the independently valid artifacts actually describe the same resource slug, canonical/package identity, reviewed source state, and resource-verification status. It is **not** run for ordinary resource acquisition when no child exists. Rerun this gate whenever a refresh or repair changes child provenance, resource identity, reviewed source state, or the record's generated-skill linkage.

Record new behavioral claims as structured `skill_validation.checks` and set `claim_scope` to `advice-only` or `executable-integration` only for the scope actually proven. Bind each check to its actual execution mode, target version/state, result, and only the fixture/API/configuration/contract/dependency inputs that determine it. Keep static/construction, owned lifecycle, runtime-host, and clean-diagnostics results separate; one green command cannot promote an unobserved lane. Executable integration and lifecycle-failure/cleanup passes require a maintained fixture plus the command and result that ran it. During authorized integration, install the applicable assertions in the owning analyzer/test/Studio harness rather than leaving them as review advice; unavailable execution narrows the claim. Routing uses the catalog fingerprint plus one `activation-metadata` input for every child or competitor in the tested routing set, including the current child. The validator recomputes each input and the declared set fingerprint from name, description, routing boundaries, and source state so declared activation drift cannot pass against stale recorded values. It cannot discover an omitted host-visible competitor; inspecting the host surface and declaring the complete tested set remains part of the routing test. Instruction-response evidence stays labeled as such and cannot stand in for executable integration. The optional whole-child hash is historical attribution only. Run the record validator with `--current-skill` or the bundle validator before finalization so missing, changed, or deleted current inputs make the claim stale. Mark superseded/removed-fixture entries `historical`; preserve their tested target even after a version upgrade without presenting them as current.

Whenever a child is added, refreshed, repaired, or adopted, run `scripts/validate_skill_catalog.py <generated-skill-directory-or-root> [...]` against the target generated-child set. Also inspect host-visible skill activation metadata; pass every plausible non-generated routing competitor as `--routing-competitor <path>`. Competitors contribute routing metadata/fingerprint state but are not forced through the generated resource-skill contract. Duplicate generated identities/descriptions fail. Reported activation-overlap clusters require the catalog behavioral tests in [testing-protocol.md](testing-protocol.md); static PASS never proves host routing.

After artifact validation, host adoption follows [operational-lifecycle.md](operational-lifecycle.md). For a project-local Codex adoption, transition the validated artifact into the resolved `<skill-scope-root>/.agents/skills/<skill-name>/` location without leaving a second independently editable canonical child. File placement records `installed`; only host evidence and explicit activation can establish `operational`.

### Script dependencies

All scripts in `scripts/` require Python 3.10+ and PyYAML (`pip install -r requirements.txt`); everything else is standard library. PyYAML is required rather than optional so that every environment parses registry, learnings, and record files identically — a validation verdict, and therefore a trust decision, must never depend on which parser happened to be installed. When PyYAML is missing the scripts exit with code 2 and an install hint (exit 1 remains validation failure, 0 pass). No other packages, databases, or network access are needed.
