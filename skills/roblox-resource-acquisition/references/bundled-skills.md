# Bundled Roblox resource skills

The distribution checkout has a `children/` directory containing portable, pinned resource guidance collected from the two Roblox UI projects. These folders are distribution artifacts. Their presence in this repository does not install a dependency, adopt it for another project, or establish runtime or host verification in that project.

| Resource role | Bundled package |
| --- | --- |
| Vide 0.4.1 reactive UI and scope cleanup | [roblox-vide-0-4-1](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-vide-0-4-1/SKILL.md) |
| Charm 0.11.1 reactive application state | [roblox-charm-0-11-1](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-charm-0-11-1/SKILL.md) |
| UI Labs 1.6.1 story previews | [roblox-ui-labs-1-6-1](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-ui-labs-1-6-1/SKILL.md) |
| Bootstrapper 1.2.2 startup lifecycle | [roblox-bootstrapper-1-2-2](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-bootstrapper-1-2-2/SKILL.md) |
| Janitor 1.18.3 resource cleanup | [roblox-janitor-1-18-3](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-janitor-1-18-3/SKILL.md) |
| LemonSignal 2.0.0 custom events | [roblox-lemonsignal-2-0-0](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-lemonsignal-2-0-0/SKILL.md) |
| Blink 0.18.9 schema compilation | [roblox-blink-0-18-9](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-blink-0-18-9/SKILL.md) |
| Nevermore UI with Blend 12.50.1, Rx 13.34.1 and Brio 14.37.1 | [roblox-nevermore-ui](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-nevermore-ui/SKILL.md) |

Nevermore uses one parent entrypoint with focused [Blend](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-nevermore-ui/references/blend.md), [Rx](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-nevermore-ui/references/rx.md) and [Brio](https://github.com/osabased/osaskills/blob/main/skills/roblox-resource-acquisition/children/roblox-nevermore-ui/references/brio.md) references. It is an existing companion skill with a narrower layout; it does not claim to satisfy every generated-child contract field. The seven other packages use the generated-resource contract. Read each package's actual verification boundary before relying on it.

`structure-roblox-projects` remains a separate project-structure parent under `skills/structure-roblox-projects/`; it is already distributed by this repository and is not a resource child.

## Select and install a child

1. Resolve the active project and its declared dependency pins. Choose only guidance that matches the canonical resource and reviewed target. For another target, use the parent workflow to validate an appropriate variant; do not silently upgrade the project to match a bundle.
2. Follow [project adoption](project-adoption.md#place-generated-project-skills) to resolve `<skill-scope-root>` and check destination ownership. Stage outside discovery when review or validation is still pending.
3. After applicable validation and installation authorization, copy the complete chosen folder from `children/<skill-name>/` into `<skill-scope-root>/.agents/skills/<skill-name>/`. Preserve its references and scripts. Refuse to overwrite an unrelated or ambiguous existing skill. Do not install every bundled resource merely because the parent is installed.
4. Resolve `<child-skill-directory>` and `<parent-skill-directory>` from the actual package locations when running child verification commands. Keep resource records, manifest/lock files, integration fixtures and their evidence in the active project. Bundled historical claims do not establish that project's current record or host state.
5. Complete the applicable [generation validation](generation-validation.md) and [host adoption](operational-lifecycle.md) checks before presenting the child as operational. Copying files establishes placement only.

When installing the parent workflow itself into a host's skill directory, omit `children/` from that parent copy. Keep the distribution checkout outside discovery and install selected children separately at the resolved project scope. This preserves explicit child selection regardless of how a host scans nested folders. The parent does not need the bundle for ordinary acquisition, generation or maintenance work.

Global/user installation is available only when explicitly requested for that scope. An unknown project root is not permission to fall back to a user-global child. Keep one canonical editable child per resolved scope and retain version-qualified names when projects adopt different targets.

Codex's supported local scopes and current-directory discovery are described in [official OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills). Actual host activation remains a separate proof step.
