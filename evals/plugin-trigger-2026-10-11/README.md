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

## Limits

- There is 1 run per prompt, on one model, and the prompts are fairly direct.
- It tests triggering only, not answer quality.
- Cowork and claude.ai (marketplace install or zip upload) are untested.
