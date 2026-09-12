# Script Capabilities boundaries

Use this reference when the affected structure is under `Workspace.SandboxedInstanceMode = Experimental`, or when affected project data explicitly configures `Sandboxed = true` or non-empty `Capabilities` and the Workspace setting cannot be inspected.

Treat the effective sandbox container and capability set as a structural security boundary. The mere existence of `Sandboxed` or `Capabilities` properties in the engine API is not evidence that capability enforcement is active.

Before moving code across an active or materially suspected boundary:

1. Identify the effective sandbox container and capability set.
2. Trace affected ModuleScript requires and instance access.
3. Trace Bindable and Remote communication that crosses the boundary.
4. Determine whether the move changes whether scripts can run or which instances they can access.
5. Preserve the existing boundary unless the user explicitly requests a security-model change.
6. Validate the affected execution and communication paths after the move.

When the Workspace setting is unavailable but affected project data configures sandboxing, mark the capability model unresolved and preserve the apparent boundary until it can be established.

Do not recommend adopting Script Capabilities merely because they are available.

Re-open current Roblox documentation when the task depends on beta status, enforcement behavior, or API semantics.

## Source

- [Script Capabilities](https://create.roblox.com/docs/scripting/capabilities)