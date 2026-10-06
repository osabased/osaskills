---
name: roblox-ui-labs-1-6-1
description: Use for UI Labs Studio plugin 1.6.1 installation, story discovery, Vide story contracts and preview troubleshooting; exclude gameplay UI component implementation, generic plugin management and dependency selection/upgrades.
---

# UI Labs Studio plugin 1.6.1

Reviewed target: `1.6.1`, source reviewed 2026-10-02. The [resource contract](resource.yaml) owns exact identity and check profiles. This guidance is advice-only; the affected project's matching record owns current resource execution evidence.

## Before use

Resolve the affected project and installed `roblox-resource-acquisition` parent; read its `references/child-usage.md` once per task for guards, first-use checks and repair. Policy is **required**: before version-sensitive use, verify the installed asset, run the shared record query and reconcile the full matching record/learnings. Require exit 0, `status: PASS`, selector `1.6.1`, `lane: asset-integrity`, and record query `HEALTHY`. An unknown target or block stops affected use.

```text
python "PARENT/scripts/check_resource_install.py" "CHILD" --project "PROJECT" --asset "INSTALLED-ASSET"
```

## Common use

Open UI Labs from Studio's toolbar in edit mode. Local release files use `UI Labs (DEV)`/`UILabs(DEV)` toolbar/widget names; standard installations use `UI Labs`/`UILabs`. Inspect the loaded widget identity when installations overlap.

Locate the mapped `.story` ModuleScript in Story Explorer. A Vide story returns `{ vide = Vide, controls = ..., story = function(props) ... end }` with scalar control values. Read controls as Sources, e.g. `props.controls.Title()`, and pass typed getter adapters to the component.

Select the story, vary controls, stop/remount it and inspect Output. Exercise reload when claiming that behavior. Distinguish observed discovery, construction, execution, input/layout and diagnostics.

## Ownership and critical constraints

UI Labs owns the Vide preview scope. Return the component in that scope; an independent gameplay mount hides cleanup ownership. Stories must not yield. Register Instance cleanup immediately and invalidate story-owned pending work before teardown.

Stories/fixtures stay in development-only mappings excluded from release builds. The plugin runs in the editor; the chosen UI framework remains a client runtime dependency. Preview with local/mock state, without live persistence or privileged actions. Server gameplay and validation retain authority.

## Complete and read further

Retain the pre-use `asset-integrity` result while its inputs remain unchanged. Run project source/build checks and report only the Studio lanes actually exercised. Source hashes/static integration do not prove preview execution, rendering, input or clean diagnostics.

- For installation, locked restoration or mapping compatibility, read [setup](references/setup.md).
- For additional APIs, cross-library integration or partial-acquisition/teardown recipes, read [API and lifecycle](references/api-and-lifecycle.md).
- For a matching failure symptom or a resource-specific security question, read [troubleshooting](references/troubleshooting.md).
