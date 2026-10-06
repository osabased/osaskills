# Resource-comparison behavioral cases

[comparison-cases.json](comparison-cases.json) contains fictional, closed-world cases for the resource-comparison policy. These are evaluation fixtures, not runtime instructions. Static checks validate their structure; they do not execute agents or prove better decisions.

## Compare outcomes

Use fresh isolated sessions with the same model/settings, tool availability, and per-case budget for: no skill, the resource-acquisition skill at `bbb1bdfee536b3e44923520b93fa5c3e818a8e8a`, and the exact candidate commit. Explicitly invoke the skill in the two skill conditions. Load only its runtime instructions and conditionally needed references. Keep this README, grader-only `accept`/`reject` fields, related cases, and implementation discussion out of the evaluated agent's context.

Supply one `prompt` at a time. The supplied measurements and observations are fixtures, not claims about real resources or tools. Resumed-evaluation cases supply earlier evidence as context; they do not establish that the evaluated agent performed those checks. For cases asking for the next evidence step, judge whether it addresses the deciding gap without claiming execution.

Judge substantive outcomes rather than new terminology or headings. Record each expectation as met, missed, or unclear with an excerpt or trace; retain rejected behaviors separately. A supported quantitative calculation is valid. Unsupported grades and weights matter when they distort or substitute for the required reasoning, not merely because a response contains numbers.

## Paired safeguards and limits

Run `strict-priority` with `threshold-only`, and `unknown-not-tie` with `supported-tie`, in separate sessions. Include the authority, trust/verification, existing-capability, bounded-refinement, ordinary-comparison, owner-preference, resumed-evaluation, and missing-evidence cases so a local improvement does not hide regressions in neighboring boundaries.

Keep exact commits, model/settings, responses/traces, judgments, and available tool/token/time measurements outside the evaluated agent's context. Choose repeat counts before reviewing results. Unavailable measurements remain unavailable. Do not add model calls to CI or interpret a green schema/document check as behavioral success. A static walkthrough can expose contradictory instructions but is not an independent model run or a measured improvement. Keep new real-world failures separate from repeatedly tuned fixtures.

## Full adoption and cross-project cases

[adoption-cases.json](adoption-cases.json) exercises proactive adoption, reliability/maintenance selection, default project scope, unresolved project scope, explicit user scope, unavailable tool proof, different project pins, explicit evaluation-only scope, an already-solved simple task, and factual repair versus upgrade decisions. Supply only one case's `prompt` and the runtime skill to each fresh read-only session; keep `accept`/`reject` fields and other cases hidden. Score decisions and truthful remaining work, not wording. These simulations establish instruction-response evidence only, never actual integration, runtime execution, host discovery or implicit routing.

[community-cases.json](community-cases.json) exercises topic-level recommendations, repeated endorsements, version/context disagreement, fixed curated targets, inaccessible community channels and healthy-use boundaries. Follow the same isolated-session and hidden-grading rules; use only the supplied fictional evidence, and distinguish supplied proof from checks the agent actually ran.

For a non-Git local skill, capture the exact baseline/candidate file fingerprints instead of inventing commits. A candidate-only run can expose defects but does not measure improvement against a matched baseline. Keep unavailable paired conditions explicit.

## Maintenance and ordinary-use cases

[maintenance-cases.json](maintenance-cases.json) preserves the behavioral requirements behind the parent router's former exact-prose tests: target-bound refresh, hard/soft/harmless repair, healthy conditional use, required plugin integrity and unresolved project scope. Use the same isolated-session and hidden-grading protocol. Static tests check reference reachability and fixture structure; they do not establish that an agent followed a repair route or performed a check. Use the comparison/adoption/community cases alongside them to check neighboring boundaries.
