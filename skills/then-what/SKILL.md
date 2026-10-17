---
name: then-what
description: Turns findings, review results, or unfamiliar options into one scannable recommendation, a plain-language why, and a labeled next action (user or agent) with a done-when cue. Invoke with /then-what after a long review, audit, debugging session, or agent report leaves you unsure what matters or what to do next.
disable-model-invocation: true
---

# Then What

Close the loop on the user's goal. Do the reasoning for them and cut down what they must read, choose, or remember before acting.

## Build the recommendation

1. **Recover the goal.** Read the preceding exchange and findings. Establish what the user wanted, what is done, and what still blocks the outcome. If that work includes changes the user didn't ask for or the goal doesn't need, or your recommendation would be one, load the bigger-picture skill, print its output first, and build on it.
2. **Explain the consequence.** Translate unfamiliar terms into their practical effect on that goal, in a few familiar words at first use. Keep evidence and uncertainty next to the claim. A check that wasn't run means "unknown", not "broken".
3. **Choose one next move.** Recommend one path with its deciding reason and main tradeoff. Look up anything you can inspect that could change the recommendation. Don't recommend changing things that work unless there is an observed problem or the user asked. When the goal is met, recommend stopping.

## Format the first layer

Write these as normal lines (not a code block), keeping only the lines that help:

- 🧭 **Recommendation:** one clear recommendation.
- **Why:** the practical consequence and deciding reason.
- ➡️ **Next (User)** or **Next (Agent):** the concrete action and where to start.
- **Done when:** an observable cue that the action is finished.

Label every next action with who performs it. Approval or input only the user can give is a User action. Use only the two emoji shown, and drop them when the user asks for plain text or the output goes into a file, commit, PR, or another agent's prompt.

Keep the first layer to a few short lines and put any risk or uncertainty that could change the decision there. Add explanation below only in small chunks that help the user decide; leave optional background for a follow-up. Mention alternatives only when they would change the choice, and say when one would be better. Name any prerequisite needed to start. For multi-step work, show the immediate step and its done-when cue; include the wider plan only if it helps the user orient.

**Example** (after a performance investigation):

> 🧭 **Recommendation:** Wire the existing lookup index into the inventory-search caller.
>
> **Why:** Every keystroke rescans all items. The tested index returns identical results in 12 ms instead of 140 ms. Redis and a framework swap have no measurements behind them. Mobile wasn't load-tested, so mobile speed is unknown, not broken.
>
> ➡️ **Next (Agent):** Making the caller change now, then running the equivalence and latency tests.
>
> **Done when:** Results match the old output and the sample search runs in about 12 ms.

## Ask and continue

- If the next action is yours and already authorized, do it in this turn. Use `Next (Agent)` to report what you are doing, not to stop.
- Give the user an action only when something actually needs them. Ask only for user-owned choices that change the outcome: up to three independent questions at once, each with a recommended default and its consequence. Hold back questions that depend on an earlier answer. Gather inspectable facts yourself.
- When new authorization is needed, name the concrete action and why approval is needed. When blocked, name the exact missing input or access, its consequence, and the recommended next step.
- Recommending an action does not authorize you to take it. When handing off to another agent, pass along the evidence, the remaining work, and who owns it.

**Done when:** the authorized work is finished, or the user can settle the remaining choice or blocker from your response without reconstructing the analysis.
