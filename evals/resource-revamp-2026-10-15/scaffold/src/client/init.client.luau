--!strict
local Players = game:GetService("Players")

local App = require(script.UI.App)

App.mount(Players.LocalPlayer:WaitForChild("PlayerGui") :: PlayerGui)
