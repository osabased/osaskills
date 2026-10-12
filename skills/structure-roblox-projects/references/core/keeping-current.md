# Keeping this skill current

This skill tracks the latest stable release of every tool it describes. [`versions.json`](../../versions.json) lists each one: its source, the version the guidance was last reviewed against (`reviewed`), and the files that depend on it. This is about the skill's own content. A user's project keeps its tool pins (for example in `rokit.toml`) unless the user asks to upgrade.

## Check

Run once per session, before relying on version-specific guidance. Results are cached for a day, so repeat runs are instant:

```sh
python "SKILL_DIR/scripts/check_updates.py"
```

It needs only Python 3.9+ and network access. Exit 0 means everything is current, 1 means something is outdated, and 2 means nothing could be checked. If it can't run, carry on and don't mention it unless the task depends on a version.

In a plugin install, a session-start hook runs the same check and adds an "osaskills freshness check" note to the session when something is outdated; treat that note like this script's output.

When an item is outdated:

- If the current task depends on it (for example, a Rojo question while Rojo has a newer release), say so before using version-specific guidance. Check the claim against the project's actual pinned version.
- Otherwise finish the user's task first, then mention the outdated items in one line.

Then update the skill, as below, when you can. Don't hold up the user's task for it.

## Update

You can update the skill when the `osabased/osaskills` repository is reachable with push access: `gh repo view osabased/osaskills --json viewerPermission` reports `WRITE`, `MAINTAIN` or `ADMIN`. Without that, report the outdated items and suggest updating the installed plugin or skill later.

Do one tool per pull request:

1. **Skip duplicates.** `gh pr list --repo osabased/osaskills --state open --search "update <id>"`. If a PR already covers the tool, stop.
2. **Work outside the user's checkout.** If you're inside an osaskills clone, `git fetch` and `git worktree add <temp-dir> -b update/<id>-<version> origin/main`. Otherwise `gh repo clone osabased/osaskills <temp-dir>` and branch there. Never edit the user's working tree for this.
3. **Read what changed.** Read the release notes for every version between `reviewed` and the latest. Note new or removed commands and flags, changed defaults, new config fields, deprecations, and fixes to anything the guidance warns about.
4. **Update the files** listed for the tool (`files` relative to this skill, `repo_files` relative to the repository root):
   - version-specific claims, commands and flags;
   - "verified on" notes;
   - links to new docs.

   If a release changes nothing the guidance says, only the manifest changes.
5. **Verify with the real tool** where the skill has a test for it.
   - **Rojo:** download the new release into the temporary directory, put it first on `PATH`, and run `python -m pytest -q tests`. The real-Rojo tests must run, not skip.
   - **Other tools:** run the specific commands the guidance documents (for example `stylua --check`, or `selene` with `roblox-std-source = "pinned"`) in a scratch project.
   - Say what you could not run.
6. **ModuleLoader** is the fixed SSA compatibility contract. Follow [migration and upgrade](../ssa/ssa-bootstrap.md#migration-and-upgrade) in full before changing its pin:
   - API, discovery defaults, lifecycle order and failure behavior;
   - the release asset's SHA-256 and the license.

   A new major version needs a fresh review of every rule in [`ssa.md`](../ssa/ssa.md).
7. **Record it.** Set `reviewed` and `reviewed_on` in `versions.json`.
8. **Open the PR** with `gh pr create`. Use the title `Update <name> to <version>` and include in the body:
   - the old and new versions with release links;
   - what changed upstream that matters;
   - what you changed;
   - what you verified;
   - anything you couldn't verify.

If a check fails or the release changes behavior you can't resolve with confidence, open a draft PR that lists the open questions instead of guessing.

Remove the temporary worktree or clone when done. Once merged, installed plugin copies pick the change up on their next plugin update; the plugin version follows the repository's commits, so no version bump is needed.
