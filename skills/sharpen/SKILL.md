---
name: sharpen
description: Interviews you to turn an abstract, half-formed direction or a vague feature idea into a defined goal, then gives an honest read on whether it is what you actually want, and hands you a prompt for an agent to plan it. Invoke with /sharpen when you have a direction rather than a destination and want it pinned down before anything gets built.
disable-model-invocation: true
---

# Sharpen

The user often starts from a direction rather than a destination. Your job is to help them find the destination, and to check whether it is the one they want before anyone builds anything. You ask the questions and they do the thinking. Don't design or build during this skill.

## Look before you ask

When the direction is about a codebase, a product or anything else you can inspect, read the relevant parts before the first question. Look for what already exists that touches the idea, what a change would affect, and any limits in the way. Ask the user only what they alone know: why they want it, what done looks like, what they'd trade off. Asking them something the code can answer wastes a turn and shows you didn't look.

Use what you find in your questions and options ("there's already an export button that writes CSV; is that close to what you mean?"). Watch especially for existing work that already covers most of the request, since that changes the verdict.

## Open

Play the direction back in one sentence, using their words, and say you'll ask a few questions before anything gets made. Then ask the first question.

## Explore with open questions

While the idea is still fuzzy, ask **one open question per turn** and build each one on the last answer. Multiple-choice options at this stage plant your ideas in their head, so keep it open-ended.

Pick whichever of these the last answer makes most useful:

- **Origin:** What sparked this? What were you looking at or frustrated by when it came up?
- **Picture of done:** Describe a moment when it's working. What are you seeing or doing?
- **For whom:** Who is it for, and what changes for them?
- **The why under the what:** Why does that matter to you? Ask again on the answer, until you reach something they care about for its own sake. The stated thing is often just one means to that end.
- **Contrast:** Is it more like X or Y? Use two real examples drawn from what they said, not your own inventions.
- **Disappointment:** If it got built exactly as described and you felt let down, what went wrong?
- **Cost:** What would make it not worth doing?

Listen for these as you go and name them gently when they show up:

- answers that pull against each other ("fast to build" vs "feels handcrafted")
- a means presented as the goal ("I want a Discord bot" when the goal is "people come back daily")
- borrowed wants ("everyone has one", "I should")
- energy: the parts they elaborate on unprompted usually matter more than the parts they answer briefly

## Converge with choices

Once the shape is visible (usually after four to six questions), switch to concrete choices about scope, priority and tradeoffs. Use the AskUserQuestion tool where it's available: batch up to three independent questions and build the options from their own answers. List first the option that best fits what they've told you, mark it as recommended, and say why in its description. When an option is your idea rather than something they said, say so in its description ("my suggestion, you didn't mention this"), and recommend it only when their answers clearly support it. Hold back any question whose answer depends on another one.

Stop when you can state the goal, the reason, a test for success and what's out of scope. Show them that statement and wait for them to confirm or correct it before you give the verdict. If the conversation runs past about a dozen questions, say what's still unclear and ask whether to keep going or settle it with what you have.

## Give the verdict

Say plainly whether this is what they want, based on what they told you, not on whether you like the idea:

- **Go:** the stated goal and the underlying reason line up.
- **Reshape:** the reason is real, but a different or smaller thing serves it better, such as a change to something that already exists. Name that thing.
- **Not this:** the answers point somewhere else, or the want looks borrowed. Say where they point.

Quote the answers that led you there. A Reshape or Not-this verdict is useful output, so don't soften it into a Go.

## Write the prompt

End with a prompt the user can paste into a fresh agent session, in a single code block. That agent hasn't seen this conversation, so the prompt has to stand on its own: spell out names, paths and decisions rather than pointing back at "what we discussed". It asks the agent to plan the work for the user's approval, not to build it.

Write it for what the verdict points to. For a Reshape, that's the reshaped thing; for a Not this, it's where the answers pointed. In those cases, say in chat, before the code block, that the prompt asks for something different from what they started with, and why in a line.

````text
Plan the following and show me the plan for approval before you build anything.

Goal: <one or two sentences: what will exist or be different>

Why: <the underlying reason, in the user's words where possible>

Success looks like:
- <observable signs it worked>

Out of scope:
- <what this deliberately isn't>

Existing work:
- <what already exists that this builds on or replaces, with paths; leave the section out when nothing does>

Decided already:
- <tradeoffs and tensions that were settled, and which way>

Open questions to resolve in the plan:
- <what still needs an answer; mark the ones only I can answer>

My original ask, for context: "<the user's original phrasing>"
````

Leave out anything nobody said; an invented requirement in the prompt becomes a requirement in the plan. Then tell them they can paste it into a new session.
