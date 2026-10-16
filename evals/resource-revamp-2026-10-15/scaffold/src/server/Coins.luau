--!strict
local Players = game:GetService("Players")

local Coins = {}

local balances: { [Player]: number } = {}

function Coins.get(player: Player): number
	return balances[player] or 0
end

function Coins.add(player: Player, amount: number)
	balances[player] = Coins.get(player) + amount
end

function Coins.start()
	Players.PlayerAdded:Connect(function(player)
		balances[player] = 0
	end)
	Players.PlayerRemoving:Connect(function(player)
		balances[player] = nil
	end)
end

return Coins
