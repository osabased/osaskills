local ProbeLog = require(game:GetService("ReplicatedStorage"):WaitForChild("ProbeLog"))

-- Recorded at require time: the loader should never require this module.
ProbeLog.record("ignored-required")

return {}
