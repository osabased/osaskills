# Roblox structure project profile

Use this reference when:

- a material structural convention remains unresolved and the nearest project-local `.codex/roblox-structure.md` may resolve it;
- the user explicitly requests reusable project-level structural preferences, profile creation, repair, normalization, or update;
- an Implementation establishes the durable structure of a greenfield project/experience;
- an established-project Implementation lacks a usable local structure handoff and either a useful profile already exists or the current bootstrap establishes at least one high-confidence durable structural convention; or
- an explicitly requested project-wide redesign or migration is being implemented and changes durable structural conventions.

A project profile is **convention memory**, not modification authority and not a repository snapshot. It records only durable structural rules deliberately selected or coherently established in the project.

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
- Remove a persisted convention only when the user explicitly requests its removal or an implemented project-wide redesign/migration makes that persisted decision no longer applicable.

When profile evidence still leaves a material choice unresolved for the current task, resolve that choice with [`preference-resolution.md`](preference-resolution.md). Do not persist the resulting task-local recommendation unless a persistence mode below requires it or the user explicitly requests project-level persistence for that choice.

## Fresh-agent handoff

When durable project structure is persisted, also maintain a small discovery pointer in the affected project root's `AGENTS.md`. The profile remains the durable structural convention record; `AGENTS.md` only tells fresh agents that the profile exists and when to read it.

Use this owned block:

```markdown
<!-- structure-roblox-projects:start -->
## Roblox structure handoff

Before making a structural placement, startup, source-of-truth, or organization decision, read `.codex/roblox-structure.md` for the project's durable structural conventions.
<!-- structure-roblox-projects:end -->
```

Maintain it with these rules:

1. Use only the `AGENTS.md` at the affected project root for this handoff. Do not create or modify a global `AGENTS.md` or an unrelated nested project's instructions.
2. If project-root `AGENTS.md` already exists and the owned markers are absent, append the complete block after the existing content. Preserve all pre-existing content byte-for-byte except for any final newline needed to append cleanly.
3. If the owned markers already exist, update only the content between those markers when the canonical handoff changes. Preserve everything outside the markers.
4. If no project-root `AGENTS.md` exists, create one containing only the owned block.
5. Never replace, normalize, reorder, summarize, or otherwise rewrite an existing `AGENTS.md` to install this handoff. Similar human-authored Roblox guidance outside the owned markers is governing context, not content this skill owns.
6. Keep detailed structural conventions in `.codex/roblox-structure.md`; do not duplicate the profile into `AGENTS.md`.

For automatic established-project initialization, a **usable local structure handoff** requires both a useful profile and the canonical owned discovery block in the project-root `AGENTS.md`.

Task-local use of this skill must not create or modify `AGENTS.md` merely to advertise the skill or record transient findings. The established-project initialization mode below is the narrow automatic exception because it points fresh agents to durable convention memory established from existing project evidence.

## Persistence modes

Choose persistence from the user's requested scope and what is actually implemented:

- **Task-local work:** Review, design-only work, and ordinary established-project Implementation do not create or update the profile or handoff after a usable local structure handoff exists unless the user explicitly requests persistence or another persistence mode applies. The one-time established-project initialization below is the only automatic persistence exception for ordinary established-project Implementation.
- **Established-project handoff initialization:** during an already-authorized Implementation in an established project, initialize a missing usable local structure handoff without broadening discovery. If a useful profile already exists, leave its conventions unchanged and only install or refresh the owned `AGENTS.md` discovery block. Otherwise, when the current bootstrap has already established one or more high-confidence durable conventions from coherent implemented structure, create or minimally update the sparse profile with only those conventions and maintain the handoff. Do not inspect unrelated systems, resolve extra preferences, or persist recommendations/defaults solely to make the profile more complete. If the current bootstrap established no durable convention suitable for persistence, skip automatic initialization rather than create an empty profile or expand discovery.
- **Foundational setup:** when Implementation creates or sets up a greenfield project's durable structure, persist the durable conventions actually established by that implementation and maintain the fresh-agent handoff. This is part of completing the requested setup; it does not require a separate `remember this` request or an extra approval stop solely for persistence.
- **Implemented project-wide redesign or migration:** when the user explicitly requests and authorizes implementation of a project-wide redesign or migration and the completed target changes durable structural conventions, update only the affected persisted decisions and maintain the handoff. A review, proposal, design, or migration plan alone does not update durable guidance.
- **Explicit profile/preference setup:** when the user directly asks to create, update, repair, normalize, or persist project-level structural preferences, persist only the decisions included in that request.

Automatic persistence in established-project handoff initialization, foundational setup, or implemented project-wide redesign/migration is narrow modification authority for `.codex/roblox-structure.md` and the owned `AGENTS.md` block only. It does not authorize unrelated repository instructions or broader project changes. If either destination crosses an unclear, shared, generated, or protected write boundary, apply `../core/modification-scope.md` before writing.

## Create or update a profile

1. Determine the active persistence mode above. If none applies, keep the result task-local.
2. Identify the affected project root, destination `.codex/roblox-structure.md`, and project-root `AGENTS.md` handoff destination.
3. Build the smallest sparse profile required by that mode:
   - for established-project handoff initialization, leave an already useful profile unchanged; otherwise persist only high-confidence durable conventions already established by the current bootstrap, preserving unrelated existing profile content;
   - for foundational setup, include only durable conventions actually established by the implemented project structure;
   - for an implemented project-wide redesign/migration, update only persisted decisions the implemented target changed or invalidated, preserving every unrelated existing section;
   - for explicit profile/preference setup, persist only the requested decisions and omit every otherwise unset section.
4. Prepare the `AGENTS.md` handoff operation required by **Fresh-agent handoff**: append the owned block, update only the existing owned block, or create a minimal `AGENTS.md` when absent.
5. For established-project handoff initialization, foundational setup, and implemented project-wide redesign/migration, perform the applicable profile/handoff writes as part of the authorized Implementation once the durable outcome is known. Do not add a separate approval stop solely for these owned persistence writes.
6. For explicit profile/preference setup outside an already authorized Implementation, show one exact pre-write preview of the resulting sparse profile and handoff block, state whether `AGENTS.md` will be appended, the owned block updated, or a new file created, and write them only after the user confirms that persistence operation.
7. Treat every persistence write as authority only for the sparse profile decisions established by the active mode and the owned `AGENTS.md` block.

A profile update is complete when the resulting file contains only the applicable durable convention memory, unrelated persisted conventions remain unchanged, the project-root `AGENTS.md` points fresh agents to the profile without altering unrelated instructions, and any detected drift outside the active persistence scope is left documented rather than silently reconciled.
