# Project resource adoption

Use this when a resource becomes, stops being, or changes as a project-standard dependency, when another project document fixes the resource target, or when the project's resource list in CLAUDE.md must change.

This file owns project-use state, the CLAUDE.md resource list, project conflicts and where project children go. Trust and verification live in [state policy](state-policy.md); child validation in [generation and validation](generation-validation.md); installing children in [installing children](operational-lifecycle.md).

## Establish project-use authority

Before changing a project-standard resource, find out who owns that choice.

- **This skill owns it:** this workflow selected the resource, or was explicitly told to make it the project standard for the stated role. It may maintain that choice within the authorized scope.
- **Someone else owns it:** another durable project document or skill already fixes the resource, its pin, role, replacement or upgrade. Copy that authority into `project_use.authority`. This workflow may acquire, inspect, verify, record evidence and write guidance for that target, but must not substitute, retarget, upgrade or retire it on its own.

For example, `structure-roblox-projects` owns the ModuleLoader identity, pin, placement and upgrade decision for its Canonical SSA layout; treat that loader as a fixed target.

Trust and project-use authority are different claims. `trust.basis: project` says project policy trusts the resource identity; `project_use.authority` says which document controls whether it is the standard choice for its role.

## Check for conflicts before changing anything

Read the project's `CLAUDE.md` (and files it imports with `@path`) and any project guidance it points to that could choose a resource for the same role, such as the structure guide at `AGENT_DIR/roblox/project.md`.

A conflict exists only when existing guidance and the proposed use pick incompatible resources for the **same role and scope**. Adjacent capabilities are not conflicts. When one exists:

1. show the user the conflicting guidance and the proposed resource;
2. leave the existing project-use state and resource list unchanged; and
3. continue only after the user or the owning document resolves it.

Never overwrite human-written instructions, another skill's owned block or another authority's target.

## Record project use

Records use the location in [state policy](state-policy.md#portable-resource-record-location). Every current record has a `project_use` mapping:

- `status`: `adopted`, `retired` or `not-applicable`;
- `role`: short durable role;
- `scope`: project-relative scope the role applies to;
- `authority`: the workflow or document that owns the choice.

`adopted` means future sessions should treat the resource as the standard choice for that role. `retired` keeps a former choice auditable and removes it from the active list. `not-applicable` means the record is evidence or candidate state.

Keep project use independent of verification and child state. An adopted resource stays adopted while its verification or child is blocked; the resource list must then show the affected use as blocked.

## Maintain the resource list in CLAUDE.md

When at least one record has `project_use.status: adopted`, keep this owned block in the project root's `CLAUDE.md`:

```markdown
<!-- roblox-resource-acquisition:onboarding:start -->
## Roblox resources

Use the project-standard resources below for their listed roles. If a choice conflicts with other project guidance, raise the conflict before changing either.

- **RESOURCE** — ROLE. [Optional authority note.] [Optional "Use the `SKILL-NAME` skill." when that child is installed.]
<!-- roblox-resource-acquisition:onboarding:end -->
```

Rules:

1. Edit only the project root's `CLAUDE.md`. If the project keeps its instructions in another file that `CLAUDE.md` imports (for example `@AGENTS.md`), you may put the block there instead; the import makes it visible. Do not edit a user-wide or unrelated project's instructions.
2. If the markers are absent, append the whole block after the existing content.
3. If the markers exist, change only the content between them.
4. If no `CLAUDE.md` exists, create one containing only the block.
5. List adopted resources only. Do not copy versions, provenance, verification history or API guidance into the block; the record and child hold those.
6. Name the owner only when that prevents ambiguity, for example: `Structural selection is governed by .claude/roblox/project.md.` (the structure skill's guide at `AGENT_DIR/roblox/project.md`)
7. Add "Use the `<child>` skill." only when that child is installed for this project (or user-wide on request). A missing or broken child does not remove an otherwise valid choice.
8. When the resource is blocked for its adopted use, keep the entry but mark that use blocked and point to repair.
9. Remove the block entirely when no adopted resources remain, leaving everything else untouched.

An authorized adoption that establishes or changes a project-standard dependency also authorizes the matching record and owned-block writes once the conflict check passes. Do not add a separate confirmation just for those writes.

## Nested projects

Claude Code loads `CLAUDE.md` from the working directory and its parents at startup, and loads a nested project's `CLAUDE.md` when it works with files inside that folder. If sessions usually start above a nested Roblox project, the nested project's block may not be loaded at startup. When an ancestor `CLAUDE.md` is within the authorized write scope, add one pointer line, for example: `For Roblox resource work under <path>/, read <path>/CLAUDE.md before choosing or changing project-standard resources.` Otherwise report the limitation instead of claiming future sessions will see the list.

## Place project children

Children are opt-in (see [adoption policy](adoption-policy.md#scope-and-autonomy)). When one is requested:

- stage it outside discovery at `AGENT_DIR/roblox/resources/artifacts/skills/<skill-name>/`;
- install it at `<project>/.claude/skills/<skill-name>/`;
- keep the record at `AGENT_DIR/roblox/resources/records/<slug>.yaml` unless the project already uses another authoritative location.

AGENT_DIR follows the rule in [state policy](state-policy.md#portable-resource-record-location).

If the project root cannot be found, report that and continue other preparation; do not install user-wide instead. A user-wide request may stage at `~/.claude/roblox/resources/artifacts/skills/<skill-name>/` and install at `~/.claude/skills/<skill-name>/`, with the same exact-target, collision and validation rules.

Before writing into a skill folder, inspect any existing folder at that path. If it is the same managed child, update it through the guarded flow. If it is unrelated or its ownership is unclear, stop and report the collision; never overwrite, merge, rename or repurpose an existing skill. Keep one editable copy per scope and record its location in `host_adoptions`.

## Refresh, repair, replacement and removal

- Verification changes do not change `project_use` authority or the adopted identity by themselves.
- A child failure affects only the child and its install state unless evidence also blocks the resource itself.
- A resource block keeps the adopted choice but marks that use blocked until it is repaired or the owner changes the decision.
- This skill may replace or retire an adopted resource only when it owns that choice or the user explicitly authorizes the change.
- For externally owned resources, report evidence to the owner and keep the target until the owner changes it.

Project adoption is complete when the record states the role and authority truthfully, the CLAUDE.md block matches the adopted state without altering unrelated text, any child is installed where intended (or its absence is stated), and conflicts or blocks are explicit.
