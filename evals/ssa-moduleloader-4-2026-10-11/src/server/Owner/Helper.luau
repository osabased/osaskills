local ProbeLog = require(game:GetService("ReplicatedStorage"):WaitForChild("ProbeLog"))

local Helper = {}

-- Must never run: the loader should not load a module nested under another module.
function Helper:Init()
	ProbeLog.record("helper-init")
end

return Helper
