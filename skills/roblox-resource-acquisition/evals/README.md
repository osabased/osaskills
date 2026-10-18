# Behavioral eval fixtures

Hand-graded, closed-world cases for `roblox-resource-acquisition`. All resources, URLs and results in them are fictional fixtures. They are not runtime instructions, and the static tests only check their structure; a green test run says nothing about agent behavior.

| File | Covers |
| --- | --- |
| [comparison-cases.json](comparison-cases.json) | Choosing between candidates: strict priorities vs thresholds, supplied quantitative models, unknown evidence vs real ties, hard gates, fixed targets and project-listed preferences, existing capabilities, unverified vs unavailable checks, bounded workarounds, owner-reserved choices, resumed evaluations. Each case has a `family`; paired cases list each other in `related`. |
| [adoption-cases.json](adoption-cases.json) | The add/adopt flow: proactive adoption, pending adoption when a required check can't run, different pins across projects, unresolved project scope, explicit user-wide skill placement, evaluation-only scope, an already-solved task, and a guidance fix vs a new release, cloning a missing catalog skill, preferring the catalog pin, a pending install that refuses the clone, executing an upgrade, executing a removal. |
| [community-cases.json](community-cases.json) | Community evidence: copied endorsements, a project-named target, inaccessible channels, version/context disagreement, sparse evidence, and when no survey is needed. |
| [maintenance-cases.json](maintenance-cases.json) | Using an adopted library skill: pin check `PASS` / `UNAVAILABLE` / `FAIL`, a plugin file outside the lock, hard / soft / harmless guidance defects, and a project pin newer vs older than the skill's. |
| [trigger-cases.json](trigger-cases.json) | Queries that should and should not select the skill, for tuning the `description`. Rerun after any description change; near-misses matter as much as positives. Boundary pairs with `structure-roblox-projects`: this skill owns choosing, pinning, adding, upgrading or removing a specific package or tool; first-time setup of a manager or toolchain belongs to that skill. |

## Running a case

1. Start a fresh, isolated session per case with the same model, settings, tools and budget across conditions. Conditions: no skill, the skill at a baseline commit, and the skill at the candidate commit. In the skill conditions, invoke the skill explicitly.
2. Give the agent only the case's `prompt` and the skill's runtime files (`SKILL.md` and the references it chooses to read). Keep `accept`, `reject`, `related`, other cases and this README out of its context.
3. Grade outcomes, not wording: mark each `accept` item met, missed or unclear with an excerpt, and record any `reject` behavior separately. Supplied results in a prompt are fixtures; the agent must not present them as checks it ran.
4. Run paired cases (`strict-priority` / `threshold-only`, `unknown-not-tie` / `supported-tie`) in separate sessions, and include neighboring cases so a local improvement can't hide a regression.

Choose repeat counts before looking at results. Keep commits, settings, transcripts and grades outside the evaluated context. A candidate-only run can expose defects but doesn't measure improvement. Don't add model calls to CI, and keep new real-world failures separate from fixtures that have been tuned against.
