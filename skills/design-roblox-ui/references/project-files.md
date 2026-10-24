# Project files

The design lives in the repository, so the next agent and the reviewer start from the user's decisions instead of guessing them. A pick that isn't written down gets undone by the next agent who has a different idea.

| File | Written | Read |
| --- | --- | --- |
| `docs/design/brief.md` | In the [brief](process.md#brief) and [references](process.md#references) steps; each major screen adds its job and content | Before any design work, and by the reviewer |
| `docs/design/refs/` | By the user | When writing the brief, and by the reviewer |
| `docs/design/taste.md` | After every pick, review round and user comment | Before any visual change, and by the reviewer |
| `docs/design/picks/` | With each pick | When someone asks why a direction or layout was chosen |
| The theme module | In [theme and base components](process.md#theme-and-base-components) | By every UI component |

The project guide can move any of these; when it does, use its paths.

## Brief

About a page, read before every design task and sent to the reviewer. It says what the game needs from its UI, not how the UI is built. It holds:

- the game and its players in a paragraph: who, how old, how long they play, how much they read;
- platforms, ranked;
- the feel: three words for it, two it must not be;
- fixed constraints, including the size and aspect ratio of any art the UI frames;
- the references: what to take from each and what to leave, then what they share, or that the user had none;
- the screens, with a job and ranked content for each major one;
- assumptions you made, dated, so the user can correct them.

Write what the references share in words and in the hex values `palette.py` measures, not only as images. `refs/` is often gitignored, and an agent without the images, such as a cloud session, still has the words.

An example, for a made-up game:

```markdown
# Design brief: Tidewater

Co-op fishing on a stormy coast. Crews of 2 to 4 sail out, fish, and sell the
catch at the harbour. Players are 10 to 16, play for 20 to 40 minutes, and read
little during a trip.

## Platforms

Phone first, then desktop, tablet, console.

## Feel

Weathered, warm, handmade. Not glossy, not sci-fi.

## Constraints

- The logo in `assets/logo.png` stays as it is.
- Fish icons are 512 px square paintings from the art team; UI icons must sit beside them.

## References

| File | Take | Leave |
| --- | --- | --- |
| `refs/pirate-map-ui.jpg` | Paper and ink, hand-drawn edges | The parchment texture behind everything |
| `refs/farm-shop.png` | Dense item lists that stay readable | Pixel-art type |
| `refs/travel-poster.jpg` | Two strong accents on cream | The distressed print texture |

What they share: cream and sand paper (`#F3E9D2`, `#E8D9B5`), dark brown ink
(`#2B1D14`) for text and outlines, two accents (rust `#C4552D`, sea green
`#1F6F6B`), 2 to 3 px outlines instead of shadows, small radii (4 to 8), heavy
numbers, dense lists and a sparse HUD.

`refs/` is in `.gitignore`: the images are other studios' work.

## Screens

| Screen | Kind | Status |
| --- | --- | --- |
| HUD | Major | Built |
| Shop | Major | Layout picked |
| Inventory | Major | Not started |
| Settings | Minor | Not started |

### Shop

Job: sell today's featured rod, and let players restock bait fast.

Content, most important first:

1. The featured rod: its art, stats and price
2. The player's coins
3. Bait, bought every trip
4. Other rods
5. Cosmetics

## Assumptions

- 2026-10-20: phone first, because the user didn't rank platforms.
```

## Taste log

`docs/design/taste.md` is how the user's eye carries from one screen and one agent to the next. It has three parts:

- **Standing preferences:** rules that hold on every screen, each dated. When the user says the same thing twice, about any screen, it becomes one.
- **Reviewer calibration:** what the reviewer flags that the user likes anyway. Every review is sent this list.
- **Decisions,** newest first: each pick, review and user comment.

In a session with a taste vault (a start note says how to propose a rule to it), propose each new standing preference to the vault instead of writing it here; this log keeps the reviewer calibration and decisions.

Each pick is marked `(user)` when the user chose it, or `(provisional)` when an agent chose alone ([user away](process.md#when-the-user-isnt-there)). When the user confirms a provisional pick, change its mark to `(user, confirmed <date>)`. A reversed pick gets a new entry naming the one it replaces; leave the old entry, so its reasons stay readable.

An example:

```markdown
# Taste log

## Standing preferences

- No glow or drop shadows; depth comes from the 3 px ink outline. (2026-10-21)
- Coin counts are never abbreviated below 100,000. (2026-10-22)

## Reviewer calibration

- Flags the 3 px outlines as heavy: house style, keep them.
- Asks for more padding in item lists: the user wants them dense.

## Decisions

### 2026-10-23 Inventory layout: A, "Tackle box" (provisional)
- Chosen for: slots in a grid match the fish icons; the selected fish's
  details sit beside the grid, so phone needs no second screen.
- Rejected: B, "List" (long names truncate on phone).
- Sheet: `picks/2026-10-23-inventory-layouts.png`

### 2026-10-22 Shop: user review
- "The featured rod should be even bigger on phone." It now takes 55% of the width.
- "The bait list is great." No change.

### 2026-10-21 Shop layout: B, "Featured shelf" (user)
- Chosen for: the featured rod reads first on phone, and bait is one tap away.
- Rejected: A, "Grid" (nothing featured); C, "Tabs" (bait hidden behind a tab).
- Mixed in: C's coin chip in the top right.
- Sheet: `picks/2026-10-21-shop-layouts.png`

### 2026-10-20 Style tile: A, "Field journal" (user)
- Chosen for: closest to the references; warm paper and ink outlines.
- Rejected: B, "Harbour neon" (against "not sci-fi"); C, "Clean slate" (could be any game).
- Sheet: `picks/2026-10-20-style-tiles.png`
```

## Picks

`docs/design/picks/<date>-<what>.png`, such as `2026-10-21-shop-layouts.png`, is the contact sheet the user picked from, rejected options included. Drafts are deleted after a pick, so the sheet is the only record of what was turned down and why the log's reasons make sense. Commit the sheets, and keep each to about 1500 px on its long side with the contact sheet's `--max-size`.
