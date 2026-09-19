# Operational Child Lifecycle

Use this reference when adopting a generated child, reconciling state before use, repairing a hard post-adoption defect or an authorized child artifact, or validating a multi-child catalog. Soft repair diagnosis alone does not require this lifecycle branch.

## States

Keep these claims separate:

- **Artifact:** the generated child exists and has its recorded structural and behavioral validation.
- **Installed:** the child occupies a host-recognized location, but operational checks are incomplete.
- **Operational:** every host-applicable installation, registration, discovery, and enablement check is confirmed, and explicit activation passed.
- **Blocked:** the child remains installed, but current evidence prohibits the affected use until repair and regression checks pass.

An empty `host_adoptions` list means artifact only. Placement in a host discovery path establishes at most `installed`; it never establishes `operational` by itself. A record with no `generated_skill` cannot carry host adoption entries or completed/unavailable/failed catalog-routing evidence because there is no child for that lifecycle state to describe.

## Portable resource records

Resolve matching resource records using the canonical [portable resource-record location](state-policy.md#portable-resource-record-location) policy.

Bind records and learnings by `slug` plus `canonical_url`, and by `package_id` when present. A same-named fork, mirror, or package does not inherit state.

Use only schema-version 3 records. A record that does not satisfy the current contract must enter `repair/reconcile`; do not invent missing lifecycle or project-use evidence.

## Pre-use reconciliation

Every generated child declares its reconciliation policy:

- **required:** every version-sensitive use must reconcile independently drifting installed state with parent lifecycle evidence before proceeding;
- **conditional:** ordinary use can cheaply confirm the declared pin plus its lock/header counterpart, while a canonical verifier provides the deferred installed-integrity gate before completion;
- **not-applicable:** the installation mechanism fixes an immutable reviewed state, or the documented behavior is demonstrably insensitive to independently drifting state. Record the concrete reason.

When reconciliation is required:

1. Run the child's resource-specific installed-state check.
2. Compare the observed canonical identity and version/commit/source state with the child's provenance.
3. Load matching schema-version 3 resource records and resource-bound learnings.
4. Re-check adverse learnings against current evidence; a learning directs the check but never decides it alone.
5. Stop the affected use and invoke `roblox-resource-acquisition` in `repair/reconcile` mode when the installed identity differs, installed state is unknown or mismatched, a current block applies, a material adverse observation remains unresolved, or an instruction defect is hard because correctness, security, identity, version, or verification is unreliable.

Record `matched` only after applicable installed-state and parent-state checks complete. Use `mismatched`, `blocked`, or `unknown` truthfully when they do not.

When reconciliation is conditional:

1. Follow the child's **Common path** and confirm only its declared project pin plus the named lockfile or generated-version header.
2. If they match, run `scripts/check_resource_status.py --pair <child-skill-directory> <matching-record.yaml>`. This read-only hot path reads the child's provenance labels and only the record fields needed for schema, exact slug/canonical/package identity, reviewed version/state, block, reconciliation, verification, and matching-host status. It does not inspect skill-validation/resource-proof evidence, load learnings, or execute recorded commands. Proceed only on `HEALTHY`, then run the child's named integrity gate before task completion and require its documented pass condition.
3. Escalate to the full required-policy sequence above when the query returns `BLOCKED` or `UNKNOWN`; the declaration or lock/header is missing or mismatched; the task is adoption, upgrade, or an authorized repair that invalidates evidence; the verifier fails or reports drift; or repair diagnosis classifies a defect as hard.
4. On escalation, stop version-sensitive work until the full sequence resolves or truthfully records the mismatch/block.

A soft instruction defect still activates the parent repair interrupt, but it does not automatically activate this full state sequence. Diagnose and surface its reproduction, safe workaround, and durable correction first; enter reconciliation only if diagnosis finds a hard/state trigger or an authorized edit invalidates lifecycle evidence.

The query accepts only a matching schema-version 3 record. `HEALTHY` requires exact current identity/version, a known usable reconciliation state (`matched` or justified `not-applicable`), no nonempty block, no failed verification, and no blocked, disabled, removed, failed, or unavailable adoption that matches the child location. Missing/malformed records, identity/version mismatches, and `unknown`/`mismatched` reconciliation are `UNKNOWN`, never healthy. A nonempty legacy `blocked_use_or_version` is conservatively `BLOCKED`; do not infer a narrower or cleared scope from its prose. Full record evidence and learnings remain reconciliation inputs rather than ambient prerequisites for a healthy conditional task. Use repeated `--pair` arguments for a project verification batch; the command exits nonzero if any pair is blocked or unknown.

## Adoption gate

Host mutation is a separate gate after artifact validation.

1. Detect the host and its supported skill locations, registration mechanism, enablement control, discovery surface, and explicit invocation mechanism.
2. For project-local children, read [project-adoption.md](project-adoption.md) and resolve the skill scope before selecting the host path.
3. Present the exact target and mutation when host adoption is not already authorized by the surrounding project adoption request/policy.
4. Install, update, enable, disable, or remove only after explicit user authorization or an explicit project policy.
5. Record each available evidence facet rather than inferring unsupported host behavior.
6. Mark the child `operational` only when all host-applicable facets are confirmed and an explicit activation smoke test passes.
7. Run catalog validation against the target host's generated-child set before completing adoption. Inspect the host-visible activation surfaces for plausible non-generated competitors; include each material competitor with `--routing-competitor` so it participates in overlap checks and the routing fingerprint without being subjected to the generated-child contract.
8. When an overlap cluster exists — including generated-child versus non-generated-host-skill overlap — require independent multi-skill routing tests before catalog routing becomes `verified`.

If a host cannot expose enough evidence, retain the strongest truthful non-operational state such as `installed` or `unavailable`.

## Codex adapter

Current official Codex guidance establishes these checks:

- Repository skills are discovered from `.agents/skills` directories from the working directory through the repository root.
- A nested project's `.agents/skills` directory is therefore visible only when it lies on that upward search path; do not assume Codex searches downward from a repository-root session into nested projects.
- User skills are discovered from `$HOME/.agents/skills`.
- Admin skills may be discovered from `/etc/codex/skills`; system skills are bundled by Codex. Include either as routing competitors when their host-visible activation scope materially overlaps the generated child.
- Same-named skills are not merged, so a separately visible skill with the same name remains a distinct routing/conflict surface.
- Codex normally detects skill changes automatically; restart only when the change does not appear.
- `[[skills.config]]` entries in `~/.codex/config.toml` can disable a skill by `SKILL.md` path.
- In Codex CLI or the IDE extension, explicit invocation uses `/skills` or `$skill-name`; implicit invocation depends on the frontmatter description.
- Large skill catalogs can cause descriptions to be shortened or skills to be omitted from the initial list.

For Codex adoption, resolve the intended fresh-agent working scope first, then confirm the installed path, absence of an applicable disable entry, visibility in that skill surface, and a successful explicit `$skill-name` smoke task. Treat implicit-routing behavior as separate catalog evidence.

Source reviewed 2026-08-29: [OpenAI Codex skill docs](https://learn.chatgpt.com/docs/build-skills)

## Canonical child location

For a project-local generated child, artifact staging and host installation are different locations with different meaning:

- staged artifact: `<project-root>/.agents/roblox/resources/artifacts/skills/<skill-name>/`;
- adopted Codex repository skill: `<skill-scope-root>/.agents/skills/<skill-name>/`.

Do not leave both as independently editable canonical children after adoption. Transition the validated artifact into the adopted location and record that host location. A later repair edits the canonical adopted child when that host copy is the managed project artifact; if a separate host outside the project contains another installed copy, follow the ordinary authorized host-update rule below.

## Post-adoption defects

Capture the task, host, project, installed identity/version, expected behavior, observed behavior, smallest reproduction, workaround, and proposed durable correction, then classify the defect before changing lifecycle state.

- **Hard:** Mark matching operational entries `blocked`, invalidate affected behavioral and catalog-routing passes, and enter the repair loop plus applicable state reconciliation.
- **Soft, diagnosis only:** Safe reversible immediate work may continue. Surface the defect before completion; do not invalidate unrelated lifecycle evidence or force provenance reconciliation when no artifact changes are authorized.
- **Soft, authorized child repair:** Keep the host truthfully `installed` while the canonical child is being repaired, invalidate structural, behavioral, catalog-routing, and explicit-activation evidence affected by the edit, and restore `operational` only after fresh validation and explicit activation.

A repaired artifact does not update a separate installed host copy automatically. Obtain authorization for that host mutation, update it, rerun all invalidated regression checks, rerun catalog validation, and repeat explicit host activation before restoring `operational`. For a managed project-local child whose canonical copy is already the adopted `.agents/skills/<skill-name>/` directory, repair that canonical child in place and rerun the same invalidated host checks; do not manufacture a second staging copy.

## Catalog coherence

Run `scripts/validate_skill_catalog.py` whenever a child is added, refreshed, repaired, or adopted. The ordinary positional paths are generated children and receive full generated-skill validation. Add materially overlapping host-visible non-generated skills with `--routing-competitor <path>`; they contribute only activation metadata to overlap detection and the order-independent routing fingerprint. Store that fingerprint with routing evidence. A change to any member of the tested routing set invalidates the old fingerprint/evidence.

Static validation detects structural conflicts and overlap risk; it does not prove host selection. Verify reported overlap clusters with independent tasks that exercise each generated child's positive boundary, the competing skill's boundary, and a simpler task that should select neither. A host with one generated child still requires Test J when a plausible non-generated routing competitor exists.
