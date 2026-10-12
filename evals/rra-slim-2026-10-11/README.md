# Audit: structure-roblox-projects and roblox-resource-acquisition (2026-10-11)

This audit covers the two Roblox workflow skills. The decisions taken (with the user):

- slim `roblox-resource-acquisition` (RRA) substantially;
- keep the ModuleLoader SSA contract opt-in only, without cross-skill ownership machinery;
- apply the fixes on a branch, then run a targeted old-vs-new A/B.

## Findings and what changed

### roblox-resource-acquisition

| # | Severity | Finding | Change |
|---|---|---|---|
| 1 | High | **Disproportionate weight.** The skill had 15 references (about 160 KB), 11 scripts (about 4k lines) and 257 tests. Most of that served a record-keeping layer: schema-v3 resource records, four trust bases, a curated registry, a learnings store, guard-file update transactions, installed vs operational child states, catalog fingerprints, a repair loop with attempt budgets, and testing protocol A–K. An ordinary "add a library" task read several of these. In the earlier A/B it cost about 3× with no quality gain, and the answer reported on records. | Rewritten around the actual work: choose → adopt → (optional) child skill. There are now 5 references (about 32 KB): `choosing`, `adopting`, `child-usage`, `child-authoring` and `bundled-skills`. Pins live in manifests and locks. Adopted resources are listed in the existing `CLAUDE.md` block, which can also note a known issue or blocked use. |
| 2 | High | **Child status vocabulary was heavy.** Children had to interpret PASS / HEALTHY / NO-RECORD / UNAVAILABLE / UNKNOWN / FAIL / MISMATCH / BLOCKED / FAILED from two checkers. | One checker (`check_resource_install.py`) with `PASS` (0), `FAIL` (1, stop) and `UNAVAILABLE` (2, advisory). All 8 children's "Check the pin" sections were updated. |
| 3 | Medium | **Cross-skill coupling.** RRA hard-coded that `structure-roblox-projects` owns the ModuleLoader pin through `project_use.authority`, and its maintenance reference governed the structure skill too. | Replaced with one plain rule in `adopting.md`: a pin fixed by another document stays fixed (SSA is given as the example). The maintenance/guard flow is gone. |
| 4 | Medium | **AGENT_DIR rule duplicated** in about 6 places (SKILL.md, child-usage, state-policy, project-adoption, adoption-policy, scripts). | No longer needed by RRA: nothing is stored under `AGENT_DIR/roblox/resources/` any more. The structure skill keeps the rule once, for its project guide. |
| 5 | Low | **Dense, jargon-heavy prose** ("verified-acquisition trust", "project-use authority", "instruction-response evidence"). | Plain wording throughout. Roblox-specific substance is kept: search terms, hard gates, comparison criteria, community-evidence rules, Wally `@=` exact pins, cleanup-composition rules for Janitor/Maid/Trove/Vide. |
| 6 | Compatibility | Existing children (bundled or user-generated) carry `reconciliation.record`/`learnings`. | Kept on child contract 1. Those fields are accepted and ignored, so older children still validate. |

Scripts kept: `check_resource_install.py`, `validate_skill.py`, `_resource_contract.py`, `_common.py`. Removed:

- `check_resource_status.py`
- `validate_resource_record.py`
- `validate_resource_bundle.py`
- `validate_learnings_store.py`
- `validate_curated_registry.py`
- `guard_skill_update.py`
- `validate_skill_catalog.py`

The record, learning and curated templates were also removed. Tests: 144 pass on Python 3.11 and 3.13, with 82% branch coverage (the CI floor is 59%). The skill's hand-graded eval fixtures (`skills/roblox-resource-acquisition/evals/`) were rewritten to the new behavior and none were dropped. Six case ids were renamed: `child-blocked`, `fixed-curated-target`, `healthy-existing-capability`, `healthy-conditional`, `curated-preference` and `trusted-unverified`.

### structure-roblox-projects

| # | Severity | Finding | Change |
|---|---|---|---|
| 1 | Medium | `ssa-bootstrap.md` claimed this skill "owns" the ModuleLoader dependency in RRA's authority terms, and routed acquisition through RRA's `acquire/adopt` mode. SSA itself was already opt-in (`preference-resolution.md`: "not the default for new projects"). | Ownership is restated as architecture: the loader pin changes only through the SSA migration/upgrade steps, never as a side effect of a refresh. Acquisition is direct (exact asset or Wally version plus SHA-256), with RRA optional. |
| 2 | Low | References to RRA storage that no longer exists: the `.skill-maintenance` guard note in SKILL.md, observation logs under `AGENT_DIR/roblox/resources/`, and the legacy `~/.roblox-resources/`. | Removed. |
| 3 | Low | The real-Rojo tests skipped on `shutil.which("rojo")`. A Rokit shim passes that check but fails outside a Rokit project, so the tests errored instead of skipping. | They now skip unless `rojo --version` actually runs. |
| 4 | Freshness | `rojo.md` facts were "verified on 7.7.0". | Rerun on Rojo 7.7.1: 13/13 pass, including the duplicate-service wrapper case. The docs now say 7.7.0 and 7.7.1. |

Not changed:

- The description is 819 of 1024 characters, which is fine.
- `migration.md` is still abstract and could be tightened later.
- Two dated platform claims weren't re-checked against Creator Hub in this audit: the Server Authority full release on 2026-07-09 and Script Capabilities "client beta as of 2026-10". The skill already tells the agent to re-open the official page before relying on them.

## A/B: old RRA vs slim RRA

Headless Claude Code (`claude -p`, model `sonnet`) ran in the [earlier scaffold](../sonnet-ab-2026-10-11/scaffold/). Bash, web search and subagents were disabled. Only project and local settings were loaded, so no user plugins or skills were present. The "old" condition used every skill at `cf9847e` (main before this audit); "new" used this branch. There were 2 runs per cell. An Opus subagent graded the answers blind against [rubrics](grading/rubrics.md), and [`grading/key.json`](grading/key.json) maps the labels back to runs. Run a case with `python harness.py cases.json <case-id>`.

| Task | Skill that loaded | Rubric old | Rubric new | Overall old | Overall new | Cost old | Cost new |
|---|---|---|---|---|---|---|---|
| "Add a signal library" (LemonSignal already declared) | RRA | 9/10 | 9/10 | 8.3 | 8.0 | $0.21 | $0.11 |
| Janitor vs Trove, recommendation only | RRA | 10/10 | 10/10 | 8.0 | 8.5 | $0.07 | $0.08 |
| Janitor edit with the project pinned to 1.17.0 (guide targets 1.18.3) | roblox-janitor | 10/10 | 10/10 † | 8.3 | 8.3 † | $0.09 | $0.08 |
| Add StyLua | structure-roblox-projects | 10/10 | 10/10 | 8.8 | 9.0 | $0.12 | $0.11 |
| **Total** | | **39/40** | **39/40** | **8.3** | **8.4** | $0.12 | $0.09 |

† After one fix. On the first slim version, one of the two mismatch runs refused to edit because the rewritten "stop on a mismatch" wording read as absolute (rubric 4/5, overall 4.0). The old children had the same sentence, but their surrounding status table softened it. The children and `child-usage.md` now say: on a mismatch, tell the user, keep the project's pin, continue with API confirmed at the project's version, and stop only where the task depends on version-specific behavior. Both reruns made the edit, flagged the pin and kept it (5/5, 8.5 and 8.0; `results/q-mismatch-new-*-v2.json`).

What changed:

- **Same quality at lower cost.** The rubric total is unchanged at 39/40, and blind overall scores are within noise.
- **"Add a signal library" costs half as much** ($0.21 → $0.11, 21.5 → 12.5 turns, 10.5 → 6.5 file reads). Both versions found the declared LemonSignal; the old one read more lifecycle material on the way.
- **The StyLua task loaded the structure skill, not RRA**, in both versions. Its default-tooling reference covers StyLua, which is reasonable. The tie there mostly reflects the structure skill.

Limits: two runs per cell, one model, no web, and fairly direct prompts. Child-generation, upgrade and repair flows weren't exercised; the [skill's own eval fixtures](../../skills/roblox-resource-acquisition/evals/README.md) cover them for manual runs. The triggering check wasn't rerun: the RRA description changed only "BLOCKED" to "FAIL", and the child descriptions are unchanged. The [2026-10-11 triggering results](../sonnet-ab-2026-10-11/README.md) still apply.
