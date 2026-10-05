# resource.yaml schema 1

The descriptor is safe YAML with duplicate-key rejection. Unknown fields and unsupported versions fail closed. All source selectors and integrity expectations are static reviewed facts. Current lifecycle state belongs in the matching schema-v3 resource record.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`; a changed unsupported schema requires regeneration. |
| `parent_contract` | `{name: roblox-resource-acquisition, version: 1}`; declares the shared usage dependency. |
| `scope` | `project` by default; `user` only for an explicit user/global scope choice. |
| `resource` | `slug`, `name`, canonical HTTPS URL, package ID or null, selector, `source_review_date` string and exact DevForum URL or null. |
| `resource.selector` | `kind: version/commit/source-state`, immutable `value`; Git profiles also require the full `tree`. Optional immutable `release_commit` identifies version release source. |
| `routing` | Nonempty `use_when` and `avoid_when` lists. Frontmatter remains the actual pre-load host description. |
| `guidance` | `claim_scope`, `shared_usage: references/child-usage.md`, document map and `executable_fixture`. Advice-only uses a null fixture. |
| `guidance.documents` | Each existing Markdown `path` has nonempty `roles` and `when`. Core roles stay in SKILL.md; every reference is linked and reachable. |
| `reconciliation` | `policy: required/conditional/not-applicable`, concrete `reason`, project-relative `record` and `learnings`. User scope additionally declares `no_project_record` and `no_project_learnings`. |
| `installation` | A supported declarative profile below. No shell/evidence commands or current pass/status fields. |

Coverage roles are `routing`, `common-use`, `ownership`, `security`, `verification`, `maintenance`, `setup`, `troubleshooting`, `recipes`, `lifecycle` and `api`. An author chooses document layout and headings; validation checks required coverage and navigation, while realistic tasks check content.

## Installation profiles

- `pesde-wally` / `pesde-registry`: canonical package ID and exact version come from `resource`. Supply `dependency_section`, canonical `registry`, resource `target`, and source `integrity`. The checker resolves a matching direct alias and its exact lock counterpart.
- `pesde-git`: canonical repository/commit/tree come from `resource`. Supply `dependency_section`, `target`, optional reviewed `new_structure`, and source `integrity`. The tree and canonical repository bind the lock identity.
- `npm`: canonical npm package ID and exact version come from `resource`. Supply `dependency_section` (`dependencies` or `devDependencies`), canonical `registry`, reviewed `archive_url` and SHA512 SRI `archive_integrity`, source `integrity`, and any material direct `companions`. Each companion declares its own package ID, exact version, dependency section, archive URL/integrity and source integrity. The checker binds exact manifest/root-lock declarations to package-lock format 2/3 entries and verifies installed package.json plus reviewed source. It accepts exact npm aliases and explicit mapped source directories, executes no package scripts, and does not claim verification of the transitive graph.
- `asset`: supply `asset_sha256`; the caller resolves the actual installed asset through its project/host binding and passes `--asset`.
- `custom`: supply a child-relative `custom_checker` under scripts/. Structural validation checks its existence. The shared checker never executes a metadata-selected script; the child documents its real command and observable result.

Integrity supports relative-file SHA256 expectations, a flat source-directory aggregate (sorted filename plus per-file SHA256), a literal source version header, and an installed TOML/JSON manifest name/version. An aggregate may set `recursive: true`; its sorted entries then use source-directory-relative POSIX paths, so nested source edits and new files change the digest. Paths remain within the selected source root. Wrapper files and project-generated artifacts stay in project integration checks.

Material Wally companions declare package ID, exact version, canonical registry, upstream parent package, dependency edge alias and their own integrity. Keep them in dependency order. The checker verifies each lock edge and accepts explicit companion locations.

The parent shares checker logic. Nonstandard project layouts use explicit source inputs; resource metadata does not require one alias or one user's filesystem. Use Python 3.11+ and PyYAML. Restore environment dependencies with uv when available.
