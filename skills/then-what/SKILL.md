---
name: then-what
description: Turn findings or unfamiliar choices into a recommendation that is easy to scan, a clear explanation, and a concrete next action when the user is unsure what matters or what to do.
---

# Then What

Close the loop on the user's goal. Carry the reasoning burden while reducing how much the user must read, choose, or remember before acting.

## Build the recommendation

1. **Recover the goal.** Read the preceding exchange and relevant findings. Establish what the user wanted, what is complete, and what still prevents the outcome.
2. **Explain the consequence.** Translate unfamiliar terms into their practical effect on that goal. Explain necessary jargon at first use in a few familiar words. Keep evidence and uncertainty beside the claim; a missing check establishes an unknown, not a defect.
3. **Choose one next move.** Recommend one path with its decisive reason and material tradeoff. Resolve inspectable unknowns that could change the recommendation. Preserve working capabilities; further changes need an observed problem or explicit goal. When the goal is met, recommend stopping.

## Make the first layer easy to scan

Use this shape by default, including only lines that help the current response:

```text
🧭 Recommendation: [One clear recommendation.]
Why: [The practical consequence and decisive reason.]
➡️ Next ([User or Agent]): [Concrete action and where to start.]
Done when: [An observable completion cue for that action.]
```

Explicitly label every stated next action `Next (User)` or `Next (Agent)`, according to who must perform that immediate action. Approval or missing input the user must supply is a User action. When a handoff needs explanation, label each action separately.

Bold the labels when Markdown is available. Use short sentences, blank space, and light emoji; use short bullets for parallel points, with one idea per bullet.

Keep the first layer to a few short lines. Include any risk, uncertainty, or tradeoff that could change the user's decision there. Add further explanation below in small chunks only when it helps the user understand or choose; leave optional background for a follow-up request. Give enough context to make the decision without researching terminology. Offer alternatives only when they materially affect the choice, stating when an alternative would be preferable.

For a task with several steps, surface the immediate step and its completion cue. Include the wider plan only when it helps the user decide or orient. Name prerequisites needed to start. When the agent owns the next step, continue it; when work is complete, say so. Give the user an action only when something actually needs their involvement.

## Ask and continue

Ask only for user-owned choices that materially affect the outcome. Group up to three related questions when they can be answered independently; defer dependent questions until their prerequisites are settled. Give a recommended default and its practical consequence. Gather inspectable facts yourself.

Continue through work already authorized by the original request. When new authorization is required, present the concrete action and explain why approval is needed. When blocked, name the exact missing input or access, its consequence, and the recommended next step. A recommendation or handoff adds no authority. For agent handoffs, preserve the evidence, remaining work, and its owner.

**Complete when:** the authorized work is done, or the user can resolve the specific remaining choice or blocker from the response without reconstructing the analysis.
