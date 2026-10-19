# Roblox checklist

What Roblox adds to UI design: screen space that Roblox and the device take, three kinds of input, and player settings a screen must follow. The API names are from Roblox's [engine reference](https://create.roblox.com/docs/reference/engine); defaults marked as checked were read in Studio on 2026-10-19.

## Screen space

- **Insets.** A ScreenGui's `ScreenInsets` sets the area its content is laid out in:
  - `CoreUISafeInsets`, the default, keeps clear of the notches and Roblox's top bar. Use it for anything a player reads or presses.
  - `DeviceSafeInsets` keeps clear of the notches but reaches up behind the top bar's buttons.
  - `None` is the whole screen, notches included: only for full-bleed backgrounds and scrims, nothing a player reads or aims for.
  - `TopbarSafeInsets` is the part of the top bar beside Roblox's buttons. Its size is `GuiService.TopbarInset`, which changes as Roblox's buttons do, so listen with `GetPropertyChangedSignal` instead of hard-coding it. rhr lays it out as the core area, and its `TopbarInset` is the whole top bar ([known gaps](rendering.md#known-gaps)), so check it in a play-test.
- Leave `ClipToDeviceSafeArea` on, its default, so nothing slides under a notch.
- Set `SafeAreaCompatibility` to None on new ScreenGuis, and put a full-bleed background in its own ScreenGui with `ScreenInsets` None, under the content's gui. The default, FullscreenExtension, stretches a frame that covers the safe area out to the screen edges; Roblox keeps it for UI made before notches and recommends insets for new work.
- Hiding Roblox's own UI with `StarterGui:SetCoreGuiEnabled` or `StarterGui:SetCore("TopbarEnabled", false)` takes away what players expect, such as chat and the player list. Ask the user first.
- The smallest screens are landscape phones. Below the top bar and inside the safe area they have 734 by 314 points on rhr's `phone` preset and 686 by 281 on `android`. Lay a screen out there first.
- Roblox's buttons take the left end of the top bar, about 208 points on Studio's iPhone 16.

## Touch controls

On phones and tablets Roblox puts a jump button and a thumbstick in the bottom corners.

- Jump is a square in the core area's bottom right. On a phone it is 70 points, 25 in from the right and 20 up from the bottom: its corner sits at `UDim2.new(1, -95, 1, -90)`. Once the core area's short side is over 500 points, as on a tablet, it is 120 points, 50 in and 90 up, at `UDim2.new(1, -170, 1, -210)`.
- A character driven by an `AbilityManagerActor`, with `Humanoid.EvaluateStateMachine` off, gets another layout: jump is 72 points at `(1, -136, 1, -136)`, or 120 at `(1, -220, 1, -232)`. rhr checks the first layout only.
- The thumbstick starts wherever a thumb lands in its zone. On a landscape screen the zone is the left 40% of the core area and its lower two-thirds, reaching out to the screen's left and bottom edges; in portrait it is the full width and the lower 40%. A button there fights the stick.
- `rhr check` reports overlaps as `under-touch-controls`. The controls are in a ScreenGui at DisplayOrder 0, so a modal's scrim (InputSink All) in a gui above it takes every touch, and the controls do nothing while it is open: check a modal's story with `--ignore under-touch-controls`. The jump button still shows through a see-through scrim. Hiding the controls while a modal is open (`GuiService.TouchControlsEnabled`) changes the look, so ask the user.
- Put the game's own touch buttons in an arc around jump, at full target size, where the right thumb already rests.
- `GuiService.TouchControlsEnabled = false` hides both controls and frees the corners, but then the game needs its own movement and jump. Ask the user first.

## Input

- **Activated.** Connect `Activated`, not `MouseButton1Click`: it fires for a click, a tap and the gamepad's A on a selected button.
- **The input in use.** Branch on `UserInputService.PreferredInput` (such as KeyboardAndMouse, Touch or Gamepad), which follows what the player is using, rather than `TouchEnabled` or `KeyboardEnabled`, which say what the device has. It changes mid-session when a player picks up a gamepad, so listen with `GetPropertyChangedSignal`.
- **Input and settings in stories.** rhr renders each preset with its device's input, such as touch on `phone` and a gamepad on `console`, and with Roblox's default [settings](#accessibility-settings) ([devices](rendering.md#devices)). Read input and settings in one place, the app root, listen there, and pass them down as props or context, so a story can render any other variant, such as a gamepad on desktop or reduced motion.
- **Per input.** Touch has no hover, so every control needs a pressed state. Show button hints, such as a B glyph beside Back, only on gamepad.

Gamepad navigation moves a selection between controls with the stick and D-pad:

- When a screen opens on gamepad, select a control: `GuiService:Select(screen)` selects the screen's visible, selectable descendant with the smallest `SelectionOrder`, or set `GuiService.SelectedObject` directly. Set `SelectedObject` to nil when the screen closes. Selecting on other inputs draws the outline for no one.
- Only pressables are `Selectable`. Buttons and TextBoxes are by default, frames and labels aren't (checked).
- Draw the selection outline from the theme's `selection`: set `PlayerGui.SelectionImageObject` once for the game, or a control's own `SelectionImageObject`. Size it with Scale, such as `UDim2.fromScale(1, 1)`, so it fits whichever control is selected.
- Set `NextSelectionUp`, `NextSelectionDown`, `NextSelectionLeft` and `NextSelectionRight` where the automatic order goes wrong, such as between a grid and a sidebar.
- A modal's panel is a `SelectionGroup` with its four `SelectionBehavior` directions set to Stop, so selection can't leave it while it's open. The default, Escape, lets it.
- B goes back, as A accepts ([Roblox's convention](https://create.roblox.com/docs/input/gamepad#common-control-schemas)). Bind ButtonB while a screen is open and unbind it when it closes: with the Input Action System, an `InputContext` holding the B action, `Enabled` while the screen is open, with a `Priority` above the game's contexts and `Sink` on; or with ContextActionService or the project's input layer.
- [TV remotes](https://create.roblox.com/docs/input/micro-gamepad) read as a gamepad (Gamepad1) with no thumbsticks: in menus the arrows are the D-pad, the centre is ButtonA and back is ButtonB. Make every control reachable with four directions, close screens with back the same way everywhere, return selection to where it was when a screen closes, and keep controls big enough to read from the sofa.
- Test navigation with a gamepad or Studio's [Controller Emulator](https://create.roblox.com/docs/studio/controller-emulator), and remotes with the Device Emulator on Android TV and the Controller Emulator's TV Remote. Renders can't show either.

## Scaling

- One UIScale per ScreenGui grows the UI on bigger screens ([scaling](theme.md#scaling)). Inside it, sizes and gaps are Offset in tokens; Scale is for layout regions, and a UISizeConstraint caps a panel's width.
- A tablet gets scale 1 and far more room than a phone: rhr's `tablet` is 1180 by 820. Regions decide how a screen looks there, so render it.
- Pick layout variants, such as a sidebar that becomes tabs, from the ScreenGui's `AbsoluteSize` divided by the root scale: the room the layout really has, in points. `workspace.CurrentCamera.ViewportSize` is the whole screen in rhr but leaves out the side notches in Studio, so a breakpoint on it can branch differently in the two.
- `rhr check <story> --devices all` checks every preset in one run.

## Text and localization

Translations run longer than English, and short strings the most. The average expansion into European languages, from IBM's figures as the [W3C](https://www.w3.org/International/articles/article-text-size.en) publishes them:

| English length | Expansion |
| --- | --- |
| Up to 10 characters | 200–300% |
| 11 to 20 | 180–200% |
| 21 to 30 | 160–180% |
| 31 to 50 | 140–160% |
| 51 to 70 | 151–170% |
| Over 70 | 130% |

- Size boxes for it: a 6-letter button label needs room for about 15. Let labels and buttons grow with `AutomaticSize`, wrap with `TextWrapped` where a second line is fine, and keep a fixed box only where the longest translation fits.
- Measure text with `TextService:GetTextBoundsAsync`, which takes a `FontFace` and yields, so wrap it in `pcall`. `GetTextSize` takes only an `Enum.Font`. Both include the player's text size setting. rhr only estimates both ([known gaps](rendering.md#known-gaps)), so a box sized from them can look too tight or too loose in a render: check it in a play-test.
- Truncate (`TextTruncate` AtEnd) only where the full text is shown elsewhere, such as a details panel. Usernames and display names run to 20 characters.
- Keep lines under about 80 characters, or 40 in Chinese, Japanese and Korean, and centre only short lines.
- Format every number with one function, so coins read the same on every screen.
- Bake no text into images: it can't be translated and ignores the player's text size.
- In [rich text](https://create.roblox.com/docs/ui/rich-text), take colours from the theme: `'<font color="#' .. Theme.color.accent:ToHex() .. '">'`, since `ToHex` leaves out the `#`. The raw-value guard can't see a colour inside a string, so the review has to.
- Escape what a player typed before putting it in rich text (`&lt;`, `&gt;`, `&quot;`, `&apos;`, `&amp;`), or their text can add tags.
- Text one player writes for others to see, such as a pet's name, must pass Roblox's text filter on the server (`TextService:FilterStringAsync`), and can come back with words replaced by `#`. Show it as returned.

## Images

- Make icons white on transparent and tint them with `ImageColor3` from the theme, so one upload serves every colour and state.
- Upload at about 3 times the largest size an image is drawn, in points: phones draw about 3 pixels per point, and the root scale grows UI on big screens. Roblox shrinks uploads past about 1024 pixels on a side.
- Uploading publishes the image under the user's account and sends it through moderation. Ask the user first.
- Panels and buttons that stretch use 9-slice: `ScaleType` Slice, `SliceCenter` for the stretching middle in image pixels, and `SliceScale` for the upload's density, such as 1/3 for an image made at 3 times.
- A well that frames art takes the art's aspect ratio, with a `UIAspectRatioConstraint`: in a well of another shape, `ScaleType` Fit only letterboxes it.
- Pixel art uses `ResampleMode` Pixelated.
- Roblox UI has no blur, so a soft shadow or glow is an image.
- Use an Image's id, not a Decal's: Roblox draws nothing for the id of a Decal, a Model or a sound, and neither does rhr. A Decal's `Texture` holds its Image's id. Once rhr has asked Roblox for such an id, `missingAssets` lists it as `not an image`; before that, as `offline` or `not downloaded`.
- In stories, give images as `rbxassetid://` ids. rhr draws nothing for `rbxasset://` paths or `rbxthumb://` thumbnails, so the reviewer can't judge them ([known gaps](rendering.md#known-gaps)).

## Layering

- A ScreenGui made with `Instance.new` gets `ZIndexBehavior` Global and `ResetOnSpawn` true (checked). Set Sibling, so children draw over their parents and ZIndex only orders siblings, and set `ResetOnSpawn` false, or Roblox deletes the gui when the character respawns.
- Take `DisplayOrder` from the theme's layer tokens ([layers](theme.md#sizes-and-layers)). A modal's is above 0, the touch controls' DisplayOrder, so it draws over them ([touch controls](#touch-controls)).
- Behind a modal goes a scrim: a full-screen button coloured from `overlay`, with `AutoButtonColor` off, `Selectable` off, and `InputSink` All, so no press, tap or hover reaches the UI or the world behind it. A button's default, Activate, lets hover through. Its `Activated` closes the dialog as a cancel, unless the dialog needs an answer. Under `CoreUISafeInsets` the scrim stops at the safe area and leaves the top bar and the notch sides uncovered: put it in a gui of its own with `ScreenInsets` None, or accept the gap.
- In a game where the camera can lock the mouse, such as first person or shift lock, give every screen that needs the cursor a visible button with `Modal` on: while it shows, the mouse isn't locked.
- Use a CanvasGroup only to fade or tint a group as one. It costs texture memory and draws blank past a cap set by the graphics quality, always clips its children, flattens only under Sibling, and works best at a fixed size.

## Accessibility settings

Players set these in Roblox's Settings menu, in the app or during a game, and can change them while playing, so listen to each with `GetPropertyChangedSignal`. Roblox's [accessibility guide](https://create.roblox.com/docs/production/publishing/accessibility) has samples. rhr stories get Roblox's defaults, so read them at the app root and pass them down, where a story can pass another value ([input](#input)).

- **Text size:** `GuiService.PreferredTextSize`, Medium by default, then Large, Larger and Largest. Roblox grows TextSize itself, except for TextScaled text and past a UITextSizeConstraint's `MaxTextSize`, so never cap text a player reads. Boxes with `AutomaticSize` grow to fit, and `TextWrapped` text wraps inside its box. Let boxes grow, and check Largest in a play-test, set from Text Size in the in-game Settings menu.
- **Reduced motion:** `GuiService.ReducedMotionEnabled`. Snap movement to its end, with a tween time of 0, or fade instead of moving.
- **Background transparency:** `GuiService.PreferredTransparency`, 1 by default and 0 for fully opaque. Multiply each see-through background's transparency by it: `transparency * GuiService.PreferredTransparency`.
- Colour is never the only signal ([colour tells](ai-tells.md#colour)).
