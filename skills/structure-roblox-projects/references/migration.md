# Moves and migrations

Use the full workflow only when the user asks for a migration, conversion or migration plan. Ordinary moves, renames and restructures use only the tracing, write-scope and check items they can trip.

## Trace what a move can break

- `require` calls and string paths;
- loader and discovery conventions;
- Remote and Bindable lookups;
- callers and tests;
- script attributes and tags;
- Rojo project, meta and model mappings;
- `script.Parent` and other ancestry or sibling traversal;
- `script.Name`, `GetFullName()`, and registrations derived from names or paths;
- topology- or identity-sensitive discovery.

Read the specialist reference when the current or target structure crosses its boundary: [Rojo](rojo.md), [Script Sync](script-sync.md), [engine modes](engine-modes.md), [SSA](ssa.md). For a sync tool, compiler or loader none of them describes, trace its mapping and discovery from its [contract](unfamiliar-stack.md).

## Write scope

- **Necessary:** the minimum edits the change needs to work, including existing callers, shared entrypoints, mappings, config and focused checks. These belong to the task unless the user excluded them.
- **Context only:** material read for understanding. Leave it unchanged.
- **Restricted or uncertain:** paths the user excluded, pre-existing work of unclear ownership, or changes that expand the outcome (adopting a framework to deliver a feature). Resolve these before writing.

A file being shared or outside the feature folder doesn't need approval; tool access or a failing check doesn't override a restriction. For example, "add inventory startup" includes wiring the existing bootstrap, but "implement inventory only under `Server/Inventory`; don't edit the bootstrap" excludes it. Do the allowed part, then report the exact bootstrap edit still needed rather than crossing the restriction or calling the feature integrated. Use an existing extension point if it solves the task cleanly; don't build compatibility machinery to dodge a simple restricted edit.

Before broad writes (formatters, generators, dependency operations, syncback, snapshot updates): list every output they can touch, check `git status` and keep unrelated pre-existing work, constrain the tool to the intended paths, and review the result against that list. Keep unrelated cleanup and upgrades out of the task.

## Plan an explicit migration

Inventory the current and target hierarchies, the mappings, the entrypoints and every move. Plan in slices, each moving one concept once with the references it needs to keep working. Record for each slice:

- current and target path;
- affected callers, `require`s, Remotes, mappings, config and tests;
- the source of truth before and after, and the cutover step that prevents two owners;
- owner actions, the recovery boundary, and the check that closes it.

Items that don't move but need reference or topology updates still belong in a slice. If a field is unknown, name the evidence needed instead of writing "update references". Git is enough recovery for reversible file edits it fully captures; destructive, Studio-only or external-state changes need an explicit recovery step.

For a source-of-truth migration (Studio to Rojo, Script Sync to Rojo), name when writes freeze in the old owner, how its final state is captured, which side wins a conflict, when the new owner takes over, and how to return without split edits. Installing a tool or a first successful sync is not the cutover. A slice that needs a write the user hasn't authorized is blocked: state the owner action rather than leaving a topology that can't work.

The plan is complete when every move, affected reference, owner action, specialist boundary, check and needed recovery step is accounted for.

## Check

Check only what the change can break: dependency cycles, authoritative logic or data newly replicated, startup, discovery and registration, sync representation and metadata, mapping topology, and engine-mode boundaries. After topology- or identity-sensitive moves, exercise discovery in a play-test when one is available, and run a client/server path when entrypoints, Remotes or replicated state changed ([verification](verification.md)).
