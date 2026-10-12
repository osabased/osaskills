local ProbeLog = require(game:GetService("ReplicatedStorage"):WaitForChild("ProbeLog"))

local FailInit = {}

function FailInit:Init()
	ProbeLog.record("fail-init-attempted")
	error("probe: deliberate Init failure (expected)")
end

function FailInit:Start()
	ProbeLog.record("fail-start")
end

return FailInit
