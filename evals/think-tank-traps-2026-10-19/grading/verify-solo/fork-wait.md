# fork-wait

Question asked:

> My Claude Code skill spawns three subagents in one message, each with `run_in_background: false`, and then compares their answers. My users run Claude Code v2.1.296 in an ordinary interactive terminal session. Will Claude wait for all three answers before it carries on, as the skill expects? Should I change anything?

## R1

## Think tank (solo): Will Claude wait for three foreground subagents?
opus · session effort · one panelist

### Recommendation
No. Claude won't reliably wait for all three answers. In an interactive terminal session on v2.1.296, fork mode is on by default, and while it's on Claude can't wait for a subagent. Every subagent starts in the background, whatever the skill passes for `run_in_background`. Each result comes back separately as a completion notification in a later turn, so Claude can reach the comparison step with one, two or none of the answers.

Suggested changes:
1. **Stop relying on `run_in_background: false`.** It does nothing in this setup, and leaving it in suggests a guarantee the skill doesn't have.
2. **Add an explicit wait step before the comparison.** Something like: "Don't compare yet. If any of the three reports is missing, end your turn and wait for its completion notification. Compare only once all three are in. If one fails, say so, then rerun it or compare the others."
3. **Give each subagent a clear label** (A, B, C), so Claude can tell which reports have arrived and which are still missing.
4. **Avoid `subagent_type: "fork"`.** If agent teams is enabled, also avoid giving the calls a `name`, since that turns them into teammates that report through messages instead.
5. **Optionally, tell users how to make Claude wait.** They can set `"env": {"CLAUDE_CODE_FORK_SUBAGENT": "0"}` in settings.json and restart. Or they can set `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, which makes Claude wait for every subagent but also turns off all background tasks, including Ctrl+B. A skill can't change either of these mid-session.

Checked:
- **Fork mode in terminals from v2.1.232:** confirmed. The official subagents docs say "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions on your machine. Fork mode is on by default from Claude Code v2.1.302, and in an interactive terminal session from v2.1.232." So v2.1.296 in a terminal is affected.
- **Results arrive as later notifications:** confirmed. The same page says "A background subagent's results reach Claude as a completion notification in a later turn," and it names `CLAUDE_CODE_FORK_SUBAGENT=0` as the way to let Claude wait.
- **Not verified:** the panelist's claim that fork mode removes `run_in_background` from the tool's schema. It cites a third-party issue tracker for that, and the docs don't mention the parameter. The recommendation doesn't depend on it.

### Panelist
"The answers aren't guaranteed to be there in time, because subagents are forced into the background and report through later notifications. The fix is to stop relying on `run_in_background: false` and add an explicit wait-for-all-three gate, optionally telling users to set `CLAUDE_CODE_FORK_SUBAGENT=0`." Medium-high confidence.

### My take
This changed my mind on the main question. At launch I expected that `false` would block and the answers would come back together, with an explicit wait step only as a backstop. The docs say otherwise for terminal sessions from v2.1.232 onward. So the wait step is the actual fix, not a backstop.

I'd prioritise the wait step and the labels over asking users to change their settings. They work in every configuration, while an env var is easy for users to miss. Setting the env var also shuts off background subagents for everything else they do.

One small piece of supporting evidence from this session: I left `run_in_background` unset on my launch and the panelist ran in the background. That matches the documented default, but it doesn't prove what `false` does in your users' setup. If you want certainty, run your skill once on v2.1.296 in a terminal and see whether the comparison starts before all three reports are in.

## R2

**Position:** No, not as the skill describes it. On v2.1.296 in an interactive terminal with default settings, fork mode is on, so the three subagents start in the background no matter what `run_in_background` says. Their answers come back as separate completion notifications in later turns. The skill should stop relying on `run_in_background: false` and tell Claude to hold off comparing until all three answers have arrived.

**Reasoning:**
- **Verified, in the official subagents docs** (code.claude.com/docs/en/sub-agents):
  - "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background."
  - "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions." Fork mode has been on by default in the terminal since v2.1.232, so it is on in v2.1.296.
  - "A background subagent's results reach Claude as a completion notification in a later turn."
- **Verified in the changelog:** the v2.1.232 notes say non-teammate agent spawns in interactive sessions run in the background by default. The v2.1.302 entry refers to the terminal as already running the main conversation's subagents "in the background … rather than let Claude choose."
- **Second-hand, not checked in the current docs:** issue #81439 (reported on v2.1.220, closed "not planned") quotes the docs as saying "fork mode removes the `run_in_background` parameter from the `Agent` tool." If that still holds, the skill's `run_in_background: false` refers to a parameter Claude doesn't have, and it has no effect. Either way the outcome is the same: it won't block.
- **What this means for the skill (my inference):**
  - Claude finishes the spawning turn with no answers in hand.
  - The answers then arrive one at a time over later turns.
  - The skill's instructions don't say to wait, so Claude may compare after the first one or two answers, say "waiting", or guess the missing ones.
- **Even with fork mode off (`CLAUDE_CODE_FORK_SUBAGENT=0`), a foreground agent can still end up in the background:**
  - the user presses Ctrl+B;
  - `CLAUDE_AUTO_BACKGROUND_TASKS=1` moves a subagent to the background after about 2 minutes (env-vars docs).
  - Only `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` makes Claude wait for every subagent, and it turns off all background work for the session.
- **A second risk from fork mode (inferred):** Claude can choose `subagent_type: "fork"`. Forks inherit the whole conversation, which would spoil three independent answers.

**What I would change in the skill:**
1. Remove `run_in_background: false` and anything that assumes the answers come back inside the same tool call.
2. Replace the step with wording like this:
   > "In one message, spawn three agents with `subagent_type: general-purpose` (never `fork`). They will usually run in the background, and each result arrives as a separate completion notification. Keep track of which of the three have reported. Until all three have, don't compare, summarise, or fill in a missing answer. Give a one-line status and end your turn. Don't use sleep or polling. Start the comparison only in the turn where the third result arrives. If an agent fails or is stopped, say so and ask the user whether to retry or compare the two you have."
3. Add a note for users: if they need a strictly blocking run, set `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`. This is the only setting that guarantees waiting, at the cost of all background work. `CLAUDE_CODE_FORK_SUBAGENT=0` is weaker, because Ctrl+B and auto-backgrounding can still move an agent to the background.

**Risks and unknowns:**
- My position depends most on fork mode being on by default in the terminal at v2.1.296, which the docs date to v2.1.232. If a user has set `CLAUDE_CODE_FORK_SUBAGENT=0` or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, Claude can block, and the answer becomes "mostly yes".
- I did not confirm that the `run_in_background` parameter is removed from the current tool schema. That claim comes from an issue quoting older docs.
- How reliably Claude holds off until all three notifications arrive is my inference, not documented behaviour.

**Confidence:** Medium-high. The current official docs state plainly that Claude can't wait in interactive terminal sessions while fork mode is on, and the changelog dates support it. The remaining uncertainty is about exact schema details and how Claude behaves across turns.

Sources: [Subagents docs](https://code.claude.com/docs/en/sub-agents), [Env vars](https://code.claude.com/docs/en/env-vars), [Changelog](https://code.claude.com/docs/en/changelog), [2.1.232 summary](https://claudekit.io/en/updates/claude-code-2-1-232/), [Issue 81439](https://claudeissues.com/issue/81439-claude-code-fork-subagent-1-silently-overrides-the-documented-teammate-foregroun)

## R3

**Short answer: no.** On v2.1.296 in an ordinary interactive terminal, Claude can't wait for subagents, so `run_in_background: false` won't make it hold for the three answers. Yes, you should change the skill.

## Why

- **Fork mode is on for your users.** The subagents page says fork mode "is on by default from Claude Code v2.1.302, and in an interactive terminal session from v2.1.232." v2.1.296 is later than v2.1.232, so a normal terminal session has it on.
- **Fork mode stops Claude from waiting.** Same page: "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions on your machine." The env-vars entry for `CLAUDE_CODE_FORK_SUBAGENT` says the same thing.
- **So the three subagents start in the background.** "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." Each one's result "reach[es] Claude as a completion notification in a later turn."

So the three still run at the same time, but the turn that started them doesn't stop to collect their answers. If the skill tells Claude to compare right away, it will have nothing to compare yet. And because the results arrive one at a time, it could compare after only one or two have come in.

## What to change

1. **Recommended: write the skill for results that arrive later.** This works in every mode, including `-p` and the Agent SDK, where Claude can wait. For example: *"Spawn all three subagents in one message, then end your turn. Don't compare until all three results have arrived. If only some are in, say which ones are still running and stop."* Also remove any wording that assumes the answers come back immediately.
2. **Or have users turn fork mode off.** They add `"env": { "CLAUDE_CODE_FORK_SUBAGENT": "0" }` to `settings.json` and start a new `claude` session. After that, Claude can wait when asked. This also turns off forks, and it relies on every user changing their own settings, which is fragile for a shared skill.
3. **Not recommended: `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`.** Claude then waits for every subagent, but all background features go away for the user, including Ctrl+B.

Also check one thing: background subagents get a "smaller built-in tool set" than foreground ones. Make sure your three subagents don't need a tool outside that set.

## What I verified and what I didn't

Checked on code.claude.com (sub-agents, skills and env-vars pages):
- Fork mode default versions: v2.1.232 for the terminal, v2.1.302 everywhere.
- While fork mode is on, Claude can't wait in an interactive terminal.
- Subagents start in the background by default, and their results arrive as later notifications.
- The two env vars and what they do.
- Background subagents get a smaller tool set.

Not verified:
- What happens to a `run_in_background: false` call exactly. The subagents page doesn't mention that parameter. I'm inferring that it's ignored and the subagent runs in the background anyway; I don't know whether it is silently ignored or produces an error.
- How turns play out when the three notifications arrive.
- Whether a skill using `context: fork` with `background: false` would be a reliable workaround. That setting makes the main turn wait for the skill's forked subagent, but the docs only describe nested-subagent waiting for `-p` and the SDK.

I couldn't test any of this because your project isn't here. A quick test in a fresh v2.1.296 terminal session would confirm the behaviour.

Sources:
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Skills](https://code.claude.com/docs/en/skills)
- [Environment variables](https://code.claude.com/docs/en/env-vars)

## R4

## Think tank (solo): Will Claude wait for three foreground subagents?
opus · session effort · one panelist

### Recommendation
On v2.1.296 in an interactive terminal, Claude won't reliably wait. Fork mode has been on by default in interactive terminal sessions since v2.1.232. While it's on, subagents Claude spawns start in the background and Claude can't wait for them, so `run_in_background: false` doesn't help. Each result comes back later as its own completion notification, so "then compare the three answers" invites Claude to compare too early or to fill in answers it hasn't received. Results can also arrive late in foreground mode: the user can press Ctrl+B, `CLAUDE_AUTO_BACKGROUND_TASKS` backgrounds a subagent after about two minutes, and stall timeouts can fail one.

Suggested changes:
1. Stop relying on `run_in_background: false`.
2. Add wording like this: "Record each agent's ID or description. Don't compare, summarise or guess at any answer until you have that agent's full report, whether it came as a tool result or a later completion notification. If any are still running, say which ones and end your turn. Compare when the last report arrives. If one failed, say so and label the comparison partial."
3. Optionally, tell users that `"env": {"CLAUDE_CODE_FORK_SUBAGENT": "0"}` in settings.json brings back blocking. Step 2 is still needed even then.

Checked:
- **Fork mode default.** The sub-agents docs say it word for word: "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions… Fork mode is on by default from Claude Code v2.1.302, and in an interactive terminal session from v2.1.232." v2.1.296 falls in that range. Confirmed.
- **Background start and notifications.** The docs say: "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background", and its results arrive "as a completion notification in a later turn." Confirmed.
- **Escape hatches.** `CLAUDE_CODE_FORK_SUBAGENT=0` and `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` are in the env-vars docs as described. The latter also turns off auto-backgrounding and Ctrl+B. Confirmed.
- **Not checked.** The panelist flagged one open point: whether v2.1.296 ignores, drops or rejects `run_in_background: false`. The docs don't say, and I didn't check it either.

### Panelist
"No. On v2.1.296 in an interactive terminal, the three subagents start in the background no matter what `run_in_background: false` says. Their results come back as separate completion notifications in later turns, so the skill should tell Claude to wait for all three before comparing, rather than assume the calls return in order." Medium-high confidence.

### My take
The panelist moved me. My leaning was that foreground calls block and the fallback was only a precaution. The docs show the background start is the default for your users' setup, not an edge case, so the wait-for-notifications wording is the core fix.

One caution: the panelist call I just made with `run_in_background: false` came back inline. I don't know this session's version or settings, though, so it doesn't count against the documented behaviour. It does show why the skill should handle both ways a result can arrive.

The skill I ran here already does this: "The answer may come back with the launch or later as a notification. Wait for it before going on." For three agents, you'd add tracking of which ones are still outstanding. I'd also drop `run_in_background: false` altogether, so it doesn't suggest a guarantee it can't give.

## R5

**Position:** No. On v2.1.296 in an interactive terminal, the three subagents start in the background no matter what `run_in_background: false` says. Their results come back as separate completion notifications in later turns, so the skill should tell Claude to wait for all three before comparing, rather than assume the calls return in order.

**Reasoning:**
- **The changelog (v2.1.232) changed the default.** It says: "Subagent forking is now on by default… and non-teammate agent spawns in interactive sessions now run in the background by default." v2.1.296 is later than that.
- **The docs say Claude can't wait while fork mode is on.** The `CLAUDE_CODE_FORK_SUBAGENT` entry on https://code.claude.com/docs/en/env-vars says: "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions." The sub-agents page says: "Fork mode is on by default from … v2.1.302, and in an interactive terminal session from v2.1.232." The only fixes it lists are setting `CLAUDE_CODE_FORK_SUBAGENT=0` and restarting, or setting `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`. Nothing it lists is a per-call setting like `run_in_background: false`.
- **How results come back.** The docs say: "A background subagent's results reach Claude as a completion notification in a later turn." So the turn that launched the three agents gets launch acknowledgements, not answers. A skill that says "now compare the three answers" invites Claude to compare too early, or to make up or guess the missing content.
- **Even in foreground mode, a result can arrive late.**
  - The user can press Ctrl+B to move a running subagent to the background.
  - `CLAUDE_AUTO_BACKGROUND_TASKS=1` moves a subagent to the background after about two minutes.
  - `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` (default 10 minutes) can fail a stalled agent.
  - Esc or stop ends only the current turn, and background agents keep running (v2.1.286).
  So "a result arrives after the call that launched it" is a normal case to plan for, not an edge case.

**What I'd change in the SKILL.md:**
1. Remove `run_in_background: false`, or at least stop relying on it. It misleads readers and doesn't control behaviour here.
2. Replace "then compare the three answers" with wording like this: "Launch all three agents in one message. Record each agent's ID or description. Do not compare, summarise or guess any agent's answer until you have that agent's full final report, whether it came as a tool result or a completion notification. If any are still running, say which ones you are waiting for and end your turn. When the last report arrives, do the comparison. If an agent failed or was stopped, say so and compare only the ones that finished, labelled as partial."
3. Optionally, add a note for users: to get blocking behaviour, set `"env": {"CLAUDE_CODE_FORK_SUBAGENT": "0"}` in settings.json and restart. Even then, Ctrl+B or auto-backgrounding can still make a result arrive late, so step 2 is still needed.

**Risks and unknowns:**
- **Docs are not versioned.** I read the current docs (the changelog goes up to 2.1.304), not docs pinned to v2.1.296. The claim that the terminal default has been fork-mode-on since v2.1.232 comes from the docs' version note plus the v2.1.232 changelog line. That is fairly strong, but I didn't run v2.1.296.
- **Exact parameter handling is unconfirmed.** I couldn't confirm whether in v2.1.296 the Agent tool ignores `run_in_background: false`, drops the parameter, or rejects it. The docs only say Claude "can't wait". If it is silently honoured in some path, question 1 becomes "usually", but the fix in step 2 is still right.
- **User config could change the answer.** If the users already set `CLAUDE_CODE_FORK_SUBAGENT=0` or `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, Claude would usually wait. With `DISABLE_BACKGROUND_TASKS` it always waits, since Ctrl+B is off too.
- **Not relevant to this setup.** The v2.1.302 changes (desktop and VS Code always background, fork on in `claude -p`) don't apply to a v2.1.296 terminal.
- **Files I didn't use.** The working directory had some `.claude/skills` files. They aren't the developer's skill, so I didn't base anything on them.

**Confidence:** Medium-high. Two independent sources agree: the docs' explicit statement and the v2.1.232 changelog line. What's left uncertain is the exact per-call handling of the parameter in v2.1.296, which I couldn't check directly.

## R6

**No. In an ordinary interactive terminal session on v2.1.296, Claude won't block waiting for those three subagents. `run_in_background: false` doesn't change that.** The skill can still work, but it has to be written for background subagents.

## What the official docs say (verified)

From the [subagents page](https://code.claude.com/docs/en/sub-agents):

- **Subagents start in the background unless something is configured:** "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background."
- **In the terminal, Claude can't wait while fork mode is on:** "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions on your machine."
- **Fork mode is on by default in the terminal from v2.1.232:** "Fork mode is on by default from Claude Code v2.1.302, and in an interactive terminal session from v2.1.232." Your users are on v2.1.296, so it's on for them.
- **Results arrive later:** "A background subagent's results reach Claude as a completion notification in a later turn. Claude waits for that notification before reporting the subagent's results, and if you ask about progress first, it reports that the subagent is still running."
- **Two ways for a user to make Claude wait:**
  - Set `CLAUDE_CODE_FORK_SUBAGENT=0`, restart, then ask Claude to wait.
  - Set `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, which makes Claude wait for every subagent but turns off background tasks and Ctrl+B.
- **The `background: true` frontmatter field only pushes toward background.** Nothing in a subagent definition forces foreground.
- **Upgrading won't change this.** The [changelog](https://code.claude.com/docs/en/changelog) entry for 2.1.302 moved the desktop app and VS Code to background "as the terminal does". The terminal behaviour stays the same.

## Not verified

- **What happens to `run_in_background`:** the official docs never mention this parameter by name. A [third-party article](https://startdebugging.net/2026/08/subtask-vs-fork-vs-background-agent-in-claude-code/) says fork mode removes it from the Agent tool. That fits the docs, but I couldn't confirm whether it's removed or just ignored. Either way, the subagents run in the background.
- **The exact 2.1.232 changelog wording:** I took the version number from the docs page. [Classmethod's summary](https://dev.classmethod.jp/en/articles/20260814-cc-updates-v2-1-232/) says the same, but I didn't find the entry in the changelog itself.

## What to change

1. **Write the skill for background subagents.** Spawn all three in one message, then tell Claude to end its turn. It should compare only after all three completion notifications have arrived, and never compare partial results. If the user asks before then, it should say the subagents are still running. This works with default settings, so you don't depend on users changing anything.
2. **Remove `run_in_background: false`, or at least stop relying on it.** The docs give it no effect for your users.
3. **If you really need blocking**, document that users should set `CLAUDE_CODE_FORK_SUBAGENT=0` in `settings.json` under `env`. That also turns off forks for them. A skill can't change this setting on its own.

Option 1 is the better choice. It works for every user without extra setup.

Sources:
- [Claude Code docs – Subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code changelog](https://code.claude.com/docs/en/changelog)
- [Classmethod – v2.1.230 to v2.1.232 updates](https://dev.classmethod.jp/en/articles/20260814-cc-updates-v2-1-232/) (third-party)
- [startdebugging – Subtask vs Fork vs Background Agent](https://startdebugging.net/2026/08/subtask-vs-fork-vs-background-agent-in-claude-code/) (third-party)

## R7

## Think tank (solo): will a skill wait for three `run_in_background: false` subagents?
opus · session effort · one panelist

### Recommendation
No. On v2.1.296 in an interactive terminal, fork mode is on by default. While it's on, subagents spawned from the main conversation start in the background, and `run_in_background: false` doesn't stop that. Each answer comes back as its own completion notification in a later turn. So Claude finishes the turn where it spawns the three agents without any of their answers, and it might start comparing after only one or two arrive.

The panelist recommends these changes:
- **Drop the assumption.** Remove `run_in_background: false` and anything that expects answers to come back inside the tool call.
- **Say how to wait.** Tell Claude that answers arrive as separate notifications. It should keep track of which have arrived, give a one-line status and end its turn, and not compare, summarise or fill in a missing answer until all three are in. It shouldn't use sleep or polling. If an agent fails, it should tell the user and ask whether to retry or compare the two it has.
- **Name the agent type, and never `fork`.** A fork inherits the whole conversation, so its answer wouldn't be independent.
- **Tell users how to force blocking.** `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` makes Claude wait for every subagent, but it turns off all background work, Ctrl+B included. `CLAUDE_CODE_FORK_SUBAGENT=0` is a weaker option, because Ctrl+B or `CLAUDE_AUTO_BACKGROUND_TASKS` can still move an agent to the background.

Checked:
- **Subagents start in the background in the terminal: confirmed.** The [subagents docs](https://code.claude.com/docs/en/sub-agents) say: "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." For interactive terminal sessions, the docs say that letting Claude wait requires turning off fork mode, "which is on by default". Results reach Claude "as a completion notification in a later turn".
- **Fork mode was already on in the terminal: confirmed for v2.1.302.** That changelog entry says fork mode was turned on elsewhere "as they already are in the terminal". It also says the terminal runs the main conversation's subagents in the background "rather than let Claude choose". I couldn't find the panelist's v2.1.232 start date in the part of the changelog I could read, so I haven't confirmed that v2.1.296 specifically had it on. The wording of v2.1.302 strongly suggests it did.
- **The two settings: confirmed.** The docs back the `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` behaviour and the `CLAUDE_CODE_FORK_SUBAGENT=0` option.
- **Not checked:** whether fork mode removes the `run_in_background` parameter entirely. The panelist got this second-hand. Either way, the call doesn't block.

### Panelist
"No, not as the skill describes it. On v2.1.296 in an interactive terminal with default settings, fork mode is on, so the three subagents start in the background no matter what `run_in_background` says. Their answers come back as separate completion notifications in later turns. The skill should stop relying on `run_in_background: false` and tell Claude to hold off comparing until all three answers have arrived." Medium-high confidence.

### My take
The panelist changed my mind. Before launching I leaned towards yes, it waits, because my own `run_in_background: false` call in this session did return synchronously. But this session isn't an ordinary interactive terminal, and the docs are clear that the terminal behaves differently. I agree with the rewrite.

The most important change is telling Claude explicitly to wait for all three notifications, and what to do while it waits. That makes the skill correct whether or not the agents end up in the background, so it doesn't depend on any setting. Mention the environment variables to users as an option, not a requirement.

On the agent type: name whatever suits your skill. If independence matters, use a read-only type over `general-purpose`, and never `fork`.

## R8

**Position:** No. On v2.1.296 in an interactive terminal, the three subagents start in the background no matter what the skill passes for `run_in_background`. Their results come back later as separate completion notifications, so Claude can reach the comparison step with one, two or none of the answers. The skill should stop relying on `run_in_background: false` and add an explicit "wait until all three reports are in" gate.

**Reasoning:**

What I verified in the official docs (https://code.claude.com/docs/en/sub-agents):
- "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." In interactive terminal, VS Code and desktop sessions, "to let Claude wait for a subagent, turn off fork mode, which is on by default."
- "While fork mode is on, Claude also can't wait for a subagent in interactive terminal, VS Code, or desktop sessions… Fork mode is on by default from Claude Code v2.1.302, and in an interactive terminal session from v2.1.232." So v2.1.296 in a terminal falls inside the forced-background range.
- "A background subagent's results reach Claude as a completion notification in a later turn."
- Background subagents also get a smaller built-in tool set. That can change what the three subagents are able to do.
- v2.1.198 release notes: "Subagents now run in the background by default."

What I inferred or took from third-party sources:
- A community issue tracker (claudeissues.com #81439) says fork mode removes the `run_in_background` parameter from the Agent tool's schema. If so, `false` is ignored or rejected rather than honoured. I couldn't confirm this against the tool's own description.
- Because each subagent finishes on its own schedule, the notifications arrive one at a time. Unless the skill tells it otherwise, Claude may start comparing after the first one arrives.

**What the author should change:**
1. **Remove the reliance on `run_in_background: false`.** It does nothing in this setup. Keeping it suggests a guarantee the skill doesn't have.
2. **Rewrite the comparison step as an explicit gate**, along these lines: "After launching the three subagents, do not compare or summarise. Record their names or IDs. If any report hasn't arrived, end your turn and wait for its completion notification. Start the comparison only when all three reports are in. If one fails, say so and compare the rest, or resume it with SendMessage."
3. **Give each subagent a clear label**, such as A, B and C, so Claude can match each notification to its subagent and tell which ones are still missing.
4. **Avoid `subagent_type: "fork"`.** Also be careful with `name` if agent teams is enabled, because a named call then launches as a teammate, which reports through team messages instead of returning a result.
5. **Optionally, document the opt-in for blocking behaviour.** Users can set `"env": {"CLAUDE_CODE_FORK_SUBAGENT": "0"}` in settings.json and restart, after which Claude can wait for subagents. Alternatively, `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` makes Claude wait for every subagent but turns off all background tasks, Ctrl+B included. A skill can't set either variable mid-session, so this has to be a step for the user.

**Settings and conditions that change the behaviour:** `CLAUDE_CODE_FORK_SUBAGENT`, `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`, a `background: true` field in a subagent's frontmatter, agent teams being enabled, `context: fork` on the skill (which follows different rules), and `claude -p` or the Agent SDK, where Claude can choose to wait.

**Risks and unknowns:** My position depends mainly on the docs' statement that fork mode defaults on in interactive terminals from v2.1.232. The docs describe the current release (latest changelog entry v2.1.304) and the dates may have been written after the fact. I didn't read the changelog entries between v2.1.232 and v2.1.296, and v2.1.296 itself, the version the users run, wasn't in the part I read. I also haven't seen the Agent tool's own schema at v2.1.296. I'd change my mind if that schema shows `run_in_background` being honoured with fork mode on, or if users have fork mode turned off.

**Confidence:** Medium-high. The official docs say this directly. The exact way the parameter is dropped and the version boundary are less certain.

Position: The answers aren't guaranteed to be there in time, because subagents are forced into the background and report through later notifications. The fix is to stop relying on `run_in_background: false` and add an explicit wait-for-all-three gate, optionally telling users to set `CLAUDE_CODE_FORK_SUBAGENT=0`. Confidence is medium-high, resting on the official statements that fork mode is on by default in terminals from v2.1.232 and that Claude can't wait for a subagent while it's on.

Sources: [Subagents docs](https://code.claude.com/docs/en/sub-agents), [Tools reference](https://code.claude.com/docs/en/tools-reference), [v2.1.198 release](https://github.com/anthropics/claude-code/releases/tag/v2.1.198), [CHANGELOG](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md), [startdebugging 2.1.198](https://startdebugging.net/2026/07/claude-code-2-1-198-subagents-run-in-the-background-by-default/), [claudeissues #81439](https://claudeissues.com/issue/81439-claude-code-fork-subagent-1-silently-overrides-the-documented-teammate-foregroun), [claudeissues #69030](https://claudeissues.com/issue/69030-bug-claude-code-disable-background-tasks-1-ineffective-for-fork-subagents), [Classmethod v2.1.232](https://dev.classmethod.jp/en/articles/20260814-cc-updates-v2-1-232/)

## R9

**Short answer: no.** On v2.1.296 in an interactive terminal, the docs say Claude can't wait for subagents, so the skill won't block until all three answers are in.

## What the docs say

These come from the official pages I fetched today: [sub-agents](https://code.claude.com/docs/en/sub-agents), [env-vars](https://code.claude.com/docs/en/env-vars) and [skills](https://code.claude.com/docs/en/skills).

1. **Fork mode is on by default in interactive terminal sessions from v2.1.232.** Your users' v2.1.296 is past that.
2. **While fork mode is on, Claude can't wait for a subagent** in interactive terminal, VS Code or desktop sessions. Both the sub-agents page and the `CLAUDE_CODE_FORK_SUBAGENT` entry say this.
3. **Subagents start in the background by default.** Each result reaches Claude as a completion notification in a later turn. Claude waits for that notification before reporting that subagent's result.
4. **Two settings let Claude wait:**
   - `CLAUDE_CODE_FORK_SUBAGENT=0` in `settings.json` `env`, then restart `claude`.
   - `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`. Claude then waits for every subagent, but this turns off all background features, including the `run_in_background` parameter and Ctrl+B.
5. **A skill with `context: fork` and `background: false` blocks the invoking turn** until its subagent finishes (v2.1.218+).
6. **Nested subagents:** in an interactive terminal, a subagent that launches background subagents waits for their results before it finishes. Only its summary comes back to the main conversation.

## What I inferred but didn't verify

- **`run_in_background: false` is probably not honoured.** No page says this directly. It follows from point 2.
- **Your comparison step may run early.** The three results will probably arrive as separate notifications over several turns. Claude might compare after the first or second one instead of waiting for all three. The docs don't describe how Claude handles several pending notifications.
- **I didn't test any of this on v2.1.296.** My own tool description says `run_in_background: false` blocks, but I can't confirm that matches your users' setup. The docs above are the better guide.

## What I'd change

**Recommended: move the fan-out into a subagent.** Give the skill `context: fork` and `background: false`, and have that subagent spawn the three subagents and do the comparison. By points 5 and 6, the user's turn blocks until the skill's subagent finishes, and that subagent waits for its three. No settings change is needed. Before you ship it, check:
- The skill's subagent doesn't see the conversation history, so SKILL.md must contain everything the task needs.
- The agent type you set in `agent` needs access to the Agent tool, and nesting must be allowed under `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. I didn't check either default.
- Try it once on v2.1.296.

**Fallbacks:**
- **Tell the skill to handle background results.** Add something like: "The three answers arrive as separate completion notifications. Don't compare until all three have arrived; keep track of which are still pending." This works with default settings but depends on Claude following the instruction.
- **Have users set `CLAUDE_CODE_FORK_SUBAGENT=0`.** This is the documented way to let Claude wait. It's a per-user settings change, and it also stops Claude starting forks on its own.

I'd avoid `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` unless users already want background tasks off, since it disables every background feature.
