# Theme

The theme module is the only place visual values live. Components read tokens from it and never write a colour, font, text size, spacing, radius, stroke or duration of their own. That makes a restyle one file, and it lets the [raw-value guard](#the-raw-value-guard) catch drift.

This file gives the roles every theme has, their names, and starting values to tune. A real theme's values come from the style tile the user picked. The example values come from the made-up brief in [project files](project-files.md#brief).

## Colour roles

Name colours by their job, not their hue: `accent`, not `orange`. A restyle then changes one value, not every component that says orange.

| Token | Job |
| --- | --- |
| `surface` | The base of panels and screens |
| `surfaceRaised` | Cards, rows and buttons on a surface |
| `surfaceSunken` | Wells: inputs, slots, progress-bar tracks |
| `border` | Outlines and dividers |
| `text` | Body text and headings |
| `textMuted` | Secondary text: labels, hints, timestamps |
| `textOnAccent` | Text and icons on `accent` |
| `textDisabled` | Text of disabled controls |
| `accent` | The primary action and the selected state |
| `accentPressed` | `accent` while pressed |
| `positive`, `negative`, `warning` | Gains, losses and errors, cautions |
| `currency` | A table with one colour per currency, such as `currency.coins` |
| `overlay` | The scrim behind a modal |
| `selection` | The gamepad selection outline |

- Transparencies are tokens of their own (`transparency.overlay`), because Roblox keeps colour and transparency in separate properties.
- Game groups such as rarities and teams get their own tables (`rarity.epic`). They meet the same [contrast](#contrast) bars on the surfaces they sit on, and never carry meaning by colour alone ([colour tells](ai-tells.md#colour)).
- The darkest and lightest colours come from the palette, tinted toward it, as `text` and `surfaceRaised` are here. Pure black and white look harsh beside tinted colours.

## Type

| Token | TextSize | For |
| --- | --- | --- |
| `display` | 48 | Big numbers, and titles that are part of the art |
| `title` | 28 | Screen and panel titles |
| `body` | 20 | Anything a player reads, including names in list rows |
| `label` | 20 | Text on buttons, tabs and chips, set apart from `body` by weight |
| `caption` | 14 | Details a player can do without |

- Each token is a font and a size: `FontFace = Theme.text.body.font` and `TextSize = Theme.text.body.size`.
- Use at most two families and two or three weights. Hierarchy comes from steps of size and weight, not from more fonts.
- TextSize is the height of a line, not the font's point size. Builder Sans, Roblox's own family, has a line 1.26 em tall, so its TextSize is about 1.26 × the point size: Apple's 17 pt body text is about TextSize 21. Other families differ, so check a family's line height before turning a guideline into a TextSize.
- Numbers that change, such as coins, timers and scores, get a box sized for their largest value and aligned to one side, so the layout doesn't shift as digits change.
- TextScaled is only for display numbers that must fill a box, with a UITextSizeConstraint. TextScaled text ignores the player's text size setting ([accessibility settings](roblox-checklist.md#accessibility-settings)), so nothing a player reads uses it. A MinTextSize is never below 9.

## Space, shape and depth

| Group | Starting values |
| --- | --- |
| `space` | `xs` 4, `sm` 8, `md` 12, `lg` 16, `xl` 24, `xxl` 32 |
| `radius` | `sm` 4, `md` 8, `lg` 16, and `pill` as `UDim.new(0.5, 0)` |
| `stroke` | `thin` 1, `thick` 3 |

- Group with space before boxes: less space inside a group than between groups. Add a border or background only where space can't separate things.
- Radii are UICorner `UDim`s, so `md` is `UDim.new(0, 8)`. A corner inside another stays concentric: the inner radius is the outer radius minus the padding between them, or 0.
- A UIStroke on a TextLabel or TextButton outlines the glyphs unless its ApplyStrokeMode is Border. A stroke around a box draws outside it by default, so 3 px strokes on two buttons 8 apart leave 2 px between them; `BorderStrokePosition` Inner keeps an outlined control's look inside its hit box.
- Strokes and corners grow with the root UIScale, so they keep their proportions on every screen ([scaling](#scaling)).
- Depth has two or three levels at most and one construction for all of them, named as a token: an offset copy in a darker colour, a stroke, or a 9-slice shadow image. Roblox has no blurred shadow, so a soft one is an image upload ([images](roblox-checklist.md#images)). Depth means something floats above the rest: a modal, a tooltip, a held item.

## Motion

| Token | Starting value | For |
| --- | --- | --- |
| `motion.press` | `TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)` | Press and release |
| `motion.panel` | `TweenInfo.new(0.25, Enum.EasingStyle.Quint, Enum.EasingDirection.Out)` | Panels and screens arriving |

- Springs get named settings too, such as the period and damping ratio of Vide's `spring`.
- With reduced motion on, movement snaps to its end or becomes a short fade ([accessibility settings](roblox-checklist.md#accessibility-settings)).
- Renders show tweens at their end and springs at 0.5 s, so timing is judged in a play-test ([motion](process.md#motion)).

## Sizes and layers

- `size.target` 44 is the smallest touch target. A small icon button keeps a 44 hit area around a smaller icon.
- `size.icon`: `sm` 16, `md` 24, `lg` 32.
- `layer` holds the DisplayOrder of each kind of ScreenGui, so stacking is decided once: HUD, then menus, then modals, then toasts.

## Module shape

One `--!strict` module returning a frozen table, with every level frozen too: `table.freeze` is shallow, and a component that writes into the theme changes every screen. Code spells it `color`, as Roblox's API does. The example is the "Field journal" tile from the made-up brief, which keeps its radii small:

```luau
--!strict
local display = Font.fromName("Merriweather", Enum.FontWeight.Heavy)
local bold = Font.fromName("BuilderSans", Enum.FontWeight.Bold)
local regular = Font.fromName("BuilderSans", Enum.FontWeight.Regular)

return table.freeze({
	color = table.freeze({
		surface = Color3.fromHex("F3E9D2"),
		surfaceRaised = Color3.fromHex("FBF5E6"),
		surfaceSunken = Color3.fromHex("E8D9B5"),
		border = Color3.fromHex("2B1D14"),
		text = Color3.fromHex("2B1D14"),
		textMuted = Color3.fromHex("6B5442"),
		textOnAccent = Color3.fromHex("FFF8EC"),
		textDisabled = Color3.fromHex("8A7764"),
		accent = Color3.fromHex("B54A24"),
		accentPressed = Color3.fromHex("9A3E1C"),
		positive = Color3.fromHex("1A6460"),
		negative = Color3.fromHex("B3261E"),
		warning = Color3.fromHex("7A4F00"),
		currency = table.freeze({
			coins = Color3.fromHex("7A4F00"),
		}),
		overlay = Color3.fromHex("2B1D14"),
		selection = Color3.fromHex("1A6460"),
	}),
	transparency = table.freeze({
		overlay = 0.35,
	}),
	text = table.freeze({
		display = table.freeze({ font = display, size = 48 }),
		title = table.freeze({ font = display, size = 28 }),
		body = table.freeze({ font = regular, size = 20 }),
		label = table.freeze({ font = bold, size = 20 }),
		caption = table.freeze({ font = regular, size = 14 }),
	}),
	space = table.freeze({ xs = 4, sm = 8, md = 12, lg = 16, xl = 24, xxl = 32 }),
	radius = table.freeze({
		sm = UDim.new(0, 4),
		md = UDim.new(0, 6),
		lg = UDim.new(0, 8),
		pill = UDim.new(0.5, 0),
	}),
	stroke = table.freeze({ thin = 1, thick = 3 }),
	motion = table.freeze({
		press = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		panel = TweenInfo.new(0.25, Enum.EasingStyle.Quint, Enum.EasingDirection.Out),
	}),
	size = table.freeze({
		target = 44,
		icon = table.freeze({ sm = 16, md = 24, lg = 32 }),
	}),
	layer = table.freeze({ hud = 0, menu = 10, modal = 20, toast = 30 }),
})
```

## Scaling

Tokens are in phone points: the units Roblox lays a phone's UI out in, about 850 by 390 on a landscape phone. One UIScale per ScreenGui grows everything on bigger screens, so a layout that works on a phone keeps its proportions everywhere else.

```luau
local function rootScale(viewport: Vector2, displaySize: Enum.DisplaySize): number
	local factor = if displaySize == Enum.DisplaySize.Large
		then 1.8
		elseif displaySize == Enum.DisplaySize.Medium then 1.25
		else 1
	return math.max(1, math.min(viewport.X, viewport.Y) / 1080 * factor)
end
```

| Screen | Scale |
| --- | --- |
| Phone, tablet, a 768 px laptop | 1 |
| 1080p desktop | 1.25 |
| 1440p desktop | 1.67 |
| 4K desktop | 2.5 |
| 1080p TV | 1.8 |

Each ScreenGui holds one root Frame that undoes the scale's growth, so its content fills the gui:

```text
ScreenGui
└─ Root: Frame, Size = UDim2.fromScale(1 / s, 1 / s), Position (0, 0), AnchorPoint (0, 0), no background
   ├─ UIScale, Scale = s
   └─ the screen's content
```

- The app's root passes in `workspace.CurrentCamera.ViewportSize` and `GuiService.ViewportDisplaySize`, and again whenever either changes. The camera's viewport, rather than each gui's own area, gives every ScreenGui the same scale whatever its insets.
- `ViewportDisplaySize` sorts screens by kind: Small for phones, tablets and handhelds, Medium for laptops and monitors, Large for TVs.
- Each rhr device preset has its kind's display size ([devices](rendering.md#devices)), so a story that passes both in, as the app's root does, gets the scale a game would.
- Inside the root, components use Offset in tokens. Scale is only for layout regions, such as a sidebar that takes a third of the width. A UISizeConstraint caps a panel's width on wide screens.
- The factors put `body` and `label` (20) at 25 on a 1080p desktop and 36 on a 1080p TV. The [Xbox Accessibility Guidelines](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/101) measure text from the top of its ascenders to the bottom of its descenders. In Builder Sans that is 0.72 of the TextSize, so 25 and 36 give 18 and 26 pixels, the guidelines' minimums for PC and console. `caption` (14) lands at 17.5 and 25, below them. In a game ranked for PC or console, use captions for nothing a player needs, or raise the token.

## Contrast

Check the theme's pairs with `contrast.py` whenever a colour changes. If the project has a test runner, a spec over the same pairs keeps a later change from slipping below the bars.

The pairs:

- `text`, `textMuted` and `textDisabled` on each surface;
- `textOnAccent` on `accent` and `accentPressed`;
- `positive`, `negative`, `warning`, each currency and each game group, on the surfaces they are drawn on;
- `border` on its surface, where it is a control's only edge;
- `selection` on every surface.

| What | Ratio | Source |
| --- | --- | --- |
| Body and label text | 4.5:1 | WCAG 1.4.3 |
| Large text: TextSize 30, or 24 bold | 3:1 | WCAG 1.4.3 |
| Icons, control edges and the selection outline | 3:1 | WCAG 1.4.11 |
| Disabled text | 3:1 | [Xbox Accessibility Guideline 102](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/102); WCAG exempts it, but players still read what is locked |

The WCAG ratios are from [1.4.3](https://www.w3.org/TR/WCAG22/#contrast-minimum) and [1.4.11](https://www.w3.org/TR/WCAG22/#non-text-contrast). Its large text is 18 pt, or 14 pt bold; the TextSizes above convert that for Builder Sans, and other families convert as [type](#type) says.

A see-through surface is checked over white and over black, since anything can be behind it. `contrast.py` takes a colour with an `@` transparency, as in `2B1D14@0.35` (Roblox's transparency, so 0 is opaque), composites it over both and reports the worse ratio.

```sh
uv run --no-project python <skill>/scripts/contrast.py 2B1D14 F3E9D2  6B5442 F3E9D2  FFF8EC B54A24
uv run --no-project python <skill>/scripts/contrast.py --min 3 8A7764 F3E9D2  1A6460 E8D9B5
uv run --no-project python <skill>/scripts/contrast.py FFF8EC 2B1D14@0.35
```

The first line checks body text, muted text and text on the accent; the second, disabled text and the selection outline at 3:1; the third, a hint written straight on the modal scrim.

In the example, the brief's rust `#C4552D` gave `textOnAccent` only 4.25:1, so the theme's `accent` is a darker `#B54A24` at 5.01:1. Its sea green `#1F6F6B` gave 4.24:1 on `surfaceSunken`, so `positive` is `#1A6460`. Adjusting a sampled colour to pass is normal; tell the user when the change is visible.

## The raw-value guard

`<skill>/scripts/theme_guard.py` fails on visual values written outside the theme, in `.luau` and `.lua` files:

- colours: `Color3.new`, `Color3.fromRGB`, `Color3.fromHex`, `Color3.fromHSV` and `BrickColor`;
- fonts: `Font.new`, `Font.fromEnum`, `Font.fromName`, `Font.fromId` and `Enum.Font`;
- text sizes: `TextSize`, `MinTextSize` or `MaxTextSize` set to a number.

It skips comments and strings, and any line marked `-- theme-guard: allow <reason>` for a value that really is one-off. The reason is for the user to read, so a marker without one doesn't count. Spacing, radii and durations aren't checked, because too many plain numbers are legitimate. The review catches those. It reads no other language, so a roblox-ts project needs its own check for these values.

Copy the script into the project, beside its other check scripts, because CI can't reach this skill's folder. Run it from the project's check, with whatever Python the check uses, on the UI folders, allowing the theme module:

```sh
python scripts/theme_guard.py src/client/UI --allow src/client/UI/Theme.luau
```

- While style tiles are drafted, also allow the drafts' folder, and remove the allowance with the drafts.
- For a restyle of an existing game, guard only the folders already moved to the theme, and widen it as screens move.

## Styling

Roblox's Styling (StyleSheet, StyleRule, StyleLink and StyleDerive) can hold tokens as style attributes, but rhr doesn't apply it, so styled UI renders wrong. Keep tokens in the Luau module until rhr does.
