# osaskills

Reusable agent skills for decision-making, review, preference discovery, and Roblox development. These folders contain instructions and optional supporting files, not a running service. Start with one skill.

## Skill catalogue

| Problem | Owning skill |
|---|---|
| My agent is having trouble making worthwhile codebase architecture improvements without speculative refactoring | [**architecture-improvement**](./skills/architecture-improvement/) |
| My agent is having trouble choosing or reassessing a consequential direction | [**direction-selection**](./skills/direction-selection/) |
| My agent is having trouble discovering and expressing the preferences that matter to my task | [**preference-discovery**](./skills/preference-discovery/) |
| My agent is having trouble finding failures that emerge across interacting parts of a system | [**system-review**](./skills/system-review/) |
| My agent is having trouble organizing the structure of my Roblox project | [**structure-roblox-projects**](./skills/structure-roblox-projects/) |
| My agent is having trouble finding, choosing, or managing a Roblox community resource | [**roblox-resource-acquisition**](./skills/roblox-resource-acquisition/) |

## Using these skills

Each skill has a `SKILL.md` entrypoint and may include supporting references, scripts, templates, or host metadata. Inspect the selected skill before use and preserve its complete folder when installing it.

Shared instructions refer to skills by plain name, such as `direction-selection`. Use your host's supported mechanism to load or invoke the named skill; a name in prose is not evidence that the skill was loaded. Codex-specific examples and metadata retain Codex invocation syntax.

For other agent environments, follow that host's documented installation and invocation instructions. Locations, discovery rules, metadata support, and available tools can differ. Some references still describe Codex-specific onboarding and paths; this repository does not claim tested compatibility with every host. Do not treat file placement or a sensible response alone as proof of native skill loading.

### Invocation and authority

A matching task can trigger a skill implicitly where the host supports it. [Architecture improvement](./skills/architecture-improvement/) is configured for explicit invocation and can make code changes after its intervention gate passes; an explicit review-only request keeps it read-only. For any skill, state the target and whether you want advice, review, or implementation. Installing a skill does not install Roblox tools, provide credentials, or authorize unrelated changes.

## Quickstart: local Codex skills

The installation locations and invocation below follow [OpenAI's skill documentation](https://developers.openai.com/codex/skills/). This section is specific to Codex.

### Install one skill

With Git and Python 3.10+ available, clone this repository into a new directory:

```sh
git clone https://github.com/osabased/osaskills.git
cd osaskills
```

Inspect the selected skill before installing it. From this checkout's root, this command copies the complete `preference-discovery` folder into your user-level Codex skills directory:

```sh
python -c "from pathlib import Path; import shutil; src = Path('skills/preference-discovery'); dst = Path.home() / '.agents' / 'skills' / src.name; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copytree(src, dst); print(dst / 'SKILL.md')"
```

The command refuses to overwrite an existing destination. For an update, review and back up any local edits before replacing that one skill folder. Updating this checkout does not update the installed copy.

Alternatively, copy the selected folder manually; Python is not needed to read or manually install instruction-only skills. Preserve the whole folder, including any `references/`, `scripts/`, `agents/`, and `templates/` subdirectories. The result must be `~/.agents/skills/preference-discovery/SKILL.md`, not another nested `skills/` directory. For project-only use, put it at `<project-root>/.agents/skills/preference-discovery/` instead. Avoid duplicate installations of the same skill. Use the home and filesystem of the environment running Codex; Windows and WSL installations are separate.

### Verify discovery and try it

In Codex CLI or the IDE extension, open `/skills` or type `$` and confirm that `preference-discovery` is listed. If it is missing, check the directory layout and restart Codex. Select it and try this read-only task:

```text
Use $preference-discovery. This draft feels too corporate:
"We are delighted to announce our innovative new inventory system."
Show two short alternatives and help me identify which qualities I want.
Do not edit files.
```

A sensible response alone does not prove that the host loaded the skill; check the skill selector and the loaded-skill trace when the host exposes one.

## Scripts and repository checks

The resource validators require Python 3.10+ and PyYAML. From the checkout root, install their [runtime dependencies](./skills/roblox-resource-acquisition/requirements.txt) in your chosen Python environment:

```sh
python -m pip install -r skills/roblox-resource-acquisition/requirements.txt
```

For contribution checks, install the [test dependencies](./skills/roblox-resource-acquisition/requirements-dev.txt), then run the two suites separately:

```sh
python -m pip install -r skills/roblox-resource-acquisition/requirements-dev.txt
python -m pytest -q -ra skills/roblox-resource-acquisition/tests
python -m pytest -q -ra skills/structure-roblox-projects/tests
```

The real-Rojo artifact test skips when `rojo` is not on `PATH`; the summary reports the reason. A skipped test is not real-build coverage. These Python checks do not test interactive skill loading in any host or measure agent performance. Run behavioral comparisons separately using the [resource-comparison](./skills/roblox-resource-acquisition/evals/README.md), [direction-selection](./skills/direction-selection/evals/README.md), or [preference-discovery](./skills/preference-discovery/evals/README.md) evaluation guide.
