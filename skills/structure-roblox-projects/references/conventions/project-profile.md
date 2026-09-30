# Reusable Roblox project guidance

Use when interpreting existing project documentation, building an onboarding overview, or proposing a correction to saved guidance. [Review and persistence](project-profile-persistence.md) owns saving and instruction-pointer edits.

## Find and reuse the project's guide

Read applicable instructions and the documentation they identify first. Prefer a coherent existing project guide over creating a competing document. When no equivalent destination exists, propose `.agents/roblox/project.md` under the affected project root. The document describes how to work in that project; it does not grant modification authority.

A useful guide makes the project navigable to an agent without this chat. It covers the applicable orientation areas in [project orientation](../workflows/project-orientation.md), anchors material facts to implemented sources, and exposes relevant missing evidence. Reuse the usable sections even when other sections need investigation. Do not equate a title, fixed headings, an instruction marker, or one convention with verified completeness.

Project documentation is evidence whose scope and freshness must be established. The current request and governing instructions prevail; within those bounds, coherent implemented ownership/conventions guide ordinary work. Resolve an apparent filesystem/DataModel conflict through the actual authoring mapping before choosing which description is stale.

## Content and structure

Adapt headings to the project. A useful starting shape is:

```markdown
# Roblox project guide

## Scope and evidence
Project/target boundaries, evidence reviewed, relevant inaccessible surfaces.

## Authoring and topology
Owned source, generated/vendor/Studio-owned content, runtime or host mapping.

## Startup and systems
Bootstrap/lifecycle owners, major feature areas, dependency and authority rules.

## Working conventions
Placement, naming/API/lifecycle/cleanup/test conventions and intentional exceptions.

## Development and verification
Authoritative preparation/check/build/sync definitions, Studio/host checks, delivery ownership.

## Rechecking this guide
Sources of truth and change signals that require focused reinspection.
```

Explain stable relationships and non-obvious rules. Link entry files, manifests, configurations, tests, and existing docs. Commands can be shown when needed for an executable handoff, but cite their owning definition and verify rather than treating the displayed copy as authoritative forever. Do not duplicate inventories or version lists cheaply discoverable from native configuration.

Include the review date and evidence scope; dates do not substitute for checking changed facts. Explicitly label supported project facts, provisional inferences, inaccessible surfaces, and checks that were or were not run. The guide can be useful with declared gaps; do not hide them behind a claim of full onboarding.

Keep the assessment separate from factual working instructions. If the user approves saving assessment, use a clearly labeled section or a separate destination named in the preview. Optional proposals remain proposals until chosen. Do not persist temporary task logs, access secrets, or unselected defaults as conventions.

## Freshness and drift

Recheck relevant claims when a source link, mapping, target, tool/dependency contract, startup path, ownership, or canonical command changes or contradicts observed behavior. Investigate at the claimed scope before declaring a convention stale. A local exception, unresolved mapping, or dirty/pre-existing change alone is insufficient.

Preserve reliable sections and existing human-authored documentation. Present the smallest evidence-backed guide correction for review; do not silently repair even during authorized implementation. A user's explicit request to save/update documentation can approve that operation; otherwise the exact preview waits for their approval.

## Legacy `.agents/roblox/structure.md`

Existing profiles are narrow convention memory and remain valid evidence at their stated scope. Preserve their `Freshness` guidance and supported choices, including deliberately owned dependency targets. Missing fields express no preference. Do not reinterpret a sparse profile as an exhaustive project overview or fill it with inferred defaults.

When broader onboarding is needed, propose an extension to existing documentation or a project guide that references the legacy profile. Show any pointer replacement, content migration, or profile edit in the review preview; never automatically delete the profile or duplicate its rules into a second authority.

## Agent reachability

Provide a small pointer in the applicable project instructions so future agents can reach the guide before Roblox work. Preserve existing human instructions and pointer conventions. Verify the intended entry directory and instruction scope using the actual host's discovery behavior. A nested guide/pointer is not automatically visible to agents starting above that project.

When an ancestor pointer is needed, propose only a project-scoped link in an instruction file within the user's authorized scope. If visibility cannot be established or that write is unavailable, say exactly where agents must start or what owner action is needed. Do not claim usable fresh-agent onboarding merely because a file was created.
