# Installing children and reconciling their state

Use this when installing a generated child, reconciling a child's state before use, repairing a hard defect after installation, or validating several children together. Diagnosing a soft defect does not need this file.

## States

Keep these claims separate:

- **Artifact:** the child exists and has passed its recorded structural and behavioral validation.
- **Installed:** the child sits in a folder the host discovers, but discovery or explicit invocation has not been observed.
- **Operational:** the child was seen in the host's skill list and an explicit invocation worked in a fresh session.
- **Blocked:** the child stays installed, but current evidence forbids the affected use until repair and regression checks pass.

An empty `host_adoptions` list in a record means artifact only. Copying files into a skill folder establishes at most `installed`. A record without `generated_skill` cannot carry host entries or catalog-routing evidence.

## Records

Find records with the [record location rules](state-policy.md#portable-resource-record-location). Bind records and learnings by `slug` plus `canonical_url`, and by `package_id` when present. A same-named fork, mirror or package inherits nothing. Use only schema-version 3 records; a record that does not satisfy the current contract goes to `repair/reconcile`. Never invent missing evidence.

## Pre-use reconciliation

[Child usage](child-usage.md) owns the commands and how to act on each result. This section covers the full sequence that a `required` policy, or an escalation from `conditional`, runs:

1. Run the child's installed-state check.
2. Compare the observed identity and version/commit/source state with the child's `resource.yaml`.
3. Load the matching record and the resource's learnings, if they exist.
4. Re-check adverse learnings against current evidence; a learning points at what to check but never decides alone.
5. Stop the affected use and enter `repair/reconcile` when the installed identity differs, a current block applies, a material adverse observation is confirmed, or a hard defect makes correctness, security, identity, version or verification unreliable.

Record `matched` only after these checks complete. Use `mismatched`, `blocked` or `unknown` truthfully otherwise.

Escalate a `conditional` child to this sequence when the status query returns `BLOCKED` or `MISMATCH`, the pin or lock is missing or mismatched, the task is an adoption, upgrade or authorized repair, the integrity check fails, or diagnosis finds a hard defect. A soft defect alone does not trigger it.

`HEALTHY` requires the exact identity and version, a usable reconciliation state (`matched` or justified `not-applicable`), no recorded block, no failed verification, and no adverse host entry for this copy. A `blocked` host entry for the same skill name blocks every copy, because the defect is in the content. `disabled`, `removed`, `failed` and `unavailable` apply only to the copy at that location. A nonempty legacy `blocked_use_or_version` is treated as `BLOCKED`. Use repeated `--pair` arguments to check a batch.

## Install a child

Installing changes the host, so it is separate from validating the artifact.

1. Resolve the project root first. An unknown project leaves installation pending; never fall back to a user-wide folder silently.
2. Child generation and installation are opt-in under [adoption policy](adoption-policy.md#scope-and-autonomy). Once the user has asked for a child, installing it in the project's skill folder needs no second confirmation. A user-wide install needs an explicit request.
3. Before writing, inspect any existing folder at the destination. If it is the same managed child, update it through the guarded flow. If it is unrelated or ambiguous, stop and report the collision; never overwrite, merge or rename someone else's skill.
4. Record each piece of host evidence you actually observed.
5. Mark the child `operational` only after you see it listed and an explicit invocation works.
6. Run `scripts/validate_skill_catalog.py --host claude` over the children visible to that host before finishing. Add materially overlapping non-generated skills with `--routing-competitor`.
7. When the catalog reports an overlap cluster, run independent routing tasks before calling catalog routing `verified`.

If the host cannot show enough evidence, keep the strongest truthful state, such as `installed` or `unavailable`.

## Host locations

| Host | Project install | User install | Instructions file it loads | Explicit invocation |
| --- | --- | --- | --- | --- |
| Claude Code | `<project>/.claude/skills/<name>/` | `~/.claude/skills/<name>/` | `CLAUDE.md` (and files it imports with `@path`) | `/<name>` |
| Claude Code plugin | the plugin's `skills/<name>/` (this repository's marketplace) | — | — | `/osaskills:<name>` |
| Cowork / claude.ai | upload the skill folder as a zip, or install the plugin | — | — | ask for the skill by name |

- Claude Code discovers project skills from `.claude/skills/` in the working directory, and from nested `.claude/skills/` folders when it works with files below them. Check current Claude Code documentation when the exact discovery rule matters.
- Skills installed through the Skills CLI (`npx skills add … --agent claude-code`) may be symlinks to a canonical copy; edit and guard the real folder.
- To stop a skill from loading automatically, set `disable-model-invocation: true` in its frontmatter; it can still be invoked with `/<name>`.
- Cowork and claude.ai run scripts in a sandbox or Linux VM. Python, `uv`, PyYAML, the parent skill, the project files or network access may all be missing. Children must then run in advisory mode (see [child usage](child-usage.md)), and an install there can be at most `installed` unless you observe the skill being listed and invoked.

Confirm the install by checking that the skill appears in `/skills` (or the host's skill list) in a fresh session and that `/<name>` loads it. Automatic selection from the description is separate catalog evidence.

## One editable copy per scope

Stage a new or repaired child outside any skill folder, for example `<project>/.roblox-resources/artifacts/skills/<name>/`, then move it into `<project>/.claude/skills/<name>/`. Do not leave two editable copies in the same scope. Record the installed location in `host_adoptions`.

An explicit user-wide request may stage at `~/.roblox-resources/artifacts/skills/<name>/` and install at `~/.claude/skills/<name>/`. Reuse that child across projects in that scope; being visible everywhere does not adopt the resource in any project. Leave existing installs where they are unless moving them is separately authorized.

A later repair edits the installed child in place through [guarded correction](on-demand-maintenance.md#guarded-correction-and-recovery). A copy installed elsewhere (another project or the user folder) is updated separately and only when authorized.

## Defects after installation

Capture the task, host, project, installed identity and version, expected and observed behavior, smallest reproduction, workaround and proposed fix, then classify the defect before changing state.

- **Hard:** mark the matching host entries `blocked`, invalidate the affected behavioral and routing evidence, and enter the [repair loop](repair-loop.md) plus reconciliation.
- **Soft, diagnosis only:** safe reversible work may continue. Report the defect before finishing; do not invalidate unrelated evidence.
- **Soft, authorized repair:** keep the host entry `installed` while the child is repaired, invalidate only the evidence the edit affects, and restore `operational` only after fresh validation and a fresh explicit invocation.

A repaired copy does not update other installed copies automatically. A local-only update the user authorized may finish as `installed` with discovery and invocation recorded as unavailable; it cannot claim `operational`. An interrupted or failed update stays guarded until recovered or completed.

## Catalog coherence

Run `scripts/validate_skill_catalog.py` whenever a child is added, refreshed, repaired or installed. Positional paths are generated children and get full validation. `--routing-competitor <path>` adds a non-generated skill (for example `structure-roblox-projects`) for overlap detection only. Store the printed fingerprint with routing evidence; changing any member of the tested set invalidates it.

Static validation finds overlap risk; it does not prove which skill the host selects. For each overlap cluster, test one task per child, one per competing skill, and one simpler task that should select neither (Test J in the [testing protocol](testing-protocol.md)).
