# osaskills

Skills for engineering, Roblox development, and VOD discovery.

## Install

```sh
npx skills@latest add osabased/osaskills
```

Use Node.js 22.20+ with npm/npx and Git. The [Skills CLI](https://github.com/vercel-labs/skills#readme) lets you select skills, agent hosts, and project or global scope. Run it from your project's root for a project installation.

List the available skills without installing:

```sh
npx skills@latest add osabased/osaskills --list
```

Install selected skills for Codex:

```sh
npx skills@latest add osabased/osaskills --skill consolidate system-review --agent codex
```

Add `--global` for availability across projects. On Windows, `--copy` selects copies when symlinks are unsuitable. Use the terminal of the environment running your agent; Windows and WSL installations are separate.

The CLI installs each selected skill's supporting files and records its source for updates:

```sh
npx skills@latest list
npx skills@latest update
```

Review local customizations before updating. Confirm availability in your agent's skill list; file placement and a sensible response alone do not prove that the host loaded the skill.

## Skill catalogue

| Problem | Owning skill |
|---|---|
| My agent left me with unfamiliar findings or open-ended choices, and I need a clear explanation and next step | [**consolidate**](./skills/consolidate/) |
| My agent is having trouble finding failures that emerge across interacting parts of a system | [**system-review**](./skills/system-review/) |
| My agent needs feedback on uncertain motion before costly production work | [**motion-studies**](./skills/motion-studies/) |
| My agent needs to understand an existing Roblox project or help set up a new one | [**structure-roblox-projects**](./skills/structure-roblox-projects/) |
| My agent needs to evaluate, adopt, or maintain Roblox libraries/modules and development tools | [**roblox-resource-acquisition**](./skills/roblox-resource-acquisition/) |
| I need to find useful moments across long VODs and prepare concise Premiere markers with relevant alternate POVs | [**vod-discovery**](./skills/vod-discovery/) |

Install `roblox-resource-acquisition` alongside `structure-roblox-projects` for the shared acquisition and maintenance workflow. The CLI does not infer this dependency.

## Bundled Roblox resource guidance

The [eight pinned resource skills](./skills/roblox-resource-acquisition/references/bundled-skills.md) live under [skills/roblox-resources/](./skills/roblox-resources/): Vide, Charm, UI Labs, Bootstrapper, Janitor, LemonSignal, Blink, and Nevermore's Blend/Rx/Brio guidance. Each is separately selectable in the installer.

Choose the child matching your project's adopted target and include its required parent, `roblox-resource-acquisition`. For example, from the project root:

```sh
npx skills@latest add osabased/osaskills --skill roblox-resource-acquisition roblox-vide-0-4-1 --agent codex
```

Installing the parent alone leaves the children uninstalled. Resource children use [resource-child contract 1](./skills/roblox-resource-acquisition/references/resource-skill-contract.md): a compact entrypoint, static `resource.yaml`, and conditional references. The parent supplies shared usage rules and installation checkers; project records own current verification and adoption state. Installing guidance does not install Roblox packages, change project pins, or complete runtime/host verification. See the bundled catalog for the applicable selection and adoption steps.

## Manual installation

For an agent host outside the CLI's supported set, clone this repository outside its skill-discovery directories and copy the complete selected skill folder into that host's documented skill location. Resource children are separate folders under `skills/roblox-resources/`; include their parent in an accessible skill scope. Preserve support files and avoid duplicate installations of the same skill.

## Scripts and repository checks

Instruction-only skills need no Python setup. Resource checker scripts additionally require Python 3.11+ and PyYAML. For a Codex project installation, install their [runtime dependencies](./skills/roblox-resource-acquisition/requirements.txt) with:

```sh
uv venv --python 3.11
uv pip install -r .agents/skills/roblox-resource-acquisition/requirements.txt
```

Use the actual installed parent path for a different scope or host.

For repository development, clone the checkout, install the [test dependencies](./skills/roblox-resource-acquisition/requirements-dev.txt), and run the suites separately:

```sh
git clone https://github.com/osabased/osaskills.git
cd osaskills
uv venv --python 3.11
uv pip install -r skills/roblox-resource-acquisition/requirements-dev.txt
uv run python -m pytest -q -ra skills/roblox-resource-acquisition/tests
uv run python -m pytest -q -ra skills/structure-roblox-projects/tests
```

The real-Rojo artifact test skips when `rojo` is not on `PATH`; the summary reports the reason. A skipped test is not real-build coverage. These Python checks do not test interactive skill loading or measure agent performance. Run behavioral comparisons separately using the [resource-comparison evaluation guide](./skills/roblox-resource-acquisition/evals/README.md).

The [2026-10-06 simplification review](./evals/skill-simplification-2026-10-06/README.md) records the original/revised/no-skill advisory responses, validation results, and limits of that comparison.

The VOD discovery adapters and panel mock can be checked without footage, model downloads, or Premiere:

```sh
python -m unittest discover -s skills/vod-discovery/tests -p "test_*.py" -v
node skills/vod-discovery/tests/test_panel.js
```

See [VOD discovery setup](./skills/vod-discovery/references/setup.md) for media-processing dependencies and [validation notes](./skills/vod-discovery/references/validation.md) for the limits of the Premiere pilot.
