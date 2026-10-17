--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Config = require(ReplicatedStorage.Shared.Config)

local player = Players.LocalPlayer
local lastDash = 0

local function onCharacter(character: Model)
	local humanoid = character:WaitForChild("Humanoid") :: Humanoid
	UserInputService.InputBegan:Connect(function(input, processed)
		if processed or input.KeyCode ~= Config.DASH_KEY then
			return
		end
		if os.clock() - lastDash < Config.DASH_COOLDOWN then
			return
		end
		lastDash = os.clock()
		humanoid:Move(humanoid.MoveDirection * 2)
	end)
end

if player.Character then
	onCharacter(player.Character)
end
player.CharacterAdded:Connect(onCharacter)
