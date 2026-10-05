---
name: roblox-rojo-build-contract
description: Use pinned Rojo 7.7.0 to build XML places and verify project-owned script contracts; excludes live Studio synchronization and gameplay execution.
---

# Rojo build contract

Reviewed target: `7.7.0`, source reviewed 2026-09-30. The [resource contract](resource.example.yaml) owns static identity; project records own current execution evidence. This authoring example carries no executed upstream or host proof.

## Choose the task

- An authorized project needs a reproducible CLI build with an independent script-presence contract.

- The requested proof needs live Studio synchronization, physics or gameplay execution.

## Before use

Resolve the affected project, this child and the available installed parent. Read the parent's references/child-usage.md once per task for freshness, guards, reconciliation and repair. Project resolution failure is unknown state with no global fallback. This required custom profile needs its documented exact-target check before version-sensitive use. The shared checker reports custom checks unavailable and never executes metadata-supplied commands.

The child-owned build checker validates canonical tool identity, exact version and executable hash from the project tool lock before invoking the CLI. Read [setup](references/setup.md) for required project-owned inputs.

Run `python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/rojo-rbx-rojo.yaml"`; require HEALTHY. BLOCKED/UNKNOWN or mismatched identity enters parent repair/reconcile before affected use.

## Common use and ownership

Use `scripts/check_build.py` against the project's actual configuration and independent expected contract. The representative source in `scripts/smoke_build.py` generates disposable inputs outside this child and demonstrates both a valid mapping and an omitted server mapping. Keep project-specific integration fixtures and contracts in the project rather than maintaining a second example here.

```powershell
python "$Child/scripts/check_build.py" --rojo "$Rojo" --tool-lock "$Project/tool-lock.json" --project "$Project/default.project.json" --expected "$Project/expected-scripts.json" --output "$Project/build/place.rbxlx" --report "$Project/build/report.json"
```

Rojo maps authored files into a DataModel. Process success proves it built that mapping; it does not prove the mapping contains the project's intended scripts. An independent contract checks the resulting XML before publishing the last-good output.

- Initialization: The invocation owner selects the executable, lock, input project and output paths before starting the build process. Each verifier call owns a temporary build directory and its report.
- Reuse: Repeated builds reuse project-owned inputs and replace the requested output only after its content checks pass.
- Cleanup/destruction: TemporaryDirectory removes the temporary build after success or failure. A failed build or contract check leaves the previous output byte-identical. There are no pending waits or spawned gameplay tasks; the helper's subprocess timeout bounds its owned command, and no long-running serve process is started.
- Ownership boundary: The helper owns only temporary build files, the requested successful output and explicit report. It does not remove project source, tool-manager caches or a developer's Studio process.

Rojo exposes no callable API for this workflow. Use `rojo --version` and `rojo build PROJECT --output PLACE.rbxlx` through the helper; these command/configuration behaviors are separate from engine execution.

Engine client/server placement is not applicable to the Rojo CLI process. Its project configuration places generated Script, LocalScript and ModuleScript instances; verify their actual classes and sources without claiming that those scripts executed.

## Complete and read further

Executable fixture: scripts/smoke_build.py

Run: Execute `python "$Child/scripts/smoke_build.py" --rojo "$Rojo" --tool-lock "$Project/tool-lock.json" --workspace "$Project/build/qualification" --report "$Project/build/qualification.json"` in an isolated project; choose a fresh fixture workspace. Then run the Common path against the active project's maintained configuration, source and independent expected contract.

Pass condition: The command exits 0 and report status is passed; the happy build has three matching script classes/sources; omission exits 1 identifying `ServerScriptService/Main`; the last-good output remains byte-identical and no `.rojo-build-*` directory remains.

Evidence boundary: Fake-tool tests prove wrapper behavior only. Actual pinned CLI execution proves the observed build behavior; neither establishes Studio gameplay, project strict analysis, independent child usability or operational host activation.

- For installation/configuration, read [setup](references/setup.md).
- For the named failure symptoms and security constraints, read [troubleshooting](references/troubleshooting.md).
