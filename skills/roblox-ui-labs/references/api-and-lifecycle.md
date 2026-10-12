# UI Labs 1.6.1 API and lifecycle

Everything below was checked against the `v1.6.1` tag: `src/` and `docs/en/docs/`.

## Discovery

- Story modules: ModuleScripts whose `Name` matches `%.story$`. Storybooks: names matching `%.storybook$`. The displayed name is the module name without the extension; a `name` key in a story is ignored.
- A storybook's `storyRoots` lists the Instances to search. Each subfolder becomes a folder in the explorer, and `groupRoots = true` adds one folder per root. The `roact`, `react` and `reactRoblox` keys in a storybook are ignored; put the library in each story.
- The plugin only sees what is in the edit DataModel. A successful build doesn't prove discovery; check that Rojo synced the current file.

## Vide stories, as mounted

The `VideLib` mounter (`src/UI/StoryPreview/PreviewController/Mounters/VideLib/index.tsx`) does the following:

1. Inside its own `vide.mount`, it creates one `vide.source(value)` per control.
2. It calls `vide.mount(() => story(props), MountFrame)`. `props` holds `controls` (the Sources), `target` (the mount frame) and `inputListener`. If the story yields, UI Labs warns and renders nothing; if it errors, UI Labs warns with the error.
3. When a control changes in the panel, it writes the new value into that control's Source.
4. On unmount, it calls `vide.step(0)` (disconnecting that sandboxed Vide's stepper), runs the story's disposer in a protected call, and then disposes the control sources.

So: return the component (Vide parents it to the target), or parent to `props.target` and return `nil`. Use `Vide.cleanup` for story-owned resources, and cancel story-owned threads in a cleanup. UI Labs disposes the story scope, which runs your cleanups. The returned Instance itself is not destroyed by the Vide disposer, so `cleanup` anything you must destroy.

## Generic stories

```luau
return {
	controls = { Visible = true },
	render = function(props)
		local frame = Instance.new("Frame")
		frame.Visible = props.controls.Visible
		frame.Parent = props.target
		local unsubscribe = props.subscribe(function(values, infos)
			frame.Visible = values.Visible -- infos.Visible.__new / .__old
		end)
		return function()
			unsubscribe()
			frame:Destroy()
		end
	end,
}
```

## Controls

- Primitive literals (string, number, boolean, `Color3`) become controls automatically.
- Advanced controls come from the UI Labs **utility package** (a separate dependency, with its own version): `Slider(def, min, max, step?)`, `RGBA(color, transparency?)`, `Choose(options, index?)`, `EnumList(record, key)`, plus `String`/`Number` constructors with filters and ranges. Only add the utility package if the project already uses it.

## Environment helpers

Each story runs in a virtual environment that replaces `require`, `script` and `_G`. Through the utility package's `Environment`: `IsStory()`, `Unmount()`, `Reload()`, `CreateSnapshot(name?)`, `SetStoryHolder(instance?)`, `GetJanitor()` (destroyed on unmount), `InputListener` (because `UserInputService` doesn't fire in plugin widgets), `UserInput`, `EnvironmentUID` and `PreviewUID`.

## Plugin lifecycle

- The plugin creates its toolbar and dock widget in edit mode. A plugin whose name contains `.rbxm`, meaning any local file install including the official release file, gets the toolbar `UI Labs (DEV)` and widget `UILabs(DEV)`. A Creator Store install gets `UI Labs` / `UILabs` (`IsLocalPlugin` in `src/Utils/MiscUtils.ts`).
- Hiding the widget doesn't unmount the plugin's interface. The toolbar's stop action unmounts it and resets state.
- Re-mounting the same story through the plugin is the supported way to reset it. Don't keep a second, independent preview mount.

## Limits of this guidance

Utility-package helpers, StyleSheet previews, custom control ranges, pixel layout, real input and hot reload were not reviewed here. Verify them in Studio before claiming they work.
