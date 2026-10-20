# control-tools

Question asked:

> I wrote a Claude Code subagent in .claude/agents/auditor.md with `tools: Read, Grep, Glob` in its frontmatter. It must never modify files. Is that enough, or does it need more?

## R1

**Position:** Enough with caveats. As written, `tools: Read, Grep, Glob` is a real allowlist, and none of those three tools writes files. Whether it holds depends on whether the `tools` line is the only thing in the definition that grants capability, and on whether this definition is the one that actually runs. If the requirement is a hard guarantee, add `disallowedTools` and deny rules.

**Reasoning:**

Confirmed by the docs (https://code.claude.com/docs/en/sub-agents):
- `tools` is an allowlist. The docs' own `tools: Read, Grep, Glob, Bash` example is described as "can't edit files, write files, or use any MCP tools". Omitting `tools` means the subagent inherits everything.
- `disallowedTools` is applied first and then `tools` is resolved against what remains. It is the documented belt-and-braces mechanism: `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, Agent, Skill, mcp__*`.
- The docs say "Claude Code ignores a field it doesn't recognize without reporting an error." A misspelling such as `tool:` or `allowed-tools:` would therefore silently give the subagent every tool. The docs suggest `claude --debug` and searching for `does not recognize or apply`. The line you quoted is spelled correctly.

Gaps, ranked by how likely they are to matter:
1. **A different definition wins.** When names collide, the order is managed settings, then `--agents`, then `.claude/agents/`, then `~/.claude/agents/`, then plugins. A same-named `auditor` at a higher level replaces yours. This is confirmed. How often it happens is my guess.
2. **Forks.** The docs say a fork "sees the same system prompt, tools, model, and message history as the main session" and skips the tool filters. A fork is not your `auditor`, so its restrictions don't apply. If you mean "no delegated work edits files", forks are a bypass. That follows from the docs but isn't spelled out for this scenario.
3. **Other frontmatter fields.** I couldn't see the rest of the file. A `Bash` entry in `tools` is the biggest risk, because Bash can write files through redirects and similar. The docs' answer is a `permissions.deny` rule or a PreToolUse hook. Inline `mcpServers` may add write-capable tools. The docs don't say clearly whether an allowlist excludes inline-server tools, so that is unverified. Skills are only blocked if `Skill` is left out of `tools`, and it is in your list. `hooks` in the file or in settings can run arbitrary commands.
4. **`permissionMode` has no bearing on Read, Grep and Glob.** It would matter only if a write tool were present. If the main session is in `bypassPermissions` or `acceptEdits`, it overrides the subagent's `permissionMode`, which is another reason to keep write tools out of the pool entirely.
5. **Inference, not in the docs.** Edits made by the parent session, or by a user acting on the auditor's report, are outside the subagent's control. A subagent also can't be stopped from putting write instructions in its output.

**Fixes:**
- Add `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, Agent, mcp__*`.
- Put `permissions.deny` entries for `Edit`, `Write` and `Bash` in settings. Managed settings are the strongest option because they have the highest priority.
- Don't set `mcpServers`, `hooks` or `skills` in the file.
- Run `claude --debug` to check the field was parsed, and use `/agents` to confirm the effective tool list and which definition won.
- Set `permissionMode: plan` or `dontAsk` as an extra layer. Note that the main session's mode can override it.

**Risks and unknowns:** My verdict depends on `tools` being the only capability-granting field in the file and on this being the definition that runs. I could only read the docs, not the file. The fetch was truncated at about 100k of 109k characters. The behaviour of inline MCP tools under an allowlist is unverified. If the file has `Bash` in `tools`, or the debug output shows ignored fields, my verdict changes to "not enough".

**Confidence:** Medium-high. The allowlist behaviour is directly documented. The caveats come from the docs but I couldn't test them.

Sources: https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/permissions

## R2

**Position:** Sufficient with caveats. `tools: Read, Grep, Glob` is a real allowlist, and none of those three tools can write, so the line alone gives the subagent no file-modifying tool. "Never" also depends on the file loading, on the name resolving to this file, and on no other mechanism adding write access.

**Reasoning (checked against code.claude.com/docs/en/sub-agents and /permissions):**
- **Allowlist semantics.** The docs say a subagent "inherits every tool available to subagents if omitted", and listing tools restricts it to that list. The docs' own read-only reviewer examples rely on this. Your list has no Bash, Write, Edit, NotebookEdit or MCP tools. Bash is the usual loophole, because `>`, `tee` and `sed -i` can all write, and you've omitted it.
- **Misspelled names.** If no entry resolves, the docs say Claude Code "usually refuses to launch" the subagent and reports the unresolved entries. The docs don't say what happens when only some entries are misspelled. Misspelling doesn't widen access, but the agent may then run with fewer tools than you intended.
- **Parent permission mode.** This does not widen the tool set. `bypassPermissions`, `acceptEdits` and auto mode in the parent override the subagent's `permissionMode`. They change prompting, not which tools exist, so they can't add Write to a subagent that doesn't have it.
- **Hooks and skills.** Subagent frontmatter hooks only add restrictions. Skills preloaded through the `skills` field inject text, not tools.
- **MCP.** The docs' own example says `tools: Read, Grep, Glob, Bash` means the subagent "can't… use any MCP tools". That implies the allowlist also filters MCP tools. The docs don't state this explicitly for inline `mcpServers`.
- **Name precedence.** Same-named definitions resolve by priority: managed settings, then `--agents` CLI, then `.claude/agents/`, then `~/.claude/agents/`, then plugins. A managed or `--agents` definition named `auditor` would silently replace your file. Two files with the same name in one directory are resolved by "filesystem read order", which is undocumented. Nested `.claude/agents/` directories resolve to the one closest to the working directory.
- **Silent skips.** A file is skipped with only a debug-log entry if its YAML doesn't parse, the `---` isn't on line 1, or `name` or `description` is missing. The `auditor` agent then doesn't exist, so a call to it may land on a different agent or fail.
- **Memory.** If you ever add `memory:`, the docs say Read, Write and Edit are automatically enabled. This is the one documented way for a listed `tools` field to be overridden.

**Prioritized checklist:**
1. Never add `memory:` or Bash to this agent. Verified in the docs.
2. Add `disallowedTools: Write, Edit, NotebookEdit` to the frontmatter, plus `mcp__*` if you want no MCP tools. It is applied before `tools`, which makes the denial explicit and robust against later edits to the `tools` line. Verified.
3. Add `permissions.deny` rules for `Edit` (and `Write`) in project or managed settings. The permissions docs say `Edit` rules cover all built-in file-editing tools, and deny is evaluated first. Whether a settings-level deny applies to a subagent with the tool already withheld is the same layer as the check above, which I didn't separately confirm.
4. Run `claude --debug` or `/agents` to confirm `auditor` loads and that its tool list is exactly the three tools. Also search for duplicate `auditor` names in `~/.claude/agents`, nested directories, plugins, managed settings and `--agents`. Verified the precedence rules.
5. If you ever need Bash, don't rely on the prompt to keep it read-only. Add a PreToolUse hook that exits 2 on write commands, or use the sandbox with filesystem write restrictions. The docs show the hook pattern, and the sandbox is mentioned in the permissions page. Neither is needed for the current three tools.
6. For a hard guarantee, use OS-level read-only access, such as a read-only mount or a container.

**Risks and unknowns:**
- My verdict depends most on the `tools` field being an enforced allowlist, and on the file actually loading as `auditor`.
- I didn't verify partial-typo behavior, or whether inline MCP servers are filtered by `tools`.
- I read about 95% of the sub-agents page. The last roughly 9.5k characters were summarized only by the fetch tool.
- Docs may differ from your installed Claude Code version.
- Outside the subagent, the parent session or user hooks can still write files. "The subagent never modifies files" doesn't cover them.

**Confidence:** High that the line removes all write tools. Medium that "never" holds without the extra layers, because of the precedence and silent-skip edge cases.

## R3

Yes, that's enough. `tools: Read, Grep, Glob` is an allowlist, so the subagent gets only those three tools. It won't have Edit, Write, NotebookEdit or Bash, and Bash is the one that matters most, since a shell can change anything. It also won't get MCP tools unless you list them. None of those three tools can write to disk, so the agent has no way to modify files.

I can't see your file, so check these yourself:

1. **The field has to parse.** If `tools` is missing or the frontmatter is malformed, the subagent inherits *all* tools, so a broken file fails open. Check that:
   - `tools:` sits inside the `---` block at the very top of the file.
   - It's spelled exactly `tools`.
   - The names are capitalized as shown.

   Then run `/agents` in that project to confirm it lists only Read, Grep and Glob.
2. **Don't add tools later without thinking.** WebFetch and WebSearch are fine. Bash undoes the whole guarantee: even "just for `git log`" lets it run `rm` or redirect output into a file.
3. **The prompt doesn't enforce anything.** Writing "never modify files" in the body is fine as guidance, but the `tools` list is what actually stops it.

Things outside the subagent's control:

- **The main agent can still edit.** The restriction applies only to the auditor. If the main agent acts on the auditor's report, it uses its own tools and permissions.
- **Hooks still run.** Any PreToolUse/PostToolUse hooks in your settings run when the subagent calls Read/Grep/Glob. If one of them writes files, that happens outside the allowlist.
- **Read-only doesn't mean it can't see secrets.** It can read `.env`, keys and similar files. If that matters, add deny rules in `settings.json`, e.g. `"deny": ["Read(./.env)", "Read(./secrets/**)"]`.

If you paste the frontmatter, I'll check it.

## R4

**Position:** Sufficient with caveats. In the normal case, `tools: Read, Grep, Glob` is an allowlist of three read-only tools, so the subagent can't edit files through its own tool set. A "never" requirement needs a few more checks and some defense in depth, because the line can be silently ignored or bypassed.

**Reasoning (checked against code.claude.com/docs/en/sub-agents and /permissions):**
- **Allowlist semantics (verified).** `tools` is an allowlist, and omitting it means the subagent inherits every tool, including MCP tools. If no entry resolves to a tool, Claude Code usually refuses to launch the subagent. A misspelled field name such as `tool:` is silently ignored, which would fall back to inheriting everything. The docs don't say what happens when only some entries are unknown.
- **No write tool is listed (verified).** Read, Grep and Glob can't write. Bash, Edit, Write and NotebookEdit are absent, so the `tools` line closes the main path.
- **Precedence (verified).** The same name in a higher-priority location overrides the file. The order is managed settings, then the `--agents` flag, then `.claude/agents/`, then `~/.claude/agents/`, then plugins. A different `auditor` definition elsewhere (for example from `--agents` or managed settings) would win. Two files in the same `.claude/agents/` tree with the same `name` are resolved by filesystem read order, and `/doctor` reports them.
- **Inheritance and permission modes (verified).** A subagent inherits the parent's `bypassPermissions`, `acceptEdits` or auto mode, and its own `permissionMode` is ignored in that case. This only affects prompting for tools the subagent actually has, so it doesn't add Write to a three-tool allowlist. It does matter if the allowlist ever fails.
- **MCP.** MCP tools are inherited by default only when `tools` is omitted. The docs' MCP table describes `mcp__server__*` entries as ways to add tools, so a three-tool allowlist should exclude them. I didn't find an explicit statement of that, so treat it as inferred.

**Prioritized checklist:**
1. **Confirm the file parses.** Use the exact field name `tools` and valid frontmatter. Run `/agents` or `claude --debug` and look for "does not recognize or apply". This prevents a silent fall back to inheriting all tools (verified).
2. **Add `disallowedTools: Write, Edit, NotebookEdit, Bash` (plus `mcp__*` if no MCP tools are needed).** A denylist is applied first, and a tool in both lists is removed (verified). This stays safe even if someone later edits `tools`.
3. **Add deny rules in `.claude/settings.json` or managed settings.** Use `Edit(**)` and a tool-level deny for Write. These apply session-wide, so they would also block the main session and other agents. That makes them a poor fit unless the whole session should be read-only. Path rules for `Write` or `NotebookEdit` are never consulted, so use `Edit(...)` for paths (verified). Set `permissions.disableBypassPermissionsMode` to `"disable"` (verified).
4. **Check for shadowing definitions.** Look for another `auditor` in `--agents`, managed settings, nested `.claude/agents/` directories, `~/.claude/agents/`, or duplicate files. Consider a unique name.
5. **Decide whether the subagent needs Bash.** If it does, don't rely on the allowlist. Add a PreToolUse hook in the agent's frontmatter that exits 2 on write-like commands, but this is only best-effort. Project-level hooks need workspace trust accepted, and plugin agents ignore `hooks`, `mcpServers` and `permissionMode` (verified). For hard enforcement, enable the sandbox. The docs say deny rules don't cover arbitrary subprocesses such as a Python script (verified).
6. **Use a `PreToolUse` hook on `Edit|Write|NotebookEdit` in user or managed settings** if the guarantee must be airtight against edits to the agent file itself. Anyone with write access to `.claude/agents/auditor.md` can change the `tools` line.

**Risks and unknowns:**
- **Main dependency.** The verdict rests on the file actually loading with the `tools` allowlist applied, and on no higher-priority `auditor` existing.
- **Outside Claude Code.** Another process or user can still modify files, and the agent file itself is writable by the main session.
- **Partly unknown entries.** The docs don't specify the behavior when only some `tools` entries are unresolved.
- **What would change my mind.** A fresh test showing the subagent can call a write-capable tool, or docs saying MCP tools are added alongside an explicit allowlist, would move me to "not sufficient."

**Confidence:** Medium-high. The allowlist, precedence and mode-inheritance facts come straight from the docs. The MCP behavior with an explicit allowlist is inferred, and the partial-unknown-entries case is undocumented.

## R5

Yes. `tools: Read, Grep, Glob` is enough to stop the subagent from modifying files. When `tools` is set, it's an allowlist: the subagent gets only those three tools. Edit, Write, NotebookEdit, Bash, MCP tools and the Agent tool are all unavailable. None of those three can write to disk.

The setup can still fail silently in a few ways, so check these:

1. **Frontmatter has to parse.** The `---` block must be the very first thing in the file, and the key must be exactly `tools` (lowercase). If the key is misspelled or missing, the subagent **inherits every tool** from the main session, including Edit, Write and Bash. That's the main way this goes wrong.
2. **Tool names must match exactly.** A misspelled name (e.g. `grep` instead of `Grep`) is dropped, not reported. That only removes capability, so it's safe, but the subagent may not work as you expect.
3. **Check what it actually loaded.** Run `/agents` and look at the auditor's tool list. Restart the session after editing the file so the new definition is picked up.
4. **Optional extra safeguard.** Newer Claude Code versions support a `disallowedTools` field, so you can name the write tools explicitly as well:
   ```yaml
   ---
   name: auditor
   description: Read-only code auditor
   tools: Read, Grep, Glob
   disallowedTools: Edit, Write, NotebookEdit, Bash
   ---
   ```
   You don't need this if `tools` is correct. It does mean the write tools stay blocked even if someone later widens `tools`.
5. **It only restricts the subagent.** The main agent that calls the auditor keeps its own tools. It could still act on the auditor's findings by editing files itself. If you want to stop that, you need permission rules or hooks in settings, not changes to the agent file.

Don't add Bash "just for running scripts" later. Bash can write files, so adding it removes the guarantee.

## R6

**Yes, that's enough for the subagent itself.** The `tools` field is an allowlist. When it's present, the subagent gets only the tools you list. `Read`, `Grep`, and `Glob` can't change anything on disk, and nothing that can write is included:

- No `Edit`, `Write`, or `NotebookEdit`
- No `Bash` (the big one, since a shell can modify anything)
- No `Agent`, so it can't hand work to a subagent that has write access
- No `Skill`, and no MCP tools. MCP tools are only inherited when you leave `tools` out entirely.

**Things to check so it actually takes effect:**

1. **The frontmatter has to parse.** It needs `---` delimiters at the top of the file, valid YAML, and a `name` and `description` alongside `tools`. If it's malformed, the agent may not load as you intended.
2. **Tool names are case-sensitive.** `read, grep` won't match. Yours look right.
3. **Don't delete the `tools` line later.** Without it, the subagent inherits *every* tool from the main session, including Bash and Edit. That's the most likely way this breaks in the future.
4. **Verify it.** Run `/agents` in that project and confirm the auditor shows only those three tools. Then ask it to create a file as a test; it should report that it has no tool to do that.

**Optional extra safety:**

- Newer Claude Code versions also support `disallowedTools` (a denylist) and `permissionMode` in subagent frontmatter. `disallowedTools: Edit, Write, Bash, NotebookEdit` would be a second guard if someone loosens `tools` later. Check that your version supports it, and confirm with `/agents`.
- `permissions.deny` rules in `.claude/settings.json` give a guarantee at the settings level, but they apply to the whole session, not just this agent. Only use them if nothing in that project should be editing.

**What it doesn't cover:**

- Being read-only doesn't stop the auditor from *reading* sensitive files like `.env` or credentials. If that matters, add `permissions.deny` rules such as `Read(./.env)`.
- It only restricts the auditor. If the main session acts on the auditor's report, the main session can still edit files.

## R7

**Position:** The `tools: Read, Grep, Glob` line is enough, with caveats. Those three tools can't write anything, and the docs say `tools` is a real allowlist. What isn't guaranteed is that the definition actually running is the one you think it is. Fields that silently add or remove tools, shadowing definitions, and edits made during the session can all undermine it.

**Reasoning:**

What the docs confirm (https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/permissions):
- `tools` is an allowlist. The docs' example with `tools: Read, Grep, Glob, Bash` says the subagent "can't edit files, write files, or use any MCP tools." MCP tools only come in if you list them, such as `mcp__server__*`.
- The permissions page classes Read and Grep as "read-only," needing no approval. Running in the background only removes tools; it never adds them.
- Skills can't be used to get around this. A subagent can only call skills through the `Skill` tool, and `Skill` isn't in the list.

Gaps, most likely to matter first:
1. **The frontmatter is silently wrong.** The docs say "Claude Code ignores a field it doesn't recognize without reporting an error," and if `tools` is omitted the subagent "inherits every tool available." So `Tools:`, `allowed-tools:` (the skills field name, an easy mix-up) or YAML that doesn't parse would quietly give the subagent Edit, Write and Bash. Fix: check `claude --debug` and `/agents` to see which tools it actually resolves to.
2. **The `memory` field.** If it's set, the docs say "Read, Write, and Edit tools are automatically enabled so the subagent can manage its memory files." Fix: don't set `memory`. The docs also say it has no effect if auto memory is turned off with `autoMemoryEnabled: false`.
3. **The definition gets replaced or edited.** Same-name agents from managed settings or `--agents` take precedence. Two files with the same name in `.claude/agents/` are resolved "by filesystem read order." Files are watched and reloaded, so if the main conversation, which can edit, rewrites `auditor.md`, "the next delegation uses the updated definition." Fix: put `Edit(.claude/agents/**)` in `permissions.deny`. The docs say `Edit` rules "apply to all built-in tools that edit files," which covers Write too. Add `NotebookEdit` as well, because Read deny rules don't cover it.
4. **Hooks.** Hooks from settings, policy and plugins "all apply inside subagents." A PostToolUse hook that runs a command could write files even though the subagent itself can't. Review those hooks.

Defense in depth (my inference, not confirmed by the docs):
- Add `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell`. The docs say it's applied before `tools`, so it backs things up if `tools` is ever mistyped or deleted.
- A PreToolUse hook in the frontmatter that denies everything except `Read|Grep|Glob` is optional and not reliable. The docs say project-level frontmatter hooks are silently skipped until the folder is trusted.

Things that aren't gaps (inferred): prompt injection can't add tools. `permissionMode`, including bypass, changes whether you get asked for approval, not which tools exist. The subagent can't start other subagents because `Agent` isn't listed. The main agent acting on the auditor's report is outside the subagent's boundary.

**Risks and unknowns:**
- I'm assuming that permission modes never add tools. The docs imply this but don't state it.
- The docs don't say whether `memory` overrides `disallowedTools`, or what happens when only some entries in `tools` resolve.
- I can't see the actual file. If it has `memory:`, a misspelled field name, or a duplicate with the same name, my verdict becomes "not enough."
- If "never modify" includes hooks you've configured or the main agent acting on the report, it's not enough either.

**Confidence:** Medium-high. The main allowlist behaviour and the `memory` exception are quoted from the docs. How the remaining gaps rank, and the mode/tool interaction, are my inference.

## R8

## Think tank: is `tools: Read, Grep, Glob` enough to keep a subagent read-only?
opus, sonnet, sonnet · session effort · identical brief · debate

### Recommendation (3–0)
**Yes, with caveats.** All three panelists agree that `tools` is an enforced allowlist. None of Read, Grep or Glob can write, and Bash, Edit, Write, NotebookEdit and MCP tools are all left out. Running the parent session in `bypassPermissions` or `acceptEdits` doesn't add tools back, because those modes only change prompting for tools the subagent already has. The risk is that the line silently stops applying, not that it's too weak. Checks, ranked:

1. **Spell the key exactly `tools`.** Claude Code ignores a misspelled field such as `tool:` without an error. The agent then behaves as if `tools` were omitted and gets every tool. You can catch this by searching `claude --debug` output for `does not recognize or apply` (needs v2.1.296+). (A, C → B)
2. **Don't add `memory:`.** It automatically enables Read, Write and Edit. (B → A, C)
3. **Make sure your file is the `auditor` that actually loads.** A same-named definition from managed settings or `--agents` takes priority over `.claude/agents/`. Duplicate names in one directory are resolved by filesystem read order. Check in `/agents`, or give the agent a more unique name. (A, B, C)
4. **Optionally add `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, mcp__*`.** It's applied before `tools`, so it guards against someone widening `tools` later. It won't help if the frontmatter is misspelled or fails to parse. (A, B, C)
5. **If "never" must be absolute,** add a control outside the file: OS-level read-only access, a sandbox, or a `git diff` after each audit. Anyone who can edit `auditor.md` can change its tools. (A, B; C → in debate)
6. **YAML that doesn't parse fails closed.** Claude Code skips the file, so the auditor doesn't exist and isn't silently widened. (B → A, C; A had said it fails open and corrected this after checking)

Checked: I read the subagents docs page myself. They confirm the allowlist, and that omitting `tools` means it "inherits every tool available to subagents". They confirm unknown fields are ignored "without reporting an error", with the debug-log search to find them. Their own example says `tools: Read, Grep, Glob, Bash` "can't edit files, write files, or use any MCP tools". They also confirm the precedence order. The `memory` section does say Read, Write and Edit "are automatically enabled". It doesn't say whether that overrides an explicit `tools` list, so assume it does.

### Panel
- **A** (opus): "Sufficient with caveats. `tools: Read, Grep, Glob` is an enforced allowlist, so the subagent has no tool that can change files. Permission modes can't add tools back. The guarantee holds only while three things stay true: this file is the `auditor` that actually loads, the key is spelled `tools`, and no field that grants write tools (`memory:`) is added." Medium-high confidence. In debate, A added the `memory:` point (from B) and corrected its claim that malformed YAML fails open after checking the docs.
- **B** (sonnet): "Sufficient with caveats. `tools: Read, Grep, Glob` is an allowlist of three tools that cannot write, so as long as the line is applied, the subagent has no file-modifying tool. The risk is the line silently not being applied, so the user should verify it and add a redundant denial." High confidence that the line removes write tools, medium that "never" holds without checks. In debate, B moved the misspelled-key check (from C) to the top of its list.
- **C** (sonnet): "Sufficient with caveats. `tools: Read, Grep, Glob` is a real allowlist of three tools that can't write, so it's enough in the normal case. "Never" holds only if the file loads, nothing shadows the name, and no other frontmatter field (especially `memory:`) re-adds write tools." Medium-high confidence. In debate, C added the `memory:` point (from B) and ranked controls outside the file higher (from A).

### Where they split
- **Project-wide `permissions.deny` rules for Edit/Write.** In round 1, B and C suggested these. A rejected them in debate because they apply to the whole session, so they'd also block your main session. They're also redundant when the tools are already absent. C had flagged the session-wide scope itself, and B demoted the item after debate. Only C still lists one, as one option for a control outside the file. This is a judgement about scope, not a factual disagreement.
- **Undocumented edges no one could settle:** what happens when only some tool names are misspelled, and how an inline `mcpServers` field interacts with `tools`. A quick test on your installed version would answer both.

### My take
I started out thinking the line was essentially enough, and that still holds. The panel taught me two specific traps I hadn't named: a misspelled `tools` key fails open silently, and `memory:` adds Write and Edit. For an auditor, I'd keep the file as it is, add the `disallowedTools` line since it costs nothing, and confirm the setup once by opening `/agents` and asking the auditor to create a file. If it refuses because it has no tool to do that, you've confirmed it in your own environment rather than from the docs. I'd skip project-wide deny rules unless you want your whole session read-only.

## R9

## Think tank: is `tools: Read, Grep, Glob` enough to keep a subagent read-only?
opus, sonnet, sonnet · session effort · identical brief · debate

### Recommendation (3–0, two of the three on sonnet)
**Mostly yes, with caveats.** `tools` really is an enforced allowlist, and none of Read, Grep or Glob can write a file. The risk is that the setting you think is in effect isn't the one Claude Code actually uses. The gaps, roughly most likely first:

- **A misspelled key gives the agent every tool.** If the key is `Tools:`, `tool:` or `allowed-tools:`, or the YAML doesn't parse, Claude Code ignores it without any error. With no `tools` field, the agent gets every tool, Write and Edit included. (A, B, C)
- **Another definition with the same name wins.** A same-named `auditor` from managed settings, `--agents`, or a nested or duplicate `.claude/agents/` file replaces yours. (A, B, C)
- **Someone later adds `Bash`.** Bash can write through `>`, `sed -i` or `git checkout`. (B, C)
- **The `memory:` field adds write tools.** The docs say setting it "automatically enables" Read, Write and Edit. They don't say whether that overrides your `tools` list. (A → B, C)
- **The file can be rewritten mid-session.** Agent files reload automatically, so if the main session edits `auditor.md`, the next run uses the edited version. (A → B, C)
- **Hooks still run.** Hooks from your settings or plugins also run inside subagents, so a command hook could write files. (A, C)
- **Inline `mcpServers` is unclear.** The docs don't say whether the allowlist filters MCP servers defined inside the agent file. (C → A, B)

**Fixes the panel agrees on:**
- **Add a backstop in the frontmatter:** `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, Agent, mcp__*`. It's applied before `tools`, so it still protects you if the `tools` line is lost or misspelled. (A, B, C)
- **Leave out `memory`, `mcpServers`, `hooks` and `skills`.** (A → B, C)
- **Check what's actually in effect.** `/agents` shows which definition won and its tools. `claude --debug` reports fields it didn't recognise. Then ask the auditor to create a file and confirm it can't. (A, B, C)

Checked: I read the whole subagents docs page, including the last ~9.5k characters the panelists' fetches cut off. These are all confirmed word for word:
- `tools` is an allowlist, and leaving it out inherits every tool.
- "ignores a field it doesn't recognize without reporting an error".
- `memory` "automatically enabled" Read, Write and Edit. Whether it overrides `tools` is not documented anywhere on the page.
- The name priority order, and that duplicates in one directory resolve "by filesystem read order".
- Settings hooks "apply inside subagents".
- Forks "skip both filters and receive the main conversation's exact tool pool". Fork mode is on by default from v2.1.302 and can be turned off with `Agent(fork)` in `permissions.deny`.

### Panel
- **A** (opus): "My verdict stands: enough with caveats. Read, Grep and Glob can't write, and `tools` is an enforced allowlist. The guarantee breaks if the frontmatter is mis-parsed, if another field adds tools, or if a different or edited definition is the one that actually runs. Neither panelist gave me a new argument or fact that changes this." Medium-high. Didn't move.
- **B** (sonnet): "Enough with caveats. The three listed tools can't modify files, but the line alone isn't a guarantee. Silent failure modes, a `memory:` field, scope overrides, hot-reload of the agent file and forks can all undermine it. For a hard "never", add `disallowedTools` and settings deny rules, and verify." Medium-high, down from high. Same verdict, but it added the `memory` and auto-reload gaps from A after checking the docs. It also dropped its round-1 claim that a bad `tools` line fails safely: that only holds when the key is right and nothing in the list resolves to a real tool.
- **C** (sonnet): "Enough with caveats. `tools: Read, Grep, Glob` is a real allowlist, and none of the three tools writes. The guarantee holds only if nothing else in the file or its environment adds write capability. For a hard guarantee, add `disallowedTools` and settings deny rules, and protect the definition file itself." Medium-high. Same verdict, but it added A's `memory` gap and protecting the agent file itself.

### Where they split
- **How broad the settings deny rule should be.** B and C suggest `permissions.deny` for `Edit` and `Write`. A pointed out that deny rules also apply to the main conversation, so this makes the whole session read-only. A prefers a scoped `Edit(.claude/agents/**)` that only protects the definition file. B and C added that scoped rule in round 2 but kept the broad one too. What settles it is whether you want only the auditor to be read-only, or the whole session.
- **Whether forks matter.** B and C list forks as a bypass. A says a fork is a separate feature, not a way of running `auditor`. The docs support both: forks use the main session's tools and never read your agent definition. That only matters if your requirement covers delegated work in general.
- **`permissionMode: plan` or `dontAsk`.** B and C suggest it as an extra layer. A calls it weak, since the main session's mode overrides it. All agree it does nothing while the agent has no write tools.

### My take
I started out leaning "enough, if the frontmatter parses, and add a settings backstop". The panel kept the first part and moved me on two points:
- **`memory:`** is a real gap I hadn't thought of. I confirmed it's in the docs, and the docs don't say whether it overrides your `tools` list. If your file sets it, assume it's not safe.
- **The backstop.** I side with A. A project-wide `Edit`/`Write` deny would stop your main session from editing too, which you probably don't want. Use `disallowedTools` in the agent file plus the scoped `Edit(.claude/agents/**)` deny.

The project isn't in this directory, so I can't check the file itself. Run `/agents` there to see which tools the auditor actually ends up with, or paste the frontmatter here and I'll check it against these gaps.

## R10

**Position:** Enough with caveats. As written and parsed, `tools: Read, Grep, Glob` gives the subagent no tool that can modify files, because the harness enforces the allowlist. It only holds if that line is actually in effect, and it breaks the moment someone adds Bash or drops the line. I'd add cheap defense-in-depth rather than rely on that one line.

**What the docs confirm.** I read the sub-agents and permissions pages on code.claude.com. The fetch of the sub-agents page was truncated, so I didn't read its last ~9.5k characters.
- **Allowlist:** `tools` lists the tools the subagent can use. If it's omitted, the subagent "inherits every tool available to subagents", which includes Write, Edit and MCP tools.
- **Read-only example:** The docs' read-only example is `tools: Read, Grep, Glob`. Custom subagents can write only if `tools` includes Write or Edit, or if they inherit those tools.
- **`Agent` and `Skill`:** Neither is in your list, so the auditor can't spawn other agents. The docs say to omit `Skill` from `tools` to stop skill invocation.
- **`disallowedTools`:** It is applied first, and then `tools` is resolved against what remains. A tool listed in both is removed.
- **`permissionMode`:** A parent in `bypassPermissions`, `acceptEdits` or auto mode overrides the subagent's mode. That doesn't matter here, because the auditor has no write tool for the mode to approve.
- **Settings deny rules:** The docs say a Bash deny rule in `permissions.deny` "applies to the main conversation and to subagents". I'm inferring that `Edit` and `Write` deny rules behave the same way.

**Gaps, most likely to matter first**
1. **Drift or fail-open.** This is the most likely failure. Someone adds `Bash` to run tests or `git diff`, and the "never modifies" guarantee is gone, because Bash can run `sed -i`, `>`, or `git checkout`. Likewise, a misspelled key such as `tool:` or `Tools:` leaves `tools` omitted, so the agent inherits everything. The docs confirm omission means inheritance. That a misspelled key is treated as omission is my inference. An unresolvable list fails closed, because the docs say a list with no resolvable entries usually fails to launch.
2. **Same-name override.** A definition with the same name at another scope, or one passed with `--agents`, could replace yours. The scope priority is my recollection, not something I confirmed. Check with `/agents` which definition is active.
3. **Other agents.** The parent conversation or the built-in general-purpose agent can still edit files. If the requirement is "the audit process never changes files" rather than "this one agent never does", the allowlist doesn't cover it.
4. **Prompt text.** Body text such as "don't modify files" is not enforcement. It only matters if a write-capable tool exists.
5. **Read, Grep and Glob side effects.** I found none, so I'd treat this as not a real gap.

**Fixes**
- **Frontmatter:** Add `disallowedTools: Write, Edit, NotebookEdit, Bash, Agent, Skill`. Add `permissionMode: plan` or `dontAsk`, so anything not pre-approved is denied rather than prompted.
- **Settings (`.claude/settings.json`):** Add `permissions.deny` entries for `Edit` and `Write`. Put them in managed settings if you need them to be un-overridable. Run `/agents` and `/permissions` to confirm what is actually in effect.
- **If Bash is ever required:** Add a `PreToolUse` hook that allows only specific read-only commands, with exit code 2 to block everything else. The docs show this for a read-only SQL validator. Frontmatter hooks need folder trust to run. Add OS-level sandboxing as well, since the permissions page says deny rules don't match a program by path or inside `sh -c`.
- **Verification:** Ask the auditor to create a file and confirm it can't. Check the agent loads and lists exactly three tools.

**Risks and unknowns:** My verdict depends on the file parsing as intended and being the active definition. I couldn't see the file, so I took the question to mean this one subagent's tool surface. If MCP tools can leak into an allowlisted subagent, that would change my answer. The docs say MCP tools are included via `tools` entries such as `mcp__server__*`, which implies they are not included otherwise. I'd confirm that.

**Confidence:** High that the allowlist is sufficient when correctly parsed. Medium on the override and misspelled-key edge cases, which are inferred.

Sources: https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/permissions

## R11

**Position:** The `tools` line is sufficient, with caveats. `tools: Read, Grep, Glob` is a strict allowlist, so this subagent gets no Edit, Write, NotebookEdit, Bash/PowerShell or MCP tools. Permission modes cannot add them back. The guarantee only holds if this exact file is the definition that loads and its frontmatter parses. That is what the user should check. They don't need to add much.

**Reasoning (all checked against https://code.claude.com/docs/en/sub-agents unless marked otherwise):**
- **Allowlist semantics.** The docs say `tools` restricts the subagent's tool pool. Their own example is nearly this one: `tools: Read, Grep, Glob, Bash` means "the subagent can't edit files, write files, or use any MCP tools". Without Bash, the user's version is stricter still. Read, Grep and Glob cannot change files.
- **MCP.** MCP tools are inherited only when `tools` is omitted. With an allowlist, they come in only if listed (for example `mcp__github__*`). The `mcpServers` field supplies servers, but `tools` still filters them.
- **Permission modes.** If the parent session is in `bypassPermissions`, `acceptEdits` or auto mode, the subagent inherits that mode. Modes control whether a call needs approval. They don't grant tools that aren't in the pool, so they don't widen this agent.
- **Background filter.** Background runs only remove built-in tools, never add them.

**What to check or add, in priority order:**
1. **Make sure this file is the one that runs (verified).** If two definitions share a name, the higher-priority one wins: managed settings, then `--agents`, then `.claude/agents/`, then `~/.claude/agents/`, then plugins. Nested `.claude/agents/` directories resolve to the one closest to the working directory. Two files with the same `name` in one directory are picked "by filesystem read order". Failure prevented: a differently-scoped `auditor` with Edit or Bash runs instead. Fix: give it a unique `name` and confirm in `/agents` that it resolves to this file and these tools.
2. **Keep the frontmatter valid and the allowlist tight (verified).** If `tools` is omitted, the subagent "inherits every tool available to subagents", including Write, Edit, Bash and every MCP tool. Malformed YAML, a mistyped key or a later edit that drops the line fails open. If no entry resolves, launch "usually" fails. I did not verify what happens when YAML is malformed or only some names resolve. Fix: treat the file as security-relevant, review it, and never add Bash, PowerShell, `mcp__*`, Skill or Agent. Adding `disallowedTools: Write, Edit, NotebookEdit, Bash, PowerShell, mcp__*` is cheap redundancy against someone later widening `tools`. It does not help if the whole frontmatter fails to parse.
3. **Back it up outside the agent file if "never" really means never (inferred).** Frontmatter hooks are skipped until the workspace is trusted, and hooks in the same file share its failure modes. Stronger options are OS or sandbox-level read-only access, or a `git status` / diff check after each audit.
4. **Watch for side channels (not verified).** The subagent's final report goes back to the parent, which can still edit files. Project or user settings hooks run shell commands on tool events and could modify files while the auditor is working. That isn't the auditor writing, but it matters if the requirement is "no file changes during audits."

**Risks and unknowns:** My verdict rests on two documented facts: an explicit `tools` list is an allowlist that excludes MCP, and permission modes don't add tools. Precedence rules, the inherit-all default and the background filter were checked on the docs page. I'd change my view if the parsing behaviour for partly invalid entries turned out to fail open, or if a doc or changelog showed a path that adds tools to an allowlisted subagent. The errors page's "zero tools" section was truncated when I fetched it.

**Confidence:** Medium-high. The main mechanism is explicitly documented. The remaining risk is configuration (shadowing, bad frontmatter), not the `tools` semantics.
