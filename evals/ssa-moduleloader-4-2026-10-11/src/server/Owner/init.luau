local ProbeLog = require(game:GetService("ReplicatedStorage"):WaitForChild("ProbeLog"))

local Owner = {}

function Owner:Init()
	ProbeLog.record("owner-init")
end

return Owner
