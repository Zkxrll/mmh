--!strict
--[[
	EnvironmentFX - brings the map props to life (client side).
	Works on instances tagged by the Studio setup script:
	  Campfire    fire + smoke + embers particles, flickering light, crackle loop
	  Lamp        warm flickering PointLight on the lantern glass
	  Building    warm lights on the building's lanterns / windows
	  IceCrystal  cyan glow light + drifting sparkles
	  FinishGate  confetti burst + "FINISH!" when the local player rides through
]]

local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Config = require(script.Parent.Config)
local Effects = require(script.Parent.Effects)

local EnvironmentFX = {}

local finishEvent = Instance.new("BindableEvent")
EnvironmentFX.FinishCrossed = finishEvent.Event -- fires on the local client when the local player crosses a FinishGate

type Flicker = { light: PointLight, base: number, seed: number }
local flickers: { Flicker } = {}

local function neonParts(model: Instance): { BasePart }
	local out = {}
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and d.Material == Enum.Material.Neon then
			table.insert(out, d)
		end
	end
	if model:IsA("BasePart") and model.Material == Enum.Material.Neon then
		table.insert(out, model)
	end
	return out
end

local function addLight(part: BasePart, color: Color3, brightness: number, range: number, flicker: boolean)
	if part:FindFirstChild("EnvLight") then
		return
	end
	local l = Instance.new("PointLight")
	l.Name = "EnvLight"
	l.Color = color
	l.Brightness = brightness
	l.Range = range
	l.Shadows = true
	l.Parent = part
	if flicker then
		table.insert(flickers, { light = l, base = brightness, seed = math.random() * 100 })
	end
end

local function campfire(model: Instance)
	local parts = neonParts(model)
	if #parts == 0 then
		return
	end
	-- the tallest neon part is the flame
	table.sort(parts, function(a, b)
		return a.Size.Y > b.Size.Y
	end)
	local flame = parts[1]
	if flame:FindFirstChild("Fire") then
		return
	end
	local a = Effects.attachment(flame, "FireFX", Vector3.new(0, -flame.Size.Y * 0.3, 0))
	local fire = Effects.emitter(a, "Fire", {
		texture = Config.Textures.Flame,
		rate = 45,
		lifetime = NumberRange.new(0.5, 0.9),
		speed = NumberRange.new(2, 4),
		spread = Vector2.new(12, 12),
		size = Effects.seq({ { 0, 1.4 }, { 0.5, 1.1 }, { 1, 0.1 } }),
		transparency = Effects.seq({ { 0, 0.4 }, { 0.3, 0.1 }, { 1, 1 } }),
		color = ColorSequence.new({
			ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 220, 110)),
			ColorSequenceKeypoint.new(0.5, Color3.fromRGB(255, 120, 30)),
			ColorSequenceKeypoint.new(1, Color3.fromRGB(180, 40, 10)),
		}),
		lightEmission = 1,
		lightInfluence = 0,
		acceleration = Vector3.new(0, 4, 0),
		rotSpeed = NumberRange.new(-60, 60),
	})
	fire.Name = "Fire"
	Effects.emitter(a, "Smoke", {
		texture = Config.Textures.Smoke,
		rate = 8,
		lifetime = NumberRange.new(3, 5),
		speed = NumberRange.new(2, 3),
		spread = Vector2.new(10, 10),
		size = Effects.seq({ { 0, 1.5 }, { 1, 5 } }),
		transparency = Effects.seq({ { 0, 1 }, { 0.15, 0.75 }, { 1, 1 } }),
		color = Effects.colors(Color3.fromRGB(90, 90, 95), Color3.fromRGB(160, 160, 170)),
		acceleration = Vector3.new(0.6, 1.5, 0.2),
		zOffset = -1,
	})
	Effects.emitter(a, "Embers", {
		texture = Config.Textures.Spark,
		rate = 10,
		lifetime = NumberRange.new(1, 2),
		speed = NumberRange.new(3, 7),
		spread = Vector2.new(25, 25),
		size = Effects.seq({ { 0, 0.12 }, { 1, 0 } }),
		color = Effects.colors(Color3.fromRGB(255, 170, 60), Color3.fromRGB(255, 80, 20)),
		lightEmission = 1,
		lightInfluence = 0,
		acceleration = Vector3.new(0, 2, 0),
	})
	addLight(flame, Color3.fromRGB(255, 150, 70), 3, 22, true)
	local crackle = Effects.sound(flame, "Crackle", Config.Sounds.Campfire, true, 0.6)
	if crackle then
		crackle.RollOffMaxDistance = 60
		crackle:Play()
	end
end

local function lamp(model: Instance)
	for _, p in neonParts(model) do
		addLight(p, Color3.fromRGB(255, 190, 120), 1.6, 20, true)
	end
end

local function building(model: Instance)
	-- one soft light per glowing part keeps it cheap (a house's windows are one part)
	for _, p in neonParts(model) do
		addLight(p, Color3.fromRGB(255, 185, 110), 1.2, 26, false)
	end
end

local function iceCrystal(model: Instance)
	for _, p in neonParts(model) do
		addLight(p, Color3.fromRGB(110, 230, 255), 1.4, 16, false)
		if not p:FindFirstChild("Sparkles") then
			local e = Effects.emitter(p, "Sparkles", {
				texture = Config.Textures.Sparkle,
				rate = 4,
				lifetime = NumberRange.new(1.5, 3),
				speed = NumberRange.new(0.5, 1.5),
				spread = Vector2.new(180, 180),
				size = Effects.seq({ { 0, 0 }, { 0.5, 0.35 }, { 1, 0 } }),
				color = Effects.colors(Color3.fromRGB(180, 245, 255)),
				lightEmission = 1,
				lightInfluence = 0,
			})
			e.Name = "Sparkles"
		end
	end
end

local lastFinish = 0
local function finishGate(model: Instance)
	if not model:IsA("Model") or model:FindFirstChild("FinishTrigger") then
		return
	end
	local cf, size = model:GetBoundingBox()
	local trigger = Instance.new("Part")
	trigger.Name = "FinishTrigger"
	trigger.Anchored = true
	trigger.CanCollide = false
	trigger.CanQuery = false
	trigger.Transparency = 1
	-- a thin wall between the pillars (thin along the gate's shortest horizontal axis)
	local thinIsX = size.X < size.Z
	trigger.Size = if thinIsX then Vector3.new(2, size.Y, size.Z) else Vector3.new(size.X, size.Y, 2)
	trigger.CFrame = cf
	trigger.Parent = model
	local att = Effects.attachment(trigger, "Confetti", Vector3.new(0, size.Y * 0.35, 0))
	local confetti = Effects.emitter(att, "Confetti", {
		texture = Config.Textures.Confetti,
		lifetime = NumberRange.new(2, 3.5),
		speed = NumberRange.new(18, 30),
		spread = Vector2.new(60, 60),
		size = Effects.seq({ { 0, 0.5 }, { 1, 0.4 } }),
		color = ColorSequence.new({
			ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 70, 90)),
			ColorSequenceKeypoint.new(0.33, Color3.fromRGB(255, 210, 60)),
			ColorSequenceKeypoint.new(0.66, Color3.fromRGB(70, 200, 255)),
			ColorSequenceKeypoint.new(1, Color3.fromRGB(130, 255, 120)),
		}),
		acceleration = Vector3.new(0, -18, 0),
		drag = 1.5,
		rotSpeed = NumberRange.new(-300, 300),
		lightInfluence = 0.5,
		enabled = false,
	})
	local chime = Effects.sound(trigger, "Chime", Config.Sounds.TrickSuccess, false, 0.8)
	trigger.Touched:Connect(function(hit)
		local player = Players.LocalPlayer
		local character = player.Character
		if not character or not hit:IsDescendantOf(character) then
			return
		end
		if os.clock() - lastFinish < 4 then
			return
		end
		lastFinish = os.clock()
		confetti:Emit(160)
		Effects.play(chime)
		finishEvent:Fire(model)
	end)
end

local handlers: { [string]: (Instance) -> () } = {
	Campfire = campfire,
	Lamp = lamp,
	Building = building,
	IceCrystal = iceCrystal,
	FinishGate = finishGate,
}

local started = false
function EnvironmentFX.start()
	if started then
		return
	end
	started = true
	for tag, fn in handlers do
		for _, inst in CollectionService:GetTagged(tag) do
			task.spawn(fn, inst)
		end
		CollectionService:GetInstanceAddedSignal(tag):Connect(function(inst)
			task.spawn(fn, inst)
		end)
	end
	RunService.Heartbeat:Connect(function()
		local t = os.clock()
		for i = #flickers, 1, -1 do
			local f = flickers[i]
			if not f.light.Parent then
				table.remove(flickers, i)
			else
				f.light.Brightness = f.base * Effects.flicker(t, f.seed)
			end
		end
	end)
end

return EnvironmentFX
