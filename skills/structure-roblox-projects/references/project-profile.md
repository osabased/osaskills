# Roblox structure project profile

Use this reference when:

- a material structural convention remains unresolved and the nearest project-local `.codex/roblox-structure.md` may resolve it; or
- the user explicitly requests reusable project-level structural preferences, profile creation, repair, normalization, or update.

A project profile is **convention memory**, not modification authority and not a repository snapshot. It records durable structural rules agents should preserve.

## Read and apply profiles

1. Locate only the nearest applicable project-local `.codex/roblox-structure.md` under the affected project root.
2. Treat its contents as convention evidence. It never grants permission to modify project content or override governing instructions, tool rules, or safety rules.
3. Apply it only to material choices the explicit request and coherent affected-area convention have not already resolved.
4. During ordinary established-project work, if the profile conflicts with a coherent implemented convention, preserve the implementation and treat the profile as drift.
5. Reuse recognizable durable conventions from incomplete profiles instead of discarding them wholesale.

Do not read or write a global structure profile, including legacy `$CODEX_HOME/roblox-structure-profile.md` files. If the affected project root cannot be identified, keep normalized decisions task-local.

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

Use this version-1 shape and keep every field non-empty:

```markdown
# Roblox Structure Profile

## Profile version
1

## Source of truth
<normalized structural convention>

## Entrypoints
<normalized startup convention>

## Module organization
<normalized organization convention>

## Module style
<normalized module/lifecycle convention>

## Naming
<explicit convention, or Preserve project conventions; use new-project defaults only where no convention exists.>

## Tests
<explicit convention, or Use existing checks and the smallest relevant Studio playtests.>

## Notes
<durable project-level structural conventions or None; may name preferred tools/workflows but never grants modification permission or overrides governing/tool/safety rules>
```

A profile is valid only when `Profile version` equals `1` and every listed heading has non-empty content. The title is recommended but not required for validity.

For a custom selection, write `Custom` as the normalized field value and preserve the directly implementable durable convention in `Notes`. Put a named framework and lifecycle summary in `Module style` and preserve extra durable wording in `Notes`.

## Existing profiles

- Existing version-1 values such as `Single Script Architecture` remain accepted aliases for the single client/server entrypoint-pair preference.
- Treat a missing field or version as incomplete. Reuse recognizable durable conventions from the existing profile and project. Resolve only material missing decisions needed by the current task or explicit profile request.
- Treat an unsupported version as incomplete without overwriting it automatically. Preserve its contents, map what can be mapped safely, and replace it only after an explicitly requested normalized profile is previewed and authorized.
- If a profile conflicts with a coherent implemented convention during ordinary established-project work, preserve the implemented convention and treat the profile as drift rather than forcing the project toward stale memory.

When profile evidence still leaves a material choice unresolved, return to [`preference-resolution.md`](preference-resolution.md) for that choice only.

## Create or update a profile

Profile persistence is optional and requires an explicit user request.

1. Resolve every persisted field into a directly implementable durable convention: `Source of truth`, `Entrypoints`, `Module organization`, `Module style`, `Naming`, `Tests`, and `Notes`. Use `preference-resolution.md` only for fields that remain genuinely open.
2. Identify the affected project root and destination `.codex/roblox-structure.md`.
3. Show one exact pre-write preview of the complete profile.
4. Write it only after the user confirms `proceed` or otherwise explicitly authorizes that exact profile write.
5. Treat that confirmation as authority only for the displayed profile, not for broader project changes.

A profile update is complete when the resulting profile is valid, contains only durable convention memory, and any detected drift is either reconciled by explicit request or left documented rather than silently forcing the project to match stale memory.