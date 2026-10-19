# Behavioral evaluation scenarios

Use after changing the paths, the process, the project files, the review briefing, the reviewer's instructions or the rendering advice. Run affected cases with independent agents in isolated fixtures, with rhr installed and offline. Give each agent the request, the skill and the raw project; withhold expected outcomes, suspected defects and prior conclusions. Where the user must answer, the evaluator plays the user with the scripted answers. Inspect actual responses, reads, commands and writes, and open the renders the agent made. The document and script tests don't prove agent behaviour.

## Light path in a themed project

Fixture: a Rojo game with Vide UI and UI Labs stories, a theme module, base components with state-grid stories, a taste log with two standing preferences, and a check command that runs the raw-value guard. The inventory screen has a footer with one button.

Request A: "Add a Sell all button to the inventory footer."

Assess: reads the taste log and theme before building, and builds from the theme's tokens and the Button component. A value the theme lacks becomes a token named in the summary. Fills the footer with worst-case content, runs `rhr check` with `--devices all`, renders phone and desktop and opens both, and names in its summary the renders it looked at and what it checked. Asks no brief questions and makes no tiles, layouts or review rounds. Fails if it writes a raw colour, font or text size, or reports the change done without opening a render.

Request B, independent fixture: the same game with no theme module or design files. "Add a gem counter under the coins."

Assess: takes the light path, matching the coin counter's existing values rather than inventing a style, renders and checks as in A, and offers the full path once, in the summary. Doesn't start the brief or tiles unasked.

## New game UI with the user present, three rounds

Fixture: a Rojo game with Vide UI and UI Labs stories, a placeholder HUD, and no theme or design files.

Round 1 request: "Build the HUD for my fishing game."

Assess: asks the brief in one batch: the game and its players, platforms ranked, three words for the feel and two against, reference images, fixed constraints, and the screens. Offers a default for each, phone first among them. Asks for 3 to 8 images in `docs/design/refs/` with a note on each. Writes no UI yet.

Round 2 answers: a full brief, four reference images placed in `docs/design/refs/` with notes and one marked as the favourite, and "I also love the numbers in Tiny Fishing."

Assess: asks for screenshots of the named game rather than downloading or searching for any. Writes `docs/design/brief.md` with traits sampled from the references (hex colours, corner shapes, type, density) and an Assumptions section. Calibrates the reviewer once on the favourite reference and logs what it flagged under Reviewer calibration. Makes three named directions, each with a one-line bet, differing in shape, colour, type, surface and density, not one look in three palettes. Builds one specimen story over three draft theme tables, runs `contrast.py` on each tile's pairs, renders each on phone and desktop, and renders the HUD's floating parts with `--transparent` over backdrops. Shows one contact sheet and asks for a pick, offering a mix. Builds no HUD before the pick.

Round 3 answers: "B, but with A's colours."

Assess: renders the mix as a new tile and shows it before building on it. Logs the pick and its reasons in the taste log and saves the sheet in `docs/design/picks/` at about 1500 px. Turns the chosen table into the theme module, keeps the specimen story rendering it as the style guide, deletes the other drafts and adds the raw-value guard to the check.

## Make it look better, with no theme

Fixture: a Fusion game with a working shop screen built from raw values: the stock font, a half-transparent black panel, one corner radius on everything, a red X close button and a uniform grid of equal cards. No stories, theme or design files. The user is present and answers the brief.

Request: "Make the shop look better."

Assess: treats the request as a restyle of a major screen and takes the full path. Proposes a story format the project's preview library supports, or renders the place, then renders the current shop on phone and desktop and names the generic tells it sees in them. Asks the brief before restyling, and gets a direction picked from tiles before changing any screen. Guards only the folders moved to the theme. Fails if it restyles straight away by swapping one set of raw values for another, or picks the direction for a user who is present.

## The user is away

Fixture: the new-UI fixture after round 2: a brief and references in place, no tiles or theme, and the user unreachable.

Request A: "I'm away until tomorrow. Build the HUD without waiting for me."

Assess: doesn't stop at the first choice. Makes the three tiles, picks the one it would recommend and marks it `provisional` in the taste log with its reasons, and does the same for the layout pick. Keeps what depends on the picks in tokens rather than hand-tuned screens. Runs checks and review rounds as usual. The final summary names each provisional pick and what changing it would cost. Fails if a pick is logged as final, or the summary implies the user approved anything.

Request B, the project as A left it, with the user back: "Add the quest tracker to the HUD."

Assess: raises the provisional picks with the user before building further on them.

## Review hygiene

Fixture: a themed game with a finished shop screen, its state stories, a brief, references, and a taste log whose standing preferences include 3 px dark outlines. rendering.md lists a known gap the shop's header gradient hits. A stub `roblox-ui-reviewer` agent records each prompt it receives. In round 1 it answers Ship after fixes, with a major fix to the hierarchy and a minor fix asking for thinner outlines; in round 2 it answers Ship.

Request: "The shop is built. Take it through review."

Assess: runs the check and looks at its own renders against the rubric before spending a review. The round 1 prompt gives absolute paths to the contact sheet first and then each render, all at most 1500 px; the style guide render; the brief, every reference and the taste log; the rubric and AI tells; the screen's job and content ranking; and render notes with each render's device, size and image scale, the text sizes after the root scale, the input each render was drawn with, what the white stands for, how the shop sits over the touch controls, the gradient gap, and the `missingAssets` and `notes` from `rhr ui --json`. It sends no code, file excerpts or opinion of its own. Applies the hierarchy fix, declines the outlines fix citing the taste log, checks again, and sends round 2 to the same reviewer with SendMessage and each fix's status. Stops at Ship and shows the user the final sheet, the verdict, and what it applied and declined. Fails if a standing preference is reversed on the reviewer's word, or round 2 goes to a fresh reviewer while the first can be continued.

## Minor screen

Fixture: the themed game from the light path, whose base components have no slider.

Request: "Add a settings screen with music and sound effect volume."

Assess: offers no layouts. Adds a Slider to the base components first, with a state-grid story, then builds the screen from the theme and base components. Checks and looks, usually runs one review round, and shows the user. Fails if it styles a slider inside the screen alone or makes the user pick between layouts.

## Not this skill

Fixture: the themed game from the light path.

Request: "The shop's buy button charges twice when it's tapped twice quickly. Fix it."

Assess: fixes the logic with the project's usual checks and leaves the look alone. Asks no design questions and makes no tiles, renders for review or reviewer calls. Fails if the fix changes a visual value.

## Reviewer calibration

Fixture: the reviewer agent alone. Two shop screens for the same brief and references, rendered with rhr on phone and desktop: A is deliberately generic (the stock font, a half-transparent black panel, one radius on everything, a red X, a uniform grid of equal cards, everything centred); B is built to match the references. The taste log has a Reviewer calibration entry that B shows.

Request: the round 1 prompt from review.md, once for each screen, in separate agents.

Assess: for A, flags the tells by element and device, ranks them by what they cost a player with the rubric's severity, keeps at most five fixes in the theme's terms, and answers Rework or Ship after fixes. For B, answers Ship or asks only minor fixes, and doesn't flag the calibration entry. Both open the contact sheet before the full-size renders, then every render and reference, open no source file, keep the answer's shape at about 400 words or fewer, and put anything that looks like the renderer under Render doubts. Fails if A gets Ship, or B gets a major fix for a choice its references settle.
