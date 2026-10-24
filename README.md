# osaskills

Skills for Claude covering Roblox development, VOD discovery, and review workflows. They work in Claude Code and in Cowork / claude.ai.

## Install

### Claude Code plugin (recommended)

```text
/plugin marketplace add osabased/osaskills
/plugin install osaskills@osaskills
```

Recent Claude Code versions also accept `/plugin install osaskills --marketplace osabased/osaskills` as a single step. The Roblox library skills live in a catalog at `skills/roblox-resource-acquisition/libraries/`. The plugin doesn't load them; when a project needs one, the agent clones it into that project's `.claude/skills/`, and a session-start hook points out declared libraries that have no current clone. Plugin skills are namespaced, for example `/osaskills:then-what`.

Claude Code leaves auto-update off for third-party marketplaces. To get new versions automatically, open `/plugin` → **Marketplaces** → `osaskills` → **Enable auto-update**, or add `"autoUpdate": true` to the `osaskills` entry under `extraKnownMarketplaces` in `~/.claude/settings.json`. To update by hand, run `claude plugin update osaskills@osaskills`.

### Cowork / Claude desktop

Open **Customize → Plugins → Add → Add marketplace**, enter `osabased/osaskills`, then install `osaskills`. You can also zip a single skill folder and upload it in the Skills section of Claude's settings. Before you upload `then-what`, `sharpen` or `vod-discovery` as a zip, delete their `disable-model-invocation: true` line, because claude.ai uploads reject frontmatter keys outside the base skill spec. Scripts may not run in an uploaded skill; the Roblox library skills then fall back to advisory mode and tell you which checks they skipped. think-tank runs its panelists as the plugin's `think-tank-member` agent, and chat and uploaded skills don't load agents, so it needs a plugin install; it has only been tried in Claude Code. design-roblox-ui renders with rhr, which needs a local install, and sends renders to the plugin's `roblox-ui-reviewer` agent, falling back to a general-purpose subagent without it; it too has only been tried in Claude Code.

### Skills CLI or manual copy

```sh
npx skills@latest add osabased/osaskills --agent claude-code
npx skills@latest add osabased/osaskills --full-depth --skill roblox-vide --agent claude-code
```

Run the command from your project root to install into `.claude/skills/`, or add `--global` for `~/.claude/skills/`. `--list` shows the available skills. To install by hand, copy whole skill folders from `skills/` into either location. Keep each folder intact. The second command adds one Roblox library skill to a project; by hand, copy its folder from `skills/roblox-resource-acquisition/libraries/` into the project's `.claude/skills/`. think-tank also needs its panelist agent, and design-roblox-ui its reviewer: copy `agents/think-tank-member.md` or `agents/roblox-ui-reviewer.md` into `.claude/agents/` or `~/.claude/agents/`.

Check that Claude actually loaded a skill: it should appear under `/skills`, and `/<name>` should run it.

## Skill catalogue

| Problem | Skill | Invocation |
|---|---|---|
| An agent left you with findings or open-ended choices, and you need a clear recommendation and next step | [then-what](./skills/then-what/) | `/then-what` only |
| You have a vague direction and want help defining it, and checking it's what you actually want, before anything gets built | [sharpen](./skills/sharpen/) | `/sharpen` only |
| A long session has you unsure whether the agent's changes still serve what you asked for | [bigger-picture](./skills/bigger-picture/) | automatic, or `/bigger-picture` |
| You want independent second opinions on a question or plan, with their disagreements shown rather than smoothed over | [think-tank](./skills/think-tank/) | `/think-tank` only |
| You need to place Roblox code correctly, set up Rojo or Script Sync, start or onboard a project, or make a Roblox repo agent-ready (guide, checks, hooks, CI, play-test verification) | [structure-roblox-projects](./skills/structure-roblox-projects/) | automatic |
| You want to choose, add, compare, or upgrade a Roblox library or development tool | [roblox-resource-acquisition](./skills/roblox-resource-acquisition/) | automatic |
| You're building or restyling Roblox game UI and want it to look designed rather than generic: a direction you pick, a theme, and screens checked from phone and desktop renders by a reviewer that never sees the code | [design-roblox-ui](./skills/design-roblox-ui/) | automatic |
| You need to find moments across long VODs and prepare Premiere markers or a review timeline with alternate POVs | [vod-discovery](./skills/vod-discovery/) | `/vod-discovery` only |

With the plugin, prefix the name: `/osaskills:then-what`.

### Pinned Roblox library guides

Each library skill is an API guide for one pinned version: core API table, example, and version-specific gotchas. `resource.yaml` in each folder holds the exact identity. A project clones the ones it uses into its `.claude/skills/`.

| Skill | Library | Pin |
|---|---|---|
| [roblox-vide](./skills/roblox-resource-acquisition/libraries/roblox-vide/) | Vide (reactive UI) | 0.4.1 |
| [roblox-charm](./skills/roblox-resource-acquisition/libraries/roblox-charm/) | Charm (reactive state) | 0.11.1 |
| [roblox-ui-labs](./skills/roblox-resource-acquisition/libraries/roblox-ui-labs/) | UI Labs (story previews) | 1.6.1 |
| [roblox-bootstrapper](./skills/roblox-resource-acquisition/libraries/roblox-bootstrapper/) | Bootstrapper (startup lifecycle) | 1.2.2 |
| [roblox-janitor](./skills/roblox-resource-acquisition/libraries/roblox-janitor/) | Janitor (cleanup) | 1.18.3 |
| [roblox-lemonsignal](./skills/roblox-resource-acquisition/libraries/roblox-lemonsignal/) | LemonSignal (signals) | 2.0.0 |
| [roblox-blink](./skills/roblox-resource-acquisition/libraries/roblox-blink/) | Blink (networking IDL compiler) | 0.18.9 |
| [roblox-nevermore-ui](./skills/roblox-resource-acquisition/libraries/roblox-nevermore-ui/) | Nevermore Blend, Rx, Brio | Blend 12.50.2, Rx 13.34.2, Brio 14.37.2, loader 10.11.3 |

Use the guide only when your project pins the same version. Cloning a guide doesn't install the library or change your project's pins. Each guide's "Check the pin" section names the manifest entry and lock key it expects, and [library skills](./skills/roblox-resource-acquisition/references/library-skills.md) covers cloning them and comparing their pins with a project.

Agent-facing project files live in the project's agent directory: `.claude/` if it exists, otherwise `.agents/` if it exists, otherwise a new `.claude/`. The Roblox project guide goes in `<agent dir>/roblox/project.md` and VOD project notes in `<agent dir>/vod/project-context.md`. Adopted Roblox resources are listed in a marked block in the project's `CLAUDE.md`; their pins stay in the project's manifests and locks.

## Staying current

structure-roblox-projects and roblox-resource-acquisition each record in `versions.json` the release of every tool and library they pin (Rojo, Rokit, Wally, pesde, Lune, Lute, StyLua, Selene, Luau-LSP, Lest, ModuleLoader, and the bundled library guides) that their guidance was last reviewed against. The skills are updated on demand, not on a schedule.

- **When a task depends on a tool's version,** the agent compares your project's pin with that release. For a newer pin it checks the release notes for the claims the task uses and tells you; for an older one it confirms those claims at your version and warns you. It never changes your game project's pins to fit a skill. In a plugin install, a session-start hook notes `rokit.toml` and `aftman.toml` pins that differ, without network access.
- **When you ask** ("update rojo"), or accept the agent's offer after a task that found a gap, the agent reads the release notes, updates the skill, reruns its checks against the target version, and opens one pull request per item. A fix to a single claim gets its own `Fix <name>: <claim>` pull request. Pull requests need push access to this repository; other installs just report the gap.
- **Weekly,** the [Freshness workflow](./.github/workflows/freshness.yml) runs `check_updates.py` in CI and keeps an "Outdated skill pins" issue up to date for the maintainer.

design-roblox-ui has no `versions.json`: its [rendering guide](./skills/design-roblox-ui/references/rendering.md) names the rhr build it was checked against and where that build differs from Studio.

The plugin has no fixed version, so each commit is a new version. Turn on auto-update for this marketplace in `/plugin` → Marketplaces to receive merged updates automatically.

[CHANGELOG.md](./CHANGELOG.md) lists notable changes to the Roblox skills and their library catalog, and to bigger-picture, then-what and think-tank. A pull request that changes one of these skills or a library skill adds an entry to it.

## Scripts

Instruction-only skills need no setup. The Roblox resource checkers need Python 3.11+ and PyYAML. With [uv](https://docs.astral.sh/uv/) you don't need to install anything first:

```sh
uv run --no-project --python ">=3.11" --with pyyaml python .claude/skills/roblox-resource-acquisition/scripts/clone_children.py --help
```

Adjust the path to where the skill is installed. design-roblox-ui's scripts need Python 3.11+, and its contact sheet also Pillow, which `--with pillow` adds the same way; its renderer, rhr, installs as its [rendering guide](./skills/design-roblox-ui/references/rendering.md#install) describes. `vod-discovery` has its own environment; see its [setup guide](./skills/vod-discovery/references/setup.md).

## Repository checks

```sh
git clone https://github.com/osabased/osaskills.git
cd osaskills
uv venv --python 3.13
uv pip install -r skills/roblox-resource-acquisition/requirements-dev.txt -r skills/design-roblox-ui/requirements-dev.txt -r skills/vod-discovery/requirements.txt

# Roblox skills
uv run python -m pytest -q -ra skills/roblox-resource-acquisition/tests
uv run python -m pytest -q -ra skills/structure-roblox-projects/tests
uv run python -m pytest -q -ra skills/design-roblox-ui/tests

# VOD discovery (no footage, model downloads, or Premiere needed; ffmpeg must be on PATH)
uv run python -B -m unittest discover -s skills/vod-discovery/tests -p "test_*.py"
for t in skills/vod-discovery/tests/test_*.js; do node "$t"; done

# Plugin manifests
claude plugin validate .
```

The real-Rojo tests skip when `rojo` can't run (not on `PATH`, or a Rokit shim outside a Rokit project), and a skipped test is not real-build coverage. CI runs the test suites above, with Rojo 7.7.1 installed. None of these checks measure how well a skill triggers or how an agent performs with it; for that, see [`evals/`](./evals/) and the [resource-comparison guide](./skills/roblox-resource-acquisition/evals/README.md). The [2026-10-15 structure revamp](./evals/structure-revamp-2026-10-15/README.md) and [resource-acquisition revamp](./evals/resource-revamp-2026-10-15/README.md) evals compare each skill's old and new versions. The [bigger-picture eval](./evals/bigger-picture-2026-10-17/README.md) measures when that skill runs on its own in multi-turn sessions, and how long its output is. The [think-tank trap eval](./evals/think-tank-traps-2026-10-19/README.md) compares think-tank's panel with one Opus session on questions whose confident answer is wrong. The [2026-10-11 Sonnet with/without comparison](./evals/sonnet-ab-2026-10-11/README.md) measures triggering and answer quality with the current skills. The [2026-10-11 audit](./evals/rra-slim-2026-10-11/README.md) records the slimming of the two Roblox workflow skills and an old-versus-new comparison. The [plugin triggering check](./evals/plugin-trigger-2026-10-11/README.md) repeats the triggering test with the installed plugin, including that the user-only skills stay out of automatic use. The [2026-10-06 simplification review](./evals/skill-simplification-2026-10-06/README.md) is a historical snapshot that predates the Claude port and uses the old skill names. New evals import [`evals/_lib/isolation.py`](./evals/_lib/isolation.py), which keeps the user's `CLAUDE.md`, past session transcripts and installed skills out of headless runs and records the model id each run resolved to.

Every eval run also appends one row to [`evals/ledger.jsonl`](./evals/ledger.jsonl) through [`evals/_lib/ledger.py`](./evals/_lib/ledger.py): the date, the commit under test, the eval folder and results directory, the model and condition, the skills under test, how many trigger checks passed per skill, the judge score where the run was graded, and cost, duration and case count. The dated evals' harnesses append their rows when they finish, and `python evals/_lib/ledger.py backfill` built the rows for the runs before the ledger existed from their `results/` and `grading/` files. `python evals/_lib/ledger.py report` prints one line per run, newest last, grouped by eval folder, so a skill's trigger rate can be followed across evals. The standing subset in [`evals/gate/`](./evals/gate/) is the gate: a registration probe for every skill, three trigger prompts for each automatic skill plus negatives and slash checks for the user-only ones, all on Haiku with three runs per prompt, and three judged tasks graded by Sonnet against ground truth. Each run is compared with the last gate row for that model that the gate did not fail (every gate row carries `gate_ok`), so one regression keeps failing until the rate recovers instead of becoming the new baseline; a run narrowed to fewer cases writes its rows as `cond partial`, which the comparison never reads. A skill fails when its trigger pass rate drops by more than 0.2, and the judged score fails when it drops by more than 0.04 and its 95% upper bound sits below the earlier score, which needs at least two runs. The [eval gate workflow](./.github/workflows/eval-gate.yml) runs it when `skills/`, `hooks/`, `agents/` or `CLAUDE.md` change, uploads the ledger and results as an artifact, commits nothing back (so its baseline is the committed ledger), and skips with a notice while the repository has no `ANTHROPIC_API_KEY` secret. Locally, `python evals/gate/harness.py` runs the same subset against this checkout for under a dollar, appends the row and prints the decision.
