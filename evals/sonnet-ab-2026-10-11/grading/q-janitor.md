===== R1 =====
I couldn't read `wally.toml`, and there's no `Packages/` folder to check the library source against. The code below uses the Janitor and LemonSignal APIs as I remember them. The cleanup-error behavior comes from my memory of Janitor's source, not from your installed copy.

## The class

```lua
--!strict
local RunService = game:GetService("RunService")

-- adjust paths to match your wally.toml aliases / project layout
local Janitor = require(script.Parent.Packages.Janitor)
local LemonSignal = require(script.Parent.Packages.LemonSignal)

local Tracker = {}
Tracker.__index = Tracker

function Tracker.new(owner: Instance, onCleanup: () -> ())
	local self = setmetatable({}, Tracker)

	self._janitor = Janitor.new()
	self.Changed = LemonSignal.new()

	-- 1. Part: Instances default to :Destroy()
	self.Part = self._janitor:Add(Instance.new("Part"), "Destroy")
	self.Part.Anchored = true
	self.Part.Parent = workspace

	-- 2. LemonSignal connection: it's a table, so Janitor's default method
	--    would be "Destroy". Name "Disconnect" explicitly.
	self._janitor:Add(self.Changed:Connect(function(value)
		self.Part.Transparency = value
	end), "Disconnect")

	-- 3. Heartbeat connection (RBXScriptConnection defaults to Disconnect)
	self._janitor:Add(RunService.Heartbeat:Connect(function(dt)
		self.Part.CFrame *= CFrame.Angles(0, dt, 0)
	end), "Disconnect")

	-- 4. Cleanup callback: functions are called directly (method = true)
	self._janitor:Add(onCleanup, true)

	-- 5. The signal itself, so its remaining connections are dropped too
	self._janitor:Add(self.Changed, "Destroy")

	-- Tie everything to the owner's lifetime. When owner is destroyed/unparented
	-- out of the DataModel, the janitor cleans itself up.
	self._janitor:LinkToInstance(owner)

	return self
end

function Tracker:Destroy()
	self._janitor:Destroy()
end

return Tracker
```

Usage: `Tracker.new(someModel, function() print("gone") end)`. Calling `:Destroy()` by hand before the owner dies is also fine.

Two details:
- `LinkToInstance` listens for the owner's `Destroying`/`AncestryChanged`. It uses its own internal connection and hooks it up for you. By default, if the owner is only unparented, the janitor won't fire until the instance is actually destroyed. It also returns a connection you can store if you need to detach the link.
- Cleanup order isn't guaranteed. Janitor stores objects in a hash table and walks it with `next`. Don't make one callback depend on another having already run.

## What happens if a cleanup callback throws

Janitor's `Cleanup` doesn't wrap anything in `pcall`. In 1.18.x, from memory, it works roughly like this:

1. It loops with `next(self)` and calls each object's cleanup method, which is `Object()` for functions and `Object:Method()` for everything else.
2. The thrown error propagates straight out of `Cleanup`, and out of `Destroy` and the `LinkToInstance` handler too.
3. The loop stops at that point. Every object not yet reached is skipped. Depending on hash order, that can include the Part, the Heartbeat connection and the LemonSignal connection. The Heartbeat connection would then keep running, with its closure still holding the Part.
4. Objects already cleaned are gone from the table. Whether the throwing entry is removed first or left behind depends on the exact order of the "call, then clear" lines, and I'm not sure which. I'd read `Cleanup` in `Packages/Janitor.lua` after `wally install` to confirm.
5. When it runs through `LinkToInstance`, the error surfaces in the `Destroying`/`AncestryChanged` handler. Roblox logs it as a script error and the thread dies. Nothing retries the cleanup.

If you want one bad callback not to leak the rest, wrap the user callback yourself:

```lua
self._janitor:Add(function()
	local ok, err = pcall(onCleanup)
	if not ok then
		warn("Tracker cleanup callback failed:", err)
	end
end, true)
```

That protects against your own callback throwing, which is the likely case. It doesn't protect against the library's own `:Destroy()`/`:Disconnect()` calls throwing, but those essentially never do.


===== R2 =====
I haven't checked `wally.toml` for the pins. I wrote this against the Janitor 1.18.3 and LemonSignal 2.0.0 APIs only.

## The class

```luau
--!strict
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Janitor = require(ReplicatedStorage.Packages.Janitor)       -- use your mapped path
local LemonSignal = require(ReplicatedStorage.Packages.LemonSignal)

local Tether = {}
Tether.__index = Tether

export type Tether = typeof(setmetatable(
	{} :: {
		Part: Part,
		_janitor: any,
		_disposed: boolean,
	},
	Tether
))

function Tether.new(
	host: Instance,
	source: LemonSignal.Signal<number>, -- type only if your wrapper re-exports it
	onTick: (dt: number) -> (),
	onCleanup: () -> ()
): Tether
	local self = setmetatable({
		_janitor = Janitor.new(),
		_disposed = false,
	}, Tether) :: any
	local janitor = self._janitor

	-- Part: default method is "Destroy".
	local part = janitor:Add(Instance.new("Part"))
	part.Anchored = true
	part.Parent = workspace
	self.Part = part

	-- LemonSignal connection: it's a table, so the default would be "Destroy"
	-- and cleanup would silently skip it. Name the method.
	janitor:Add(source:Connect(function(value)
		if not self._disposed then
			part.Position = Vector3.new(0, value, 0)
		end
	end), "Disconnect")

	-- Heartbeat is a native RBXScriptConnection: default is "Disconnect".
	janitor:Add(RunService.Heartbeat:Connect(function(dt)
		if not self._disposed then
			onTick(dt)
		end
	end))

	-- Cleanup callback: functions are called on cleanup. Wrapped in pcall (see below).
	janitor:Add(function()
		local ok, err = pcall(onCleanup)
		if not ok then
			warn("Tether onCleanup failed: " .. tostring(err))
		end
	end)

	-- Tie everything to the host's lifetime.
	janitor:LinkToInstance(host)

	return self
end

function Tether.Destroy(self: Tether)
	if self._disposed then
		return
	end
	self._disposed = true
	self._janitor:Destroy()
end

return Tether
```

## What happens if a cleanup callback throws

This follows Janitor 1.18.3's documented behavior. I haven't run it.

If you add `onCleanup` directly with `janitor:Add(onCleanup)` and it throws:

1. **The order is unspecified.** Janitor walks its table with `next()`, so the Part, the LemonSignal connection, the Heartbeat connection and the callback can run in any order.
2. **The throw stops the loop.** Every entry that hadn't run yet is skipped. If the callback happens to run first, the Part stays in `workspace`, the signal listener stays connected, and the Heartbeat callback keeps firing. The `_disposed` flag only makes those callbacks no-ops. The objects still leak.
3. **The Janitor stays marked as cleaning.** Later `Cleanup()` and `Destroy()` calls silently do nothing, so you can't retry. The skipped entries can't be cleaned up through this Janitor.
4. **Who sees the error depends on the trigger.**
   - **Host destroyed:** `LinkToInstance` runs `Cleanup` inside the host's `Destroying` handler. The error shows up in the output as an unhandled error in that handler, and no caller can catch it.
   - **Your `:Destroy()` called:** the error propagates out of `Tether:Destroy()`. By then `_disposed` is already `true`, so a second call returns early.

The class avoids this by wrapping the user callback in `pcall` and turning a failure into a `warn`. That way one bad callback can't skip the Part, the signal connection or the Heartbeat connection. If you need ordering (for example, run the callback before the Part is destroyed), use a second Janitor or explicit steps. A single Janitor doesn't guarantee order.


===== R3 =====
Here is the class. I didn't open `wally.toml`, so I haven't confirmed the pins.

```luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Janitor = require(ReplicatedStorage.Packages.Janitor)
local LemonSignal = require(ReplicatedStorage.Packages.LemonSignal)

local Owned = {}
Owned.__index = Owned

function Owned.new(owner: Instance, source, onCleanup: () -> ())
	local self = setmetatable({}, Owned)
	self._disposed = false
	self._janitor = Janitor.new()

	-- Part: not a function/thread/connection, so the default method is "Destroy"
	local part = self._janitor:Add(Instance.new("Part"))
	part.Anchored = true
	part.Parent = workspace
	self.Part = part

	-- LemonSignal connection: a table, so the default would be "Destroy" and it
	-- would be silently skipped. Name the method.
	self._janitor:Add(source:Connect(function(value)
		part.Position = Vector3.new(0, value, 0)
	end), "Disconnect")

	-- Heartbeat: RBXScriptConnection, defaults to "Disconnect"
	self._janitor:Add(RunService.Heartbeat:Connect(function(dt)
		part.CFrame *= CFrame.Angles(0, dt, 0)
	end))

	-- Cleanup callback: a function, so it is called on cleanup
	self._janitor:Add(onCleanup)

	-- Tie everything to the owner's lifetime. The Janitor's Cleanup runs on owner.Destroying.
	self._janitor:LinkToInstance(owner)

	return self
end

function Owned.Destroy(self)
	if self._disposed then
		return
	end
	self._disposed = true
	self._janitor:Destroy() -- single-use, hence the flag
end

return Owned
```

You'd use it like this:

```luau
local sig = LemonSignal.new()
local obj = Owned.new(character, sig, function() print("bye") end)
character:Destroy() -- Part destroyed, both connections disconnected, "bye" printed
```

## What happens if a cleanup callback throws

This follows Janitor 1.18.3's behavior as described in its skill notes. I haven't run it or read the source myself.

1. **The rest of the cleanup is skipped.** Janitor walks its entries in `next()` order, which is unspecified, and doesn't `pcall` them. The error aborts the loop. Any entries not yet reached stay alive. Depending on the order, that could be the Part, the Heartbeat connection, the LemonSignal connection, or all three. A skipped Heartbeat connection keeps running against a Part that may still exist.
2. **The Janitor gets stuck.** It stays marked as "cleaning", so every later `Cleanup()` or `Destroy()` call silently does nothing. Calling `Owned:Destroy()` afterwards won't retry the skipped entries and won't raise an error. They leak until the Janitor itself is garbage collected, and even then the connections stay live.
3. **The error goes to the output, not to your code.** Through `LinkToInstance`, cleanup runs inside the `Destroying` handler. The error is reported in the output and doesn't propagate to whoever called `owner:Destroy()`. The instance is destroyed regardless. If you call `Owned:Destroy()` directly, the error does propagate to you, but the Janitor is already stuck by then.
4. **Which entries survive is nondeterministic.** If the thrower happens to run last, nothing is lost, which can hide the bug in testing.

**Mitigation:** wrap risky user callbacks so they can't throw, for example:

```luau
self._janitor:Add(function()
	local ok, err = pcall(onCleanup)
	if not ok then
		warn("Owned cleanup callback failed:", err)
	end
end)
```

If cleanup order matters (stop producers, then destroy consumers), use separate Janitors or explicit steps. One Janitor won't guarantee order.


===== R4 =====
I couldn't read `wally.toml`, and the packages aren't installed locally. The `require` paths below are guesses, and the throw behavior comes from my memory of Janitor's source, not from 1.18.3 itself.

## The class

```lua
--!strict
local RunService = game:GetService("RunService")

-- Adjust to your wally.toml aliases / Packages location
local Packages = script.Parent.Parent.Packages
local Janitor = require(Packages.Janitor)
local LemonSignal = require(Packages.LemonSignal)

local Tracker = {}
Tracker.__index = Tracker

export type Tracker = typeof(setmetatable({} :: {
	Part: Part,
	Changed: any, -- LemonSignal instance
	_janitor: any,
}, Tracker))

function Tracker.new(owner: Instance, onCleanup: () -> ()): Tracker
	local self = setmetatable({}, Tracker) :: any
	local janitor = Janitor.new()
	self._janitor = janitor

	-- 1. Part (Instance -> :Destroy())
	local part = janitor:Add(Instance.new("Part"), "Destroy")
	part.Anchored = true
	part.Parent = workspace
	self.Part = part

	-- 2. LemonSignal + a connection to it
	local changed = janitor:Add(LemonSignal.new(), "Destroy")
	self.Changed = changed
	janitor:Add(changed:Connect(function(value)
		print("changed", value)
	end), "Disconnect")

	-- 3. Heartbeat connection
	janitor:Add(RunService.Heartbeat:Connect(function(dt)
		part.CFrame *= CFrame.Angles(0, dt, 0)
	end), "Disconnect")

	-- 4. Cleanup callback (`true` = call it as a function)
	janitor:Add(onCleanup, true)

	-- Tie everything to the owner's lifetime: when `owner` is destroyed
	-- (AncestryChanged -> nil parent), the Janitor cleans up.
	janitor:LinkToInstance(owner)

	return self
end

function Tracker.Destroy(self: Tracker)
	self._janitor:Destroy()
end

return Tracker
```

Two notes:
- `LinkToInstance` fires cleanup when the owner is destroyed. It does not fire when the owner is only unparented, because the link is made with `allowMultiple` unset and Janitor watches for the real `Destroying` signal. If you want the cleanup on unparenting, use `owner.AncestryChanged` yourself.
- In 1.18.x you can also write `janitor:Add(onCleanup, true)` for functions. The `true` is required, and without it Janitor looks for a method named by the second argument.

## What happens if a cleanup callback throws

Janitor's `Cleanup` has no `pcall` around the individual cleanups. As I remember the source:

1. **The error propagates out of `Cleanup()`/`Destroy()`.** When the cleanup was triggered by `LinkToInstance`, that is inside the `Destroying`/`AncestryChanged` handler. Roblox reports it as an uncaught error in the output, with the stack pointing at your callback. Nothing catches it.
2. **Whatever Janitor hadn't reached yet is not cleaned in that pass.** It iterates the internal table with `next`, so the order is not guaranteed. That means the Part, the Heartbeat connection, the signal connection or the signal itself may still be alive. If `onCleanup` happens to run first, all four are still alive. The Heartbeat connection would keep running against a Part that might still exist.
3. **The cleanup state can be left half-finished.** Janitor sets a "currently cleaning" flag during the loop, and the code after the loop resets it and clears the index map. A throw skips that code. A later `Destroy()` or `Cleanup()` on the same Janitor may then do nothing, or retry only the entries that weren't already removed. Treat the object as unrecoverable.
4. **Entries that had already run are fine.** Janitor removes each entry as it processes it, so those aren't run twice.

To make that safe, wrap the user-supplied callback so a throw can't abort the sweep:

```lua
janitor:Add(function()
	local ok, err = pcall(onCleanup)
	if not ok then
		warn("Tracker cleanup callback failed:", err)
	end
end, true)
```

With that wrapper, the Part, signal and connections are always cleaned. Only your callback's failure gets reported, as a warning. The built-in `Destroy` and `Disconnect` methods don't throw in practice, so the user callback is the only realistic failure point.

To confirm the exact ordering and flag behavior for 1.18.3, open `Packages/Janitor.lua` after `wally install` and read `Janitor:Cleanup`. I can check it against the installed source if you grant read access or paste it.
