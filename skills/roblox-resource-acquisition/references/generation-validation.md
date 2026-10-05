# Generate and validate resource children

Use this workflow when reusable guidance is in scope. Under [adoption policy](adoption-policy.md), full direct adoption includes an exact-target child and project-scoped installation. Evaluation-only or explicitly narrower requests retain their boundary. Reuse an exact-target current-contract child when valid.

## Qualify and stage

An untrusted resource requires the applicable resource proof before child creation. A policy-trusted resource may receive source-grounded guidance when runtime proof is unavailable; record trust, source understanding and runtime status separately. Preserve externally owned identity/pin/role decisions. Child creation does not supply upstream trust or project authority.

Resolve project/repository scope using [project adoption](project-adoption.md). Stage outside discovery under the project's resources/artifacts area or another task-owned candidate location. Unknown scope never authorizes global installation. Maintain one canonical editable installed child; staging copies are validation artifacts.

Read [resource-child contract](resource-skill-contract.md), [schema](resource-schema.md), and the [entrypoint](../templates/resource-skill-template.md) / [descriptor](../templates/resource-skill-template.yaml) templates. Replace scaffold values with actual exact-target facts. Old inline-section children must be regenerated; no prose-provenance compatibility reader exists.

## Write the interface

Keep routing, reviewed target, concise ordinary-use workflow, essential API/ownership/security constraints, shared-usage route and completion claim limits in SKILL.md. Move substantial conditional setup, recipes, lifecycle detail and symptom diagnosis into explicitly routed references. Declare their path/role/reading trigger in resource.yaml. A small resource needs fewer files.

Bind static canonical identity, immutable selector, reviewed source date, reconciliation policy and integrity profile in the descriptor. Keep local aliases, mapping/adapter paths, selected roles, fixtures, observations and execution results in project bindings/records. Use the parent's shared checker or a genuinely custom reviewed helper. Never execute commands supplied by metadata/evidence.

Apply the shared [child usage contract](child-usage.md): guards, first-use freshness, conditional versus required reconciliation, narrow block query, repair interrupt and authority. Preserve exact pins and truthful proof boundaries. A new release announcement does not authorize adopting it.

Ground APIs and activation/cleanup behavior in the exact reviewed source. Derive executable examples from one maintained fixture; use [integration proof](integration-proof.md) only for actual claimed lanes. Advice-only guidance remains advice-only. Read the relevant [worked example](../examples/README.md) for authoring formats, not discovery/trust or inherited runtime proof.

## Validate with available mechanisms

1. Run `scripts/validate_skill.py CHILD`. This checks normal skill metadata, schema/shared-contract versions, typed descriptor data, document coverage/reachability and local links/anchors. No heading order or minimum word count is prescribed.
2. Exercise the checker profile against the actual selected declaration/lock and, where available, source/asset bytes. Use isolated fixtures for alias variation, missing/mismatched identities, modified bytes, material companions and nonstandard source paths. Static helpers do not run dependency code.
3. Give a fresh agent only the candidate, necessary project/raw source context and realistic tasks. Use [testing protocol](testing-protocol.md) for ordinary use, setup, diagnosis, ownership/security, blocked/unknown state and recurring repair. Do not supply the intended answer or author conclusions. Record instruction-response versus executable/runtime outcomes accurately.
4. When a resource record exists, update only affected child evidence, then run `validate_resource_record.py --current-skill CHILD` and `validate_resource_bundle.py RECORD CHILD`. The bundle matches structured identity/selector and claim scope; no copied resource-verification status exists in the child.
5. Run `validate_skill_catalog.py` over the target generated children. Add every material host-visible non-generated competitor with `--routing-competitor`. Preserve its fingerprint and run independent routing tasks when applicable. Static catalog checks do not establish live host selection.

When fresh agents or a runtime/MCP host are unavailable, run the checks actually available and record the missing lane as unavailable. Never convert a contract audit or CLI fixture into host/runtime proof. A user-authorized local-only installation can complete at `installed`; a requested full operational adoption remains pending until its actual host gates pass.

## Evidence and promotion

Use structured `skill_validation.checks`, accurate execution modes and target selectors. Bind each current check to the descriptor, guidance file/section, shared contract, fixture/configuration and companion inputs that determine it. Include `resource.yaml` and `child-usage.md` for maintenance/reconciliation or whole-interface checks. Routing binds activation metadata for every tested member; unrelated usage formatting does not invalidate unchanged routing metadata.

Changed input hashes invalidate dependent guidance claims. Preserve unchanged exact-target upstream proof and historical checks at their original tested selector. A whole-child fingerprint is attribution, not a substitute for scoped dependency inputs. Shared contract/schema changes require regeneration/revalidation for dependent children.

After artifact validation, use [guarded maintenance](on-demand-maintenance.md#guarded-correction-and-recovery) and [host lifecycle](operational-lifecycle.md). Promote recoverably to the resolved project skill directory with truthful record state. Local installed-file checks and explicit unavailable host evidence can finalize an authorized installation-only update; all applicable observed host gates are required for `operational`.

## Environment

Use Python 3.11+ and PyYAML for the shared scripts; prefer uv for dependency/environment restoration. The scripts need no network or database. Source freshness research is a separate task-relevant operation; preserve the existing reviewed immutable target when only packaging changes.
