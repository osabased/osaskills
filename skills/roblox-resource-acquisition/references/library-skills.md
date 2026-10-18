# Library skills

This skill's `libraries/` folder is a catalog of library skills: one `roblox-<library>` skill per library, each pinned to one reviewed version. A project gets one by cloning it into its `.claude/skills/`; the catalog itself loads nothing. Having a library skill doesn't install the library, adopt it, or prove it works in a project.

| Library and role | Skill | Pin |
| --- | --- | --- |
| Vide: reactive UI and scope cleanup | [roblox-vide](../libraries/roblox-vide/SKILL.md) | 0.4.1 (commit `5ed4c01`) |
| Charm: reactive application state | [roblox-charm](../libraries/roblox-charm/SKILL.md) | 0.11.1 |
| UI Labs: story previews (Studio plugin) | [roblox-ui-labs](../libraries/roblox-ui-labs/SKILL.md) | 1.6.1 |
| Bootstrapper: startup lifecycle | [roblox-bootstrapper](../libraries/roblox-bootstrapper/SKILL.md) | 1.2.2 (commit `ff6700d`) |
| Janitor: resource cleanup | [roblox-janitor](../libraries/roblox-janitor/SKILL.md) | 1.18.3 |
| LemonSignal: custom events | [roblox-lemonsignal](../libraries/roblox-lemonsignal/SKILL.md) | 2.0.0 |
| Blink: networking schema compiler | [roblox-blink](../libraries/roblox-blink/SKILL.md) | 0.18.9 |
| Nevermore UI: Blend, Rx and Brio | [roblox-nevermore-ui](../libraries/roblox-nevermore-ui/SKILL.md) | Blend 12.50.2, Rx 13.34.2, Brio 14.37.2, loader 10.11.3 |

Each skill's `resource.yaml` holds its exact pin and how a project declares it ([contract 2](writing-library-skills.md#resourceyaml)). Its `## Check the pin` section names the manifest entry and lock key that match, so it works without any script. Read each skill's advice-only or executable boundary before relying on it.

`structure-roblox-projects` is a separate skill, not a library skill.

## Clone into a project

From this skill's folder:

```sh
python scripts/clone_children.py --project PROJECT --status
python scripts/clone_children.py --project PROJECT roblox-vide roblox-charm
```

It needs Python 3.11+ with PyYAML; `uv run --no-project --python ">=3.11" --with pyyaml python scripts/clone_children.py ...` supplies both. It reads the project's manifest and lock and never runs anything from the project.

`--status` lists every catalog skill with:

- `pin`: the version or commit the catalog skill targets.
- `declared`: the project's manifest and lock compared with that pin, with a reason. `PASS` matches. `FAIL` means the project declares something else, and the reason names the entry. `UNAVAILABLE` means there was nothing to compare: no manifest, the library isn't declared, or the skill pins something outside the project, such as a Studio plugin file.
- `clone`: `missing`, `current`, `stale` (same pin, files differ from the catalog), `other-pin` (a clone of another version, described by `clone_pin` and `clone_declared`) or `foreign` (the folder holds a different skill).

Cloning writes `PROJECT/.claude/skills/<skill>/` and prints one JSON result per skill:

- `cloned`, `refreshed` (with the changed files) or `current`: read the clone's `SKILL.md` and follow it. It loads as a skill from the next session on.
- `refused` (exit 1): the folder holds a different skill, the project declares another version, or an existing clone targets another pin and the project doesn't declare the catalog's. Report the reason and leave the folder alone. Never change the project's pin to fit a catalog skill; to move the project to the catalog's version, [upgrade](adopting.md#upgrade-replace-or-remove).

An `UNAVAILABLE` comparison still clones; say which check was skipped.

Commit clones with the project, so every checkout and cloud session has them. When the project's agent setup is personal to one developer (structure-roblox-projects puts its onboarding pointer in `CLAUDE.local.md`), list each clone in the exclude file `git rev-parse --git-path info/exclude` names instead, and say other checkouts won't have it. A refresh replaces the whole folder, so a local edit lasts only until the next one: fix the catalog instead (see "When a library skill is wrong" in this skill's `SKILL.md`) and re-clone.

## The session hook

In a plugin install, a session-start hook runs `--status` on the project. It names clones to add or refresh (a declared library at the catalog pin without a current clone, or a clone that differs from the catalog) and cloned skills whose pin the project's manifest or lock contradicts. Act on it only for libraries the session's task uses. For a mismatch, keep the project's pin and follow the [check](keeping-current.md#check).

## Without Python or the plugin

Copy the skill's folder from `libraries/` into `PROJECT/.claude/skills/` whole. Without the plugin, the Skills CLI adds one skill from the project root: `npx skills@latest add osabased/osaskills --full-depth --skill roblox-vide --agent claude-code` (`--full-depth` because the skills are nested). In Cowork or claude.ai, upload the skill's folder as a zip. Each skill's `## Check the pin` works by reading the manifest and lock, so nothing else is needed.

Older installs may use versioned names such as `roblox-vide-0-4-1`. Remove the old folder when you switch to the unversioned skill, so the two don't compete.
