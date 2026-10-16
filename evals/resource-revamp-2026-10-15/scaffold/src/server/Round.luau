--!strict
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local Coins = require(script.Parent.Coins)

local Round = {}

function Round.play(duration: number)
	local coin = Instance.new("Part")
	coin.Name = "Coin"
	coin.Anchored = true
	coin.Size = Vector3.new(2, 2, 2)
	coin.Position = Vector3.new(0, 5, 0)
	coin.Parent = workspace

	local spin = RunService.Heartbeat:Connect(function(dt)
		coin.CFrame *= CFrame.Angles(0, dt * 2, 0)
	end)

	local touched = coin.Touched:Connect(function(hit)
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		if player then
			Coins.add(player, 1)
		end
	end)

	task.wait(duration)

	spin:Disconnect()
	touched:Disconnect()
	coin:Destroy()
end

return Round
