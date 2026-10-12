# osaskills

Skills for Claude covering Roblox development, VOD discovery, and review workflows. They work in Claude Code and in Cowork / claude.ai.

## Install

### Claude Code plugin (recommended)

```text
/plugin marketplace add osabased/osaskills
/plugin install osaskills@osaskills
```

Recent Claude Code versions also accept `/plugin install osaskills --marketplace osabased/osaskills` as a single step. The plugin installs every skill side by side, so the Roblox library skills always find `roblox-resource-acquisition`. Plugin skills are namespaced, for example `/osaskills:then-what`.

### Cowork / Claude desktop

Open **Customize → Plugins → Add → Add marketplace**, enter `osabased/osaskills`, then install `osaskills`. You can also zip a single skill folder and upload it in the Skills section of Claude's settings. Before you upload `then-what`, `motion-studies` or `vod-discovery` as a zip, delete their `disable-model-invocation: true` line, because claude.ai uploads reject frontmatter keys outside the base skill spec. Scripts may not run in an uploaded skill; the Roblox library skills then fall back to advisory mode and tell you which checks they skipped.

### Skills CLI or manual copy

```sh
npx skills@latest add osabased/osaskills --agent claude-code
npx skills@latest add osabased/osaskills --skill roblox-resource-acquisition roblox-vide --agent claude-code
```

Run the command from your project root to install into `.claude/skills/`, or add `--global` for `~/.claude/skills/`. `--list` shows the available skills. To install by hand, copy whole skill folders from `skills/` into either location. Keep each folder intact, and put Roblox library skills next to `roblox-resource-acquisition`.

Check that Claude actually loaded a skill: it should appear under `/skills`, and `/<name>` should run it.

## Skill catalogue

| Problem | Skill | Invocation |
|---|---|---|
| An agent left you with findings or open-ended choices, and you need a clear recommendation and next step | [then-what](./skills/then-what/) | `/then-what` only |
| A failure or risk depends on how parts of a system interact (retries, partial failures, ordering, handoffs) | [system-review](./skills/system-review/) | automatic or `/system-review` |
| You want to preview an uncertain animation before production work | [motion-studies](./skills/motion-studies/) | `/motion-studies` only |
| You need to understand an existing Roblox project, place code correctly, set up Rojo or Script Sync, or start a new project | [structure-roblox-projects](./skills/structure-roblox-projects/) | automatic |
| You want to choose, add, compare, or upgrade a Roblox library or development tool | [roblox-resource-acquisition](./skills/roblox-resource-acquisition/) | automatic |
| You need to find moments across long VODs and prepare Premiere markers or a review timeline with alternate POVs | [vod-discovery](./skills/vod-discovery/) | `/vod-discovery` only |

With the plugin, prefix the name: `/osaskills:then-what`.

### Pinned Roblox library guides

Each library skill is an API guide for one pinned version: core API table, example, and version-specific gotchas. `resource.yaml` in each folder holds the exact identity.

| Skill | Library | Pin |
|---|---|---|
| [roblox-vide](./skills/roblox-vide/) | Vide (reactive UI) | 0.4.1 |
| [roblox-charm](./skills/roblox-charm/) | Charm (reactive state) | 0.11.1 |
| [roblox-ui-labs](./skills/roblox-ui-labs/) | UI Labs (story previews) | 1.6.1 |
| [roblox-bootstrapper](./skills/roblox-bootstrapper/) | Bootstrapper (startup lifecycle) | 1.2.2 |
| [roblox-janitor](./skills/roblox-janitor/) | Janitor (cleanup) | 1.18.3 |
| [roblox-lemonsignal](./skills/roblox-lemonsignal/) | LemonSignal (signals) | 2.0.0 |
| [roblox-blink](./skills/roblox-blink/) | Blink (networking IDL compiler) | 0.18.9 |
| [roblox-nevermore-ui](./skills/roblox-nevermore-ui/) | Nevermore Blend, Rx, Brio | Blend 12.50.1, Rx 13.34.1, Brio 14.37.1, loader 10.11.2 |

Use the guide only when your project pins the same version. Installing a guide doesn't install the library or change your project's pins. The [bundled catalogue](./skills/roblox-resource-acquisition/references/bundled-skills.md) has the selection rules.

Agent-facing project files live in the project's agent directory: `.claude/` if it exists, otherwise `.agents/` if it exists, otherwise a new `.claude/`. The Roblox project guide goes in `<agent dir>/roblox/project.md` and VOD project notes in `<agent dir>/vod/project-context.md`. Adopted Roblox resources are listed in a marked block in the project's `CLAUDE.md`; their pins stay in the project's manifests and locks.

## Staying current

The Roblox workflow skills track the latest stable release of every tool and library they pin (Rojo, Rokit, Wally, pesde, Lune, Lute, StyLua, Selene, Luau-LSP, Lest, ModuleLoader, and the bundled library guides). Each skill's `versions.json` records what its guidance was last reviewed against.

- **When an agent uses the skills,** it runs `scripts/check_updates.py` (cached for a day). In a plugin install, a session-start hook runs the same check and tells the agent only when something is outdated.
- **When something is outdated,** the agent mentions it, finishes your task, then reads the release notes, updates the skill, reruns its checks against the new version, and opens one pull request per item. It never changes your game project's pins for this. Pull requests need push access to this repository; other installs just report the outdated item.
- **Weekly,** the [Freshness workflow](./.github/workflows/freshness.yml) runs the same check in CI and keeps an "Outdated skill pins" issue up to date.

The plugin has no fixed version, so each commit is a new version. Turn on auto-update for this marketplace in `/plugin` → Marketplaces to receive merged updates automatically.

## Scripts

Instruction-only skills need no setup. The Roblox resource checkers need Python 3.11+ and PyYAML. With [uv](https://docs.astral.sh/uv/) you don't need to install anything first:

```sh
uv run --no-project --python ">=3.11" --with pyyaml python .claude/skills/roblox-resource-acquisition/scripts/check_resource_install.py --help
```

Adjust the path to where the skill is installed. `vod-discovery` has its own environment; see its [setup guide](./skills/vod-discovery/references/setup.md).

## Repository checks

```sh
git clone https://github.com/osabased/osaskills.git
cd osaskills
uv venv --python 3.13
uv pip install -r skills/roblox-resource-acquisition/requirements-dev.txt -r skills/vod-discovery/requirements.txt

# Roblox skills
uv run python -m pytest -q -ra skills/roblox-resource-acquisition/tests
uv run python -m pytest -q -ra skills/structure-roblox-projects/tests

# VOD discovery (no footage, model downloads, or Premiere needed; ffmpeg must be on PATH)
uv run python -B -m unittest discover -s skills/vod-discovery/tests -p "test_*.py"
for t in skills/vod-discovery/tests/test_*.js; do node "$t"; done

# Plugin manifests
claude plugin validate .
```

The real-Rojo tests skip when `rojo` can't run (not on `PATH`, or a Rokit shim outside a Rokit project), and a skipped test is not real-build coverage. CI runs the test suites above, with Rojo 7.7.1 installed. None of these checks measure how well a skill triggers or how an agent performs with it; for that, see [`evals/`](./evals/) and the [resource-comparison guide](./skills/roblox-resource-acquisition/evals/README.md). The [2026-10-11 Sonnet with/without comparison](./evals/sonnet-ab-2026-10-11/README.md) measures triggering and answer quality with the current skills. The [2026-10-11 audit](./evals/rra-slim-2026-10-11/README.md) records the slimming of the two Roblox workflow skills and an old-versus-new comparison. The [plugin triggering check](./evals/plugin-trigger-2026-10-11/README.md) repeats the triggering test with the installed plugin, including that the user-only skills stay out of automatic use. The [2026-10-06 simplification review](./evals/skill-simplification-2026-10-06/README.md) is a historical snapshot that predates the Claude port and uses the old skill names.
