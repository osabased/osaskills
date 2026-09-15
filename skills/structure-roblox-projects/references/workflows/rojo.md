# Rojo structure work

Use this reference when reviewing, designing, planning, adopting, removing, or changing a Rojo mapping/workflow; changing a Rojo mapping or project/meta/model file; or migrating content into, out of, or within Rojo mapping where path, name, topology, version-sensitive sync behavior, `syncback`, or live `rojo serve` safety can affect the resulting DataModel. A routine source edit inside a clear stable mapping does not require this reference.

For a small filesystem-first project, prefer a compact source tree and let the project file define the DataModel mapping:

```text
src/
  client/
    init.client.luau
  server/
    init.server.luau
  shared/
default.project.json
```

## Establish the effective mapping

1. Inspect the repository's Rojo pin and run `rojo --version` when available if version-sensitive behavior matters.
2. Determine the effective DataModel mapping, not only the visible directory tree. Inspect applicable `*.project.json` / `*.project.jsonc`, nested projects, relevant `*.meta.json` and `*.model.json` files plus version-supported JSONC equivalents, `init.*` conventions, and project instance-description fields such as `$path`, `$className`, `$properties`, and `$ignoreUnknownInstances`.
3. Inspect version-relevant mapping behavior such as `emitLegacyScripts`, `syncRules`, `globIgnorePaths`, suffix conventions, nested project behavior, compatibility settings, and `syncbackRules` when the task can be affected by them.
4. For moves or renames inside mapped content, determine whether the path, filename, `init.*` role, suffix, nested project, or metadata changes the resulting DataModel even when no project file is edited.
5. Trace the full DataModel effect of a mapping or topology change. A filesystem move or project/metadata edit can affect instances outside the source subtree that appears to contain the change.
6. Keep structural migration separate from Rojo version upgrades. Change pins, manifests, lockfiles, or generated mappings only when those writes belong to the authorized task.

## Review

For a read-only Rojo architecture review, inspect only the mapping and version-sensitive behavior needed to answer the review question. Existing mapping is evidence, not proof of correctness; compare its effective DataModel result against the relevant structural requirements.

## Version-sensitive work

When external documentation is available, re-open the official release notes, applicable changelog entries, and project-format documentation before recommending an upgrade or relying on version-specific mapping, suffix, `syncRules`, `syncback`, or serve-safety behavior. State any material assumption that cannot be verified.

## Live sync and syncback

- Prefer `rojo build`, sourcemap generation, or another non-live structural check when it can validate the mapping adequately.
- Before live `rojo serve`, inspect version-supported place and network safeguards such as `servePlaceIds`, `blockedPlaceIds`, `serveAddress`, and `serveAllowedHosts`. Verify the intended place and binding before connecting Studio.
- Treat `rojo syncback` as a filesystem-writing migration operation, not a validation command. Read [`modification-scope.md`](../core/modification-scope.md) and [`migration.md`](migration.md) before using it. Account for every potentially written path, preserve pre-existing work, establish recovery, and inspect the resulting diff.
- Preserve working mappings and versions unless their change is part of the request.

## Sources

- [Project format](https://rojo.space/docs/v7/project-format/)
- [Sync details](https://rojo.space/docs/v7/sync-details/)
- [Releases](https://github.com/rojo-rbx/rojo/releases)
- [Changelog](https://github.com/rojo-rbx/rojo/blob/master/CHANGELOG.md)