# Rubric

What a finished screen gets right. You go through it before spending a review, and the reviewer judges against it and cites its items by name. Every item can be judged from renders; what can't be is [listed at the end](#what-renders-cant-show).

Look at each render small first, about 400 px wide: `rhr ui <story> --device phone --max-size 400`, or a contact-sheet cell. A player's first glance decides what they notice, and at that size hierarchy and grouping show before detail distracts. Then look at full size.

## Items

1. **Job.** The screen's main action is its most prominent element and one tap away. Two equally loud actions mean the job wasn't decided; the brief says what it is.
2. **Hierarchy.** The brief's content ranking shows in size, weight, colour and position. At 400 px wide the top two items still read, and the rest recede.
3. **Legibility.** Text meets the [bars](#bars) on every device. Nothing is clipped, overlapping, or cut short without a way to read it in full. Text over the game world holds over white, black and busy backdrops.
4. **Reach and safety.**
   - Targets meet the bars and sit about 8 apart.
   - Nothing that matters is under the thumbstick, the jump button, a notch or Roblox's top-bar buttons.
   - On a landscape phone, frequent actions sit along the sides and bottom, near the thumbs. The top centre is farthest from both.
   - Spending and destructive actions sit apart from frequent ones, so a missed tap costs nothing.
5. **Grouping and alignment.** Related things sit closer together than unrelated ones, and space separates groups before borders and boxes do. Edges line up on a few shared lines. Every gap is a step of the theme's space scale.
6. **Consistency.** One look per role: every primary button matches, and selected, locked and new each look one way across the game. Radii, strokes and depth come from the theme, and nested corners are concentric. Icons come from one family.
7. **Character.** The brief's three feel words show and its two "not" words don't. At least one choice is specific to this game rather than a default. No [tell](ai-tells.md) appears without a reason.
8. **Content and states.**
   - Worst-case content: the longest name, the biggest number, many items and none.
   - Every state that changes the layout is rendered.
   - The empty state says what to do next.
   - Copy is plain and specific ("Buy for 250", not "Purchase"), lines are in sentence case, and numbers have one format across the game.
9. **Density.** The HUD shows only what a player needs mid-play and leaves the world visible. Menus can be dense, as long as targets keep their size and groups stay distinct.
10. **Polish.** Icons and labels are optically centred, baselines line up along a row, borders don't double where two boxes meet, and things that should match do, to the pixel. Discount what rhr draws differently from Roblox ([known gaps](rendering.md#known-gaps)).

## Bars

| What | Bar | Source |
| --- | --- | --- |
| Text a player reads | TextSize 20 (`body` and `label`) on phone; after the root scale, 25 on a 1080p desktop and 36 on a 1080p TV | [Type](theme.md#type) and [scaling](theme.md#scaling) |
| The smallest text | 14 (`caption`), for nothing a player needs; MinTextSize never below 9 | Apple's 11 pt minimum, in Builder Sans |
| Touch targets | 44 by 44, about 8 apart | [WCAG 2.5.5](https://www.w3.org/TR/WCAG22/#target-size-enhanced), Apple's 44 pt, Material's 8 dp spacing |
| Mouse targets | 24 by 24 | [WCAG 2.5.8](https://www.w3.org/TR/WCAG22/#target-size-minimum) |
| Text contrast | 4.5:1, or 3:1 for large text | [Contrast](theme.md#contrast) |
| Icons, control edges, the selection outline and disabled text | 3:1 | [Contrast](theme.md#contrast) |

## Severity

- **Major:** a player can't do the screen's job, can't read or reach something they need, or the screen breaks on a device the brief ranks; or it contradicts the brief or the taste log.
- **Minor:** everything else. The screen works, and the fix makes it read or look better.

## Quick check

For a small change inside an existing theme, on the [light path](../SKILL.md#light-path):

1. Only theme tokens and base components. A new token is named by its role, added to the theme, and named in your summary.
2. Text meets the bars, and the worst-case content fits on phone.
3. Every new colour pair passes `contrast.py`.
4. Targets meet the bars and stay clear of the touch controls.
5. Every state you touched is rendered on phone and desktop, and you opened the PNGs.
6. Spacing, radii and strokes match the neighbours.
7. Nothing contradicts the taste log.

## What renders can't show

- Motion: timing, easing and springs settling ([motion](process.md#motion)).
- Hover, press and gamepad selection, unless a story renders that state.
- Scrolling, dragging and long presses.
- Gamepad navigation: where selection starts and the order it moves in.
- The live world behind the UI, unless the render is laid over a screenshot of the game.
- Text at the player's largest text size ([accessibility settings](roblox-checklist.md#accessibility-settings)).
- A device used with another input, such as a gamepad on desktop, unless a story passes the input kind in ([input](roblox-checklist.md#input)).

These are checked in a Studio play-test and in the user's review. Say in your summary which of them the change touches and whether you checked them.
