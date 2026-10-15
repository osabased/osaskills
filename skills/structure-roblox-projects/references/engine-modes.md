# Engine modes: Server Authority and Script Capabilities

Use when the current or target structure uses either mode, or the task enables, disables, reviews or migrates one. Don't recommend adopting either just because it exists, and keep a project's conventional networking model unless the request or a real requirement calls for Server Authority.

## Server Authority

`Workspace.AuthorityMode = Server` is an engine simulation model with prediction and rollback, not a synonym for server-side validation. Generic validation or `SetNetworkOwner(nil)` doesn't indicate it. Confirm the mode from the DataModel or mapped Workspace properties; if prediction APIs are visible but the mode can't be inspected, mark it unresolved and keep the apparent boundaries. It reached full release, opt-in per experience, on 2026-07-09 ([announcement](https://devforum.roblox.com/t/full-release-ship-fair-and-competitive-games-with-server-authority/4727993)).

- Setting it changes other settings automatically: next-generation replication, the input action system, deferred signals, fixed simulation and streaming. Account for each in the write set and checks, and confirm the current list in the setup docs.
- Predicted simulation runs on both client and server, so shared simulation code belongs in a client-visible container such as `ReplicatedStorage`; final authority stays on the server. Secrets, validation, persistence and purchases stay server-only.
- Keep presentation (effects, sounds, smoothing) out of rollback-sensitive simulation.
- RemoteEvents aren't ordered with property or attribute replication; preserve simulation-sensitive ordering on purpose.

Before moving simulation code, trace the client and server loaders, `RunService:BindToSimulation()` registrations, `SetPredictionMode()` and `GetPredictionStatus()` use, the InputActions and InputContexts that drive simulation, rollback-aware attributes and synchronized state, `RunService.Rollback` handling for custom state, and predictive instance creation (deterministic stitching uses the source script's identity, so identical code in two scripts isn't the same source). Validate client and server behavior with Studio network simulation; a zero-latency play-test doesn't prove rollback correctness.

## Script Capabilities

Under `Workspace.SandboxedInstanceMode = Experimental`, a sandboxed container and its capability set form a security boundary. The `Sandboxed` and `Capabilities` properties existing in the API doesn't mean enforcement is on; if project data configures them but the Workspace setting can't be inspected, mark it unresolved and keep the apparent boundary. As of 2026-10 Roblox documents it as experimental and a client beta.

Nested sandboxes intersect their capabilities. Requires from outside the sandbox and cross-boundary Bindable and Remote calls are subject to them, and a script can move only to a container with the same or fewer capabilities. Before moving code across a boundary, identify the container and its capabilities, trace the requires, instance access and Bindable or Remote traffic that cross it, decide whether the move changes what runs or what it can reach, keep the boundary unless the user asked to change the security model, and validate the affected paths afterward.

## Sources

- [Server authority](https://create.roblox.com/docs/projects/server-authority), [techniques](https://create.roblox.com/docs/projects/server-authority/techniques), [RunService](https://create.roblox.com/docs/reference/engine/classes/RunService), [Workspace.AuthorityMode](https://create.roblox.com/docs/reference/engine/classes/Workspace/AuthorityMode)
- [Script Capabilities](https://create.roblox.com/docs/scripting/capabilities)
