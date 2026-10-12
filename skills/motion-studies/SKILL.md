---
name: motion-studies
description: Builds a rough, replayable preview of an unresolved animation or motion choice (UI transitions, easing and timing, camera moves, character or object movement) inside the real target app or engine, such as a web app or Roblox Studio, so the user can judge and accept it before production work. Invoke with /motion-studies when you want to try out how something should move before it is built for real.
disable-model-invocation: true
---

# Motion Studies

Resolve a meaningful motion choice through rough playback, then carry the accepted movement into production.

## Decide whether a study is needed

The user invoked this skill, so build a study for the motion they named. If they point at motion that is already specified, previously accepted, or a routine pattern, say so and implement it directly instead. Honor "skip the study" or "just build it".

Before stopping for review, name the specific motion choice you want the user to judge. Once the user has accepted a motion, texture or styling changes and reuse don't need a new study; reopen only for a new motion choice.

Start within the task's authorization. Infer context, and put timing values in named constants or parameters so they are easy to change. Ask only for missing information that materially changes the preview.

## Build and observe

- Build the smallest useful preview in the intended app and runtime. Reuse an existing scene, story, or timeline where practical.
- Use placeholders, but keep the scale, pivots, contacts, camera, timing, and relationships needed to judge the movement. Keep preview controls separate from the reusable motion code or parameters.
- Start with one faithful interpretation. Add variants only when different choices need comparing, with everything else held constant.
- Show a readable start state, action, and end state. Support repeat playback and relevant return interactions; add scrubbing or speed controls when judgment needs them.
- Observe a full cycle at normal speed, twice. For direct manipulation, check both the response during input and the settling after release.

To observe, use whatever runtime access you have (for example browser or screen tools capturing frames across the cycle). Stills or sampled frames don't verify timing or easing: say so and ask the user to watch it. Claim playback is verified only after observing the intended runtime. If you can't, keep the runnable study, name the unverified behavior and the access or user action needed, and continue other work. Get the user's OK before substituting an exported video or another preview format.

## Review and carry forward

Show the preview, explain how to replay it, and ask focused questions about the unresolved choice. A revision such as "slower" updates the study and needs another showing, unless the user also accepts it or asks for implementation.

Wait for explicit acceptance before building the motion in production; silence or a surrounding feature request is not acceptance. Unrelated authorized work can continue meanwhile.

Once accepted and authorized, reuse the approved movement, replace placeholders, and check playback in the target runtime. Preserve timing and relationships, then remove the disposable preview scaffolding.

**Done when:** the accepted movement is in the requested deliverable, or the next review or access requirement is concrete and the runnable study is preserved.
