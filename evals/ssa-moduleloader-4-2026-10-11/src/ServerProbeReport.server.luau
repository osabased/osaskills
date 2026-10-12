local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Packages = ReplicatedStorage:WaitForChild("Packages")
local loader = Packages:WaitForChild("ModuleLoader")
local ProbeLog = require(ReplicatedStorage:WaitForChild("ProbeLog"))

-- Start() sets this attribute after the whole load, Init and Start sequence.
while not loader:GetAttribute("ServerLoaded") do
	loader:GetAttributeChangedSignal("ServerLoaded"):Wait()
end

local failures = 0
local function check(label: string, ok: boolean, note: string)
	if not ok then
		failures += 1
	end
	print(string.format("[probe server] %s  %s  (%s)", if ok then "PASS" else "FAIL", label, note))
end

check("1. any-depth discovery through Folders",
	ProbeLog.count("deep-init") == 1,
	"Server/Probes/Deep/DeepProbe Init ran " .. ProbeLog.count("deep-init") .. "x, want 1")
check("2. module nested under a module is not loaded on its own",
	ProbeLog.count("owner-init") == 1 and ProbeLog.count("helper-init") == 0,
	"Owner Init " .. ProbeLog.count("owner-init") .. "x, Owner/Helper Init " .. ProbeLog.count("helper-init") .. "x; want 1 and 0")
check("3. Start is skipped after a failed Init",
	ProbeLog.count("fail-init-attempted") == 1 and ProbeLog.count("fail-start") == 0,
	"FailInit Init attempted " .. ProbeLog.count("fail-init-attempted") .. "x, Start ran " .. ProbeLog.count("fail-start") .. "x; want 1 and 0")
local selves = ProbeLog.details("base-init")
check("4. inherited Init runs once, on the defining module",
	#selves == 1 and selves[1] == "Base",
	"Base.Init ran " .. #selves .. "x with self = " .. table.concat(selves, ", ") .. "; want once with self = Base")
check("5. IgnoreLoader keeps a module from being required",
	ProbeLog.count("ignored-required") == 0,
	"Ignored was required " .. ProbeLog.count("ignored-required") .. "x, want 0")
print(string.format("[probe server] done: %d failure(s)", failures))
