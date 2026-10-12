# Resource child contract 1

A child is a per-library skill: a short `SKILL.md`, a static `resource.yaml`, optional references, and custom checkers only when the shared profiles cannot express the check. Children live flat beside this skill (for example `skills/roblox-janitor/` next to `skills/roblox-resource-acquisition/`), so the shared contract is reachable at `../roblox-resource-acquisition/references/child-usage.md`. A child must still work as advice when that sibling is missing.

Contents: [SKILL.md](#skillmd) · [resource.yaml](#resourceyaml) · [Installation profiles](#installation-profiles) · [Validation](#validation)

## SKILL.md

Start from [the template](../templates/resource-skill-template.md). Name the child `roblox-<library>` without a version; the pin lives in the body and in `resource.yaml`.

```
---
name: roblox-<lib>
description: <Library> (<owner/repo>) for Roblox Luau, pinned <version>. Use when ... Not for ...
---

# <Library> <version>

Pinned target: `<selector value>` (source reviewed <date>). [resource.yaml](resource.yaml) holds the exact identity.

## Check the pin
## Core API
## Example
## Gotchas
## Read further
```

- **Description:** concrete and specific: library and repo names, key API names, file names (`wally.toml`, `default.project.json`), and phrases a user would type. Say what and when, plus one short exclusion. At most 1024 characters.
- **Check the pin:** one short paragraph. If the project pins this library, confirm it matches the target. If `roblox-resource-acquisition` is installed beside the child, run its checks per [child usage](child-usage.md). If the parent, Python or a project record is unavailable, read the project's manifest/lock directly and say which checks were skipped. Stop only on a `FAIL`, `MISMATCH`, `BLOCKED` or `FAILED` result, an observed mismatch, or an explicit block.
- **Core API:** a table of `call | returns | notes`, grounded in the reviewed source. Never invent APIs from names or other libraries.
- **Example:** 8–15 lines of Luau (or the tool's real command line) derived from the reviewed source or the maintained fixture.
- **Gotchas:** 3–6 pin-specific bullets: cleanup order, cancellation limits, idempotence, client/server boundary, security.
- **Read further:** links to `references/*.md`, each with "read when …".

`## Check the pin`, `## Core API`, `## Gotchas` and `## Read further` are required; `## Example` is recommended. Other headings are allowed. Put long setup, recipes and symptom diagnosis in references; a small library may need none.

Frontmatter may use the Agent Skills fields (`name`, `description`, `license`, `compatibility`, `allowed-tools`, `metadata`) and the Claude Code fields `disable-model-invocation`, `user-invocable`, `argument-hint` and `model`. Other keys produce a warning.

## resource.yaml

The descriptor is safe YAML; duplicate keys, unknown fields and unsupported versions fail. Everything in it is a static reviewed fact. Live state (trust, project use, blocks, verification, validation results, install state) belongs in the project's record, never here.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`. |
| `parent_contract` | `{name: roblox-resource-acquisition, version: 1}`. |
| `scope` | `project` by default; `user` only for an explicit user-wide child. |
| `resource` | `slug`, `name`, canonical HTTPS `canonical_url`, `package_id` or null, `selector`, `source_review_date` (YYYY-MM-DD) and exact DevForum topic URL or null. |
| `resource.selector` | `kind: version / commit / source-state` and an immutable `value`. Git profiles also need the full `tree`; optional `release_commit` names the release's source commit. |
| `routing` | Nonempty `use_when` and `avoid_when` lists. The frontmatter description remains what the host routes on. |
| `guidance` | `claim_scope` (`advice-only` or `executable-integration`), `shared_usage: references/child-usage.md`, `documents` and `executable_fixture` (null for advice-only). |
| `guidance.documents` | Each Markdown `path` with nonempty `roles` and `when`. `SKILL.md` must carry `routing`, `common-use`, `ownership`, `security`, `verification` and `maintenance`; `setup` and `troubleshooting` must be covered somewhere. Other roles: `recipes`, `lifecycle`, `api`. Every declared reference must be linked from `SKILL.md`. |
| `reconciliation` | `policy: required / conditional / not-applicable`, a concrete `reason`, and project-relative `record` and `learnings` paths, normally `.roblox-resources/records/<slug>.yaml` and `.roblox-resources/learnings/`. User scope also declares `no_project_record` and `no_project_learnings` under `~/.roblox-resources/`. |
| `installation` | One profile below. No shell commands or pass/status fields. |

Older children may name `.agents/roblox/resources/...` record paths; they still validate, but move project data to `.roblox-resources/`.

## Installation profiles

- `wally`: a Wally package. Supply `dependency_section` (`dependencies`, `server-dependencies` or `dev-dependencies`), canonical `registry`, source `integrity` and optional `companions`. The checker binds the `wally.toml` requirement to the exact `wally.lock` entry (a range requirement is reported as a note) and hashes the package under `Packages/_Index`, `ServerPackages/_Index` or `DevPackages/_Index`.
- `pesde-wally`: a Wally-index package. Supply `dependency_section` (`dependencies` or `dev_dependencies`), `registry`, `target` and `integrity`. The checker uses `pesde.toml`/`pesde.lock`, and falls back to `wally.toml`/`wally.lock` (searching all three Wally sections) when the project has no `pesde.toml`.
- `pesde-registry`: like `pesde-wally` for the pesde registry, without companions.
- `pesde-git`: canonical repository, commit and tree come from `resource`. Supply `dependency_section`, `target`, optional `new_structure` and `integrity`.
- `npm`: canonical npm package and exact version come from `resource`. Supply `dependency_section` (`dependencies` or `devDependencies`), `registry`, reviewed `archive_url`, SHA512 SRI `archive_integrity`, source `integrity` and any material `companions` (each with its own package, version, section, archive and integrity). The checker binds `package.json` to `package-lock.json` format 2/3 and checks the installed `package.json` and source. It runs no package scripts and does not verify the transitive graph.
- `asset`: supply `asset_sha256`; the caller passes the installed asset with `--asset`.
- `custom`: supply a child-relative `custom_checker` under `scripts/`. The shared checker never runs it; the child documents its command and expected result.

`integrity` supports per-file SHA256 values, a source-directory aggregate (sorted file name plus per-file SHA256; `recursive: true` uses relative POSIX paths), a literal version header, and an installed TOML/JSON manifest name and version. Paths stay inside the package root. Wrapper files and generated project files are project integration checks, not upstream hashes.

Wally/pesde companions declare `package_id`, exact `version`, `registry`, `parent_package`, `edge_alias` and their own `integrity`, in dependency order. The checker verifies each lock edge.

## Validation

Run `scripts/validate_skill.py CHILD` for frontmatter, the required headings, the descriptor, document coverage and reachability, and local links and anchors. The sibling-parent link is checked as a route only, because the parent may be absent. Run the record, bundle and catalog validators when those artifacts are in scope (see [generation and validation](generation-validation.md)). Static checks never establish runtime behavior or host routing.

Shared-contract changes invalidate dependent child claims, not unrelated resource proof. Unsupported schema or contract versions require regeneration; there is no fallback reader for older inline-provenance children.
