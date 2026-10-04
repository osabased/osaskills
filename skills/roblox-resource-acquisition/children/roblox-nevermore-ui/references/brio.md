# Brio value lifetimes

Use for values with an alive/dead lifetime, work owned by that lifetime, or
stale-value handling. The parent [Nevermore skill](../SKILL.md) owns the exact
pins, imports, shared cleanup rules, and verification boundary.

## Values and owned work

- Brio.new(...) contains values whose validity ends permanently when destroyed.
- Check IsDead before GetValue or ToMaid. Do not use captured values after death or assume a dead Brio can be revived.
- brio:ToMaid():GiveTask(task) ties that work to Brio death. Destroy kills the Brio and is safe to repeat.

Read [Rx](rx.md) when the lifetime participates in an observable pipeline.
Read [Blend](blend.md) when the lifetime controls mounted UI. Keep cleanup
ownership tied to the Brio and follow the parent's cross-library teardown rules.

## Sources

- [Brio API](https://quenty.github.io/NevermoreEngine/api/Brio/)
