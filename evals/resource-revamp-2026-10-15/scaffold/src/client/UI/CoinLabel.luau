--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local vide = require(ReplicatedStorage.Packages.vide)

local create = vide.create

return function()
	return create "TextLabel" {
		Name = "Coins",
		AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 12),
		Size = UDim2.fromOffset(160, 36),
		BackgroundTransparency = 0.3,
		TextScaled = true,
		Text = "Coins: 0",
	}
end
