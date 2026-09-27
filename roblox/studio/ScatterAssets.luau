--!strict
--[[
	ScatterAssets  (paste into the Studio Command Bar and press Enter)

	Scatters trees / rocks from ServerStorage.MapAssets over the terrain inside a region.
	1. Insert a Part, size it to cover the area (height doesn't matter), name it "ScatterRegion".
	2. Adjust ITEMS / COUNT below and run. Run again to re-roll (old scatter is replaced).
	Undo with Ctrl+Z. Results go to Workspace.Map.Scatter.
]]

local COUNT = 150 -- how many objects to try to place
local MIN_SPACING = 9 -- studs between objects
local MAX_SLOPE = 38 -- degrees; steeper ground is skipped
local TERRAIN_ONLY = true -- only place on Terrain (not on parts / buildings)
local SEED = 1 -- change for a different layout
local ITEMS = {
	-- name in ServerStorage.MapAssets, weight, min scale, max scale, tilt to the slope?
	{ name = "pine_tall", weight = 4, min = 0.8, max = 1.35, align = false },
	{ name = "pine_medium", weight = 5, min = 0.8, max = 1.3, align = false },
	{ name = "pine_small", weight = 3, min = 0.7, max = 1.2, align = false },
	{ name = "pine_leaning", weight = 1, min = 0.8, max = 1.2, align = false },
	{ name = "rock_boulder", weight = 2, min = 0.6, max = 1.6, align = true },
	{ name = "rock_flat", weight = 1, min = 0.7, max = 1.4, align = true },
	{ name = "rock_cluster", weight = 1, min = 0.7, max = 1.3, align = true },
}

local ChangeHistoryService = game:GetService("ChangeHistoryService")
local ServerStorage = game:GetService("ServerStorage")

local region = workspace:FindFirstChild("ScatterRegion", true)
local library = ServerStorage:FindFirstChild("MapAssets")
if not region or not region:IsA("BasePart") then
	error("Make a Part named 'ScatterRegion' covering the area first")
end
if not library then
	error("Run SetupImportedAssets first (it fills ServerStorage.MapAssets)")
end

local recording = ChangeHistoryService:TryBeginRecording("ScatterAssets")
local map: Instance
local existing = workspace:FindFirstChild("Map")
if existing then
	map = existing
else
	local f = Instance.new("Folder")
	f.Name = "Map"
	f.Parent = workspace
	map = f
end
local old = map:FindFirstChild("Scatter")
if old then
	old:Destroy()
end
local out = Instance.new("Folder")
out.Name = "Scatter"
out.Parent = map

local rng = Random.new(SEED)
local total = 0
for _, it in ITEMS do
	total += it.weight
end
local function pick()
	local r = rng:NextNumber() * total
	for _, it in ITEMS do
		r -= it.weight
		if r <= 0 then
			return it
		end
	end
	return ITEMS[1]
end

local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
params.FilterDescendantsInstances = { region, out }

local placed: { Vector3 } = {}
local minDot = math.cos(math.rad(MAX_SLOPE))
local cf, size = region.CFrame, region.Size
local made = 0
for _ = 1, COUNT * 4 do
	if made >= COUNT then
		break
	end
	local lx = (rng:NextNumber() - 0.5) * size.X
	local lz = (rng:NextNumber() - 0.5) * size.Z
	local top = cf:PointToWorldSpace(Vector3.new(lx, 0, lz)) + Vector3.new(0, 2000, 0)
	local hit = workspace:Raycast(top, Vector3.new(0, -4000, 0), params)
	if not hit or hit.Normal.Y < minDot then
		continue
	end
	if TERRAIN_ONLY and hit.Instance ~= workspace.Terrain then
		continue
	end
	if hit.Material == Enum.Material.Water then
		continue
	end
	local ok = true
	for _, p in placed do
		if (p - hit.Position).Magnitude < MIN_SPACING then
			ok = false
			break
		end
	end
	if not ok then
		continue
	end
	local it = pick()
	local template = library:FindFirstChild(it.name)
	if not template or not template:IsA("Model") then
		continue
	end
	local m = template:Clone()
	m:ScaleTo(rng:NextNumber(it.min, it.max))
	local yaw = CFrame.Angles(0, rng:NextNumber(0, math.pi * 2), 0)
	local base: CFrame
	if it.align then
		local up = hit.Normal
		local right = up:Cross(Vector3.zAxis)
		if right.Magnitude < 0.01 then
			right = Vector3.xAxis
		end
		base = CFrame.fromMatrix(hit.Position, right.Unit, up) * yaw
	else
		base = CFrame.new(hit.Position) * yaw
	end
	-- sink slightly so nothing floats on slopes
	m:PivotTo(base * CFrame.new(0, -0.4, 0))
	m:SetAttribute("Scattered", true)
	m.Parent = out
	table.insert(placed, hit.Position)
	made += 1
end

if recording then
	ChangeHistoryService:FinishRecording(recording, Enum.FinishRecordingOperation.Commit)
end
print(string.format("[ScatterAssets] placed %d objects in Workspace.Map.Scatter", made))
