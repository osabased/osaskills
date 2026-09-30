# Modification scope

Use this reference when explicit restrictions, ambiguous ownership/pre-existing changes, or broad/generated operations could take a write outside the requested outcome. The normal integration authority is defined in [SKILL.md](../../SKILL.md#feature-integration-and-implementation).

## Resolve the boundary

- **Necessary integration:** the minimum edits needed for the requested feature/change to work, including existing callers, shared entrypoints, mappings, configuration, and focused checks. These belong to the task unless an explicit restriction excludes them.
- **Context only:** adjacent material inspected for understanding, whose modification is unnecessary for the requested outcome. Leave it unchanged.
- **Restricted or uncertain:** explicitly excluded paths, ownership-ambiguous pre-existing work, or changes that materially expand the outcome (such as adopting a new framework to deliver an ordinary feature). Resolve that boundary before writing.

A file being shared, pre-existing, or outside a feature folder does not by itself require approval. Conversely, tool access, conventions, or a failing check do not override an explicit restriction or authorize unrelated repairs.

For example, “add inventory startup” normally includes wiring the existing bootstrap. “Implement inventory only under `Server/Inventory`; do not edit the bootstrap” excludes that write even when startup needs it. Report the precise required bootstrap edit instead of silently crossing the restriction or delivering a feature as fully integrated.

## Before broad or sensitive writes

1. Identify direct and indirect outputs, including mappings, manifests, pins, lockfiles, generated files, snapshots, profiles, and formatter output.
2. Inspect relevant status/diffs and preserve unrelated pre-existing work. If edits overlap and ownership cannot be established, resolve that uncertainty first.
3. Constrain generators, formatters, dependency operations, sync tools, and snapshot updates to intended outputs where possible. Inspect the resulting changes against that set.
4. Keep unrelated cleanup, dependency upgrades, and repairs outside the task.

## When a restriction blocks integration

Use an existing compatible extension point if it solves the task cleanly within the boundary. Otherwise identify the minimum blocked edit, why it is needed, the validation impact, and the approval or owner action required. Avoid adding lasting compatibility machinery merely to evade a simple restricted edit.

Scope resolution is complete when every necessary write is authorized or identified as a specific blocker. Continue independent authorized work; do not describe blocked integration as complete.

