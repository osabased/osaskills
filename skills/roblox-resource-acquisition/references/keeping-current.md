# Keeping this skill current

[`versions.json`](../versions.json) lists every library this skill's catalog pins: its source, the version the guidance was last reviewed against (`reviewed`, which is also the library skill's pin), and the files that depend on it. The guidance is updated on demand, not on a schedule. This is about the skills' own content. A user's project keeps its pins unless the user asks to upgrade (see [adopting](adopting.md#upgrade-replace-or-remove)).

## Check

Only when a task depends on a library skill's version-specific guidance, compare the version the project declares with the skill's pin. `clone_children.py --status` reports it as `declared` ([library skills](library-skills.md#clone-into-a-project)), and in a plugin install the session hook names cloned skills whose pin the project contradicts.

- **Same version** (`PASS`): trust the guidance.
- **Project newer:** check the release notes between the two versions for the API and behavior the task uses, follow the newer behavior, and tell the user in one line.
- **Project older:** confirm the API and behavior the task uses at the pinned version, and warn the user.
- **Nothing to compare** (`UNAVAILABLE`, such as a vendored copy or a Studio plugin file): use the version of the project's copy as the baseline. If the project has none, check the claims the task uses against the current docs.

Never change the project's pin to fit the skill.

`scripts/check_updates.py` lists libraries whose latest stable release is newer than `reviewed` (Python 3.9+ and network access; exit 0 means all current, 1 something newer, 2 nothing checked). Run it when you need that, such as before an update. A weekly workflow runs it for the maintainer's tracking issue.

## Update

Update only on demand: when the user asks ("update janitor"), or when you offer it in one line after a task whose check found a gap and the user agrees. Target the project's version or one the user names, and never lower `reviewed`.

Only a full review sets `reviewed` to a version X: the release notes up to X checked against every file listed for the item. A fix to a single claim goes in its own PR titled `Fix <name>: <claim>` and leaves `reviewed`, `reviewed_on` and the skill's pin unchanged.

You can update the skill when the `osabased/osaskills` repository is reachable with push access: `gh repo view osabased/osaskills --json viewerPermission` reports `WRITE`, `MAINTAIN` or `ADMIN`. Without that, report the gap and suggest updating the installed plugin or skills later; installed copies get fixes from the repository.

Do one item (or one group of companions, such as the four Nevermore packages), or one fix, per pull request:

1. **Skip duplicates.** `gh pr list --repo osabased/osaskills --state open --search "<name> in:title"` lists open `Update <name>` and `Fix <name>` PRs. Stop if one already does this work: an update to the same or a later version, or a fix to the same claim. An update and a fix don't block each other; name the other PR in yours.
2. **Work outside the user's checkout.** If you're inside an osaskills clone, `git worktree add <temp-dir> -b update/<id>-<version> origin/main` (after `git fetch`; a fix: `fix/<id>-<slug>`). Otherwise `gh repo clone osabased/osaskills <temp-dir>` and branch there. Never edit the user's working tree for this.
3. **Read what changed.** Read the release notes or changelog for every version between `reviewed` and the target, or for a fix, those that bear on the claim. Where those are thin, diff the source between the two tags. Note breaking changes, new or removed API, behavior changes, and fixes to anything the guidance warns about.
4. **Update the library skill** (`files` in `versions.json`). A fix changes only its claim and leaves `resource.yaml` alone:
   - `resource.yaml`:
     - `selector` value (for commit pins, resolve the new tag to its full commit and, for pesde git, the tree);
     - `release_commit`;
     - `source_review_date`;
     - companion versions, and for npm the reviewed `archive_url` and `archive_integrity`;
     - for an asset, `asset_sha256` of the new release file.
   - `SKILL.md`: the pinned version and the `## Check the pin` entries (the validator fails until they state the new pin), the Core API table, the example and the gotchas, so they match the new source. Remove gotchas the release fixed and add new ones.
   - Any affected `references/*.md`.
   - Volatile facts that drift between releases: Blink's unreliable-payload byte limit (1000 bytes at 0.18.9) and the `pesde.lock` format the pin check reads (format 2).
   - The pin in the [catalog table](library-skills.md) and the repository `README.md` table.
5. **Verify.**
   - Run `scripts/validate_skill.py libraries/roblox-<lib>`.
   - Run this skill's tests (`python -m pytest -q` in this folder).
   - Make a fixture project in the temporary directory whose manifest and lock pin the new version, and confirm `scripts/clone_children.py --project FIXTURE --status` reports the skill's `declared` as `PASS`.
   - When the API or behavior changed, give a fresh subagent a realistic task with the updated skill and check that it uses the new API correctly.
6. **Record it.** Add an entry dated today under this skill in `CHANGELOG.md` at the repository root. After a full review, also set `reviewed` and `reviewed_on` in `versions.json`; a fix leaves both unchanged.
7. **Open the PR** with `gh pr create`. Use the title `Update <name> to <version>` or `Fix <name>: <claim>` and include in the body:
   - the old and new versions with release links (for a fix, the version the claim was checked at);
   - what changed upstream that matters;
   - what you changed;
   - what you verified;
   - anything you couldn't verify.

If the release breaks the guidance in ways you can't resolve with confidence, or a check fails, open the PR as a draft and list the open questions instead of guessing. A new major version always gets a fresh source review, not just a version bump.

Remove the temporary worktree or clone when done. Once merged, installed plugin copies pick the change up on their next plugin update; the plugin version follows the repository's commits, so no version bump is needed. A project's clone of the skill picks it up only when re-cloned: after the plugin update, `--status` reports the clone as `stale` and the session hook names it (see [cloning](library-skills.md#clone-into-a-project)).
