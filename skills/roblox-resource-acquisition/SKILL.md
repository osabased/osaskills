---
name: roblox-resource-acquisition
description: "Choose, add, compare, pin, upgrade or troubleshoot third-party Roblox libraries and development tools. Use whenever a Roblox/Luau task might pull in an external dependency: adding or installing a Wally, pesde or npm (roblox-ts) package; picking a signal (GoodSignal, LemonSignal), cleanup (Janitor, Maid, Trove), Promise, ProfileStore/DataStore wrapper, networking (Blink, ByteNet), UI (Vide, Fusion, React-lua) or state (Charm) library; questions like \"is there a module for X\", \"X vs Y\" or \"library or write it myself\"; evaluating a DevForum community resource; setting up tools like Rojo, Rokit, Selene, StyLua or Lune; or refreshing a pinned version. Also use when a task uses Vide, Charm, UI Labs, Bootstrapper, Janitor, LemonSignal, Blink or Nevermore UI and the project lacks its skill (this skill clones it), or a roblox-* library skill reports a FAIL, a version mismatch or wrong guidance. Not for ordinary coding with a library whose skill the project has, or project layout (use structure-roblox-projects)."
---

# Roblox Resource Acquisition

Choose the smallest reliable solution for the actual task. Keep the project's chosen resources and pins unless the user asks to change them. Ordinary use of an adopted library follows its own child skill; it does not restart acquisition.

**Child skill:** a per-library skill such as `roblox-janitor`, with a `SKILL.md` and a static `resource.yaml` holding the exact pin. This skill's [catalog](references/bundled-skills.md) holds children for Vide, Charm, UI Labs, Bootstrapper, Janitor, LemonSignal, Blink and Nevermore UI. They load as skills only once cloned into a project's `.claude/skills/`. Having guidance available does not install or adopt the library.

**First, once per session:** run `python scripts/check_updates.py` from this skill's folder (cached for a day, no packages needed). If it prints `OUTDATED`, tell the user which library has a newer release, and after the task follow [keeping current](references/keeping-current.md). Skip silently if it can't run.

**From a library skill's pin check:** follow [child usage](references/child-usage.md), then return to that skill.

## Start with the need

Check the manifests first (`wally.toml`, `pesde.toml`, `package.json`, `rokit.toml`). If a dependency the project already declares, a Roblox built-in or a small local implementation does the job, use it and validate it. Stop there: no acquisition references, no `CLAUDE.md` edit, and no report about skipped steps. Use the dependency's child skill if the project has one. If it has none and the catalog has a child at the declared pin, clone it from this skill's folder with `python scripts/clone_children.py --project PROJECT roblox-<lib>`, then read the clone's `SKILL.md` and follow it, because it loads as a skill only from the next session. Clone only the children the task uses; on a refusal, see [cloning a child](references/bundled-skills.md#clone-a-child-into-a-project).

Otherwise pick the mode the request needs and read only its references.

## Evaluate or compare

Follow [choosing a resource](references/choosing.md): establish the intended use, apply the hard gates, then compare survivors on the same criteria and evidence. Stop at the decision. Evaluation does not authorize installing, editing the project or writing a child.

Report the criteria, the decisive evidence, the recommendation, the strongest alternative's losing tradeoff and any material uncertainty. Mark the result evaluation-only.

## Add, adopt or upgrade

1. Choose the resource with [choosing a resource](references/choosing.md), unless the user already named the exact target.
2. Follow [adopting](references/adopting.md): pin the exact version, install through the project's package or tool manager, run the smallest checks that show the intended use works, and update the project's resource list in `CLAUDE.md`.
3. If a required check cannot run, say adoption is pending and name the missing check. Installed files alone do not complete adoption.
4. **Child skill:** if the [catalog](references/bundled-skills.md) has a child at the adopted pin, clone it into the project. Otherwise offer one in a single sentence, and write it with [child authoring](references/child-authoring.md) only when the user asks, or when the same pinned resource is clearly reused across projects.

An upgrade is the same flow for a new pin: read the release notes between the two versions, rerun the checks the change affects, and update any child whose pin or guidance changed: a cloned child in the catalog, then re-clone it; a project-only child in place. A newer release alone is not a reason to upgrade.

## When a child's guidance is wrong

A workaround you had to repeat, or a guess you had to make because guidance was wrong or missing, is a defect. A harmless one-off local adjustment is not.

- **Hard** (correctness, security, identity or version): stop the affected work and keep the smallest reproduction.
- **Soft** (safe, reversible workaround): finish the immediate work, then report it.

Report the library and pin, expected and observed behavior, the smallest reproduction, the workaround and the exact proposed fix (file, current text, replacement). Edit the child only when the current task or the user's standing instructions authorize it; otherwise propose the change and wait. A cloned child's fix belongs in the catalog, because a refresh overwrites local edits to the clone. After a fix, rerun the check that failed.

## Shared rules

- Bind every claim to the exact identity and pin. Forks, mirrors and modified copies inherit nothing.
- Use canonical sources (repository, releases, package registry) and current Roblox Creator Hub documentation. Never infer APIs or passing tests from names or from reading source alone.
- Keep checks proportional and reversible. Preserve server authority and validate client input. Never publish, spend money, expose secrets or make irreversible project changes just to validate a resource.
- Say what you actually ran separately from what you only read. "Unverified" means not yet checked; "unavailable" names a check that cannot run here.

## Completion

Finish the requested decision or change. Report the exact target and pin, what was checked, and any limitation or pending check. Do not add adoption reporting to a no-acquisition or evaluation-only result.
