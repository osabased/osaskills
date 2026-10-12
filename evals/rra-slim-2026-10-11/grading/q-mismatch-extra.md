# q-mismatch (additional answers)

Prompt: In src/server/init.server.luau, spawn a part each round and use Janitor to clean up the part and a Heartbeat connection when the round ends. Make the edit (you can't run commands).

---

## Answer E

### Final message

I edited `src/server/init.server.luau`. I couldn't run or test it.

- **Each round:** `startRound()` makes a Janitor and spawns an anchored part in `workspace`. It adds the part to the Janitor (cleanup calls `Destroy`) and adds a `Heartbeat` connection that rotates the part (cleanup calls `Disconnect`). It returns an end-of-round function that calls `janitor:Destroy()`, which cleans up both.
- **Round loop:** The project had no round system, so I added a placeholder loop. It runs a round for 30 seconds (`ROUND_LENGTH`), ends it, waits 5 seconds, and repeats. Replace the `task.wait(ROUND_LENGTH)` with your real round-end signal.
- **Janitor path:** It's required from `ReplicatedStorage.Packages.Janitor`, which matches `default.project.json`. I didn't check that `Packages/` exists, since I couldn't run commands.
- **Version mismatch:** `wally.toml` pins Janitor at `1.17.0`, while the Janitor skill targets `1.18.3`. I kept your pin. The calls I used (`new`, `Add`, `Destroy`) are basic API, so I don't expect a problem on 1.17.0, but I didn't check its source.

### File written: src\server\init.server.luau

```
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Janitor = require(ReplicatedStorage.Packages.Janitor)

local ROUND_LENGTH = 30

print("server")

local function startRound(): () -> ()
	local janitor = Janitor.new()

	local part = janitor:Add(Instance.new("Part"))
	part.Name = "RoundPart"
	part.Anchored = true
	part.Position = Vector3.new(0, 10, 0)
	part.Parent = workspace

	janitor:Add(RunService.Heartbeat:Connect(function(dt)
		part.CFrame *= CFrame.Angles(0, dt, 0)
	end))

	-- Call the returned function when the round ends.
	return function()
		janitor:Destroy()
	end
end

-- Placeholder round loop; replace the task.wait with the real round-end signal.
task.spawn(function()
	while true do
		local endRound = startRound()
		task.wait(ROUND_LENGTH)
		endRound()
		task.wait(5) -- intermission
	end
end)

```

---

## Answer F

### Final message

I edited `src/server/init.server.luau`. Nothing has been run or tested, since you said I couldn't.

- **Each round:** `runRound()` creates a Janitor and spawns an anchored `RoundPart` in `workspace`. It also connects a `Heartbeat` handler that bobs the part up and down.
- **Cleanup:** both the part and the connection are added to the Janitor. When the round ends, `janitor:Destroy()` destroys the part and disconnects `Heartbeat`.
- **Loop:** rounds repeat forever, each lasting `ROUND_LENGTH = 30` seconds with a 5-second intermission. The project had no round system, so I made up that loop and the timings. If you have a real round start/end signal, swap it in for the `task.wait(ROUND_LENGTH)`.
- **Janitor path:** the script requires it from `ReplicatedStorage.Packages.Janitor`, which matches `default.project.json`.

Janitor is pinned to `howmanysmall/janitor@1.17.0` in `wally.toml`, but the Janitor skill targets 1.18.3. I kept the project's pin. The calls I used (`new`, `Add`, `Destroy`) are core API and should work in 1.17.0, but I couldn't confirm that against the installed version.

`Packages/` didn't exist in the project when I searched, so run `wally install` before syncing.

### File written: src\server\init.server.luau

```
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Janitor = require(ReplicatedStorage.Packages.Janitor)

local ROUND_LENGTH = 30
local INTERMISSION = 5

print("server")

local function runRound()
	local janitor = Janitor.new()

	local part = janitor:Add(Instance.new("Part"))
	part.Name = "RoundPart"
	part.Anchored = true
	part.Position = Vector3.new(0, 10, 0)
	part.Parent = workspace

	local origin = part.Position
	local elapsed = 0
	janitor:Add(RunService.Heartbeat:Connect(function(dt)
		elapsed += dt
		part.Position = origin + Vector3.new(0, math.sin(elapsed * 2) * 2, 0)
	end))

	task.wait(ROUND_LENGTH)

	-- Round ended: destroys the part and disconnects Heartbeat.
	janitor:Destroy()
end

task.spawn(function()
	while true do
		runRound()
		task.wait(INTERMISSION)
	end
end)

```
