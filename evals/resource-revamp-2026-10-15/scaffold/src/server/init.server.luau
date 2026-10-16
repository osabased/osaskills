--!strict
local Coins = require(script.Coins)
local Round = require(script.Round)

Coins.start()

while true do
	Round.play(30)
	task.wait(5)
end
