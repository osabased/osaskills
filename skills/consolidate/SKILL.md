---
name: consolidate
description: Turn an open-ended agent response into a clear explanation, recommendation, and concrete next step. Use when findings or unfamiliar choices leave the user unsure what matters or what to do.
---

# Consolidate

Close the loop on the user's goal. Carry the reasoning burden: explain what the findings mean, recommend what to do, and take the next authorized step.

## Build the recommendation

1. **Recover the goal.** Read the preceding exchange and relevant findings. Establish what the user wanted, what is complete, and what still prevents the outcome.
2. **Explain the consequence.** Translate unfamiliar terms into their practical effect on that goal. Keep evidence and uncertainty beside the claim; a missing check establishes an unknown, not a defect. Include enough explanation for the user to judge the recommendation without researching the terminology.
3. **Recommend the next move.** Synthesize the findings into one coherent recommendation, with its decisive reason and material tradeoff. Resolve inspectable unknowns when they could change that recommendation. Ask only for a user-owned choice that materially affects the outcome, giving a recommended default and its consequences. Preserve working capabilities; further changes need an observed problem or explicit goal. When the goal is met, recommend stopping.

## Present and continue

Lead with the recommendation, then explain what matters and the next action. Use 🧭 for the recommendation and ➡️ for the next move unless the requested format calls for plain text. Keep the explanation concise; include alternatives only when they materially affect the user's choice. For agent handoffs, preserve the evidence, remaining work, and its owner.

Continue through work already authorized by the original request. When new authorization is required, present the concrete action and explain why approval is needed. When blocked, name the exact missing input or access, its consequence, and the recommended next step. A recommendation or handoff adds no authority.

**Complete when:** the authorized work is done, or the user can resolve the specific remaining choice or blocker without reconstructing the analysis.
