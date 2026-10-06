---
name: consolidate
description: Turn accumulated findings and suggestions into a recommended direction and concrete next move for a human or agent. Use when analysis needs synthesis; skip routine status updates and raw evidence transfers.
---

# Consolidate

Turn findings into a proposal the recipient can judge and act on. Recommend a coherent direction, explain its effect, and finish with the next useful action.

## Build the recommendation

1. **Establish the need.** Ground each proposed change in an observed problem or explicit goal. A related fact or missing evidence may justify a check, without establishing a defect. Make speculative improvements conditional on what would validate them.
2. **Synthesize.** Group changes that serve the same outcome; keep independently assessable choices separate. Put each change beside its reason, decisive evidence, dependencies, and material tradeoff. Preserve working capabilities unless the goal or evidence justifies changing them.
3. **Resolve only deciding uncertainty.** Reuse available evidence and distinguish observations from inference. Resolve a missing fact when it could invalidate the next step; ask about a user-owned preference when it changes the choice. Keep unaffected recommendations actionable.

If a consequential direction remains unresolved, use `direction-selection` for that choice, carrying the goal, constraints, priorities, and evidence. Incorporate its returned result, scope, and blockers without repeating the comparison. Routine prioritization and grouping compatible improvements remain here.

## Present and continue

Lead with the recommendation and its main reason. Keep evidence and caveats beside the claims they qualify; omit empty sections and process narration. For human-facing recommendations, use 🧭 for the direction and ➡️ for the next move unless the requested format calls for plain text. For agent handoffs, use the receiving task's format and retain relevant evidence, dependencies, open decisions, authority, and ownership.

Finish with a concrete next action and any unresolved user choice. Continue when the original request authorizes that action; a recommendation or handoff adds no authority.

**Complete when:** the recipient can understand the proposal, judge its basis, and take or decide the next step without reconstructing the analysis.
