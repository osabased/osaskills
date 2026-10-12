local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local ModuleLoader = require(ReplicatedStorage.Packages.ModuleLoader)
ModuleLoader.Start(ServerScriptService.Server)
