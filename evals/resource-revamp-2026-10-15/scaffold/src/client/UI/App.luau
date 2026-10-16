--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local vide = require(ReplicatedStorage.Packages.vide)
local CoinLabel = require(script.Parent.CoinLabel)

local create = vide.create

local App = {}

function App.mount(playerGui: PlayerGui)
	return vide.mount(function()
		return create "ScreenGui" {
			Name = "HUD",
			ResetOnSpawn = false,
			CoinLabel(),
		}
	end, playerGui)
end

return App
