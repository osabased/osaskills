# Skill simplification review — 2026-10-06

## Decision and scope

Retain all six included top-level skills and all eight bundled resource children, with smaller entrypoints and conditional detail. Leave `skills/vod-discovery/**` unchanged.

The revision concentrates each skill on the behavior it should change:

- **consolidate:** synthesize an evidence-backed recommendation and continue authorized work.
- **direction-selection:** frame the immediate commitment, compare credible options, examine deciding evidence, and stop. Full comparison extends that loop; detailed handoff schemas live in one conditional reference.
- **system-review:** trace interactions, challenge findings, and close defects with positive evidence.
- **motion-studies:** resolve an actual motion choice through observed playback and acceptance; preserve accepted motion during ordinary refinements.
- **structure-roblox-projects:** locate the affected source and ownership boundary, complete the task, and verify its behavior. Broad onboarding remains available when requested.
- **roblox-resource-acquisition and children:** use the needed acquisition/maintenance route, preserve exact targets and lifecycle states, and keep version-specific API/lifecycle guidance accessible. Shared checker commands and first-use freshness have single owners.

No new top-level primitive skills were introduced. The reusable child command contract was already shared; it now owns the repeated command recipes. Recorded review, freshness, adoption, and guarded-maintenance preferences remain in force.

## Size

Whitespace-separated word counts include frontmatter, links, and code. They measure text size, not model tokens or runtime cost.

| Entrypoint | Before | After |
| --- | ---: | ---: |
| consolidate | 611 | 333 |
| direction-selection | 2,995 | 1,213 |
| motion-studies | 693 | 429 |
| roblox-resource-acquisition | 2,285 | 1,130 |
| structure-roblox-projects | 1,384 | 779 |
| system-review | 1,095 | 672 |
| Eight bundled children, combined | 4,195 | 3,099 |
| **All 14 entrypoints** | **13,258** | **7,655** |

Entrypoint text is **42.3% smaller**. All included `SKILL.md` and runtime-reference Markdown combined decreases from **64,913 to 54,447 words (16.1%)**. Conditional technical references account for much of the remaining material; these totals do not represent a typical activation's context load.

## Repository checks

Baseline: `30da5400534ac091fca0073dbf5ca3a9efe9d54f`.

| Check | Baseline | Candidate |
| --- | --- | --- |
| Resource Python suite | 238 passed | 240 passed |
| Structure Python suite | 10 passed, 1 skipped, 4 subtests passed | 10 passed, 1 skipped, 4 subtests passed |
| Included skill frontmatter | — | All 14 valid |
| Local Markdown links/anchors in changed documents | — | 160 checked; no broken targets |
| Removed direction-reference pointers | — | No stale mentions |
| `git diff --check` | — | Passed |
| Excluded VOD subtree | — | All 59 files byte-identical |
| Executable checker implementations | — | Unchanged |

The skipped structure test requires a real Rojo installation, unavailable in the execution environment. The environment used Python 3.12.14, pytest 9.1.1, coverage 7.15.2, and PyYAML 6.0.3.

The resource test changes replace affected exact-prose assertions with packaging/navigation checks and validate seven new maintenance case definitions. The extra passing tests do **not** mean additional behavioral cases were executed. Existing executable validators, selector pins, source-integrity rules, and historical proof records were preserved.

One independent read-only adversarial review inspected the diff, affected reference routes, shared checker arguments, output/ownership contracts, and preservation boundaries. It retained no material finding. It did not rerun upstream qualification, host activation, or Studio checks.

## Advisory scenario comparison

[Cases](cases.json) cover all 14 included skills through 18 supplied-fact requests. [Expectations](expectations.json) were fixed before the responses were inspected.

Three fresh agents received the same requests in the same order, one batch per condition:

| Anonymous label used for grading | Condition | Saved answers |
| --- | --- | --- |
| A | Original repository skills | [Original](original-responses.json) |
| B | No repository skill loaded | [No skill](no-skill-responses.json) |
| C | Revised repository skills | [Revised](revised-responses.json) |

Each agent had a fresh conversation, inherited the same parent model/settings without overrides, and handled all 18 requests. Cases within a batch therefore shared agent context. Agents were instructed to treat them independently, use only supplied facts and the permitted runtime references, and give advisory answers without modifying projects or invoking external/runtime systems. The no-skill condition retained the normal agent/system instructions; it was not an unprompted bare-model condition.

Skill agents received the appropriate entrypoint for each case and could read relevant runtime references. Grader expectations, evaluation directories, other conditions' answers, and implementation discussion were excluded from their authorized reading. A separate fresh grader received the rubric and anonymously labeled answers. It could inspect pinned guidance to resolve a disputed API fact and recorded that access.

The candidate snapshot matched all 220 supplied skill-package files when checked after the runs. A final whitespace check then removed one extra blank line at the end of the first-use reference; no instruction text changed. [Snapshot metadata](snapshot.json) records final file fingerprints, that evaluated-file difference, and the original commit. Transcript-local sandbox links refer to the transient source snapshots; their equivalent original files are available at the recorded baseline commit.

### Observations

The substantive general-reasoning decisions were similar across conditions: bounded evidence gathering for the adapter decision, proportional handling of a one-line fix, rejection of an unsupported redesign, separate defect/refutation outcomes for the transaction cases, and truthful limits on unobserved runtime checks.

The package-specific guidance supplied details the no-skill answer did not fully recover. In the Blink case, both skill conditions named the pinned local `pesde run blink` invocation; the no-skill answer called for a supported pinned invocation without supplying it. In the Vide case, both skill conditions identified `step(0)` as disconnecting the shared stepper at the reviewed pin; the no-skill answer rejected component teardown through that call but described it imprecisely as a scheduling operation.

See [per-expectation judgments](judgments.json) and [grading observations](grading-observations.md) for omissions, uncertainties, and supporting excerpts. These are advisory outcome observations, not proof of tool execution.

### Limits

- This is **three batches and 54 answers**, not 54 independent trials. There were no repeats, randomized orders, or per-case fresh conversations.
- The cases are small, supplied-fact smoke checks chosen around the affected behavior. They are not a held-out benchmark, a comprehensive run of the existing evaluation suites, or evidence of open-web retrieval quality.
- No automatic skill discovery, live project adoption, host activation, Roblox execution, rendering, input, teardown, or release pipeline was exercised.
- The provider-resolved model identifier and reasoning setting, per-case tool costs, token usage, and elapsed time were not captured as reproducible measurements.
- Similar correct answers do not prove that a skill adds value. Shorter entrypoints do not prove better reasoning, latency, or token efficiency. These runs support retaining the reduced version without a demonstrated regression in the exercised cases; they do not establish general superiority over the original or no-skill condition.

## Next evidence worth collecting

Use actual sessions to identify instructions that prevent recurring failures or impose avoidable work. Add those failures as new cases before tuning to them, and compare original/reduced/no-skill conditions with genuinely isolated repeated runs when a retention decision depends on measured benefit. Generic reasoning skills should continue to earn their place; exact project policy and pinned domain contracts already have a clearer information role.
