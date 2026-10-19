---
name: design-roblox-ui
description: "Design Roblox game UI that looks deliberate rather than generic, and check it the way players will see it. Use whenever you build, restyle or polish a Roblox screen, HUD, menu, shop, inventory, dialog, nameplate or UI component (Vide, React-lua, Fusion, Roact or plain Instances), or the user asks for UI that looks better, cleaner, more polished or less AI-made, even if they don't mention design. Covers a design brief and references, style tiles the user picks from, a theme of tokens, layout options, renders on phone and desktop with rhr, and an independent visual reviewer. For a small change inside an existing theme it is a short checklist. Not for UI logic or state with no visual change."
---

# Design Roblox UI

Generic UI is made of defaults nobody chose: the stock font, a half-transparent black panel, one corner radius on everything, a red close X in the corner. Taste here means two things. Every visible choice traces back to a decision the user made or approved, and every screen is judged from renders at phone and desktop size, the way players see it, never from its code.

## Pick the path

| Task | Path |
| --- | --- |
| New game UI, a major screen (HUD, main menu, shop, inventory, results), a restyle, or "make it look better" | The full [process](references/process.md) |
| A minor screen (settings, a confirm dialog, a tooltip) in a game that has a theme | [Minor screens](references/process.md#minor-screens) |
| A small change inside an existing theme: a row, a button, a label, a new state | The [light path](#light-path) below |
| UI logic or state with no visual change | Not this skill |

With no theme yet, a small change still takes the light path, using the values the screen already has; offer the full path once, in your summary.

## Light path

1. Read the project's taste log and theme module ([project files](#project-files)).
2. Build only from the theme's tokens and base components. A value the theme lacks is a design decision: add it to the theme as a token and name it in your summary, so the user can veto it.
3. Fill the change with worst-case content: the longest name, the biggest number, the empty state.
4. Run `rhr check <story> --devices all`, render phone and desktop ([rendering](references/rendering.md)), open the PNGs, and go through the [quick check](references/rubric.md#quick-check).
5. In your summary, name the renders you looked at and what you checked in them.

## What holds on every path

- **Players see pictures.** Code that reads well can render badly. Judge from renders you opened, at the sizes players use.
- **The user owns the look.** They choose the direction and each major screen's layout, and give the final verdict; you propose, render and check. When they aren't there to choose, make a provisional pick and mark it ([user away](references/process.md#when-the-user-isnt-there)).
- **Every visual value comes from the theme:** colours, fonts, text sizes, spacing, radii, strokes and durations. One source keeps screens consistent and lets the user restyle the game without hunting through components ([theme](references/theme.md)).
- **Smallest screen first.** A phone in landscape, with the thumbstick and jump button in the bottom corners and Roblox's buttons along the top, is where layouts break. One that works there grows to desktop; the reverse rarely holds ([Roblox checklist](references/roblox-checklist.md)).
- **Worst-case content in every state:** long names, huge numbers, many items and none, locked, disabled, loading. A screen shown only with tidy sample content hasn't been tested.
- **The player's settings win:** text size, reduced motion and transparency ([accessibility settings](references/roblox-checklist.md#accessibility-settings)).
- **Motion is watched, not rendered.** rhr shows a tween at its end and a spring at 0.5 s, so a still frame says nothing about timing or feel ([motion](references/process.md#motion)).
- **Know the generic tells** and why each reads as unchosen ([AI tells](references/ai-tells.md)).

## Project files

| File | Holds |
| --- | --- |
| `docs/design/brief.md` | The game, players, platforms, mood, references and screen list |
| `docs/design/refs/` | Reference images the user supplied |
| `docs/design/taste.md` | Standing preferences, reviewer calibration, and every pick with its reasons |
| `docs/design/picks/` | The contact sheet behind each pick |
| The theme module | Every visual token, usually `Theme.luau` beside the UI code |

The project guide can move any of these; their formats are in [project files](references/project-files.md). Read the taste log before any visual change: it keeps the next agent from undoing the last one's decisions.

## Tools

`<skill>` is this skill's folder.

- **rhr** renders stories and places to PNG and checks them for overflowing text, low contrast, small targets and unsafe areas. [Rendering](references/rendering.md) has the version to install and the gaps to discount.
- **Contact sheet:** `uv run --no-project --with pillow python <skill>/scripts/contact_sheet.py --help`. Lays renders out in one labelled image, optionally over white, black and busy backdrops, so options compare side by side.
- **Contrast:** `python <skill>/scripts/contrast.py --help`. WCAG contrast ratios for colour pairs, including see-through panels.
- **Raw-value guard:** `python <skill>/scripts/theme_guard.py --help`. Fails on colours, fonts and text sizes written outside the theme module; copy it into the project and run it from the project's check ([guard](references/theme.md#the-raw-value-guard)).
- **Reviewer:** the `osaskills:roblox-ui-reviewer` agent, or `roblox-ui-reviewer` outside the plugin, critiques the renders cold, without the code ([review](references/review.md)).

## References

- [Process](references/process.md): the full path step by step, minor screens, and working without the user.
- [Project files](references/project-files.md): the brief, taste log and picks.
- [Theme](references/theme.md): token roles, the type scale, scaling, contrast bars and the raw-value guard.
- [Rubric](references/rubric.md): what a finished screen gets right, and the quick check.
- [AI tells](references/ai-tells.md): defaults that make UI look generated, and better moves.
- [Roblox checklist](references/roblox-checklist.md): screen space, touch controls, input, scaling, text, images, layering and accessibility settings.
- [Review](references/review.md): briefing the reviewer and weighing its fixes.
- [Rendering](references/rendering.md): rhr setup, commands and known gaps.
