# Resource-comparison behavioral cases

[comparison-cases.json](comparison-cases.json) contains fictional, closed-world cases for the resource-comparison policy. These are evaluation fixtures, not runtime instructions. Static checks validate their structure; they do not execute agents or prove better decisions.

## Compare outcomes

Use fresh isolated sessions with the same model/settings, tool availability, and per-case budget for: no skill, the resource-acquisition skill at `bbb1bdfee536b3e44923520b93fa5c3e818a8e8a`, and the exact candidate commit. Explicitly invoke the skill in the two skill conditions. Load only its runtime instructions and conditionally needed references. Keep this README, grader-only `accept`/`reject` fields, related cases, and implementation discussion out of the evaluated agent's context.

Supply one `prompt` at a time. The supplied measurements and observations are fixtures, not claims about real resources or tools. Availability fixtures must match the harness: make direction-selection unavailable for `standalone-supported` and available for `live-direction-routing`. Keep its version and host capabilities constant between baseline and candidate conditions. If the harness cannot expose the requested capability, report that case as blocked, not executed. Return cases supply an already-completed handoff as context; they do not establish actual invocation. Do not count plausible routing prose as proof of a tool call.

Judge substantive outcomes rather than new terminology or headings. Record each expectation as met, missed, or unclear with an excerpt or trace; retain rejected behaviors separately. A supported quantitative calculation is valid. Unsupported grades and weights matter when they distort or substitute for the required reasoning, not merely because a response contains numbers.

## Paired safeguards and limits

Run `strict-priority` with `threshold-only`, and `unknown-not-tie` with `supported-tie`, in separate sessions. Include the authority, trust/verification, existing-capability, bounded-refinement, standalone, and handoff cases so a local improvement does not hide regressions in neighboring boundaries.

Keep exact commits, model/settings, responses/traces, judgments, and available tool/token/time measurements outside the evaluated agent's context. Choose repeat counts before reviewing results. Unavailable measurements remain unavailable. Do not add model calls to CI or interpret a green schema/document check as behavioral success. A static walkthrough can expose contradictory instructions but is not an independent model run or a measured improvement. Keep new real-world failures separate from repeatedly tuned fixtures.

## Full adoption and cross-project cases

[adoption-cases.json](adoption-cases.json) exercises proactive adoption, reliability/maintenance selection, unavailable tool proof, different project pins, explicit evaluation-only scope, an already-solved simple task, and factual repair versus upgrade decisions. Supply only one case's `prompt` and the runtime skill to each fresh read-only session; keep `accept`/`reject` fields and other cases hidden. Score decisions and truthful remaining work, not wording. These simulations establish instruction-response evidence only, never actual integration, runtime execution, host discovery or implicit routing.

[community-cases.json](community-cases.json) exercises topic-level recommendations, repeated endorsements, version/context disagreement, fixed curated targets, inaccessible community channels and healthy-use boundaries. Follow the same isolated-session and hidden-grading rules; use only the supplied fictional evidence, and distinguish supplied proof from checks the agent actually ran.

For a non-Git local skill, capture the exact baseline/candidate file fingerprints instead of inventing commits. A candidate-only run can expose defects but does not measure improvement against a matched baseline. Keep unavailable paired conditions explicit.
