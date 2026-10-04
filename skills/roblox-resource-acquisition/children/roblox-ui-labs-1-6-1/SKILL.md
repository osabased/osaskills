---
name: roblox-ui-labs-1-6-1
description: "Use for UI Labs Studio plugin 1.6.1 installation, story discovery, Vide story contracts and preview troubleshooting; exclude gameplay UI component implementation, generic plugin management and dependency selection/upgrades."
---

# UI Labs Studio plugin 1.6.1

Use **UI Labs** for Studio story previews. Guidance targets **1.6.1** (source reviewed **2026-10-02**). Resource verification: **verified**.

The official release asset and project-owned Studio fixtures proved edit-mode story discovery, representative preview rendering/input, a reactive disabled control, scope disposal and fresh remount. Resolve exact-target proof through the active project's matching record; this is not a universal hot-reload, cross-device or clean-console claim. Generated guidance has an advice-only claim boundary.

## Use when

- Installing/reconciling the already-selected UI Labs Studio plugin 1.6.1.
- Authoring its plain advanced Vide story table, diagnosing discovery and verifying preview scope ownership.

## Do not use when

- Implementing gameplay components without a story/plugin issue; use the selected UI framework's guidance.
- Managing an unrelated Studio/Codex plugin, selecting/upgrading dependencies, or doing a tiny native property edit.
- The project's selected plugin target differs; preserve its target and find exact-target guidance.

## Prerequisites and installation

Resolve `<project-root>` from the supplied active project and `<child-skill-directory>` from this loaded `SKILL.md`. Resolve `<parent-skill-directory>` from the installed `roblox-resource-acquisition` skill's loaded location; prefer the active project's `.agents/skills` copy when present, otherwise use the host's discovered skill location. Substitute these placeholders with actual paths before executing commands, quote paths containing spaces, and run project commands from `<project-root>`. Checker inputs resolve against that project; never infer it from the shared skill's location. Default adoption of a bundled child is project-local.

The parent `roblox-resource-acquisition` skill must be installed for status and repair checks. Its Python scripts require PyYAML; restore that prerequisite with `python -m pip install -r <parent-skill-directory>/requirements.txt` in the selected Python environment.

1. Use Roblox Studio, Python 3.11+ for the read-only helper and the active project's selected plugin metadata. The documented project installer requires Windows and PowerShell 7.2+; on other hosts use the verified official asset through Studio's local plugin folder. This target is the plugin release `v1.6.1`, not the utility package's unrelated version. The official asset is https://github.com/PepeElToro41/ui-labs/releases/download/v1.6.1/Plugin.rbxm with SHA256 `c785b1fc2593d633ad3dba51aeb778cee3026393574b99438fa276ad31d5283b`.

For a project with the maintained pinned installer, run `pwsh scripts/install-studio-plugins.ps1`. It caches/downloads the exact release, verifies the digest, backs up a differing managed local plugin and installs `UILabsManagedPlugin.rbxm` in Studio's local Plugins folder. On other hosts resolve Studio's local plugin folder through Studio; verify the same digest before placing the official asset. Restart/reload Studio if it has not discovered the new file. Inspect existing installations and widget names before diagnosing duplicate entries; do not delete unrelated/account-managed plugins.

Story ModuleScripts end in `.story` and must be present in the development DataModel. A plain Vide story table needs the selected Vide package but no UI Labs utility package.

## On-demand maintenance

- Promotion guard: At activated use, check `<skill-directory-parent>/.skill-maintenance/<skill-directory-name>.json`; ordinary dependent use waits while it exists. Controlled candidate validation is separate.
- Freshness triggers: Relevant current claims, acquisition/upgrade, source drift, consequential practices or reusable defects invoke `roblox-resource-acquisition` once for the affected scope and its `references/on-demand-maintenance.md`. Carry the selected identity, claim and reproduction; do not recursively reopen an active handoff.
- Target and economy: Resolve the project's exact target and local compatibility guidance first. Healthy immutable-target use does not need unrelated latest-release research. The parent may apply tested factual repairs within its approved authority; dependency versions, architecture and changed practices return to their owner. No scheduled upkeep.

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode when this guidance requires guessing, bypassing instructions, repeating a workaround, or an undocumented adjustment likely to recur. A harmless one-off task-local adjustment is not an interrupt.
- Hard defect: Stop dependent work for unreliable correctness, security, canonical identity, selected version or verification; enter parent state reconciliation and the repair loop before continuing.
- Soft defect: Safe reversible immediate work may continue, but invoke parent repair diagnosis and surface the reproduction, workaround and durable correction before completion. Soft diagnosis does not force unrelated provenance reconciliation.
- Handoff: Capture the task, installed state, expected behavior, observed behavior, smallest reproduction, workaround and proposed durable correction. Parent invocation authorizes diagnosis and reporting, not unrestricted edits. Use current task authorization or the parent's applicable standing factual-repair grant in `references/on-demand-maintenance.md#approved-authority` for edits.

## Common path

1. Resolve the active project, exact plugin target and local plugin folder. Because the plugin is independently mutable, complete the required Installed-state and Parent-state checks below before version-sensitive use.
2. Open UI Labs from Studio's toolbar in edit mode. Locally installed release files use the source's `UI Labs (DEV)` toolbar and `UILabs(DEV)` widget names; the standard installation uses `UI Labs`/`UILabs`.
3. Locate the mapped `.story` ModuleScript in Story Explorer. For Vide return a table with `vide = Vide`, scalar `controls` values and `story = function(props)` returning a GUI component inside the scope UI Labs already owns.
4. Read controls as Sources, e.g. `props.controls.Title()`. Pass typed getter adapters to the component. Do not create an independent gameplay mount inside the story; it would hide cleanup ownership from the preview host.
5. Select the story, vary controls, stop/remount it and check Output. Repeat for reload when that behavior is claimed. Keep discovery/construction, preview execution, real input/layout and diagnostics as separate results.

## Operational reconciliation

- Policy: required — local Studio plugin files and account/plugin-manager installations can change independently of project manifests.
- Installed-state check: Run `python <child-skill-directory>/scripts/check_install.py --metadata tooling.json --plugin-dir RESOLVED-STUDIO-PLUGINS-DIRECTORY` after resolving the active project root and folder. It checks version, canonical release URL, managed filename and actual installed asset SHA256. On Windows the folder is under the current user's LocalApplicationData Roblox/Plugins. Also inspect the loaded widget identity so another installation is not mistaken for this one.
- Expected identity/state: slug `ui-labs`, https://github.com/PepeElToro41/ui-labs, plugin 1.6.1 official asset digest `c785b1fc2593d633ad3dba51aeb778cee3026393574b99438fa276ad31d5283b`; no package identity applies to this plugin.
- Current-block check: Before affected use run `python <parent-skill-directory>/scripts/check_resource_status.py --pair <child-skill-directory> MATCHING-RECORD.yaml` using the resolved matching record. Proceed only on HEALTHY (exit 0); BLOCKED or UNKNOWN enters full parent-state reconciliation.
- Parent-state check: Prefer an explicitly supplied authoritative record. Otherwise resolve the affected project root and read its schema-version 3 record `.agents/roblox/resources/records/ui-labs.yaml` and resource-bound learnings in `.agents/roblox/resources/learnings/`. If this project-scoped child's project cannot be resolved, report UNKNOWN state and invoke roblox-resource-acquisition in repair/reconcile mode; do not silently switch to global records. Only for an explicitly user/global-scoped child with no applicable project root, use `~/.roblox-resources/records/ui-labs--1-6-1.yaml` and `~/.roblox-resources/learnings/`. Match slug `ui-labs` and canonical identity.
- Mismatch/unknown action: Stop affected version-sensitive use and invoke `roblox-resource-acquisition` in `repair/reconcile` mode when installed identity/version, parent state or current block is unknown or mismatched. Adoption/upgrades, invalidated repair evidence, verifier drift and hard defects also require this route.
- Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth.

## Client/server placement

UI Labs runs as an editor plugin, not as a gameplay client/server startup dependency. Keep story modules and fixtures in development-only mappings; release builds must exclude them. The chosen UI framework remains a client runtime dependency. Server gameplay and client-action validation retain server authority; editor previews must use local/mock state and must not run live persistence or privileged actions.

## Mental model

The plugin discovers story modules, loads them into a preview environment, mounts their returned GUI and owns that preview lifetime. Controls are preview inputs, not gameplay state. Framework-specific advanced contracts tell the host how to convert controls and own cleanup; the Vide contract differs from a generic target-and-cleanup callback.

## Lifecycle and cleanup

Initialization: The editor plugin owns the widget lifetime and creates toolbar/widget infrastructure in edit mode. Enabling its widget first creates the plugin's React root and Story Explorer; hiding the widget alone does not unmount that root. The Stop toolbar action unmounts it and resets state; plugin unloading unmounts/reset/disconnects its toolbar/widget connections. Studio owns the plugin's engine GUI teardown.

Reuse: Select/remount the same story through the host instead of retaining a second independent preview. Hide/show can reuse the editor root; Stop resets its state.

Cleanup/destruction: Cancel or invalidate story-owned pending tasks and waits before teardown. UI Labs 1.6.1's Vide mounter creates a control-source scope and a story scope. It converts controls to Sources, calls `vide.mount` around the story, and updates sources when controls change. During preview unmount it calls `vide.step(0)` on that preview's Vide environment, starts protected story disposal, then disposes the source scope. Component-owned Instances still require `Vide.cleanup`. Do not attach unrelated host-global finalizers or create a second uncontrolled mount.

Stories must not yield. Establish scope-owned cleanup immediately before fallible construction; invalidate/cancel any owned pending callbacks on teardown. Vide 0.4.1 cleanup uses insertion order and does not promise error continuation, so keep cleanup callbacks nonthrowing and avoid depending on unsupported order. Gameplay mounts outside UI Labs retain their own idempotent disposal owner.

## API used by this skill

The plugin has no supported public Luau mount method to invoke from gameplay. Its supported authoring interface here is the returned story table: `vide`, `controls`, `story(props)`, with `props.controls` carrying Sources. The project installer and read-only checker are tooling commands. Do not invent `UILabs.mount`, `UILabs.reload` or use internal Reflex actions as a production API.

## Failure modes

### Installation or lifecycle symptom

- Missing story: confirm the ModuleScript suffix is `.story`, development mapping includes it, source returns the correct table and Studio/Rojo loaded the current source. Build success alone does not prove plugin discovery.
- Nil `props.controls` or missing cleanup: check the selected advanced Vide contract and pass the same Vide package through `vide`; avoid nesting gameplay mounts.
- Multiple widgets: identify local `UILabs(DEV)` versus standard `UILabs` installations before interpreting results. Preserve unrelated plugin ownership.
- Stale preview or repeated reload leakage: reduce to one story, stop/remount and retain Output plus exact version. Diagnose with the parent repair workflow; source review is not a hot-reload pass.
- Installer/hash failure: compare official release URL, expected digest and actual bytes. Preserve the previous managed asset; never bypass the digest to finish setup.

## Limitations

- The plugin and utility-package versions differ. This skill targets only plugin 1.6.1 with plain Vide controls. Utility helpers, custom control ranges, StyleSheet previews, pixel-layout correctness and real input/hot reload need separate source review and execution. Plugin auto-update or a different loaded installation cannot inherit this exact release proof.

## Security notes

Studio plugins execute editor code with authoring privileges. Download the canonical exact release, verify its digest and preserve the managed asset's identity. Stories execute arbitrary project code: use local fixtures/mock data, keep credentials and live service actions out, and do not publish or mutate production data merely to prove a preview. Keep gameplay authorization server-owned.

## Verify after installation

Executable fixture: not-applicable — this generated guidance claims advice/instruction correctness only; the active project maintains its strict story/plugin fixtures and records their execution independently.

Run: `python <child-skill-directory>/scripts/check_install.py --metadata tooling.json --plugin-dir RESOLVED-STUDIO-PLUGINS-DIRECTORY`, then open the matching widget in Studio and select the mapped story using the Common path.

Pass condition: The check exits with code 0 and prints PASS reporting plugin 1.6.1 with the expected official asset digest. Studio must then show the actual Story Explorer and selected story; control changes and stop/remount must have separately observed results before claiming preview behavior.

Evidence boundary: Digest/version proves installation, widget/discovery proves only those host lanes, and the companion story's direct Vide fixture proves its engine contract. None alone proves UI Labs preview rendering, actual input, hot reload, normal client startup or clean diagnostics.

## Alternatives

- Use a development-only PlayerGui workbench to preview one component with explicit gameplay mount cleanup. Other story hosts or framework-specific test tools may suit different needs. Preserve an already-selected UI Labs target; an alternative or upgrade remains a decision for the project's owning authority.

## Provenance

- Resource slug: ui-labs
- Package identity: no package identity exists
- DevForum: no DevForum topic used
- Canonical source/docs: https://github.com/PepeElToro41/ui-labs
- Source version/release/commit: 1.6.1
- Source review date: 2026-10-02
- Resource verification: verified

## Version drift

Re-check release notes, the official asset, story recognition, Vide mounter control/cleanup behavior and plugin bootstrap before selecting a newer version. Keep utility-package releases separate from plugin releases. Preserve existing project pins and rerun affected host/instruction/routing checks after an authorized update.

