# Rojo

Rojo facts here were reviewed against the version in [`versions.json`](../versions.json); the session's first [update check](keeping-current.md#check) says whether a newer release exists. Use this when changing a `*.project.json`, `*.meta.json` or `*.model.json`, moving content into, out of or within the mapping, or setting up builds, topology checks or live sync. A routine edit inside a stable mapping doesn't need it.

A small project:

```text
src/
  client/
    init.client.luau
  server/
    init.server.luau
  shared/
default.project.json
```

## Establish the mapping

1. Check the repository's Rojo pin, and `rojo --version` when version-sensitive behavior matters.
2. Read the effective mapping, not the directory tree: the project files and nested projects, `*.meta.json` and `*.model.json` (and their JSONC forms), `init.*` files, and the fields `$path`, `$className`, `$properties` and `$ignoreUnknownInstances`.
3. Check the version-dependent settings that can affect the task: `emitLegacyScripts` (7.4+; default `true` builds `*.client.luau` as a `LocalScript` and `*.server.luau` as a legacy `Script`, while `false` builds `Script`s with `RunContext` Client or Server; verified on 7.7.0 and 7.7.1), `syncRules` (7.5+), `globIgnorePaths`, and `syncbackRules` (7.7+). Set `emitLegacyScripts` in the project file that holds the tree: a wrapper's value doesn't reach a nested project (observed on 7.7.1). rojo.space lags for fields added after 7.4; the [changelog](https://github.com/rojo-rbx/rojo/blob/master/CHANGELOG.md) is more complete.
4. A move or rename can change the DataModel with no project-file edit: the path, filename, `init.*` role, suffix and metadata all count. Trace the whole effect, including instances outside the subtree that seems to contain it.
5. Keep structural changes separate from Rojo upgrades.

## Check the built place

Assert the runtime topology the architecture needs: each entrypoint at its intended path with its intended class, appearing exactly once in the whole tree (a second mapping under another name is still a duplicate), and the shared dependencies it requires. A matching name somewhere in the tree doesn't prove parentage. Derive expected paths from the intended architecture, not by copying the current mapping, or the check repeats the mistake. Check the built `.rbxlx`, not only the sourcemap: the two can disagree (see below).

[`check_rojo_artifact.py`](../scripts/check_rojo_artifact.py) checks a text `.rbxlx` and a sourcemap together (Python 3.11+; build both with the project's pinned Rojo):

- `--require-path` asserts a full DataModel-relative path in both. A sourcemap rooted below DataModel keeps its root name as the first segment.
- `--require-path-fragment` and `--forbid-path-fragment` are substring matches, for exclusion classes such as `.story`.
- `--singleton-class` requires exactly one instance of a class in each.
- It doesn't check per-path classes, `RunContext` or execution; add project assertions for those.

To make it a project gate, copy it into the repository with a note of its origin and call it from the check command; a path into one machine's installed skill folder is fine for a probe, not a gate. Break-test it once: move an entrypoint to the wrong service or map it twice, remove a required dependency, leak dev content, and confirm each fails.

## Dev and release builds

When a project has dev-only content (stories, specs, previews, dev tools), decide ship or exclude for each. One verified Rojo 7.7 shape: `common.project.json` holds the full tree, and thin wrappers point at it. The dev wrapper (`default.project.json`, used by `rojo serve`, the sourcemap and luau-lsp) adds nothing; the release wrapper drops dev files:

```json
{
  "name": "Example Release",
  "globIgnorePaths": [
    "**/*.story.luau",
    "**/*.spec.luau",
    "**/Preview"
  ],
  "tree": {
    "$path": "common.project.json"
  }
}
```

- Globs match paths relative to the project file's directory. `**/Preview` drops an `init`-backed directory and everything under it; `**/Preview/**` alone leaves the directory's own ModuleScript. `!` negation works from 7.7.0.
- Packages can ship their own dev files (a dependency's `init.spec.lua`); include them in the patterns.
- Never add a service beside a wrapper's root `$path`. On 7.7.0 and 7.7.1, `rojo build` then emits that service twice, while `rojo sourcemap` shows one and silently drops the wrapper's children.
- In the release build, assert each dev-only item is absent and each singleton service appears once. Keep excluded dev source in type checks and tests.
- A dev-only module that a loader starts can reach a published place through the dev sync. Make it return early unless `RunService:IsStudio()`.
- If Studio owns content Rojo doesn't map (Workspace, lighting, models), publish from Studio after syncing the release wrapper. Never publish a `rojo build` place: it holds only the mapped code and would replace everything else.

## Live sync

- Prefer `rojo build` or `rojo sourcemap` when a static check is enough.
- Before `rojo serve`, set the safeguards the version supports: `servePlaceIds` (the plugin refuses any other place), `blockedPlaceIds`, `serveAddress`, `serveAllowedHosts`. Confirm the intended place before connecting Studio. If several wrappers serve, give them the same `servePlaceIds`, and guard it ([guards](checks.md#guards)).
- `rojo syncback` writes the filesystem: treat it as a [migration](migration.md), with a recovery path and a reviewed diff.

## Sources

- [Project format](https://rojo.space/docs/v7/project-format/), [Sync details](https://rojo.space/docs/v7/sync-details/)
- [Releases](https://github.com/rojo-rbx/rojo/releases), [Changelog](https://github.com/rojo-rbx/rojo/blob/master/CHANGELOG.md)
