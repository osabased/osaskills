local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Packages = ReplicatedStorage:WaitForChild("Packages")
local ModuleLoader = require(Packages:WaitForChild("ModuleLoader"))
local Client = ReplicatedStorage:WaitForChild("Client")
ModuleLoader.Start(Client)
