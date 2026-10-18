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

1. **Recover the goal.** Take the user's request and any later corrections, and state the outcome they want in one short phrase, in their words where you can, without the steps they asked for along the way. If the goal is unclear, give your reading and mark it "(my reading, correct me)".
2. **Collect the changes.** Include the ones made since the user last weighed in or since the last check, and the ones you're about to make or propose.
3. **Sort each one.** A change helps the goal when the goal needs it or it directly supports what the user asked for. Say how, in terms of what the user gets. A change the user didn't ask for still helps when the goal needs it; tag it "not asked for but needed". Renames, tidy-ups, refactors and swaps that the goal doesn't need are not needed for the goal, even when they're improvements.
4. **Act on changes the goal doesn't need.** Drop planned ones from the plan and list them as Skipped, so the user can ask for them back. Only an explicit ask brings one back; "keep going" means keep going without it. List ones already made as Kept and leave them in place.

## Format

Print the check as plain markdown, not in a code block and without the `>` quote markers this example sits in:

> 🎯 **Goal:** players keep their progress if they disconnect mid-match
>
> **Helps the goal**
> - Done: progress saves the moment a player drops and loads back when they rejoin
> - Done, not asked for but needed: a failed save retries
> - Next: test a mid-match disconnect on a live server
>
> ⚠️ **Not needed for the goal**
> - Kept: settings menu renamed (already done)
> - Skipped: folder reorganization, UI library swap. Ask to bring either back.

When every change helps the goal, end with this line instead of the second list; that is the answer to "why are we touching this?":

> ⚠️ **Not needed for the goal:** nothing

- End the Goal line at the outcome, even when the user named a first step. Write "players keep their progress if they disconnect mid-match", not "…, starting with a save when they drop"; the steps belong in the bullets.
- Use only these tags, in this order: Done; Done, not asked for but needed; Next; Next, not asked for but needed; Kept; Skipped.
- Put all the changes with one tag into one bullet, joined with commas or "and". Keep every bullet, its tag included, under 20 words; aim for about 15. Start a second bullet for that tag only when one can't fit. Name each Kept and Skipped change in a few words, since those are what the user checks.
- Describe each change by what's different for the user or the product. Leave out file, function and code names and how a change works.
- End the Skipped bullet with "Ask to bring it back." ("either" or "any" for more than one). Add nothing after the last bullet: no offers, reasons or caveats.
- Use only the two emoji shown, and drop them when the user asks for plain text or the output goes into a file, commit, PR, or another agent's prompt.

## Keep going

Start the message that ends this turn with the check, in the format above, updated with anything you did after it, even when that message also reports other work. Don't rephrase it into your own summary; the fixed shape is what lets the user find it. Don't ask for approval or wait. After the check, carry on with the work that helps the goal. When the user's question prompted the check, the check is the answer; add a sentence only if they asked something it doesn't cover. When then-what runs this, print it first and let then-what build its recommendation on the result without repeating the lists.
