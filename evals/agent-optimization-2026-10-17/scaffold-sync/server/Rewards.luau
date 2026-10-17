--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.Config)

local Rewards = {}

function Rewards.start()
	Players.PlayerAdded:Connect(function(player)
		local stats = Instance.new("Folder")
		stats.Name = "leaderstats"
		local coins = Instance.new("IntValue")
		coins.Name = "Coins"
		coins.Value = Config.STARTING_COINS
		coins.Parent = stats
		stats.Parent = player
	end)
end

return Rewards
