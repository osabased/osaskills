# Evidence and freshness

Use when you adopt, add, or upgrade a tool or library; rely on version-sensitive behavior you have not confirmed for the project's pinned version; make a current platform, compatibility, or recommendation claim; or find guidance that has drifted from the project. Running a project's already-pinned tools needs none of this.

This skill's references give navigation and compatibility context. They don't guarantee currentness.

## Match evidence to the claim

| Claim | Use |
| --- | --- |
| Project behavior or ownership | Implemented source, effective mappings, native manifests/locks/configuration, and available runtime evidence. A saved snapshot proves snapshot facts, not unseen live state. |
| Platform/tool behavior | Current canonical docs, source, and releases for the project's actual version and channel. Latest docs alone can't prove an older pin's behavior. |
| Recommended practice | Maintained primary guidance or inspectable implementations matched to the use case. Popularity and copied opinions are not enough; don't claim consensus without independent support. |

Keep observations, conventions, recommendations, and uncertainty distinct. A supported compatibility or correctness failure is a defect; several viable approaches are choices.

## Check a tool or library you are introducing

1. Resolve its canonical identity and the target version.
2. Read its canonical releases and the docs for the intended use. Separate stable releases from previews. If there is no stable release, note the maintained source and date instead of inventing a version.
3. Tell the user about task-relevant changes, incompatibilities, or lookups you could not make.

Check only what this task uses, not the whole dependency graph. Reuse a check already done in this task while its inputs are unchanged. A newer release does not authorize an upgrade. A failed lookup does not erase valid proof for an unchanged exact target. Unknown identity, a known incompatibility, or a hard defect still blocks dependent use.

If the project keeps a source-observation log (for example under `.roblox-resources/`), append the check to it. Older projects may still have `.agents/roblox/resources/`; move it to `.roblox-resources/`.

## Make a bounded recommendation

1. Resolve intended use, runtime and authoring environment, constraints, and deciding priorities from the request and the project. Ask only when a missing input could change the choice; keep researching meanwhile.
2. Compare plausible candidates against the same needs, using canonical behavior and release evidence. Check fit, compatibility, maintenance, platform availability, license, and replacement cost where they matter.
3. Recommend the supported fit with its deciding tradeoff, material uncertainty, and what would change it. Leave a genuinely open consequential choice to the user. Cite current claims with source, version or channel, and review date.

Keep an established, healthy package or tool manager. When acquiring or adopting a resource, use the `roblox-resource-acquisition` skill if it is installed ([SKILL.md](../../../roblox-resource-acquisition/SKILL.md)).

## Respond to drift

Reinspect affected guidance when mappings, ownership, startup, targets, dependency contracts, entry files, or commands change. A provisional observation, local exception, or failed lookup does not justify rewriting project-wide conventions. Propose guide corrections through the [project guide](../conventions/project-guide.md#save-it) workflow. Research grants no new write permission; keep project pins and passing proof whose inputs are unchanged.

## Starting sources

- Roblox: [Data model](https://create.roblox.com/docs/projects/data-model), [script locations](https://create.roblox.com/docs/scripting/locations), [Script Sync](https://create.roblox.com/docs/scripting/sync), [Studio testing](https://create.roblox.com/docs/studio/testing-modes), [client/server boundary](https://create.roblox.com/docs/scripting/security/client-server-boundary).
- Rojo: [versioned docs](https://rojo.space/docs/), [repository/releases](https://github.com/rojo-rbx/rojo), [changelog](https://github.com/rojo-rbx/rojo/blob/master/CHANGELOG.md) (more complete than rojo.space for fields added after 7.4).
- roblox-ts: [docs](https://roblox-ts.com/docs/), [usage](https://roblox-ts.com/docs/usage/), [repository](https://github.com/roblox-ts/roblox-ts).
- Other tools and frameworks: their maintained canonical docs, source, releases, and the project's adopted contract.
