--!strict
--[[
	SnowboardFX - visual + sound effects for every board model tagged "Snowboard".
	Runs on each client, so everyone sees everyone's spray, trails and sparks.

	Per board:
	  * snow spray from the trailing end (more when carving hard)
	  * carve spray thrown off the edge in turns
	  * track ribbon on the snow + neon glow trail at speed (board's glow color)
	  * jump pop, landing burst (bigger after longer air), powder puff
	  * grind sparks + grind sound on parts tagged "Grindable"
	  * carve / wind / grind sound loops driven by speed
	  * spin detection in the air -> 180 / 360 / 540 ... + Big Air, Rail Grind

	Integrate with your own game:
	  SnowboardFX.TrickLanded:Connect(function(board: Model, trick: string, info) ... end)
	  SnowboardFX.trick(board, "Backflip")   -- trigger the trick burst + sound yourself
]]

local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Config = require(script.Parent.Config)
local Effects = require(script.Parent.Effects)

local TAG = "Snowboard"
local GRIND_TAG = "Grindable"
local cfg = Config.Board

type Board = {
	model: Model,
	deck: BasePart,
	owner: Player?,
	isLocal: boolean,
	longIsX: boolean,
	halfLen: number,
	halfWidth: number,
	glowColor: Color3,
	rayParams: RaycastParams,
	-- effects
	sprayAtt: Attachment,
	spray: ParticleEmitter,
	carveAtt: Attachment,
	carveSpray: ParticleEmitter,
	burst: ParticleEmitter,
	sparkle: ParticleEmitter,
	sparks: ParticleEmitter,
	track: Trail,
	glowTrail: Trail,
	carve: Sound?,
	wind: Sound?,
	grind: Sound?,
	sLand: Sound?,
	sJump: Sound?,
	sWhoosh: Sound?,
	sSuccess: Sound?,
	sPowder: Sound?,
	-- state
	grounded: boolean,
	airTime: number,
	spin: number,
	lastHeading: number,
	grinding: boolean,
	grindTime: number,
	whooshed: boolean,
	folder: Folder,
}

local SnowboardFX = {}

local trickEvent = Instance.new("BindableEvent")
SnowboardFX.TrickLanded = trickEvent.Event -- (board: Model, trick: string, info: {airTime: number, spin: number, isLocal: boolean})

local localHooks: { (board: Model, kind: string, value: number) -> () } = {}
-- Local-player hooks (camera shake, speed FOV, popups):
-- kind = "land" (value = power 0..1) | "speed" (studs/s) | "air" (seconds) | "trick:<name>" (air time)
function SnowboardFX.onLocal(fn: (board: Model, kind: string, value: number) -> ())
	table.insert(localHooks, fn)
end

local function fireLocal(b: Board, kind: string, value: number)
	if not b.isLocal then
		return
	end
	for _, fn in localHooks do
		task.spawn(fn, b.model, kind, value)
	end
end

local boards: { [Model]: Board } = {}

local SNOW = Color3.fromRGB(240, 246, 255)
local SNOW_SHADE = Color3.fromRGB(200, 218, 240)

local function findDeck(model: Model): BasePart?
	if model.PrimaryPart then
		return model.PrimaryPart
	end
	local best: BasePart? = nil
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			if d.Name:match("Deck$") then
				return d
			end
			if not best or d.Size.Magnitude > best.Size.Magnitude then
				best = d
			end
		end
	end
	return best
end

local function findGlowColor(model: Model): Color3
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and d.Material == Enum.Material.Neon then
			return d.Color
		end
	end
	return Color3.fromRGB(150, 220, 255)
end

local function longAxis(b: Board): Vector3
	local cf = b.deck.CFrame
	return if b.longIsX then cf.RightVector else cf.LookVector
end

local function heading(v: Vector3): number
	return math.atan2(v.X, v.Z)
end

local function wrapAngle(a: number): number
	return (a + math.pi) % (2 * math.pi) - math.pi
end

local function isGrindable(inst: Instance): boolean
	local cur: Instance? = inst
	for _ = 1, 4 do
		if not cur then
			break
		end
		if CollectionService:HasTag(cur, GRIND_TAG) then
			return true
		end
		cur = cur.Parent
	end
	return false
end

local function trickName(spinDeg: number): string?
	local n = math.floor((spinDeg + cfg.SpinTolerance) / 180)
	if n >= 1 then
		return tostring(n * 180)
	end
	return nil
end

local function emitTrick(b: Board, name: string, airTime: number, spinDeg: number)
	b.sparkle:Emit(40)
	b.burst:Emit(25)
	Effects.play(b.sSuccess, 0.6)
	trickEvent:Fire(b.model, name, { airTime = airTime, spin = spinDeg, isLocal = b.isLocal })
	fireLocal(b, "trick:" .. name, airTime)
end

local function setup(model: Model)
	if boards[model] then
		return
	end
	local deck = findDeck(model)
	local t0 = os.clock()
	while not deck and os.clock() - t0 < 5 do
		task.wait(0.1)
		deck = findDeck(model)
	end
	if not deck or not model.Parent then
		return
	end

	local ownerId = model:GetAttribute("OwnerUserId")
	local owner = if typeof(ownerId) == "number" then Players:GetPlayerByUserId(ownerId) else nil
	local longIsX = deck.Size.X > deck.Size.Z
	local halfLen = (if longIsX then deck.Size.X else deck.Size.Z) / 2
	local halfWidth = (if longIsX then deck.Size.Z else deck.Size.X) / 2
	local bottom = -deck.Size.Y / 2
	local glowColor = findGlowColor(model)

	local folder = Instance.new("Folder")
	folder.Name = "SnowboardFX"
	folder.Parent = deck

	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	-- ignore the rider (the board is parented to the character) and the board itself
	local rider = model.Parent
	params.FilterDescendantsInstances = if rider and rider:FindFirstChildOfClass("Humanoid")
		then { rider }
		else { model }

	local centre = Effects.attachment(deck, "FX_Centre", Vector3.new(0, bottom, 0))
	local sprayAtt = Effects.attachment(deck, "FX_Spray", Vector3.new(0, bottom, 0))
	local carveAtt = Effects.attachment(deck, "FX_Carve", Vector3.new(0, bottom, 0))
	local side = if longIsX then Vector3.new(0, 0, halfWidth) else Vector3.new(halfWidth, 0, 0)
	local trackL = Effects.attachment(deck, "FX_TrackL", Vector3.new(0, bottom + 0.02, 0) + side * 0.9)
	local trackR = Effects.attachment(deck, "FX_TrackR", Vector3.new(0, bottom + 0.02, 0) - side * 0.9)
	local glowL = Effects.attachment(deck, "FX_GlowL", Vector3.new(0, bottom + 0.06, 0) + side)
	local glowR = Effects.attachment(deck, "FX_GlowR", Vector3.new(0, bottom + 0.06, 0) - side)

	local spray = Effects.emitter(sprayAtt, "Spray", {
		texture = Config.Textures.SnowPuff,
		lifetime = NumberRange.new(0.35, 0.8),
		speed = NumberRange.new(4, 10),
		spread = Vector2.new(35, 55),
		size = Effects.seq({ { 0, 0.5 }, { 0.4, 1.4 }, { 1, 2.2 } }),
		transparency = Effects.seq({ { 0, 0.25 }, { 0.6, 0.55 }, { 1, 1 } }),
		color = Effects.colors(SNOW, SNOW_SHADE),
		acceleration = Vector3.new(0, -26, 0),
		drag = 2.5,
	})
	local carveSpray = Effects.emitter(carveAtt, "CarveSpray", {
		texture = Config.Textures.SnowPuff,
		lifetime = NumberRange.new(0.4, 0.9),
		speed = NumberRange.new(10, 22),
		spread = Vector2.new(18, 35),
		size = Effects.seq({ { 0, 0.4 }, { 0.5, 1.2 }, { 1, 1.8 } }),
		transparency = Effects.seq({ { 0, 0.15 }, { 0.7, 0.6 }, { 1, 1 } }),
		color = Effects.colors(SNOW, SNOW_SHADE),
		acceleration = Vector3.new(0, -34, 0),
		drag = 2,
	})
	local burst = Effects.emitter(centre, "LandBurst", {
		texture = Config.Textures.SnowPuff,
		lifetime = NumberRange.new(0.5, 1.1),
		speed = NumberRange.new(8, 18),
		spread = Vector2.new(85, 85),
		size = Effects.seq({ { 0, 0.8 }, { 0.5, 2.2 }, { 1, 3.2 } }),
		transparency = Effects.seq({ { 0, 0.2 }, { 0.6, 0.6 }, { 1, 1 } }),
		color = Effects.colors(SNOW, SNOW_SHADE),
		acceleration = Vector3.new(0, -20, 0),
		drag = 3,
		enabled = false,
	})
	local sparkle = Effects.emitter(centre, "TrickSparkle", {
		texture = Config.Textures.Sparkle,
		lifetime = NumberRange.new(0.5, 1.2),
		speed = NumberRange.new(6, 16),
		spread = Vector2.new(180, 180),
		size = Effects.seq({ { 0, 0.6 }, { 0.3, 0.9 }, { 1, 0 } }),
		transparency = Effects.seq({ { 0, 0 }, { 0.8, 0.3 }, { 1, 1 } }),
		color = Effects.colors(glowColor, Color3.new(1, 1, 1)),
		lightEmission = 1,
		lightInfluence = 0,
		drag = 4,
		enabled = false,
	})
	local sparks = Effects.emitter(centre, "GrindSparks", {
		texture = Config.Textures.Spark,
		lifetime = NumberRange.new(0.15, 0.45),
		speed = NumberRange.new(10, 20),
		spread = Vector2.new(60, 25),
		size = Effects.seq({ { 0, 0.25 }, { 1, 0 } }),
		transparency = Effects.seq({ { 0, 0 }, { 1, 0.6 } }),
		color = Effects.colors(Color3.fromRGB(255, 230, 120), Color3.fromRGB(255, 110, 30)),
		lightEmission = 1,
		lightInfluence = 0,
		acceleration = Vector3.new(0, -50, 0),
		squash = Effects.seq({ { 0, 2 }, { 1, 2 } }),
		enabled = false,
	})
	local track = Effects.trail(
		folder,
		"Track",
		trackL,
		trackR,
		Effects.colors(Color3.fromRGB(215, 230, 250)),
		Effects.seq({ { 0, 0.55 }, { 1, 1 } }),
		1.6
	)
	local glowTrail = Effects.trail(
		folder,
		"GlowTrail",
		glowL,
		glowR,
		Effects.colors(glowColor, Color3.new(1, 1, 1)),
		Effects.seq({ { 0, 0.35 }, { 1, 1 } }),
		0.35,
		1
	)

	local s = Config.Sounds
	local b: Board = {
		model = model,
		deck = deck,
		owner = owner,
		isLocal = owner == Players.LocalPlayer,
		longIsX = longIsX,
		halfLen = halfLen,
		halfWidth = halfWidth,
		glowColor = glowColor,
		rayParams = params,
		sprayAtt = sprayAtt,
		spray = spray,
		carveAtt = carveAtt,
		carveSpray = carveSpray,
		burst = burst,
		sparkle = sparkle,
		sparks = sparks,
		track = track,
		glowTrail = glowTrail,
		carve = Effects.sound(folder, "Carve", s.Carve, true, 0),
		wind = nil,
		grind = Effects.sound(folder, "Grind", s.Grind, true, 0),
		sLand = Effects.sound(folder, "Land", s.Land, false, 0.8),
		sJump = Effects.sound(folder, "Jump", s.Jump, false, 0.6),
		sWhoosh = Effects.sound(folder, "Whoosh", s.Whoosh, false, 0.5),
		sSuccess = Effects.sound(folder, "Success", s.TrickSuccess, false, 0.6),
		sPowder = Effects.sound(folder, "Powder", s.Powder, false, 0.6),
		grounded = true,
		airTime = 0,
		spin = 0,
		lastHeading = 0,
		grinding = false,
		grindTime = 0,
		whooshed = false,
		folder = folder,
	}
	b.lastHeading = heading(longAxis(b))
	if b.isLocal then
		b.wind = Effects.sound(folder, "Wind", s.Wind, true, 0)
	end
	for _, snd in { b.carve, b.wind, b.grind } do
		if snd then
			snd:Play()
		end
	end
	boards[model] = b
end

local function teardown(model: Model)
	local b = boards[model]
	if not b then
		return
	end
	boards[model] = nil
	if b.folder.Parent then
		b.folder:Destroy()
	end
	for _, name in { "FX_Centre", "FX_Spray", "FX_Carve", "FX_TrackL", "FX_TrackR", "FX_GlowL", "FX_GlowR" } do
		local a = b.deck:FindFirstChild(name)
		if a then
			a:Destroy()
		end
	end
end

local function step(b: Board, dt: number)
	local deck = b.deck
	if not deck.Parent then
		teardown(b.model)
		return
	end
	local vel = deck.AssemblyLinearVelocity
	local flat = Vector3.new(vel.X, 0, vel.Z)
	local speed = flat.Magnitude
	local up = deck.CFrame.UpVector
	local long = longAxis(b)

	local hit = workspace:Raycast(deck.Position + up * 0.5, -up * (cfg.GroundRay + 0.5), b.rayParams)
	local grounded = hit ~= nil
	local onRail = hit ~= nil and isGrindable(hit.Instance)

	-- trailing end follows the direction of travel
	local sign = if flat:Dot(long) >= 0 then -1 else 1
	local localLong = if b.longIsX then Vector3.xAxis else Vector3.zAxis
	b.sprayAtt.Position = Vector3.new(0, -deck.Size.Y / 2, 0) + localLong * (b.halfLen * 0.85 * sign)

	-- carving = sideways slide relative to the board
	local sideDir = up:Cross(long)
	local lateral = if speed > 0.1 then flat:Dot(sideDir) else 0
	local carveAmt = math.clamp(math.abs(lateral) / 18, 0, 1)
	local speedAmt = math.clamp((speed - cfg.SprayMinSpeed) / 60, 0, 1)

	if grounded and not onRail then
		b.spray.Rate = cfg.SprayMaxRate * speedAmt * (0.35 + 0.65 * carveAmt)
		b.spray.Speed = NumberRange.new(3 + 6 * speedAmt, 8 + 14 * speedAmt)
		if carveAmt > 0.15 and speed > 10 then
			local outDir = (sideDir * math.sign(lateral) * 0.8 + up * 0.75 - flat.Unit * 0.25).Unit
			local pos = deck.Position - up * (deck.Size.Y / 2) + sideDir * math.sign(lateral) * b.halfWidth
			local right = outDir:Cross(Vector3.yAxis)
			if right.Magnitude < 0.01 then
				right = Vector3.xAxis
			end
			b.carveAtt.WorldCFrame = CFrame.fromMatrix(pos, right.Unit, outDir)
			b.carveSpray.Rate = 140 * carveAmt * speedAmt
		else
			b.carveSpray.Rate = 0
		end
		b.track.Enabled = speed > 2
	else
		b.spray.Rate = 0
		b.carveSpray.Rate = 0
		b.track.Enabled = false
	end
	b.glowTrail.Enabled = speed > cfg.GlowTrailSpeed or (not grounded and b.airTime > 0.2)

	-- grinding
	if onRail and speed > 3 then
		if not b.grinding then
			b.grinding = true
			b.grindTime = 0
		end
		b.grindTime += dt
		b.sparks.Enabled = true
		b.sparks.Rate = 60 + speed * 2
	elseif b.grinding then
		b.grinding = false
		b.sparks.Enabled = false
		if b.grindTime >= cfg.GrindMinTime then
			emitTrick(b, "Rail Grind", b.airTime, 0)
		end
	end

	-- air time, spins, jumps and landings
	local h = heading(long)
	if not grounded then
		if b.grounded then
			-- just left the ground
			b.airTime = 0
			b.spin = 0
			b.whooshed = false
			if vel.Y > 4 then
				Effects.play(b.sJump, 0.6, 0.95 + math.random() * 0.1)
				b.burst:Emit(8)
			end
		end
		b.airTime += dt
		b.spin += wrapAngle(h - b.lastHeading)
		if not b.whooshed and math.abs(b.spin) > math.rad(120) then
			b.whooshed = true
			Effects.play(b.sWhoosh, 0.5, 0.9 + math.random() * 0.2)
		end
		if b.airTime > 0.3 then
			fireLocal(b, "air", b.airTime)
		end
	elseif not b.grounded then
		-- just landed
		local air = b.airTime
		if air >= cfg.LandMinAirTime then
			local power = math.clamp(air / 1.5, 0.3, 1)
			b.burst:Emit(math.floor(20 + 50 * power))
			Effects.play(b.sLand, 0.5 + 0.5 * power, 1.05 - 0.15 * power)
			if air > 0.8 then
				Effects.play(b.sPowder, 0.6)
			end
			fireLocal(b, "land", power)
			local spinDeg = math.abs(math.deg(b.spin))
			local name = trickName(spinDeg)
			if name then
				emitTrick(b, name, air, spinDeg)
			elseif air >= cfg.HugeAirTime then
				emitTrick(b, "Huge Air", air, spinDeg)
			elseif air >= cfg.BigAirTime then
				emitTrick(b, "Big Air", air, spinDeg)
			end
		end
		b.airTime = 0
		b.spin = 0
	end
	b.lastHeading = h
	b.grounded = grounded

	-- sound loops
	if b.carve then
		local target = if grounded and not onRail then 0.15 + 0.85 * speedAmt * (0.5 + 0.5 * carveAmt) else 0
		if speed < 1 then
			target = 0
		end
		b.carve.Volume += (target - b.carve.Volume) * math.min(1, dt * 8)
		b.carve.PlaybackSpeed = 0.8 + 0.5 * speedAmt
	end
	if b.grind then
		local target = if b.grinding then 0.8 else 0
		b.grind.Volume += (target - b.grind.Volume) * math.min(1, dt * 12)
		b.grind.PlaybackSpeed = 0.9 + 0.3 * speedAmt
	end
	if b.wind then
		local target = Config.Ambience.WindVolume + 0.9 * math.clamp((speed - 15) / 70, 0, 1)
		b.wind.Volume += (target - b.wind.Volume) * math.min(1, dt * 3)
		b.wind.PlaybackSpeed = 0.85 + 0.35 * speedAmt
	end

	fireLocal(b, "speed", speed)
end

-- Play the trick burst + chime yourself (e.g. from your own trick system).
function SnowboardFX.trick(model: Model, name: string)
	local b = boards[model]
	if b then
		emitTrick(b, name, b.airTime, 0)
	end
end

local started = false
function SnowboardFX.start()
	if started then
		return
	end
	started = true
	for _, inst in CollectionService:GetTagged(TAG) do
		if inst:IsA("Model") then
			task.spawn(setup, inst)
		end
	end
	CollectionService:GetInstanceAddedSignal(TAG):Connect(function(inst)
		if inst:IsA("Model") then
			task.spawn(setup, inst)
		end
	end)
	CollectionService:GetInstanceRemovedSignal(TAG):Connect(function(inst)
		if inst:IsA("Model") then
			teardown(inst)
		end
	end)
	RunService.Heartbeat:Connect(function(dt)
		for _, b in boards do
			step(b, dt)
		end
	end)
end

return SnowboardFX
