local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Packages = ReplicatedStorage:WaitForChild("Packages")
local loader = Packages:WaitForChild("ModuleLoader")
local ProbeLog = require(ReplicatedStorage:WaitForChild("ProbeLog"))

-- Start() sets this attribute after the whole load, Init and Start sequence.
while not loader:GetAttribute("ClientLoaded") do
	loader:GetAttributeChangedSignal("ClientLoaded"):Wait()
end

local failures = 0
local function check(label: string, ok: boolean, note: string)
	if not ok then
		failures += 1
	end
	print(string.format("[probe client] %s  %s  (%s)", if ok then "PASS" else "FAIL", label, note))
end

check("1. any-depth discovery through Folders (client)",
	ProbeLog.count("client-deep-init") == 1,
	"Client/Ui/Deep/ClientDeepProbe Init ran " .. ProbeLog.count("client-deep-init") .. "x, want 1")
print(string.format("[probe client] done: %d failure(s)", failures))
