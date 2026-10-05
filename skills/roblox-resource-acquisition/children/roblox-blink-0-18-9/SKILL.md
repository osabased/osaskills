---
name: roblox-blink-0-18-9
description: "Use for Blink 0.18.9 pesde CLI schema compilation, generated client/server/types placement and compiler diagnosis; exclude networking library selection/upgrades, UI events/previews and production receive activation without a validated size/rate budget."
---

# Blink 0.18.9

Use **Blink** for schema-based Luau network code generation through the pinned pesde CLI. Guidance targets **0.18.9** (source reviewed **2026-10-03**). Resource verification: **verified**.
This child is advice-only: it claims instruction correctness and exact-install checking, not maintained executable Luau examples or a runtime harness. The affected project's matching resource record owns executed proof. Pinned CLI --version, successful empty schema compilation, paired source placement, generated strict analysis and development/release source identity are executed. Production networking is outside the adopted role.

## Use when

- Authoring or diagnosing Blink 0.18.9 CLI configuration, generated code placement or regeneration.

## Do not use when

- Selecting/upgrading a transport; ordinary UI events or preview tooling; production server receive activation before a validated predecode size/rate budget exists.
- The project's adopted target differs: preserve its pin and resolve exact-target guidance.

## Prerequisites and installation

Resolve `<project-root>` from the supplied active project and `<child-skill-directory>` from this loaded `SKILL.md`. Resolve `<parent-skill-directory>` from the installed `roblox-resource-acquisition` skill's loaded location; prefer the active project's `.agents/skills` copy when present, otherwise use the host's discovered skill location. Substitute these placeholders with actual paths before executing commands, quote paths containing spaces, and run project commands from `<project-root>`. Checker inputs resolve against that project; never infer it from the shared skill's location. Default adoption of a bundled child is project-local.

Resolve the active Roblox project and its owned pin first. Reviewed pesde 0.7.4 supports this package directly; use pesde rather than introducing Wally as a separate manager. Parent roblox-resource-acquisition must be installed; its scripts need Python and PyYAML. This child's checker needs Python 3.11+ and only the standard library.

1. Add `blink = { name = "1axen/blink", version = "=0.18.9", target = "lune" }` to `[dev_dependencies]`. Keep `[indices].default="https://github.com/pesde-pkg/index"` and a Lune engine (reviewed 0.10.5). No Studio compiler plugin is required.

Initial intentional resolution is `pesde install`; ordinary restoration is `pesde install --locked`. Do not modify package-generated wrappers or vendor source. MIT license. 

## On-demand maintenance

- Promotion guard: Check sibling `.skill-maintenance/roblox-blink-0-18-9.json` before ordinary use; presence stops dependent use until recovery/completion.
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
3. Read the adopted schema and output placement. Execute the project-pinned alias with `pesde run blink -- --version`; expect Blink 0.18.9. Compile with `pesde run blink -- network/main` for a network/main.blink source, or substitute the adopted source basename. `pesde exec` is a different registry-execution command and is not the locked local alias.

Use option ServerOutput, ClientOutput and TypesOutput with quoted paths relative to the schema’s directory. Use a unique quoted RemoteScope per generated transport. Regenerate all outputs from the same schema/CLI; do not hand-edit generated modules. Example configuration: ServerOutput="../src/server/Network/Server.luau", ClientOutput="../src/client/Network/Client.luau", TypesOutput="../src/shared/Network/Types.luau", RemoteScope="GameName" (each line prefixed by `option `).

Keep an empty starter schema until server contracts are defined. Do not require generated Client/Server modules merely to verify generation: even an empty running server module starts remote listeners and Heartbeat work. For future endpoints, inspect the generated predecode receive path and establish byte/rate budgets before activation; handler-only validation cannot stop parser work.

Before completion run the Integrity gate. Any runtime claim requires the project's corresponding execution evidence.

## Operational reconciliation

- Policy: conditional — exact declaration and lock counterpart establish ordinary-use identity; installed integrity is deferred to completion.
- Installed-state check: `scripts/check_install.py` compares the direct alias, canonical registry/package, exact version, target and lock counterpart. Its integrity mode additionally checks this resource's reviewed runtime/compiler source files.
- Expected identity/state: slug `blink`, package `1axen/blink`, https://github.com/1Axen/blink, version 0.18.9.
- Current-block check: Before affected use run `python <parent-skill-directory>/scripts/check_resource_status.py --pair <child-skill-directory> MATCHING-RECORD.yaml`, substituting the resolved record path. Proceed only on HEALTHY (exit 0); BLOCKED or UNKNOWN enters full parent-state reconciliation. This read-only query executes no evidence commands.
- Integrity gate: Before completion run `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock`. PASS (exit 0) reports blink, 0.18.9 and installed-integrity. Package files resolve relative to the manifest directory; reviewed standard pesde layout is required. Run the affected project's source/build check separately.
- Escalation triggers: Missing/mismatched declaration or lock; adoption/upgrade; authorized repair invalidating evidence; verifier failure/drift; hard correctness/security/identity/version/verification defect; known block or BLOCKED/UNKNOWN query. Stop affected version-sensitive use and perform Parent-state check.
- Parent-state check: Use an explicitly supplied authoritative record when present. Otherwise resolve the project root and its schema-version 3 `.agents/roblox/resources/records/blink.yaml` plus resource-bound learnings under `.agents/roblox/resources/learnings/`. If this project-scoped child's project cannot be resolved, report UNKNOWN state and invoke roblox-resource-acquisition in repair/reconcile mode; do not silently switch to global records. Only for an explicitly user/global-scoped child with no applicable project root, use selector-qualified `~/.roblox-resources/records/blink--0.18.9.yaml` and `~/.roblox-resources/learnings/`. Match resource slug, canonical URL and package identity. Load full evidence/learnings only after escalation.
- Mismatch/unknown action: For every state escalation trigger, stop the affected use, perform Parent-state check and invoke roblox-resource-acquisition in repair/reconcile mode before continuing.
- Defect handoff: Follow the earlier Repair interrupt handoff as the source of truth.

## Client/server placement

The pesde CLI runs in the authoring/build environment with Lune, not in the engine. Generated Server belongs under ServerScriptService, Client in client-required replicated modules, and shared type output in the project’s shared module root. Replication alone does not execute a ModuleScript. Server remains authoritative for client requests; the compiler’s type serialization is not authorization.

## Mental model

Schema-based luau network code generation through the pinned pesde cli; the application retains lifetime and authority decisions.

## Lifecycle and cleanup

Initialization: the build owner invokes the CLI to create output files; it reads the source/imports and writes the configured outputs; it does not run the generated engine modules. Establish owned output locations and retain the same pin before generation. Invalid schema must fail with a compiler diagnostic and nonzero exit.

Reuse: one-shot compilation exits normally. Watch owns a long-lived process; stop only a task-owned watcher. Preserve prior output until a successful compile, and check paired output headers and current schema content before builds; do not claim generation is transactional.

Cleanup/destruction: cancel pending task-owned watch processes explicitly; generated runtime modules have process-global _G._BLINK scope registration. Requiring the running server creates/finds remotes and registers PlayerRemoving, Heartbeat and OnServerEvent listeners; the client waits for those remotes and subscribes. There is no feature-level universal Destroy API. Empty generation is inert only while the runtime remains unrequired. UI stories should use an application transport boundary/mock rather than activate networking.

Ownership boundary: a component owns its handler subscriptions and awaited work as exposed by the actual generated API, not the transport’s shared scheduler or engine services. Pending generated RPC waits are not assumed cancellable; use explicit feature invalidation/time-budget design before relying on them. Compiler-only adoption owns files and any task-created watcher, not Studio’s user-owned process or another watcher.

## API used by this skill

No callable API is exposed by the compiler inside the engine. CLI: `pesde run blink -- source-base`, `--version`, and optional `--watch`; watch belongs to the caller process and ends on its cancellation. Generated event/function APIs are schema-dependent: read the emitted definitions instead of inventing a universal Send/On interface. Stable 0.18.9 is distinct from 1.0.0 prereleases.

## Failure modes

### Wrong setup, stale API or cleanup ownership

Unexpected-token diagnostic -> inspect the schema grammar; # is not a comment marker here. Missing outputs -> inspect schema-relative paths and run the exact local alias. Wrong generated side -> require Server only on server and Client only on client when runtime activation is authorized. Duplicate scope -> unique RemoteScope and avoid cloned/re-required transport modules. Client waits forever -> its server transport was not activated. Handler rate checks leave parser exposed -> receiver validation must precede decode, a second listener cannot veto the generated listener.

## Limitations

- Compiler role and empty generation are verified; no game endpoint delivery, network performance, input rendering or production receive-safety claim. Stable 0.18.9 generated receive callbacks parse buffers without a predecode byte/rate gate. Empty generated modules still start listeners if required in a running game. Output is compiler-owned and not a general feature-cleanup owner.

## Security notes

[Upstream issue #45](https://github.com/1Axen/blink/issues/45) documents oversized-buffer server DoS; the reviewed 0.18.9 generator still loops over incoming bytes before any application handler. Do not represent schema bounds, handler throttling or a parallel RemoteEvent listener as a fix. Before untrusted server activation, require an explicit tested predecode byte/rate budget in the actual receive path and server-authoritative permission/business validation. Do not silently patch generated/vendor source or advance to a prerelease to claim mitigation. Compiler-only empty adoption leaves generated network modules unrequired. No secrets in schemas/client output; arbitrary payload Instance references require server validation.

## Verify after installation

Executable fixture: not-applicable — advice-only instructions and a read-only exact-install checker; no embedded executable Luau integration, rendering, network delivery or clean-diagnostics claim. Project resource execution is recorded separately.

Run: `python <child-skill-directory>/scripts/check_install.py --manifest pesde.toml --lock pesde.lock` from the affected project.

Pass condition: The command exits 0 and prints status `PASS`, resource `blink`, version `0.18.9`, lane `installed-integrity`. A modified package source or mismatched manifest/lock exits 1. After setup, run the project's check command for mapped strict consumers and artifacts; that source/build lane still does not prove runtime behavior.

Evidence boundary: helper PASS proves declaration/lock and source identity only. Advice tests verify this instruction interface. Any real lifecycle/input/network claim must name and execute an owned project fixture in its engine host; no process-global finalization or clean-console promise is supplied here.

## Alternatives

- Native RemoteEvent/UnreliableRemoteEvent, Zap and ByteNet are informational alternatives. Small projects may use native remotes with explicit contracts. The user selected Blink; preserve the adopted pin and return runtime-security blockers to the owner rather than substitute.

## Provenance

- Resource slug: blink
- Package identity: 1axen/blink
- DevForum: No DevForum topic is used/applicable.
- Canonical source/docs: https://github.com/1Axen/blink
- Source version/release/commit: 0.18.9
- Source review date: 2026-10-03
- Resource verification: verified

## Version drift

Preserve the project's adopted pin. Check source/release changes affecting this API or command before proposing an upgrade. Revalidate changed instructions, exact source checker, project execution and host activation after an authorized update. A newer stable or prerelease announcement is evidence to report, not authority to replace an externally owned dependency.
