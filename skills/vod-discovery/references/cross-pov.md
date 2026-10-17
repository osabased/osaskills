# Cross-POV linking

POV recordings drift and only sometimes share audio. A whole-file offset or a multicam sync is not a prerequisite, and it is not trustworthy across hours.

Before following leads one by one, run [alignment](alignment.md): it proposes where each alternate overlaps the main POV and at what offset, from shared speech and on-screen text, and a pair sheet confirms it at a glance. Local anchors below tighten that offset for an event.

## Follow leads

Investigate another POV when it may explain an off-screen action, add setup or payoff, show the event more clearly, supply useful audio, or reveal a reaction. Follow another hop when new evidence warrants it. Stop when the connection becomes speculative or adds no editorial information.

- Reuse ranges that were already reviewed and combine overlapping investigations.
- If a main POV is designated, organize the first pass around it, but do not treat unrelated secondary-POV moments as irrelevant.
- Track secondary coverage gaps explicitly.
- Delegate bounded investigations (one event, one question) as described in [packet-review](packet-review.md). Verify disputed dialogue, timing or claims of better coverage directly instead of repeating a broad pass.

## Find local anchors

Good anchors are distinctive shared dialogue, a clearly identical action or outcome, a shared visible clock, or common audio.

1. Search the other POVs' transcripts to narrow the interval: `vod.py search` for exact phrases, or [unified search](unified-search.md) for keyword, meaning and OCR leads.
2. View the images around each hit and confirm that the same event is shown.
3. When shared audio could narrow an uncertain correspondence, compare short windows with the Audalign helper in [optional-tools](optional-tools.md). Its output is a candidate for local review or an unresolved result, never a placement.

Shared voice-chat audio can have latency, so independently visible evidence is stronger than a reaction's timing. Two verified anchors can bracket a search interval, but interpolating between them is only a search estimate until checked locally. Never extrapolate one offset across a drifting VOD or across discontinuities. Do not stretch or retime media.

## Record the link

- Give corroborated views of the same event one shared event ID, with source-local start and end seconds recorded independently per POV.
- Give each perspective a role: action, reaction, context, or simultaneous activity.
- Keep editorial status and alignment in separate fields. `alignment: observed` is only for locally verified timing. `estimated` needs a positive `uncertainty_sec` and an explanation, and may stay an uncertain suggestion.
- If no correspondence is established, omit the perspective and report the link as unresolved. Never invent a timestamp or call an independent event simultaneous.
- Similar dialogue or scenery alone does not establish simultaneity.
- Earlier setup and later reactions are separate events with their own clocks, connected through `related_events`, not extra simultaneous views. Do not stack them as if simultaneous.
- Distinguish observed footage from suggested editorial use. Recommend a replacement view only for a concrete reason, such as an action that is obscured in the main view.

Field formats are in [events](events.md). Timeline placement of alternates uses the same verified anchors; see [timeline](timeline.md).
