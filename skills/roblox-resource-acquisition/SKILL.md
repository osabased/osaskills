---
name: roblox-resource-acquisition
description: "Choose, add, compare, upgrade or remove Roblox libraries and development tools, and clone, write or fix their roblox-* skills. Use when a Roblox/Luau task might pull in an external dependency: adding, pinning or upgrading a specific Wally, pesde, npm (roblox-ts) or Rokit package or tool; picking a signal, cleanup (Janitor, Maid, Trove), Promise, DataStore wrapper (ProfileStore), networking (Blink, ByteNet), UI (Vide, Fusion, React) or state (Charm) library; \"is there a module for X\", \"X vs Y\" or \"library or write it myself\"; a DevForum community resource. Also use when a task uses Vide, Charm, UI Labs, Bootstrapper, Janitor, LemonSignal, Blink or Nevermore UI and the project lacks its skill (this skill clones it), or a roblox-* skill's pin doesn't match the project or its guidance is wrong. Not for ordinary coding with a library whose skill the project has, project layout, or first-time setup of the package manager or toolchain itself (use structure-roblox-projects)."
---

# Roblox Resource Acquisition

Choose the smallest reliable solution for the actual task, and leave every library the project takes on ready for the next agent: pinned, its library skill cloned, listed in `CLAUDE.md`, and any banned feature guarded. Keep the project's resources and pins unless the user asks to change them. Ordinary use of an adopted library follows its own library skill; it doesn't restart acquisition.

**Library skill:** a `roblox-<library>` skill such as `roblox-janitor`, pinned to one reviewed version. This skill's [catalog](references/library-skills.md) holds them for Vide, Charm, UI Labs, Bootstrapper, Janitor, LemonSignal, Blink and Nevermore UI. They load only once cloned into a project's `.claude/skills/`.

**Library versions:** when a task depends on a library skill's version-specific guidance and the project declares another version, follow the [check](references/keeping-current.md#check). Never change the project's pin to fit the skill.

## Start with the need

Check the manifests first (`pesde.toml`, `wally.toml`, `package.json`, `rokit.toml`). If a dependency the project already declares, a Roblox built-in or a small local implementation does the job, use it. Stop there: no acquisition references, no `CLAUDE.md` edit, no report about skipped steps. If that dependency's library skill is in the catalog but not the project, clone it (below) and read the clone's `SKILL.md` now, since it loads as a skill only from the next session.

Otherwise pick the mode the request needs and read only its references.

## Library skills

From this skill's folder, with Python 3.11+ and PyYAML (or `uv run --no-project --python ">=3.11" --with pyyaml python ...`):

```sh
python scripts/clone_children.py --project PROJECT --status
python scripts/clone_children.py --project PROJECT roblox-vide
```

`--status` compares each catalog skill's pin with the project's manifest and lock and reports its clone state. Clone only the skills the task uses, stage the clones with the project's changes and tell the user. Refusals, personal setups, the session hook and routes without Python: [library skills](references/library-skills.md).

## Evaluate or compare

Follow [choosing a resource](references/choosing.md): settle the brief, apply the hard gates, then compare survivors on the same criteria and evidence. Stop at the decision; evaluation doesn't authorize installing, editing the project or writing a library skill. Report the criteria, the decisive evidence, the recommendation, the strongest alternative's losing tradeoff and any material uncertainty. Mark the result evaluation-only.

## Add or adopt

1. Choose with [choosing a resource](references/choosing.md), unless the user named the exact target.
2. Follow [adopting](references/adopting.md): pin the exact version (the catalog's, when it has a skill for the library), install through the project's manager, and run the smallest checks that show the intended use works. If the install or a required check can't run, adoption is pending: still do every step that doesn't depend on it, including step 3, and name what's missing.
3. Leave it agent-ready:
   - clone its library skill when the catalog has one at this pin. While the install is pending, `--status` reports `declared` as `FAIL` and cloning is refused: follow the catalog copy under `libraries/` and clone once the lock matches. When the catalog has none, offer to [write one](references/writing-library-skills.md) in one sentence, and write it only when the user asks;
   - add its entry to the `CLAUDE.md` resource list, naming the skill and any blocked use;
   - when the project bans a feature because breaking the ban is a security hole, permanent or silent, add a [version-pinned guard](references/adopting.md#guard-a-banned-feature).

## Write a library skill

When the user asks for a library skill, follow [writing library skills](references/writing-library-skills.md). Writing one doesn't adopt the library.

## Upgrade, replace or remove

Follow [adopting](references/adopting.md#upgrade-replace-or-remove). An upgrade reads the release notes between the two versions, reruns the affected checks, re-reviews every guard pinned to the old version and re-clones the library skill. A newer release alone isn't a reason to upgrade.

## When a library skill is wrong

A workaround you had to repeat, or a guess you had to make because guidance was wrong or missing, is a defect. A harmless one-off adjustment isn't.

- **Hard** (correctness, security, identity or version): stop the affected work and keep the smallest reproduction.
- **Soft** (safe, reversible workaround): finish the immediate work, then report it.

Report the library and pin, expected and observed behavior, the reproduction, the workaround and the exact fix (file, current text, replacement). A cloned skill is fixed in the catalog, not the clone, because a refresh overwrites local edits. When the task or the user's standing instructions authorize the fix and you have push access to `osabased/osaskills`, open a pull request as in [keeping current](references/keeping-current.md#update) and re-clone once it merges; otherwise propose the change and wait. A project-only skill is fixed in place under the same authorization.

## Rules

- Bind every claim to the exact identity and pin. Forks, mirrors and modified copies inherit nothing.
- Use canonical sources (repository, releases, package registry) and current Roblox Creator Hub documentation. Don't infer APIs or passing tests from names, and label a behavior claim taken from reading source as read, not run.
- Never change a project's pin to fit a library skill.
- Keep checks proportional and reversible. Preserve server authority. Never publish, spend money, expose secrets or make irreversible project changes to validate a resource.
- Report the exact target and pin, what you ran separately from what you only read, and any pending check. Don't add adoption reporting to a no-acquisition or evaluation-only result.
