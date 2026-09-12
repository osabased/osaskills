# Server Authority structure work

Use this reference when the current or target structure uses or materially plans to use Roblox's specific Server Authority engine mode (`Workspace.AuthorityMode = Server`), prediction/rollback APIs, or shared deterministic simulation; or when the task explicitly reviews, designs, plans, enables, disables, or migrates to/from Server Authority.

Treat Server Authority as an engine simulation model, not as a synonym for ordinary server-side validation. Confirm the mode from the DataModel or mapped Workspace properties when available. Generic server validation, `SetNetworkOwner(nil)`, or ordinary client/server code does not prove it. When prediction APIs or a complete related configuration are visible but `AuthorityMode` cannot be inspected, mark the mode unresolved and preserve the apparent simulation boundaries.

## Structural rules

- Custom predicted gameplay can intentionally execute core deterministic simulation on both client and server. Shared simulation code therefore belongs in a client-visible location such as `ReplicatedStorage` when both sides must execute it; final state authority still belongs to the server.
- Keep secrets, privileged validation, persistence, purchases, and authoritative-only data server-only. Replicated deterministic code and rollback-aware state are inspectable by clients.
- Preserve a clear simulation-to-presentation boundary. Effects, sounds, smoothing, and other irreversible presentation work should not accidentally become part of rollback-sensitive simulation.
- Do not assume ordinary RemoteEvents are ordered with property or attribute replication. Preserve simulation-sensitive ordering intentionally.

## Before moving affected simulation code

Trace the affected:

- client and server loaders;
- `RunService:BindToSimulation()` registrations;
- `RunService:SetPredictionMode()` / `GetPredictionStatus()` use;
- InputActions or InputContexts that drive core simulation;
- rollback-aware attributes or synchronized state;
- `RunService.Rollback` handling for custom Luau state;
- predictive instance creation; and
- simulation-to-presentation boundaries.

## Validation

When a change touches prediction, synchronized simulation state, or core simulation input, validate both client and server behavior. Use representative Studio network simulation when available; a zero-latency playtest alone does not establish rollback-sensitive correctness.

Preserve an established conventional networking model unless the request or an independent requirement justifies adopting Server Authority.

Re-open current Roblox documentation whenever the task depends on release state, API behavior, prerequisites, or current platform recommendations.

## Sources

- [Server authority model](https://create.roblox.com/docs/projects/server-authority)
- [Advanced techniques](https://create.roblox.com/docs/projects/server-authority/techniques)
- [RunService](https://create.roblox.com/docs/reference/engine/classes/RunService)
- [Workspace.AuthorityMode](https://create.roblox.com/docs/reference/engine/classes/Workspace/AuthorityMode)