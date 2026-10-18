# Writing a library skill (contract 2)

Use this only when the user asks for a library skill, or the same pinned library is clearly reused across projects. First check the [catalog](library-skills.md): clone a catalog skill, or reuse an existing one, for the same exact pin instead of writing a duplicate.

A library skill is a short `SKILL.md`, a static `resource.yaml`, optional `references/`, and a `scripts/` checker only when the standard profiles can't describe the pin. Catalog skills live in this skill's `libraries/` folder and run from clones in a project's `.claude/skills/`, where no relative path reaches this skill. So a library skill names `roblox-resource-acquisition` in prose instead of linking it, and must work on its own.

Contents: [Before writing](#before-writing) · [SKILL.md](#skillmd) · [resource.yaml](#resourceyaml) · [Install profiles](#install-profiles) · [Validate](#validate) · [Executable claims](#executable-claims) · [Install](#install)

## Before writing

Understand the exact pinned library from its canonical source: the problem it solves and doesn't, installation and DataModel placement, the public API the skill will cover, client/server model, lifecycle and cleanup, configuration defaults, dependencies, failure modes, security boundaries, and how a project declares and locks it. A library you chose yourself should have passed its adoption checks first (see [adopting](adopting.md)). Writing a skill doesn't adopt or prove anything.

A contract table from structure-roblox-projects is a starting point, not a skill. Use only its `read` rows quoted from the tool's own docs: Restore feeds `## Check the pin` and the install profile, and Startup, Boundaries and Check feed `## Core API` and `## Gotchas`. Project facts such as mapping paths stay in that project's guide, and everything else on this page still applies.

## SKILL.md

Start from [the template](../templates/resource-skill-template.md). The [checked examples](../examples/README.md) show the finished layout:

- [GoodSignal](../examples/goodsignal/SKILL.example.md): read when writing a skill for a Luau module.
- [Rojo build](../examples/rojo-build/SKILL.example.md): read when writing a skill for a command-line development tool.

Name the skill `roblox-<library>` without a version; the pin goes in the body and `resource.yaml`.

- **Description** (at most 1024 characters): library and repo names, key API names, file names (`pesde.toml`, `default.project.json`) and phrases a user would type; say what and when, plus one short exclusion.
- **`## Check the pin`:** the exact manifest entry and lock key (or, for an asset, the SHA-256) that match the pin, for each manager the profile supports, then the standard closing paragraph from the template: on another version, tell the user, keep the project's pin, use only API confirmed at that version, and stop where behavior may differ; upgrade through `roblox-resource-acquisition`; advice only when the project doesn't declare the library; stop on a blocked use noted in the project's `CLAUDE.md`; say what was checked. The validator fails unless this section states the selector value, the git tree and the asset hash where the descriptor has them.
- **`## Core API`:** a `call | returns | notes` table grounded in the reviewed source. Never invent APIs from names or from other libraries.
- **`## Example`** (recommended): 8–15 lines of Luau, or the tool's real command line, taken from the reviewed source or the maintained fixture.
- **`## Gotchas`:** 3–6 pin-specific bullets: cleanup order, cancellation limits, idempotence, client/server boundary, security.
- **`## Read further`:** links to `references/*.md`, each with "read when …", ending with the template's line on reporting wrong guidance to the catalog.

The headings above (except Example) are required; others are allowed. Put long setup, recipes and symptom diagnosis in references; a small library may need none.

Frontmatter may use the Agent Skills fields (`name`, `description`, `license`, `compatibility`, `allowed-tools`, `metadata`) and the Claude Code fields `disable-model-invocation`, `user-invocable`, `argument-hint` and `model`. Other keys produce a warning.

## resource.yaml

Start from [the descriptor template](../templates/resource-skill-template.yaml). It is safe YAML holding only static reviewed facts; duplicate keys, unknown fields and other schema versions fail. Project state (which projects use it, blocked uses) belongs in the project, not here.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `2`. |
| `parent_contract` | `{name: roblox-resource-acquisition, version: 2}`. |
| `scope` | `project` by default; `user` only for an explicit user-wide skill. |
| `resource` | `slug`, `name`, HTTPS `canonical_url`, `package_id` or null, `selector`, `source_review_date` (YYYY-MM-DD), and an exact DevForum topic URL or null. |
| `resource.selector` | `kind` (`version`, `commit` or `source-state`) and an immutable `value`. `pesde-git` also needs the full `tree`; optional `release_commit` names the release's source commit. |
| `routing` | Nonempty `use_when` and `avoid_when` lists. The frontmatter description is still what the host routes on. |
| `guidance` | `claim_scope` (`advice-only` or `executable-integration`), `documents`, and `executable_fixture` (null for advice-only). |
| `guidance.documents` | Each Markdown `path` with nonempty `roles` and `when`. `SKILL.md` must carry `routing`, `common-use`, `ownership`, `security`, `verification` and `maintenance`; `setup` and `troubleshooting` must be covered somewhere. Other roles: `recipes`, `lifecycle`, `api`. Every declared reference must be linked from `SKILL.md`. |
| `installation` | One profile below. No shell commands or result fields. |

## Install profiles

The profile tells `clone_children.py` and the session hook how a project declares the pin. They compare the manifest and lock only; nothing hashes installed packages.

- `wally`: `dependency_section` (`dependencies`, `server-dependencies` or `dev-dependencies`), canonical `registry`, optional `companions`. Binds the `wally.toml` requirement to the exact `wally.lock` entry; a range requirement is reported as a note.
- `pesde-wally`: a Wally-index package used through pesde. `dependency_section` (`dependencies` or `dev_dependencies`), `registry`, `target`, optional `companions`. Falls back to `wally.toml`/`wally.lock` when the project has no `pesde.toml`.
- `pesde-registry`: like `pesde-wally` for the pesde registry, without companions.
- `pesde-git`: repository, commit and tree come from `resource`. `dependency_section`, `target`, optional `new_structure`.
- `npm`: package and exact version come from `resource`. `dependency_section` (`dependencies` or `devDependencies`), `registry`, the reviewed `archive_url` and its SHA-512 SRI `archive_integrity`, and any material `companions` with the same fields. Binds `package.json` to `package-lock.json` (format 2 or 3) and compares the lock's resolved URL and integrity with the reviewed archive.
- `asset`: `asset_sha256` of the reviewed file. The file lives outside the project (a Studio plugin), so the comparison reports `UNAVAILABLE` and `SKILL.md` says how to hash it.
- `custom`: a skill-relative `custom_checker` under `scripts/`. Nothing here runs it; `SKILL.md` documents its command.

Wally and pesde companions declare `package_id`, exact `version`, `registry`, `parent_package` and `edge_alias`, in dependency order; the lock must resolve each edge to that version.

## Validate

1. **Structure:** `scripts/validate_skill.py SKILL_DIR` checks frontmatter, required headings, the descriptor, the pin values in `## Check the pin`, document coverage and reachability, and local links. Static checks never prove runtime behavior or routing.
2. **Pin check:** make a fixture project whose manifest and lock pin the reviewed version. For a catalog skill, `scripts/clone_children.py --project FIXTURE --status` reports its `declared` as `PASS`; change the pin and confirm `FAIL`. For a skill outside the catalog, follow its `## Check the pin` against the fixture yourself.
3. **Behavior:** give fresh subagents the skill, the needed project context and a realistic task, without the intended answer:
   - a task that should use the skill (it activates and solves it with the real API);
   - a nearby task that shouldn't (a built-in or tiny local solution; the skill stays out);
   - a project pinned to another version (the agent reports it, keeps the pin, and avoids version-specific claims);
   - when two skills could compete, one task for each and one that should select neither;
   - when the library touches remotes, persistence, HTTP or arbitrary assets, a task that probes the security boundary.
4. Fix what fails, rerun the failed case, and confirm the case can still fail against the old wording. A test weakened until it can't fail proves nothing.

Stop when these pass. More examples or polish are not reasons to keep iterating. If fresh subagents or Studio aren't available, run what you can and say which checks didn't run.

## Executable claims

Mark a skill `executable-integration` only when a maintained fixture actually runs. Keep its examples derived from that one fixture. Report separately what each kind of evidence shows: an analyzer, build or construction test proves only static and construction behavior; real input, rendered layout, animation, normal startup or a clean Studio console need a Studio or client run.

When the library composes with a cleanup owner (Janitor, Maid, Trove, Vide scopes), inspect the exact pinned cleanup implementations rather than trusting method names:

- create the owner and register cleanup before any fallible construction;
- stop producers (signals, loops, callbacks) before destroying the state they reach;
- don't assume an insertion or reverse cleanup order the library doesn't document; if order matters, use one composite cleanup;
- repeated or reentrant destroy runs each cleanup at most once, and nothing reaches a disposed consumer afterwards.

A component cleans only what it created. Package-global schedulers may live for the whole runtime.

## Install

Write a skill into `<project>/.claude/skills/<name>/` by default, or `~/.claude/skills/<name>/` on an explicit user-wide request. When other projects will use the same pin, also propose it for the catalog at `libraries/<name>/` in `osabased/osaskills` (with push access, as a pull request like those in [keeping current](keeping-current.md#update)); once merged, projects [clone it](library-skills.md#clone-into-a-project). A skill built from a contract goes straight to that pull request, since the project's guide already holds the contract. Before writing, look at any existing folder at that path; if it belongs to a different skill, stop and report the collision instead of overwriting it. Keep one editable copy per scope. A new skill may only appear in a new session; confirm it is listed and that `/<name>` invokes it before calling it working.
