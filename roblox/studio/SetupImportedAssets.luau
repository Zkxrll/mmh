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
	["board_cosmic_deck.png"] = "",
	["board_frostbite_deck.png"] = "",
	["board_inferno_deck.png"] = "",
	["board_rookie_deck.png"] = "",
	["board_shop_sign.png"] = "",
	["board_sunset_deck.png"] = "",
	["board_viper_deck.png"] = "",
	["gate_finish_banner.png"] = "",
	["gate_start_banner.png"] = "",
	["signpost_arrows.png"] = "",
}

local CollectionService = game:GetService("CollectionService")
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

type PartInfo = { material: string?, color: { number }?, texture: string? }
type ModelInfo = { category: string, collision: string, parts: { [string]: PartInfo } }

-- generated from blender-models/out/*/manifest.json
local MANIFEST: { [string]: ModelInfo } = {
	["bench"] = {
		category = "Props",
		collision = "Default",
		parts = {
			["bench"] = { texture = "palette.png" },
		},
	},
	["board_cosmic"] = {
		category = "Boards",
		collision = "Default",
		parts = {
			["board_cosmic_Deck"] = { texture = "board_cosmic_deck.png" },
			["board_cosmic_Bindings"] = { texture = "palette.png" },
			["board_cosmic_Glow"] = { material = "Neon", color = { 190, 40, 220 } },
		},
	},
	["board_frostbite"] = {
		category = "Boards",
		collision = "Default",
		parts = {
			["board_frostbite_Deck"] = { texture = "board_frostbite_deck.png" },
			["board_frostbite_Bindings"] = { texture = "palette.png" },
			["board_frostbite_Glow"] = { material = "Neon", color = { 60, 240, 255 } },
		},
	},
	["board_inferno"] = {
		category = "Boards",
		collision = "Default",
		parts = {
			["board_inferno_Deck"] = { texture = "board_inferno_deck.png" },
			["board_inferno_Bindings"] = { texture = "palette.png" },
			["board_inferno_Glow"] = { material = "Neon", color = { 255, 140, 40 } },
		},
	},
	["board_rookie"] = {
		category = "Boards",
		collision = "Default",
		parts = {
			["board_rookie_Deck"] = { texture = "board_rookie_deck.png" },
			["board_rookie_Bindings"] = { texture = "palette.png" },
		},
	},
	["board_shop"] = {
		category = "Buildings",
		collision = "PreciseConvexDecomposition",
		parts = {
			["board_shop_Structure"] = { texture = "palette.png" },
			["board_shop_Icicles"] = { material = "Glass", color = { 168, 214, 240 } },
			["board_shop_Windows"] = { material = "Neon", color = { 255, 196, 110 } },
			["board_shop_Sign"] = { texture = "board_shop_sign.png" },
		},
	},
	["board_sunset"] = {
		category = "Boards",
		collision = "Default",
		parts = {
			["board_sunset_Deck"] = { texture = "board_sunset_deck.png" },
			["board_sunset_Bindings"] = { texture = "palette.png" },
			["board_sunset_Glow"] = { material = "Neon", color = { 255, 40, 140 } },
		},
	},
	["board_viper"] = {
		category = "Boards",
		collision = "Default",
		parts = {
			["board_viper_Deck"] = { texture = "board_viper_deck.png" },
			["board_viper_Bindings"] = { texture = "palette.png" },
			["board_viper_Glow"] = { material = "Neon", color = { 80, 255, 120 } },
		},
	},
	["cabin"] = {
		category = "Buildings",
		collision = "PreciseConvexDecomposition",
		parts = {
			["cabin_Structure"] = { texture = "palette.png" },
			["cabin_Icicles"] = { material = "Glass", color = { 168, 214, 240 } },
			["cabin_Windows"] = { material = "Neon", color = { 255, 196, 110 } },
		},
	},
	["campfire"] = {
		category = "Props",
		collision = "Default",
		parts = {
			["campfire_Main"] = { texture = "palette.png" },
			["campfire_Neon_fire"] = { material = "Neon", color = { 255, 140, 40 } },
			["campfire_Neon_flame_yellow"] = { material = "Neon", color = { 255, 210, 60 } },
			["campfire_Neon_ember"] = { material = "Neon", color = { 255, 90, 30 } },
		},
	},
	["crate"] = {
		category = "Props",
		collision = "Default",
		parts = {
			["crate"] = { texture = "palette.png" },
		},
	},
	["gate_finish"] = {
		category = "Park",
		collision = "PreciseConvexDecomposition",
		parts = {
			["gate_finish_Main"] = { texture = "palette.png" },
			["gate_finish_Neon_glow_cyan"] = { material = "Neon", color = { 60, 240, 255 } },
			["gate_finish_gate_finish_banner"] = { texture = "gate_finish_banner.png" },
		},
	},
	["gate_start"] = {
		category = "Park",
		collision = "PreciseConvexDecomposition",
		parts = {
			["gate_start_Main"] = { texture = "palette.png" },
			["gate_start_Neon_glow_cyan"] = { material = "Neon", color = { 60, 240, 255 } },
			["gate_start_gate_start_banner"] = { texture = "gate_start_banner.png" },
		},
	},
	["grind_box"] = {
		category = "Park",
		collision = "PreciseConvexDecomposition",
		parts = {
			["grind_box"] = { texture = "palette.png" },
		},
	},
	["ice_crystals"] = {
		category = "Nature",
		collision = "Default",
		parts = {
			["ice_crystals_Glass_ice"] = { material = "Glass", color = { 168, 214, 240 } },
			["ice_crystals_Neon_glow_cyan"] = { material = "Neon", color = { 60, 240, 255 } },
			["ice_crystals_Main"] = { texture = "palette.png" },
		},
	},
	["kicker_big"] = {
		category = "Park",
		collision = "PreciseConvexDecomposition",
		parts = {
			["kicker_big"] = { texture = "palette.png" },
		},
	},
	["kicker_small"] = {
		category = "Park",
		collision = "PreciseConvexDecomposition",
		parts = {
			["kicker_small"] = { texture = "palette.png" },
		},
	},
	["lamp_post"] = {
		category = "Props",
		collision = "Default",
		parts = {
			["lamp_post_Main"] = { texture = "palette.png" },
			["lamp_post_Neon_window_glow"] = { material = "Neon", color = { 255, 196, 110 } },
		},
	},
	["lift_chair"] = {
		category = "Props",
		collision = "Default",
		parts = {
			["lift_chair_Chair"] = { texture = "palette.png" },
			["lift_chair_SafetyBar"] = { texture = "palette.png" },
		},
	},
	["lift_tower"] = {
		category = "Props",
		collision = "Default",
		parts = {
			["lift_tower_Main"] = { texture = "palette.png" },
			["lift_tower_Neon_bright_red"] = { material = "Neon", color = { 255, 60, 50 } },
		},
	},
	["lodge"] = {
		category = "Buildings",
		collision = "PreciseConvexDecomposition",
		parts = {
			["lodge_Structure"] = { texture = "palette.png" },
			["lodge_Icicles"] = { material = "Glass", color = { 168, 214, 240 } },
			["lodge_Windows"] = { material = "Neon", color = { 255, 196, 110 } },
		},
	},
	["mountain_hill"] = {
		category = "Mountains",
		collision = "Default",
		parts = {
			["mountain_hill"] = { texture = "palette.png" },
		},
	},
	["mountain_peak"] = {
		category = "Mountains",
		collision = "Default",
		parts = {
			["mountain_peak"] = { texture = "palette.png" },
		},
	},
	["mountain_range"] = {
		category = "Mountains",
		collision = "Default",
		parts = {
			["mountain_range"] = { texture = "palette.png" },
		},
	},
	["pine_leaning"] = {
		category = "Nature",
		collision = "Default",
		parts = {
			["pine_leaning"] = { texture = "palette.png" },
		},
	},
	["pine_medium"] = {
		category = "Nature",
		collision = "Default",
		parts = {
			["pine_medium"] = { texture = "palette.png" },
		},
	},
	["pine_small"] = {
		category = "Nature",
		collision = "Default",
		parts = {
			["pine_small"] = { texture = "palette.png" },
		},
	},
	["pine_tall"] = {
		category = "Nature",
		collision = "Default",
		parts = {
			["pine_tall"] = { texture = "palette.png" },
		},
	},
	["rail_flat"] = {
		category = "Park",
		collision = "Default",
		parts = {
			["rail_flat"] = { texture = "palette.png" },
		},
	},
	["rail_kink"] = {
		category = "Park",
		collision = "PreciseConvexDecomposition",
		parts = {
			["rail_kink"] = { texture = "palette.png" },
		},
	},
	["rock_boulder"] = {
		category = "Nature",
		collision = "Default",
		parts = {
			["rock_boulder"] = { texture = "palette.png" },
		},
	},
	["rock_cluster"] = {
		category = "Nature",
		collision = "Default",
		parts = {
			["rock_cluster"] = { texture = "palette.png" },
		},
	},
	["rock_flat"] = {
		category = "Nature",
		collision = "Default",
		parts = {
			["rock_flat"] = { texture = "palette.png" },
		},
	},
	["signpost"] = {
		category = "Props",
		collision = "Default",
		parts = {
			["signpost_Main"] = { texture = "palette.png" },
			["signpost_Signs"] = { texture = "signpost_arrows.png" },
		},
	},
	["slalom_blue"] = {
		category = "Park",
		collision = "Default",
		parts = {
			["slalom_blue"] = { texture = "palette.png" },
		},
	},
	["slalom_red"] = {
		category = "Park",
		collision = "Default",
		parts = {
			["slalom_red"] = { texture = "palette.png" },
		},
	},
	["snow_fence"] = {
		category = "Park",
		collision = "Default",
		parts = {
			["snow_fence"] = { texture = "palette.png" },
		},
	},
	["snowman"] = {
		category = "Props",
		collision = "Default",
		parts = {
			["snowman"] = { texture = "palette.png" },
		},
	},
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
