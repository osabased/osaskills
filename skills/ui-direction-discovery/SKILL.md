---
name: ui-direction-discovery
description: Guide the user from vague visual instinct to explicit, testable UI direction. Use targeted contrasts, references, simple reactions, interpretation checkpoints, and rendered feedback to help the user discover and express what they want without requiring design vocabulary.
---

# UI Direction Discovery

Use this skill when the user has incomplete, hard-to-express, or evolving visual intent; when references or comparisons would help them discover what they prefer; or when an implemented UI does not feel right but the user cannot yet explain why.

The goal is not to design autonomously around vague input. The goal is to help the user **discover, articulate, and validate** a direction that the model can implement.

The user supplies taste, instinct, and reactions. You supply useful contrasts, vocabulary, decomposition, implementation, and visual verification.

## Core behavior

Do not require the user to arrive with a design specification or design vocabulary.

Treat statements such as:

- "I don't know exactly what I want"
- "this feels too bubbly"
- "I want it heavier"
- "I like this but not all of it"
- "this looks cheap"
- "I want a unique interaction"

as starting evidence, not insufficient input.

Guide the user toward clearer preferences, then translate those preferences using:

**reaction → observation → design decision**

Example:

> Reaction: "It feels like a mobile app."
>
> Observation: large rounded cards, oversized controls, generous spacing, pill-shaped actions.
>
> Decision: increase density, reduce radii and control height, remove unnecessary card containers, and subordinate secondary actions.

Do not silently turn an ambiguous reaction into a design choice.

## Choose the smallest useful discovery path

First determine what is actually uncertain.

- If the direction is already explicit, do not force discovery. Implement or validate it.
- If one dimension is uncertain, explore only that dimension.
- If several dimensions are uncertain, resolve the highest-impact one first.
- If the user cannot describe a preference, give them concrete contrasts or references to react to.
- If an existing implementation is close, preserve successful decisions and investigate only what feels wrong.

Avoid turning the skill into a questionnaire. Ask only questions that meaningfully reduce design uncertainty.

## Guide discovery through contrasts

When the user does not know what they want, do not ask broad questions such as "What style do you want?"

Instead, make the uncertainty easier to judge by presenting a small contrast.

Examples:

- dense vs sparse
- sharp vs soft
- flat vs layered
- restrained vs decorative
- asymmetric vs centered
- borderless vs heavily framed
- utilitarian vs polished
- immediate vs weighty motion
- fixed-duration motion vs spring-like motion

Prefer 2–4 meaningfully different options rather than a long menu.

Explain each option in concrete visual terms. The user should be able to answer with low-effort reactions such as:

- "left is closer"
- "between 1 and 3"
- "I like 2 except the rounded cards"
- "none of these, but 4 has the right weight"

If the user gives a vague reaction, translate it and continue from the new evidence. Do not make them learn terminology before progress can continue.

## Use references when words are insufficient

When visual examples would reduce ambiguity, search by **specific UI concern**, not vague aesthetic phrases.

Useful concerns include:

- composition and layout
- hierarchy
- density
- typography
- geometry
- containers and separators
- color treatment
- depth
- item presentation
- navigation
- interaction behavior
- motion

Prefer queries shaped like:

`[UI object] + [context] + [specific characteristic]`

Examples:

- `RPG inventory equipment layout`
- `dense survival game inventory`
- `character select large portrait RPG`
- `radial weapon selector game UI`
- `drag equip inventory interaction`

For static appearance, prefer screenshots and shipped interfaces.
For motion or unusual interactions, prefer video, GIF, or interactive examples.

Do not search for one perfect reference. Different references may supply different properties.

## Present references as decisions, not inspiration dumps

Show only a small, meaningfully different set. Usually 3–6 references is enough.

For each reference, state what it is useful for in one short line, such as:

- stronger central composition
- much denser information presentation
- sharper geometry with fewer containers
- more restrained typography
- heavier motion with less bounce

Ask what the user wants to **take from** or **reject from** each reference.

The user should not need to choose one complete design. They may combine properties from several references.

## Surface the interpretation before implementation

This is a required user-visible checkpoint, not private reasoning.

Before implementing newly inferred visual direction, show a compact **Interpretation** of what you believe the user wants.

Include only the dimensions that materially affect the current task:

- **What I think you want** — the direction in plain language.
- **Why I think that** — the reactions, contrasts, or reference properties that support it.
- **Concrete decisions** — the resulting layout, hierarchy, density, geometry, styling, interaction, or motion choices.
- **Still uncertain** — only material ambiguity that could change the result. Omit when none remains.
- **First test** — the smallest screen, component, or interaction that can validate the interpretation.

Example:

```text
Interpretation

What I think you want
- A dense, utilitarian inventory where the items dominate and the surrounding UI recedes.

Why I think that
- You preferred the split layout in Reference 2.
- You liked Reference 3's tighter item spacing.
- You rejected Reference 1's repeated rounded cards.

Concrete decisions
- Asymmetric split layout.
- Compact item grid with nearly square geometry.
- Separators and continuous surfaces instead of nested cards.
- Selected-item details remain visually secondary.

First test
- Build only the inventory grid + selected-item panel and render it for review.
```

Do not hide this translation inside chain-of-thought, scratch work, planning, or tool output.

If the interpretation contains a material choice the user has not established, pause at this checkpoint so they can correct it before that choice becomes code. Do not require redundant confirmation for choices the user already made or explicitly delegated.

## Derive only what the evidence supports

Use the user's reactions to form a compact design direction. Do not fill gaps with arbitrary taste when the missing choice materially affects the result.

Possible dimensions:

- **Composition** — centered, asymmetric, split-pane, grid, anchored, full-bleed
- **Hierarchy** — dominant element, secondary information, visual weight
- **Density** — compact, dense, sparse, breathable, information-heavy
- **Spacing** — tight, loose, grouped, uniform
- **Typography** — restrained, condensed, bold, muted, uppercase, numeric emphasis
- **Geometry** — sharp, soft, rounded, angular, pill-shaped
- **Containers** — card-based, borderless, divided, nested, framed
- **Depth** — flat, layered, elevated, inset, translucent
- **Color** — muted, saturated, monochrome, accent-driven, low-contrast
- **Interaction** — hover, selected, active, drag, snap, threshold, cancel behavior
- **Motion** — origin, trajectory, timing, easing, spring, inertia, overshoot, stagger, morph, continuity

State negative constraints when they narrow the direction more reliably than positive adjectives.

## Help with hard-to-describe motion and interactions

When motion is difficult to describe, convert it into states over time:

**trigger → immediate response → transition → intermediate behavior → resting state**

Example:

```text
Pointer down
→ item lifts slightly
→ item follows pointer with light inertia
→ compatible target reacts within attraction range
→ release on valid target snaps item into place
→ slight overshoot
→ settle
```

For unique interactions, expose meaningful alternatives when the user is unsure. For example:

- direct pointer tracking vs slight trailing inertia
- hard snap vs magnetic attraction
- simple fade/scale vs shared-element morph
- no overshoot vs restrained settle vs elastic bounce

Also capture, when relevant:

- trigger
- origin
- trajectory
- timing
- easing or spring behavior
- threshold
- interruptibility
- cancel behavior
- valid and invalid outcomes

Use physical descriptions when they communicate intent better than technical terms: weight, resistance, attraction, elasticity, momentum, settling.

## Prototype to help the user discover, not just to implement

When references and words are no longer enough, build the smallest visual test that can answer the unresolved question.

A rough prototype is part of discovery when the user needs to **see or feel** an option before deciding.

Prefer:

- one representative screen over the whole UI
- one interaction prototype over the complete system
- placeholder content when polish would distract from the decision
- side-by-side variants only when the comparison itself is useful

Do not prematurely build a design system around an unvalidated direction.

## Render, show, and ask for reaction

A UI task is not validated because the code is correct.

Render or run the implementation whenever the environment permits it. Surface the result to the user when possible so they can react to the same artifact you inspected.

Compare it against:

- the surfaced interpretation
- selected reference properties
- established project UI
- the intended hierarchy and interaction behavior

Inspect at least the dimensions relevant to the task:

- hierarchy
- proportions
- alignment
- spacing
- density
- typography
- geometry
- contrast
- consistency
- interaction states
- motion behavior

Then ask for simple reactions rather than a formal critique. Examples:

- "Is this too dense, too sparse, or close?"
- "Does the motion feel too light, too bouncy, or about right?"
- "Is the item grid now the thing your eye goes to first?"

Ask only the smallest useful question for the remaining uncertainty.

## Correct with deltas

If the result is partly correct, preserve what works.

Prefer targeted changes such as:

> Reduce the details panel width by about 20% and give that space to the inventory grid. Preserve the current typography and item treatment.

Use comparative language where useful:

- more / less prominent
- tighter / looser
- heavier / lighter
- sharper / softer
- denser / sparser
- faster / slower
- more / less bounce

Do not restart the design because one dimension is wrong.

If new feedback materially changes the inferred direction, surface a revised **Interpretation** before applying that new direction.

## Lock successful patterns

Once a representative screen or interaction matches the user's intent, treat it as a visual precedent.

Extract only stable primitives that will help future work, such as:

- spacing scale
- radii
- typography hierarchy
- borders and separators
- button treatment
- item/card treatment
- hover/selected/disabled states
- animation characteristics

Future UI should reuse that visual grammar rather than repeatedly rediscovering established preferences.

## User-facing output discipline

Keep the discovery loop fast and scannable.

Prefer this sequence:

1. identify the highest-impact uncertainty
2. show a small contrast or reference set
3. collect a simple reaction
4. translate the reaction
5. surface the Interpretation checkpoint
6. build the smallest useful visual test
7. render and collect another simple reaction
8. make targeted corrections

Do not bury the user in design theory unless they ask for it.
Do not dump large reference boards without explaining the decision each reference helps with.
Do not ask the user to repeat preferences already established in the conversation or project.
Do not keep material interpretations private.

## Completion criteria

Stop when the requested UI or representative slice:

- reflects a direction the user has seen articulated,
- resolves the material visual uncertainties for the current task,
- has been visually inspected when possible,
- no longer has material mismatches with the user's expressed reactions,
- and establishes enough precedent for the next related UI task without unnecessary rediscovery.
