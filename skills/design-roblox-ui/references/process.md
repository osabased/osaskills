# The full path

For new game UI, a major screen, a restyle, or a request to make UI look better. Every step leaves a file behind, so a later agent can pick up where this one stopped: read the [project files](project-files.md) first and start at the first step that hasn't been done.

1. [Set up](#set-up)
2. [Brief](#brief)
3. [References](#references)
4. [Calibrate the reviewer](#calibrate-the-reviewer)
5. [Style tiles](#style-tiles)
6. [Theme and base components](#theme-and-base-components)
7. [Layouts for a major screen](#layouts-for-a-major-screen)
8. [Build the screen](#build-the-screen)
9. [Check and look](#check-and-look)
10. [Review rounds](#review-rounds)
11. [The user's review](#the-users-review)
12. [Motion](#motion)

Steps 2 to 6 happen once per game, and 7 to 12 once per screen. Also here: [minor screens](#minor-screens) and [when the user isn't there](#when-the-user-isnt-there).

## Set up

- Check that rhr is installed and recent enough ([rendering](rendering.md#install)). `rhr doctor` says what is missing.
- Find how the project previews UI: its story format (UI Labs, Hoarcekat or Flipbook) and where stories live. rhr renders any of them, or the place itself. With no stories, propose the format of the project's preview library. Stories run project code, so render only code you trust.
- Read the project guide and the UI library's skill. This skill decides how the UI looks; the library skill decides how it's written.
- Read the brief, taste log and theme if they exist.

## Brief

Ask the user in one batch, then write `docs/design/brief.md` ([format](project-files.md#brief)):

- the game in a sentence, and who plays it: age, session length, how much they read;
- platforms, ranked: phone, desktop, tablet, console, VR;
- three words for how the UI should feel, and two for how it must not;
- 3 to 8 reference images ([references](#references));
- fixed constraints: a logo, existing art and its sizes, a font, brand colours;
- the screens the game needs, and which matter most.

Offer a default for anything they don't know; for a Roblox game, that is phone first. Write down anything you inferred under Assumptions, so the user can correct it later.

## References

References are how the user's eye gets into the work. Ask the user to put 3 to 8 images in `docs/design/refs/`, other games, screenshots, illustration, anything, each with a note on what they like in it ("the chunky numbers", "how the HUD stays out of the way"). Don't download images yourself; if the user names a game, ask for screenshots.

Open each image and write down in the brief what they share: their colours as hex, corner shapes, type (weight, case, width), density, how the UI sits over the game world, and how much is decoration. Measure the colours with `palette.py` ([tools](../SKILL.md#tools)), whose last section is what the images share: a colour read by eye from a picture is a guess, and the theme's palette is built from these values. An accent can cover too little of an image to make the list; when the images have one, run it again with a lower `--min-share`. Take traits, not designs: a game's layout answered that game's needs, and copying its look copies its identity.

Reference images are usually other studios' work. In a public repository, add `docs/design/refs/` to `.gitignore` and say so in the brief.

If the user has no references, don't wait for some. Say so in the brief, and make the [style tiles](#style-tiles) from the feel words, the players and the constraints alone. The picked tile then stands in for the references: it is what the reviewer is [calibrated](#calibrate-the-reviewer) on.

## Calibrate the reviewer

Once per project, before the first review, check how the reviewer's eye differs from the user's. Send the reviewer ([review](review.md)) the user's favourite reference with the brief, as if it were a screen to review. It should mostly approve. Write down what it flags that the user likes anyway under "Reviewer calibration" in the taste log. Every later review gets that list, so the reviewer stops fighting the house style. With no references, calibrate right after the style-tile pick, on the picked tile's render.

## Style tiles

A style tile is one specimen board showing a direction's palette, type and components, with no real screen's layout. It makes directions cheap to compare, and the user picks a look before any screen depends on it.

Make three directions. Give each a name and a one-line bet ("Field journal: warm paper, ink outlines, hand-set numbers"). Space them from calm to bold on shape, colour, type, surface and density, so the user chooses between real alternatives, with one close to the references wherever they sit. Make the bold one as loud as the brief's "not" words allow, the way many Roblox games are: saturated colour, chunky display type, thick strokes and outlined text. Younger players often expect that end, so give it the same care as the others rather than making it a foil.

Every tile shows the same specimen content, so the comparison is fair:

- the palette as swatches with role names and hex values ([colour roles](theme.md#colour-roles));
- every step of the type scale, with real strings;
- primary, secondary and quiet buttons, each default, pressed and disabled, and a selected toggle;
- a panel with a header and four rows, one selected and one locked;
- a progress bar empty, partly full and full;
- a currency chip with a big number;
- tabs and a few icons.

Write one specimen story that builds this from a theme table, and three draft theme tables for it. A direction that needs a different construction, such as a 9-slice frame instead of rounded corners, gets a token for it rather than a forked story. After the pick, the chosen table becomes the theme module, the specimen story keeps rendering the real theme as the game's style guide, and the other drafts are deleted; their sheet keeps what they looked like.

Render each tile on phone and desktop and run `contrast.py` on its text and background pairs. Anything that floats over the game, like the HUD, is also rendered with `--transparent` and laid over white, black and busy backdrops, or over a screenshot of the game if the user has one. Put it all on one contact sheet, one row per direction:

```sh
uv run --no-project --with pillow python <skill>/scripts/contact_sheet.py \
  a-phone.png="A phone" a-desktop.png="A desktop" b-phone.png="B phone" ... \
  --columns 2 --title "Style tiles" --out tiles.png
```

Show the user the sheet and ask them to pick one or mix them ("A's colours with C's type"). A mix is a new tile: render it and show it before building on it. Log the pick and its reasons in the taste log, and save the sheet in `docs/design/picks/`.

## Theme and base components

Turn the picked tile into the theme module ([theme](theme.md)), then build the base components every screen shares: Panel, Button, Text, Icon and Bar, each reading only from the theme. Give each one a story that shows all of its states in a grid. That story is how a later agent sees the system at a glance, and its render is how the user reviews it.

Add the raw-value guard to the project's check, so the theme stays the only source of visual values ([guard](theme.md#the-raw-value-guard)).

## Layouts for a major screen

Major screens are the ones players spend time in or judge the game by: the HUD, main menu, shop, inventory and results. The rest are [minor](#minor-screens).

Before laying one out, write two things under the screen in the brief: its job in one sentence ("Sell the featured item; let players browse the rest"), and its content ranked by importance. Layout is that ranking made visible; a screen without one shows everything at the same size.

Make 2 or 3 layouts that differ in composition: what is biggest, where the eye lands first, how content is grouped. They aren't one layout restyled. Build them from the theme and base components with real content, render each on phone and desktop, put them on one sheet and ask the user to pick. Log the pick.

## Build the screen

- Build the picked layout from the theme and base components.
- Write one story per state that changes the layout: empty, full, loading, error, locked, a long list. Each calls one shared builder with fixed props. rhr renders a story with its controls at their defaults, so a control can't show a second state but a second story can.
- Use worst-case content: the longest name the game shows (a 20-character username in wide letters, `WWWWWWWWWWWWWWWWWWWW`), the biggest number it can hold (1,234,567,890, or however the game abbreviates it), many items, and none. An empty state says what to do next.
- Leave room for longer translations ([text and localization](roblox-checklist.md#text-and-localization)).
- Make every action work by touch, mouse and gamepad ([input](roblox-checklist.md#input)).

## Check and look

1. Run `rhr check <story> --devices all`. Warnings don't change its exit code, so read its findings. Fix every error. Fix each warning, or silence it with an `RhrIgnore` attribute and say why in your summary. Check a modal's story with `--ignore under-touch-controls`, since in the game its scrim takes every touch ([touch controls](roblox-checklist.md#touch-controls)).
2. Run `contrast.py` on any colour pair the [theme's pairs](theme.md#contrast) don't cover, such as text over an image or a one-off badge.
3. Render every state story on phone and desktop, and on tablet or console when the brief ranks them.
4. Open every PNG and go through the [rubric](rubric.md) yourself. Fix what you find before you spend a review on it.

## Review rounds

Send the renders to the reviewer as [review](review.md) describes. Apply its fixes, check again, re-render, and send round 2 to the same agent. Stop when it says Ship, when only minor fixes remain, or after three rounds. Past that, the screen drifts from the user's direction toward the reviewer's. Each round is an Opus call: in testing, round 1 took about 80k tokens and 40 to 95 s, and round 2, continued, about 100k and 35 s.

## The user's review

Show the user the final contact sheet, the reviewer's last verdict, and which of its fixes you applied or declined and why. Log what they say in the taste log. When they say the same thing twice, about any screen, make it a [standing preference](project-files.md#taste-log).

## Motion

Stills can't show timing, so motion is set in the theme and judged by watching it.

- Durations and easing are theme tokens, and every screen uses the same few. Starting points for the user to tune: about 0.1 to 0.15 s for a press, 0.2 to 0.3 s for a panel opening.
- Animate what helps a player follow a change: a panel arriving, a number counting up, a reward landing. A bounce on everything is a [tell](ai-tells.md#interaction).
- With reduced motion on, snap to the end or fade instead of moving ([accessibility settings](roblox-checklist.md#accessibility-settings)).
- Watch it in a Studio play-test, and ask the user to watch the moments that matter.

## Minor screens

A minor screen skips layouts: build it from the theme and base components, check and look, usually one review round, then the user's review. If it needs a component the system lacks, add the component to the system first, with its state-grid story.

## When the user isn't there

The user owns the direction, but an agent working alone can't stop at every choice. Make the pick you would recommend, mark it `provisional` in the taste log with the reasons, and tell the user at the end what you picked and what changing it would cost. Later agents and the reviewer treat a provisional pick as open: raise it again rather than build on it further. Keep what depends on it cheap to redo, in tokens rather than in hand-tuned screens.
