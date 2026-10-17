---
name: bigger-picture
description: Restates the user's goal and sorts each recent or planned change into what serves it and what is off-goal, in a few lines with no implementation detail, then keeps working. Use in a long session before starting or proposing a change the user's goal doesn't clearly need (a rename, cleanup, refactor, swap or suggestion, including a step from an earlier plan the user said to carry on with), when several changes have piled up since the user last weighed in, or when the user asks why a change matters or seems unsure it helps ("wait, why are we touching X?"). Not for a change the user just asked for, or a short exchange.
---

# Bigger Picture

In a long session the user can lose sight of why the agent is doing what it does, and the agent can lose sight of what the user wanted. Give the user just enough to judge whether the recent and planned changes serve their goal. They trust you with the implementation, so leave it out.

## When to run it

- You're about to start or propose a change the goal doesn't clearly need. That includes a step from an earlier plan: "carry on with the plan" approves the plan's purpose, not every step in it.
- Several changes have piled up since the user last weighed in.
- The user asks why a change matters, or sounds unsure it helps.
- The user or then-what asks for it.

Skip it for a change the user just asked for, a short exchange, or when nothing has changed since the last check.

## Sort the changes

1. **Recover the goal.** Take the user's request and any later corrections, and quote their words where you can. Quote the outcome they want, not the steps they asked for along the way. If the goal is unclear, give your reading and mark it "(my reading, correct me)".
2. **Collect the changes.** Include the ones made since the user last weighed in or since the last check, and the ones you're about to make or propose.
3. **Sort each one.** A change serves the goal when the goal needs it or it directly supports what the user asked for. Say how, in terms of what the user gets. A change the user didn't ask for still serves the goal when the goal needs it; put it under Serves it and say it wasn't asked for. Renames, tidy-ups, refactors and swaps that the goal doesn't need are off-goal, even when they're improvements.
4. **Act on off-goal changes.** Drop planned ones from the plan and list them as dropped, so the user can ask for them back. Only an explicit ask brings one back; "keep going" means keep going without it. Flag ones already made and leave them in place.

## Format

Write these as normal lines (not a code block):

> 🎯 **Goal:** "players keep their progress if they disconnect mid-match"
>
> **Serves it:** progress now saves the moment a player drops, and retries if that save fails. Planned: rejoin mid-match to confirm progress comes back.
>
> ⚠️ **Off-goal:** settings menu was renamed (left in place). Dropped from the plan: folder reorganization and UI library swap; ask to bring either back.

When nothing is off-goal, say so; that is the answer to "why are we touching this?":

> ⚠️ **Off-goal:** nothing.

- Describe each change by what's different for the user or the product. Leave out file, function and code names and how a change works.
- Group changes with the same purpose into one phrase, so the whole thing stays within 80 words even with many changes. List off-goal items individually, since those are what the user checks, a few words each.
- Add nothing after the Off-goal line: no offers, reasons or caveats beyond "ask to bring it back".
- Use only the two emoji shown, and drop them when the user asks for plain text or the output goes into a file, commit, PR, or another agent's prompt.

## Keep going

Start the message that ends this turn with the three lines, in the format above, updated with anything you did after the check, even when that message also reports other work. Don't rephrase them into your own summary; the fixed shape is what lets the user find the check. Don't ask for approval or wait. After the lines, carry on with the on-goal work. When the user's question prompted the check, the three lines are the answer; add a sentence only if they asked something they don't cover. When then-what runs this, print it first and let then-what build its recommendation on the result without repeating the buckets.
