--!strict
-- SnowboardClient: starts every client-side effect. Lives in StarterPlayerScripts.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Kit = ReplicatedStorage:WaitForChild("SnowboardKit")
local SnowboardFX = require(Kit:WaitForChild("SnowboardFX"))
local EnvironmentFX = require(Kit:WaitForChild("EnvironmentFX"))

local Ambience = require(script:WaitForChild("Ambience"))
local CameraFX = require(script:WaitForChild("CameraFX"))
local Popup = require(script:WaitForChild("Popup"))
local BoardPicker = require(script:WaitForChild("BoardPicker"))

SnowboardFX.start()
EnvironmentFX.start()
Ambience.start()
CameraFX.start()

SnowboardFX.onLocal(function(_board, kind, airTime)
	local name = kind:match("^trick:(.+)$")
	if not name then
		return
	end
	if name:match("^%d+$") then
		Popup.show(name .. "!", "spin", string.format("%.1fs air", airTime))
	elseif name == "Rail Grind" then
		Popup.show("RAIL GRIND!", "grind")
	else
		Popup.show(name:upper() .. "!", "air", string.format("%.1fs", airTime))
	end
end)

EnvironmentFX.FinishCrossed:Connect(function()
	Popup.show("FINISH!", "finish")
end)

task.spawn(BoardPicker.start)
