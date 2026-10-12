---
name: roblox-resource-acquisition
description: "Choose, add, compare, pin, upgrade or troubleshoot third-party Roblox libraries and development tools. Use whenever a Roblox/Luau task might pull in an external dependency: adding or installing a Wally, pesde or npm (roblox-ts) package; picking a signal (GoodSignal, LemonSignal), cleanup (Janitor, Maid, Trove), Promise, ProfileStore/DataStore wrapper, networking (Blink, ByteNet), UI (Vide, Fusion, React-lua) or state (Charm) library; questions like \"is there a module for X\", \"X vs Y\" or \"library or write it myself\"; evaluating a DevForum community resource; setting up tools like Rojo, Rokit, Selene, StyLua or Lune; or refreshing a pinned version. Also use when a roblox-* library skill reports BLOCKED or a version mismatch, or its guidance is wrong. Not for ordinary coding with an already-adopted library (use its own skill) or project layout (use structure-roblox-projects)."
---

# Roblox Resource Acquisition

Choose the smallest reliable solution for the actual task. Preserve the project's selected resource, pin and role. Ordinary use of an adopted library follows its own child skill; it does not restart acquisition.

## Terms

- **Resource:** a third-party Roblox library/module or development tool.
- **Pin / selector:** the exact version, commit or dated source state in use.
- **Child skill:** a per-library skill such as `roblox-janitor` with a `SKILL.md` plus a static `resource.yaml`. Children share this skill's checkers through [child usage](references/child-usage.md).
- **AGENT_DIR:** the project's agent directory. It is the project's `.claude/` if it exists; otherwise `.agents/` if it exists; otherwise create `.claude/`. If both exist, use the one that already contains `roblox/`; if neither or both do, use `.claude/`. All project resource data lives under `AGENT_DIR/roblox/resources/`; the user-wide store is `~/.claude/roblox/resources/`.
- **Record:** the project's YAML file for one resource at `AGENT_DIR/roblox/resources/records/<slug>.yaml`. It holds trust, verification and blocks.
- **Trust basis:** why a resource may be used at all: `curated`, `project`, `explicit-user` or `verified-acquisition`. Trust is not proof that it works.
- **Project-use authority:** who owns the choice of resource for a role. Another skill or project document may own it; then preserve its target.
- **Guard:** a `.skill-maintenance/<skill-name>.json` file beside an installed skill's folder. It means an update of that skill is in progress. Finish or recover the update before using the skill.

## Start with the needed work

- **No acquisition needed:** if a Roblox built-in, an existing authorized project dependency or a small local implementation does the job, do that and validate it. Do not open a registry, comparison or record.
- **A resource is needed:** choose a mode below. For an open-ended choice, establish the intended use first. A target that the project already fixes stays fixed unless its owner changes it.
- **Using an adopted resource:** follow its child skill. Read [maintenance](references/on-demand-maintenance.md) only when a correction, changed practice or guarded update is needed.

Bundled children for Vide, Charm, UI Labs, Bootstrapper, Janitor, LemonSignal, Blink and Nevermore UI are listed in the [bundled catalog](references/bundled-skills.md). Having guidance available does not install the library, adopt it or prove it works.

## Route the operating mode

Read only the references the selected work needs.

### `evaluate/compare`

1. Follow [qualification](references/qualification-workflow.md) and the [evaluation rubric](references/evaluation-rubric.md): hard gates first, then compare survivors against the same intended-use criteria and evidence standard.
2. Stop at the requested decision. Evaluation does not authorize installing, editing the project or generating a child.

Report criteria, decisive findings, the recommendation and material uncertainty. Mark the result evaluation-only.

### `acquire/adopt`

1. Read [adoption policy](references/adoption-policy.md) for scope and completion. A normal "add/use a library" request covers selection, pinning, integration and the project's own checks.
2. Follow [qualification](references/qualification-workflow.md) for the exact target. Before changing a durable project dependency or an externally owned target, read [project adoption](references/project-adoption.md).
3. Make reversible changes and run the resource and project checks that show the intended use works. If a required check cannot run, say adoption is pending and name the missing proof.
4. **Child skill (opt-in):** offer a reusable child skill in one sentence. Generate one only when the user asks for it, or when the same pinned resource is clearly reused across projects; then follow [generation and validation](references/generation-validation.md) and [installing children](references/operational-lifecycle.md). Reuse an existing exact-target child instead of creating a duplicate.
5. Apply [state policy](references/state-policy.md) when writing a record and in the final report. Report trust basis, project role and what was actually verified, separately. Report child and install status only when a child was in scope.

Installed files alone do not complete adoption.

### `refresh`

1. Confirm the canonical identity, pin, project-use authority, installed state and recorded state. Reconcile mismatches first. An externally owned target goes back to its owner; a refresh is not a reason to upgrade or to look for alternatives.
2. Identify changed inputs and keep unchanged ones. Earlier runtime proof stays bound to its recorded target. Rerun only proof that a source, API, intended-use, integration or child change invalidated.
3. Read the affected parts of [qualification](references/qualification-workflow.md), [project adoption](references/project-adoption.md) and [generation and validation](references/generation-validation.md). Use the [repair loop](references/repair-loop.md) for iterative proof or test defects.
4. Apply [state policy](references/state-policy.md) when updating records. Report changed and unchanged inputs and the checks rerun or still required.

## When guidance is wrong

A workaround you had to repeat, or a guess you had to make because the guidance was wrong or missing, is a defect to report. A harmless one-off local adjustment is not. Classify the defect by its impact:

- **Hard:** correctness, security, identity, the selected version or verification is unreliable. Stop the affected work and keep the smallest reproduction.
- **Soft:** the workaround is safe and reversible. Finish the immediate work, then report the reproduction, the workaround and the proposed durable fix before you finish.
- **Unknown:** run the smallest check that classifies it before continuing the affected use.

### `repair/reconcile`

1. Write the defect handoff from known facts: identity and pin, affected task, installed and recorded state, expected and observed behavior, smallest reproduction, impact, safe workaround, proposed fix, invalidated evidence and owner. Mark unknown facts as unknown.
2. For a hard identity, version or security defect, read [installing children](references/operational-lifecycle.md), the [repair loop](references/repair-loop.md), [qualification](references/qualification-workflow.md) and [state policy](references/state-policy.md) before dependent use resumes.
3. Use [project adoption](references/project-adoption.md) for authority, replacement or onboarding questions and [generation and validation](references/generation-validation.md) only for child files a repair changes.
4. Diagnosis and reporting are always allowed. Edit skill files or records only when the current task authorizes it; otherwise propose the exact change.

## Shared invariants

- Bind every verification claim to the canonical identity and exact pin. Forks, mirrors and modified copies inherit no proof. Unknown coordinates prevent an exact-target claim.
- Keep technical fit, trust, project-use authority, runtime verification and child validation distinct. `unverified` means not yet proven; `unavailable` names a required check that cannot run here; `failed` records contradicting evidence.
- Use canonical sources and current Roblox Creator Hub documentation. If a source cannot be reached, try the [bounded fallbacks](references/search-playbook.md#when-an-evidence-route-fails). Never infer APIs or passing tests from names or source reading alone.
- Keep checks proportional and reversible, preserve server authority and validate client input. Never publish, spend money, expose secrets or make irreversible project changes just to validate a resource.

## Completion

Finish the requested decision or change. Report the exact target, the result and any material limitation, and make blocked use, missing proof and authority conflicts explicit. Do not add lifecycle reporting to a no-acquisition or evaluation-only result.
