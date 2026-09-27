--!strict
-- Local rider feel: FOV opens up with speed, speed lines at high speed, a punchy shake on landing.

local RunService = game:GetService("RunService")

local Kit = game:GetService("ReplicatedStorage"):WaitForChild("SnowboardKit")
local Config = require(Kit:WaitForChild("Config"))
local Effects = require(Kit:WaitForChild("Effects"))
local SnowboardFX = require(Kit:WaitForChild("SnowboardFX"))

local CameraFX = {}

local c = Config.Camera
local speed = 0
local lastSpeedTime = 0
local shake = 0

function CameraFX.start()
	local camera = workspace.CurrentCamera

	local linesPart = Instance.new("Part")
	linesPart.Name = "SpeedLines"
	linesPart.Anchored = true
	linesPart.CanCollide = false
	linesPart.CanQuery = false
	linesPart.CanTouch = false
	linesPart.CastShadow = false
	linesPart.Transparency = 1
	linesPart.Size = Vector3.new(34, 20, 1)
	linesPart.Parent = camera
	local lines = Effects.emitter(linesPart, "Lines", {
		texture = Config.Textures.Streak,
		lifetime = NumberRange.new(0.18, 0.3),
		speed = NumberRange.new(60, 90),
		spread = Vector2.new(0, 0),
		size = Effects.seq({ { 0, 0.08 }, { 1, 0.04 } }),
		transparency = Effects.seq({ { 0, 1 }, { 0.3, 0.55 }, { 1, 1 } }),
		squash = Effects.seq({ { 0, 8 }, { 1, 8 } }),
		orientation = Enum.ParticleOrientation.VelocityParallel,
		lightEmission = 1,
		lightInfluence = 0,
		direction = Enum.NormalId.Back,
		rotSpeed = NumberRange.new(0, 0),
		rotation = NumberRange.new(0, 0),
	})

	SnowboardFX.onLocal(function(_board, kind, value)
		if kind == "speed" then
			speed = value
			lastSpeedTime = os.clock()
		elseif kind == "land" and c.LandShake then
			shake = math.max(shake, 0.35 * value)
		end
	end)

	RunService:BindToRenderStep("SnowboardCameraFX", Enum.RenderPriority.Camera.Value + 1, function(dt: number)
		-- speed is only reported while riding; ease back when off the board
		local s = if os.clock() - lastSpeedTime < 0.3 then speed else 0
		local k = math.clamp((s - c.FovSpeedLow) / (c.FovSpeedHigh - c.FovSpeedLow), 0, 1)
		local fov = c.BaseFov + c.MaxFovBoost * k * k
		camera.FieldOfView += (fov - camera.FieldOfView) * math.min(1, dt * 4)

		if c.SpeedLines then
			linesPart.CFrame = camera.CFrame * CFrame.new(0, 0, -14)
			lines.Rate = if s > c.SpeedLinesFrom then 60 + 4 * (s - c.SpeedLinesFrom) else 0
		end

		if shake > 0.001 then
			local r = shake
			camera.CFrame *= CFrame.new((math.random() - 0.5) * r * 0.6, (math.random() - 0.5) * r * 0.6, 0) * CFrame.Angles(
				(math.random() - 0.5) * r * 0.05,
				0,
				(math.random() - 0.5) * r * 0.05
			)
			shake *= math.exp(-dt * 9)
		end
	end)
end

return CameraFX
