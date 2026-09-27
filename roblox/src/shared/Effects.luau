--!strict
-- Small factories for particles, trails and sounds so every effect shares one look.

local Config = require(script.Parent.Config)

local Effects = {}

local function seq(values: { { number } }): NumberSequence
	local keys = {}
	for _, kv in values do
		table.insert(keys, NumberSequenceKeypoint.new(kv[1], kv[2]))
	end
	return NumberSequence.new(keys)
end
Effects.seq = seq

function Effects.colors(c0: Color3, c1: Color3?): ColorSequence
	return ColorSequence.new(c0, c1 or c0)
end

export type EmitterProps = {
	texture: string?,
	rate: number?,
	lifetime: NumberRange?,
	speed: NumberRange?,
	spread: Vector2?,
	size: NumberSequence?,
	transparency: NumberSequence?,
	color: ColorSequence?,
	lightEmission: number?,
	lightInfluence: number?,
	acceleration: Vector3?,
	drag: number?,
	rotSpeed: NumberRange?,
	rotation: NumberRange?,
	direction: Enum.NormalId?,
	locked: boolean?,
	zOffset: number?,
	squash: NumberSequence?,
	orientation: Enum.ParticleOrientation?,
	brightness: number?,
	enabled: boolean?,
}

function Effects.emitter(parent: Instance, name: string, p: EmitterProps): ParticleEmitter
	local e = Instance.new("ParticleEmitter")
	e.Name = name
	e.Texture = p.texture or Config.Textures.SnowPuff
	e.Rate = p.rate or 0
	e.Lifetime = p.lifetime or NumberRange.new(0.5, 1)
	e.Speed = p.speed or NumberRange.new(5, 10)
	e.SpreadAngle = p.spread or Vector2.new(30, 30)
	e.Size = p.size or seq({ { 0, 0.5 }, { 1, 1.5 } })
	e.Transparency = p.transparency or seq({ { 0, 0.2 }, { 1, 1 } })
	e.Color = p.color or Effects.colors(Color3.new(1, 1, 1))
	e.LightEmission = p.lightEmission or 0
	e.LightInfluence = p.lightInfluence or 1
	e.Acceleration = p.acceleration or Vector3.zero
	e.Drag = p.drag or 0
	e.RotSpeed = p.rotSpeed or NumberRange.new(-90, 90)
	e.Rotation = p.rotation or NumberRange.new(0, 360)
	e.EmissionDirection = p.direction or Enum.NormalId.Top
	e.LockedToPart = p.locked or false
	e.ZOffset = p.zOffset or 0
	if p.squash then
		e.Squash = p.squash
	end
	e.Orientation = p.orientation or Enum.ParticleOrientation.FacingCamera
	e.Brightness = p.brightness or 1
	e.Enabled = if p.enabled == nil then true else p.enabled
	e.Parent = parent
	return e
end

function Effects.attachment(parent: BasePart, name: string, position: Vector3): Attachment
	local a = Instance.new("Attachment")
	a.Name = name
	a.Position = position
	a.Parent = parent
	return a
end

function Effects.trail(
	parent: Instance,
	name: string,
	a0: Attachment,
	a1: Attachment,
	color: ColorSequence,
	transparency: NumberSequence,
	lifetime: number,
	lightEmission: number?
): Trail
	local t = Instance.new("Trail")
	t.Name = name
	t.Attachment0 = a0
	t.Attachment1 = a1
	t.Color = color
	t.Transparency = transparency
	t.Lifetime = lifetime
	t.LightEmission = lightEmission or 0
	t.LightInfluence = if (lightEmission or 0) > 0.5 then 0 else 1
	t.MinLength = 0.05
	t.FaceCamera = false
	t.Enabled = false
	t.Parent = parent
	return t
end

-- Returns nil when no sound id is configured, so callers can just skip it.
function Effects.sound(parent: Instance, name: string, id: string, looped: boolean, volume: number): Sound?
	if id == "" then
		return nil
	end
	local s = Instance.new("Sound")
	s.Name = name
	s.SoundId = id
	s.Looped = looped
	s.Volume = volume
	s.RollOffMode = Enum.RollOffMode.InverseTapered
	s.RollOffMinDistance = 8
	s.RollOffMaxDistance = Config.Board.SoundMaxDistance
	s.Parent = parent
	return s
end

function Effects.play(s: Sound?, volume: number?, pitch: number?)
	if not s then
		return
	end
	if volume then
		s.Volume = volume
	end
	s.PlaybackSpeed = pitch or 1
	s.TimePosition = 0
	s:Play()
end

-- Warm light flicker helper for fires and lanterns.
function Effects.flicker(t: number, seed: number): number
	return 0.85 + 0.1 * math.noise(t * 3.1, seed) + 0.05 * math.noise(t * 9.7, seed + 10)
end

return Effects
