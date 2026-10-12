local ProbeLog = require(game:GetService("ReplicatedStorage"):WaitForChild("ProbeLog"))

local Base = { Tag = "Base" }
Base.__index = Base

function Base:Init()
	ProbeLog.record("base-init", self.Tag)
end

return Base
