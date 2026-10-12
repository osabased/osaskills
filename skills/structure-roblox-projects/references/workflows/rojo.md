# Rojo structure work

Use when reviewing, designing, adopting, removing, or changing a Rojo mapping or workflow; editing a `*.project.json`, `*.meta.json`, or `*.model.json` file; or moving content into, out of, or within Rojo mapping where path, name, topology, `syncback`, or live `rojo serve` safety can change the resulting DataModel. A routine source edit inside a clear, stable mapping doesn't need this reference.

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

1. If version-sensitive behavior matters, check the repository's Rojo pin and run `rojo --version` when available.
2. Determine the effective DataModel mapping, not just the directory tree. Inspect the applicable `*.project.json` / `*.project.jsonc`, nested projects, relevant `*.meta.json` and `*.model.json` files and their JSONC equivalents, `init.*` conventions, and the instance fields `$path`, `$className`, `$properties`, and `$ignoreUnknownInstances`.
3. When they can affect the task, inspect version-dependent settings: `emitLegacyScripts` (7.4+; default `true` makes `*.client.luau` a `LocalScript` and `*.server.luau` a legacy `Script`, while `false` emits `Script`s with `RunContext` Client/Server; verified on 7.7.0), `syncRules` (7.5+), `globIgnorePaths`, suffix conventions, nested project behavior, and `syncbackRules` (7.7+). rojo.space lags behind for fields added after 7.4; the [changelog](https://github.com/rojo-rbx/rojo/blob/master/CHANGELOG.md) is more complete.
4. For moves or renames inside mapped content, check whether the path, filename, `init.*` role, suffix, nested project, or metadata changes the resulting DataModel even when no project file is edited.
5. Trace the full DataModel effect of a mapping or topology change. A filesystem move or project/metadata edit can affect instances outside the subtree that appears to contain it.
6. Keep structural changes separate from Rojo version upgrades. Change pins, manifests, lockfiles, or generated mappings only when the task covers those writes.

## Validate runtime topology

When you set up or change mapping/startup verification, parse the generated sourcemap and assert the runtime paths, instance classes, and unique critical entrypoints the architecture needs. For each critical entrypoint, check its source sits at the intended path and appears only once in the whole tree: a second mapping under another name or parent is still a duplicate. Check required shared dependencies as well as the bootstraps. A matching name or JSON fragment somewhere in the tree doesn't prove parentage or execution boundary. To claim the built place's topology is verified, apply the same path/class checks to the built place; source filenames need not survive in the place format.

Derive expected paths from the intended architecture, not by copying the current mapping, or the check validates the same mistake twice. When it's unclear whether the assertions catch real errors, run them once against a deliberately broken mapping (for example, an entrypoint moved to the wrong service or mapped twice) and confirm they fail. Put the assertions in the project's own canonical check. A static topology check needs no separate dev/release profiles or live Studio proof.

## Development and release artifacts

Use this section only when the task creates or changes development-only content (stories, previews, test bootstraps) or distinct development and release builds. Keep an established coherent composition unless the request is to change it.

1. Decide ship or exclude for each demo, story, preview, and development bootstrap. A module with no startup entrypoint still appears in the sourcemap and place, so startup inspection can't prove exclusion.
2. Keep the project's existing mapping as the source of truth. When new profiles are needed, derive them without copying runtime mappings or duplicating singleton services. Check the generated artifacts rather than trusting filenames, moves, or ignore settings.
3. In both the parsed sourcemap and a parsed text place build, require exact paths for the affected runtime entrypoints, feature roots, and their shared/network dependencies; surviving entrypoints don't prove their dependencies survived. In the release build, confirm each development-only item is absent. Count affected singleton services and require exactly one of each.
4. Keep excluded development source in strict analysis and test discovery. Release exclusion is an artifact boundary, not permission to stop checking the source.

One verified Rojo 7.7 shape is a shared `common.project.json` holding the full tree, plus thin wrappers whose `tree` is only `{ "$path": "common.project.json" }`. The release wrapper adds `globIgnorePaths`:

```json
{
  "name": "Example Release",
  "globIgnorePaths": [
    "**/*.story.luau",
    "**/Preview"
  ],
  "tree": {
    "$path": "common.project.json"
  }
}
```

Glob patterns match paths relative to the project file's directory, so write `src/client/Preview`, not `client/Preview`. `**/Preview` excludes an `init`-backed directory and everything under it; `**/Preview/**` alone leaves the directory's own ModuleScript in place. Rojo 7.7.0 also supports `!` negation in these patterns.

Don't add a service such as `ReplicatedStorage` beside the wrapper's root `$path`. In 7.7.0, `rojo build` then emits two of that service, while `rojo sourcemap` shows one and silently drops the wrapper's added children. This is why both artifacts must be checked. Use this shape only when it fits the project, adapt the names, and recheck against the project's pinned Rojo.

For repeatable checks, use [`../../scripts/check_rojo_artifact.py`](../../scripts/check_rojo_artifact.py) when the project can produce a text `.rbxlx` and a sourcemap. It needs Python 3.11+; build the artifacts separately with the project's pinned Rojo.

- `--require-path` asserts a complete DataModel-relative instance path in both artifacts. The checker drops a sourcemap's DataModel root name and an `.rbxlx` DataModel wrapper; a sourcemap rooted below DataModel keeps its root name as the first segment.
- `--require-path-fragment` / `--forbid-path-fragment` are substring matches, useful for exclusion classes such as `.story`. Use exact paths for identity and required content.
- `--singleton-class` requires exactly one instance of a class in each artifact.
- It rejects blank invariants and runs with no invariants. It does not check per-path classes, duplicate source mappings, RunContext, or execution; add project-owned assertions for those.

To make these assertions a project gate, copy the checker into the repository (or use an equivalent project tool), note where it came from, declare its runtime in CI, and call it from the canonical build/release check. A command that reaches into one developer's installed skill folder is fine for a probe, not for a project gate. When you add such a gate, confirm it fails if an implementation subtree is removed while a similarly named bootstrap remains, if a required dependency is removed, and if development content leaks, mutating each artifact independently.

## Observable client previews

Use this section only when a Rojo-backed development workflow must prove rendered client UI or real input.

- Serve the preview through the Rojo source of truth and the established client startup path, in the same Studio session your input, inspection, console, and screenshot tools can reach. A development-only lifecycle root is fine if it keeps the loader contract and is excluded from release.
- Keep active Script Capabilities boundaries and loader semantics. Don't widen capabilities, move scripts between incompatible capability containers, inject code through a privileged tool, or replace the startup path just to make a preview run. See [`../platform/script-capabilities.md`](../platform/script-capabilities.md).
- Before interacting, make sure Studio is running the bytes you just edited (uncommitted edits included); a commit hash alone doesn't identify dirty content.
- Use real pointer and text events for input claims, inspect state and console output, and capture the rendered states that matter. Calling the domain callback directly proves domain behavior only. Stop only play/serve sessions you started.
- UI Labs can complement this for isolated states and variants.

Report what you executed separately from what you only planned. Never report an unrun Studio check as passed. If the open question is whether a third-party preview or test library supports the needed runtime, that is a resource question for the `roblox-resource-acquisition` skill if installed; keep Rojo composition and startup decisions here.

## Review

For a read-only Rojo review, inspect only the mapping and version behavior the question needs. An existing mapping is evidence, not proof of correctness; compare its effective DataModel against the structural requirements.

## Live sync and syncback

- Prefer `rojo build`, `rojo sourcemap`, or another non-live check when it validates the mapping well enough.
- Before live `rojo serve`, check the place and network safeguards your version supports, such as `servePlaceIds`, `blockedPlaceIds`, `serveAddress`, and `serveAllowedHosts`. Confirm the intended place and binding before connecting Studio.
- Treat `rojo syncback` as a filesystem-writing migration, not a check. Read [`modification-scope.md`](../core/modification-scope.md) and [`migration.md`](migration.md) first, account for every path it may write, keep pre-existing work, have a recovery path, and inspect the diff.
- Keep working mappings and versions unless changing them is part of the request.

## Sources

- [Project format](https://rojo.space/docs/v7/project-format/)
- [Sync details](https://rojo.space/docs/v7/sync-details/)
- [Releases](https://github.com/rojo-rbx/rojo/releases)
- [Changelog](https://github.com/rojo-rbx/rojo/blob/master/CHANGELOG.md)
