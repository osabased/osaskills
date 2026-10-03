---
name: motion-studies
description: "Preview unresolved motion choices in the target application when user feedback or avoided production rework justifies a study. Skip routine, specified, or accepted motion."
---

# Motion Studies

Resolve meaningful motion choices through rough playback while changes are cheap, then carry the accepted movement into production.

## Decide whether a study earns its cost

Create a study when the user requests one. Otherwise, use one only when both conditions hold:

- Playback can resolve a meaningful uncertainty about motion feel, direction, or interaction.
- The expected benefit of early feedback outweighs the work of building the preview and obtaining review. Consider how costly the wrong choice would be to revise after production.

Before adding a checkpoint, identify the motion decision and why reviewing it early is worthwhile. Minor unspecified details alone are insufficient. Implement established patterns, fully specified or already accepted motion, and repairs that preserve intended movement directly. For a small animation that is cheap to adjust in place, direct implementation and normal playback verification may be the smallest useful approach.

Honor explicit instructions to skip studies or proceed straight to production. Existing acceptance carries through visual refinement and reuse. These criteria apply across animation domains, including motion proposed within a larger task.

When warranted, start the study without asking permission to create it. Infer the target application, movement, and trigger from the conversation and project; choose reasonable, reversible timing defaults. Ask only for missing information that materially affects the preview.

## Build the smallest useful preview

Use primitive shapes, spatial landmarks, or a proxy rig with just enough context to judge the decision. Preserve relevant scale, layout, pivots, contacts, camera framing, and relationships between moving parts. Keep the timing, spacing, path, easing, sequencing, and requested anticipation or settling visible.

Build in the intended application and runtime. Reuse an existing preview scene, story, timeline, or feature when practical; otherwise add a small, reversible entry point. Keep setup proportionate to the decision and stop once the movement is reviewable. Add artwork, effects, or production architecture only if needed to judge it.

Prefer motion code, clips, or parameters that can carry into production when this reduces total work. Keep placeholders and preview controls separable from the movement being reviewed.

Default to one faithful interpretation. Compare variants only when materially different choices need judgment; keep their context consistent and vary the main motion choice.

## Observe playback

Use the intended interaction and make the starting state, action, and ending state readable. Support repeat playback and any return interaction that belongs to the behavior. Add pause, scrubbing, or speed controls only when needed for judgment or requested.

Run the study at normal speed, observe a complete cycle, and repeat it. For direct manipulation, observe response during input and settling on release. Claim playback verification only from an observed runtime session; source code and screenshots provide supporting evidence.

If native playback or viewing tools are unavailable, preserve the runnable study, report what remains unverified, and request the specific missing access or user action. Continue independent authorized work. A substitute animation or exported video requires explicit user acceptance of that preview format.

## Review and carry the movement forward

Show or open the preview. Briefly state the interpretation and significant assumptions, explain how to repeat it, and request focused feedback on the decision: for example, weight, responsiveness, pace, path, or sequencing.

For motion selected for a study, wait for acceptance before developing that motion in production. A surrounding feature request, silence, or elapsed time does not approve it; unrelated authorized work may continue. During review, requests such as "slower" or "less bounce" revise the same study and require another showing unless the user also accepts the adjusted direction or asks to implement it.

Once the direction is accepted and production work is authorized, reuse the approved motion code, clips, or parameter values where practical. Preserve timing and movement relationships as placeholders become finished visuals, and check the resulting motion in the target runtime. Remove disposable preview scaffolding when no longer needed.

Reopen review only when a new meaningful motion choice meets the study criteria above. Acceptance covers the reviewed movement, not unrelated implementation work.
