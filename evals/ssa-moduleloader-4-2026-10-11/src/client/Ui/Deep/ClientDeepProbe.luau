local ProbeLog = require(game:GetService("ReplicatedStorage"):WaitForChild("ProbeLog"))

local ClientDeepProbe = {}

function ClientDeepProbe:Init()
	ProbeLog.record("client-deep-init")
end

return ClientDeepProbe
