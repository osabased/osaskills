# Generate and validate resource children

Use this only when a child skill is in scope: the user asked for one, or the same pinned resource is clearly reused across projects (see [adoption policy](adoption-policy.md#scope-and-autonomy)). Reuse an existing exact-target child on the current contract when it is valid, including a bundled one from the [bundled catalog](bundled-skills.md).

## Qualify and stage

An untrusted resource needs its resource proof before you write a child. A policy-trusted resource may get source-grounded guidance while runtime proof is unavailable; record trust, source understanding and runtime status separately. Preserve externally owned identity, pin and role decisions. Writing a child grants neither trust nor project authority.

Resolve the project with [project adoption](project-adoption.md). Stage outside discovery, for example `<project>/.roblox-resources/artifacts/skills/<skill-name>/`. An unknown project never authorizes a user-wide install. Keep one editable installed child; staging copies are validation artifacts.

Read the [resource child contract](resource-skill-contract.md) and the [entrypoint](../templates/resource-skill-template.md) and [descriptor](../templates/resource-skill-template.yaml) templates. Replace every scaffold value with real exact-target facts.

## Write the child

Follow the lean `SKILL.md` layout in the contract: `## Check the pin`, `## Core API`, `## Example`, `## Gotchas`, `## Read further`. Keep the routing description, the pin, the core API table, one example and the pin-specific gotchas in `SKILL.md`. Move long setup, recipes, lifecycle detail and symptom diagnosis into references and declare each one's path, role and reading trigger in `resource.yaml`.

Put the static identity, immutable selector, review date, reconciliation policy and integrity profile in `resource.yaml`. Keep local aliases, mapping paths, roles, fixtures and results in the project's record. Use the shared checker or a reviewed custom helper; never execute commands taken from metadata or evidence.

Ground APIs and activation/cleanup behavior in the reviewed source. Derive executable examples from one maintained fixture, and use [integration proof](integration-proof.md) only for lanes you actually claim. Advice-only guidance stays advice-only. The [worked examples](../examples/README.md) show the format; they carry no trust or proof.

## Validate

1. Run `scripts/validate_skill.py CHILD`: frontmatter, required headings, descriptor, document coverage and reachability, local links and anchors.
2. Exercise the install checker against the actual manifest and lock and, where available, the installed source or asset. Use isolated fixtures for alias changes, missing or mismatched identities, modified bytes and companions.
3. Give a fresh subagent only the candidate, the necessary project or source context and a realistic task, following the [testing protocol](testing-protocol.md). Do not hand it the intended answer. Record instruction-response results separately from executable or runtime results.
4. When a record exists, update only the affected child evidence, then run `validate_resource_record.py --current-skill CHILD RECORD` and `validate_resource_bundle.py RECORD CHILD`.
5. Run `validate_skill_catalog.py --host claude` over the children the host will see, adding each materially overlapping non-generated skill with `--routing-competitor`. Keep the fingerprint and run routing tasks when it reports an overlap.

When fresh subagents or a Studio/MCP host are unavailable, run what you can and record the missing lane as unavailable. A contract audit or CLI fixture is never host or runtime proof.

## Evidence and promotion

Use structured `skill_validation.checks` with honest execution modes and target selectors. Bind each check to the inputs that determine it: the descriptor, the guidance file or section, the shared contract, fixtures, configuration and companions. Include `resource.yaml` and `child-usage.md` for whole-interface checks. Routing checks bind the activation metadata of every tested member.

Changed input hashes invalidate dependent claims. Keep unchanged exact-target proof and historical checks at their original selector. Shared contract or schema changes require revalidation of dependent children.

After validation, install through [guarded maintenance](on-demand-maintenance.md#guarded-correction-and-recovery) and [installing children](operational-lifecycle.md). A user-authorized local install can finish as `installed`; `operational` needs an observed listing and explicit invocation.

## Environment

The scripts need Python 3.11+ and PyYAML. `uv run --no-project --python ">=3.11" --with pyyaml python <parent>/scripts/<script>.py …` supplies both without setup. The scripts need no network or database. Researching source freshness is a separate step; a packaging-only change keeps the reviewed target.
