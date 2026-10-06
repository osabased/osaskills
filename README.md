## Skill catalogue

| Problem | Owning skill |
|---|---|
| My agent is having trouble turning findings and suggestions into a defensible, actionable proposal | [**consolidate**](./skills/consolidate/) |
| My agent is having trouble choosing or reassessing a consequential direction | [**direction-selection**](./skills/direction-selection/) |
| My agent is having trouble finding failures that emerge across interacting parts of a system | [**system-review**](./skills/system-review/) |
| My agent needs feedback on uncertain motion before costly production work | [**motion-studies**](./skills/motion-studies/) |
| My agent needs to understand an existing Roblox project or help set up a new one | [**structure-roblox-projects**](./skills/structure-roblox-projects/) |
| My agent needs to evaluate, adopt, or maintain Roblox libraries/modules and development tools | [**roblox-resource-acquisition**](./skills/roblox-resource-acquisition/) |
| I need to find useful moments across long VODs and prepare concise Premiere markers with relevant alternate POVs | [**vod-discovery**](./skills/vod-discovery/) |

## Bundled Roblox resource guidance

[roblox-resource-acquisition](./skills/roblox-resource-acquisition/) includes [eight pinned child packages](./skills/roblox-resource-acquisition/references/bundled-skills.md) under its `children/` directory, including Vide, Charm, UI Labs, Bootstrapper, Janitor, LemonSignal, Blink, and Nevermore's Blend/Rx/Brio guidance.

All eight children use [resource-child contract 1](./skills/roblox-resource-acquisition/references/resource-skill-contract.md): a compact `SKILL.md`, static `resource.yaml`, and conditional setup, API/lifecycle, and troubleshooting references. Nevermore keeps separate Blend, Rx and Brio API references and uses a shared npm verification profile. The parent owns shared usage rules and installation checks; the affected project's records own current verification and adoption state.

Generated children default to the active project's resolved `.agents/skills/<skill-name>/` location. Keep the distribution checkout outside host discovery; when installing the parent workflow, omit its `children/` directory and copy only selected child folders into their intended project scope. An explicitly requested global/user child remains supported. See the bundled catalog for pin matching, collision handling and validation boundaries. Bundled instruction files do not install Roblox packages or establish runtime or host verification.

## Quickstart: local Codex skills

These folders contain agent instructions and optional supporting files, not a running service. Start with one skill. The installation locations and invocation below follow [OpenAI's skill documentation](https://developers.openai.com/codex/skills/); they are not a claim of tested compatibility with every agent host.

### Install one skill

With Git and Python 3.11+ available, clone this repository into a new directory:

```sh
git clone https://github.com/osabased/osaskills.git
cd osaskills
```

Inspect the selected skill before installing it. From this checkout's root, this command copies the complete `direction-selection` folder into your user-level Codex skills directory:

```sh
python -c "from pathlib import Path; import shutil; src = Path('skills/direction-selection'); dst = Path.home() / '.agents' / 'skills' / src.name; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copytree(src, dst); print(dst / 'SKILL.md')"
```

The command refuses to overwrite an existing destination. For an update, review and back up any local edits before replacing that one skill folder. Updating this checkout does not update the installed copy.

Alternatively, copy the selected folder manually; Python is not needed to read or manually install instruction-only skills. Preserve the whole folder, including any `references/`, `scripts/`, `agents/`, and `templates/` subdirectories. The result must be `~/.agents/skills/direction-selection/SKILL.md`, not another nested `skills/` directory. For project-only use, put it at `<project-root>/.agents/skills/direction-selection/` instead. Avoid duplicate installations of the same skill. Use the home and filesystem of the environment running Codex; Windows and WSL installations are separate.

### Verify discovery and try it

In Codex CLI or the IDE extension, open `/skills` or type `$` and confirm that `direction-selection` is listed. If it is missing, check the directory layout and restart Codex. Select it and try this read-only task:

```text
Use $direction-selection. Help choose an approach for a shared inventory service.
Reliability and ease of maintenance matter most. Use the repository evidence,
compare credible alternatives, and recommend the next step. Do not edit files.
```

A sensible response alone does not prove that the host loaded the skill; check the skill selector and the loaded-skill trace when the host exposes one.

[Consolidate](./skills/consolidate/) uses [direction-selection](./skills/direction-selection/) when a proposal depends on a consequential unresolved choice. Install both skills to support that handoff.

## Scripts and repository checks

The resource validators require Python 3.11+ and PyYAML; the shared installation checker reads TOML with Python's standard library. From the checkout root, create an environment with uv and install the [runtime dependencies](./skills/roblox-resource-acquisition/requirements.txt):

```sh
uv venv --python 3.11
uv pip install -r skills/roblox-resource-acquisition/requirements.txt
```

For contribution checks, install the [test dependencies](./skills/roblox-resource-acquisition/requirements-dev.txt), then run the two suites separately:

```sh
uv pip install -r skills/roblox-resource-acquisition/requirements-dev.txt
uv run python -m pytest -q -ra skills/roblox-resource-acquisition/tests
uv run python -m pytest -q -ra skills/structure-roblox-projects/tests
```

The real-Rojo artifact test skips when `rojo` is not on `PATH`; the summary reports the reason. A skipped test is not real-build coverage. These Python checks do not test interactive Codex skill loading or measure agent performance. Run behavioral comparisons separately using the [resource-comparison](./skills/roblox-resource-acquisition/evals/README.md) or [direction-selection](./skills/direction-selection/evals/README.md) evaluation guide.

The [2026-10-06 simplification review](./evals/skill-simplification-2026-10-06/README.md) records the original/revised/no-skill advisory responses, validation results, and limits of that comparison.

The VOD discovery adapters and panel mock can be checked without footage, model downloads, or Premiere:

```sh
python -m unittest discover -s skills/vod-discovery/tests -p "test_*.py" -v
node skills/vod-discovery/tests/test_panel.js
```

See [VOD discovery setup](./skills/vod-discovery/references/setup.md) for media-processing dependencies and [validation notes](./skills/vod-discovery/references/validation.md) for the limits of the Premiere pilot.
