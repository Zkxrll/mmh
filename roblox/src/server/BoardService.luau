--!strict
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Kit = ReplicatedStorage:WaitForChild("SnowboardKit")
local Config = require(Kit:WaitForChild("Config"))

local BoardService = {}

local BOARD_NAME = "EquippedSnowboard"
local originalHip: { [Humanoid]: number } = {}

local function boardsFolder(): Instance?
	return ReplicatedStorage:FindFirstChild(Config.BoardsFolder)
end

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

function BoardService.unequip(player: Player, keepAttribute: boolean?)
	local character = player.Character
	if character then
		local old = character:FindFirstChild(BOARD_NAME)
		if old then
			old:Destroy()
		end
		local hum = character:FindFirstChildOfClass("Humanoid")
		if hum and originalHip[hum] then
			hum.HipHeight = originalHip[hum]
			originalHip[hum] = nil
		end
	end
	if not keepAttribute then
		player:SetAttribute("EquippedBoard", nil)
	end
end

function BoardService.equip(player: Player, name: string): boolean
	local folder = boardsFolder()
	local template = folder and folder:FindFirstChild(name)
	if not template or not template:IsA("Model") then
		return false
	end
	local character = player.Character
	local hum = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not character or not hum or not root or not root:IsA("BasePart") or hum.Health <= 0 then
		return false
	end
	BoardService.unequip(player, true)

	local board = template:Clone()
	board.Name = BOARD_NAME
	board:SetAttribute("BoardName", name)
	board:SetAttribute("OwnerUserId", player.UserId)
	local deck = findDeck(board)
	if not deck then
		board:Destroy()
		return false
	end
	board.PrimaryPart = deck
	for _, d in board:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = false
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.Massless = true
		end
	end

	-- lift the rider, then sit the board between the feet and the ground
	if not originalHip[hum] then
		originalHip[hum] = hum.HipHeight
	end
	local legs = if hum.RigType == Enum.HumanoidRigType.R6 then 2 else 0
	hum.HipHeight = originalHip[hum] + Config.Board.Lift
	local groundY = -(root.Size.Y / 2) - hum.HipHeight - legs
	-- board's long axis along the character's facing (arcade style)
	local longIsX = deck.Size.X > deck.Size.Z
	local turn = if longIsX then CFrame.Angles(0, math.pi / 2, 0) else CFrame.identity
	local target = root.CFrame * CFrame.new(0, groundY + deck.Size.Y / 2, 0) * turn
	board:PivotTo(target * deck.CFrame:ToObjectSpace(board:GetPivot()))

	for _, d in board:GetDescendants() do
		if d:IsA("BasePart") and d ~= deck then
			local w = Instance.new("WeldConstraint")
			w.Part0 = deck
			w.Part1 = d
			w.Parent = deck
		end
	end
	local rootWeld = Instance.new("WeldConstraint")
	rootWeld.Name = "BoardWeld"
	rootWeld.Part0 = root
	rootWeld.Part1 = deck
	rootWeld.Parent = deck

	board.Parent = character
	CollectionService:AddTag(board, "Snowboard")
	player:SetAttribute("EquippedBoard", name)
	return true
end

function BoardService.start()
	local function onPlayer(player: Player)
		player.CharacterAdded:Connect(function(character)
			local hum = character:WaitForChild("Humanoid", 10)
			if not hum then
				return
			end
			task.wait(0.2)
			local want = player:GetAttribute("EquippedBoard")
			if typeof(want) == "string" then
				BoardService.equip(player, want)
			end
		end)
	end
	for _, p in Players:GetPlayers() do
		onPlayer(p)
	end
	Players.PlayerAdded:Connect(onPlayer)
end

return BoardService
