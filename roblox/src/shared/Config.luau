--!strict
--[[
	SnowboardKit configuration.

	After uploading the sounds (roblox/sfx/*.ogg) and particle textures
	(roblox/textures/*.png) to Roblox, paste their ids here as "rbxassetid://123".
	Anything left empty falls back to a built-in Roblox texture, or stays silent.
]]

local Config = {}

Config.Sounds = {
	Carve = "", -- carve_loop.ogg
	Wind = "", -- wind_loop.ogg
	Grind = "", -- grind_loop.ogg
	Campfire = "", -- campfire_loop.ogg
	Land = "", -- land_thump.ogg
	Jump = "", -- jump_pop.ogg
	Whoosh = "", -- trick_whoosh.ogg
	TrickSuccess = "", -- trick_success.ogg
	Powder = "", -- powder_burst.ogg
	Equip = "", -- equip_click.ogg
	UISelect = "", -- ui_select.ogg
}

-- Built-in engine textures are used until you upload the custom ones.
Config.Textures = {
	SnowPuff = "rbxasset://textures/particles/smoke_main.dds", -- fx_snow_puff.png
	Snowflake = "rbxasset://textures/particles/sparkles_main.dds", -- fx_snowflake.png
	Sparkle = "rbxasset://textures/particles/sparkles_main.dds", -- fx_sparkle.png
	Spark = "rbxasset://textures/particles/sparkles_main.dds", -- fx_spark.png
	Streak = "rbxasset://textures/particles/sparkles_main.dds", -- fx_streak.png
	Flame = "rbxasset://textures/particles/fire_main.dds", -- fx_flame.png
	Smoke = "rbxasset://textures/particles/smoke_main.dds", -- fx_smoke.png
	Confetti = "rbxasset://textures/particles/sparkles_main.dds", -- fx_confetti.png
}

Config.Board = {
	Lift = 0.22, -- studs the character is raised so the feet sit on the bindings
	GroundRay = 3.5, -- how far below the board counts as "on the snow"
	SprayMinSpeed = 6, -- studs/s before snow starts spraying
	SprayMaxRate = 160, -- particles/s at full speed + hard carve
	GlowTrailSpeed = 32, -- glow trail turns on above this speed
	LandMinAirTime = 0.35, -- seconds in the air before a landing burst plays
	SpinTolerance = 45, -- degrees of slack when naming spins (a 320 spin counts as a 360)
	BigAirTime = 1.4,
	HugeAirTime = 2.4,
	GrindMinTime = 0.5,
	SoundMaxDistance = 90,
}

Config.Camera = {
	BaseFov = 70,
	MaxFovBoost = 16, -- extra FOV at top speed
	FovSpeedLow = 25,
	FovSpeedHigh = 90,
	SpeedLines = true,
	SpeedLinesFrom = 55,
	LandShake = true,
}

Config.Ambience = {
	Snowfall = true,
	SnowRate = 70, -- multiplied by Lighting attribute "SnowIntensity" (set by the lighting presets)
	WindVolume = 0.25,
}

-- Folder in ReplicatedStorage holding the board models players can pick.
Config.BoardsFolder = "Snowboards"
Config.DefaultBoard = "board_rookie"

return Config
