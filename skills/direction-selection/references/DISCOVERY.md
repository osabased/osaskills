# Discovery Direction

Discovery is a bounded call/return subroutine for a direction-relevant evidence need, including orientation or coverage assessment. It is not a generic pre-direction evidence router, a conservative default, a production direction, or a way to maximize confidence.

## Invocation and ownership

With a surrounding controller, hand a non-directional unknown encountered before a genuine direction problem is live back to that controller. Discovery does not own general research, benchmarking, user clarification, project-state inspection, planning, persistence, or verification before invocation.

When a live direction comparison exists, enter discovery when its evidence need could materially affect the framing, candidate space, ranking, or support for the commitment. Apply the parent research-adequacy rule to orientation and coverage assessment. Preserve the interrupted comparison stage as owner, gather only the justified evidence, and return to that exact stage under the parent Continuation invariant. Do not restart applicability or the full protocol.

For standalone use only, discovery may serve an **applicability evidence probe** scoped to resolving the applicability question when evidence is necessary to determine whether a genuine direction problem exists or whether the incumbent is supportable. After the probe, return evidence and control to the [SKILL.md](../SKILL.md) applicability router. The router then exits, hands off, or enters a comparison mode. Discovery never emits a comparison outcome before comparison owns the decision.

## Discovery Entry Test

Apply this test before every discovery call. When the user explicitly mandates discovery work, only that specified work is authorized without the test; any extension requires a fresh test.

Every transition must satisfy all applicable conditions:

1. **Defined evidence need:** identify an unresolved fact, coverage gap, source-reliability concern, untested material assumption, or area needing orientation.
2. **Decision relevance:** explain how this need bears on applicability, framing, candidates, criteria, ranking, or the justification for commitment. For orientation, identify the relevant area and coverage goal without predicting specific findings or alternative outcomes.
3. **Worth investigating now:** the investigation can improve decision support in proportion to the stakes, evidence requirements, cost, delay, risk, and commitment. A direction that currently appears supported remains eligible when its evidentiary basis needs examination.

When the test fails, return to the owner. The applicability router may exit or hand off. A comparison owner may pass the best-supported direction with explicit residual uncertainty, return a `Direction Blocker`, or use the canonical adaptive path when its conditions hold.

**Complete when:** all applicable conditions pass and a bounded step is defined, or a failing condition returns control to the owner.

## Select the discovery step

Choose the methods, breadth, and depth needed to resolve the material uncertainty with applicable evidence. Use online research, documentation, inspections, tests, benchmarks, measurements, prototypes, or disposable experiments as the question requires. Define coverage around the deciding claims, relevant conditions, and credible conflicting evidence; expand the investigation when gaps could change the result. Set effort and commitment in proportion to the stakes and evidence requirements.

When the step uses source research for orientation, candidate coverage, or decision-relevant claims, read [RESEARCH.md](RESEARCH.md) completely and follow its workflow. Research supplies evidence within this discovery call; retain the recorded owner, commitment limits, and return condition. Use experiments or other methods when source research cannot establish the required property.

Record before acting:

1. **Owner and return point:** standalone applicability router or the exact interrupted comparison stage.
2. **Evidence need:** the fact, assumption, reliability concern, coverage gap, or orientation area and why it matters.
3. **Investigation:** the methods, sources, and coverage needed to address that need reliably.
4. **Decision effect:** the comparison or applicability judgments the evidence will inform; state specific discriminating outcomes when known.
5. **Commitment:** cost, delay, risk, and anything made harder to reverse at the likely future correction point.
6. **Stop / re-evaluate condition:** the evidence sufficient to return to the owner.

Design experiments to cover the conditions and integration effects material to the claim. Give higher-commitment experiments explicit limits, observability, and a rollback or exit path.

Before evidence can resolve applicability or carry a deciding comparative claim, apply the evidence applicability, reliability, and research-adequacy rules in [SKILL.md](../SKILL.md). Cheap or discriminating evidence that does not represent the actual property, version, environment, workload, integration effects, or claim at risk is informative but non-deciding.

**Complete when:** the step has a named owner, defined evidence need, coverage goal, proportionate and future-horizon-reversible commitment, and checkable stop condition.

## Execute a bounded discovery loop

1. Perform only the defined discovery work.
2. Update only the affected applicability fact, problem model, assumptions, candidate space, evidence, or comparison.
3. Return evidence and control to the recorded owner when the stop condition is met or the defined step cannot be completed.
4. Before another discovery step, rerun the Discovery Entry Test against the remaining uncertainty.

Continue while a material evidence need remains and further investigation has justified value under the Entry Test. Expand coverage when findings expose relevant gaps or leads. Scale commitment to the evidence need and safe reversibility. Return to the owner when the defined evidence need and coverage goal are addressed under the parent evidence standards, or further justified work cannot be completed; the owner assesses the gate and remaining limitations.

Distinguish:

- **Resolvable uncertainty:** evidence progressively narrows the unknown within a stable decision model. Continue only while the entry test passes.
- **Structurally unstable uncertainty:** worthwhile evidence keeps changing the model or credible futures, or commitment must occur before the question can be resolved. When further investigation has low decision value, stop ordinary discovery and return to `SKILL.md` for possible `Adaptive Direction` handling. Difficulty alone does not justify adaptive handling.

Do not rerun discovery indefinitely merely because uncertainty remains.

Exploratory code, scaffolding, prototypes, and migrations are disposable by default. They may not silently cross the governed consequential commitment boundary without a passing conventional direction or a passing bounded adaptive commitment. This does not block unrelated, already-supported, or safely future-horizon-reversible production work, and no pre-gate work may create de facto lock-in.

The loop is **complete when:** applicable, reliable evidence addresses the defined evidence need and coverage goal enough to return to the owner; the defined step fails or another entry test fails and returns control; or structurally unstable uncertainty returns to the canonical adaptive path. The owner—not discovery—selects and emits the resulting `Applicability Result`, `Direction Decision`, `Direction Blocker`, or `Adaptive Direction`.
