--!strict
local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")

local store = DataStoreService:GetDataStore("PlayerData_v3")
local KEY_PREFIX = "player_"

local coins: { [Player]: number } = {}

local PlayerData = {}

function PlayerData.getCoins(player: Player): number
	return coins[player] or 0
end

function PlayerData.addCoins(player: Player, amount: number)
	coins[player] = PlayerData.getCoins(player) + amount
	player:SetAttribute("Coins", coins[player])
end

function PlayerData.start()
	Players.PlayerAdded:Connect(function(player)
		local ok, saved = pcall(store.GetAsync, store, KEY_PREFIX .. player.UserId)
		coins[player] = if ok and type(saved) == "number" then saved else 100
		player:SetAttribute("Coins", coins[player])
	end)
	Players.PlayerRemoving:Connect(function(player)
		pcall(store.SetAsync, store, KEY_PREFIX .. player.UserId, coins[player])
		coins[player] = nil
	end)
end

return PlayerData
