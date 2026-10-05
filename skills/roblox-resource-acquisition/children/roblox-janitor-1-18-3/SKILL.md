---
name: roblox-janitor-1-18-3
description: "Use for Janitor 1.18.3 owned resource cleanup, indexed replacement and lifecycle diagnosis; exclude package selection/upgrades, Vide reactive scopes, generic project structure and trivial native disconnects."
---

# Janitor 1.18.3

Use **Janitor** for owned connection/object cleanup and indexed resource replacement. Guidance targets **1.18.3** (source reviewed **2026-10-03**). Resource verification: **verified**.
This child is advice-only: it claims instruction correctness and exact-install checking, not maintained executable Luau examples or a runtime harness. The affected project's matching resource record owns executed proof. Actual Roblox Studio checks exercised indexed replacement, native/custom connection cleanup and 100 rapid cleanup cycles; current UI startup and owner teardown are recorded separately.

## Use when

- Implementing or diagnosing Janitor 1.18.3 cleanup ownership, replacement, partial acquisition or feature teardown.

## Do not use when

- Selecting/upgrading a cleanup library; implementing Vide reactive scopes; a single native Disconnect or Destroy call.
- The project's adopted target differs: preserve its pin and resolve exact-target guidance.

## Prerequisites and installation

Resolve `<project-root>` from the supplied active project and `<child-skill-directory>` from this loaded `SKILL.md`. Resolve `<parent-skill-directory>` from the installed `roblox-resource-acquisition` skill's loaded location; prefer the active project's `.agents/skills` copy when present, otherwise use the host's discovered skill location. Substitute these placeholders with actual paths before executing commands, quote paths containing spaces, and run project commands from `<project-root>`. Checker inputs resolve against that project; never infer it from the shared skill's location. Default adoption of a bundled child is project-local.

Resolve the active Roblox project and its owned pin first. Reviewed pesde 0.7.4 supports this package directly; use pesde rather than introducing Wally as a separate manager. Parent roblox-resource-acquisition must be installed; its scripts need Python and PyYAML. This child's checker needs Python 3.11+ and only the standard library.

1. Add `Janitor = { wally = "howmanysmall/janitor", version = "=1.18.3" }` to `[dependencies]`; keep `[wally_indices].default="https://github.com/UpliftGames/wally-index"`. Map roblox_packages to a shared Packages folder with official pesde/scripts_rojo mapping and sourcemap hooks. The native Wally wrapper maps to a lowercase internal ModuleScript and requires correctly; verify the actual map before using a path.

Initial intentional resolution is `pesde install`; ordinary restoration is `pesde install --locked`. Do not modify package-generated wrappers or vendor source. MIT license. 

## On-demand maintenance

- Promotion guard: Check sibling `.skill-maintenance/roblox-janitor-1-18-3.json` before ordinary use; presence stops dependent use until recovery/completion.
- First-use freshness: Before this resource's first use in a task, read and apply the installed `roblox-resource-acquisition` parent's `references/on-demand-maintenance.md#first-use-freshness-check`. Compare canonical stable releases/maintained source and relevant documentation with the actual installed/project-pinned target, check this guidance's compatibility, reuse unchanged checks within the task, and disclose unavailable lookups. Preserve the selected pin and valid exact-target proof; the comparison alone does not authorize upgrades or full lifecycle reconciliation.
- Freshness triggers: Relevant current claims, acquisition/upgrade, generation/refresh, source drift, consequential practice or reusable defects invoke `roblox-resource-acquisition` once for this scope and its `references/on-demand-maintenance.md`.
- Target and economy: Preserve the project's selected target and local compatibility guidance. Healthy immutable use keeps the cheap declaration/lock query and deferred integrity gate. Dependency/architecture/practice changes return to their authority. No schedule.

## Repair interrupt

- Trigger: Invoke `roblox-resource-acquisition` in `repair/reconcile` mode when this guidance requires guessing, bypassing instructions, repeating a workaround, or an undocumented adjustment likely to recur. A harmless one-off task-local adjustment is not an interrupt.
- Hard defect: Stop affected work for unreliable correctness, security, identity/version or verification; reconcile and repair before continuing.
- Soft defect: Safe reversible work may continue, but invoke parent diagnosis and surface the reproduction, workaround and durable correction before completion; do not force unrelated provenance work.
- Handoff: Capture task, installed state, expected/observed behavior, smallest reproduction, workaround and proposed durable correction. Parent invocation authorizes diagnosis/reporting; edits require current task authorization or the parent's approved on-demand factual-repair grant.


## Common path

1. Run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock --declared` in the affected project.
2. Resolve the matching record below and run the narrow Current-block query. Continue only on HEALTHY without package internals, full proof or learnings.
3. Create `Janitor.new()` before fallible acquisition. Register native or LemonSignal connections with `owner:Add(connection, "Disconnect", optionalIndex)` immediately after acquisition. Register owned objects with their explicit `"Destroy"` method and callbacks with `true`. Replacing an index cleans its previous resource synchronously. Use `Remove(index)` for cleanup; `RemoveNoClean(index)` transfers ownership without cleanup.

Keep producer connections and consumer destruction in separate explicit phases. Detach the owner and set a disposed flag before teardown. Protect each top-level phase so a failed phase cannot skip the next one. Do not rely on order among entries in a Janitor or on retry after a throwing entry. Call a raw Janitor's `Destroy()` at most once; its successful implementation clears the table and metatable.

Before completion run the Integrity gate. Any runtime claim requires the project's corresponding execution evidence.

## Operational reconciliation

- Policy: conditional — exact declaration and lock counterpart establish ordinary-use identity; installed integrity is deferred to completion.
- Installed-state check: `scripts/check_install.py` compares the direct alias, canonical registry/package, exact version, target and lock counterpart. Its integrity mode additionally checks every reviewed runtime/compiler source file and Janitor's material companion sources.
- Expected identity/state: slug `janitor`, package `howmanysmall/janitor`, https://github.com/howmanysmall/Janitor, version 1.18.3.
- Current-block check: Before affected use run `python <parent-skill-directory>/scripts/check_resource_status.py --pair <child-skill-directory> MATCHING-RECORD.yaml`, substituting the resolved record path. Proceed only on HEALTHY (exit 0); BLOCKED or UNKNOWN enters full parent-state reconciliation. This read-only query executes no evidence commands.
- Integrity gate: Before completion run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock`. PASS (exit 0) reports janitor, 1.18.3 and installed-integrity. Package files resolve relative to the manifest directory; reviewed standard pesde layout is required. Run the affected project's source/build check separately.
- Escalation triggers: Missing/mismatched declaration or lock; adoption/upgrade; authorized repair invalidating evidence; verifier failure/drift; hard correctness/security/identity/version/verification defect; known block or BLOCKED/UNKNOWN query. Stop affected version-sensitive use and perform Parent-state check.
- Parent-state check: Use an explicitly supplied authoritative record when present. Otherwise resolve the project root and its schema-version 3 `.agents/roblox/resources/records/janitor.yaml` plus resource-bound learnings under `.agents/roblox/resources/learnings/`. If this project-scoped child's project cannot be resolved, report UNKNOWN state and invoke roblox-resource-acquisition in repair/reconcile mode; do not silently switch to global records. Only for an explicitly user/global-scoped child with no applicable project root, use selector-qualified `~/.roblox-resources/records/janitor--1.18.3.yaml` and `~/.roblox-resources/learnings/`. Match resource slug, canonical URL and package identity. Load full evidence/learnings only after escalation.
- Mismatch/unknown action: For every state escalation trigger, stop the affected use, perform Parent-state check and invoke roblox-resource-acquisition in repair/reconcile mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth.

## Client/server placement

The shared package can be replicated. Client and server require caches and cleanup owners are separate; a server Janitor cannot clean client UI. Use a client feature owner for UI and a server owner for privileged gameplay. Janitor creates no remote channel.

## Mental model

Owned connection/object cleanup and indexed resource replacement; the application retains lifetime and authority decisions.

## Lifecycle and cleanup

Initialization: requiring Janitor loads FastDefer and its Promise companion modules; `new()` creates an inert cleanup table. `Add` registers ownership and an indexed replacement can immediately invoke prior cleanup. `LinkToInstance` activates an owned Destroying subscription.

Reuse: on successful Cleanup the owner can accept new resources. Set ownership before construction, add each acquisition immediately, and explicitly roll back registered resources if later construction fails. Use an outer disposed/detached wrapper for reentrant and repeated teardown.

Cleanup/destruction: disconnect producers and cancel registered tasks explicitly; cleanup uses table iteration with no deterministic resource ordering. User callbacks and object methods are called directly; a thrown entry aborts the remaining entries and may leave CurrentlyCleaning set. Do not claim best-effort continuation or a reliable retry. Isolate failure-prone entries in protected callbacks or separate top-level owners. Disconnect producers before destroying their consumers. Threads use task.cancel with the resource's protected/deferred fallback; independently running async work still needs cancellation or invalidation at its owner.

Ownership boundary: a feature may own its connections, objects and tasks; it must not finalize shared engine services, Vide package work, LemonSignal’s shared coroutine pool or other package/global schedulers. A module-level owner-removal listener may be needed when connections made from a LocalScript disappear with that script.

## API used by this skill

`new`, `Add`, `AddObject`, `Remove`, `RemoveNoClean`, `Get`, `GetAll`, `Cleanup`, `Destroy`, `LinkToInstance`, `LinkToInstances`. `AddPromise` exists but is outside this child’s proof and ordinary connection role. `Cleanup` keeps a successfully cleaned owner reusable. `Destroy` invalidates it. `LinkToInstance` subscribes to Instance.Destroying; it does not detect reparenting/removal by itself.

## Failure modes

### Wrong setup, stale API or cleanup ownership

Wrong cleanup method -> use explicit Disconnect, Destroy or true. Consumer dies before producer -> split phases. Cleanup stops on a thrown callback -> isolate the callback and keep later top-level phases protected. UI remains after bootstrap removal -> verify module-owned removal handling rather than relying only on caller-owned Destroying connections. Wrapper missing -> locked restoration, mapping and actual ModuleScript class first.

## Limitations

- No resource order or error-continuation guarantee. Raw successful Destroy is not repeatable. LinkToInstance covers destruction, not all removal lifecycles. No automatic cancellation of unregistered tasks. Janitor 1.18.3 brings howmanysmall/typed-promise 4.0.6 and evaera/promise 4.0.0 in the reviewed pesde lock; their promise APIs are not tested by this cleanup guidance.

## Security notes

Janitor has no special network or persistence trust boundary. Cleanup callbacks execute arbitrary application code: register only trusted local callbacks and owned objects. Never accept client-provided cleanup method names or object ownership. Keep privileged rules server-authoritative. Preserve pinned dependencies and ordinary locked restoration.

## Verify after installation

Executable fixture: not-applicable — advice-only instructions and a read-only exact-install checker; no embedded executable Luau integration, rendering, network delivery or clean-diagnostics claim. Project resource execution is recorded separately.

Run: `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock` from the affected project.

Pass condition: The command exits 0 and prints status `PASS`, resource `janitor`, version `1.18.3`, lane `installed-integrity`. A modified package source or mismatched manifest/lock exits 1. After setup, run the project's check command for mapped strict consumers and artifacts; that source/build lane still does not prove runtime behavior.

Evidence boundary: helper PASS proves declaration/lock and source identity only. Advice tests verify this instruction interface. Any real lifecycle/input/network claim must name and execute an owned project fixture in its engine host; no process-global finalization or clean-console promise is supplied here.

## Alternatives

- Trove and Maid are informational alternatives. Direct native Disconnect/Destroy is sufficient for a lone resource. The user selected Janitor; preserve the owner’s identity and pin rather than substituting.

## Provenance

- Resource slug: janitor
- Package identity: howmanysmall/janitor
- DevForum: No DevForum topic is used/applicable.
- Canonical source/docs: https://github.com/howmanysmall/Janitor
- Source version/release/commit: 1.18.3
- Source review date: 2026-10-03
- Resource verification: verified

## Version drift

Preserve the project's adopted pin. Check source/release changes affecting this API or command before proposing an upgrade. Revalidate changed instructions, exact source checker, project execution and host activation after an authorized update. A newer stable or prerelease announcement is evidence to report, not authority to replace an externally owned dependency.
