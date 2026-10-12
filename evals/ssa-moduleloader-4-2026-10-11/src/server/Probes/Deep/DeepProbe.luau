local ProbeLog = require(game:GetService("ReplicatedStorage"):WaitForChild("ProbeLog"))

local DeepProbe = {}

function DeepProbe:Init()
	ProbeLog.record("deep-init")
end

return DeepProbe
