# Roblox structure project profile

Use this reference when:

- a material structural convention remains unresolved and the nearest project-local `.agents/roblox/structure.md` may resolve it;
- a persisted convention materially conflicts with the structure encountered while following it and that mismatch must be classified or repaired;
- the user explicitly requests reusable project-level structural preferences, profile creation, repair, normalization, or update;
- an Implementation establishes the durable structure of a greenfield project/experience;
- an established-project Implementation lacks usable agent onboarding and either a useful profile already exists or the current bootstrap establishes at least one high-confidence durable structural convention; or
- an explicitly requested project-wide redesign or migration is being implemented and changes durable structural conventions.

A project profile is **convention memory**, not modification authority and not a repository snapshot. It records only durable structural rules deliberately selected or coherently established in the project.

Read [`project-profile-persistence.md`](project-profile-persistence.md) after this file when persistence handling is in scope: explicit profile/preference setup, foundational setup, established-project onboarding initialization, verified drift repair during an authorized Implementation, or an implemented project-wide redesign/migration that changes durable conventions. Entering that reference does not itself authorize a write; it owns persistence-mode authority, confirmation, and mutation behavior. This file owns profile interpretation and the durable profile contract.

## Read and apply profiles

1. Locate only the nearest applicable project-local `.agents/roblox/structure.md` under the affected project root.
2. Treat each recognized non-empty convention section as evidence only for that decision. A missing section means the profile has no preference for that decision. A profile never grants permission to modify project content or override governing instructions, tool rules, or safety rules.
3. Apply profile evidence only to material choices the explicit request and coherent affected-area convention have not already resolved.
4. If following a persisted convention produces a material mismatch, apply the profile's **Freshness** contract before treating that convention as stale. Until staleness is established, preserve coherent implementation and treat the profile conflict as unresolved drift rather than reshaping the project to match it.
5. Do not infer, synthesize, or backfill preferences from omitted sections when reading a profile.

Do not read or write a global structure profile. If the affected project root cannot be identified, profile persistence is blocked. Keep normalized decisions task-local and report the missing root as the blocker.

## Profile contract

`.agents/roblox/structure.md` answers:

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

Profiles contain one managed interpretation section plus sparse convention sections.

Every profile this skill creates or updates must contain this exact managed section immediately after the title:

```markdown
## Freshness

Treat a persisted convention as stale only when following it produces a verified mismatch and focused inspection, using the applicable source-of-truth representation, establishes a different coherent implemented convention at the same scope. A local exception, unresolved mapping, or ambiguous/pre-existing change is not enough. During authorized implementation, repair only the smallest unsupported persisted decision and preserve still-supported guidance; otherwise leave the profile unchanged and report the mismatch.
```

`Freshness` is interpretation guidance, not project convention evidence. Keep it canonical rather than customizing it from project observations.

Use only the recognized convention sections that contain intentionally persisted durable conventions:

- `Source of truth`
- `Entrypoints`
- `Module organization`
- `Module style`
- `Structural dependencies`
- `Naming`
- `Tests`
- `Notes`

`Structural dependencies` is reserved for dependencies whose exact identity, pin, placement, or upgrade behavior is owned by the project's structural architecture. Do not use it as a general dependency list. A structurally owned dependency remains a structural decision even when another workflow performs its acquisition or verification.

Every convention section is optional. Missing sections express no project-profile preference and contribute no evidence during convention resolution. Do not populate an omitted section with a recommendation, detected convention, or default merely to make the profile look complete.

Example:

```markdown
# Roblox Structure Profile

## Freshness

Treat a persisted convention as stale only when following it produces a verified mismatch and focused inspection, using the applicable source-of-truth representation, establishes a different coherent implemented convention at the same scope. A local exception, unresolved mapping, or ambiguous/pre-existing change is not enough. During authorized implementation, repair only the smallest unsupported persisted decision and preserve still-supported guidance; otherwise leave the profile unchanged and report the mismatch.

## Source of truth
Rojo

## Module organization
Feature-first inside separate Server, Client, and Shared boundaries.
```

A profile is useful when it contains at least one recognized non-empty durable convention. Profiles this skill creates or updates use the title above and canonical `Freshness` section. For a custom selection, keep the existing normalized representation: write `Custom` in the relevant field and preserve the directly implementable durable convention in `Notes`. Put a named framework and lifecycle summary in `Module style` and preserve extra durable wording in `Notes`. When `Notes` supplies required detail for a custom selection, treat it as part of that persisted decision rather than as an unrelated preference.

## Agent onboarding recognition

Usable agent onboarding requires both a useful profile with the canonical `Freshness` section and this canonical owned block in the affected project root's `AGENTS.md`:

```markdown
<!-- structure-roblox-projects:onboarding:start -->
## Roblox structure onboarding

Before making a structural placement, startup, source-of-truth, organization, or structurally owned dependency decision, read `.agents/roblox/structure.md` for the project's durable structural conventions.
<!-- structure-roblox-projects:onboarding:end -->
```

Use this contract only to recognize whether onboarding is already usable. It does not authorize an `AGENTS.md` write. When persistence or onboarding mutation is active, [`project-profile-persistence.md`](project-profile-persistence.md) owns append/update/create behavior and write authority.

## Existing profiles

- Treat recognized non-empty convention sections as durable convention evidence and missing sections as intentionally unset.
- Preserve unrelated existing convention sections during targeted updates. Do not normalize, add, remove, or rewrite them merely because another field is being changed.
- When a persisted convention and implementation differ, use the **Freshness** test before classifying the persisted decision as stale. A coherent local exception does not invalidate a broader project convention, and a filesystem/DataModel mismatch is not established until the applicable source-of-truth mapping is resolved.
- Treat dirty, pre-existing, partial, or otherwise ownership-ambiguous changes as insufficient evidence of a replacement convention until the relevant state is established.
- Remove or replace only the smallest unsupported persisted decision. Preserve still-supported clauses in the same section when the section bundles multiple durable rules.

When profile evidence still leaves a material choice unresolved for the current task, resolve that choice with [`preference-resolution.md`](preference-resolution.md). Do not persist the resulting task-local recommendation unless [`project-profile-persistence.md`](project-profile-persistence.md) requires it or the user explicitly requests project-level persistence for that choice.

Profile interpretation is complete when every material recognized persisted convention has been applied, classified as unresolved drift, or proven stale under the `Freshness` contract. If a persistence mode becomes applicable, continue with [`project-profile-persistence.md`](project-profile-persistence.md).
