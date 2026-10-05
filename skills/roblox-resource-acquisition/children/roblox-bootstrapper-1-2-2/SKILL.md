---
name: roblox-bootstrapper-1-2-2
description: "Use for LDGerrits Bootstrapper 1.2.2 module discovery, lifecycle dispatch and owned scheduler bindings at the adopted commit; exclude generic project structure, UI components, dependency selection/upgrades and simple direct require calls."
---

# Bootstrapper 1.2.2

Use **Bootstrapper** for deterministic Roblox module discovery and method dispatch.
Guidance targets **ff6700d32875dde5ef9e3625a159436ebd4dc3e9** (source reviewed **2026-10-02**).
Resource verification: **verified**. This child claims advice/instruction correctness;
the matching project's resource record owns executed upstream/integration proof.

## Use when

- Implementing or diagnosing Bootstrapper 1.2.2 loading, init/start phases or owned signal bindings at this commit.

## Do not use when

- A direct require or tiny native Instance change solves the task.
- Selecting/upgrading a loader, designing general project topology, implementing Vide UI, or managing UI Labs.
- The project's adopted Bootstrapper target differs: preserve that target and resolve matching guidance.

## Prerequisites and installation

Resolve `<project-root>` from the supplied active project and `<child-skill-directory>` from this loaded `SKILL.md`. Resolve `<parent-skill-directory>` from the installed `roblox-resource-acquisition` skill's loaded location; prefer the active project's `.agents/skills` copy when present, otherwise use the host's discovered skill location. Substitute these placeholders with actual paths before executing commands, quote paths containing spaces, and run project commands from `<project-root>`. Checker inputs resolve against that project; never infer it from the shared skill's location. Default adoption of a bundled child is project-local.

Use a Roblox project, pesde with Git/Wally compatibility (reviewed 0.7.4), a mapped
package root and official sourcemap/mapping hooks. Parent `roblox-resource-acquisition`
must be installed; its scripts require Python and PyYAML. This checker needs Python 3.11+.
1. Add `Bootstrapper = { repo = "https://github.com/LDGerrits/Bootstrapper", rev = "ff6700d32875dde5ef9e3625a159436ebd4dc3e9" }`
to `[dependencies]` only when adoption is authorized. Initial resolution is `pesde install`;
ordinary restoration is `pesde install --locked`. Its Wally-format package is supported
directly by pesde: retain a `[scripts].sourcemap_generator` hook for exported types.
Resolve the mapped ModuleScript before choosing its require path. At the reviewed pesde 0.7.4 Git/Wally layout, the generated wrapper looks for lowercase bootstrapper but upstream's Rojo root is Bootstrapper. Changing alias casing and clean restoration did not repair it. Use a project-owned import adapter that requires the actual Bootstrapper ModuleScript under the locked .pesde package namespace. Keep its path bound to the selected lock tree and verify its class/source in artifacts; do not edit generated packages or upstream source.

## On-demand maintenance

- Promotion guard: Check sibling `.skill-maintenance/roblox-bootstrapper-1-2-2.json` before ordinary use; presence stops dependent use until recovery/completion.
- First-use freshness: Before this resource's first use in a task, read and apply the installed `roblox-resource-acquisition` parent's `references/on-demand-maintenance.md#first-use-freshness-check`. Compare canonical stable releases/maintained source and relevant documentation with the actual installed/project-pinned target, check this guidance's compatibility, reuse unchanged checks within the task, and disclose unavailable lookups. Preserve the selected pin and valid exact-target proof; the comparison alone does not authorize upgrades or full lifecycle reconciliation.
- Freshness triggers: Relevant current claims, acquisition/upgrade, generation/refresh, source drift, consequential practice or reusable defects invoke `roblox-resource-acquisition` once for this scope and its `references/on-demand-maintenance.md`.
- Target and economy: Preserve the project's selected target and local compatibility guidance. Healthy immutable use keeps the cheap declaration/lock query and deferred integrity gate. Dependency/architecture/practice changes return to their authority. No schedule.

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode when this guidance requires guessing, bypassing instructions, repeating a workaround, or an undocumented adjustment likely to recur. A harmless one-off task-local adjustment is not an interrupt.
- Hard defect: Stop affected work for unreliable correctness, security, identity/version or verification; reconcile and repair before continuing.
- Soft defect: Safe reversible work may continue, but invoke parent diagnosis and surface the reproduction, workaround and durable correction before completion; do not force unrelated provenance work.
- Handoff: Capture task, installed state, expected/observed behavior, smallest reproduction, workaround and proposed durable correction. Parent invocation authorizes diagnosis/reporting; edits require current task authorization or the parent's approved on-demand factual-repair grant.

## Common path

1. From the active project, run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock --declared`.
2. Resolve the matching record below; run the Current-block query. Continue only on HEALTHY without loading internals/full record evidence/learnings.
3. Resolve the package require and the startup root. Use a suffix predicate such as `Bootstrapper.byName("Controller$")`; keep helpers outside that discovery set.
4. `loadDescendants(root, predicate)` returns a name-sorted module-table array and optional errors. Require each discovered ModuleScript to return a table. Check returned load errors before running phases.
5. Use synchronous `run(modules, ".init", context)` then `run(modules, ".start", context)`, checking each returned error map. Prefix `.` means no self; `:` or an unprefixed name injects the module table. Context/other arguments follow it.
6. Retain the original loaded array between phases. `run` returns only modules with that method that succeeded: chaining its init result can incorrectly drop a start-only module. Missing methods are skipped.
7. Run the Integrity gate and the project's source/build check before completion. Separately execute the application's startup for a runtime claim.

Strict Luau array types are invariant here: copy the returned LoadedModules into an array
typed `{ Instance | Bootstrapper.LoadedModule | Bootstrapper.ModulePath }` for dispatch.
Use the same widened list for both phases; preserve its module order and do not replace it
with run's filtered return. The project-owned adapter may re-export the needed upstream types.

```luau
local modules, loadErrors = Bootstrapper.loadDescendants(root, Bootstrapper.byName("Controller$"))
assert(not loadErrors, "Module loading failed")
local dispatchModules: { Instance | Bootstrapper.LoadedModule | Bootstrapper.ModulePath } = {}
for _, module in modules do
	table.insert(dispatchModules, module)
end
for _, phase in { ".init", ".start" } do
	local _, errors = Bootstrapper.run(dispatchModules, phase, owner)
	assert(not errors, "Startup phase failed")
end
```

## Operational reconciliation

- Policy: conditional — declaration and direct Git lock cheaply fix the target; installed integrity is deferred to completion.
- Installed-state check: The checker compares canonical repo/rev, direct alias, Git tree, Roblox target and Wally layout. Integrity additionally checks source digest, version header and manifest.
- Expected identity/state: slug `bootstrapper`, package `ldgerrits/bootstrapper`, https://github.com/LDGerrits/Bootstrapper, commit `ff6700d32875dde5ef9e3625a159436ebd4dc3e9`, tree `4f94dfb887d0d0f81faaf00849d8670e5e8ed7de`, version 1.2.2.
- Current-block check: Before affected use run `python <parent-skill-directory>/scripts/check_resource_status.py --pair <child-skill-directory> MATCHING-RECORD.yaml`, substituting the resolved matching record path. Proceed only on HEALTHY (exit 0); BLOCKED or UNKNOWN enters full parent-state reconciliation.
- Integrity gate: Before completion run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock --package-dir RESOLVED-PACKAGE-DIRECTORY`. Resolve from mapping/lock. PASS exits 0 and reports installed 1.2.2 plus source SHA256 `dd7f94d7a0a10de13b838e65549c9de3b540c568c7c44cf89f0b3ace2b1725fc`.
- Escalation triggers: Missing/mismatched pin or lock; adoption/upgrade; authorized repair invalidating evidence; verifier failure/drift; a hard correctness/security/identity/version/verification defect; a known block or BLOCKED/UNKNOWN query. Stop affected use and perform Parent-state check.
- Parent-state check: Use an explicit authoritative record path when supplied. Otherwise resolve the affected project root and load its matching schema-version 3 record `.agents/roblox/resources/records/bootstrapper.yaml` and resource-bound learnings from `.agents/roblox/resources/learnings/`. If this project-scoped child's project cannot be resolved, report UNKNOWN state and invoke roblox-resource-acquisition in repair/reconcile mode; do not silently switch to global records. Only for an explicitly user/global-scoped child with no applicable project root, use the selector-qualified `~/.roblox-resources/records/bootstrapper--ff6700d32875dde5ef9e3625a159436ebd4dc3e9.yaml` and `~/.roblox-resources/learnings/`. Match by resource slug plus canonical identity and package identity.
- Mismatch/unknown action: For every state escalation trigger, stop the affected version-sensitive use, perform the Parent-state check, and invoke `roblox-resource-acquisition` in `repair/reconcile` mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff; it is the source of truth for defect evidence and parent activation.

## Client/server placement

The shared package can be replicated, but each runtime has its own require cache and module state.
Discover client controllers on clients and server services in ServerScriptService on servers.
Do not include packages, helpers, stories or every replicated module in a blanket startup scan.
Render-step/PreRender bindings are client-only. Keep privileged rules, persistence and client validation server-owned.

## Mental model

Discover module tables once; the caller chooses the method names, execution mode and phase barriers.

## API used by this skill

- `loadChildren`, `loadDescendants`: filtered ModuleScript discovery sorted by Name, with full-path tie break.
- `loadSequence`: retains manual input order. Loaded tables and ModuleScript instances are supported inputs.
- `byName`: Lua pattern, not a regex/glob. Unique discovered names keep diagnostics unambiguous.
- `run`: synchronous sequential dispatch; catches callback errors, continues the current sequence and returns successful invoked modules plus errors. Application policy must stop later phases if required.
- `runAsync`: starts an ordered background sequence; `runConcurrent` starts separate tasks. They return no completion/error receipt and no cancellation handle. Use run when startup dependencies need a barrier.
- `bindTo`: binds an owned method sequence to a Roblox/custom signal or subscription function and returns cleanup. Frame/interval binding APIs are source-reviewed; only claim execution for the specific tested binding.

## Lifecycle and cleanup

- Initialization: The caller/bootstrap owns and activates discovery with loadDescendants and method execution with run. Requiring the bundle gets RunService but creates no subscription or startup task; feature owners retain acquired binding cleanup for their lifetime.
Discovery requires modules, so their top-level code can activate behavior. Keep fallible
activation in owned lifecycle methods, establish cleanup ownership first, and make explicit
partial acquisition roll back before raising. Bootstrapper supplies no dependency graph,
automatic init/start names, module teardown or rollback for module side effects.

- Reuse: `run` calls are activated and owned by the caller. Synchronous calls can yield indefinitely
if a module never returns. Missing methods are skipped. Callback/require failures also emit
an asynchronous error diagnostic; inspecting returned errors does not suppress that output.

- Cleanup/destruction: The feature owner detaches and calls its binding disposer to disconnect subscriptions before destroying consumers. Synchronous use spawns no pending task; async/concurrent work has no cancellation handle. Retain the returned disposer; detach before invoking
it, disconnect producers before destroying consumers, and make the owner's wrapper idempotent.
Bootstrapper does not own or destroy your module tables. An async/concurrent sequence has no
supported cancellation handle: do not use it for a startup barrier or claim its pending
work is cancelled by binding cleanup. No global finalizer is required for ordinary synchronous use.

## Failure modes

### Discovery or phase failure

- No module starts: check mapping/root, suffix pattern, table return and exact method case/prefix.
- Start-only module vanishes: the caller replaced the original array with run's filtered init result.
- Init failure still lets Start run: Bootstrapper continues its current phase; check errors and abort the next phase in your caller.
- Wrong argument/self: dot is static; colon/unprefixed injects self.
- Work after teardown: retain the binding disposer; a binding cleanup does not cancel independently spawned module work.
- Wrapper/type missing: verify official sourcemap hook and restore locked packages; preserve upstream source.

## Limitations

- No dependency resolution, cycle detection, readiness flags, automatic lifecycle names or universal destructor.
Alphabetical order is deterministic, not dependency ordering. For required dependencies, select a
manual sequence or explicit requires within init. Errors are keyed by module name for ModuleScripts;
avoid duplicate names. No comprehensive scheduler, animation or clean-console proof is implied.

## Security notes

There is no special network/credential boundary in discovery/dispatch. Requiring discovered
modules executes their code: constrain roots/predicates to authored trusted modules and preserve
server authority. Avoid arbitrary asset/string paths or client-supplied module lists; use actual
ModuleScript instances/tables in Roblox. Keep the immutable Git pin and locked restoration.

## Verify after installation

Executable fixture: not-applicable — generated guidance claims advice only. Project integration
and resource execution evidence remain external. Its source-grounded recipes are instructions,
not a claim that a generated example ran.

Run: `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock --package-dir RESOLVED-PACKAGE-DIRECTORY` from the active project after resolving that directory from its mapping/lock.

Pass condition: The command returns exit code 0 and output contains the PASS line with commit ff6700d32875dde5ef9e3625a159436ebd4dc3e9, installed version 1.2.2 and source digest dd7f94d7a0a10de13b838e65549c9de3b540c568c7c44cf89f0b3ace2b1725fc; then run the active project's strict/source/build gate. These prove installed
identity and static consumers, not actual startup, subscriptions, rendering or clean diagnostics.
For an application claim, separately run its owned client/server startup and teardown path.

## Alternatives

Direct explicit requires are sufficient for small fixed startup sequences. Other loaders are
informational alternatives, not authority to replace this project's user-selected Bootstrapper pin.

## Provenance

- Resource slug: bootstrapper
- Package identity: ldgerrits/bootstrapper
- DevForum: no DevForum topic used
- Canonical source/docs: https://github.com/LDGerrits/Bootstrapper
- Source version/release/commit: ff6700d32875dde5ef9e3625a159436ebd4dc3e9
- Source review date: 2026-10-02
- Resource verification: verified

## Version drift

Preserve this commit. A newer upstream version is evidence to review, not authorization to
change the project. Re-review ordering, method dispatch, returned errors, async ownership and
binding cleanup before refreshing guidance; rerun only evidence invalidated by changed inputs.
