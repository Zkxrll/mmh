--!strict
--[[
	SetupImportedAssets  (paste into the Studio Command Bar and press Enter)

	Run this after importing the .fbx files from blender-models/out/ with the 3D Importer.
	It finds the imported models anywhere in Workspace and:
	  * sets Neon / Glass / SmoothPlastic materials and glow colors (from each model's manifest)
	  * sets CollisionFidelity, anchors map pieces, turns off collision on windows / icicles
	  * tags props so SnowboardKit's effects find them (Campfire, Lamp, Grindable, FinishGate ...)
	  * moves boards to ReplicatedStorage.Snowboards (ready for the board picker)
	  * sorts map pieces into Workspace.Map.<Category> and keeps a copy in ServerStorage.MapAssets
	    (the scatter tool clones from there)
	Safe to run again. Undo with Ctrl+Z.

	If the colors came in grey, upload textures/palette.png and paste its id below.
]]

local PALETTE_TEXTURE = "" -- "rbxassetid://..." of palette.png (only needed if colors import grey)
local EXTRA_TEXTURES: { [string]: string } = {
	-- only needed if a textured part imported blank: ["board_inferno_deck.png"] = "rbxassetid://...",
__TEXTURE_KEYS__
}

local CollectionService = game:GetService("CollectionService")
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

type PartInfo = { material: string?, color: { number }?, texture: string? }
type ModelInfo = { category: string, collision: string, parts: { [string]: PartInfo } }

-- generated from blender-models/out/*/manifest.json
local MANIFEST: { [string]: ModelInfo } = {
__MANIFEST__
}

local TAGS: { [string]: { string } } = {
	campfire = { "Campfire" },
	lamp_post = { "Lamp" },
	lodge = { "Building" },
	cabin = { "Building" },
	board_shop = { "Building" },
	ice_crystals = { "IceCrystal" },
	rail_flat = { "Grindable" },
	rail_kink = { "Grindable" },
	grind_box = { "Grindable" },
	gate_finish = { "FinishGate" },
	gate_start = { "StartGate" },
}

local MATERIALS: { [string]: Enum.Material } = {
	Neon = Enum.Material.Neon,
	Glass = Enum.Material.Glass,
	Ice = Enum.Material.Ice,
	SmoothPlastic = Enum.Material.SmoothPlastic,
}
local FIDELITY: { [string]: Enum.CollisionFidelity } = {
	Default = Enum.CollisionFidelity.Default,
	Box = Enum.CollisionFidelity.Box,
	Hull = Enum.CollisionFidelity.Hull,
	PreciseConvexDecomposition = Enum.CollisionFidelity.PreciseConvexDecomposition,
}

local function folder(parent: Instance, name: string): Instance
	local f = parent:FindFirstChild(name)
	if not f then
		local nf = Instance.new("Folder")
		nf.Name = name
		nf.Parent = parent
		f = nf
	end
	return f :: Instance
end

-- "lodge_Structure (1)" / "lodge_Structure.001" -> "lodge_Structure"
local function clean(name: string): string
	return (name:gsub("%s*%(%d+%)$", ""):gsub("%.%d+$", ""))
end

local function modelFor(partName: string): string?
	local best: string? = nil
	for modelName, info in MANIFEST do
		if info.parts[partName] or partName == modelName then
			if not best or #modelName > #best then
				best = modelName
			end
		end
	end
	return best
end

-- exact part name, else "<model>_<name>", else any part key ending in "_<name>"
local function partInfo(modelName: string, info: ModelInfo, partName: string): PartInfo?
	local direct = info.parts[partName] or info.parts[modelName .. "_" .. partName]
	if direct then
		return direct
	end
	for key, p in info.parts do
		if key:sub(-(#partName + 1)) == "_" .. partName then
			return p
		end
	end
	-- single-part models: the only entry applies
	local only: PartInfo? = nil
	local n = 0
	for _, p in info.parts do
		only = p
		n += 1
	end
	return if n == 1 then only else nil
end

local function setupPart(p: MeshPart, info: PartInfo?, isBoard: boolean, collision: string)
	local nm = clean(p.Name)
	if info and info.material then
		p.Material = MATERIALS[info.material] or Enum.Material.SmoothPlastic
		local c = info.color
		if c then
			p.Color = Color3.fromRGB(c[1], c[2], c[3])
		end
		p.TextureID = ""
		local sa = p:FindFirstChildOfClass("SurfaceAppearance")
		if sa then
			sa:Destroy()
		end
		if info.material == "Neon" then
			p.CastShadow = false
		elseif info.material == "Glass" then
			p.Transparency = 0.25
			p.Reflectance = 0.1
		end
	else
		p.Material = Enum.Material.SmoothPlastic
		local tex = info and info.texture
		if p.TextureID == "" and not p:FindFirstChildOfClass("SurfaceAppearance") then
			if tex == "palette.png" and PALETTE_TEXTURE ~= "" then
				p.TextureID = PALETTE_TEXTURE
			elseif tex and EXTRA_TEXTURES[tex] and EXTRA_TEXTURES[tex] ~= "" then
				p.TextureID = EXTRA_TEXTURES[tex]
			end
		end
	end
	if isBoard then
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Massless = true
	else
		p.Anchored = true
		if nm:match("_Windows$") or nm:match("_Icicles$") or (info and info.material == "Neon") then
			p.CanCollide = false
		end
		pcall(function()
			p.CollisionFidelity = FIDELITY[collision] or Enum.CollisionFidelity.Default
		end)
	end
end

local recording = ChangeHistoryService:TryBeginRecording("SetupImportedAssets")
local done: { [Instance]: boolean } = {}
local counts = { boards = 0, map = 0, parts = 0 }
local boardsFolder = folder(ReplicatedStorage, "Snowboards")
local mapFolder = folder(workspace, "Map")
local library = folder(ServerStorage, "MapAssets")

local candidates: { { container: Instance, modelName: string } } = {}
for _, inst in workspace:GetDescendants() do
	if inst:IsDescendantOf(mapFolder) then
		continue
	end
	if inst:IsA("Model") and MANIFEST[clean(inst.Name)] then
		table.insert(candidates, { container = inst :: Instance, modelName = clean(inst.Name) })
	end
end
for _, inst in workspace:GetDescendants() do
	if not inst:IsA("MeshPart") or inst:IsDescendantOf(mapFolder) then
		continue
	end
	local inside = false
	for _, c in candidates do
		if inst:IsDescendantOf(c.container) then
			inside = true
			break
		end
	end
	local modelName = if inside then nil else modelFor(clean(inst.Name))
	if modelName then
		-- a loose part, or the importer's container Model with a different name
		-- only adopt the parent Model if every mesh in it belongs to this asset
		-- (never rename one of your own models)
		local container: Instance = inst
		local parent = inst.Parent
		if parent and parent:IsA("Model") then
			local allOurs = true
			for _, d in parent:GetDescendants() do
				if d:IsA("BasePart") and modelFor(clean(d.Name)) ~= modelName then
					allOurs = false
					break
				end
			end
			if allOurs then
				container = parent
			end
		end
		table.insert(candidates, { container = container, modelName = modelName })
	end
end

for _, cand in candidates do
	local container, modelName = cand.container, cand.modelName
	if done[container] or not container.Parent then
		continue
	end
	done[container] = true
	local model: Model
	if container:IsA("Model") then
		model = container
	else
		model = Instance.new("Model")
		model.Parent = container.Parent
		container.Parent = model
	end
	model.Name = modelName
	local info = MANIFEST[modelName]
	local isBoard = modelName:match("^board_") ~= nil
	local biggest: BasePart? = nil
	for _, d in model:GetDescendants() do
		if d:IsA("MeshPart") then
			setupPart(d, partInfo(modelName, info, clean(d.Name)), isBoard, info.collision)
			counts.parts += 1
			if (isBoard and clean(d.Name):match("Deck$")) or (not isBoard and (not biggest or d.Size.Magnitude > biggest.Size.Magnitude)) then
				biggest = d
			end
		end
	end
	if biggest then
		model.PrimaryPart = biggest
	end
	-- pivot at the bottom centre so models sit on the ground when placed
	local cf, size = model:GetBoundingBox()
	model.WorldPivot = cf * CFrame.new(0, -size.Y / 2, 0)
	local tags = TAGS[modelName]
	if tags then
		for _, tag in tags do
			CollectionService:AddTag(model, tag)
			if tag == "Grindable" then
				for _, d in model:GetDescendants() do
					if d:IsA("BasePart") then
						CollectionService:AddTag(d, tag)
					end
				end
			end
		end
	end
	model:SetAttribute("AssetName", modelName)
	if isBoard then
		local old = boardsFolder:FindFirstChild(modelName)
		if old then
			old:Destroy()
		end
		model.Parent = boardsFolder
		counts.boards += 1
	else
		model.Parent = folder(mapFolder, info.category)
		local old = library:FindFirstChild(modelName)
		if old then
			old:Destroy()
		end
		model:Clone().Parent = library
		counts.map += 1
	end
end

if recording then
	ChangeHistoryService:FinishRecording(recording, Enum.FinishRecordingOperation.Commit)
end
print(
	string.format(
		"[SetupImportedAssets] %d boards -> ReplicatedStorage.Snowboards, %d map models -> Workspace.Map, %d mesh parts set up",
		counts.boards,
		counts.map,
		counts.parts
	)
)
