--!strict
-- Falling snow that follows the camera + a soft ambient wind bed.
-- Snow amount follows the Lighting attribute "SnowIntensity" (set by the lighting presets).

local Lighting = game:GetService("Lighting")
local RunService = game:GetService("RunService")
local SoundService = game:GetService("SoundService")

local Kit = game:GetService("ReplicatedStorage"):WaitForChild("SnowboardKit")
local Config = require(Kit:WaitForChild("Config"))
local Effects = require(Kit:WaitForChild("Effects"))

local Ambience = {}

function Ambience.start()
	local camera = workspace.CurrentCamera
	if Config.Ambience.Snowfall then
		local emitterPart = Instance.new("Part")
		emitterPart.Name = "SnowfallEmitter"
		emitterPart.Anchored = true
		emitterPart.CanCollide = false
		emitterPart.CanQuery = false
		emitterPart.CanTouch = false
		emitterPart.CastShadow = false
		emitterPart.Transparency = 1
		emitterPart.Size = Vector3.new(140, 1, 140)
		emitterPart.Parent = camera

		local flakes = Effects.emitter(emitterPart, "Snow", {
			texture = Config.Textures.Snowflake,
			lifetime = NumberRange.new(7, 11),
			speed = NumberRange.new(3, 6),
			spread = Vector2.new(15, 15),
			size = Effects.seq({ { 0, 0.18 }, { 0.5, 0.3 }, { 1, 0.2 } }),
			transparency = Effects.seq({ { 0, 1 }, { 0.08, 0.15 }, { 0.85, 0.2 }, { 1, 1 } }),
			color = Effects.colors(Color3.fromRGB(255, 255, 255)),
			acceleration = Vector3.new(2.5, -0.5, 1),
			rotSpeed = NumberRange.new(-120, 120),
			lightEmission = 0.25,
			direction = Enum.NormalId.Bottom,
		})

		local t = 0
		RunService.RenderStepped:Connect(function(dt: number)
			t += dt
			local pos = camera.CFrame.Position
			emitterPart.CFrame = CFrame.new(pos + Vector3.new(0, 35, 0))
			local intensity = Lighting:GetAttribute("SnowIntensity")
			local k = if typeof(intensity) == "number" then intensity else 1
			-- gentle gusts
			local gust = 0.75 + 0.25 * math.noise(t * 0.15, 3.3)
			flakes.Rate = Config.Ambience.SnowRate * k * gust
			flakes.Acceleration = Vector3.new(2.5 + 4 * k * gust, -0.5, 1 + 2 * math.noise(t * 0.1, 7))
		end)
	end

	local wind = Effects.sound(SoundService, "AmbientWind", Config.Sounds.Wind, true, Config.Ambience.WindVolume * 0.6)
	if wind then
		wind:Play()
	end
end

return Ambience
