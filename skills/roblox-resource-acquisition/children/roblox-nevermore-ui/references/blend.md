# Blend UI and previews

Use for UI composition, reactive properties, mount ownership, or UI Labs stories.
The parent [Nevermore skill](../SKILL.md) owns the exact pins, imports, shared
cleanup rules, and verification boundary.

## Composition and state

- Blend.New(className)(props) returns an observable. Each subscription creates an instance and its bindings; disposing that subscription destroys the created instance.
- Blend.mount(existingInstance, props) returns a Maid for bindings/children. Disposing it does not destroy the existing root; its caller retains root ownership.
- Blend.State(initial) is a Nevermore ValueObject. Its owner updates .Value and destroys the state.
- Blend.Computed returns an observable; pass it as a reactive property or subscribe under an owner.

For pipelines or event conversion, read [Rx](rx.md). For value lifetimes and
work that ends with a value, read [Brio](brio.md).

## Studio stories

For a simple UI Labs *.story.luau, return a function(target: Frame) that mounts
owned UI under target and returns a cleanup function. Each mount needs its own
subscriptions/state. The shared adapter supplies the Studio edit-mode loader.

The story cannot return cleanup after a construction error, so dispose partial
acquisitions before rethrowing. Use generic advanced stories when controls are
needed: render(props) receives target, controls, and subscribe; dispose both the
control subscription and UI subscription on unmount.

## Sources

- [Blend API](https://quenty.github.io/NevermoreEngine/api/Blend/)
- [UI Labs function stories](https://ui-labs.luau.page/docs/stories/function)
- [UI Labs generic stories](https://ui-labs.luau.page/docs/stories/advanced/generic)
