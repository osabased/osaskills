# Checks, guards, hooks and CI

Use when making a project agent-ready, adding or changing its check command, a guard, a hook or CI. Claude Code mechanics come first; the last section says what carries over to other agents. Size it to the project: a solo prototype may need only the check command and a Stop hook.

## One check command

One script runs everything static, in this order, and stops at the first failure. If the project already has one (look in `scripts/`, the README and CI config), extend it rather than adding a second:

1. **Restore:** `rokit install`, then the package manager's locked install (`wally install` or `pesde install --locked`).
2. **Guards** ([below](#guards)).
3. **Codegen:** regenerate generated modules (networking, types) so the rest checks fresh output.
4. **Tests** that run offline ([verification](verification.md)).
5. **Format** (`stylua --check`), **lint** (`selene`), **types** (`luau-lsp analyze` with the sourcemap and definitions). Flags: [tooling](tooling.md).
6. **Build** each project file, then check the built place's **topology** ([Rojo](rojo.md#check-the-built-place)).

Output is for an agent whose context is the bottleneck: one line per step (`ok   format (2s)` or `FAIL types (9s)`), then only the failing step's last 40 lines, with the full log written to a file. Under `CI`, print the failing step in full. A passing run should be about ten lines.

- Allowlist the command in `.claude/settings.json` `permissions.allow` so an agent can run it without a prompt.
- Put `~/.rokit/bin` first on `PATH` inside the script, so a globally installed tool of another version doesn't win.
- On Windows, run it with Git Bash. The `bash` that PowerShell finds can be WSL, which lacks the Rokit tools; say so in `CLAUDE.md`.
- When every step passes, write a fingerprint of the files the check reads (content hashes of tracked and untracked files under the checked paths). The hooks below skip a tree that already passed.

## Guards

A guard is a check step that enforces one project rule. Add one only when breaking the rule is:

- **permanent:** saved-data identity, such as the DataStore name, a ProfileStore key prefix or store index, or a data bundle's mode. Changing one on a live game hides every existing player's data.
- **a security hole:** client-to-server entry points the project has banned (for example a networking library's client-to-server events when its receive path has a known flaw), or secrets in replicated containers.
- **silent:** nothing else would notice. A startup script in the wrong container or a second one, dev content in the release build, a lost `servePlaceIds` lock, a file missing `--!strict`, a require that bypasses a typed wrapper.

Style, library preferences and patterns stay in the guide, where they can change without fighting a check.

- **Identity literals:** keep a copy of the exact lines (store name, key prefix) in the guard and fail on any difference. Changing one on purpose then takes two edits, which makes it deliberate.
- **Library-coupled guards are version-pinned.** A guard that reads a library's files or bans one of its features was reviewed against one version. Read the version from the lockfile or a versioned install path, and fail with "reviewed against 0.18.9, found 0.19.0: re-review this guard" when it differs or the file it inspects is missing. A guard that silently passes after the library moves is worse than none.
- **Messages** name the rule, the file and line, and how to change it on purpose.
- **Break-test each guard once:** make the violation, confirm the check fails with that message, revert.
- **List the guards in one place,** the guide or the guard script's header, and link to it rather than repeating the list.

## Hooks and CI

| Hook | Does | Notes |
| --- | --- | --- |
| Claude Code `PostToolUse`, matcher `Edit\|Write` | Formats the written file (`stylua --respect-ignores <file>` for `.luau`) | Never blocks; a format failure shows up in the check |
| Claude Code `Stop` | Exits 0 at once when the hook input has `"stop_hook_active": true`. Otherwise runs the check when checked paths changed and the fingerprint is stale, and on failure prints `{"decision":"block","reason":"<check output>"}` so the agent keeps working | Without that early exit, a failure the agent can't fix blocks every stop until Claude Code's continuation cap. Set the hook `timeout` above the check's run time |
| Git `pre-push` | Runs the check unless the fingerprint matches | Install with `git config core.hooksPath scripts/hooks` once per clone; say so in the README |

- Commit `.claude/settings.json` (hooks and allowlist) so every session gets them; personal settings go in `.claude/settings.local.json`. Hook commands reference scripts through `$CLAUDE_PROJECT_DIR`.
- **CI** runs the same command with `CI=1` on push and pull request, installing tools from the Rokit manifest with a pinned setup action (for example `CompeyDev/setup-rokit` at a release tag). Studio rungs can't run in CI; the guide says which checks are local only.
- **Fresh and cloud sessions** start from a clean checkout: the restore step must install everything the check needs from committed manifests, and skills the project relies on must be committed under `.claude/skills/`, since user and plugin skills aren't there.

Other agents don't read `.claude/settings.json`, but the check script, git hooks and CI apply to them unchanged, and an `AGENTS.md` can point to the same guide.

## Sources

- Claude Code [hooks](https://code.claude.com/docs/en/hooks) and [settings](https://code.claude.com/docs/en/settings)
- [Rokit](https://github.com/rojo-rbx/rokit), [setup-rokit](https://github.com/CompeyDev/setup-rokit)
