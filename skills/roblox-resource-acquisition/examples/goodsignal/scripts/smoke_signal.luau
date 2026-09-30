--!strict
-- Maintained representative fixture; adapt only the project's installation path.
local Signal = require(game:GetService("ReplicatedStorage"):WaitForChild("Packages"):WaitForChild("GoodSignal") :: ModuleScript)
local signal = Signal.new()
local active = true
local connection: any = nil
local callbackCount = 0
local received: string? = nil

local function cleanup()
    if not active then
        return
    end
    active = false
    if connection then
        connection:Disconnect()
        connection = nil
    end
    signal:DisconnectAll()
end

local ok, problem = pcall(function()
    connection = signal:Connect(function(payload: string)
        if active then
            callbackCount += 1
            received = payload
        end
    end)
    signal:Fire("ready")
    task.wait()
    assert(callbackCount == 1 and received == "ready", "payload was not delivered once")
    cleanup()
    cleanup()
    signal:Fire("after-cleanup")
    task.wait()
    assert(callbackCount == 1, "callback ran after disconnection")
end)
cleanup()
assert(ok, tostring(problem))
print("goodsignal-ready")
