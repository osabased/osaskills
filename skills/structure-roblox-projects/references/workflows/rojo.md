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

## Validate runtime topology

When establishing or changing a setup's mapping/startup verification, parse the generated sourcemap and assert the complete runtime paths, instance classes, source identities, and unique critical entrypoints required by the selected architecture. For each critical entrypoint, check its expected source at the intended path and count that source across the whole tree: a second mapping under a different name or parent is still a duplicate. Check required shared dependencies as well as their bootstraps. A matching name, filename, or serialized JSON fragment anywhere in the tree does not prove its parentage or execution boundary. Apply equivalent path/class checks to the built place when claiming the distributable's topology is verified; source filenames need not survive in the place format.

Qualify the checker with separate negative probes for moving a critical entrypoint to an incompatible service, removing a required dependency, and mapping an existing entrypoint source a second time under another runtime path. Each probe must fail for its intended structural violation; record each result before claiming topology qualification complete. Derive the expected boundaries from the intended architecture independently of the mapping under test; copying the current mapping into expected values can validate the same mistake twice. Integrate the assertions into the project-owned canonical gate. This does not require separate development/release profiles or live Studio proof for a static topology claim.

## Development and release artifacts

Apply this section only when the task creates or changes development-only UI/test content or distinct development/release artifacts. Preserve an established coherent composition unless the request includes changing it.

1. Record explicit ship/exclude intent for every authored demo, story, preview, and development bootstrap. A module without a startup entrypoint can still be present in a sourcemap or place file, so startup inspection cannot establish release exclusion.
2. Preserve the project's existing mapping source of truth. When new profiles are actually needed, choose a composition that derives them without copying runtime mappings or duplicating singleton services. Assert the generated development and release artifacts rather than trusting filenames, directory moves, or ignore configuration alone.
3. In both the parsed sourcemap and a parsed text place build, require exact paths for the affected runtime entrypoints, feature roots, and their required shared/network dependencies. Surviving entrypoints alone do not prove that their dependencies survived. Likewise, require the development preview's actual implementation and story paths in its development artifact; a similarly named bootstrap cannot establish subtree retention. In release, prove that every development-only sentinel is absent. Count singleton services affected by composition and require exactly one of each.
4. Keep excluded development source in strict analysis and applicable test discovery. Release exclusion is an artifact boundary, not permission to stop checking the source.

For pinned Rojo 7.7, one verified candidate is a shared project containing the complete tree and thin wrappers whose tree is only `{ "$path": "common.project.json" }`. Use this shape only when it fits the established workflow or the authorized setup; it is not a reason to replace another coherent composition. A release wrapper can add project-level ignore paths:

```json
{
  "name": "Example Release",
  "globIgnorePaths": [
    "**/*.story.luau",
    "**/Preview",
    "**/Preview/**"
  ],
  "tree": {
    "$path": "common.project.json"
  }
}
```

The passing 7.7 probe used both the directory-node and descendant patterns. Its earlier failed pattern was `client/Preview/**`, so the evidence does not isolate path-prefix mismatch from descendant matching. Inspect both generated outputs and ensure the `init`-backed directory node itself is excluded; treat the dual pattern above as a verified example rather than a general claim about every descendant glob. Do not add a second `ReplicatedStorage` or other singleton service beside the root `$path`; that probe produced duplicate service instances. Recheck this behavior against the project's actual Rojo pin and generated outputs before relying on it in another version. Adapt names and paths to the project rather than introducing `common.project.json`, `Preview`, or these profiles as universal conventions.

For repeatable checks, use [`../../scripts/check_rojo_artifact.py`](../../scripts/check_rojo_artifact.py) when its text `.rbxlx` and sourcemap inputs fit the project. Use exact `--require-path` assertions for retained runtime sentinels; required paths are relative to the DataModel and must match a complete instance path. The checker removes a sourcemap's DataModel root name and an optional `.rbxlx` DataModel wrapper. When a sourcemap is rooted below DataModel, its root name remains the first path segment and the checker does not infer absent parent services. Clearly named required/forbidden fragment options remain available for cases such as `.story` suffix filtering. The checker rejects empty invariants and invocations with no invariants. It accepts arbitrary artifact paths and singleton classes. Build the artifacts separately with the project's pinned Rojo; the checker does not install or require Rojo and does not choose project names or mappings.

When adopting these assertions as a project gate, make the checker a repository-owned, versioned tool (or use an equivalent existing project tool), record its provenance, and declare its runtime in CI. Invoke it from the canonical build/release verification path on the project's supported platforms. A command that reaches into one developer's installed skill directory is suitable for an evaluation probe, not a portable project gate.

Test the project's selected assertions as well as the generic checker: removing an implementation subtree while retaining a similarly named bootstrap, removing a required server/shared dependency while retaining entrypoints, and leaking development content must each fail. Mutate either artifact independently so a clean sourcemap cannot hide a broken place build. Fragment matching is useful for exclusion classes such as `.story`; use exact paths for identity and required-content claims.

## Observable client previews

Apply this section when a Rojo-backed development workflow is intended to prove rendered client behavior or actual input.

- Supply the preview through the filesystem/Rojo source of truth and an established normal client startup path in the same Studio session exposed to the available input, inspection, console, and screenshot tools. A development-only lifecycle root is valid when it preserves the established loader contract and is excluded from release by the artifact checks above.
- Preserve active Script Capabilities boundaries and loader semantics. Do not widen capabilities, move scripts between incompatible capability containers, inject code through a privileged tool, or replace the project's startup path merely to make a preview run. Read [`../platform/script-capabilities.md`](../platform/script-capabilities.md) when that branch is active.
- Before interaction, verify a source fingerprint that covers the exact source bytes being served, including uncommitted edits, plus the effective project configuration and an expected UI marker. A commit hash alone cannot identify dirty content.
- Use actual pointer and text events for input claims, inspect observable state and console output, and capture the material rendered states. Calling the domain callback directly establishes domain behavior only. Stop only the play/serve session started by the task and preserve user-owned sessions.
- UI Labs can complement this path for isolated states and variants. Treat any bridge between its host and the available Studio interaction tools as unproved until the same-session workflow succeeds end to end.

State the planned observable path concretely even when execution is unavailable: the exact client entrypoint and preview/story path, expected UI marker, input event to perform, rendered/state change to observe, and console condition. Artifact inclusion/exclusion checks establish composition only; they do not establish rendering or input wiring. If the same-session client path cannot run, report those claims as unavailable and keep the artifact results separate.

A development-tooling answer is complete only when it names the retained runtime sentinels, excluded development sentinels, singleton services to count exactly once, and the concrete observable-client path above. Do not substitute “document or verify later” for these assertions. Report executed evidence separately from the planned check so unavailable Studio access never becomes a fabricated pass.

If the blocker is whether a third-party preview/test library or integration actually supports the needed runtime, route that bounded evidence question to the available Roblox resource-acquisition workflow. Keep Rojo composition, source-of-truth, and startup topology decisions in this skill.

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
