---
name: roblox-rojo-build-contract
description: Use pinned Rojo 7.7.0 to build XML places and verify project-owned script contracts; excludes live Studio synchronization and gameplay execution.
---

# Rojo build contract

Use Rojo to build a place and verify expected script classes and sources. Guidance targets **7.7.0** (source reviewed **2026-09-30**). Resource verification: **unverified** in this illustrative record. This is a worked tool-child example, with no independent child or operational host claim.

## Use when

- An authorized project needs a reproducible CLI build with an independent script-presence contract.

## Do not use when

- The requested proof needs live Studio synchronization, physics or gameplay execution.

## Prerequisites and installation

1. Resolve the project-owned target and installation before using the common path.

Resolve the active project's selected tool and configuration. This example models a child installed at project/repository scope; an unresolved project does not authorize a user/global fallback. Use Python 3.10+ and the canonical `rojo-rbx/rojo` 7.7.0 executable. A broken PATH shim may have an already installed versioned executable in the configured tool-manager cache; confirm `rojo --version` and its integrity before use.

Keep project-specific files outside this child. The project owns `tool-lock.json` containing `canonical_url: https://github.com/rojo-rbx/rojo`, `package_id: rojo-rbx/rojo`, `version: 7.7.0` and `sha256` as the raw SHA-256 hex of the inspected executable. This helper's lock format uses raw hex; schema-v3 evidence-input hashes separately require the `sha256:` prefix. The project also owns a Rojo JSON configuration, authored strict Luau source and `expected-scripts.json` with a `scripts` list of objects containing `path`, `class` and `sourceFile`. Build the expected paths from the intended project contract, independently from Rojo's mapping: a successful build can omit a whole directory.

In the commands below, PowerShell variables `$Parent`, `$Child`, `$Project` and `$Rojo` hold the resolved absolute installed parent directory, canonical child directory, project root and inspected executable. Another shell uses equivalent path arguments. Do not embed a task's machine-specific paths into this reusable child.

## On-demand maintenance

- Promotion guard: Check the sibling `.skill-maintenance/<skill-directory-name>.json`; ordinary use waits while it exists.
- First-use freshness: Before this tool's first use in a task, apply the installed parent's `references/on-demand-maintenance.md#first-use-freshness-check`. Compare canonical stable releases and relevant documentation with the installed/project-pinned version, reuse unchanged checks within the task, and disclose unavailable lookups.
- Freshness triggers: For relevant current tool claims, adoption/upgrade, source drift, recurring workaround or reusable defects, invoke `roblox-resource-acquisition` for the affected target and read its `references/on-demand-maintenance.md`.
- Target and economy: Preserve the project owner's chosen version after the freshness comparison. A newer release alone does not require full requalification or invalidate exact-target proof; changed versions/practices return to the owner.

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode for guessing, bypassed instructions, repeated rediscovery or an undocumented workaround likely to recur; a harmless task-local adjustment is not an interrupt.
- Hard defect: Stop dependent work when correctness, security, canonical identity, selected version or verification is unreliable; enter parent reconciliation and repair.
- Soft defect: If a workaround is safe and reversible, immediate work may continue, but invoke parent repair diagnosis and surface the reproduction, workaround and durable correction before completion.
- Handoff: Record the task, installed state, expected and observed behavior, smallest reproduction, workaround and proposed durable correction. Parent activation authorizes diagnosis and reporting, not edits without current authorization.

## Common path

Use `scripts/check_build.py` against the project's actual configuration and independent expected contract. The representative source in `scripts/smoke_build.py` generates disposable inputs outside this child and demonstrates both a valid mapping and an omitted server mapping. Keep project-specific integration fixtures and contracts in the project rather than maintaining a second example here.

```powershell
python "$Child/scripts/check_build.py" --rojo "$Rojo" --tool-lock "$Project/tool-lock.json" --project "$Project/default.project.json" --expected "$Project/expected-scripts.json" --output "$Project/build/place.rbxlx" --report "$Project/build/report.json"
```

## Operational reconciliation

- Policy: required — a project's tool manager or executable can drift independently from the guidance.
- Installed-state check: Compare the canonical URL, package identity, version and executable hash in the project's tool-lock against the selected executable; the helper checks the hash and version before building.
- Expected identity/state: rojo-rbx-rojo + https://github.com/rojo-rbx/rojo + rojo-rbx/rojo + 7.7.0.
- Current-block check: Before affected use, run `python "$Parent/scripts/check_resource_status.py" --pair "$Child" .agents/roblox/resources/records/rojo-rbx-rojo.yaml` from the resolved project root; require HEALTHY, and enter full reconciliation on BLOCKED or UNKNOWN. Resolve `$Parent` and `$Child` from the applicable host/project configuration, and use another authoritative record location when supplied.
- Parent-state check: Resolve the affected project root, then read the matching schema-version 3 resource record and learnings at authoritative locations, otherwise `.agents/roblox/resources/records/rojo-rbx-rojo.yaml` and `.agents/roblox/resources/learnings/` relative to that root. If this project-scoped child's project cannot be resolved, report `UNKNOWN` and enter parent `repair/reconcile`; do not switch to global records. Only when explicitly authoring a user/global-scoped variant, document the no-project fallback at `~/.roblox-resources/records/rojo-rbx-rojo.yaml` and `~/.roblox-resources/learnings/`. Match slug plus canonical identity.
- Mismatch/unknown action: Stop affected version-sensitive use and invoke `roblox-resource-acquisition` in `repair/reconcile` mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth for defect evidence and parent activation.

## Client/server placement

Engine client/server placement is not applicable to the Rojo CLI process. Its project configuration places generated Script, LocalScript and ModuleScript instances; verify their actual classes and sources without claiming that those scripts executed.

## Mental model

Rojo maps authored files into a DataModel. Process success proves it built that mapping; it does not prove the mapping contains the project's intended scripts. An independent contract checks the resulting XML before publishing the last-good output.

## Lifecycle and cleanup

- Initialization: The invocation owner selects the executable, lock, input project and output paths before starting the build process. Each verifier call owns a temporary build directory and its report.
- Reuse: Repeated builds reuse project-owned inputs and replace the requested output only after its content checks pass.
- Cleanup/destruction: TemporaryDirectory removes the temporary build after success or failure. A failed build or contract check leaves the previous output byte-identical. There are no pending waits or spawned gameplay tasks; the helper's subprocess timeout bounds its owned command, and no long-running serve process is started.
- Ownership boundary: The helper owns only temporary build files, the requested successful output and explicit report. It does not remove project source, tool-manager caches or a developer's Studio process.

## API used by this skill

Rojo exposes no callable API for this workflow. Use `rojo --version` and `rojo build PROJECT --output PLACE.rbxlx` through the helper; these command/configuration behaviors are separate from engine execution.

## Failure modes

### Build succeeds but a script is absent

A wrong `$path` can omit an intended script. Inspect the independent expected path and source, repair the project's mapping and rerun; do not derive the expected contract from the faulty mapping.

### Tool identity check fails

A changed executable or pin does not match the reviewed target. Inspect the selected tool, invoke reconciliation and preserve the prior output; do not update the lock merely to silence the failure.

## Limitations

- XML script class/source proof covers authored builds, not gameplay, Studio plugin synchronization, runtime diagnostics or strict analysis of the project source.

## Security notes

Pin canonical source and inspect executable integrity. Do not expose credentials or start live publishing merely to prove a build. Preserve Roblox server authority when checking generated script placement.

## Verify after installation

Executable fixture: scripts/smoke_build.py

Run: Execute `python "$Child/scripts/smoke_build.py" --rojo "$Rojo" --tool-lock "$Project/tool-lock.json" --workspace "$Project/build/qualification" --report "$Project/build/qualification.json"` in an isolated project; choose a fresh fixture workspace. Then run the Common path against the active project's maintained configuration, source and independent expected contract.

Pass condition: The command exits 0 and report status is passed; the happy build has three matching script classes/sources; omission exits 1 identifying `ServerScriptService/Main`; the last-good output remains byte-identical and no `.rojo-build-*` directory remains.

Evidence boundary: Fake-tool tests prove wrapper behavior only. Actual pinned CLI execution proves the observed build behavior; neither establishes Studio gameplay, project strict analysis, independent child usability or operational host activation.

## Alternatives

- Prefer the project's existing build check when it already verifies the intended script contract. Manual Studio inspection may fit a one-off place; keep alternatives informational when the project owner selected Rojo.

## Provenance

- Resource slug: rojo-rbx-rojo
- Package identity: rojo-rbx/rojo
- DevForum: No DevForum topic is used/applicable
- Canonical source/docs: https://github.com/rojo-rbx/rojo
- Source version/release/commit: 7.7.0
- Source review date: 2026-09-30
- Resource verification: unverified

## Version drift

Before changing the selected version, inspect canonical release/source changes affecting CLI arguments, script classes and mapping behavior; rerun applicable proof. Return target changes to the owning project contract.
