---
name: consolidate
description: Turn accumulated findings and suggestions into a defensible proposal the user can understand, evaluate, and steer. Use when analysis needs synthesis into a recommended direction and concrete next move.
---

# Consolidate

Turn what you have learned into a defensible proposal the user can understand, evaluate, and steer. Take responsibility for recommending a direction: explain what should change, what it would accomplish, and why it fits the user's goal. Exercise judgment about what matters, what belongs together, and what to drop or defer. A direction can include as many improvements as needed; show how they contribute to the intended outcome.

Ground each proposed change in an observed problem or explicit goal. Check that its evidence actually supports the need for that change: a related fact or missing information does not establish a defect. When evidence only raises a question about a component, recommend checking it and make any change conditional on what that check finds. Preserve working capabilities unless a justified change is needed. Label speculative improvements as hypotheses and identify what would validate them before treating them as commitments or prerequisites.

Make each meaningful choice assessable. Keep its proposed change, reason, and evidence together. Explain what the observation, test result, source, or stated requirement establishes, link it when available, and distinguish that support from your inference.

Separate suggestions the user could reasonably accept, adjust, or defer individually, while making dependencies and consequential tradeoffs visible. Keep implementation details with the choice they support.

Use the evidence already available. For factual uncertainty, state an assumption if the next action remains justified; otherwise resolve the specific missing fact. When an unresolved user preference changes the choice, ask about that tradeoff and recommend any next action that remains useful either way. Measurements can inform a tradeoff but cannot establish the user's priorities. Any proposed investigation should identify its question and how the answer affects the direction.

When the proposal depends on a consequential unresolved direction choice, use `$direction-selection` for that choice, carrying forward the goal, constraints, priorities, and existing evidence. Honor its applicability routing, then incorporate the returned outcome into the proposal without repeating completed comparison work. Preserve the outcome's scope, blockers, and limitations; keep unaffected recommendations actionable. Routine prioritization and organizing compatible improvements remain within consolidation.

Lead with the direction. For multi-part proposals, give each current suggestion a bold title followed by separate short Why and Evidence paragraphs, with blank lines between them. Keep caveats beside the relevant claim. Put deferred possibilities in a separate brief paragraph, only when their exclusion helps explain the proposal. Finish with a concrete next move, retaining any unresolved user choice alongside it. Simple recommendations can stay a few lines. The result is complete when the user can understand the direction, judge its basis, and change meaningful parts without reconstructing the analysis.

Continue into execution when the original request already authorizes it. Consolidation alone calls for a recommendation, not additional implementation authority.
