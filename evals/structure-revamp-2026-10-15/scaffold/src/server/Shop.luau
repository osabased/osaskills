--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local PlayerData = require(script.Parent.PlayerData)
local Prices = require(ReplicatedStorage.Shared).Prices

local Shop = {}

function Shop.start()
	local remotes = Instance.new("Folder")
	remotes.Name = "Remotes"
	local purchase = Instance.new("RemoteEvent")
	purchase.Name = "PurchaseItem"
	purchase.Parent = remotes
	remotes.Parent = ReplicatedStorage

	purchase.OnServerEvent:Connect(function(player, itemName)
		if type(itemName) ~= "string" then
			return
		end
		local price = Prices[itemName]
		local template = ServerStorage:FindFirstChild(itemName)
		if not price or not template or PlayerData.getCoins(player) < price then
			return
		end
		PlayerData.addCoins(player, -price)
		template:Clone().Parent = player:WaitForChild("Backpack")
	end)
end

return Shop
