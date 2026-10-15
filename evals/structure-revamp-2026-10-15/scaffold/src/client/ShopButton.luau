--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ShopButton = {}

function ShopButton.start()
	local gui = Instance.new("ScreenGui")
	gui.Name = "ShopGui"
	gui.ResetOnSpawn = false

	local button = Instance.new("TextButton")
	button.Name = "BuySword"
	button.Text = "Buy Sword (50)"
	button.Size = UDim2.fromOffset(160, 40)
	button.Position = UDim2.new(1, -180, 1, -60)
	button.Parent = gui

	local purchase = ReplicatedStorage:WaitForChild("Remotes"):WaitForChild("PurchaseItem") :: RemoteEvent
	button.Activated:Connect(function()
		purchase:FireServer("Sword")
	end)

	gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
end

return ShopButton
