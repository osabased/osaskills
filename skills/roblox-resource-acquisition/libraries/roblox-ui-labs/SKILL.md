---
name: roblox-ui-labs
description: UI Labs (PepeElToro41/ui-labs) Roblox Studio storybook plugin, pinned 1.6.1. Use when writing .story or .storybook modules (Vide, generic or function stories, controls, props.target, storyRoots), when stories don't appear or don't clean up, or when installing and verifying the plugin file. Not for gameplay UI logic outside stories.
---

# UI Labs 1.6.1

Pinned target: plugin release `v1.6.1` (source reviewed 2026-10-02). [resource.yaml](resource.yaml) holds the exact identity, including the `Plugin.rbxm` SHA-256. The plugin's version is separate from the UI Labs utility package's version.

## Check the pin

The installed plugin file can change without any project lock changing, so check it before relying on version-specific behavior. If the `roblox-resource-acquisition` skill is available, load it and run the asset check its `references/child-usage.md` describes, passing the installed plugin file with `--asset`. If the parent, Python, or the plugin file is unavailable, compare what you can (the toolbar name, the installed file's hash) and say which checks were skipped. On a `FAIL` result or an observed mismatch, tell the user and keep the project's pin; continue with API you can confirm at the project's version, and stop only where the task depends on version-specific behavior. Stop on a blocked use noted in the project's `CLAUDE.md`.

## Core API

| Story shape | Module returns | Notes |
| --- | --- | --- |
| Function story | `function(target: Frame) ... return cleanup end` | Mount under `target`; UI Labs calls `cleanup` on unmount. |
| Vide story | `{ vide = Vide, controls = {...}?, story = function(props) return instance end }` | Runs once inside `vide.mount(..., target)`. `props.controls.X` is a Vide Source. `props.target` is the frame. `Vide.cleanup` works. |
| Generic story | `{ controls = {...}?, render = function(props) ... return cleanup end }` | `props.target`, `props.controls` (initial values), `props.converted`, and `props.subscribe(fn(values, infos)) -> unsubscribe`. |
| Storybook | `{ name = "UI"?, storyRoots = { folder, ... }, groupRoots = true? }` | Groups the stories found under `storyRoots`. Stories outside every book show under "Unknown Stories". |
| Primitive controls | `controls = { Title = "Hi", Count = 3, Visible = true, Tint = Color3.new(1, 0, 0) }` | Strings, numbers, booleans and Color3 become editable controls. |

Advanced stories may also set `summary` (rich text). React, Roact, Fusion and Iris stories use their own keys; see the upstream docs.

File naming: a story is a ModuleScript whose name ends in `.story` (for example a `Button.story.luau` file in Rojo). A storybook ends in `.storybook`. UI Labs runs each story in a sandboxed environment with its own `require` cache.

## Example

```luau
-- src/client/Stories/InventoryButton.story.luau
local Vide = require(ReplicatedStorage.Packages.vide) -- use the project's mapped path
local InventoryButton = require(script.Parent.Parent.Components.InventoryButton)

return {
	vide = Vide,
	controls = { Label = "Bag", Count = 3, Enabled = true },
	story = function(props)
		local c = props.controls -- each entry is a Vide Source
		Vide.cleanup(function() print("story unmounted") end)
		return InventoryButton({
			label = function() return `{c.Label()} ({c.Count()})` end,
			enabled = c.Enabled,
		})
	end,
}
```

## Gotchas

- Stories must not yield. If a Vide story yields, UI Labs warns and renders nothing; the yielded thread may still finish later, outside the story's scope. Load data before the story, or use mock data.
- With function stories, a story that errors before returning its cleanup leaks whatever it mounted (the docs say a Studio restart may be needed). Clean up partial work yourself before rethrowing.
- In a Vide story, return the component; don't call `Vide.mount` again inside. UI Labs owns the scope and calls `vide.step(0)` on its sandboxed Vide copy at unmount. Never copy that `step(0)` into gameplay code.
- Keep stories and storybooks in development-only Rojo mappings that release builds exclude. Use mock state: no DataStores, no purchases, no live remotes.
- A plugin loaded from a local `.rbxm` file, including the verified release file, is named `UI Labs (DEV)` (widget `UILabs(DEV)`); a Creator Store install is `UI Labs` (`UILabs`). When both appear, find out which one is under test before judging a bug.

## Read further

- The Vide mounter's lifecycle, the controls API, Environment helpers and story discovery: read [API and lifecycle](references/api-and-lifecycle.md).
- Installing or verifying the plugin file: read [setup](references/setup.md).
- A missing story, nil controls, duplicate widgets or a stale preview: read [troubleshooting](references/troubleshooting.md).
