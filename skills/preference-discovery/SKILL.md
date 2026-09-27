---
name: preference-discovery
description: Help users discover and express unclear, hard-to-articulate, or evolving preferences that materially affect a task. Use focused questions, concrete contrasts, references, and small samples across creative work, experiences, and workflows. Skip discovery when applicable preferences are already clear; investigate factual uncertainty through evidence instead.
---

# Preference Discovery

Help the user **discover, articulate, and validate** the preferences needed for the current task without requiring specialist vocabulary or inventing preferences on their behalf. This includes visual design, writing, video editing, sound, interaction and game feel, workflow behavior, and user-owned tradeoffs.

The user supplies reactions and makes or delegates subjective choices. You supply useful examples, vocabulary, interpretation, and appropriate tests. Treat statements such as "this feels cheap," "too corporate," "I want it heavier," or "the agent interrupts too often" as starting evidence, not insufficient input.

The guidance below is conditional, not a mandatory sequence. Use only what changes the next authorized action; a clear request may need no discovery at all.

## Start with the actual uncertainty

Reuse applicable preferences and constraints already established in the conversation or project. Preserve explicit priorities. If direction is clear, implement or validate within the user's authorization instead of interviewing them again. If an existing result is close, investigate only what feels wrong.

Distinguish these only when the difference affects the action:

- **Preference:** a desired quality or tradeoff, such as direct rather than conversational instructions.
- **Goal:** the outcome the work must achieve, such as helping a beginner complete a task.
- **Constraint:** a boundary, such as a word limit, budget, accessibility requirement, or mandated tool.
- **Delegation:** permission to choose within a scope. It allows a choice; it does not establish that the user prefers the selected result.
- **Indifference:** the user says the relevant alternatives are acceptable. Stop exploring that distinction; "I don't know yet" is not indifference or consent.

Resolve technical, factual, and project-state unknowns through the appropriate evidence route, not taste questions. Explain relevant feasibility or outcome tradeoffs without presenting expert advice as evidence of the user's preference. Keep the user's taste separate from an audience's needs or demonstrated effectiveness; clarify whose preference matters only when consequentially unclear.

This skill establishes user-owned inputs. `direction-selection` compares solutions against established objectives, constraints, and preferences when a consequential direction comparison is actually needed. Do not invoke both skills automatically, take over the surrounding workflow, or treat benchmarks as proof of what the user wants.

## Choose the smallest useful discovery method

Resolve the highest-impact preference uncertainty first. Ask a focused question when words suffice. When they do not, offer something concrete to react to rather than asking "What style do you want?" or requesting a complete specification.

| Uncertainty | Possible small test |
|---|---|
| Writing sounds too formal | Two short rewrites of the same passage. |
| Video pacing feels wrong | Two treatments of the same short segment. |
| Sound feels too sharp | Available audio examples or short variants with different attacks. |
| An interaction lacks weight | A small playable comparison, not a complete system. |
| An agent interrupts too often | Concrete scenarios with different approval behavior. |
| Visual intent is hard to describe | A small reference set or representative mockups. |
| A tradeoff is unclear | A concrete choice showing the benefit and sacrifice. |

These are examples, not domain checklists or requirements to create multiple variants. Select methods the environment supports and keep work within existing authorization.

### Make comparisons informative

Prefer a small contrast, often two options, over a long menu. Describe differences neutrally and concretely; avoid labels that make one choice sound inherently superior. Do not frame compatible qualities, such as utilitarian and polished, as mutually exclusive.

When diagnosing a known dimension, keep unrelated content and properties reasonably consistent. When the overall direction is unknown, broader bundled alternatives can be useful. A bundle selection supports that overall choice in context; it does not independently establish approval of every attribute. Explore properties separately only when doing so could change the next action.

Allow low-effort reactions: "left is closer," "between these," "keep the pacing but not the captions," "neither," "both are fine," or "use your judgment." The user need not learn terminology or choose one complete reference. Repeated rejection is a reason to reconsider the alternatives or framing, not endlessly refine the same set.

Treat relative feedback such as "closer" or "better" as evidence about the comparison, not automatically as satisfaction or authorization to finalize. Use it to guide the next refinement. Resolve acceptability only when the next commitment depends on it; an explicit instruction such as "use B" is sufficient within its stated scope and needs no redundant confirmation.

### Use references selectively

Use existing examples when they can resolve ambiguity more cheaply than new work. Search by the specific property at issue, such as composition, rhythm, voice, or feedback behavior, rather than vague aesthetic phrases. Show only a small useful set and explain what each reference helps decide. Ask what to take or reject, not which entire example to copy.

Different references may supply different properties. Distinguish what the user endorsed from incidental properties, defaults, and your proposed refinements. Negative feedback may narrow a direction more clearly than positive adjectives, but a dislike is not automatically a universal prohibition.

## Interpret without overclaiming

Use **reaction → tentative interpretation → useful question or sample → supported decision** when ambiguity could materially change the next action. This is not an extra confirmation loop for explicit instructions such as "remove the jokes; keep everything else."

Separate what the user said from what you infer. State a hypothesis plainly and test only the consequential ambiguity. Do not translate one vague reaction into several settled preferences.

Example:

> User: "This sounds too corporate: Our solution empowers teams to leverage actionable insights. The report lists delayed orders and their owners."
>
> Interpretation and sample: "The vague benefit claim may be the problem. A first revision keeps the concrete information: ‘The report lists delayed orders and their owners.’ Does removing the claim address what bothered you?"
>
> Keep formality and friendliness open unless the reaction makes them relevant. This sample tests removing the vague claim while preserving the factual wording.
>
> Not established: a preference for humor, first-person writing, or casual language in every context.

## Keep material interpretations visible

Before acting on newly inferred material preferences, surface a compact **Interpretation** in user-visible prose, not only in private reasoning, tool output, or project files. State what you think the user wants, the reaction or reference property supporting it, and the concrete consequence. Include remaining material uncertainty and the first test only when useful. A sentence can be enough; headings and a full template are optional.

For example:

> "You liked the split layout and tighter item spacing, but rejected the rounded cards. I propose a compact inventory grid with secondary details. Panel width is still uncertain; the first test will compare widths while preserving the item treatment."

Use the task's existing authorization for routine, reversible implementation choices. For example, a request to improve a paragraph permits a concrete rewrite, and a request to adjust spacing permits a local spacing change without asking for every value. Such choices remain your implementation judgment until the user endorses them.

Pause for input when an unresolved preference would change the intended outcome or commit substantial work that would be costly to redo, unless the user has delegated that choice. For example, settle an uncertain visual direction before applying it across an entire product. Judge the commitment by its cost, side effects, and downstream reliance; reversibility alone does not make extensive work cheap. Continue independent authorized work while waiting. Explicit choices and corrections need no redundant confirmation.

### Experiments are not commitments

Within existing authorization, use small disposable samples to investigate an unresolved preference. Surface the hypothesis being tested without first demanding approval of the preference the sample is meant to discover. Such a sample may be text, code, a mockup, media, or a scenario; writing code is not itself the commitment boundary.

Keep real cost, side effects, persistence, and downstream reliance bounded. A "prototype" label does not authorize paid generation, production-file changes, publication, or extensive implementation. If the scope does not permit the needed experiment, use a supported lower-cost method or request the specific authorization needed.

Do not propagate an exploratory choice into consequential dependent work merely because the sample exists. Approval of an experiment is not approval of its outcome. Apply established or explicitly delegated choices within their authorized scope; leave untested material properties provisional.

## Validate through the relevant experience

Use evidence that exposes the property being judged. A screenshot can support composition judgments, not responsive feel. A storyboard can communicate an editing idea, not establish experienced pacing. A written description of sound is not a listening test.

Render, run, play, or otherwise expose the relevant sample when the environment and authorization permit it. Show the user the artifact you inspected when possible. Compare against the surfaced interpretation, selected reference properties, and applicable project precedent. Ask the smallest useful reaction question; do not require a formal critique or repeatedly ask about properties already resolved.

Keep three things distinct: your inspection, the user's approval of the description, and the user's reaction to the experienced sample. Technical correctness alone does not establish subjective fit. State unavailable playback, rendering, interaction, or user feedback as limits on validation rather than substituting your confidence for evidence. Continue work those limits do not affect; do not claim validation of the missing property.

## Correct and reuse with scope

When a result is partly right, preserve successful decisions and make targeted deltas. For example: "Reduce the details-panel width and give that space to the grid; preserve typography and item treatment." If feedback changes a material interpretation, surface the revised interpretation before adopting it. An explicit correction does not need another approval round.

Retain only what future work needs: what is established, what supports it, and where it applies. Distinguish confirmed feedback, tentative inference, and delegated choices in ordinary language, using existing conversation or project notes when persistence is warranted. Do not require a new profile database, numerical confidence scores, or a record for every reaction.

"For this tutorial, the user preferred direct instructions; humor is unspecified" is different from "the user dislikes conversational writing." Preserve explicitly broad preferences at their stated scope. Do not silently globalize local feedback or unnecessarily narrow a broad instruction. When feedback changes, update the affected preference and known dependent choices; preserve unaffected decisions. Clarify conflicts only when they change the next action rather than making the user defend an evolving preference.

## UI and motion reference

When discovery needs UI references, visual vocabulary, or a representative interaction test, read [UI and motion guidance](references/ui-and-motion.md).

## Stop at the next supported action

Finish discovery when the next authorized action is supported by established preferences, delegation, indifference, or routine implementation judgment within the requested scope. Distinguish the last three from evidence of what the user likes. Keep unresolved properties provisional and say what they prevent when that matters. Supporting an exploratory sample is not validating the eventual direction; experienced feel may still require a later test.

Return the useful preferences, boundaries, and remaining material uncertainty to the caller or continue the already-authorized task. No fixed output schema or complete artifact is required. Do not resolve unrelated future preferences, claim the entire result is validated, or end the larger task merely because this discovery step is complete.
