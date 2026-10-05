# Brio value lifetimes

Use for values with an alive/dead lifetime, work owned by that lifetime, or
stale-value handling. The parent [Nevermore skill](../SKILL.md) owns the exact
pins, imports, shared cleanup rules, and verification boundary.

Reviewed API: `@quenty/brio` 14.37.1 at NevermoreEngine commit `7ab0297833aa73c193d8c20dc23332280439af7c`.

## Values and owned work

- Brio.new(...) contains values whose validity ends permanently when destroyed.
- Check IsDead before GetValue or ToMaid. Do not use captured values after death or assume a dead Brio can be revived.
- brio:ToMaid():GiveTask(task) ties that work to Brio death. Destroy kills the Brio and is safe to repeat.

Each `ToMaid` call creates a new Maid that listens for this Brio's death. Create one owned lifetime Maid for the relevant operation, register its work before activation, and clean it when that operation ends early. Destroying that Maid does not destroy a borrowed Brio. A captured value and an `IsDead` check before yielding do not establish validity after the yield; re-check death and the feature disposal guard before applying an async result. `Destroy`/`Kill` clears and freezes the Brio; death is permanent.

Read [Rx](rx.md) when the lifetime participates in an observable pipeline.
Read [Blend](blend.md) when the lifetime controls mounted UI. Keep cleanup
ownership tied to the Brio and follow the parent's cross-library teardown rules.

## Sources

- [Brio API](https://quenty.github.io/NevermoreEngine/api/Brio/)
- [Exact Brio implementation](https://github.com/Quenty/NevermoreEngine/blob/7ab0297833aa73c193d8c20dc23332280439af7c/src/brio/src/Shared/Brio.lua)
