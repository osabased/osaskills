---
name: think-tank-solo
description: Put a question or task to one fresh, independent subagent, check the facts its answer rests on, and report. The think-tank flow with one panelist and no debate, for this eval only.
argument-hint: "[model] [effort] [question]"
disable-model-invocation: true
---

Put the question to one fresh panelist who judges it on its own, then check its answer and report. The panelist's value is its independence, and most of what follows exists to protect it.

Arguments: $ARGUMENTS

## Read the arguments

- **Model**: `opus`, `sonnet`, `haiku` or `fable`. The Agent tool takes only the family and runs its newest version, so ignore a version number written after one (`opus 5.5` means `opus`).
- **Effort**: `low`, `medium`, `high`, `xhigh` or `max`.
- Everything else is the question.

Only the leading words count as model and effort, so a question that mentions "haiku" or "max" stays intact. Without a model, use `opus`. Without an effort, the panelist inherits the session's.

With no question, use what the conversation is currently about. With nothing to go on, ask what the panelist should consider.

## Write the brief

The panelist has seen none of this conversation, so the brief has to stand on its own: the question, the context that bears on it (goals, constraints, what's been tried, relevant file paths and why they matter), and what a useful answer looks like. Point to files rather than pasting them, since the panelist can read. The panelist starts without any CLAUDE.md, so when one bears on the question, point to it too.

Leave out your own leaning and any hint of the answer you expect. A brief that tilts the panelist makes its judgement worthless.

If the question is a task ("fix this bug", "write the intro"), the panelist proposes how to do it, and any change gets made here afterwards, once the user has seen the report.

Show the brief before you launch. If you built it from the conversation rather than from a question the user typed, wait for a go-ahead. Otherwise launch in the same message.

## Launch

Say in one line what you're launching, saying "session effort" if the panelist inherits it, e.g. "Asking one opus panelist at session effort." Under it, give your own leaning in a line, before the answer arrives, so "My take" can show whether the panelist moved you.

Spawn one `osaskills:think-tank-member` agent, or `think-tank-member` if that is the name installed, with its model, the effort if given, and the description "Panelist A".

If neither is installed, tell the user this needs the `think-tank-member` agent from osaskills and stop. Other agent types can change files and load CLAUDE.md, so they don't make an independent panelist.

The answer may come back with the launch or later as a notification. Wait for it before going on. If the panelist fails, spawn a fresh one with the same brief.

## Report

Before writing, check the one or two facts the recommendation rests on, starting with the ones the panelist said its position depends on. A panelist reading one brief can hold a wrong premise with high confidence.

Report back in this shape, leaving out any section or note that would be empty:

```
## Think tank (solo): <question in a few words>
<model> · <effort> · one panelist

### Recommendation
<the panelist's final position and its reasons>
Checked: <each fact it rests on, and what you found>

### Panelist
"<its Position line, verbatim>" <Its confidence.>

### My take
<your own view, drawing on what you know from this conversation, whether the panelist moved you from the leaning you gave at launch, and where and why you differ from it>
```

Write "session effort" if the panelist inherited it. Quote the Position line exactly, since a paraphrase is where your own view slips in.

Keep your own view out of the Recommendation and in "My take", so the user can tell the independent judgement from yours. If a check contradicts the panelist, say so on the Checked line, and leave what follows from it to "My take".

Hold on to the brief and the answer. If the user asks to see one, show it verbatim.
