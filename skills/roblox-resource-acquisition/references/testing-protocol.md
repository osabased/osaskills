# Generated Skill Testing Protocol

Validate the generated skill as an interface for another agent, not as prose.

For executable integration, composed cleanup ownership, or runtime/diagnostic claims, first read [integration-proof.md](integration-proof.md). Enumerate the child claims and run only the applicable proof lanes. Advice-only guidance and inert utilities do not acquire Studio, UI, or lifecycle gates merely because this protocol supports them.

## Test A - Appropriate activation

Give a task whose requirements closely match the resource. Pass if the skill is selected for a justified reason and the agent does not over-expand scope.

## Test B - Negative activation

Give an unrelated task or a task better solved by Roblox built-ins/a tiny local implementation. Pass if the skill does not force the resource into the solution.

## Test C - Clean setup

Start from documented prerequisites only. Pass if an agent can install/place/require the resource without relying on hidden research context.

## Test D - Minimal happy path

Implement the smallest useful behavior from the maintained fixture. For project-authored Luau, pass strict analysis over the authoritative fixture with the actual adopted resource and material companion libraries. Pass if observed behavior matches the skill and upstream validated behavior. A response that merely repeats the instructions is `instruction-response` evidence, not executable proof.

## Test E - Representative integration

Use a realistic task that executes the maintained representative fixture and exercises the reason the resource was acquired. Pass if the actual implementation uses the correct activation owner, execution side, configuration, and project conventions. When libraries compose, inspect the exact pinned cleanup owner and verify ownership is registered before fallible construction, producers stop before their consumers, and the integration does not assume unsupported cleanup ordering or continuation.

Record static/construction separately from runtime-host evidence. If the child claims real input, focus, rendered layout, animation, or normal startup, exercise that behavior in an appropriate Studio/client path; domain-method calls and construction assertions cannot substitute. Record the fixture, configuration, contract, API, and material companion-dependency inputs and hashes that determine each check.

## Test F - Edge/failure diagnosis

Introduce a likely integration problem: missing dependency, wrong placement, invalid config, unavailable service, cleanup issue, or similar. Pass if the executed fixture exposes the failure and the skill leads to the real cause without hallucinating methods or unrelated rewrites.

When activation owns resources, test the applicable partial-acquisition, teardown, and cancellation cases from [integration-proof.md](integration-proof.md). Cleanup must still run after a failed assertion; a throwing producer/phase must not prevent later top-level phases; repeated destroy runs each resource at most once; and post-disposal producer activity cannot reach the consumer. Distinguish component-owned cleanup from package/process-global work using [Respect host ownership](integration-proof.md#respect-host-ownership).

When claiming clean diagnostics, force an unallowlisted generic warning and a generic error after otherwise passing assertions. Each must make the harness fail and retain an artifact associated with the active/last fixture through the complete runtime boundary the harness owns. Expected diagnostics must be exact and test-local. A green test summary without those red-capability checks does not prove a clean console. Apply [Respect host ownership](integration-proof.md#respect-host-ownership); do not attribute an unknown diagnostic producer until this guard can fail and a reduced reproduction identifies the owner.

## Test G - Version/provenance/verification truthfulness

Ask what source/version the guidance targets and whether the upstream resource was actually runtime-verified. Pass if both are recoverable directly from the skill and source review is not mislabeled as runtime verification.

## Test H - Security boundary

Required when the resource touches remotes, HTTP, credentials, persistence, arbitrary assets/code, or other trust boundaries. Pass if the skill preserves Roblox's server-authoritative/security expectations and identifies special resource risks.

## Test I - Operational reconciliation

For `required`, use a project whose installed resource state is independently mutable. Pass if every version-sensitive use detects the installed identity/version, compares it with its reviewed state, consults matching parent-maintained records/learnings, and stops on an unknown, mismatch, or current block.

For `conditional`, run both branches:

- Healthy ordinary use: make the declared pin and named lock/header match and supply a compatible unblocked schema-v3 record. Pass only if the narrow `check_resource_status.py` query returns `HEALTHY`, the agent avoids package internals/full record evidence/learnings, and it retains the exact integrity gate for completion.
- Block query: separately test a matching free-text block, missing/malformed record, identity/version mismatch, adverse or unknown reconciliation/verification/matching-host state, and compatible legacy record. Pass only if the blocked case produces `BLOCKED`; every missing, malformed, mismatched, unknown, or adverse case produces `UNKNOWN`; the compatible unblocked legacy record has a known usable reconciliation state and no adverse verification or matching-host state and is `HEALTHY`; and no evidence command is executed.
- State escalation: separately introduce a missing/mismatched pin or lock/header, verifier failure or drift, adoption/upgrade, an authorized repair, a hard correctness/security/identity/version defect, and an already-known block. Pass only if each applicable trigger stops version-sensitive use, loads the deterministic parent record/learnings route, and invokes `roblox-resource-acquisition` in `repair/reconcile` mode.

For `not-applicable`, pass only when the child gives a concrete immutable-install or version-insensitivity reason.

For a conditional repair, also run the economy test against the prior always-reconcile wording or an equivalent defective fixture. It must fail because healthy ordinary use unnecessarily reads lifecycle records, learnings, package internals, or provenance. This falsifiability check prevents the new fast path from becoming an untested prose preference.

## Test J - Catalog routing

Inspect the target host's visible skill activation surfaces whenever a generated child is added, refreshed, repaired, or adopted. Run this behavioral test when either (a) the target host set contains two or more generated children, or (b) any generated child has a plausible activation competitor among non-generated host-visible skills. First run `scripts/validate_skill_catalog.py` over the generated-child set and add each material non-generated competitor with `--routing-competitor <path>`; retain the resulting fingerprint. Non-generated competitors are routing inputs only and do not need to satisfy the generated resource-skill contract. For every reported overlap cluster, give independent agents:

- one task specific to each generated child in the cluster;
- one task specific to each competing host-visible skill needed to exercise the boundary;
- one simpler task that should select neither;
- one explicit-invocation smoke task per generated child.

Pass if the intended skill is selected for each specific task, competing skills stay out, the simpler task selects neither, explicit generated-child invocation succeeds, and the recorded fingerprint still matches the exact tested routing set. If independent execution is unavailable, record catalog routing `unavailable`, not passed. Record `not-applicable` only after host-visible activation inspection finds no plausible competitor and fewer than two generated children share the target host. Any later change to a tested generated child or routing competitor invalidates the prior fingerprint/evidence.

## Test K - Repair interrupt

Run each case without naming the parent skill unless the case explicitly tests direct invocation:

1. Introduce a reusable soft guidance defect with a safe reversible workaround. Pass only if the agent may finish the immediate work, invokes `roblox-resource-acquisition` repair diagnosis, and surfaces the task, installed state, expected/observed behavior, smallest reproduction, workaround, and durable correction before completion without forcing unrelated provenance reconciliation.
2. Introduce separate hard defects affecting correctness, security, canonical identity/version, and verification. Pass only if each stops dependent work and enters parent state reconciliation plus the repair loop.
3. Introduce a harmless one-off task-local adjustment. Pass only if it does not spuriously invoke resource repair.
4. Explicitly invoke the parent repair mode. Pass if the same classification and authority boundaries apply.

Run the soft case against the previous compliant behavior or an equivalent defective fixture that silently absorbs the recurring workaround. It must fail. This falsifiability control proves that finishing the immediate task is not mistaken for resolving reusable guidance debt.

## Change-based invalidation rule

After a repair patch, rerun the failed check first, then only previously passing checks whose declared inputs changed or whose assumptions depend on those inputs:

- API/example/lifecycle or maintained-fixture changes invalidate the executable integration and affected failure/cleanup checks;
- activation metadata or host-visible competitor changes invalidate catalog routing for the affected fingerprint;
- shared contracts, configuration, or dependency changes invalidate every check that declares that input and may require broader relevant integration;
- unrelated content leaves passing evidence current.

Bind this rule mechanically through structured `skill_validation.checks` input hashes. A whole-child hash may record which artifact ran, but cannot invalidate unrelated checks. Batch related fixes once their common cause is understood; speculative batches that obscure falsifiability remain invalid.

A repaired test must additionally demonstrate that it can still fail: run it against the defective state it was written to catch, or an equivalent. A test weakened until it cannot fail is deleted evidence, not a repair.

From the moment an input changes until its dependent reruns complete and pass, only those affected claims are stale. Preserve unrelated passing evidence. If a fixture is removed, mark its prior entry `historical`; its result remains truthful history but cannot satisfy current integration. Attempt budgets, convergence, and stop criteria for the repair loop live in [repair-loop.md](repair-loop.md).

## Reliability threshold

Mark a generated resource skill behaviorally verified only when:

- all applicable tests pass through their required execution mode;
- no applicable required test is recorded as unavailable;
- generated-skill structural validator passes;
- when a portable resource record is emitted, its resource-record structural/state validator passes;
- when both a portable record and generated child exist, their `validate_resource_bundle.py` identity/source-state consistency gate passes;
- operational reconciliation Test I passes when applicable;
- catalog routing Test J passes when two or more generated children share the target host set or a generated child has a plausible non-generated host-visible competitor;
- no unsupported API statement remains;
- no high-severity safety/integration defect remains;
- runtime tests are labeled accurately;
- static/construction, owned-lifecycle, runtime-host, and diagnostics claims are recorded separately, with every claimed lane actually observed;
- any clean-console claim passed forced generic warning/error regressions through owned teardown and retained its failure artifacts;
- every current behavioral claim has structured evidence whose declared inputs still match; booleans plus environment/result prose alone are legacy history;
- independent behavioral execution was actually performed rather than replaced by a same-agent contract audit;
- failures are not being hidden by weakening assertions.

Optional embellishments, more examples, or stylistic improvements are not reasons to continue once the threshold is met.
