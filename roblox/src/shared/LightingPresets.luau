--!strict
--[[
	Lighting / atmosphere / post-processing presets for a snowy mountain.

	Studio (Command Bar):   require(game.ReplicatedStorage.SnowboardKit.LightingPresets).apply("SunnyPowder")
	In game (server):        same call - e.g. switch to "Blizzard" for a storm event.

	Presets: SunnyPowder, GoldenHour, Blizzard, Night
	Also sets Lighting attribute "SnowIntensity", which drives the falling snow.
]]

local Lighting = game:GetService("Lighting")

local LightingPresets = {}

type Preset = {
	clock: number,
	brightness: number,
	ambient: Color3,
	outdoor: Color3,
	exposure: number,
	shadowSoftness: number,
	atmosphere: { density: number, offset: number, color: Color3, decay: Color3, glare: number, haze: number },
	bloom: { intensity: number, size: number, threshold: number },
	cc: { brightness: number, contrast: number, saturation: number, tint: Color3 },
	sunRays: { intensity: number, spread: number },
	dof: { far: number, focus: number, radius: number },
	stars: number,
	snow: number,
}

local rgb = Color3.fromRGB

LightingPresets.presets = {
	SunnyPowder = {
		clock = 13.6,
		brightness = 3.2,
		ambient = rgb(70, 82, 100),
		outdoor = rgb(150, 160, 180),
		exposure = 0.05,
		shadowSoftness = 0.3,
		atmosphere = {
			density = 0.3,
			offset = 0.2,
			color = rgb(199, 220, 242),
			decay = rgb(110, 140, 178),
			glare = 0.35,
			haze = 1.4,
		},
		bloom = { intensity = 0.55, size = 26, threshold = 1.7 },
		cc = { brightness = 0.02, contrast = 0.12, saturation = 0.1, tint = rgb(246, 250, 255) },
		sunRays = { intensity = 0.05, spread = 0.7 },
		dof = { far = 0.12, focus = 60, radius = 140 },
		stars = 0,
		snow = 0.5,
	} :: Preset,
	GoldenHour = {
		clock = 17.35,
		brightness = 2.4,
		ambient = rgb(90, 70, 80),
		outdoor = rgb(170, 140, 140),
		exposure = 0.15,
		shadowSoftness = 0.2,
		atmosphere = {
			density = 0.33,
			offset = 0.25,
			color = rgb(255, 208, 172),
			decay = rgb(150, 96, 124),
			glare = 1.4,
			haze = 2.0,
		},
		bloom = { intensity = 0.85, size = 30, threshold = 1.45 },
		cc = { brightness = 0.03, contrast = 0.15, saturation = 0.18, tint = rgb(255, 240, 226) },
		sunRays = { intensity = 0.12, spread = 0.9 },
		dof = { far = 0.15, focus = 70, radius = 150 },
		stars = 0,
		snow = 0.3,
	} :: Preset,
	Blizzard = {
		clock = 12.5,
		brightness = 1.3,
		ambient = rgb(120, 128, 140),
		outdoor = rgb(170, 178, 190),
		exposure = 0.2,
		shadowSoftness = 0.8,
		atmosphere = {
			density = 0.6,
			offset = 0.05,
			color = rgb(214, 222, 236),
			decay = rgb(172, 182, 200),
			glare = 0,
			haze = 3.6,
		},
		bloom = { intensity = 0.4, size = 24, threshold = 1.9 },
		cc = { brightness = 0.04, contrast = -0.05, saturation = -0.25, tint = rgb(236, 242, 255) },
		sunRays = { intensity = 0, spread = 0.5 },
		dof = { far = 0.3, focus = 40, radius = 90 },
		stars = 0,
		snow = 3.2,
	} :: Preset,
	Night = {
		clock = 21.6,
		brightness = 0.7,
		ambient = rgb(40, 48, 78),
		outdoor = rgb(60, 72, 112),
		exposure = 0.35,
		shadowSoftness = 0.35,
		atmosphere = {
			density = 0.34,
			offset = 0.1,
			color = rgb(70, 92, 140),
			decay = rgb(40, 50, 90),
			glare = 0,
			haze = 1.2,
		},
		bloom = { intensity = 1.1, size = 34, threshold = 1.2 },
		cc = { brightness = 0.02, contrast = 0.18, saturation = 0.05, tint = rgb(220, 230, 255) },
		sunRays = { intensity = 0, spread = 0.5 },
		dof = { far = 0.1, focus = 60, radius = 140 },
		stars = 5000,
		snow = 0.8,
	} :: Preset,
}

local function ensure(className: string, name: string): Instance
	local found = Lighting:FindFirstChild(name)
	if found and found.ClassName == className then
		return found
	end
	local inst = Instance.new(className :: any)
	inst.Name = name
	inst.Parent = Lighting
	return inst
end

function LightingPresets.apply(name: string)
	local p = LightingPresets.presets[name]
	if not p then
		error("Unknown lighting preset '" .. name .. "'")
	end
	pcall(function()
		(Lighting :: any).Technology = Enum.Technology.Future -- only allowed from Studio
	end)
	Lighting.ClockTime = p.clock
	Lighting.Brightness = p.brightness
	Lighting.Ambient = p.ambient
	Lighting.OutdoorAmbient = p.outdoor
	Lighting.ExposureCompensation = p.exposure
	Lighting.ShadowSoftness = p.shadowSoftness
	Lighting.GlobalShadows = true
	Lighting.EnvironmentDiffuseScale = 1
	Lighting.EnvironmentSpecularScale = 1
	Lighting.GeographicLatitude = 42

	local atm = ensure("Atmosphere", "SnowAtmosphere") :: Atmosphere
	atm.Density = p.atmosphere.density
	atm.Offset = p.atmosphere.offset
	atm.Color = p.atmosphere.color
	atm.Decay = p.atmosphere.decay
	atm.Glare = p.atmosphere.glare
	atm.Haze = p.atmosphere.haze

	local sky = Lighting:FindFirstChildOfClass("Sky")
	if not sky then
		local s = Instance.new("Sky")
		s.Parent = Lighting
		sky = s
	end
	if sky then
		sky.StarCount = p.stars
		sky.SunAngularSize = 14
		sky.MoonAngularSize = 9
		sky.CelestialBodiesShown = true
	end

	local bloom = ensure("BloomEffect", "SnowBloom") :: BloomEffect
	bloom.Intensity = p.bloom.intensity
	bloom.Size = p.bloom.size
	bloom.Threshold = p.bloom.threshold

	local cc = ensure("ColorCorrectionEffect", "SnowColor") :: ColorCorrectionEffect
	cc.Brightness = p.cc.brightness
	cc.Contrast = p.cc.contrast
	cc.Saturation = p.cc.saturation
	cc.TintColor = p.cc.tint

	local rays = ensure("SunRaysEffect", "SnowSunRays") :: SunRaysEffect
	rays.Intensity = p.sunRays.intensity
	rays.Spread = p.sunRays.spread

	local dof = ensure("DepthOfFieldEffect", "SnowDepth") :: DepthOfFieldEffect
	dof.FarIntensity = p.dof.far
	dof.NearIntensity = 0
	dof.FocusDistance = p.dof.focus
	dof.InFocusRadius = p.dof.radius

	Lighting:SetAttribute("SnowIntensity", p.snow)
	Lighting:SetAttribute("LightingPreset", name)

	-- snowy terrain palette
	local terrain = workspace.Terrain
	terrain:SetMaterialColor(Enum.Material.Snow, rgb(236, 243, 252))
	terrain:SetMaterialColor(Enum.Material.Glacier, rgb(168, 212, 240))
	terrain:SetMaterialColor(Enum.Material.Ice, rgb(150, 200, 236))
	terrain:SetMaterialColor(Enum.Material.Rock, rgb(108, 110, 120))
	terrain:SetMaterialColor(Enum.Material.Slate, rgb(92, 96, 108))
	terrain:SetMaterialColor(Enum.Material.Basalt, rgb(70, 72, 82))
	terrain:SetMaterialColor(Enum.Material.Grass, rgb(96, 128, 96))
	terrain:SetMaterialColor(Enum.Material.LeafyGrass, rgb(86, 120, 92))
end

return LightingPresets
