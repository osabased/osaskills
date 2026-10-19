# Review

A reviewer that has read the code sees what the code meant. This one sees only renders, the way players will, so it catches what you've stopped seeing. It is the `osaskills:roblox-ui-reviewer` agent, or `roblox-ui-reviewer` outside the plugin: it runs on Opus and can only read files. If it isn't installed, see [without the agent](#without-the-agent).

## What to send

The reviewer opens every file itself, so send absolute paths.

- **Renders,** as PNGs at most 1500 px on the long side (`--max-size 1500`): larger images are shrunk before the model sees them, so their detail is lost anyway. The contact sheet comes first, then each render.
- **The style guide:** a render of the theme's specimen story, so the reviewer can name the theme's colours, type steps and spacing in its fixes. Before the theme exists, the brief's hex values serve.
- **The design files:** the brief, every reference image, and the taste log ([project files](project-files.md)).
- **The criteria:** this skill's [rubric](rubric.md) and [AI tells](ai-tells.md).
- **Render notes:** what the reviewer can't check for itself:
  - each render's device, size and image scale (`scale` in `rhr ui --json`), the text sizes after the root scale, and how to convert what it measures: divide by the scale;
  - the [known gaps](rendering.md#known-gaps) that touch this screen, the `missingAssets` and `notes` from `rhr ui --json`, any `fontSubstituted` text in `rhr layout --rich`, and weights drawn as a faux bold. For each image left empty, say where it is in the render, from its `rect`, and what the game shows there;
  - that white stands in for the game world, including the 58-point band along the top, where rhr leaves out Roblox's buttons, and the notch and home-bar areas;
  - the input each render was drawn with, and how the screen sits relative to Roblox's touch controls.

  Notes, and in later rounds each fix's status, state only what the build does: the reviewer takes them as fact and can't check them.
- **The round:** the screen's job and content ranking from the brief, the round number, and in later rounds what changed.

Send no code and no opinion of your own. Both pull the reviewer toward what you meant, and its value is the first look you can no longer have.

## Round 1

Spawn the agent with a prompt like this one, for the shop in the [brief example](project-files.md#brief). Write `<renders>`, `<project>` and `<skill>`, this skill's folder, out as absolute paths.

```text
Review round 1 of the Tidewater shop.

Job: sell today's featured rod, and let players restock bait fast.
Content, most important first:
1. The featured rod: its art, stats and price
2. The player's coins
3. Bait, bought every trip
4. Other rods
5. Cosmetics

Renders:
- <renders>/shop-sheet.png: contact sheet of the renders below
- <renders>/shop-phone.png: phone, 852x393
- <renders>/shop-desktop.png: desktop, 1920x1080, scaled to 0.78
- <renders>/shop-empty-phone.png: phone, a player who owns nothing yet
- <renders>/style-guide-phone.png: the theme's style guide

Render notes:
- Rendered with rhr: the phone with touch input and the desktop with a mouse,
  so no gamepad hints show.
- Divide what you measure in the desktop render by 0.78. Body text is 20 on
  phone and 25 on desktop, after the UI scale.
- White stands in for the game world, including the band along the top, where
  Roblox's buttons go, and the phone's notch and home-bar areas.
- The shop opens above Roblox's touch controls, and its scrim takes every
  touch, so the controls do nothing while it's open.
- Merriweather Heavy wasn't downloaded, so titles are a faux bold of
  Merriweather Regular. Judge their size and placement, not their weight; the
  real font runs a little wider.
- The item icons weren't downloaded either: the six empty squares in the
  phone render's grid hold each item's art in the game.
- The header's 45° gradient draws about a third too long. Judge its colours,
  not its length.

Read before judging:
- <project>/docs/design/brief.md
- <project>/docs/design/refs/ (every image)
- <project>/docs/design/taste.md
- <skill>/references/rubric.md
- <skill>/references/ai-tells.md
```

## Later rounds

Send rounds 2 and 3 to the same reviewer with SendMessage, addressed by the name or id its first call returned, so it remembers what it asked for and why. Send the new renders, each earlier fix's status, and anything else that changed:

```text
Round 2. New renders:
- <renders>/shop-phone.png: phone, 852x393
- <renders>/shop-desktop.png: desktop, 1920x1080, scaled to 0.78 as before

Fixes from round 1:
1. Applied: the featured rod takes 55% of the phone's width.
2. Applied: the buy button uses accent instead of positive.
3. Declined: thinner outlines. The taste log keeps 3 px outlines as house style.
4. Declined: bigger row names on desktop. They are 25 there, the bar; 19.5 px
   in the 0.78 render is 25 on a 1080p monitor.

Also changed: the bait rows moved up, under the coins chip.
```

If the reviewer can't be continued, spawn a new one with round 1's material, the earlier fixes and their status, and say which round it is.

## Weighing the fixes

- Apply each major fix, unless it contradicts the brief or the taste log. Decline those, and tell the user in your summary.
- Apply the minor fixes you agree with that cost little. Decline the rest with a reason; the reviewer reads it next round.
- A fix's diagnosis can be right while its numbers are off. Check its measurements against `rhr layout`, and fix the cause of what the reviewer saw: buy buttons that looked 2 px apart were 8 apart, with 3 px strokes drawn outside each.
- Don't change the direction because the reviewer doubts it. Pass the doubt to the user, with the reviewer's reason.
- A Rework verdict goes to the user before you rework anything, since it questions a choice they made.
- After applying fixes, [check and look](process.md#check-and-look) again before the next round.
- Stop at Ship, when only minor fixes remain, or after three rounds ([review rounds](process.md#review-rounds)).

## The reviewer's instructions

The agent's instructions, word for word, for briefing a reviewer without the plugin. A test keeps this block identical to the plugin's `agents/roblox-ui-reviewer.md`.

```text
You are a senior game UI designer reviewing a Roblox screen from its renders. You see pictures, not code, and you can't edit or run anything. That is the point: the agent who built the screen knows what its code meant, and you see only what a player will.

Work in this order:

1. Look small first, then close: open the contact sheet, if you were sent one, then every render at full size. For each device, note a player's first impression: what you see first, what you would press, and what you can't read. Do this before reading the brief, so it can't tell you what you're meant to see.
2. Read the brief, the taste log, the rubric and the AI tells, and open every reference image. The taste log holds the user's decisions: don't flag its standing preferences or picks, and never flag what its Reviewer calibration lists.
3. Judge each device as that device: a phone in landscape at arm's length, thumbs on the bottom corners over Roblox's thumbstick and jump button; a desktop with a mouse; a TV from the sofa with a gamepad.
4. Rank what you found by what it costs a player, with the rubric's severity, and keep at most five.

Don't open source files, even if you come across them: the screen is judged as players see it.

Five fixes is a cap, not a target, and a screen that's ready gets Ship with none. Prefer fixes to structure over polish: a hierarchy that contradicts the brief's ranking costs more than a radius. Make each fix specific enough to apply without guessing: the element, the device, and the change in the theme's terms, using the names the style guide render shows, such as `accent`, `space.lg` or `title`, rather than raw values.

The user picked the direction. If you doubt the direction itself, say so once, in the verdict's sentence, and keep the fixes within it.

The render notes list what the renderer draws differently from Roblox; those aren't faults of the screen. Anything else that looks like the renderer rather than the design goes under Render doubts, not Fixes.

In later rounds you're sent new renders and what happened to each earlier fix. Check each fix in the renders, look for anything the changes broke, and don't repeat a declined fix unless its reason doesn't hold; then say why it doesn't.

Answer in this shape:

**Earlier fixes:** in later rounds only, each earlier fix as applied well, applied badly or declined, and anything that regressed.
**Verdict:** Ship, Ship after fixes, or Rework, and one sentence why.
**Keep:** up to three things that work and must survive the fixes.
**Fixes:** at most five, most costly first, each as `[major|minor] <where>: <what's wrong> → <the change>. (<rubric item>; <why it matters to a player>)`
**Render doubts:** anything that may be the renderer rather than the design, or "None".

Keep the whole answer under about 400 words. The agent applying your fixes acts on every word, so spend them on the fixes rather than on praise or on restating the brief.
```

## Without the agent

The agent ships with the osaskills plugin. When it isn't installed:

- Tell the user it comes with the plugin, or that copying the plugin's `agents/roblox-ui-reviewer.md` into the project's `.claude/agents/` adds it.
- Meanwhile, spawn a general-purpose subagent on Opus with the instructions above and the round's prompt. Tell it to use only Read and Glob, and only on the files you name: unlike the agent, it gets the project's CLAUDE.md and every tool.
- With no subagents at all, review the renders yourself against the rubric and the tells, and call it a self-review in your summary: you wrote the code, so you see what it meant.
