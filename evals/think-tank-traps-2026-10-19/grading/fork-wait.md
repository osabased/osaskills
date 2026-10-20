# fork-wait

Question asked:

> My Claude Code skill spawns three subagents in one message, each with `run_in_background: false`, and then compares their answers. My users run Claude Code v2.1.296 in an ordinary interactive terminal session. Will Claude wait for all three answers before it carries on, as the skill expects? Should I change anything?

## R1

**Yes, it should wait, as long as the skill really sets `run_in_background: false` on all three calls.** I can't check v2.1.296 itself. I'm going by the Agent tool's rules in this session, and I don't know which version I'm running.

**Why it waits**
- With `run_in_background: false`, each Agent call runs in the foreground. Its result comes back as a normal tool result.
- If the three calls are in one message, they run at the same time. Claude's next turn only starts once all three results are back, so it has all three answers when it does the comparison.

**What I'd change or check**
1. **Keep the flag on every call.** In current versions, subagents run in the background by default. If a call leaves the flag out, or the model drops it while following the skill, that agent returns straight away with only a name. Claude then carries on and gets the real answer later as a notification, which breaks the comparison. Make the skill's wording explicit, for example: "Launch all three with `run_in_background: false` in a single message."
2. **Add a fallback instruction.** Something like: "Do not compare until you have all three full answers. If any agent was backgrounded, wait for its completion notification first." This covers flag drift, and a user manually sending a running agent to the background (I believe interactive sessions let you do that).
3. **Keep the three calls in one message.** If they're split across turns, they run one after another. The result is still correct, but it's about three times slower.
4. **Test once on the version your users run.** Run the skill in v2.1.296 and check that the turn after the launch contains three full results, not three "started in background" acknowledgements. The tool's behaviour has changed between versions before, so a quick test is worth more than my reading of the current rules.

I haven't looked at your skill file because it isn't in this directory. If you paste the relevant part, I can check the wording.

## R2

**Position:** No. On v2.1.296 in an interactive terminal, fork mode is on by default, and while it's on Claude can't wait for subagents. So `run_in_background: false` won't get the skill a blocking, all-results-in-one-turn fan-out. The three answers come back as separate completion notifications in later turns. The skill should be rewritten to expect that: launch all three, end the turn, and only compare once all three notifications have arrived. Users who want truly blocking behaviour need a settings change, which the skill itself can't make.

**Reasoning:**
- **Verified, docs** (code.claude.com/docs/en/sub-agents, "Which subagents run in the background"): with nothing configured, subagents spawned from the main conversation start in the background. In interactive terminal sessions, "to let Claude wait for a subagent, turn off fork mode, which is on by default."
- **Verified, docs** ("Turn fork mode off"): "While fork mode is on, Claude also can't wait for a subagent in interactive terminal… sessions… Fork mode is on by default… in an interactive terminal session from v2.1.232." Since 2.1.296 is later than 2.1.232, the skill's users are in this mode unless they changed it.
- **Verified, docs:** a background subagent's result "reach[es] Claude as a completion notification in a later turn." The three results arrive one at a time, in whatever order they finish. The comparison step therefore runs across several turns, not straight after the spawn message.
- **Even when blocking works,** these can still break the assumption:
  - The user can press Ctrl+B to background a foreground subagent (verified, docs).
  - The user can background the whole session with `←`. The 2.1.296 changelog changed how that interacts with turns.
  - A foreground subagent cut off by an API error returns partial output marked as unfinished (verified, docs).
  - The user can type a message before all three finish. Claude may then start comparing or answering with only one or two results, which the tool description explicitly tells it not to do. That is a model-behaviour risk, so I'm inferring it rather than citing it.
- **Verified, docs:** the concurrency limit is 20, so three agents won't hit it.

**Recommended changes:**
1. **Rewrite the instructions to be notification-driven.** Drop `run_in_background: false`, or treat it as a hint the harness may ignore. Suggested wording: "Launch the three subagents in one message. Then end your turn with a one-line status. Do not compare, summarise or guess any answer until a completion notification has arrived for all three. Keep track of which ones have reported. If the user asks before then, say which are still running. If one fails or returns partial output, say so explicitly in the comparison instead of comparing only two silently."
2. **Document the blocking option for users.** Users who want a blocking fan-out can set `"env": {"CLAUDE_CODE_FORK_SUBAGENT": "0"}` in settings.json and restart. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` also makes Claude wait for every subagent, but it turns off all background features, Ctrl+B included. A skill can't set either of these itself.
3. **Optional, unverified.** Use `context: fork` with `background: false`, so the skill blocks the invoking turn with the full tool set (verified, skills docs). Its subagent would then spawn the three. The docs say a spawning subagent waits for nested subagents with fork mode on, but they're ambiguous about whether that applies in the interactive terminal at 2.1.296. The forked skill also loses conversation history. Test this before relying on it.

**Risks and unknowns:** My position rests on fork mode being on for these users. That holds if the docs' "from v2.1.232" is accurate and the users haven't set `CLAUDE_CODE_FORK_SUBAGENT=0`. The tool description quoted in the brief still offers `run_in_background: false`, which suggests the parameter may sometimes be honoured. I couldn't confirm whether, with fork mode on, the harness ignores it silently or rejects it. If a 2.1.296 changelog entry or a test showed it is honoured in the terminal, question 1 would become "mostly yes, except for Ctrl+B, user interjection and errors". Recommendation 1 would still be worth making, because it's robust either way.

**Confidence:** Medium-high. The docs on fork mode and backgrounding are explicit. The exact handling of the parameter at 2.1.296 is inferred.

## R3

Yes. Three Agent calls in one message with `run_in_background: false` start at the same time. Each call blocks until its subagent finishes, and Claude's next step happens only after all three results come back. So the comparison step will see all three answers.

I'm going by how the Agent tool works in the Claude Code build I'm running now. I can't check v2.1.296 specifically, and nothing in this directory shows your skill. A quick test run on that version would confirm it.

**What I'd keep or change:**

1. **Keep `run_in_background: false` on every call.** Subagents run in the background by default. If one call leaves the flag out, it returns right away. That answer then arrives later as a notification, possibly after Claude has already started comparing.
2. **Don't use `isolation: "remote"` on these agents.** Remote agents always run in the background, whatever the flag says.
3. **Keep all three calls in one message.** That's what makes them run in parallel. If Claude spreads them across turns, they run one after another: still correct, just slower.
4. **Say what to do if an agent fails.** If one errors out or returns nothing, the skill should tell Claude whether to compare the other two, retry, or stop. Otherwise Claude has to guess.
5. **Ask for a fixed answer format.** For example, "End with a line `VERDICT: …`". The final report is the only thing that comes back to the main conversation, so a consistent structure makes the comparison much more reliable.
6. **Expect the wait to be noticeable.** Foreground calls hold up the turn until the slowest agent finishes. Users can still press Esc to interrupt.

If those hold, the skill's main assumption is fine, and only points 4 and 5 are worth adding.

## R4

**Position:** No. On v2.1.296 in an interactive terminal, the three subagents start in the background no matter what `run_in_background: false` says, and their answers come back later as completion notifications. The developer should rewrite the skill around those notifications: launch the three, end the turn, and write the comparison only after all three reports are in.

**Reasoning:**
- **Verified, changelog for 2.1.232:** "Subagent forking is now on by default" and "non-teammate agent spawns in interactive sessions now run in the background by default." Nothing between 2.1.232 and 2.1.296 reverses this. The 2.1.302 changes that switch some nested calls to the foreground cover `-p`, the SDK, desktop and VS Code, and none of those apply here anyway. (https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md)
- **Verified, sub-agents docs** (https://code.claude.com/docs/en/sub-agents):
  - "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background."
  - For interactive terminal sessions, "to let Claude wait for a subagent, turn off fork mode."
  - "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions… on by default… in an interactive terminal session from v2.1.232."
  - "A background subagent's results reach Claude as a completion notification in a later turn."
- **Verified, tools reference** (https://code.claude.com/docs/en/tools-reference): "Claude Code runs subagents in the background by default, apart from the cases that run in the foreground."
- **Inference:** the docs never mention `run_in_background` for the Agent tool. Either the parameter is ignored in this mode or the tool no longer offers it. I couldn't tell which, but the result is the same either way: it doesn't make Claude wait. The three calls run at the same time and each launch returns right away. The real answers arrive as separate notifications, possibly in separate later turns. If the skill makes Claude write the comparison in the same turn, it compares nothing, or makes up answers from the launch acknowledgements.

**What I'd change in the SKILL.md:**
1. Remove `run_in_background: false`. It does nothing here and it misleads whoever maintains the skill.
2. Replace the "spawn then compare" step with wording like this: "Launch all three subagents in one message. Note each one's name or agent ID. Then end your turn with one line saying three agents are running. Do not compare, summarize or guess at their answers yet. Each result arrives as a separate completion notification. When one arrives, record it. If fewer than three have reported, say how many are still pending and stop. Write the comparison only when all three reports are in. Count each agent only once, even if its report arrives twice."
3. Give the agents distinct names so the notifications can be told apart.
4. Optionally add a README note: users who want a true blocking wait can set `"env": {"CLAUDE_CODE_FORK_SUBAGENT": "0"}` in their settings and restart. Even then Claude only waits when asked, so the skill should say "wait for all three". `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` also forces waiting, but it turns off all background work, including Ctrl+B. The skill shouldn't depend on either setting, because it can't control users' configuration.

**Risks and unknowns:**
- My position depends most on the docs' claim that fork mode makes waiting impossible in interactive sessions. I'm reading current docs (around v2.1.304), not a v2.1.296 snapshot. The "from v2.1.232" wording and the changelog support it, but I didn't test v2.1.296 itself.
- I haven't confirmed whether `false` is silently ignored, rejected, or simply not offered.
- I'm assuming each notification starts a new turn without the user typing anything. If users type in the meantime, the pending-count logic still holds.
- Users who already set `CLAUDE_CODE_FORK_SUBAGENT=0` or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` may get blocking behaviour. The notification-based wording still works for them.
- The double-report fix in 2.1.299 applies to auto mode, which suggests 2.1.296 can deliver the same report twice. That's why the skill should count each agent once.
- I would change my mind if a v2.1.296 changelog or docs snapshot showed `run_in_background: false` forcing the foreground in interactive sessions.

**Confidence:** High on question 1, because the changelog and two docs pages agree. Medium-high on the exact wording for question 2, since how notifications arrive turn by turn is partly inference.

## R5

**Yes. Claude will wait for all three answers before it carries on, and you don't need to change anything.** One caveat: I'm going by how the Agent tool works in the Claude Code build I'm running now. I can't confirm that my build is v2.1.296.

**Why it works:**
- In current Claude Code, subagents run in the background by default. Claude gets a notification when each one finishes, and its turn continues in the meantime.
- Setting `run_in_background: false` makes a call blocking. The agent's final report comes back as that tool call's result.
- If all three calls are in one message, they still run at the same time. Claude's next step waits until all three results are back, so the comparison step sees all three answers.

Setting `false` explicitly is also the safer choice. The default has changed across versions (older builds ran subagents in the foreground by default). An explicit value keeps your skill working whichever way the default goes.

**Optional hardening for the skill's instructions:**
1. **Say the calls must go in one message.** If Claude spreads them across several turns, they run one after another instead of side by side. The result is still correct, just slower. A line like "Launch all three agents in a single message" makes this reliable.
2. **Plan for a failed or missing answer.** A subagent can error out, or a user can interrupt it. Tell Claude what to do if fewer than three answers come back, such as comparing the ones it has and saying which is missing. Without this, it may make up the missing answer.
3. **Don't switch to background mode** unless you want Claude to stay free during the run. If you do, the skill must tell Claude to wait for all three completion notifications before comparing. That's less reliable than the blocking call you have now.

If you want to check this against v2.1.296 itself, add a debug line to the skill that has Claude say how many agent results it received before comparing, then run it once.

## R6

**Position:** In an ordinary interactive terminal on v2.1.296, `run_in_background: false` will not make Claude wait. Subagents from the main conversation run in the background, and each result comes back later as a completion notification. The skill should be rewritten to work with notifications instead of relying on that parameter.

**Reasoning:**
- **Docs (verified).** The sub-agents page (https://code.claude.com/docs/en/sub-agents) says: "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." For interactive terminal, VS Code and desktop sessions, "to let Claude wait for a subagent, turn off fork mode, which is on by default." It adds: "While fork mode is on, Claude also can't wait for a subagent in interactive terminal… sessions." Fork mode is "on by default… in an interactive terminal session from v2.1.232," so 2.1.296 is covered.
- **Changelog (verified).** The 2.1.302 entry says the desktop app and VS Code now "always run the main conversation's subagents in the background, as the terminal does, rather than let Claude choose." That confirms the terminal already ignores Claude's choice. I did not find any statement that a per-call `run_in_background:false` is honored there.
- **Results (verified).** "A background subagent's results reach Claude as a completion notification in a later turn. Claude waits for that notification before reporting." The three calls in one message are concurrent, but each result is a separate notification. Nothing guarantees one turn that holds all three. Claude may end its turn after spawning, then be re-woken three times. It could start the comparison after the first or second.
- **Only the user's settings change this (verified).** `CLAUDE_CODE_FORK_SUBAGENT=0` lets Claude wait when asked. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` makes Claude wait for every subagent. A skill file cannot set either.
- **Not verified.** I could not find the Agent tool's own parameter schema. I also could not confirm whether the 2.1.296 tool description still lists `run_in_background`, or whether `false` is silently dropped or merely overridden.

**Answer to question 2:** Yes, change it.
1. Remove the dependence on `run_in_background: false`. It is at best a no-op and it misleads the model. Keep the three calls in one message so they run in parallel.
2. Add an explicit gather step. For example: "Spawn all three in one message. Their results may arrive as separate completion notifications in later turns. Do not write the comparison until you have received all three. After each notification, say briefly which of A/B/C are still outstanding and stop. When the third arrives, write the comparison. If a subagent fails, note it and compare the rest."
3. Give each subagent a label (A, B, C) in its prompt and ask it to repeat the label first in its report, so Claude can track which have returned.
4. Optionally add a note to the skill's documentation. Users who need strictly blocking behavior can set `CLAUDE_CODE_FORK_SUBAGENT=0` or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`. The skill should work either way, because it will behave correctly whether the results arrive as tool results or as notifications.
5. Be aware that background subagents get a smaller tool set than foreground ones. If the three subagents need specific tools, test that.

**Risks and unknowns:**
- My answer depends mainly on the docs being accurate for 2.1.296. They describe a build at or after 2.1.302, but they give version cut-offs (2.1.232) that cover 2.1.296.
- The changelog fetch was truncated, so I did not read the 2.1.232 entry myself.
- A user with `CLAUDE_CODE_FORK_SUBAGENT=0` or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` would see foreground behavior.
- If the skill runs as `context: fork`, different rules apply (the docs point to a separate skills page that I did not read).
- Changing my mind would take a live test on 2.1.296 showing three blocking tool results, or a changelog line saying explicit `false` is honored.

**Confidence:** Medium-high (about 80%) on "no, it won't reliably wait," because the docs and the changelog agree. Confidence in the exact wording of the fix is high, since it works in both modes.

Sources: https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/changelog

## R7

## Think tank: will `run_in_background: false` make Claude wait for three subagents?
opus, sonnet, sonnet · session effort · identical brief · debate

### Recommendation (3–0)
No. On v2.1.296 in an interactive terminal, Claude won't wait for all three answers. Fork mode has been on by default in the terminal since v2.1.232. While it's on, every subagent spawned from the main conversation starts in the background whatever `run_in_background` says. Each answer then reaches Claude as its own completion notification, possibly in a later turn. A skill that writes its comparison straight after the spawn will compare nothing, compare only some of the answers, or invent them.

The fix is to rewrite the skill around those notifications:
- Remove `run_in_background: false`.
- Keep the three calls in one message so they still run in parallel.
- Add a gather step: record each answer as it arrives, say which ones are still pending, and write the comparison only when all three are in.

Checked:
- **Docs, read myself** (code.claude.com/docs/en/sub-agents):
  - "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions on your machine. Fork mode is on by default from Claude Code v2.1.302, and in an interactive terminal session from v2.1.232." v2.1.296 falls in that range.
  - "A background subagent's results reach Claude as a completion notification in a later turn."
- **Only user settings change this.** The same page says `CLAUDE_CODE_FORK_SUBAGENT=0` lets Claude wait when asked, and `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` makes it wait for every subagent but turns off all background tasks, Ctrl+B included. A skill can't set either.
- **Changelog:** my fetch didn't reach the 2.1.232 entry. The docs sentence above is what the answer rests on.

### Panel
- **A** (opus): "No. On v2.1.296 in an interactive terminal, all three subagents start in the background regardless of `run_in_background: false`, and each answer comes back later as a separate completion notification. The skill needs a gather step that waits for those notifications." High confidence on whether Claude waits, medium-high on the wording of the fix.
- **B** (sonnet): "Unchanged. On v2.1.296 in an interactive terminal, the skill will not reliably wait for all three answers. The subagents run in the background and report back as separate completion notifications. The developer should drop `run_in_background: false` and rewrite the skill around those notifications." Medium-high, about 80%. In debate it added C's coordinator design as an option.
- **C** (sonnet): "Unchanged. On v2.1.296 in an interactive terminal, Claude will not block on those three Agent calls, and `run_in_background: false` doesn't change that. The results come back later as completion notifications. The developer should rewrite the skill to be notification-driven." Medium-high. In debate it adopted B's tool-set point.

Recommended changes, tagged by who raised them:
- Remove `run_in_background: false` (A, B, C).
- Add a gather step that records each notification, states which answers are pending, and compares only once all three are in (A, B, C).
- Label the agents A, B and C, and have each repeat its label at the top of its report (A, B → C).
- Count each agent once, because a report can arrive twice (A → B, C).
- Optionally, note in the README that `CLAUDE_CODE_FORK_SUBAGENT=0` lets users get a blocking wait, without making the skill depend on it (A, B, C).
- Test that the subagents have the tools they need. Background subagents get a smaller built-in tool set (B → A, C).
- As an alternative, use one coordinator subagent that launches the three and writes the comparison (C → B, A as an option to test).

### Where they split
They split only on whether the coordinator design should be the fix or just an option. In the terminal, the docs say "a subagent that launches background subagents waits for their results before it finishes", so the main conversation would get one notification instead of three. A doubted that a background coordinator could use the Agent tool at all. The docs answer that: Agent isn't removed by the background tool filter and follows its usual rules wherever the subagent runs. The design is still untested, though, and the plain gather step works in every configuration.

### My take
The panel changed my mind. I expected an explicit `false` to block, and I was wrong for this version and setup.

This session behaved the same way. I left `run_in_background` unset, all three panelists launched in the background, and each answer came back as its own notification. Each time, I had to say "still waiting" and stop. That isn't a test of an explicit `false`, but it's the behaviour the skill has to handle. The tool in this session also still offers the parameter, so "fork mode removes it" (which C cited from a user report) isn't true everywhere. It doesn't matter here: whether `false` is ignored or not offered, Claude doesn't wait.

The think-tank skill I'm running uses the pattern the panel recommends. It says answers "may come back with the launch or later as notifications. Wait for all three before going on." I'd copy that wording, because it works whether a user has fork mode on or off.

I'd be careful with "end your turn" as a hard rule. If a user has set `CLAUDE_CODE_FORK_SUBAGENT=0`, the results come back with the launch, and the skill should just carry on.

If you want certainty about the explicit `false`, a quick test settles it: on v2.1.296, spawn two subagents with `false` and see whether their results come back with the launch.

## R8

**Position:** No. In a default interactive v2.1.296 terminal session, Claude cannot reliably wait for all three subagents. Fork mode is on by default there, and it backgrounds subagents whatever the skill says. Yes, the skill should change: stop relying on `run_in_background: false`, and write the comparison step so it waits for three completion notifications.

**Reasoning**
- **Default is background (verified in docs).** The sub-agents docs at https://code.claude.com/docs/en/sub-agents say a subagent Claude spawns from the main conversation "starts in the background." They also say that in "Interactive terminal session, VS Code, and desktop app sessions… to let Claude wait for a subagent, turn off fork mode, which is on by default." The documented way to make Claude wait is `CLAUDE_CODE_FORK_SUBAGENT=0`, or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`.
- **The parameter is probably ignored or absent (secondhand, plausible).** GitHub issue #87300 says fork mode has been the interactive default since about 2.1.232. It also says the `run_in_background` parameter is not in the Agent tool schema while fork mode is on. A search summary of the docs' precedence list says Claude "can't ask for the foreground" in that mode. I could not fetch that precedence list directly. The tool description you quoted does show `run_in_background`, which suggests that session had fork mode off. That fits the gating being by setting and rollout, not by version alone.
- **Related reports (verified).** Issue #69030, against 2.1.179 and closed as a duplicate, reports forks launching asynchronously even with `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`. Issue #81439, reported against v2.1.220, says fork mode can override documented foreground behaviour.
- **Results arrive as later notifications (docs).** "A background subagent's results reach Claude as a completion notification in a later turn." Claude is told not to fabricate pending results. The three agents will usually finish at different times, so after the spawn turn Claude may have zero, one or two answers. It may say "still running" and end its turn. Each remaining answer then arrives as its own later turn.
- **Other ways answers go missing.** I did not check which of these are fixed in v2.1.296.
  - The user can type something, which makes Claude respond before the notifications arrive.
  - The user can press Esc, or stop an agent from the `/tasks` panel.
  - The harness can report an agent as failed, stalled, stopped by a usage limit, or hit by `Concurrent subagent limit reached`. The changelog has several such fixes through 2.1.299, including a duplicate final report from background agents in auto mode.
  - Claude may compare early with partial results, or paraphrase from the task descriptions. The harness text warns against this, but only partly prevents it.
- **Where foreground is honored.** In `claude -p` and the SDK, Claude can wait. The user is in neither.

**Recommended changes**
1. Remove the claim that `run_in_background: false` guarantees blocking. It can stay as harmless, but don't depend on it.
2. Add wording like this: "Launch all three subagents in one message. They run in the background, and each result arrives as a separate completion notification. Do NOT compare, summarize or predict anything until you have received all three results, one per agent. If you get one before the others, say briefly that you are waiting for the rest and end your turn. When a notification arrives, tick off which agents are done. Compare only when all three are in. If an agent failed or was stopped, say so and compare the rest, or offer to rerun. Never write a notification yourself."
3. Optionally, have each subagent start its answer with a label (A, B or C). That makes it easy to track which have reported.
4. For users who want a strict blocking flow, tell them to set `CLAUDE_CODE_FORK_SUBAGENT=0` in `settings.json` env, or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`. The second also disables Ctrl+B and all background tasks. A skill cannot set either itself. Even then, blocking still depends on Claude choosing to wait.

**Risks and unknowns**
- The position depends most on fork mode being on in v2.1.296 interactive sessions. The docs say it is on by default, but one issue mentions a staged-rollout gate. I did not verify the gating for 2.1.296 specifically.
- I did not directly verify that explicit `run_in_background: false` is ignored or dropped with fork mode on. That rests on the issue text and a search summary.
- Even if blocking works for some users, the notification-tolerant wording costs nothing.

**Confidence:** Medium-high that the skill must tolerate late notifications. Medium on the exact mechanism, meaning whether `false` is ignored or simply absent from the schema.

Sources:
- https://code.claude.com/docs/en/sub-agents
- https://github.com/anthropics/claude-code/issues/87300
- https://claudeissues.com/issue/69030-bug-claude-code-disable-background-tasks-1-ineffective-for-fork-subagents
- https://claudeissues.com/issue/81439-claude-code-fork-subagent-1-silently-overrides-the-documented-teammate-foregroun
- https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md

## R9

**Position:** No. On v2.1.296 in an interactive terminal, Claude can't wait on those three Agent calls, so `run_in_background: false` won't make it wait. The calls start in the background and their results come back as later-turn completion notifications. The developer should rewrite the skill to be notification-driven, or have users turn fork mode off. I'm confident in the first part and less sure of the exact mechanism.

**Reasoning:**
- Docs on subagents (https://code.claude.com/docs/en/sub-agents, verified): "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." For interactive terminal sessions, "to let Claude wait for a subagent, turn off fork mode, which is on by default."
- Same page (verified): "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions on your machine. Fork mode is on by default from Claude Code v2.1.302, and in an interactive terminal session from v2.1.232." So v2.1.296 in a terminal has fork mode on.
- Changelog 2.1.302 (verified) says the terminal already ran the main conversation's subagents in the background "rather than let Claude choose".
- The page never mentions `run_in_background` (verified). I couldn't confirm whether the parameter is silently ignored, overridden, or removed from the tool schema. A third-party write-up says the Agent tool description gains "Subagents run in the background; you'll be notified when one completes" when fork is on. Either way, the doc statement that Claude "can't wait" is what carries the answer.
- Concurrency (verified): background subagents run concurrently. The default limit is 20, and three is well under it.
- Results (verified): "A background subagent's results reach Claude as a completion notification in a later turn. Claude waits for that notification before reporting the subagent's results." In practice Claude's turn ends after spawning. Each result then arrives as its own notification, so the comparison can be written too early, on partial results, or from guesses.
- Older history (verified): background-by-default began in v2.1.198, and the terminal's fork default came in v2.1.232.

**Question 2, recommended changes:**
1. Remove the claim that `run_in_background: false` blocks. It is dead or misleading text.
2. Write explicit notification-driven steps. For example: "Spawn the three subagents in one message. Subagents may run in the background, so do not write the comparison yet. Tell the user you're waiting, then end your turn. Each result arrives as a separate completion notification. Keep a tally of A, B and C. Write the comparison only after all three have arrived. If one fails or is stopped, say so and compare the rest."
3. Optionally tell users to set `CLAUDE_CODE_FORK_SUBAGENT=0` in `settings.json` `env` and restart. The doc says that lets Claude wait when asked. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` forces waiting for every subagent but disables all background tasks, so it is heavier. A skill can't set either itself. Don't make the skill depend on them without a check.
4. Alternative design, inferred from the docs: spawn one coordinator subagent that launches the three and compares them. The doc says that in an interactive terminal a subagent that launches background subagents "waits for their results before it finishes", so you get one final notification. This is less certain, and the coordinator itself still arrives as a notification.

**Risks and unknowns:**
- The facts this depends on most are the doc sentence about Claude being unable to wait with fork mode on, and v2.1.296 falling between v2.1.232 and v2.1.302. The "on by default in terminal from v2.1.232" line comes from the docs, and a secondary source (classmethod) agrees.
- Whether the explicit `false` is honored in some edge case is untested. I ran no live test. A 30-second test in a v2.1.296 session would settle it.
- A user who already set `CLAUDE_CODE_FORK_SUBAGENT=0` or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` would get waiting behavior. That is why the skill should work both ways.
- I fetched the changelog only for 2.1.295 to 2.1.304, not the earlier versions.

**Confidence:** Medium-high on "No, don't rely on blocking", because the docs are explicit. Medium on the exact mechanism, and on whether the coordinator alternative works.

Sources: https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/changelog, https://code.claude.com/docs/en/skills, https://github.com/anthropics/claude-code/releases/tag/v2.1.198, https://dev.classmethod.jp/en/articles/20260814-cc-updates-v2-1-232/

## R10

## Think tank: will `run_in_background: false` make Claude wait for all three?
opus, sonnet, sonnet · session effort · identical brief · debate skipped at 3–0

### Recommendation (3–0)
No, Claude won't wait. From v2.1.232, fork mode is on by default in interactive terminal sessions, and while it's on, Claude can't wait for a subagent in those sessions. v2.1.296 is in that range, so all three subagents run in the background no matter what the skill passes. The answers arrive one at a time, as completion notifications in later turns. Claude might reach the comparison step holding none, one or two of them.

You should rewrite the skill so it expects the results to arrive late:
- **Stop relying on `run_in_background: false`.** Drop it, or keep it knowing it does nothing here.
- **Launch, then stop.** Launch all three in one message, say they're running, and end the turn.
- **Track arrivals.** Note which of the three have reported, and say which are pending if the user asks.
- **Wait for all three.** Don't compare, summarise or guess a pending answer until all three are in.
- **Handle failures openly.** If one fails or is stopped, say so instead of quietly comparing two.
- **Document the user-side setting.** Users who want true blocking can set `CLAUDE_CODE_FORK_SUBAGENT=0` in `settings.json`. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` also works but turns off Ctrl+B and all background tasks. A skill can't set either itself.

Even when blocking does work, a result can still arrive late or not at all:
- the user presses Ctrl+B or interrupts
- an API error leaves partial output
- Claude replies to a message the user typed before the results were in

So the notification-driven wording is worth adding either way.

Checked:
- **Fork mode blocks waiting.** I read the [sub-agents docs](https://code.claude.com/docs/en/sub-agents) myself. They say: "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions on your machine. Fork mode is on by default from Claude Code v2.1.302, and in an interactive terminal session from v2.1.232."
- **Results arrive later.** The same page says a background subagent's results "reach Claude as a completion notification in a later turn".
- **Not checked.** None of the panelists or I could confirm whether the harness silently ignores `run_in_background: false` under fork mode, rejects it, or drops it from the tool's parameters. The conclusion holds whichever it is.

### Panel
- **A** (opus): "No. On v2.1.296 in an interactive terminal, fork mode is on by default, and while it's on Claude can't wait for subagents. So `run_in_background: false` won't get the skill a blocking, all-results-in-one-turn fan-out." Confidence: medium-high.
- **B** (sonnet): "No. On v2.1.296 in an interactive terminal, the three subagents will almost certainly start in the background, so their answers arrive as later completion notifications." Confidence: medium-high, about 80%.
- **C** (sonnet): "No. In a default interactive v2.1.296 terminal session, Claude cannot reliably wait for all three subagents." Confidence: medium-high on the conclusion, medium on the mechanism.

### Where they split
They agreed on the conclusion and differed only on optional extras:
- **A** and **B** suggested a wrapper: one subagent, or a `context: fork` skill, that spawns the three and returns a single combined result. Both said this is untested, and the docs I read only promise that the spawning subagent waits in `claude -p` and the SDK. I wouldn't rely on it in an interactive terminal.
- **B** suggested having each subagent write its answer to a separate file.
- **C** suggested labelling each answer A, B or C, and cited an issue claiming the parameter disappears from the tool in fork mode. I didn't verify that claim.

### My take
I started out leaning "mostly yes, with a caveat about Ctrl+B". The panel and the docs changed my mind. I hadn't known about the fork-mode default, and the documentation quoted above settles it. In this session, the three panelists also went to the background as soon as they launched. That's consistent with the panel, though I didn't pass `false`, so it doesn't test the parameter itself.

For the rewrite, the think-tank skill you just ran already uses the right pattern: "The answers may come back with the launch or later as notifications. Wait for all three before going on, and never start round 2 or the synthesis with one missing." This run went exactly that way: the answers arrived in three separate turns, and the synthesis waited for all of them.

I'd add that sentence, plus a line about failures, and stop treating `run_in_background: false` as a guarantee. Mention the `CLAUDE_CODE_FORK_SUBAGENT=0` setting in the skill's README for users who want blocking. Don't make the skill depend on it.

## R11

**Position:** No. On v2.1.296 in an interactive terminal, the three subagents will almost certainly start in the background, so their answers arrive as later completion notifications. Yes, the skill author should change the skill. Rewrite it for asynchronous results, and don't rely on `run_in_background: false`.

**Reasoning (from the docs unless marked as inference):**
- **Wait is unsupported in interactive sessions.** The sub-agents doc, [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents), says "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." For interactive terminal, VS Code and desktop sessions, "to let Claude wait for a subagent, turn off fork mode, which is on by default."
- **Fork mode is the blocker.** "While fork mode is on, Claude also can't wait for a subagent in interactive terminal… sessions." Fork mode has been on by default in interactive terminals since v2.1.232. The env-vars page says the same about `CLAUDE_CODE_FORK_SUBAGENT`.
- **Results come in a later turn.** "A background subagent's results reach Claude as a completion notification in a later turn." The Agent tool description you quoted also says "you'll be notified when one completes."
- **Inference, not verified.** The docs say Claude "can't wait", so I infer the harness ignores or overrides `run_in_background: false` rather than returning an error. The docs don't state which, and I didn't see harness source or an issue confirming it. Either way the skill's assumption fails.
- **Only the user can change this.** Setting `CLAUDE_CODE_FORK_SUBAGENT=0` or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` would make Claude wait. Both are user or settings-level env vars, and a skill can't set them.
- **Other ways results can be late or missing, even with waiting:**
  - **User actions.** Ctrl+B and `←` move work to the background. Typing a new prompt, or pressing Esc, can interrupt or cancel the turn (2.1.295 and 2.1.296 changelog entries).
  - **Auto-backgrounding.** `CLAUDE_AUTO_BACKGROUND_TASKS` moves a subagent to the background after about 2 minutes.
  - **Stalls and failures.** The default stall timeout is 10 minutes (`CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`). A subagent can also fail (for example on an API error) and return partial or no output.
  - **Claude's own behaviour.** It may run the comparison early, or guess a pending result. The tool description forbids that, but a skill that assumes synchronous results invites it.
- **Parallel calls.** Three Agent calls in one message do launch concurrently. Issue 34916 (v2.1.76, closed as fixed) showed multi-agent launches going to the background even when background tasks were disabled. The notifications come back separately, possibly in different turns.

**Recommended changes:**
1. Drop `run_in_background: false`. Either omit the parameter or set it to `true`, so the skill matches what actually happens.
2. Add wording like this:
   > "Launch all three subagents in ONE message. Do not pass `run_in_background: false`. Their results arrive as separate completion notifications in later turns. After launching, say briefly that the three reviews are running and stop. Do not compare, summarise or predict anything yet. Keep a tally of A/B/C received. Start the comparison only after all three completion notifications have arrived. If the user asks first, say which are still running. If a subagent fails or is stopped, say so and compare the rest, labelling the result partial. Never write or guess a pending agent's result."
3. Optional hardening: have each subagent write its answer to a distinct file (for example `/tmp/cmp-A.md`). The comparison step then reads all three and checks each exists.
4. Optional, untested: run the whole fan-out inside one wrapper subagent. The docs say a subagent that launches background subagents waits for their results, so the wrapper would return one finished summary. This needs checking against the spawn-depth limit and `context: fork` rules.
5. If a synchronous flow is truly required, document that users must set `CLAUDE_CODE_FORK_SUBAGENT=0` in `settings.json`. Note the 2-minute auto-background caveat if `CLAUDE_AUTO_BACKGROUND_TASKS` is enabled.

**Risks and unknowns:** The main dependency is the exact harness handling of `run_in_background: false` under fork mode, which I inferred. The docs may also lag the 2.1.296 behaviour, since the changelog fetch only covered part of the file. The user may have set `CLAUDE_CODE_FORK_SUBAGENT=0` or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, in which case waiting works. A quick test on 2.1.296 would settle it: launch three agents and see whether "Running in the background" appears. The async-safe wording is harmless either way.

**Confidence:** Medium-high (about 80%) that results arrive late in the default setup. The docs are explicit, and only the override mechanism is inferred.

Sources: [sub-agents doc](https://code.claude.com/docs/en/sub-agents), [env-vars doc](https://code.claude.com/docs/en/env-vars), [CHANGELOG](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md), [issue 34916](https://claudeissues.com/issue/34916-bug-claude-code-disable-background-tasks-ignored-when-spawning-multiple-subagent).
