# q-addsignal

Prompt: Add a signal library to this project so modules can expose custom events. Make whatever project file edits are needed (you can't run commands).

---

## Answer A

### Final message

I didn't edit any files. This project already declares a signal library, so nothing needed adding.

`wally.toml` has `LemonSignal = "data-oriented-house/lemonsignal@2.0.0"`. That is the LemonSignal 2.0.0 package, and `default.project.json` already maps `Packages` into `ReplicatedStorage`. A second signal library would only duplicate it.

The package isn't installed yet. There's no `Packages/` folder and no `wally.lock` in the project, so a `require` of it would fail until you run this in the project root:

```
wally install
```

Then commit `wally.lock`. I couldn't run that or any check, so none of the following has been tested:
- **Require path:** it should be `require(ReplicatedStorage.Packages.LemonSignal)`.
- **Behaviour:** I haven't confirmed that `Fire` and `Connect` work at the pinned version.

How a module exposes a custom event, once the package is installed:

```lua
local LemonSignal = require(ReplicatedStorage.Packages.LemonSignal)

local Health = {}
Health.Changed = LemonSignal.new()  -- Health.Changed:Fire(new, old)

return Health
```

Consumers call `Health.Changed:Connect(fn)`. The owning module should call `Health.Changed:Destroy()` on teardown. Signals only reach code in the same runtime, so use RemoteEvents or Blink to cross the client/server boundary.

I did not write the `CLAUDE.md` resource list. The skill only adds LemonSignal there once it's installed and checked, and the project has no `CLAUDE.md` yet. The project also already has a `roblox-lemonsignal` skill with the API details.

---

## Answer B

### Final message

I made no edits, because the project already has LemonSignal set up.

- **Already declared:** `wally.toml` lists `LemonSignal = "data-oriented-house/lemonsignal@2.0.0"` under `[dependencies]`, with the `shared` realm. `default.project.json` maps `Packages` to `ReplicatedStorage.Packages`, so both server and client can require it.
- **Pin matches:** 2.0.0 is the version the bundled `roblox-lemonsignal` skill covers.
- **Not installed yet:** there is no `Packages/` folder and no `wally.lock`. Running `wally install` in the project root creates both. That's the step I couldn't do. The project has both `wally.toml` and `pesde.toml`, and LemonSignal is only in `wally.toml`, so that's the one to install from.
- **How a module uses it:** it can expose an event like this (use whatever path your sourcemap gives):

```luau
local LemonSignal = require(ReplicatedStorage.Packages.LemonSignal)

local Health = {}
Health.Damaged = LemonSignal.new() -- Signal<number>

function Health.damage(amount: number)
	Health.Damaged:Fire(amount)
end

return Health
```

- **Cleanup:** listeners fire newest first. Call `:Destroy()` on any signal you create when its owner is torn down. If you use Janitor (also in `wally.toml`), add connections with `"Disconnect"` and signals with `"Destroy"`.
- **No new records:** I didn't add a record or `CLAUDE.md` entry, since nothing new was acquired.

If you want a placeholder module in `src/shared` that exposes a signal, I can add one. I held off because `src/shared/init.luau` currently just returns `{}` and I don't know what your modules look like.

---

## Answer C

### Final message

I didn't change any files, because this project already has a signal library: `wally.toml` pins `LemonSignal = "data-oriented-house/lemonsignal@2.0.0"`. That's the same version the bundled `roblox-lemonsignal` skill covers, and `default.project.json` already maps `Packages` into `ReplicatedStorage`. Adding GoodSignal or another library would just duplicate it.

I only read the files and haven't run anything. There's no `Packages/` folder yet and I can't run commands, so the library isn't installed.

To finish setup on your side:
1. Run `wally install`. It creates `Packages/` and `wally.lock`, so commit the lock.
2. Require it from any module with `require(ReplicatedStorage.Packages.LemonSignal)`.
3. Expose events from a module like this:
   ```lua
   local LemonSignal = require(ReplicatedStorage.Packages.LemonSignal)

   local Module = {}
   Module.Changed = LemonSignal.new()

   -- elsewhere: Module.Changed:Fire(value)
   -- consumers: Module.Changed:Connect(function(value) ... end)
   ```
4. Check that `LemonSignal.new()` works in a Studio play test or a Lune script.

I didn't touch `CLAUDE.md` for the same reason: the library isn't being newly adopted, and no `CLAUDE.md` exists yet. The `roblox-lemonsignal` skill is already available for the usage details.

Tell me if you want a specific module wired up with an event, or a different signal library instead.

---

## Answer D

### Final message

LemonSignal is already in this project, so I'm not editing any files. `wally.toml` declares `LemonSignal = "data-oriented-house/lemonsignal@2.0.0"`, and `default.project.json` already maps `Packages` into `ReplicatedStorage.Packages`. That version matches the bundled `roblox-lemonsignal` skill's pin, so there's nothing to add, pin or record.

**What's missing:** there is no `Packages/` folder and no `wally.lock` yet. Rojo won't build until `wally install` creates them, and I can't run commands here. Run it from the project root, then `rojo sourcemap` or `rojo serve`.

**Using it in a module:** require it from the project's mapped path.

```luau
local LemonSignal = require(ReplicatedStorage.Packages.LemonSignal)

local Module = {}
Module.Damaged = LemonSignal.new() -- consumers call Module.Damaged:Connect(fn)

function Module.hit(amount: number)
	Module.Damaged:Fire(amount)
end

return Module
```

- **Cleanup:** call `Destroy()` on a signal you own when you're done with it. In Janitor, add the signal with `"Destroy"` and its connections with `"Disconnect"`.
- **Scope:** `Fire` stays inside one runtime, so use Blink or a RemoteEvent to cross between client and server.

I haven't run or verified any of this. Do you want me to add a specific module that exposes an event?
