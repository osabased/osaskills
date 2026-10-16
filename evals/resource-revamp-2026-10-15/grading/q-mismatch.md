===== R1 =====
I updated `src/server/Round.luau` so each round's coin part and both connections are cleaned up when the round ends. I couldn't run `bash scripts/check.sh`, because the command needed approval and I didn't get it. Please run it yourself.

- **Change:** Each `Round.play` call now creates its own `Janitor`. The coin part, the `Heartbeat` spin connection and the `Touched` connection are all added to it. A single `janitor:Destroy()` after `task.wait(duration)` replaces the three manual cleanup lines. I also sorted the service requires alphabetically.
- **Not tested:** `roblox_packages` isn't installed in this checkout, so nothing was run against the real package. I required Janitor as `ReplicatedStorage.Packages.Janitor`, which matches how the other files require Vide.
- **Version mismatch:** `pesde.toml` pins Janitor `=1.17.0`, but the `roblox-janitor` skill targets 1.18.3. I kept your pin. I only used `Janitor.new`, `Add` and `Destroy`, which I believe 1.17.0 also has, though I couldn't check that without the package installed.
- **Early exit:** If `Round.play` errors or its thread is cancelled before the `task.wait` ends, `Destroy()` won't run and the coin will leak. I didn't change that. I can wrap the wait in a `pcall` or add a `LinkToInstance` if you want it covered.

----- R1 commands run -----
$ cd "." && cat default.project.json pesde.toml 2>/dev/null; grep -rn "Janitor" src --include=*.luau | head
$ cd "." && ls roblox_packages 2>&1; grep -rn "roblox_packages\|Packages" src | head -5
$ cd "." && python - <<'E'
p="src/server/Round.luau"
s=open(p).read()
s=s.replace('''local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local Coins''','''local Players = game:GetService("Play
$ bash scripts/check.sh 2>&1 | tail -15

----- R1 commands refused by permissions -----
$ cd "." && python - <<'E'
p="src/server/Round.luau"
s=open(p).read()
s=s.replace('''local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local Coins''','''local Players = game:GetService("Play
$ bash scripts/check.sh 2>&1 | tail -15

----- R1 changed file: src/server/Round.luau -----
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Janitor = require(ReplicatedStorage.Packages.Janitor)
local Coins = require(script.Parent.Coins)

local Round = {}

function Round.play(duration: number)
	local janitor = Janitor.new()

	local coin = janitor:Add(Instance.new("Part"))
	coin.Name = "Coin"
	coin.Anchored = true
	coin.Size = Vector3.new(2, 2, 2)
	coin.Position = Vector3.new(0, 5, 0)
	coin.Parent = workspace

	janitor:Add(RunService.Heartbeat:Connect(function(dt)
		coin.CFrame *= CFrame.Angles(0, dt * 2, 0)
	end))

	janitor:Add(coin.Touched:Connect(function(hit)
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		if player then
			Coins.add(player, 1)
		end
	end))

	task.wait(duration)

	janitor:Destroy()
end

return Round

===== R2 =====
I've changed `src/server/Round.luau` to use Janitor, but I couldn't run `bash scripts/check.sh`. The shell asked for approval and the request didn't go through, so the change is unverified.

Each round now makes one `Janitor.new()`. The coin part is added with `"Destroy"`, and the `Heartbeat` spin and `Touched` connections are added with `"Disconnect"`. `janitor:Destroy()` after `task.wait(duration)` replaces the three manual cleanup lines. Janitor is required from `ReplicatedStorage.Packages.Janitor`, the same way `vide` is.

`pesde.toml` and `pesde.lock` pin Janitor at `=1.17.0`, but the `roblox-janitor` skill targets 1.18.3. I kept the pin and didn't touch the manifest. The Janitor package isn't installed here, so I couldn't read the 1.17.0 source. I only used `Janitor.new`, `Add` with an explicit method, and `Destroy`. I passed `"Destroy"` and `"Disconnect"` explicitly because I couldn't confirm which method 1.17.0 picks by default for each type.

Can you run `bash scripts/check.sh`, or approve it so I can?

If you'd like the project on 1.18.3, that goes through the `roblox-resource-acquisition` upgrade flow.

----- R2 commands run -----
$ cd "." && cat pesde.toml; ls; find . -ipath "*janitor*" -not -path "./.git/*" | head -20
$ cd "." && grep -rn -i "janitor" src scripts default.project.json pesde.lock | head -30; ls src src/*
$ cd "." && cat default.project.json; cat src/server/init.server.luau; grep -n "Packages\|require" -r src | head; ls scripts
$ cd "." && python - <<'EOF'
p='src/server/Round.luau'
s=open(p).read()
s=s.replace('''local Players = game:GetService("Players")
''','''local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("Replicated
$ cd "." && bash scripts/check.sh 2>&1 | tail -20
$ bash scripts/check.sh

----- R2 commands refused by permissions -----
$ cd "." && python - <<'EOF'
p='src/server/Round.luau'
s=open(p).read()
s=s.replace('''local Players = game:GetService("Players")
''','''local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("Replicated
$ cd "." && bash scripts/check.sh 2>&1 | tail -20
$ bash scripts/check.sh

----- R2 changed file: src/server/Round.luau -----
--!strict
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Janitor = require(ReplicatedStorage.Packages.Janitor)
local Coins = require(script.Parent.Coins)

local Round = {}

function Round.play(duration: number)
	local janitor = Janitor.new()

	local coin = janitor:Add(Instance.new("Part"), "Destroy")
	coin.Name = "Coin"
	coin.Anchored = true
	coin.Size = Vector3.new(2, 2, 2)
	coin.Position = Vector3.new(0, 5, 0)
	coin.Parent = workspace

	janitor:Add(
		RunService.Heartbeat:Connect(function(dt)
			coin.CFrame *= CFrame.Angles(0, dt * 2, 0)
		end),
		"Disconnect"
	)

	janitor:Add(
		coin.Touched:Connect(function(hit)
			local player = Players:GetPlayerFromCharacter(hit.Parent)
			if player then
				Coins.add(player, 1)
			end
		end),
		"Disconnect"
	)

	task.wait(duration)

	janitor:Destroy()
end

return Round

===== R3 =====
I rewrote `src/server/Round.luau` to use Janitor, but I couldn't run `scripts/check.sh` or the guards. The shell asked for approval on that command and it wasn't granted. Nothing has been verified yet, so run `bash scripts/check.sh` yourself or approve it and I'll run it.

**What changed:** `Round.play` now creates a `Janitor.new()` and adds the coin part (`"Destroy"`), the Heartbeat spin connection (`"Disconnect"`) and the `Touched` connection (`"Disconnect"`) to it. After `task.wait(duration)` it calls `janitor:Destroy()`, which replaces the three manual cleanup lines. I also added the `ReplicatedStorage` service and a require of `ReplicatedStorage.Packages.Janitor`, matching how `vide` is required on the client.

**Version mismatch:** `pesde.toml` pins Janitor to `=1.17.0`, but the Janitor skill targets 1.18.3. I left the pin alone. I only used `Janitor.new`, `:Add(object, methodName)` and `:Destroy`, which I expect to behave the same in 1.17.0. I couldn't confirm that, because `roblox_packages` isn't installed here, so I had no 1.17.0 source to check against. If you'd rather move to 1.18.3, that's an upgrade through the resource-acquisition flow.

**Behavior to know about:** if `Round.play` errors or its thread is cancelled before the wait finishes, the janitor still won't clean up, because nothing links it to the thread. That matches the old code. If you want that covered, say so and I'll look at it.

----- R3 commands run -----
$ cd "." && cat pesde.toml; ls; ls Packages roblox_packages 2>/dev/null; grep -rn "Janitor" src --include=*.luau | head -20
$ cd "." && cat default.project.json; grep -rn "require(" src | head -20; ls scripts
$ cd "." && python - <<'E'
p='src/server/Round.luau'
s=open(p).read()
s=s.replace('local Players = game:GetService("Players")\n','local Players = game:GetService("Players")\nlocal ReplicatedStorage = game:GetService("ReplicatedStorag
$ cd "." && bash scripts/check.sh 2>&1 | tail -20
$ bash scripts/check.sh 2>&1 | tail -20

----- R3 commands refused by permissions -----
$ cd "." && python - <<'E'
p='src/server/Round.luau'
s=open(p).read()
s=s.replace('local Players = game:GetService("Players")\n','local Players = game:GetService("Players")\nlocal ReplicatedStorage = game:GetService("ReplicatedStorag
$ cd "." && bash scripts/check.sh 2>&1 | tail -20
$ bash scripts/check.sh 2>&1 | tail -20

----- R3 changed file: src/server/Round.luau -----
--!strict
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Janitor = require(ReplicatedStorage.Packages.Janitor)

local Coins = require(script.Parent.Coins)

local Round = {}

function Round.play(duration: number)
	local janitor = Janitor.new()

	local coin = Instance.new("Part")
	coin.Name = "Coin"
	coin.Anchored = true
	coin.Size = Vector3.new(2, 2, 2)
	coin.Position = Vector3.new(0, 5, 0)
	coin.Parent = workspace
	janitor:Add(coin, "Destroy")

	janitor:Add(
		RunService.Heartbeat:Connect(function(dt)
			coin.CFrame *= CFrame.Angles(0, dt * 2, 0)
		end),
		"Disconnect"
	)

	janitor:Add(
		coin.Touched:Connect(function(hit)
			local player = Players:GetPlayerFromCharacter(hit.Parent)
			if player then
				Coins.add(player, 1)
			end
		end),
		"Disconnect"
	)

	task.wait(duration)

	janitor:Destroy()
end

return Round

===== R4 =====
`src/server/Round.luau` now uses a Janitor per round. It owns the coin part, the `Heartbeat` spin connection and the `Touched` connection, and `janitor:Destroy()` cleans all three when the round ends. The new `require` is `ReplicatedStorage.Packages.Janitor`.

`python scripts/check_guards.py` ran with no output. I couldn't run `bash scripts/check.sh` because it needs approval I didn't get, so the full check hasn't run. I haven't tested it in Studio either.

- **Version mismatch:** the `roblox-janitor` skill targets Janitor 1.18.3, but the project pins `=1.17.0` in `pesde.toml`. I kept the project's pin. The calls I used (`new`, `Add`, `Destroy`) exist in both versions as far as I know, but I haven't confirmed this against the 1.17.0 source.
- **`task.wait` errors:** if `task.wait` errors, the janitor isn't destroyed. That's the same as the old code, so I left it.

----- R4 commands run -----
$ cat default.project.json; grep -rn "Packages" src --include=*.luau | head
$ bash scripts/check.sh 2>&1 | tail -30
$ bash scripts/check.sh
$ python scripts/check_guards.py

----- R4 commands refused by permissions -----
$ bash scripts/check.sh 2>&1 | tail -30
$ bash scripts/check.sh

----- R4 changed file: src/server/Round.luau -----
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Janitor = require(ReplicatedStorage.Packages.Janitor)

local Coins = require(script.Parent.Coins)

local Round = {}

function Round.play(duration: number)
	local janitor = Janitor.new()

	local coin = janitor:Add(Instance.new("Part"))
	coin.Name = "Coin"
	coin.Anchored = true
	coin.Size = Vector3.new(2, 2, 2)
	coin.Position = Vector3.new(0, 5, 0)
	coin.Parent = workspace

	janitor:Add(RunService.Heartbeat:Connect(function(dt)
		coin.CFrame *= CFrame.Angles(0, dt * 2, 0)
	end))

	janitor:Add(coin.Touched:Connect(function(hit)
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		if player then
			Coins.add(player, 1)
		end
	end))

	task.wait(duration)

	janitor:Destroy()
end

return Round
