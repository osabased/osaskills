# Roblox structure project profile

Use this reference when:

- a material structural convention remains unresolved and the nearest project-local `.codex/roblox-structure.md` may resolve it; or
- the user explicitly requests reusable project-level structural preferences, profile creation, repair, normalization, or update.

A project profile is **convention memory**, not modification authority and not a repository snapshot. It records only durable structural rules intentionally persisted for the project.

## Read and apply profiles

1. Locate only the nearest applicable project-local `.codex/roblox-structure.md` under the affected project root.
2. Treat each recognized non-empty section as convention evidence only for that decision. A missing section means the profile has no preference for that decision. A profile never grants permission to modify project content or override governing instructions, tool rules, or safety rules.
3. Apply profile evidence only to material choices the explicit request and coherent affected-area convention have not already resolved.
4. During ordinary established-project work, if a persisted convention conflicts with a coherent implemented convention, preserve the implementation and treat the profile as drift.
5. Do not infer, synthesize, or backfill preferences from omitted sections when reading a profile.

Do not read or write a global structure profile, including legacy `$CODEX_HOME/roblox-structure-profile.md` files. If the affected project root cannot be identified, profile persistence is blocked. Keep normalized decisions task-local and report the missing root as the blocker.

## Profile contract

`.codex/roblox-structure.md` answers:

> What structural rules should agents preserve?

It does not answer:

> What did the repository look like the last time an agent inspected it?

Do not persist:

- current task scope or modification authority;
- exact dependency graphs;
- current Remote or Bindable inventory;
- transient file-layout details;
- task-specific startup traces;
- task-specific bootstrap findings;
- temporary risks, blockers, or validation observations.

Profiles are sparse. Use only the recognized sections that contain intentionally persisted durable conventions:

- `Source of truth`
- `Entrypoints`
- `Module organization`
- `Module style`
- `Naming`
- `Tests`
- `Notes`

Every section is optional. Missing sections express no project-profile preference and contribute no evidence during convention resolution. Do not populate an omitted section with a recommendation, detected convention, or default merely to make the profile look complete.

Example:

```markdown
# Roblox Structure Profile

## Source of truth
Rojo

## Module organization
Feature-first inside separate Server, Client, and Shared boundaries.
```

A profile is useful when it contains at least one recognized non-empty durable convention. The title is recommended but not required. For a custom selection, keep the existing normalized representation: write `Custom` in the relevant field and preserve the directly implementable durable convention in `Notes`. Put a named framework and lifecycle summary in `Module style` and preserve extra durable wording in `Notes`. When `Notes` supplies required detail for a custom selection, treat it as part of that persisted decision rather than as an unrelated preference.

## Existing profiles

- Treat recognized non-empty sections as durable convention evidence and missing sections as intentionally unset.
- Preserve unrelated existing sections during targeted updates. Do not normalize, add, remove, or rewrite them merely because another field is being changed.
- If a persisted convention conflicts with a coherent implemented convention during ordinary established-project work, preserve the implemented convention and treat the profile as drift rather than forcing the project toward stale memory.
- Remove a persisted convention only when the user explicitly requests its removal or explicitly requests a broader profile rewrite that includes that decision.

When profile evidence still leaves a material choice unresolved for the current task, resolve that choice with [`preference-resolution.md`](preference-resolution.md). Do not persist the resulting task-local recommendation unless the user explicitly requests project-level persistence for that choice.

## Fresh-agent handoff

When durable project structure is intentionally persisted, also maintain a small discovery pointer in the affected project root's `AGENTS.md`. The profile remains the structural source of truth; `AGENTS.md` only tells fresh agents that the profile exists and when to read it.

Use this owned block:

```markdown
<!-- structure-roblox-projects:start -->
## Roblox structure handoff

Before making a structural placement, startup, source-of-truth, or organization decision, read `.codex/roblox-structure.md` and preserve its applicable durable conventions together with coherent implemented project structure.

Do not treat moves, renames, topology changes, or restructuring as a migration unless the user explicitly requests the migration/transition/conversion itself or migration planning.
<!-- structure-roblox-projects:end -->
```

Maintain it with these rules:

1. Use only the `AGENTS.md` at the affected project root for this handoff. Do not create or modify a global `AGENTS.md` or an unrelated nested project's instructions.
2. If project-root `AGENTS.md` already exists and the owned markers are absent, append the complete block after the existing content. Preserve all pre-existing content byte-for-byte except for any final newline needed to append cleanly.
3. If the owned markers already exist, update only the content between those markers when the canonical handoff changes. Preserve everything outside the markers.
4. If no project-root `AGENTS.md` exists, create one containing only the owned block.
5. Never replace, normalize, reorder, summarize, or otherwise rewrite an existing `AGENTS.md` to install this handoff. Similar human-authored Roblox guidance outside the owned markers is governing context, not content this skill owns.
6. Keep detailed structural conventions in `.codex/roblox-structure.md`; do not duplicate the profile into `AGENTS.md`.

The handoff block is maintained only as part of an authorized durable profile creation/update. Task-local use of this skill must not create or modify `AGENTS.md` merely to advertise the skill or record transient findings.

## Create or update a profile

Profile persistence is optional and requires an explicit user request.

1. Determine what durable convention memory the user intends to persist.
   - For a targeted request such as `remember that this project uses Rojo`, persist only the requested decision.
   - For an explicit broader profile setup, resolve only the durable decisions intentionally included in that setup. Use `preference-resolution.md` only for included decisions that remain genuinely open.
2. Identify the affected project root, destination `.codex/roblox-structure.md`, and project-root `AGENTS.md` handoff destination.
3. When updating an existing profile, preserve every unrelated existing section. When creating a profile, omit every unrequested or otherwise intentionally unset section.
4. Prepare the resulting sparse profile and the `AGENTS.md` handoff operation required by **Fresh-agent handoff**: append the owned block, update only the existing owned block, or create a minimal `AGENTS.md` when absent.
5. Show one exact pre-write preview of the resulting profile and the exact handoff block. State whether `AGENTS.md` will be appended, the owned block updated, or a new file created; never present replacement of an existing `AGENTS.md` as an allowed operation.
6. Write them only after the user confirms `proceed` or otherwise explicitly authorizes that exact durable persistence operation.
7. Treat that confirmation as authority only for the displayed profile and owned `AGENTS.md` handoff block, not for broader project changes.

A profile update is complete when the resulting file contains only the intended durable convention memory, unrelated persisted conventions remain unchanged, the project-root `AGENTS.md` points fresh agents to the profile without altering unrelated instructions, and any detected drift outside the requested update is left documented rather than silently reconciled.
