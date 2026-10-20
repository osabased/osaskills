---
name: think-tank
description: Put a question or task to a panel of three fresh, independent subagents, let them debate each other's answers, and synthesize where they agree and split.
argument-hint: "[model | m1,m2,m3] [effort] [--lenses[=a,b,c]] [--quick] [question]"
disable-model-invocation: true
---

Convene a think tank: three fresh panelists who each judge the question on their own, then see each other's answers and revise. The panel's value is its independence, and most of what follows exists to protect it.

Arguments: $ARGUMENTS

## Read the arguments

- **Model**: `opus`, `sonnet`, `haiku` or `fable`, or a comma list such as `opus,sonnet,fable` that gives panelists A, B and C a model each. Different models share fewer blind spots, so a mixed panel's agreement means more. If the list doesn't name three, ask which three. The Agent tool takes only the family and runs its newest version, so ignore a version number written after one (`opus 5.5` means `opus`).
- **Effort**: `low`, `medium`, `high`, `xhigh` or `max`.
- **`--lenses`**: give each panelist a different angle. Plain `--lenses` means you pick three that fit the question; `--lenses=security,ux,cost` uses the named ones. If fewer than three are named, pick the rest; if more, ask which three.
- **`--quick`**: skip the debate round.
- Everything else is the question.

Only the leading words count as model and effort, so a question that mentions "haiku" or "max" stays intact. Flags can go anywhere. Without a model, use `opus,sonnet,sonnet`, a mixed panel that costs less than three Opus panelists. Without an effort, the panelists inherit the session's.

With no question, use what the conversation is currently about. With nothing to go on, ask what the panel should consider.

## Write the brief

The panelists have seen none of this conversation, so the brief has to stand on its own: the question, the context that bears on it (goals, constraints, what's been tried, relevant file paths and why they matter), and what a useful answer looks like. Point to files rather than pasting them, since panelists can read. Panelists start without any CLAUDE.md, so when one bears on the question, point to it too.

Leave out your own leaning and any hint of the answer you expect. A brief that tilts the panel makes its agreement worthless.

If the question is a task ("fix this bug", "write the intro"), the panel proposes how to do it, and any change gets made here afterwards, once the user has seen the synthesis.

Show the brief before you launch. If you built it from the conversation rather than from a question the user typed, wait for a go-ahead, since a big panel is expensive to aim wrong. Otherwise launch in the same message.

## Round 1

Say in one line what you're launching, naming any lenses you picked and saying "session effort" if the panelists inherit it, e.g. "Convening opus, sonnet, sonnet panelists at session effort, identical brief, with debate." Under it, give your own leaning in a line, before any answer arrives, so "My take" can show whether the panel moved you.

Spawn three `osaskills:think-tank-member` agents, or `think-tank-member` if that is the name installed, in one message so they run in parallel, each with its model, the effort if given, and the descriptions "Panelist A", "Panelist B" and "Panelist C". Each gets the identical brief. With lenses, add one line to each: "Your lens: <lens>, meaning <what it covers for this question>."

If neither is installed, tell the user the panel needs the `think-tank-member` agent from osaskills and stop. Other agent types can change files and load CLAUDE.md, so they don't make independent panelists.

The answers may come back with the launch or later as notifications. Wait for all three before going on, and never start round 2 or the synthesis with one missing. Keep each agent's ID for round 2. If a panelist fails, spawn a fresh one with the same brief.

## Round 2: debate

Skip this with `--quick`, or when all three round-1 positions recommend the same thing and the answers aren't lists of points. The panelists stay reachable, so if the user asks for the debate afterwards, run it as below.

Models drift toward whichever answer reads most confidently, and panelists who converge that way look like a consensus without being one. So every change of mind has to be traceable to a specific argument.

Send each panelist the other two answers, labelled only by letter so no answer carries weight from the model that wrote it. Use SendMessage to its agent ID (load SendMessage with ToolSearch if it's deferred), sending all three in one message, each with this request:

> Here are the other two panelists' answers to the same question. Before your final answer, name the strongest point in them and either counter it or say you can't, and name the strongest point against your own answer. Where you disagree on a fact you can check, check it. Change your position only for an argument you hadn't already weighed or a fact you checked yourself, and say which one moved you. Otherwise keep your position and say why it holds. Then give your final answer in the same format as before.

The replies arrive in the background, so wait for all three before writing the synthesis. If a panelist can't be reached, spawn a fresh one with the brief, its own round-1 answer and the other two.

## Synthesis

Before writing, check the one or two facts the recommendation rests on, even at 3–0, starting with the ones the panelists said their positions depend on. Three panelists reading one brief can share a wrong premise, and a 3–0 is where it hides.

Report back in this shape, leaving out any section or note that would be empty:

```
## Think tank: <question in a few words>
<3 × model, or each panelist's model if mixed> · <effort> · <identical brief | lenses: a, b, c> · <debate | quick | debate skipped at 3–0>

### Recommendation (<3–0 | 2–1 | no consensus>; <round-1 tally> before debate, if different)
<the majority's final position and the reasons they share; with no consensus, what the call turns on>
Checked: <each fact it rests on, and what you found>

### Panel
- **A** (<its model if the panel is mixed; its lens if any>): "<its final Position line, verbatim>" <Its confidence.> <If it moved in debate: what moved it.>
- **B** …
- **C** …

### Where they split
<the crux of each disagreement, and what evidence would settle it; where that is a fact you can check, check it and say what you found>

### My take
<your own view, drawing on what you know from this conversation, whether the panel moved you from the leaning you gave at launch, and where and why you differ from the panel>
```

Write "session effort" if the panelists inherited it. When a 2–1 majority is two panelists on the same model and the dissent is on another, say so in the tally, e.g. (2–1, both sonnet), since a model agreeing with itself is weaker agreement. Quote each Position line exactly, since a paraphrase is where your own view slips in. When the answers are lists of points, tag each point with the panelists who raised it in round 1 and any who adopted it in debate, e.g. (B, C → A). Take the round-1 tally and the tags from the round-1 answers you hold, not from what panelists say about themselves in round 2.

Keep your own view out of the Recommendation and in "My take", so the user can tell the independent judgement from yours. If a check contradicts the panel, say so on the Checked line, and leave what follows from it to "My take".

Hold on to the brief and both rounds' answers. If the user asks to see one, show it verbatim.
