# Bundled Roblox resource skills

This repository ships pinned child skills beside this one, each in its own folder under `skills/`. Having a child available does not install the library in a project, adopt it, or prove it works there.

| Library and role | Child skill | Pin |
| --- | --- | --- |
| Vide: reactive UI and scope cleanup | [roblox-vide](../../roblox-vide/SKILL.md) | 0.4.1 (commit `5ed4c01`) |
| Charm: reactive application state | [roblox-charm](../../roblox-charm/SKILL.md) | 0.11.1 |
| UI Labs: story previews (Studio plugin) | [roblox-ui-labs](../../roblox-ui-labs/SKILL.md) | 1.6.1 |
| Bootstrapper: startup lifecycle | [roblox-bootstrapper](../../roblox-bootstrapper/SKILL.md) | 1.2.2 (commit `ff6700d`) |
| Janitor: resource cleanup | [roblox-janitor](../../roblox-janitor/SKILL.md) | 1.18.3 |
| LemonSignal: custom events | [roblox-lemonsignal](../../roblox-lemonsignal/SKILL.md) | 2.0.0 |
| Blink: networking schema compiler | [roblox-blink](../../roblox-blink/SKILL.md) | 0.18.9 |
| Nevermore UI: Blend, Rx and Brio | [roblox-nevermore-ui](../../roblox-nevermore-ui/SKILL.md) | Blend 12.50.2, Rx 13.34.2, Brio 14.37.2, loader 10.11.3 |

The links work in this repository and in installs where the children sit beside this skill. All eight use [child contract 1](child-authoring.md#resourceyaml). Each child's `resource.yaml` holds the exact identity, profile and integrity hashes. Read each child's advice-only or executable boundary before relying on it.

`structure-roblox-projects` is a separate project-structure skill, not a resource child.

## Pick and install a child

1. Find the project's declared pin (`wally.toml`, `pesde.toml` or `package.json` and its lock). Use a child only when its pin matches. For another version, follow the parent's `acquire/adopt` or `refresh` mode; never change the project's pin to fit a bundled child.
2. Install the child together with `roblox-resource-acquisition`, which supplies the shared checkers. A child installed alone still works as advice and says which checks it skipped.
   - **Claude Code plugin:** `/plugin marketplace add osabased/osaskills`, then `/plugin install osaskills@osaskills`. The plugin installs every skill side by side, so children always find this parent.
   - **Skills CLI:** from the project root, `npx skills@latest add osabased/osaskills --skill roblox-resource-acquisition roblox-vide --agent claude-code`. Add `--global` for `~/.claude/skills/`.
   - **Manual:** copy the whole child folder and the `roblox-resource-acquisition` folder into `<project>/.claude/skills/` (or `~/.claude/skills/` for every project). Keep references and scripts.
   - **Cowork / claude.ai:** upload each skill folder as a zip, or install the plugin. Scripts may not run there; children fall back to advisory mode.
3. Do not overwrite an unrelated existing skill with the same name; stop and report the collision.
4. Keep manifests, locks and fixtures in the project. The children carry no project state.
5. Installing files establishes placement only. A child is working once it appears in the skill list and `/<name>` invokes it.

Older installs may use versioned names such as `roblox-vide-0-4-1`. Remove the old folder when you switch to the unversioned child, so the two don't compete.
