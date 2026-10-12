# Writing a child skill (contract 1)

Use this only when the user asks for a child skill, or the same pinned resource is clearly reused across projects. First check the [bundled catalog](bundled-skills.md): reuse a bundled or existing child for the same exact pin instead of writing a duplicate.

A child is a per-library skill: a short `SKILL.md`, a static `resource.yaml`, optional `references/`, and a `scripts/` checker only when the shared profiles can't express the check. Children live in this skill's `libraries/` folder (for example `libraries/roblox-janitor/`), so the shared contract is at `../../references/child-usage.md`. Some installs place a child beside this skill instead, so a child names both locations and must still work as advice when the parent is missing.

Contents: [Before writing](#before-writing) · [SKILL.md](#skillmd) · [resource.yaml](#resourceyaml) · [Install profiles](#install-profiles) · [Validate](#validate) · [Executable claims](#executable-claims) · [Install](#install)

## Before writing

Understand the exact pinned resource from its canonical source: the problem it solves and doesn't, installation and DataModel placement, the public API the child will cover, client/server model, lifecycle and cleanup, configuration defaults, dependencies, failure modes, security boundaries, and how a project can tell which version is installed. A resource you chose yourself should have passed its adoption checks first (see [adopting](adopting.md)). Writing a child doesn't adopt or prove anything.

## SKILL.md

Start from [the template](../templates/resource-skill-template.md). Name the child `roblox-<library>` without a version; the pin goes in the body and `resource.yaml`.

- **Description** (at most 1024 characters): library and repo names, key API names, file names (`wally.toml`, `default.project.json`) and phrases a user would type; say what and when, plus one short exclusion.
- **`## Check the pin`:** one short paragraph. If the project pins this library, confirm it matches. If the parent is installed beside the child, run its check per [child usage](child-usage.md); otherwise read the manifest and lock directly and say which checks were skipped. On a `FAIL` result or an observed mismatch, tell the user, keep the project's pin, and use only API confirmed at the project's version.
- **`## Core API`:** a `call | returns | notes` table grounded in the reviewed source. Never invent APIs from names or from other libraries.
- **`## Example`** (recommended): 8–15 lines of Luau, or the tool's real command line, taken from the reviewed source or the maintained fixture.
- **`## Gotchas`:** 3–6 pin-specific bullets: cleanup order, cancellation limits, idempotence, client/server boundary, security.
- **`## Read further`:** links to `references/*.md`, each with "read when …".

The headings above (except Example) are required; others are allowed. Put long setup, recipes and symptom diagnosis in references; a small library may need none.

Frontmatter may use the Agent Skills fields (`name`, `description`, `license`, `compatibility`, `allowed-tools`, `metadata`) and the Claude Code fields `disable-model-invocation`, `user-invocable`, `argument-hint` and `model`. Other keys produce a warning.

## resource.yaml

Start from [the descriptor template](../templates/resource-skill-template.yaml). It is safe YAML holding only static reviewed facts; duplicate keys, unknown fields and unsupported versions fail. Project state (which projects use it, known issues) belongs in the project, not here.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`. |
| `parent_contract` | `{name: roblox-resource-acquisition, version: 1}`. |
| `scope` | `project` by default; `user` only for an explicit user-wide child. |
| `resource` | `slug`, `name`, HTTPS `canonical_url`, `package_id` or null, `selector`, `source_review_date` (YYYY-MM-DD), and an exact DevForum topic URL or null. |
| `resource.selector` | `kind` (`version`, `commit` or `source-state`) and an immutable `value`. Git profiles also need the full `tree`; optional `release_commit` names the release's source commit. |
| `routing` | Nonempty `use_when` and `avoid_when` lists. The frontmatter description is still what the host routes on. |
| `guidance` | `claim_scope` (`advice-only` or `executable-integration`), `shared_usage: references/child-usage.md`, `documents`, and `executable_fixture` (null for advice-only). |
| `guidance.documents` | Each Markdown `path` with nonempty `roles` and `when`. `SKILL.md` must carry `routing`, `common-use`, `ownership`, `security`, `verification` and `maintenance`; `setup` and `troubleshooting` must be covered somewhere. Other roles: `recipes`, `lifecycle`, `api`. Every declared reference must be linked from `SKILL.md`. |
| `reconciliation` | `policy` (`required`, `conditional` or `not-applicable`) and a concrete `reason`. Older children may also carry `record` and `learnings` paths; they are accepted and ignored. |
| `installation` | One profile below. No shell commands or result fields. |

## Install profiles

- `wally`: `dependency_section` (`dependencies`, `server-dependencies` or `dev-dependencies`), canonical `registry`, source `integrity`, optional `companions`. The checker binds the `wally.toml` requirement to the exact `wally.lock` entry (a range requirement is reported as a note) and hashes the package under `Packages/_Index`, `ServerPackages/_Index` or `DevPackages/_Index`.
- `pesde-wally`: a Wally-index package used through pesde. `dependency_section` (`dependencies` or `dev_dependencies`), `registry`, `target`, `integrity`. Falls back to `wally.toml`/`wally.lock` when the project has no `pesde.toml`.
- `pesde-registry`: like `pesde-wally` for the pesde registry, without companions.
- `pesde-git`: repository, commit and tree come from `resource`. `dependency_section`, `target`, optional `new_structure`, `integrity`.
- `npm`: package and exact version come from `resource`. `dependency_section` (`dependencies` or `devDependencies`), `registry`, reviewed `archive_url`, SHA512 SRI `archive_integrity`, source `integrity`, and any material `companions`. Binds `package.json` to `package-lock.json` (format 2/3). Runs no package scripts.
- `asset`: `asset_sha256`; the caller passes the installed file with `--asset`.
- `custom`: a child-relative `custom_checker` under `scripts/`. The shared checker never runs it; the child documents its command.

`integrity` supports per-file SHA-256 values, a source-directory aggregate (sorted file name plus per-file SHA-256; `recursive: true` uses relative POSIX paths), a literal version header, and an installed TOML/JSON manifest name and version. Paths stay inside the package root. Wally/pesde companions declare `package_id`, exact `version`, `registry`, `parent_package`, `edge_alias` and their own `integrity`, in dependency order.

## Validate

1. **Structure:** `scripts/validate_skill.py CHILD` checks frontmatter, required headings, the descriptor, document coverage and reachability, and local links. Static checks never prove runtime behavior or routing.
2. **Install check:** run `scripts/check_resource_install.py CHILD --project PROJECT` against a real manifest, lock and installed package. Also try a wrong pin and a modified file and confirm each gives `FAIL`.
3. **Behavior:** give fresh subagents the child, the needed project context and a realistic task, without the intended answer:
   - a task that should use the child (it activates and solves it with the real API);
   - a nearby task that shouldn't (a built-in or tiny local solution; the child stays out);
   - "which version does this target, and was it runtime-tested?" (the answer matches `resource.yaml` and doesn't call source reading a runtime test);
   - when two children or another installed skill could compete, one task for each and one that should select neither;
   - when the resource touches remotes, persistence, HTTP or arbitrary assets, a task that probes the security boundary.
4. Fix what fails, rerun the failed case, and confirm the case can still fail against the old wording. A test weakened until it can't fail proves nothing.

Stop when these pass. More examples or polish are not reasons to keep iterating. If fresh subagents or Studio aren't available, run what you can and say which checks didn't run.

## Executable claims

Mark a child `executable-integration` only when a maintained fixture actually runs. Keep its examples derived from that one fixture. Report separately what each kind of evidence shows: an analyzer, build or construction test proves only static and construction behavior; real input, rendered layout, animation, normal startup or a clean Studio console need a Studio or client run.

When the resource composes with a cleanup owner (Janitor, Maid, Trove, Vide scopes), inspect the exact pinned cleanup implementations rather than trusting method names:

- create the owner and register cleanup before any fallible construction;
- stop producers (signals, loops, callbacks) before destroying the state they reach;
- don't assume an insertion or reverse cleanup order the library doesn't document; if order matters, use one composite cleanup;
- repeated or reentrant destroy runs each cleanup at most once, and nothing reaches a disposed consumer afterwards.

A component cleans only what it created. Package-global schedulers may live for the whole runtime.

## Install

Install a child only where the user wants it: `<project>/.claude/skills/<name>/` by default, or `~/.claude/skills/<name>/` on an explicit user-wide request. Before writing, look at any existing folder at that path; if it belongs to a different skill, stop and report the collision instead of overwriting it. Keep one editable copy per scope. A new skill may only appear in a new session; confirm it is listed and that `/<name>` invokes it before calling it working.
