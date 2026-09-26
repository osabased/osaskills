# Resource Evaluation Rubric

Compare qualified resources using applicable evidence and the task's priorities, not a default numerical score.

## Hard gates

A candidate cannot be selected when any applicable hard gate fails:

- **Fit:** cannot meet the required behavior.
- **Evaluability:** behavior/source needed for safe adoption cannot be inspected or tested.
- **Compatibility:** known incompatibility with required Roblox/project behavior.
- **Safety:** unacceptable client/server trust, credential, remote-code, or asset-script risk for the use case.
- **Legitimacy:** usage/license terms clearly disallow the intended adoption.
- **Proof:** required behavior fails reproducibly in an isolated test.

Unknown is not automatically failure, but a material unknown must be resolved before a newly discovered resource earns verified-acquisition trust. Curated resources already have policy trust; unresolved facts still limit what can truthfully be called verified.

## Evidence-and-priority comparison

Use only criteria that could change the decision, consistently across serious candidates. For each deciding criterion, identify the observable outcome, whether it is a threshold or an objective to optimize, and whether its priority is strict or permits tradeoffs. Preserve established priorities; do not replace requested optimization with "good enough" or invent scores, weights, or tradeoff rates. Resolve only ambiguity that could change the recommendation.

Keep measurements in meaningful units. Use task-supplied or evidence-backed numerical models with their assumptions and limits; this rubric supplies no generic grades, weights, or aggregate total.

For each deciding claim, identify applicable evidence and separate observation from inference. Match the relevant resource identity/version, environment, workload, and integration effects. Unsupported adjectives are no substitute for unsupported scores. Before rejecting a serious candidate on a decisive weakness, consider one concrete, bounded refinement that could change the result; count its integration, maintenance, and reversal costs, and do not treat a hypothetical fix as demonstrated capability or authorization to implement it.

These are resource-specific evidence prompts, not a mandatory checklist or priority order:

| Criterion | What good evidence looks like |
|---|---|
| Requirement fit | Directly solves the brief without major unrelated machinery |
| Correctness evidence | Reproducible tests, clear source behavior, credible issue history |
| Integration cost | Simple install, limited project assumptions, reversible adoption |
| Maintenance/currentness | Recent compatible releases/commits, maintained docs, responsive fixes |
| API/documentation quality | Public API and lifecycle are explicit and match source |
| Security posture | Server authority preserved, no suspicious loaders/credential practices |
| Dependency burden | Small, justified dependency graph with understandable transitive behavior |
| Testability | Can be isolated and meaningfully validated |
| Performance fit | Evidence matches the project's actual scale; benchmarks are reproducible/relevant |
| Portability/lock-in | Resource can be replaced without infecting unrelated architecture |

Recommend the best-supported fit under the established criteria, explaining the decisive evidence, strongest alternative's losing tradeoff when one exists, material uncertainty, and what would change the recommendation. Do not manufacture a winner when the deciding support is missing.

## Decision ownership

Preserve the fixed targets, roles/pins, adequate authorized project capabilities, curated policy preferences, and lifecycle scope established by [qualification-workflow.md](qualification-workflow.md). Comparison does not independently reopen those boundaries or turn trust into runtime proof.

Keep straightforward, supported choices local. Resolve a directly inspectable resource fact through its evidence route rather than starting a direction comparison merely because it is unknown.

When a consequential direction remains live because alternatives compete, comparative justification is weak, framing or candidate-space adequacy is uncertain, or material evidence challenges the choice, use `$direction-selection` when available. Enter through its applicability router, not directly into full mode. Carry forward the brief, constraints, authority, candidates, and existing evidence; do not restart completed qualification. Resource acquisition returns bounded resource-evidence answers to the owning comparison. Honor the returned commitment-scoped decision or blocker; a blocker cannot be bypassed by a local fallback. Acquisition retains the authorized lifecycle work after the comparison returns, not a second competing direction decision.

If that skill is unavailable, apply the local comparison rules proportionately and report any decision-sensitive evidence or authority blocker. Do not claim an invocation or Direction Gate result that did not occur, or require installation merely to answer a supported local choice. Selection alone grants neither trust nor mutation authority.

## Evidence strength

Among evidence applicable to the deciding claim, prefer roughly in this order:

1. Direct executable test in the target environment.
2. Source code + official/canonical documentation.
3. Maintainer release notes/issues/tests.
4. DevForum maintainer post and discussion.
5. Independent user reports.
6. Popularity signals.

Popularity is discovery evidence, not correctness evidence.

## Tie-breakers

Distinguish a supported meaningful advantage, supported practical equivalence, and an unresolved difference. Use requirement-backed tolerances or evidence-backed ranges when available. Practical equivalence permits moving to the next ordered criterion; missing evidence or a potentially material unresolved difference does not establish a tie. Identify the smallest plausible change that would switch an uncertain recommendation, investigating only when proportionate and decision-sensitive.

For a supported tie under the established criteria, use applicable user/project tie-breakers first; otherwise prefer:

1. smaller conceptual/integration surface;
2. stronger testability;
3. clearer lifecycle and failure behavior;
4. fewer security-sensitive behaviors;
5. easier removal/replacement;
6. more current maintenance evidence.

Do not prefer additional features that the acquisition brief does not need.
