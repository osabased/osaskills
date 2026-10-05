# API and lifecycle

## Mental model

Schema-based luau network code generation through the pinned pesde cli; the application retains lifetime and authority decisions.

## API used by this skill

No callable API is exposed by the compiler inside the engine. CLI: `pesde run blink -- source-base`, `--version`, and optional `--watch`; watch belongs to the caller process and ends on its cancellation. Generated event/function APIs are schema-dependent: read the emitted definitions instead of inventing a universal Send/On interface. Stable 0.18.9 is distinct from 1.0.0 prereleases.

## Lifecycle and cleanup

Initialization: the build owner invokes the CLI to create output files; it reads the source/imports and writes the configured outputs; it does not run the generated engine modules. Establish owned output locations and retain the same pin before generation. Invalid schema must fail with a compiler diagnostic and nonzero exit.

Reuse: one-shot compilation exits normally. Watch owns a long-lived process; stop only a task-owned watcher. Preserve prior output until a successful compile, and check paired output headers and current schema content before builds; do not claim generation is transactional.

Cleanup/destruction: cancel pending task-owned watch processes explicitly; generated runtime modules have process-global _G._BLINK scope registration. Requiring the running server creates/finds remotes and registers PlayerRemoving, Heartbeat and OnServerEvent listeners; the client waits for those remotes and subscribes. There is no feature-level universal Destroy API. Empty generation is inert only while the runtime remains unrequired. UI stories should use an application transport boundary/mock rather than activate networking.

Ownership boundary: a component owns its handler subscriptions and awaited work as exposed by the actual generated API, not the transport’s shared scheduler or engine services. Pending generated RPC waits are not assumed cancellable; use explicit feature invalidation/time-budget design before relying on them. Compiler-only adoption owns files and any task-created watcher, not Studio’s user-owned process or another watcher.

## Client/server placement

The pesde CLI runs in the authoring/build environment with Lune, not in the engine. Generated Server belongs under ServerScriptService, Client in client-required replicated modules, and shared type output in the project’s shared module root. Replication alone does not execute a ModuleScript. Server remains authoritative for client requests; the compiler’s type serialization is not authorization.

## Limitations

- Compiler invocation and empty-generation proof belong to the matching project record at its tested target; this portable guidance claims no execution. No game endpoint delivery, network performance, input rendering or production receive-safety claim is implied. Stable 0.18.9 generated receive callbacks parse buffers without a predecode byte/rate gate. Empty generated modules still start listeners if required in a running game. Output is compiler-owned and not a general feature-cleanup owner.
