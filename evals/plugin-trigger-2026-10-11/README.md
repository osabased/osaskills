# Plugin triggering check (2026-10-11)

The [Sonnet comparison](../sonnet-ab-2026-10-11/README.md) copied the skills into `.claude/skills/`. This check covers the recommended install instead: the `osaskills` plugin, added with `claude plugin marketplace add <this repo>` and `claude plugin install osaskills@osaskills`, where every skill is namespaced `osaskills:<name>`.

Headless Claude Code 2.1.295 (`claude -p`, model `sonnet`) ran in a copy of the comparison's [scaffold](../sonnet-ab-2026-10-11/scaffold/), with a 3-turn limit and Bash, editing, web and subagent tools disabled. It used the normal user config, so the plugin loaded as it would for a user. Run it with `python harness.py [--cli PATH] [case-id ...]` after installing the plugin. [`cases.json`](cases.json) has the prompts, and [`results/`](results/) has one record per run.

## Results (14 prompts, 1 run each)

| Check | Result |
|---|---|
| Skills registered at startup | All 14 `osaskills:*` skills, in every run |
| What the model sees in its skill list (`probe-listing`) | The 11 automatic skills. `then-what`, `motion-studies` and `vod-discovery` are absent, as `disable-model-invocation: true` intends |
| Prompts aimed at a user-only skill (2 each, 6 total) | No skill loaded |
| Prompts for automatic skills | `system-review`, `roblox-resource-acquisition`, `roblox-vide` and `structure-roblox-projects` each loaded through the Skill tool |
| Explicit `/osaskills:then-what`, `/osaskills:motion-studies`, `/osaskills:vod-discovery` | All three ran in their skill's format |

A slash-invoked skill expands into the prompt and leaves no tool event. The harness therefore grades the explicit cases by a format cue from each skill: "Done when" for then-what, "named constant" for motion-studies, and "vod.py doctor" for vod-discovery.

`rc=1` on some runs means the 3-turn limit cut the answer off. The skill-loading decision comes earlier, so it doesn't affect these checks. The run cost about $0.95.

## Rerun after nesting the library skills

[PR #50](https://github.com/osabased/osaskills/pull/50) moved the eight library skills into `skills/roblox-resource-acquisition/libraries/`. This rerun loaded that checkout with `python harness.py --plugin-dir <checkout>` and added four cases:

- `pos-janitor` and `pos-charm`, for two more library skills;
- `lib-parent-route`, which has a library skill follow its pin check into RRA's shared `references/child-usage.md`;
- `probe-read-scope`, which checks which skill files a headless run can read.

`results/` now holds this run. [Git history](https://github.com/osabased/osaskills/commits/main/evals/plugin-trigger-2026-10-11/results) has the earlier one.

| Check | Result |
|---|---|
| Skills registered at startup | All 14 `osaskills:*` skills, including the 8 nested libraries, in every run |
| Model's skill list (`probe-listing`) | The same 11 automatic skills as before |
| The 14 original cases | All pass, as before |
| `roblox-janitor`, `roblox-charm` | Each loaded through the Skill tool |
| `lib-parent-route` | `roblox-janitor` resolved `../../references/child-usage.md`, read it, and followed its pin-check steps |

The first rerun of `lib-parent-route` had its read **denied**, and so did the skill's own `references/setup.md`. A headless run can't approve reads outside the project, and with `--plugin-dir` the skill files are outside it. The harness now passes `--add-dir <checkout>` alongside `--plugin-dir`, and it counts a read only when it succeeds. Before this, an attempted read counted as a pass. The two route cases cost about $0.17 to rerun, and the full run cost $1.19.

## Limits

- There is 1 run per prompt, on one model, and the prompts are fairly direct.
- It tests triggering only, not answer quality.
- Cowork and claude.ai (marketplace install or zip upload) are untested.
