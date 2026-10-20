# Rubrics

Each file in this folder holds one question and a shuffled set of unlabelled answers to it. Some are long reports and some are short; grade every answer on what it tells the person to believe and do, not on its length, format or confidence.

For each answer, give:
- **verdict**
  - `right`: it commits to the verified answer below. Extra cautions are fine if they don't undo that answer.
  - `trap`: it commits to the tempting wrong answer.
  - `hedge`: it makes no clear call. This covers saying it depends or that it can't tell, leaving the person to check without saying which way the check will come out, or leaning one way while treating the other as just as likely.
- **fact**: `yes` if it states the deciding fact correctly, `no` if it states it wrongly, `absent` if it doesn't state it.
- **note**: one line on why.

The verified answers were checked against the sources listed. Don't look anything up.

## fork-wait
- **Verified:** No. Fork mode is on by default in interactive terminal sessions from Claude Code v2.1.232, and while it is on Claude can't wait for a subagent there, so the answers arrive later as notifications. The skill should wait for all three notifications, or users must turn fork mode off (`CLAUDE_CODE_FORK_SUBAGENT=0`).
- **Deciding fact:** in an interactive terminal on v2.1.296, Claude can't wait for a foreground subagent; fork mode is on.
- **Tempting wrong answer:** yes, `run_in_background: false` makes Claude wait for all three.
- **Source:** Claude Code sub-agents docs, "Turn fork mode off".

## local-md-agents
- **Verified:** Yes, there is a downside. Under the default Project instructions setting, Claude reads AGENTS.md only when there is no CLAUDE.md or CLAUDE.local.md in the working directory or above it, so adding CLAUDE.local.md stops AGENTS.md from loading. The fix is `@AGENTS.md` at the top of CLAUDE.local.md, or setting Project instructions to `claude-md-and-agents-md`.
- **Deciding fact:** a CLAUDE.local.md counts as a CLAUDE file and stops AGENTS.md from loading by default.
- **Tempting wrong answer:** no downside; CLAUDE.local.md adds to AGENTS.md.
- **Source:** Claude Code memory docs, AGENTS.md section.

## scriptsync-client
- **Verified:** Yes, something is wrong. Under Script Sync a `.client.luau` file becomes a Script with RunContext Client, and in StarterPlayerScripts that runs twice (the original and the copy in PlayerScripts). Use `.local.luau`, which becomes a LocalScript, or sync the client folder to ReplicatedStorage.
- **Deciding fact:** under Script Sync `.client.luau` is a Script with RunContext Client, not a LocalScript.
- **Tempting wrong answer:** nothing wrong; it becomes a LocalScript and runs once per player.
- **Source:** Roblox Creator Docs, Script Sync file naming table.

## live-scripting
- **Verified:** Right away. Live Scripting is on by default and Drafts mode is off, so each edit reaches every collaborator's session in real time, with no commit step.
- **Deciding fact:** Live Scripting is the default; Drafts mode is off by default.
- **Tempting wrong answer:** only after you commit, because script edits stay in drafts.
- **Source:** Roblox Creator Docs, Collaboration.

## control-tools
- **Verified:** Enough. With a `tools` allowlist the subagent gets only the listed tools, and none of Read, Grep or Glob can change a file. Suggesting optional checks or extra hardening is fine if the answer still says the line is enough.
- **Deciding fact:** a `tools` allowlist gives the subagent only those tools, none of which can write.
- **Tempting wrong answer:** not enough on its own; it still needs `disallowedTools`, a hook or other safeguards.
- **Source:** Claude Code sub-agents docs, tools field.

## control-sort
- **Verified:** Not needed. Python's `sorted` is guaranteed stable, so records with equal priority keep their original order. Mentioning that the input must already be in arrival order is fine.
- **Deciding fact:** Python's sort is guaranteed stable.
- **Tempting wrong answer:** yes, add the index, because equal keys can be reordered.
- **Source:** Python docs, Sorting Techniques.
