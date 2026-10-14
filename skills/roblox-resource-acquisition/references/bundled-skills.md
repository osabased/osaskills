# Bundled Roblox resource skills

This skill's `libraries/` folder is a catalog of pinned child skills, one folder each. A project gets a child by cloning it into its `.claude/skills/`; the catalog itself loads nothing. Having a child available does not install the library in a project, adopt it, or prove it works there.

| Library and role | Child skill | Pin |
| --- | --- | --- |
| Vide: reactive UI and scope cleanup | [roblox-vide](../libraries/roblox-vide/SKILL.md) | 0.4.1 (commit `5ed4c01`) |
| Charm: reactive application state | [roblox-charm](../libraries/roblox-charm/SKILL.md) | 0.11.1 |
| UI Labs: story previews (Studio plugin) | [roblox-ui-labs](../libraries/roblox-ui-labs/SKILL.md) | 1.6.1 |
| Bootstrapper: startup lifecycle | [roblox-bootstrapper](../libraries/roblox-bootstrapper/SKILL.md) | 1.2.2 (commit `ff6700d`) |
| Janitor: resource cleanup | [roblox-janitor](../libraries/roblox-janitor/SKILL.md) | 1.18.3 |
| LemonSignal: custom events | [roblox-lemonsignal](../libraries/roblox-lemonsignal/SKILL.md) | 2.0.0 |
| Blink: networking schema compiler | [roblox-blink](../libraries/roblox-blink/SKILL.md) | 0.18.9 |
| Nevermore UI: Blend, Rx and Brio | [roblox-nevermore-ui](../libraries/roblox-nevermore-ui/SKILL.md) | Blend 12.50.2, Rx 13.34.2, Brio 14.37.2, loader 10.11.3 |

All eight use [child contract 1](child-authoring.md#resourceyaml). Each child's `resource.yaml` holds the exact identity, profile and integrity hashes. Read each child's advice-only or executable boundary before relying on it.

`structure-roblox-projects` is a separate project-structure skill, not a resource child.

## Clone a child into a project

1. Find the project's declared pin (`wally.toml`, `pesde.toml` or `package.json` and its lock). Use a child only when its pin matches. For another version, follow the parent's add, adopt or upgrade flow; never change the project's pin to fit a catalog child.
2. From this skill's folder, list each child's declaration and clone state, then clone the ones the task uses:

   ```sh
   python scripts/clone_children.py --project PROJECT --status
   python scripts/clone_children.py --project PROJECT roblox-vide roblox-charm
   ```

   It needs Python 3.11+ with PyYAML; `uv run --no-project --python ">=3.11" --with pyyaml python scripts/clone_children.py ...` supplies both. Each clone lands at `PROJECT/.claude/skills/<child>/`, and the script prints one JSON result per child.
3. Act on each result:
   - `cloned`, `refreshed` (with the changed files) or `current`: read the clone's `SKILL.md` and follow it. It loads as a skill from the next session on.
   - `refused` (exit 1): the folder holds a different skill, the project declares another version, or an existing clone targets another pin and the project's declaration of the catalog pin couldn't be confirmed. Report the reason and leave the folder as it is.
   - `declared` is the pin check. `UNAVAILABLE` still clones a missing child; say which check was skipped.
4. Commit the clones with the project, so every checkout and cloud session has them. Manifests, locks and fixtures stay in the project; the children carry no project state.
5. A refresh replaces the whole folder, so a local edit to a clone lasts only until the next refresh. Put fixes in the catalog and re-clone. `--status` reports a clone that differs from the catalog as `stale`, and the plugin's session hook names stale clones of declared libraries.

Without Python, copy the child's folder from `libraries/` into `PROJECT/.claude/skills/` whole. Without the plugin, the Skills CLI adds one child to a project from its root: `npx skills@latest add osabased/osaskills --full-depth --skill roblox-vide --agent claude-code` (`--full-depth` because the children are nested). In Cowork / claude.ai, upload a child folder as a zip; scripts may not run there, so children fall back to advisory mode. A child without the parent still works as advice and says which checks it skipped.

Older installs may use versioned names such as `roblox-vide-0-4-1`. Remove the old folder when you switch to the unversioned child, so the two don't compete.
