# Rendering

[rhr](https://github.com/TabooHarmony/roblox-headless-renderer), the Roblox headless renderer, draws Roblox UI to PNG without Studio, from a story, a Rojo project or a place file. It also checks the UI for what players run into, such as overflowing text, low contrast, small targets and unsafe areas, and reports layouts as JSON. This skill uses [osabased's fork](https://github.com/osabased/roblox-headless-renderer), which fixes gaps found comparing rhr with Studio. rhr runs the code it renders, so render only code you trust.

## Install

1. `rhr --version` should print `1.0.0rc1+osabased.10` or a later `osabased` build.
2. Otherwise, ask the user, then install the fork at the commit this skill was checked against:

   ```sh
   uv tool install --force "git+https://github.com/osabased/roblox-headless-renderer@97b98ccce5d97c008d84d051fb98adbebd6d75c8"
   ```

   On Windows, first stop rhr's background worker if one is running. It is two `python -m rhr.server` processes: one whose command line names the tool's own `roblox-headless-renderer\Scripts\python.exe`, in the folder `uv tool dir` prints, and the Python it starts, whose parent is that one. Stop both, and no other `rhr.server` process, since those belong to other rhr installs, such as a venv. PowerShell lists them: `Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object CommandLine -match 'rhr\.server' | Select-Object ProcessId, ParentProcessId, CommandLine`. While the worker runs, the install fails partway with "Access is denied" and leaves rhr broken until an install succeeds.
3. `rhr doctor` lists what rhr uses and what is missing, and `rhr setup` installs the missing tools. rhr runs `rojo` in the story's folder, where a Rokit shim fails unless a `rokit.toml` there or above it lists Rojo.
4. rhr downloads fonts and images through the Studio login on the machine. Without Studio, as in a cloud session or CI, downloads need `RHR_ROBLOX_API_KEY`: an Open Cloud API key, a user key with the `legacy-asset:manage` permission, which the user sets as a secret. Never ask for its value, paste it, or commit it.

`rhr skill` prints rhr's own guide, and `rhr <command> --help` each command's options.

## Devices

`--device` picks one preset; `rhr check --devices all`, or a list such as `phone,tablet`, checks several at once. The presets were measured in Studio's device emulator, and each has a 58-point top bar.

| Device | Modelled on | Screen | Notches and home bar (left, top, right, bottom) | Touch controls | Input | Display size |
| --- | --- | --- | --- | --- | --- | --- |
| `desktop` | A 1080p monitor | 1920 by 1080 | None | No | Keyboard and mouse | Medium |
| `laptop` | An average laptop | 1366 by 768 | None | No | Keyboard and mouse | Medium |
| `phone` | iPhone 16 | 852 by 393 | 59, 0, 59, 21 | Yes | Touch | Small |
| `android` | Galaxy A16 | 780 by 360 | 47, 0, 47, 21 | Yes | Touch | Small |
| `tablet` | iPad, 10th generation | 1180 by 820 | None | Yes | Touch | Small |
| `console` | Xbox | 1920 by 1080 | None | No | Gamepad | Large |

A story reads its preset's input in `UserInputService.PreferredInput`, the `…Enabled` flags and `GetLastInputType`, its display size in `GuiService.ViewportDisplaySize`, and its gamepads in `GetConnectedGamepads`: Gamepad1 on `console`, none elsewhere. `GuiService:IsTenFootInterface()` is true only on `console`. Player settings are Roblox's defaults: Medium text, motion on, and a `PreferredTransparency` of 1. To render another variant, such as a gamepad on desktop or reduced motion, a story passes it in ([input](roblox-checklist.md#input)).

## The loop

`<target>` is a story, such as `src/Shop.story.luau`, the Rojo project, or a place file. In a project or place, `--only StarterGui/Shop` draws one screen alone.

1. Before editing, save the findings: `rhr check <target> --out before.json`.
2. Edit.
3. `rhr check <target> --baseline before.json` reports only what the edit added. Fix errors, and fix or mark each warning. `--min-severity info` adds findings that are often intended.
4. `rhr layout <target> --path <element>` prints rects as JSON, to compare with what you meant. `--rich` adds colours, text, paint order and clipping.
5. Render and open the PNG: `rhr ui <target> --device phone --out phone.png`. `--fit --max-size 800` makes a quick look small; renders for review show the whole screen at `--max-size 1500`.
6. Before calling it done, run `rhr check <target> --devices all`. It exits 1 only on an error finding, and 2 when it failed or had nothing to draw; stderr says why. Warnings leave the exit code at 0, so read its findings, not just its exit code.

Also useful:

- Pass element paths back exactly as rhr printed them, such as `Card[2]`.
- `rhr ui --transparent` renders on an alpha background, for UI that floats over the game. Lay it over the contact sheet's backdrops.
- `rhr ui --annotate --json` numbers the buttons on the picture and maps each number to its path.
- `rhr hitmap <target> --at X,Y` says which element a click at that pixel reaches.
- `rhr compare before.png after.png` reports what changed between two renders as JSON, to confirm a fix changed only what it meant to.
- `rhr batch check <target> + ui <target>` runs several commands in one call.
- An `RhrIgnore` string attribute on an element silences findings about it: `all`, or check ids separated by commas. Say why in your summary.
- `rhr check --ignore <check id>` leaves a check out of one run, such as `under-touch-controls` for a modal's story ([touch controls](roblox-checklist.md#touch-controls)).
- `rhr ui --json` reports `missingAssets` and `notes`: what wasn't drawn exactly. Each image the picture leaves empty is in `missingAssets` with its `reason`, the `rect` it would cover in screen pixels (times `scale` on the PNG), and a `hint` where rhr knows how to get it drawn. `rhr layout --rich` marks text whose font was swapped with `fontSubstituted`. Read both before judging, and pass them to the reviewer with any weight drawn as a faux bold ([known gaps](#known-gaps)); a stand-in font says nothing about the real type.
- Ask the user before rhr's first download in a project, since it uses their Roblox account. Until then, render with `--offline` (or `RHR_OFFLINE=1`) and list what's missing in the render notes.

## Known gaps

Where rhr `1.0.0rc1+osabased.10` differs from Studio. Discount these when you look, and list the ones a screen touches in the reviewer's render notes.

Drawn differently, laid out right:

- A UIGradient on a UIStroke reaches its end colours a few pixels early at each end: rhr ramps across the object, where Studio's ramp runs past it (152 px across a 140 px frame with a 4 px Outer stroke).
- Images that are files built into the Roblox client (`rbxasset://`) or thumbnails (`rbxthumb://`) draw nothing. `missingAssets` lists each, and `rhr check --min-severity info` reports it as `image-missing`.
- Tiled and 9-sliced images have hard edges between their pieces, and UICorner on an ImageLabel is aliased.
- One frame: tweens are drawn at their goals, and springs as they are 0.5 s in.
- A bold or heavier weight that wasn't downloaded is drawn as a faux bold of a lighter weight the cache has, which usually runs narrower than the real one, and nothing reports it.
- Under Sibling, a faded or tinted CanvasGroup (GroupTransparency above 0, or a GroupColor3) fades its own UIStroke too and cuts an Outer one off at its edge, where Studio draws that stroke whole and opaque.

Laid out differently:

- Roblox's top-bar buttons aren't drawn. On Studio's iPhone 16 they take about 208 points of the top bar's left end.
- A TopbarSafeInsets gui is laid out as the core area.
- `GuiService.TopbarInset` is the whole top bar between the notches, where a game's starts after Roblox's buttons, so UI placed by it sits further left than in a game.
- `workspace.CurrentCamera.ViewportSize` is the whole screen. Studio's phone emulation leaves out the side notches: 750 by 401 on its iPhone 16.
- The `phone` preset is 852 by 393 with 59-point notches, where Studio's iPhone 16 measured 874 by 401 with 62. rhr's is a little tighter, so a layout that fits it fits Studio's.

In the checks:

- A finding can call a TextButton an ImageButton; go by its path.
- Neither the checks nor `rhr hitmap` model `InputSink`. Buttons a story creates start at Activate, Roblox's default; ones from model or place files read None.
- `under-touch-controls` goes by the preset, so a story that turns the controls off (`GuiService.TouchControlsEnabled = false`) still gets it: check that story with `--ignore under-touch-controls`.

At run time:

- While a story runs, rhr hasn't laid the UI out yet, so values Roblox works out in layout read as they do before layout, and don't change. The story's target and ScreenGui have the area's size and `AbsolutePosition` 0, 0. Any other element's `AbsoluteSize` and `AbsolutePosition` read 0, 0, as do `TextBounds`, `AbsoluteContentSize` and a grid's `AbsoluteCellSize`. UI that sizes itself from these renders as if they were zero: size it with AutomaticSize or a layout, which rhr lays out as Roblox does, or check it in a play-test. `TextFits` and an image's `IsLoaded` read true, so a loop that shrinks text until it fits, or waits for an image, goes on.
- Some reads still error in a story: `ContentText`; a ViewportFrame's `CurrentCamera` (setting one works); and `Image`, `Font`, a UICorner's `CornerRadius` and a few other properties until the story sets them. A deprecated name such as `TextWrap`, `TextColor` or `BackgroundColor` does nothing when set, so `TextWrap = true` leaves the text unwrapped: use the current names (`TextWrapped`, `TextColor3`, `BackgroundColor3`).
- `TextService:GetTextSize` and `GetTextBoundsAsync` are rough estimates, every character half the text size wide, and GetTextSize ignores line breaks and the frame size it's given.
- Roblox's [styling](theme.md#styling) isn't applied.

What matches Studio: layout, a story's area (the same as a running game's), draw order under either ZIndexBehavior (a story mounts in a Sibling ScreenGui, as UI Labs mounts it), scroll bars, notch fill, text to within 1 or 2 pixels, 9-slice sizing, `rbxassetid://` icons, UIGradients (those on text measured at Rotation 0 only), spring positions at 0.5 s, safe areas, and the touch controls' positions.
