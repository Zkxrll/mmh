--!strict
-- SetupLighting  (paste into the Studio Command Bar and press Enter)
-- Needs SnowboardKit installed in ReplicatedStorage. Presets: SunnyPowder, GoldenHour, Blizzard, Night

local PRESET = "SunnyPowder"

local kit = game:GetService("ReplicatedStorage"):FindFirstChild("SnowboardKit")
local module = kit and kit:FindFirstChild("LightingPresets")
if not module or not module:IsA("ModuleScript") then
	error("Install SnowboardKit first (ReplicatedStorage.SnowboardKit.LightingPresets not found)")
end
local recording = game:GetService("ChangeHistoryService"):TryBeginRecording("SetupLighting")
local LightingPresets = (require :: any)(module) -- dynamic require from the Command Bar
LightingPresets.apply(PRESET)
if recording then
	game:GetService("ChangeHistoryService"):FinishRecording(recording, Enum.FinishRecordingOperation.Commit)
end
print("[SetupLighting] applied " .. PRESET)
