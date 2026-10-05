---
name: roblox-ui-labs-1-6-1
description: Use for UI Labs Studio plugin 1.6.1 installation, story discovery, Vide story contracts and preview troubleshooting; exclude gameplay UI component implementation, generic plugin management and dependency selection/upgrades.
---

# UI Labs Studio plugin 1.6.1

Reviewed target: `1.6.1`, source reviewed 2026-10-02. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve `PROJECT` to the affected project root, `CHILD` to this installed directory, and `PARENT` from the available `roblox-resource-acquisition` skill location. Read its `references/child-usage.md` once per task and apply first-use freshness, guard and repair rules. Project resolution failure is unknown state and enters parent reconciliation.

Policy is required: the exact installed asset and full matching lifecycle inputs are checked before version-sensitive use. Run:

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --asset "INSTALLED-ASSET"
python "PARENT/scripts/check_resource_status.py" --pair "CHILD" "PROJECT/.agents/roblox/resources/records/ui-labs.yaml"
```

Only `HEALTHY` permits ordinary use. `BLOCKED`/`UNKNOWN`, mismatched pins, verifier drift, hard defects or invalidated repair evidence enter the parent's reconciliation path. A recurring safe workaround still activates parent repair diagnosis.

## Common use

- Open UI Labs from Studio's toolbar in edit mode. Locally installed release files use the source's `UI Labs (DEV)` toolbar and `UILabs(DEV)` widget names; the standard installation uses `UI Labs`/`UILabs`.
- Locate the mapped `.story` ModuleScript in Story Explorer. For Vide return a table with `vide = Vide`, scalar `controls` values and `story = function(props)` returning a GUI component inside the scope UI Labs already owns.
- Read controls as Sources, e.g. `props.controls.Title()`. Pass typed getter adapters to the component. Do not create an independent gameplay mount inside the story; it would hide cleanup ownership from the preview host.
- Select the story, vary controls, stop/remount it and check Output. Repeat for reload when that behavior is claimed. Keep discovery/construction, preview execution, real input/layout and diagnostics as separate results.

## Ownership and critical constraints

Keep stories in development-only mappings. UI Labs owns the Vide preview scope; return the story component inside that scope and avoid an independent gameplay mount. Stories must not yield. Register Instance cleanup immediately and invalidate story-owned pending work before teardown. Inspect the loaded widget identity to distinguish duplicate installations.

UI Labs runs as an editor plugin, not as a gameplay client/server startup dependency. Keep story modules and fixtures in development-only mappings; release builds must exclude them. The chosen UI framework remains a client runtime dependency. Server gameplay and client-action validation retain server authority; editor previews must use local/mock state and must not run live persistence or privileged actions.

## Complete and read further

Run `python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --asset "INSTALLED-ASSET"`; require exit 0 and JSON `status: PASS` with this exact resource selector and the asset-integrity lane. Use the project's source/build checks for authored consumers and generated placement. These checks establish identity/static integration; runtime, rendering, input and clean-diagnostics claims require their own project evidence.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- When changing API usage, activation, partial acquisition or teardown, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
