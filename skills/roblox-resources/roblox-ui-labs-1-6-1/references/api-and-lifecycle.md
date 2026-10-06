# API and lifecycle

## Mental model

The plugin discovers story modules, loads them into a preview environment, mounts their returned GUI and owns that preview lifetime. Controls are preview inputs, not gameplay state. Framework-specific advanced contracts tell the host how to convert controls and own cleanup; the Vide contract differs from a generic target-and-cleanup callback.

## API used by this skill

The plugin has no supported public Luau mount method to invoke from gameplay. Its supported authoring interface here is the returned story table: `vide`, `controls`, `story(props)`, with `props.controls` carrying Sources. The project installer and read-only checker are tooling commands. Do not invent `UILabs.mount`, `UILabs.reload` or use internal Reflex actions as a production API.

## Lifecycle and cleanup

Initialization: The editor plugin owns the widget lifetime and creates toolbar/widget infrastructure in edit mode. Enabling its widget first creates the plugin's React root and Story Explorer; hiding the widget alone does not unmount that root. The Stop toolbar action unmounts it and resets state; plugin unloading unmounts/reset/disconnects its toolbar/widget connections. Studio owns the plugin's engine GUI teardown.

Reuse: Select/remount the same story through the host instead of retaining a second independent preview. Hide/show can reuse the editor root; Stop resets its state.

Cleanup/destruction: Cancel or invalidate story-owned pending tasks and waits before teardown. UI Labs 1.6.1's Vide mounter creates a control-source scope and a story scope. It converts controls to Sources, calls `vide.mount` around the story, and updates sources when controls change. During preview unmount it calls `vide.step(0)` on that preview's Vide environment, starts protected story disposal, then disposes the source scope. Component-owned Instances still require `Vide.cleanup`. Do not attach unrelated host-global finalizers or create a second uncontrolled mount.

Stories must not yield. Establish scope-owned cleanup immediately before fallible construction; invalidate/cancel any owned pending callbacks on teardown. Vide 0.4.1 cleanup uses insertion order and does not promise error continuation, so keep cleanup callbacks nonthrowing and avoid depending on unsupported order. Gameplay mounts outside UI Labs retain their own idempotent disposal owner.

## Client/server placement

UI Labs runs as an editor plugin, not as a gameplay client/server startup dependency. Keep story modules and fixtures in development-only mappings; release builds must exclude them. The chosen UI framework remains a client runtime dependency. Server gameplay and client-action validation retain server authority; editor previews must use local/mock state and must not run live persistence or privileged actions.

## Limitations

- The plugin and utility-package versions differ. This skill targets only plugin 1.6.1 with plain Vide controls. Utility helpers, custom control ranges, StyleSheet previews, pixel-layout correctness and real input/hot reload need separate source review and execution. Plugin auto-update or a different loaded installation cannot inherit this exact release proof.
