# Project resource adoption

Use this reference when a resource becomes, ceases to be, or changes as a durable project-standard dependency, when a project-use authority supplies a fixed resource target, or when the project-root `AGENTS.md` resource index must change.

This file owns project-use state, project-root onboarding mutation, project conflict handling, project-local generated-skill placement, and fresh-agent visibility of the project resource index. Resource trust/verification remains in [state-policy.md](state-policy.md); generated-child validation remains in [generation-validation.md](generation-validation.md); host operational state remains in [operational-lifecycle.md](operational-lifecycle.md).

## Establish project-use authority

Before changing project-standard resource state, determine who owns the resource decision at the affected scope.

- **`roblox-resource-acquisition` authority:** this workflow selected or was explicitly directed to establish the resource as the project standard for the stated role. It may maintain that project-use decision within the authorized scope.
- **External project authority:** another durable project contract already owns the exact resource choice, identity/pin, role, replacement, or upgrade decision. Preserve that authority verbatim in `project_use.authority`. This workflow may acquire, inspect, verify, record evidence for, and generate guidance about the supplied target, but it must not substitute, retarget, upgrade, or retire it independently.

`structure-roblox-projects` is the authority for Canonical SSA's ModuleLoader identity, pin, acquisition form, placement, and upgrade/replacement decision. Treat that loader as a fixed positive target when this workflow is invoked for it.

Project trust and project-use authority are different claims. `trust.basis: project` says the resource identity is trusted by project policy; `project_use.authority` says which durable project contract controls whether that resource is the project-standard choice for its role.

## Check project conflicts before mutation

Inspect the affected project root's governing `AGENTS.md` and any directly referenced durable project guidance that can resolve the same resource role, including `.agents/roblox/structure.md` when applicable.

A conflict exists only when existing durable guidance and the proposed project use establish incompatible choices for the **same role and applicable scope**. Adjacent capabilities are not conflicts.

When a conflict exists:

1. surface the conflicting guidance and proposed resource to the user;
2. leave the existing project-use state and onboarding unchanged; and
3. continue only after the user or the owning project contract resolves the direction.

Never resolve a conflict by overwriting human-authored instructions, another skill's owned block, or another authority's resource target.

## Record project use

Portable project records use the canonical location from [state-policy.md](state-policy.md). Every current record carries a `project_use` mapping:

- `status`: `adopted`, `retired`, or `not-applicable`;
- `role`: concise durable project role;
- `scope`: project-relative scope that the role applies to;
- `authority`: workflow/project contract that owns the project-use decision.

`adopted` means future agents should treat the resource as the project-standard choice for that role and scope. `retired` records a formerly adopted role but removes it from active onboarding. `not-applicable` means the record is evidence/candidate state rather than a durable project-standard dependency.

Keep project-use state independent from resource verification and generated-child state. An adopted resource can remain adopted while verification or generated guidance is blocked; the active onboarding entry must then stop presenting the affected use as normally available until the block is resolved.

## Maintain the project resource index

When at least one resource has `project_use.status: adopted`, maintain this owned block in the affected project root's `AGENTS.md`:

```markdown
<!-- roblox-resource-acquisition:onboarding:start -->
## Roblox resources

Use the project-standard resources below when their listed roles apply. If a resource choice conflicts with other governing project guidance, surface the conflict before changing either direction.

- **RESOURCE** — ROLE. [Optional authority note.] [Optional `Use $SKILL-NAME` when the matching project skill is operational.]
<!-- roblox-resource-acquisition:onboarding:end -->
```

Mutation rules:

1. Use only the `AGENTS.md` at the affected project root for this detailed resource index. Do not mutate a global or unrelated nested project's instructions.
2. If `AGENTS.md` exists and the owned markers are absent, append the complete block after existing content, adding only the newline needed for a clean append.
3. If the markers exist, update only the content between them. Preserve everything outside them.
4. If no project-root `AGENTS.md` exists, create one containing only the owned block.
5. Derive active entries from adopted project-use records for that project/scope; do not duplicate version, provenance, verification history, or API guidance in `AGENTS.md`.
6. For externally owned choices, identify the owner only when that prevents authority ambiguity, for example: `Structural selection is governed by .agents/roblox/structure.md.`
7. Add `Use $<generated_skill>` only when the matching child has an applicable `operational` host adoption visible to fresh agents in the intended scope. A missing/broken child does not remove an otherwise valid adopted resource choice.
8. When the resource itself is currently blocked for its adopted use, keep the project decision visible but mark that use blocked and direct repair/reconciliation; do not present it as normally usable.
9. Omit `retired` and `not-applicable` resources from the active block. Remove the owned block entirely when no adopted resources remain; preserve all unrelated `AGENTS.md` content.

An already-authorized `acquire/adopt` operation that establishes or changes a project-standard dependency also authorizes the matching record and owned project-root onboarding writes after conflict checks pass. Do not add a redundant confirmation stop solely for those owned persistence writes.

## Verify fresh-agent instruction scope

The project-root index is usable onboarding only when fresh agents will actually load that `AGENTS.md`.

For Codex, identify the working directory from which fresh agents are expected to enter the project and check whether the affected project root lies on the repository/project-root-to-working-directory instruction chain.

- If the project-root `AGENTS.md` lies on that chain, the index is visible and no additional pointer is needed.
- If the expected working directory is above a nested Roblox project, that nested `AGENTS.md` is not loaded by default. Keep the project-root index as durable project state, but **do not claim usable fresh-agent onboarding** from it alone.
- When an ancestor `AGENTS.md` on the loaded instruction chain is already within the authorized write boundary, add only the smallest project-scoped context pointer needed to reach the nested project instructions, for example: `For Roblox resource work under <project-relative-path>/, read <project-relative-path>/AGENTS.md before choosing or changing project-standard resources.` Preserve every unrelated ancestor instruction.
- When that ancestor write is not authorized, leave it unchanged and report the exact condition: future agents must start Codex from the affected project root (or a descendant) for the nested resource index to apply, or the owner must separately authorize an ancestor pointer.

An ancestor pointer is a visibility aid, not resource authority, and it does not move the resource index out of the project root. Re-check current OpenAI Codex `AGENTS.md` discovery guidance when this behavior is material and external documentation is available.

## Place generated project skills

Keep generated artifact storage separate from host discovery:

- project-local artifact before host adoption: `<project-root>/.agents/roblox/resources/artifacts/skills/<skill-name>/`;
- Codex repository skill adoption: `<skill-scope-root>/.agents/skills/<skill-name>/`;
- project resource records: `<project-root>/.agents/roblox/resources/records/<slug>.yaml` unless a higher-priority authoritative registry/storage location is supplied.

Resolve `skill-scope-root` from where fresh agents are expected to work. Codex discovers repository skills from `.agents/skills` directories from the working directory upward to the repository root; therefore a nested Roblox project's `.agents/skills` is not automatically visible to a session started above that project. Prefer the repository/root scope that makes the intended project skill visible to those fresh agents, unless narrower nested visibility is explicitly intended.

Before moving or writing a child into `<skill-scope-root>/.agents/skills/<skill-name>/`, inspect any existing target directory. If it is the same managed generated child, reconcile/update it through the existing host adoption. If it is unrelated or ownership/identity is ambiguous, stop and surface the collision; never overwrite, merge, rename, or repurpose a pre-existing skill merely to complete adoption.

Host adoption remains a separate lifecycle gate. Moving a validated project artifact into a host-recognized `.agents/skills/<skill-name>/` location establishes an installed host copy, not `operational` status. Complete the checks in [operational-lifecycle.md](operational-lifecycle.md) before claiming operational adoption.

Maintain one canonical editable child. When a project artifact is adopted into a project-local host location, move it into the host location or otherwise complete the transition without leaving a second independently editable canonical copy. Record the resulting host location in `host_adoptions`.

## Refresh, repair, replacement, and removal

- Resource verification changes do not change `project_use` authority or adopted identity by themselves.
- A generated-child failure affects only the child pointer/host state unless evidence also blocks the upstream resource use.
- A resource block keeps the adopted decision but marks the affected onboarding use blocked until repaired or the owning authority changes the decision.
- `roblox-resource-acquisition` may replace or retire an adopted resource only when it owns that project-use decision or the user explicitly authorizes the authority change.
- For externally owned resources, report evidence to the owning contract/user and preserve the target until that authority changes it.

Project adoption is complete when the resource record truthfully represents the durable role and authority, the project-root onboarding block matches active adopted state without altering unrelated instructions, fresh-agent visibility is either verified for the intended working directory or its exact limitation is reported, any generated child occupies exactly the intended artifact/host state, and conflicts or blocks are explicit rather than silently resolved.
