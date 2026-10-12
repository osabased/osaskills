===== R1 =====
`network/main.blink`:

```blink
option ServerOutput = "../src/server/Network/Server.luau"
option ClientOutput = "../src/client/Network/Client.luau"
option RemoteScope = "MyGame"

event DamageNumber {
	From: Server,
	Type: Reliable,
	Call: ManyAsync,
	Data: (Position: vector, Amount: u16),
}

event AimDirection {
	From: Client,
	Type: Unreliable,
	Call: SingleAsync,
	Data: vector,
}

function GetLoadout {
	Yield: Coroutine,
	Return: string(1..32)[0..6],
}
```

I used `Data: (Position: vector, Amount: u16)` for `DamageNumber`, which sends two values. I'm going from the skill's note that `(A, B)` sends several values, and I haven't compiled it. If the compiler rejects the labels, use `(vector, u16)`. Handlers and `Fire` then take positional arguments.

Compile with `pesde run blink -- network/main`.

**Server** (`ServerScriptService`):

```luau
local Net = require(script.Parent.Network.Server)

-- Unreliable client -> server
Net.AimDirection.On(function(player, direction)
	-- Types are not authorization: sanity-check the vector here (e.g. magnitude)
	player:SetAttribute("AimDirection", direction)
end)

-- Client-invoked function: return up to 6 item ids
Net.GetLoadout.On(function(player)
	return { "sword_01", "shield_02", "potion_hp" }
end)

-- Reliable server -> client
local function showDamage(player: Player, position: Vector3, amount: number)
	Net.DamageNumber.Fire(player, position, amount)
	-- or Net.DamageNumber.FireAll(position, amount)
end
```

**Client** (`StarterPlayerScripts`):

```luau
local Net = require(script.Parent.Network.Client)

Net.DamageNumber.On(function(position, amount)
	print(("-%d at %s"):format(amount, tostring(position)))
end)

-- Yields until the server replies
local loadout = Net.GetLoadout.Invoke()
for _, itemId in loadout do
	print(itemId)
end

-- Send aim every frame (unreliable, so drops are fine)
game:GetService("RunService").RenderStepped:Connect(function()
	local camera = workspace.CurrentCamera
	Net.AimDirection.Fire(camera.CFrame.LookVector)
end)
```

Notes:
- **Receive-side risk:** Blink 0.18.9 parses the whole incoming buffer before any handler runs (issue #45). `AimDirection` is untrusted client-to-server traffic, so the schema bounds don't protect the parser. Before shipping, add a tested byte and rate budget on the receive path, or report the risk to the project owner.
- **Server-side checks:** the bounds on `GetLoadout` only shape the data. Build the loadout from the player's real data on the server.
- **Unreliable limit:** unreliable payloads are capped at 1000 bytes. A single vector is well under that.
- **Require timing:** requiring a generated module starts networking. Require `Server` and `Client` only where you want networking live.


===== R2 =====
I wrote this from memory of Blink's syntax. I didn't check it against 0.18.9 or compile it, so run the compiler once to confirm.

**network/main.blink**
```
option ServerOutput = "../src/server/Network.luau"
option ClientOutput = "../src/client/Network.luau"
option Casing = Pascal

event DamageNumber {
	From: Server,
	Type: Reliable,
	Call: SingleSync,
	Data: struct {
		Position: vector,
		Amount: u16,
	},
}

event AimDirection {
	From: Client,
	Type: Unreliable,
	Call: SingleSync,
	Data: vector,
}

function GetLoadout {
	Yield: Coroutine,
	Return: string[..6],
}
```

The `Yield` field is required on functions. `Coroutine` makes the client call block like a normal function call. `Future` and `Promise` are the alternatives. `string[..6]` is an array of 0 to 6 strings.

**Server** (for example `src/server/Main.server.luau`)
```lua
local Players = game:GetService("Players")
local Network = require(script.Parent.Network)

-- client -> server (unreliable)
Network.AimDirection.On(function(player: Player, direction: Vector3)
	-- store/use the aim direction for this player
end)

-- client-invoked function: return up to 6 item ids
Network.GetLoadout.On(function(player: Player)
	return { "sword_01", "shield_02", "potion_hp" }
end)

-- server -> client (reliable)
local function showDamage(target: Player, position: Vector3, amount: number)
	Network.DamageNumber.Fire(target, {
		Position = position,
		Amount = amount, -- must fit u16 (0..65535)
	})
end

-- or broadcast
Network.DamageNumber.FireAll({ Position = Vector3.new(0, 10, 0), Amount = 42 })
```

**Client** (for example `src/client/Main.client.luau`)
```lua
local Network = require(script.Parent.Network)

-- server -> client
Network.DamageNumber.On(function(data)
	print(("-%d at %s"):format(data.Amount, tostring(data.Position)))
end)

-- client -> server (unreliable); fire it often, for example every frame
game:GetService("RunService").RenderStepped:Connect(function()
	local camera = workspace.CurrentCamera
	Network.AimDirection.Fire(camera.CFrame.LookVector)
end)

-- request loadout (yields until the server returns)
local loadout = Network.GetLoadout.Invoke()
for _, itemId in loadout do
	print(itemId)
end
```

Notes:
- Adjust the two `*Output` paths to your project layout. The server and client modules must be generated into locations each side can `require`.
- Generate the modules with `blink network/main.blink`. If Blink is installed through pesde, use `pesde run blink network/main.blink`.
- If the compiler rejects `option Casing = Pascal`, remove it. Pascal is the default.


===== R3 =====
`network/main.blink`:

```
option ServerOutput = "src/server/Network.luau"
option ClientOutput = "src/client/Network.luau"

event DamageNumber {
	From: Server,
	Type: Reliable,
	Call: SingleSync,
	Data: (Position: vector, Amount: u16),
}

event AimDirection {
	From: Client,
	Type: Unreliable,
	Call: SingleSync,
	Data: vector,
}

function GetLoadout {
	Yield: Coroutine,
	Return: string[..6],
}
```

**Server** (`ServerScriptService`):

```lua
local Network = require(path.to.server.Network)

-- client -> server, unreliable
Network.AimDirection.On(function(player: Player, direction: vector)
	-- use direction for the player's aim
end)

-- server -> client, reliable
local function showDamage(player: Player, position: vector, amount: number)
	Network.DamageNumber.Fire(player, position, amount)
	-- also: FireAll(position, amount), FireExcept(player, position, amount), FireList({ ... }, position, amount)
end

-- loadout function: return at most 6 item id strings
Network.GetLoadout.SetCallback(function(player: Player)
	return { "sword_01", "bow_02", "potion_hp" }
end)
```

**Client** (`LocalScript`):

```lua
local Network = require(path.to.client.Network)

Network.DamageNumber.On(function(position: vector, amount: number)
	-- spawn a floating damage number at position
end)

-- send aim direction (e.g. every frame or on a timer)
Network.AimDirection.Fire(vector.create(0, 0, -1))

-- Yield: Coroutine, so Invoke blocks until the server returns
local loadout = Network.GetLoadout.Invoke()
for _, itemId in loadout do
	print(itemId)
end
```

Notes:
- I wrote this from memory of Blink's syntax. I didn't check it against the 0.18.9 docs or run the compiler, so run `blink network/main.blink` to confirm it compiles.
- The `ServerOutput` and `ClientOutput` paths are placeholders, so change them to match your project layout.
- Because `Data` is a tuple, `Fire` and `On` take positional arguments. If you'd rather pass a table, write `Data: struct { Position: vector, Amount: u16 }` instead. Then `Fire(player, { Position = ..., Amount = ... })` and the `On` callback receives that table.
- `Yield: Coroutine` makes `Invoke` yield like a normal call. You can use `Future` or `Promise` instead if you want those return types.
- Blink enforces the `[..6]` limit on both ends, so a server callback that returns more than 6 strings will error.


===== R4 =====
```blink
-- network/main.blink
option ServerOutput = "../src/server/Network/Server.luau"
option ClientOutput = "../src/client/Network/Client.luau"
option TypesOutput  = "../src/shared/Network/Types.luau"
option RemoteScope  = "MyGame"

struct DamageInfo {
	Position: vector,
	Amount: u16,
}

event DamageNumber {
	From: Server,
	Type: Reliable,
	Call: ManyAsync,
	Data: DamageInfo,
}

event AimDirection {
	From: Client,
	Type: Unreliable,
	Call: SingleAsync,
	Data: vector,
}

function GetLoadout {
	Yield: Coroutine,
	Return: string(1..32)[0..6],
}
```

Compile it with `pesde run blink -- network/main`. This writes the three outputs at the paths in the options. Paths are relative to the schema file, so `network/` is the base here. Adjust them to your Rojo layout.

**Server** (`ServerScriptService`)
```luau
local ServerScriptService = game:GetService("ServerScriptService")
local Net = require(ServerScriptService.Network.Server)

-- Client -> server, unreliable. The type only guarantees a vector, so check it.
local aim: { [Player]: vector } = {}
Net.AimDirection.On(function(player, direction)
	if direction.Magnitude < 0.5 or direction.Magnitude > 1.5 then return end -- must be ~unit length
	aim[player] = direction.Unit
end)

-- Client-invoked function. Return at most 6 ids, from server-owned data.
Net.GetLoadout.On(function(player)
	local ids = getLoadoutFor(player) -- your own lookup
	return table.move(ids, 1, math.min(#ids, 6), 1, {})
end)

-- Server -> client damage popup
local function showDamage(player: Player, position: vector, amount: number)
	Net.DamageNumber.Fire(player, { Position = position, Amount = math.clamp(amount, 0, 65535) })
end
-- Also available: Net.DamageNumber.FireAll(info), FireList(players, info), FireExcept(player, info)
```

**Client** (`StarterPlayerScripts`)
```luau
local Net = require(script.Parent.Network.Client)

Net.DamageNumber.On(function(info)
	spawnDamageNumber(info.Position, info.Amount)
end)

-- Throttle unreliable sends, e.g. once per frame at most
game:GetService("RunService").RenderStepped:Connect(function()
	local look = workspace.CurrentCamera.CFrame.LookVector
	Net.AimDirection.Fire(look)
end)

-- Yields until the server replies
local loadout = Net.GetLoadout.Invoke() -- { string }
```

Notes:
- **Receive-side DoS:** 0.18.9 parses the whole incoming buffer before any handler runs (issue #45). `AimDirection` is untrusted client-to-server input, so the schema bounds and handler checks don't protect the parser. Add a tested pre-decode byte and rate budget before shipping it. Don't silently patch the generated code.
- **Item id bounds:** `string(1..32)` and `[0..6]` are my choices for the 6-item limit. Change them if your ids differ. Because the limit is in the schema, the generated code should reject longer arrays when serializing.
- **Requiring starts networking:** requiring a generated module immediately creates the remotes on the server and makes the client wait for them. Require them only when you want networking live.
- **Call modes:** I used the `Async` modes, so handlers may yield.
- **Unverified:** I haven't compiled this schema, so the `[0..6]` array bound syntax is untested against 0.18.9. If the compiler rejects it, check `references/schema.md`.
