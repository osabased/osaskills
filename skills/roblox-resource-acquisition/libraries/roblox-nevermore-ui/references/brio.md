# Brio 14.37.2

Checked against `src/brio/src/Shared/Brio.lua` at commit `3286fd3`.

## API

| Call | Notes |
| --- | --- |
| `Brio.new(...)` | Holds the values until the Brio is killed. |
| `Brio.delayed(seconds, ...)` | Creates a Brio that dies after a delay. |
| `Brio.isBrio(x)`, `Brio.DEAD` | A type check, and a shared already-dead Brio. |
| `brio:IsDead()` | `true` after `Destroy`/`Kill`. |
| `brio:GetValue()` / `brio:GetPackedValues()` | Errors ("Brio is dead") once dead. |
| `brio:ErrorIfDead()` | Asserts that the Brio is alive. |
| `brio:GetDiedSignal()` | Fires once on death. |
| `brio:ToMaid()` / `brio:ToMaidAndValue()` | A **new** Maid each call, cleaned up when the Brio dies. Errors if the Brio is already dead. |
| `brio:Destroy()` / `brio:Kill()` | Safe to repeat. Clears and freezes the Brio, then fires the died signal. Death is permanent. |

## Patterns

```luau
if brio:IsDead() then return end
local maid, player = brio:ToMaidAndValue()
maid:GiveTask(player.CharacterAdded:Connect(onCharacter)) -- ends when the Brio dies
maid:GiveTask(task.spawn(function()
	local data = fetchAsync(player)
	if brio:IsDead() then return end -- re-check after every yield
	apply(data)
end))
```

- Make one lifetime Maid per operation and register its work before activation. If the operation ends early, clean that Maid up; that doesn't kill a borrowed Brio.
- A captured value plus an `IsDead` check before a yield proves nothing after the yield. Re-check death, and your feature's disposed flag, before applying async results.
- Brio streams usually come from `Observable<Brio<T>>` (for example `Blend.ComputedPairs` or `ValueObject:ObserveBrio()`). Each emitted Brio dies when its value is replaced or the subscription ends.

## Sources

- [Brio API](https://quenty.github.io/NevermoreEngine/api/Brio/)
- [Brio implementation at the reviewed commit](https://github.com/Quenty/NevermoreEngine/blob/3286fd397c9c42e7f29c8a881ac7dde12887e783/src/brio/src/Shared/Brio.lua)
