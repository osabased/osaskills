# AI tells

A tell is a default used without a reason: what an editor, a template or a model produces when nobody decides. Players don't name tells, but they feel the result, a game that looks like every other prototype. When the brief or the taste log asks for one of these, it's a choice, not a tell: keep it.

The entries are written for calm UI. Many Roblox games, especially for younger players, are loud on purpose: saturated colour, chunky display type, thick strokes and outlined text. When the user picked a bold direction ([style tiles](process.md#style-tiles)), those traits are its style rather than tells. Judge them by what holds in any style: one construction for depth, one outline weight, and colour spent by rank, so the accent and currencies still stand out.

Each entry says what the tell looks like, why it reads as unchosen, and a better move.

## Panels and surfaces

- **The black glass panel.** Black at about half transparency with white text, behind every panel. It's the quickest way to make text readable over the world, so it looks like nobody designed the screen. Give panels the theme's surface colour, opaque or nearly, and let the world show around them rather than through them.
- **One radius everywhere.** The same corner on buttons, panels, chips and icons. Use the theme's radius steps: small things get small radii, and an inner corner is the outer one minus the padding between them.
- **Boxes in boxes.** A panel holding cards holding rows holding chips, each with its own background and border. Every layer adds edges for the eye to sort. Group with space first, and add a background only where space can't separate things ([space](theme.md#space-shape-and-depth)).
- **Effects on everything.** A gradient, a glow, a stroke and a shadow on every element. Effects mark importance, so on everything they mark nothing and the screen turns noisy. Give depth only to what floats above the rest, with one construction.
- **Studio's defaults.** The grey background, dark one-pixel border and stock font of a freshly inserted Frame or TextLabel. Everyone who has opened Studio knows them, so they read as unfinished. Set every visible property from the theme, and turn borders off where nothing calls for one.

## Colour

- **Pure black and white.** `#000000` text on `#FFFFFF`. Beside a tinted palette they look harsh and flat. Take the darkest and lightest colours from the palette, tinted toward it ([colour roles](theme.md#colour-roles)).
- **Traffic lights.** Stock red, yellow and green for loss, warning and gain, straight from a colour picker. They clash with any palette that isn't made of primaries. Keep the meanings, tune each hue toward the palette, and check it with `contrast.py`.
- **The purple-blue gradient.** Violet fading to blue on buttons and headers, so common in generated and template UI that it reads as no choice at all. Unless the brief asks for it, use the palette's accent, flat or with a small step in lightness.
- **Everything saturated.** Every colour at full strength, so nothing stands out. Saturation is emphasis: keep surfaces quieter than the accent, currencies and rarities, which get the strongest colour.
- **Colour as the only signal.** Locked items only greyer, rarity only a border colour, errors only red. Players with colour-vision deficiencies miss them, and so does anyone on a dim phone in sunlight. Pair colour with a shape, an icon, a label or a position.

## Text and type

- **One font at one weight.** Everything in the stock font at one weight, with hierarchy from size alone. It reads as flat and could be any game. Use a display face for titles and big numbers, a plain one for reading, and two or three weights ([type](theme.md#type)).
- **TextScaled everywhere.** Every label scaled to its box, so sizes drift from row to row and ignore the player's text size setting. Use the type scale, and keep TextScaled for display numbers that must fill a box.
- **Outlines as a crutch.** A thick black stroke on all text, to make it read over anything. Over the world, such as a HUD number or a nameplate, an outline can be a fair choice. On a solid panel it does nothing for contrast and adds noise, unless outlined text is the picked style. Fix legibility with the surface behind the text.
- **Emoji as icons.** 🪙 for coins and ⚙️ for settings. They come in their own style, ignore the theme's colours, and sit on the text's baseline instead of centred. Use icons from one family, as white images tinted from the theme ([images](roblox-checklist.md#images)).
- **Placeholder copy.** "Item Name", "Description goes here", "Button". It hides how real text fits, and it ships more often than anyone means it to. Use real strings at worst-case length.
- **All-caps sentences.** Whole lines in capitals. Runs of capitals are slower to read and they shout. Keep capitals for short labels, if the style tile chose them, and write sentences in sentence case.

## Icons

- **Mixed styles.** Outline icons beside filled ones, different stroke widths, a painting beside a flat glyph. Pick one family and one weight, at the theme's icon sizes.
- **Decorative icons.** An icon on every button and row, there because the slot was empty. An icon earns its place when players recognise it faster than its label, or when it stands in for a label where space is short and the meaning is universal: close, back, settings.
- **The small red X.** A small red close button on the panel's top-right corner. Red says danger where closing loses nothing, the button is usually below the target size, a centred panel puts it near the top centre where thumbs reach worst, and nothing closes it on a gamepad. Keep the corner if you like, at full target size in a quiet colour, and also close on a tap on the scrim and on the gamepad's B ([input](roblox-checklist.md#input)).

## Composition

- **Everything centred.** Every panel in the middle of the screen and every label centre-aligned. Centring is a blank canvas's default, and centred lines have a ragged start that is slower to scan. Centre what stands alone, such as a modal or a short title; align lists, rows and paragraphs to a shared start edge.
- **An equal grid.** Every item the same size in a uniform grid, the featured one included. A grid says everything is equal, which is rarely the screen's job. Give the top of the brief's ranking more room.
- **A tall header bar.** A full-width title bar 60 or more points tall on every panel. A landscape phone has about 320 points of height inside the top bar and safe area, so the header takes a fifth of it. Put the title in a corner, or drop it when the content says what the screen is.
- **The HUD ring.** Counters, buttons and bars along every edge of the screen. The world is what players came for, and a ring of UI frames it like a dashboard. Keep the HUD to what a player needs mid-play, in a few tight clusters clear of the touch controls.
- **Uniform padding.** The same gap inside buttons, between rows and around panels. Equal space can't group anything. Use less space inside a group than between groups ([space](theme.md#space-shape-and-depth)).
- **Tall modals.** A portrait-shaped dialog laid out on a desktop canvas. On a landscape phone it overflows or shrinks its text. Lay dialogs out wide and short, with their actions in one row.

## Content and copy

- **The title as the biggest thing.** "SHOP" in display letters across the top of the shop. Players know which screen they opened; the biggest thing should be what the screen is for. Make the featured item or the main number the largest, and keep the title small or drop it.
- **Tidy sample data.** Three items with short names and round numbers. Real players have none or hundreds, names 20 characters long, and coins in the billions. Render with worst-case content ([build the screen](process.md#build-the-screen)).
- **Hype copy.** "EPIC MEGA DEALS!!!" and "Unlock AMAZING rewards". It reads like an ad, and players learn to skip it. Say what the button does and what it costs: "Buy for 250".
- **No empty states.** A blank panel when the inventory is empty or a list fails to load, so a player can't tell empty from broken. Say what's missing and what to do next: "No fish yet. Cast from the dock to catch one."

## Interaction

- **A bounce on everything.** Every button grows on hover and every panel springs in with an overshoot. Motion is for showing a change; on everything it slows players down and pulls the eye from what changed. Keep overshoot for rare, rewarding moments, and everyday motion short ([motion](process.md#motion)).
- **Feedback only on hover.** A button that changes on hover and nowhere else. Touch has no hover, so phone players get no sign their tap landed. Give every control a pressed state.
- **The default gamepad selection.** Roblox's stock selection image, and screens that open with nothing selected, so a gamepad player has to find the selection before doing anything. Draw the selection from the theme, select a control when a screen opens, and set the order where the automatic one goes wrong ([input](roblox-checklist.md#input)).
- **Unclear pressables.** Labels that look like buttons and buttons that look like labels. Players tap what looks tappable. Give every pressable one consistent look, and make nothing else look like it.
- **Confirmation for everything.** "Are you sure?" before closing a panel or equipping an item. Players learn to tap through it, so it no longer protects the actions that need it. Confirm spending and destroying; make everything else easy to undo.
- **Slow tweens.** Frequent actions animated over more than about 0.4 s. Each one is a wait, repeated hundreds of times a session. Keep presses near 0.1 s and panels near 0.25 s ([motion tokens](theme.md#motion)).
