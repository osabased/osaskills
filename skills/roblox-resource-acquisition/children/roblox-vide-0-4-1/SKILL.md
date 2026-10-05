---
name: roblox-vide-0-4-1
description: "Use for Vide 0.4.1 Luau UI components, reactive state and scope cleanup at the adopted immutable commit; exclude UI Labs plugin management, dependency selection/upgrades and simple native Instance edits."
---

# Vide 0.4.1

Use **Vide** for reactive Luau UI. Guidance targets **5ed4c01940e6bd578fb83253cfbeda0a6c05177c** (source reviewed **2026-10-02**). Resource verification: **verified**.

Proof covers this commit's engine import, reactive construction, scope disposal and failed-mount rollback. It does not establish pixels, actual input, animation, normal startup or a clean console. Generated guidance has an advice-only claim boundary; project fixtures own executable integration evidence.

## Use when

- Implementing or troubleshooting components/state/lifetime in a project that already selected Vide 0.4.1 at this commit.
- Keeping declarative properties and UI Labs stories consistent with the selected Vide lifecycle.

## Do not use when

- A tiny native Instance property edit suffices, or the task concerns another UI framework.
- Selecting/upgrading dependencies or managing the UI Labs plugin; those belong to the parent resource workflow or the UI Labs child.
- The active project's Vide pin differs; preserve its target and find matching guidance.

## Prerequisites and installation

Resolve `<project-root>` from the supplied active project and `<child-skill-directory>` from this loaded `SKILL.md`. Resolve `<parent-skill-directory>` from the installed `roblox-resource-acquisition` skill's loaded location; prefer the active project's `.agents/skills` copy when present, otherwise use the host's discovered skill location. Substitute these placeholders with actual paths before executing commands, quote paths containing spaces, and run project commands from `<project-root>`. Checker inputs resolve against that project; never infer it from the shared skill's location. Default adoption of a bundled child is project-local.

The parent `roblox-resource-acquisition` skill must be installed for status and repair checks. Its Python scripts require PyYAML; restore that prerequisite with `python -m pip install -r <parent-skill-directory>/requirements.txt` in the selected Python environment.

1. Use Python 3.11+ for the read-only checker, pesde with Git dependencies (reviewed 0.7.4), a Roblox-target project and a mapped generated package root. Resolve the active project and its require path. The authoritative declaration is `vide = { repo = "https://github.com/centau/vide", rev = "5ed4c01940e6bd578fb83253cfbeda0a6c05177c" }` in `[dependencies]`. Resolve with `pesde install` only for an authorized initial adoption/change; ordinary restoration is `pesde install --locked`. Keep generated packages untouched and use the official pesde Rojo mapping hook when the project owns that workflow.

GitHub release 0.4.1 is marked prerelease. At review the registry and the tag's pesde manifest still said 0.4.0; `src/lib.luau` reports 0.4.1. The Git commit and lock tree, rather than that stale manifest version, identify this target. Use Luau LSP's new solver: CLI `--flag:LuauSolverV2=true`, VS Code `"luau-lsp.fflags.enableNewSolver": true`.

## On-demand maintenance

- Promotion guard: At activated use, check `<skill-directory-parent>/.skill-maintenance/<skill-directory-name>.json`; ordinary dependent use waits while it exists. Controlled candidate validation is separate.
- First-use freshness: Before this resource's first use in a task, read and apply the installed `roblox-resource-acquisition` parent's `references/on-demand-maintenance.md#first-use-freshness-check`. Compare canonical stable releases/maintained source and relevant documentation with the actual installed/project-pinned target, check this guidance's compatibility, reuse unchanged checks within the task, and disclose unavailable lookups. Preserve the selected pin and valid exact-target proof; the comparison alone does not authorize upgrades or full lifecycle reconciliation.
- Freshness triggers: Relevant current claims, acquisition/upgrade, source drift, consequential practices or reusable defects invoke `roblox-resource-acquisition` once for the affected scope and its `references/on-demand-maintenance.md`. Carry the selected identity, claim and reproduction; do not recursively reopen an active handoff.
- Target and economy: Resolve the project's exact target and local compatibility guidance first. Healthy immutable-target lifecycle checks remain narrow after the first-use comparison. The parent may apply tested factual repairs within its approved authority; dependency versions, architecture and changed practices return to their owner. No scheduled upkeep.

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode when this guidance requires guessing, bypassing instructions, repeating a workaround, or an undocumented adjustment likely to recur. A harmless one-off task-local adjustment is not an interrupt.
- Hard defect: Stop dependent work for unreliable correctness, security, canonical identity, selected version or verification; enter parent state reconciliation and the repair loop before continuing.
- Soft defect: Safe reversible immediate work may continue, but invoke parent repair diagnosis and surface the reproduction, workaround and durable correction before completion. Soft diagnosis does not force unrelated provenance reconciliation.
- Handoff: Capture the task, installed state, expected behavior, observed behavior, smallest reproduction, workaround and proposed durable correction. Parent invocation authorizes diagnosis and reporting, not unrestricted edits. Use current task authorization or the parent's applicable standing factual-repair grant in `references/on-demand-maintenance.md#approved-authority` for edits.

## Common path

1. From the active project root, run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock --declared`. PASS means the canonical declaration and the direct lock entry agree with this commit/tree. This step does not read package internals.
2. Resolve the matching record by the route below, then run the narrow Current-block query. Only HEALTHY permits ordinary use; do not load full record evidence/learnings on this healthy path.
3. Resolve the mapped Vide wrapper and create a component inside a Vide scope. `source(value)` is a getter/setter; function-valued GUI properties react to reads. Use `create("TextLabel")({ Text = label })`, with `label` a typed string getter, rather than guessing overloads.
4. Register each owned root Instance with `cleanup(instance)`. Mount gameplay roots with `mount(component, target)` and retain an idempotent owner wrapper. For UI Labs return `{ vide = Vide, controls = ..., story = function(props) ... end }`; its callback returns the component within UI Labs' existing scope.
5. Run the Integrity gate before completion, plus the project's strict/source/build checks. Preserve the observed evidence boundary.

## Operational reconciliation

- Policy: conditional — the canonical declaration and direct Git lock entry cheaply identify the selected target; installed source integrity is checked before completion.
- Installed-state check: The declared checker compares manifest repo/rev plus the direct lock alias, repository, Git tree and target. On escalation additionally run its integrity mode against the resolved installed package directory.
- Expected identity/state: slug `vide`, package `centau/vide`, https://github.com/centau/vide, commit `5ed4c01940e6bd578fb83253cfbeda0a6c05177c`, tree `8890f5044158a71592249e2d91646715b98ca4aa`.
- Current-block check: Before affected use run `python <parent-skill-directory>/scripts/check_resource_status.py --pair <child-skill-directory> MATCHING-RECORD.yaml`, substituting the resolved matching record path. Proceed only on HEALTHY (exit 0); BLOCKED or UNKNOWN enters full parent-state reconciliation.
- Integrity gate: Run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock --package-dir RESOLVED-PACKAGE-DIRECTORY` before task completion. Resolve the directory from the active mapping/lock, not a guessed version string. PASS and exit 0 require the exact canonical declaration/tree, runtime version 0.4.1 and aggregate source SHA256 `73ac80a420cb550e9ae20d3f8115d5684409dbba7c3b11db2c7ee666d87fcf65`.
- Escalation triggers: Missing/mismatched installed pin or lock; adoption/upgrade; authorized repair that invalidates evidence; verifier failure/drift; hard correctness/security/identity/version/verification defect; already-known block or a BLOCKED/UNKNOWN status query. Every state trigger follows Parent-state check.
- Parent-state check: Use an explicit authoritative record path when supplied. Otherwise resolve the affected project root and its schema-version 3 record `.agents/roblox/resources/records/vide.yaml` plus resource-bound learnings in `.agents/roblox/resources/learnings/`. If this project-scoped child's project cannot be resolved, report UNKNOWN state and invoke roblox-resource-acquisition in repair/reconcile mode; do not silently switch to global records. Only for an explicitly user/global-scoped child with no applicable project root, use `~/.roblox-resources/records/vide--0-4-1.yaml` and `~/.roblox-resources/learnings/`. Match slug `vide`, canonical identity and package ID.
- Mismatch/unknown action: For every state escalation trigger, stop affected version-sensitive work, perform Parent-state reconciliation and invoke `roblox-resource-acquisition` in `repair/reconcile` mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth.

## Client/server placement

Place authored GUI components in the project's client module root and map the package where clients can require it. The client owns PlayerGui mounts and cleanup. Server code must not mount client GUI or treat reactive UI state as authority. Server-side gameplay, purchases, persistence and validation remain server-owned; a shared ModuleScript does not share state across runtimes.

## Mental model

A root establishes a reactive lifetime. Sources store values; property getter functions establish dependencies. A component constructs Instances while the scope is active, and the mount attaches returned roots to its target. Scope disposal removes effects and explicitly registered cleanup resources. Parenting children under one owned Instance gives a concrete destruction boundary.

## Lifecycle and cleanup

Initialization: Require in a running engine activates a package-global Heartbeat connection for stepping. This belongs to the package/host, not each component. `mount` establishes a root and returns its disposer; the feature owner stores it before later fallible work. Construction errors dispose resources already registered in that scope, so register cleanup immediately after creating an Instance.

Reuse: Render the same factory for each mount with that scope's state; keep external Sources owned by their caller. Do not share one mounted Instance between independent roots.

Cleanup/destruction: Vide 0.4.1 cleanup entries run in insertion order and a throwing entry can prevent later entries. Do not assume best-effort continuation or reverse order. Keep callbacks nonthrowing; orchestrate independent top-level teardown phases with protected calls and explicit producer-before-consumer order when needed. Raw disposal is not idempotent: detach the retained disposer before calling it so repeated/reentrant owner cleanup calls it once. Stop owned async producers first and use cancellation/invalidation for their pending callbacks; then dispose the UI scope. Disposal detaches effects, so subsequent external source writes cannot reach the disposed consumer.

`create` does not automatically own Instances. Register root cleanup and parent helpers/children under it. Avoid `step(0)` on component disposal: it disconnects the package-global stepper. UI Labs 1.6.1 applies that finalizer to its own sandboxed Vide instance during story teardown.

## API used by this skill

This minimal Source excerpt is derived from the active project's strict reactive-state fixture; it is an API illustration within the advice-only boundary:

```luau
local title = Vide.source("Preview")
title("Updated")
assert(title() == "Updated")
```

Source-grounded exports used here are `version.major/minor/patch`, `source(initial)`, `create(className)(properties)`, `cleanup(Instance-or-callback)`, `mount(component, target?)`, `root(callback)`, `effect(callback)`, `read(value-or-getter)` and `step(dt)`. The root/mount disposer ends that scope; do not invent `Vide.destroy` or `unmount` exports. Keep Source props typed and scalar/getter semantics explicit.

## Failure modes

### Installation or lifecycle symptom

- User-defined type function diagnostics: confirm the new solver is enabled in both editor and CLI. This target's typed `create` uses UDTFs.
- Unknown class for `create("UIPadding")` or `UISizeConstraint`: this tag's class map omits those helpers. Use native `Instance.new`, parent under the owned root, and keep strict types; do not edit generated/vendor source.
- Getter inference error: use a typed local getter instead of widening to `any`. Avoid nullable initial state until its semantics are reviewed for the selected target.
- Repeat-disposal error/leaked UI: check explicit Instance ownership and the owner's detach-before-dispose wrapper.
- Vendor analyzer errors: report them distinctly. A scoped generated-package diagnostic ignore may match project policy while checking authored consumers; it does not prove upstream source is strict-clean.

## Limitations

- 0.4.1 is a GitHub prerelease with a stale pesde manifest version. Construction proof does not establish real device layout, actual input/focus, animation, startup or clean diagnostics. Current Luau LSP can report internal vendor diagnostics; authored strict checks and installed source integrity must remain enforced.

## Security notes

Vide is executable dependency code. Use the selected canonical immutable Git target and locked restore; do not dynamic-require arbitrary asset IDs or silently auto-update it. No special HTTP, credential or persistence boundary is needed for these UI APIs. Validate client-controlled actions on the server and keep secrets out of replicated modules.

## Verify after installation

Executable fixture: not-applicable — generated guidance claims advice/instruction correctness only. The active project's maintained strict fixture and its recorded engine command own executable integration proof.

Run: `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock --package-dir RESOLVED-PACKAGE-DIRECTORY` from the active project, after resolving that path from its mapping.

Pass condition: The check exits with code 0 and prints a PASS line reporting the exact commit/tree, runtime 0.4.1 and expected source digest. Then run the project's source/build gate and separately execute its maintained engine fixture for any runtime claim.

Evidence boundary: The helper proves declared and installed identity, not runtime. This commit has engine construction/reactive-state/owned-cleanup proof in its matching resource record; fresh projects must retain their own fixture and run it. Real input, rendered layout, animation, startup and clean diagnostics require separate host checks.

## Alternatives

- Native `Instance.new` and events suffice for tiny UI edits. React Roblox, Fusion and other reactive libraries are informational alternatives for different project needs. Preserve the active project's selected Vide pin; replacing it is a decision for that project's authority, not this usage skill.

## Provenance

- Resource slug: vide
- Package identity: centau/vide
- DevForum: no DevForum topic used
- Canonical source/docs: https://github.com/centau/vide
- Source version/release/commit: 5ed4c01940e6bd578fb83253cfbeda0a6c05177c
- Source review date: 2026-10-02
- Resource verification: verified

## Version drift

Keep this commit when a project selects it. A newer tag or registry version is a candidate to review, not authorization to advance the pin. Re-review API types, Instance ownership, scope cleanup ordering/error behavior and package-global stepping before changing this guidance; rerun affected engine proof and independent instruction/routing validation.

