# Review and save project guidance

Use when an initial overview, assessment, correction, or setup guide is to be saved. Read [project guide interpretation](project-profile.md) first. The user prefers to review guidance before it is saved, including revisions; normal task implementation does not bypass this gate.

## Review the concrete result

Prepare the overview and separate assessment in the response or a requested draft artifact. Present:

- the actual proposed content, or a precise diff for an update;
- project root, destination, and whether the operation creates, appends, or updates;
- any instruction pointer, its location, and whether it is visible from the intended agent entry directory;
- material gaps/uncertainty, existing documentation preserved, and whether assessment will also be saved.

Do not write the project guide, assessment, or instruction pointer before the user approves the preview. An explicitly requested separate scratch/review artifact is permissible; it must not become active project instructions before approval. Read-only orientation and design produce a review-ready answer by default.

Approval is specific to the shown documentation operation. Approval of the overview alone does not implement modernization suggestions, install tools, or alter project architecture. If the user already approves an exact save/update request or a setup preview containing the exact documentation writes, continue without another confirmation. A material change in the result or write set needs an updated preview.

Saving may remain pending while independently authorized project work continues. If a user declines persistence, leave project documentation unchanged and use the reviewed session context as appropriate.

## Save without creating conflicting authorities

1. Recheck affected pre-existing content and scope immediately before saving. Preserve concurrent/user edits; reconcile an overlapping change before applying the approved preview.
2. Use the approved existing destination, or `.agents/roblox/project.md` when no equivalent exists. Preserve unrelated content; update only the approved sections. Do not normalize a legacy profile as an incidental side effect.
3. Install only the reviewed small instruction pointer. Prefer an existing coherent pointer rather than duplicating it. When a managed block is needed, the following is a starting form; adapt the relative path to the actual instruction file:

```markdown
<!-- structure-roblox-projects:onboarding:start -->
## Roblox project guidance

Before working in this Roblox project, read `.agents/roblox/project.md`. Verify relevant project facts against their linked sources; investigate affected gaps or drift. Present proposed guide corrections for review before saving them.
<!-- structure-roblox-projects:onboarding:end -->
```

4. For an existing managed block, replace only that block as approved. If absent, append the approved pointer, retaining existing bytes except any newline needed to append cleanly. If creating an instruction file, include only the approved content. Preserve human-authored guidance outside the block.
5. Check that links resolve and instructions cover the intended project without applying to unrelated nested projects. Ancestor pointers are separate reviewed writes. If host discovery or entry scope is unavailable, report the visibility limitation and required entry point rather than inventing verification.
6. Inspect the resulting diff against the approved write set. State what was saved, where it can be reached, and remaining evidence gaps. Unrun Studio/host behavior stays unverified.

## Setup and ongoing changes

A reviewed setup authorizes its selected implementation. The documentation save can be included in the same review when its exact contents/pointer are shown; verify the implemented result before saving that approved guide. If implementation changes the described topology or reveals a material gap, revise the preview for review.

An ordinary feature or migration may invalidate saved guidance. Identify the affected clauses, establish the actual new implemented contract, and present the smallest update for approval. Do not automatically expand or repair documentation simply because code work is authorized.

Persistence is complete when approved guidance/pointers are saved without unrelated changes, source links resolve, reachability is established or accurately limited, and no recommendation or unavailable check is presented as implemented or verified.
