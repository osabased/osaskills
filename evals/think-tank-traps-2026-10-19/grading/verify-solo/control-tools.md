# control-tools

Question asked:

> I wrote a Claude Code subagent in .claude/agents/auditor.md with `tools: Read, Grep, Glob` in its frontmatter. It must never modify files. Is that enough, or does it need more?

## R1

For blocking file edits, `tools: Read, Grep, Glob` is enough. You don't need anything else for that. I checked the current subagents page at code.claude.com/docs/en/sub-agents.

**What I verified in the docs:**

- **`tools` is an allowlist.** Only the tools you list are available. The docs' own code-reviewer example, `tools: Read, Grep, Glob, Bash`, is described as unable to "edit files, write files, or use any MCP tools." Your list doesn't include Bash either, so it's tighter than their read-only example.
- **Skills are blocked.** The docs say leaving `Skill` out of `tools` stops the subagent from invoking skills. Skills can't be used as a back door.
- **It works in the background too.** Background subagents (the default) keep only a fixed set of built-in tools. Read, Grep and Glob are on that list, so your agent has the same three tools whether it runs in the foreground or the background.
- **A misspelled tool name doesn't open everything up.** If no entry in `tools` matches a real tool, Claude Code "usually" refuses to launch the subagent and shows an error. It doesn't fall back to all tools.
- **Hooks are the one way to run code without a listed tool.** A `hooks` entry in the subagent's frontmatter runs shell commands. Don't add hooks to the auditor and nothing changes.

**One real risk (my inference from the docs):** if the `tools` key is missing, the subagent gets every available tool. That includes a typo like `tool:` or frontmatter that doesn't parse, for example when the `---` lines are missing or the YAML is broken. In that case the agent silently gets Edit, Write, Bash and the rest, and there's no error. This is the most likely way your setup would fail, so check the key spelling and the `---` delimiters.

**Optional backstop:** add `disallowedTools: Edit, Write, NotebookEdit, Bash, PowerShell`. The docs say this list is applied first, then `tools` is resolved against what's left. With a correct `tools` line it changes nothing. It protects you if someone later adds Bash or removes the `tools` line.

**What I couldn't verify:**

- I couldn't see your `auditor.md` because it isn't in this directory. Everything above assumes the frontmatter parses correctly.
- **Permission modes:** the docs say a subagent inherits `bypassPermissions`/`acceptEdits` from the main session. They don't say outright that the `tools` allowlist still applies in those modes. I'm fairly confident it does, because those modes only skip approval prompts and don't add tools, but that's my reasoning, not a quote.
- **Forks** get the main session's full tool set. A fork isn't your auditor, though: it's a copy of the main session, not something started from `auditor.md`. So this doesn't affect your definition, but don't assume every delegated task runs through the auditor.

Sources:
- [Claude Code docs: Subagents](https://code.claude.com/docs/en/sub-agents)

## R2

**Position:** It is enough, with caveats. `tools: Read, Grep, Glob` is an allowlist, so the subagent never receives Edit, Write, NotebookEdit, Bash, PowerShell, MCP tools, Skill or Agent. Nothing else is required in the definition. What you do need to confirm is that the file actually loads with that field applied, because a malformed file fails silently.

**Reasoning:**
- **What the docs say:** The current subagents page (https://code.claude.com/docs/en/sub-agents) says that when `tools` is set, it limits the subagent to the listed tools. Inheriting every available tool, MCP tools included, only happens if `tools` is omitted. The page's own example, `tools: Read, Grep, Glob, Bash`, is described as "can't edit files, write files, or use any MCP tools". Your list doesn't even include Bash, so the agent has no shell to write files through.
- **Nesting:** A subagent can only spawn its own subagents if `Agent` is in its `tools` list. Yours can't hand the work to a more capable agent.
- **Permission mode doesn't matter here:** If the main conversation runs in `bypassPermissions`, `acceptEdits` or auto mode, the subagent takes that mode and its own `permissionMode` setting is ignored. That makes `permissionMode` useless as a safeguard. It also doesn't matter, because permission modes only decide whether tools the agent already has get approved. They can't add tools.
- **Not in the definition:** No `mcpServers`, `hooks` or `skills` field adds tools here.

**Ways it could still go wrong (none of them is the tools line failing):**
1. **Frontmatter problems fail silently.** A wrong field name such as `Tools:` or `tool:` is ignored without any error, and the agent then inherits every tool. If the file has no `name`, no `description`, YAML that won't parse, or a `---` that isn't on the first line, the file is skipped. The work could then go to general-purpose, which can write.
2. **Name shadowing.** A managed definition or one passed with `--agents` that uses the same `name` takes priority over `.claude/agents/`. If two files in that directory share a name, which one loads depends on filesystem order.
3. **Hooks from settings, managed policy or plugins still run inside the subagent.** A `PreToolUse` or `PostToolUse` script triggered by Read could change files. That is your own configuration acting, not the agent, but it breaks a literal "no modifications while it runs" guarantee.
4. **Spelling of entries.** The docs don't say how partly misspelled entries in `tools` are handled. A misspelling only shrinks the allowlist, so it can't add write access.

**Recommendations:**
- **Essential:** Check the file has `name`, `description` and the exact lowercase `tools` key, and that `---` is on line 1. Then confirm in `/agents` that auditor shows only Read, Grep and Glob, or run `claude --debug` and search the log for "does not recognize or apply". Make sure no higher-priority agent uses the same name.
- **Optional hardening:**
  - Add `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, mcp__*` as a backstop, since it's applied before `tools`.
  - Add a frontmatter `PreToolUse` hook that blocks anything outside Read, Grep and Glob. It only runs once the folder is trusted.
  - Check that hooks in your settings have no side effects.
- **Not useful:** `permissionMode: plan` can be overridden by the parent's mode. A `permissions.deny` rule on Edit/Write in settings would restrict the main conversation too.

**Risks and unknowns:** Everything above depends on the October 2026 docs saying that a set `tools` list excludes inherited MCP tools and limits the agent to the listed tools. Older versions behaved differently, and the docs' own example is the best evidence I have. I'd change my answer if an MCP tool or Skill showed up in `/agents` for this agent despite the allowlist. I didn't read the last ~9.5k characters of the subagents page.

**Confidence:** High on the core verdict, because the docs state the allowlist semantics directly. Medium that I've found every side channel.

Position: The `tools: Read, Grep, Glob` line is enough to stop the subagent modifying files, provided you confirm the file loads with that field applied (no typo in the key, not shadowed by another agent of the same name), and noting that hooks from your settings still run during its tool calls.

## R3

I read this as asking about the subagent's own tool calls. The parent conversation is a separate agent with its own permissions, so I treat it as outside what the `tools` line can control.

**Position:** Enough, with caveats. `tools: Read, Grep, Glob` is an allowlist that Claude Code enforces when it builds the subagent's tool pool, and none of those three tools can write. You don't need any other frontmatter, settings, hooks or permission rules for the subagent itself. The remaining risks come from things around the file, not from the `tools` line.

**Reasoning:**
- **How it's enforced.** The subagents page (https://code.claude.com/docs/en/sub-agents) defines `tools` as the tools "the subagent can use". The full pool is inherited only when the field is omitted. This is a filter on which tools exist for the subagent, not a prompt instruction or permission prompt. So `permissionMode`, including an inherited `bypassPermissions`, can't add tools back. The docs' own `safe-researcher` example (`Read, Grep, Glob, Bash`) is described as unable to "edit files, write files, or use any MCP tools", and this list is stricter because it has no Bash.
- **Inherited tools.** Not a risk. Inheritance only happens when `tools` is omitted.
- **MCP tools.** Not a risk. They join the pool only through `tools` entries like `mcp__server__*`. One gap: the docs don't explicitly say that servers added through the `mcpServers` field still pass the allowlist. It's strongly implied, so just don't add `mcpServers`.
- **Spawning other agents.** Not a risk. The docs say "omit `Agent` from its `tools` list" to keep a subagent from spawning, and this list does omit it. The `Skill` tool is also absent, so skills can't add a route either.
- **Misspelled tool name.** This fails closed. A misspelled entry gives the subagent fewer tools, never more. If nothing resolves, it "usually fails to launch with an error". A typo can only weaken the agent, never let it write.
- **Background mode.** This filter only removes tools, so it can't add any.

**Risks and unknowns (what would close each):**
1. **Name shadowing (real but uncommon).** A same-named `auditor` from managed settings or `--agents` outranks `.claude/agents/`. A second file in the same directory with the same `name` gets picked by filesystem read order. Close it by keeping the name unique and checking with `/agents`.
2. **Parent acting on the output (real, and outside the subagent).** The auditor's report goes back to the main conversation, which can edit files. If "never modify" is meant to cover the whole session, you need `permissions.deny` rules (e.g. `Edit`, `Write`, plus Bash rules) or plan mode for the main conversation. Frontmatter can't do that.
3. **Session-wide hooks.** Hooks in `settings.json` also fire inside subagents. A hook script that writes files runs as the hook, not as a subagent tool call. Review them if this matters to you.
4. **Edits to the definition itself.** Anyone, or any agent, with write access can change `.claude/agents/auditor.md`. Version control or code review handles that.
5. **Optional extra layer.** `disallowedTools: Write, Edit, NotebookEdit, Bash, Agent` is harmless, but it's redundant once `tools` is set, because the deny list is removed first and the allowlist is then resolved against what's left. A frontmatter `PreToolUse` hook adds little, and it's skipped until the folder is trusted anyway.

The fact my position depends on most: the allowlist decides which tools the subagent has at all, before any permission mode applies. If the docs or a test showed MCP tools from `mcpServers` getting past the allowlist, I'd recommend adding `disallowedTools: mcp__*`.

**Confidence:** High for the subagent itself. The docs state the allowlist semantics directly and give a near-identical read-only example. The only inferred part is the `mcpServers` interaction.

Position: The `tools: Read, Grep, Glob` line is enough on its own to stop this subagent from modifying files, with caveats about name shadowing, session-wide hooks and the parent acting on its output, which need main-session permission rules if the guarantee should cover the whole session. Confidence: high.

## R4

For file modification, yes, that's enough. `tools:` works as an allowlist, so the auditor gets only Read, Grep and Glob. It has no Edit, Write, NotebookEdit, Bash, PowerShell, MCP tools, Skill tool, or ability to spawn other subagents (the `Agent` tool). I checked this against the current subagents page (code.claude.com/docs/en/sub-agents) today.

**What I confirmed in the docs:**
- **`tools` is an allowlist.** The docs describe it as "Tools the subagent can use… Inherits every tool available to subagents if omitted." Their own allowlist example says that subagent "can't edit files, write files, or use any MCP tools."
- **No spawning.** "Listing `Agent` in `tools` lets that subagent spawn subagents of its own." You haven't listed it, so the auditor can't hand work to an agent that can write.
- **No skills.** To stop a subagent using skills, the docs say to "omit `Skill` from the `tools` list."
- **A typo fails safely.** If nothing in `tools` matches a real tool, Claude Code "usually refuses to launch the subagent." The page doesn't say what happens if only some entries are misspelled.
- **Background runs don't add tools.** Running in the background only removes tools; Read, Grep and Glob stay.

**Optional extra layer:** add a denylist so the agent stays read-only even if someone later widens `tools`:
```yaml
tools: Read, Grep, Glob
disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell
```
The docs say `disallowedTools` is applied first and "A tool listed in both is removed," so this can't backfire.

**Things that would break the guarantee later:**
- **Adding Bash or PowerShell.** Shell commands can write files. The docs' own "read-only" code-reviewer example includes Bash, so read-only there just means no Edit or Write. If you ever need a shell, add a `PreToolUse` hook or `permissions.deny` rules. The docs say those rules "apply to the main conversation and to subagents."
- **Adding `Agent` or `Skill`.** Either one gives the auditor an indirect way to get tools you didn't grant.
- **Adding `mcpServers`.** The docs don't say whether servers listed there get past the `tools` allowlist, so I'd leave that field out.
- **Anyone who can edit the file.** It sits in `.claude/agents/` in the repo, so anyone with write access there can change the frontmatter.

**What I couldn't confirm:**
- The page says that on macOS, Linux and WSL a subagent "can also receive the Glob and Grep tools when the main conversation doesn't have them." I didn't read the linked section on this. It only adds search tools, so it doesn't affect writing.
- I didn't fetch the hooks or permissions reference pages. My points about hooks and deny rules come only from what the subagents page says.

One thing outside the subagent's control: the main conversation can still act on the auditor's findings and edit files itself. If you need to prevent that too, it's a session-level permission setting, not something the subagent file can do.

## R5

## Think tank (solo): is `tools: Read, Grep, Glob` enough to keep a subagent read-only?
opus · session effort · one panelist

### Recommendation
Yes, it's enough if the file loads correctly, but a few failure modes are silent. `tools` is a real allowlist that the harness enforces, so the subagent never gets Edit, Write, NotebookEdit, Bash, PowerShell, any MCP tools, Skill or Agent. None of Read, Grep or Glob can write files. The guarantee quietly disappears in these cases:

1. **The file is skipped.** This happens if there's no `name`, a `name` but no `description`, or YAML that doesn't parse. The main agent may then do the work itself or hand it to general-purpose, and both can write. Confirm `auditor` shows up in `/agents`.
2. **The key is misspelled** (`Tools:`, `allowed-tools:`). The field is ignored, so the subagent inherits every tool.
3. **Another definition overrides it.** A managed or `--agents` definition with the same name takes priority.
4. **It runs as a fork.** A fork gets the main session's tools and ignores the definition.
5. **There's no backstop.** Add `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, mcp__*`. For a guarantee that doesn't depend on this file at all, add `permissions.deny` rules for Edit and Write in settings, but those also restrict the main session.
6. **The main conversation acts on the report.** It can make the changes the auditor suggests. Only session-wide rules or hooks cover that.

`permissionMode` doesn't matter here: even `bypassPermissions` can't grant a tool that isn't in the subagent's tool set.

Checked against the subagent docs (code.claude.com/docs/en/sub-agents):
- **Allowlist:** confirmed. `tools` is described as an allowlist, and their `Read, Grep, Glob, Bash` example "can't edit files, write files, or use any MCP tools".
- **Ignored fields and skipped files:** confirmed. Unknown fields are ignored "without reporting an error". Files with no `name`, no `description`, or YAML that doesn't parse are skipped silently (`claude --debug` shows why).
- **Precedence:** confirmed. Managed settings, then `--agents`, then project `.claude/agents/`, then user, then plugin. Two files with the same name in one `.claude/agents/` tree resolve by filesystem read order.
- **Forks:** confirmed. Forks "skip both filters and receive the main conversation's exact tool pool".
- **`disallowedTools`:** confirmed. It's applied first, then `tools` is resolved against what's left. `mcp__*` removes every MCP tool.

### Panelist
"Enough, with caveats. If the file loads correctly, `tools: Read, Grep, Glob` is a real allowlist that the harness enforces. The subagent never receives Edit, Write, NotebookEdit, Bash, PowerShell, MCP tools, Skill or Agent, and none of the three tools it does get can write files. The guarantee breaks quietly in a few cases, though: the file fails to load, the key is misspelled, or another definition with the same name overrides it. So the user should verify the setup and add one backstop." High confidence in the core verdict, medium that the list of failure modes is complete.

### My take
I launched expecting "mostly sufficient, with caveats", and the panelist agreed. What it added was the fork case and the precedence case, which I hadn't thought of.

The `disallowedTools` backstop is weaker than it sounds. It only helps with a misspelled `tools` key, and only if `disallowedTools` is spelled correctly itself. A skipped file loses both fields together. The checks that actually matter are seeing `auditor` in `/agents` and, if you're on v2.1.296 or later, running `claude --debug` and searching for `does not recognize or apply`.

If "never" has to hold no matter what, the only protection that doesn't depend on this one file is `permissions.deny` in settings. You'd pay for that by locking down the main session too.

Your project isn't in this directory, so I couldn't look at the actual file. The checks above have to be run there.

One note: the harness flagged the panelist's report because it mentions `bypassPermissions` and `permissions.deny`. Those were just part of the answer's content, not instructions, so I treated them that way.

## R6

I've finished checking the official docs. For what you described, the `tools` line is enough on its own. I can't see your file, so this assumes the frontmatter parses and is spelled as you wrote it.

## Why it's enough
- **`tools` is an allowlist, not an addition.** The docs say subagents get every available tool only when `tools` is left out. When you set it, the subagent gets just the tools you list.
- **None of your three tools change files.** In the tools reference, `Edit`, `Write`, `NotebookEdit`, `Bash` and `PowerShell` all need permission and can change things. `Read`, `Grep` and `Glob` only read.
- **MCP tools are left out too.** The docs give `tools: Read, Grep, Glob, Bash` as an example and say that agent "can't edit files, write files, or use any MCP tools."
- **Grep and Glob still work on macOS, Linux and WSL.** Those systems leave Grep and Glob out of the default tool set and search through Bash instead. They come back when a subagent lists them in `tools` and leaves out Bash, which is exactly your setup. Don't add `Bash` "for searching": it can write files, and the docs' own read-only reviewer example includes Bash.

## What you don't need
- **`disallowedTools: Write, Edit`**: it does nothing extra here. It matters when you omit `tools` and inherit everything.
- **`permissionMode: plan`**: it doesn't add protection. The docs say that if the main session is in `bypassPermissions`, `acceptEdits` or auto mode, the subagent uses that mode and ignores your setting. Your allowlist holds either way.

## Edge cases that could get around it
1. **Another agent with the same name.** Managed settings, the `--agents` flag, or an `.claude/agents/` folder closer to your working directory all beat your file. A user-level or plugin agent named `auditor` would lose to yours.
2. **Forks don't use your file.** A fork gets the main session's tools, not the subagent's definition. The restriction only applies when `auditor` itself is called.
3. **Only the subagent is restricted.** The main conversation and other agents can still edit files.
4. **Reading isn't harmless.** Read, Grep and Glob still ask before touching paths outside the working directory. Inside it, they can read anything, including secrets.

## What I checked
I read these on code.claude.com today:
- the subagents page, `/docs/en/sub-agents`: points 1–3 above, the MCP example, the `permissionMode` override, which agent wins on a name clash, and forks
- the tools reference, `/docs/en/tools-reference`: which tools need permission, the Grep and Glob restore rule, and point 4

I didn't test anything, since your project isn't in this directory. To check it yourself, run `/agents` in the project and confirm `auditor` shows only Read, Grep and Glob.

## R7

## Think tank (solo): is `tools: Read, Grep, Glob` enough for a read-only subagent?
opus · session effort · one panelist

### Recommendation
Yes, that line is enough to stop the subagent itself from modifying files. `tools` is an allowlist: Claude Code uses it to decide which tools the subagent has at all, before any permission mode comes into play. None of Read, Grep or Glob can write, and with `tools` set the subagent gets no inherited tools, no MCP tools and no Agent tool for spawning others. A misspelled name only leaves it with fewer tools, never more. If no name in the list matches a real tool, the subagent usually fails to launch with an error.

The remaining risks come from outside the `tools` line:
- **The main conversation acting on the auditor's report.** The main session can still edit files. If "never modify" should cover the whole session, you need `permissions.deny` rules or plan mode there.
- **Session-wide hooks.** Hooks from your settings also run inside subagents. A hook script that writes files would do so regardless of the subagent's tools.
- **Name shadowing.** Another agent definition named `auditor` from managed settings or `--agents` takes priority over yours. Run `/agents` to check which one is active.
- **Someone editing the definition file itself.** Version control handles that.

Adding `disallowedTools` would be redundant. Avoid adding an `mcpServers` field, because the docs don't say outright that the allowlist also filters tools from servers added that way.

Checked: the subagents docs page (code.claude.com/docs/en/sub-agents):
- **Allowlist:** `tools` lists the tools "the subagent can use", and it "inherits every tool available to subagents if omitted".
- **Near-identical example:** the docs' `safe-researcher` example, which also allows Bash, "can't edit files, write files, or use any MCP tools". Their read-only `code-improver` example uses exactly `tools: Read, Grep, Glob`.
- **Spawning:** "If you omit `Agent` from the `tools` list entirely, the agent can't spawn any subagents."
- **Typos:** if nothing resolves, the subagent "usually refuses to launch". The docs don't cover the case where only some names are misspelled.
- **Permission modes:** these are documented as separate from the tool list and never add tools back. Background subagents get extra filtering that can only remove tools.
- **Not checked:** the panelist's claim that session hooks fire inside subagents.

### Panelist
"The `tools: Read, Grep, Glob` line is enough on its own to stop this subagent from modifying files, with caveats about name shadowing, session-wide hooks and the parent acting on its output, which need main-session permission rules if the guarantee should cover the whole session." Confidence: high.

### My take
I agree, and it didn't move me from my launch leaning, which was "enough for the subagent itself". It did sharpen one caveat. The practical gap isn't in the frontmatter but in the main conversation acting on the auditor's report. If you need a session-wide guarantee rather than one for this agent, add deny rules for `Edit`/`Write` in settings. The panelist's other caveats (name shadowing, hooks) are real but edge cases.

The harness flagged the panelist's reply for phrases like `bypassPermissions` and `permissions.deny`. I read it, and those phrases are just part of its answer about permission modes. It contained no instructions aimed at me or you.

## R8

## Think tank (solo): is `tools: Read, Grep, Glob` enough to keep the auditor read-only?
opus · session effort · one panelist

### Recommendation
Yes, the line is enough, with caveats. `tools` is an allowlist, so the auditor never gets Edit, Write, NotebookEdit, Bash, PowerShell, MCP tools or Agent. Without Agent it also can't pass work to a subagent that can write. Nothing else is required in the definition. What you do need to confirm is that the file actually loads with the field applied, because the ways it can go wrong fail silently:

- **A wrong field name is ignored, and the agent then gets every tool.** For example, `Tools:` or `tool:` instead of exact lowercase `tools`.
- **A broken file is skipped without telling you.** That happens if it has no `name`, no `description`, or YAML that won't parse. The work can then go to an agent that can write.
- **Another agent can take the name.** A managed or `--agents` definition with the same `name` wins over `.claude/agents/`.
- **Hooks still run.** `PreToolUse`/`PostToolUse` hooks from settings, plugins or managed policy fire on the auditor's Read calls. If one of them writes files, that breaks a strict "nothing changes while it runs" guarantee, even though the agent itself never writes.

**Essential:** Check the frontmatter has `name`, `description` and the exact `tools` key. Then confirm in `/agents` that the auditor shows only Read, Grep and Glob. You can also run `claude --debug` and search the log for `does not recognize or apply`.

**Optional:**
- Add `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, mcp__*` as a backstop.
- Add a `PreToolUse` hook in the frontmatter that blocks any tool outside the three.

**Not useful:**
- `permissionMode: plan`: the main conversation's `bypassPermissions`, `acceptEdits` or auto mode overrides it.
- Settings-level `permissions.deny`: it would also restrict the main conversation.

Checked against the current subagents docs (code.claude.com/docs/en/sub-agents):
- **MCP tools:** confirmed. The docs say an example with `tools: Read, Grep, Glob, Bash` "can't edit files, write files, or use any MCP tools". Tools are inherited only when the field is omitted.
- **Silent failures:** confirmed. "Claude Code ignores a field it doesn't recognize without reporting an error". Files with no name, no description or bad YAML are skipped without notice.
- **Permission mode:** confirmed. The parent's bypass, acceptEdits or auto mode overrides the subagent's `permissionMode`.
- **`disallowedTools`:** confirmed. It is applied first, then `tools` is resolved against what's left.

### Panelist
"The `tools: Read, Grep, Glob` line is enough to stop the subagent modifying files, provided you confirm the file loads with that field applied (no typo in the key, not shadowed by another agent of the same name), and noting that hooks from your settings still run during its tool calls." High confidence in the core verdict; medium that it found every side channel.

### My take
I agree, and the panelist didn't change my view. Before the answer came in, my leaning was that the allowlist does the job and the real risk is a malformed line silently giving the agent every tool. The panelist reached the same place and added two things I hadn't weighed: name shadowing and hooks from your settings. The hooks point is the only real gap left. It's your own configuration acting rather than the auditor, but it matters if "never modify files" has to cover the whole run.

The one step I'd actually take is opening `/agents` once to see the auditor's tool list. If you want a backstop against someone later deleting the `tools` line, the `disallowedTools` line is cheap. I'd skip the `PreToolUse` hook.

## R9

**Position:** Enough, with caveats. If the file loads correctly, `tools: Read, Grep, Glob` is a real allowlist that the harness enforces. The subagent never receives Edit, Write, NotebookEdit, Bash, PowerShell, MCP tools, Skill or Agent, and none of the three tools it does get can write files. The guarantee breaks quietly in a few cases, though: the file fails to load, the key is misspelled, or another definition with the same name overrides it. So the user should verify the setup and add one backstop.

**Reasoning:** This is from Anthropic's subagent docs (https://code.claude.com/docs/en/sub-agents).

- **How enforcement works.** `tools` builds the subagent's tool set; it is not a prompt hint or a permission prompt. The docs say an omitted field means the subagent "Inherits every tool available to subagents". Their own example with `Read, Grep, Glob, Bash` says the subagent "can't edit files, write files, or use any MCP tools". The background-subagent filter only removes tools and never adds them back. Leaving out `Agent` stops it spawning subagents of its own, and leaving out `Skill` stops it invoking skills.

Gaps, each with a fix:

1. **The file is skipped silently.** This happens if `name` is missing, the opening `---` isn't line 1, `description` is missing, or the YAML doesn't parse. The main agent can then hand the task to general-purpose or do it itself, and both can write. *Fix:* confirm `auditor` appears in `/agents`. A new `.claude/agents/` directory created mid-session also needs a restart before it loads.
2. **The key is misspelled.** Unknown fields are "ignored... without reporting an error", so `Tools:` or `allowed-tools:` means it inherits every tool. *Fix:* use exactly `tools`, plus the backstop in item 5.
3. **Another definition overrides it.** Managed and `--agents` definitions with the same name rank above `.claude/agents/`. *Fix:* use a unique name.
4. **It runs as a fork.** Forks "receive the main conversation's exact tool pool" and ignore the definition. *Fix:* invoke it as a named subagent, not a fork.
5. **No backstop if items 1 to 4 go wrong.** *Fix:* add `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, mcp__*`, which is applied before `tools`. For a guarantee that doesn't depend on this file at all, add `permissions.deny` rules for Edit/Write in settings, which also apply to subagents (and to the main conversation, which may be more than they want). A frontmatter `PreToolUse` hook only runs after the folder is trusted; otherwise it is skipped and only logged.
6. **Something else does the writing.** The main conversation can act on the auditor's report. That falls outside the subagent restriction, and only session-wide rules or hooks cover it.

`permissionMode` doesn't matter here. Even `bypassPermissions` can't grant a tool that isn't in the tool set.

**Risks and unknowns:**
- My verdict rests mostly on one fact: that `tools` filters which tools exist for the subagent rather than acting as a soft check. The docs say this clearly. I'd change my mind if Read, Grep or Glob turned out to have a side effect that writes files. I know of none.
- Inherited `permissions.allow` rules can't add tools back. I'm inferring that from how the filtering is described.
- I didn't check whether settings-level hooks can target a single subagent.
- Docs can drift between versions.

**Confidence:** High that a correctly loaded `tools: Read, Grep, Glob` blocks writes, since the docs state the allowlist semantics explicitly. Medium that the list of quiet failure modes is complete.
