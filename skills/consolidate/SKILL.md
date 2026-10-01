---
name: consolidate
description: Turn accumulated findings and suggestions into a defensible proposal for a human or agent recipient. Use when analysis, including an agent handoff, needs synthesis into a recommended direction and concrete next move.
---

# Consolidate

Turn what you have learned into a defensible proposal the recipient can understand, evaluate, and act on within their authority. Take responsibility for recommending a direction: explain what should change, what it would accomplish, and why it fits the user's goal. Exercise judgment about what matters, what belongs together, and what to drop or defer. A direction can include as many improvements as needed; show how they contribute to the intended outcome. Apply this when synthesis is needed; routine status updates, raw evidence transfers, and straightforward instructions can stay as they are.

Ground each proposed change in an observed problem or explicit goal. Check that its evidence actually supports the need for that change: a related fact or missing information does not establish a defect. When evidence only raises a question about a component, recommend checking it and make any change conditional on what that check finds. Preserve working capabilities unless a justified change is needed. Label speculative improvements as hypotheses and identify what would validate them before treating them as commitments or prerequisites.

Make each meaningful choice assessable. Keep its proposed change, reason, and evidence together. Explain what the observation, test result, source, or stated requirement establishes, link it when available, and distinguish that support from your inference.

Separate suggestions the recipient can assess individually, while making dependencies and consequential tradeoffs visible. Keep implementation details with the choice they support.

Use the evidence already available. For factual uncertainty, state an assumption if the next action remains justified; otherwise resolve the specific missing fact. When an unresolved user preference changes the choice, ask the user or carry the open question back to the responsible caller, and recommend any next action that remains useful either way. Measurements can inform a tradeoff but cannot establish the user's priorities. Any proposed investigation should identify its question and how the answer affects the direction.

When the proposal depends on a consequential unresolved direction choice, use `$direction-selection` for that choice, carrying forward the goal, constraints, priorities, and existing evidence. Honor its applicability routing, then incorporate the returned outcome into the proposal without repeating completed comparison work. Preserve the outcome's scope, blockers, and limitations; keep unaffected recommendations actionable. Routine prioritization and organizing compatible improvements remain within consolidation.

Adapt presentation to the recipient. Use lightweight emoji signposts in every consolidation output, including short recommendations and agent handoffs. Lead with 🧭 for the recommended direction and close with ➡️ for the concrete next move. Use 🔎 for supporting evidence and ⚖️ for a material tradeoff or uncertainty when those need their own lines. Let the emojis help readers scan; they need not create a fixed template. For a human, keep each proposed change close to its reason and evidence, and put caveats beside the relevant claim. Mention deferred possibilities separately only when their exclusion helps explain the proposal. For an agent, use a compact handoff suited to its task or required contract: retain the goal, recommended direction, supporting evidence, material uncertainty, dependencies, open decisions, and next action with its owner when known.

Finish with a concrete next move, retaining any unresolved user choice alongside it. The result is complete when the recipient can understand the direction, judge its basis, and decide or take the next authorized step without reconstructing the analysis.

Continue into execution when the original request already authorizes it. Consolidation or passing its result to another agent grants no additional execution authority and does not resolve user-owned preferences.
