# Keeping this skill current

This skill and its catalog of library skills track the latest stable release of every library they pin. [`versions.json`](../versions.json) lists each one: its source, the version the guidance was last reviewed against (`reviewed`), and the files that depend on it. This is about the skills' own content. A user's project keeps its pins unless the user asks to upgrade (see [adopting](adopting.md#upgrade-replace-or-remove)).

## Check

Run once per session from this skill's folder, before relying on version-specific guidance. Results are cached for a day, so repeat runs are instant:

```sh
python scripts/check_updates.py
```

It needs only Python 3.9+ and network access. It reports minor and major releases; a release that only bumps the patch number isn't reported. Exit 0 means everything is current, 1 means something is outdated, and 2 means nothing could be checked. If it can't run (no Python, no network), carry on and don't mention it unless the task depends on a version.

In a plugin install, a session-start hook runs the same check and adds an "osaskills freshness check" note to the session when something is outdated. When that note is present, don't run the script; treat the note as its output.

When an item is outdated:

- If the current task uses it (for example, it uses Janitor and Janitor has a newer release), say so before using the guidance. Then use the project's pinned version as usual; the project's pin is what's installed.
- Otherwise don't mention it.

After the task, offer in one sentence to update the skill for the items you mentioned. Update it, as below, only when the user asks; never start update work or open a pull request unasked.

## Update

You can update the skill when the `osabased/osaskills` repository is reachable with push access: `gh repo view osabased/osaskills --json viewerPermission` reports `WRITE`, `MAINTAIN` or `ADMIN`. Without that, report the outdated items and suggest updating the installed plugin or skills later; installed copies get fixes from the repository.

Do one item (or one group of companions, such as the four Nevermore packages) per pull request:

1. **Skip duplicates.** `gh pr list --repo osabased/osaskills --state open --search "update <id>"`. If a PR already covers the item, stop.
2. **Work outside the user's checkout.** If you're inside an osaskills clone, `git worktree add <temp-dir> -b update/<id>-<version> origin/main` (after `git fetch`). Otherwise `gh repo clone osabased/osaskills <temp-dir>` and branch there. Never edit the user's working tree for this.
3. **Read what changed.** Read the release notes or changelog for every version between `reviewed` and the latest. Where those are thin, diff the source between the two tags. Note breaking changes, new or removed API, behavior changes, and fixes to anything the guidance warns about.
4. **Update the library skill** (`files` in `versions.json`):
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
6. **Record it.** Set `reviewed` and `reviewed_on` in `versions.json`, and add an entry dated today under this skill in `CHANGELOG.md` at the repository root.
7. **Open the PR** with `gh pr create`. Use the title `Update <name> to <version>` and include in the body:
   - the old and new versions with release links;
   - what changed upstream that matters;
   - what you changed;
   - what you verified;
   - anything you couldn't verify.

If the release breaks the guidance in ways you can't resolve with confidence, or a check fails, open the PR as a draft and list the open questions instead of guessing. A new major version always gets a fresh source review, not just a version bump.

Remove the temporary worktree or clone when done. Once merged, installed plugin copies pick the change up on their next plugin update; the plugin version follows the repository's commits, so no version bump is needed. A project's clone of the skill picks it up only when re-cloned: after the plugin update, `--status` reports the clone as `stale` and the session hook names it (see [cloning](library-skills.md#clone-into-a-project)).
