# Vide troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `cannot create a new reactive scope inside another reactive scope` | `derive`, `effect`, `show`, `indexes`, or a reactive property was created inside an effect, a derive, or a property function. Move it to the component body, or into a `show`/`switch`/`indexes` branch. |
| `cannot use derive() outside a stable or reactive scope`, `cannot cleanup outside a stable or reactive scope` | The call ran at module level or in a callback after the scope ended. Run it inside `root`/`mount` or a component. |
| `attempt to yield in reactive scope` | Strict mode caught a yield in an effect or property. Do async work in `task.spawn` and write the result into a Source. |
| An effect runs twice per change | Strict mode re-runs reactive scopes to check purity. That is expected; make the effect idempotent. |
| `root already destroyed` | A disposer ran twice. Clear the reference before calling it (see the idempotent owner in [API and lifecycle](api-and-lifecycle.md#lifecycle-and-teardown)). |
| UI stays on screen after `stop()` | The mount disposer doesn't destroy the returned Instance. Call `cleanup(gui)` inside the component. |
| UI stops animating, or delayed removals never finish | Something called `Vide.step`, which disconnected the Heartbeat stepper. Remove the call, or drive `step(dt)` every frame yourself. |
| A list renders in the wrong order | `indexes`/`values` output order is not guaranteed. Set `LayoutOrder` and use a `UIListLayout` with `SortOrder = LayoutOrder`. |
| `duplicate property X at depth N` | The same property key appears twice at one nesting level of a props table. |
| `table source passed to values() contains duplicate values` | `values()` keys scopes by value. Use `indexes()` or make the values unique. |
| Type error for `create "UIPadding"` / `"UISizeConstraint"` | A gap in the 0.4.1 `Instances` type map; it works at runtime. Use `Instance.new` under the owned root, or cast the class name. |
| User-defined type function diagnostics | Enable the new solver in both the editor and the CLI ([setup](setup.md#type-checking)). |
| A Getter type error at a property | Annotate the getter (`local label: () -> string = ...`) instead of widening to `any`. |
| A Charm value never updates the UI | Charm getters don't create Vide dependencies. Bridge them through a Vide Source (see the `roblox-charm` skill). |
