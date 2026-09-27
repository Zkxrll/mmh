--!strict
-- Board picker: a "BOARDS" button opens a panel of cards, each with a slowly
-- spinning 3D preview of the board (ViewportFrame) and an EQUIP button.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local Kit = ReplicatedStorage:WaitForChild("SnowboardKit")
local Config = require(Kit:WaitForChild("Config"))
local Effects = require(Kit:WaitForChild("Effects"))

local BoardPicker = {}

local PANEL_BG = Color3.fromRGB(18, 24, 42)
local CARD_BG = Color3.fromRGB(32, 42, 70)
local ACCENT = Color3.fromRGB(90, 200, 255)

local function corner(parent: Instance, r: number)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, r)
	c.Parent = parent
end

local function stroke(parent: Instance, color: Color3, t: number)
	local s = Instance.new("UIStroke")
	s.Color = color
	s.Thickness = t
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = parent
end

local function prettyName(name: string): string
	local n = name:gsub("^board_", ""):gsub("_", " ")
	return n:upper()
end

local function button(parent: Instance, text: string, color: Color3): TextButton
	local b = Instance.new("TextButton")
	b.AutoButtonColor = false
	b.BackgroundColor3 = color
	b.Font = Enum.Font.GothamBlack
	b.Text = text
	b.TextScaled = true
	b.TextColor3 = Color3.new(1, 1, 1)
	b.Parent = parent
	corner(b, 10)
	local pad = Instance.new("UIPadding")
	pad.PaddingTop = UDim.new(0.18, 0)
	pad.PaddingBottom = UDim.new(0.18, 0)
	pad.Parent = b
	local base = color
	b.MouseEnter:Connect(function()
		TweenService:Create(b, TweenInfo.new(0.12), { BackgroundColor3 = base:Lerp(Color3.new(1, 1, 1), 0.2) }):Play()
	end)
	b.MouseLeave:Connect(function()
		TweenService:Create(b, TweenInfo.new(0.12), { BackgroundColor3 = base }):Play()
	end)
	return b
end

local function viewport(parent: Instance, model: Model): (ViewportFrame, Model)
	local vp = Instance.new("ViewportFrame")
	vp.BackgroundColor3 = Color3.fromRGB(45, 60, 100)
	vp.Size = UDim2.new(1, -16, 0.62, 0)
	vp.Position = UDim2.fromOffset(8, 8)
	vp.Ambient = Color3.fromRGB(170, 180, 200)
	vp.LightColor = Color3.fromRGB(255, 250, 240)
	vp.LightDirection = Vector3.new(-1, -2, -1)
	vp.Parent = parent
	corner(vp, 10)
	local grad = Instance.new("UIGradient")
	grad.Color = ColorSequence.new(Color3.fromRGB(120, 170, 255), Color3.fromRGB(40, 50, 90))
	grad.Rotation = 90
	grad.Parent = vp

	local clone = model:Clone()
	for _, d in clone:GetDescendants() do
		if d:IsA("Script") or d:IsA("LocalScript") then
			d:Destroy()
		end
	end
	clone:PivotTo(CFrame.identity)
	clone.Parent = vp
	local cf, size = clone:GetBoundingBox()
	local cam = Instance.new("Camera")
	cam.FieldOfView = 30
	local dist = size.Magnitude * 1.7
	cam.CFrame = CFrame.lookAt(cf.Position + Vector3.new(dist * 0.55, dist * 0.55, dist * 0.6), cf.Position)
	cam.Parent = vp
	vp.CurrentCamera = cam
	return vp, clone
end

function BoardPicker.start()
	local player = Players.LocalPlayer
	local folder = ReplicatedStorage:WaitForChild(Config.BoardsFolder, 30)
	local remote = Kit:WaitForChild("BoardRemote", 30)
	if not folder or not remote or not remote:IsA("RemoteEvent") then
		warn("[SnowboardKit] BoardPicker: no ReplicatedStorage." .. Config.BoardsFolder .. " or BoardRemote found")
		return
	end
	local click = Effects.sound(SoundService, "UISelect", Config.Sounds.UISelect, false, 0.5)
	local equipSound = Effects.sound(SoundService, "EquipClick", Config.Sounds.Equip, false, 0.7)

	local gui = Instance.new("ScreenGui")
	gui.Name = "BoardPicker"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.Parent = player:WaitForChild("PlayerGui")

	local open = button(gui, "BOARDS", ACCENT)
	open.AnchorPoint = Vector2.new(0, 1)
	open.Position = UDim2.new(0, 16, 1, -16)
	open.Size = UDim2.fromOffset(150, 48)
	stroke(open, Color3.fromRGB(20, 30, 60), 3)

	local panel = Instance.new("Frame")
	panel.AnchorPoint = Vector2.new(0.5, 0.5)
	panel.Position = UDim2.fromScale(0.5, 0.5)
	panel.Size = UDim2.fromScale(0.7, 0.72)
	panel.BackgroundColor3 = PANEL_BG
	panel.BackgroundTransparency = 0.05
	panel.Visible = false
	panel.Parent = gui
	corner(panel, 18)
	stroke(panel, ACCENT, 2)
	local sizeLimit = Instance.new("UISizeConstraint")
	sizeLimit.MaxSize = Vector2.new(980, 640)
	sizeLimit.Parent = panel
	local panelScale = Instance.new("UIScale")
	panelScale.Parent = panel

	local title = Instance.new("TextLabel")
	title.BackgroundTransparency = 1
	title.Position = UDim2.fromOffset(24, 12)
	title.Size = UDim2.new(1, -120, 0, 44)
	title.Font = Enum.Font.GothamBlack
	title.Text = "CHOOSE YOUR BOARD"
	title.TextColor3 = Color3.new(1, 1, 1)
	title.TextScaled = true
	title.TextXAlignment = Enum.TextXAlignment.Left
	title.Parent = panel

	local close = button(panel, "X", Color3.fromRGB(220, 60, 80))
	close.AnchorPoint = Vector2.new(1, 0)
	close.Position = UDim2.new(1, -14, 0, 14)
	close.Size = UDim2.fromOffset(40, 40)

	local list = Instance.new("ScrollingFrame")
	list.BackgroundTransparency = 1
	list.BorderSizePixel = 0
	list.Position = UDim2.fromOffset(16, 68)
	list.Size = UDim2.new(1, -32, 1, -84)
	list.ScrollBarThickness = 6
	list.AutomaticCanvasSize = Enum.AutomaticSize.Y
	list.CanvasSize = UDim2.new()
	list.Parent = panel
	local grid = Instance.new("UIGridLayout")
	grid.CellSize = UDim2.fromOffset(210, 250)
	grid.CellPadding = UDim2.fromOffset(14, 14)
	grid.SortOrder = Enum.SortOrder.Name
	grid.Parent = list

	local spinning: { Model } = {}
	local equipButtons: { [string]: TextButton } = {}

	local function refresh()
		local current = player:GetAttribute("EquippedBoard")
		for name, b in equipButtons do
			local on = current == name
			b.Text = if on then "UNEQUIP" else "EQUIP"
			b.BackgroundColor3 = if on then Color3.fromRGB(230, 90, 70) else Color3.fromRGB(60, 190, 120)
		end
	end

	local function addCard(model: Model)
		local card = Instance.new("Frame")
		card.Name = model.Name
		card.BackgroundColor3 = CARD_BG
		card.Parent = list
		corner(card, 14)
		local _, clone = viewport(card, model)
		table.insert(spinning, clone)
		local label = Instance.new("TextLabel")
		label.BackgroundTransparency = 1
		label.Position = UDim2.new(0, 10, 0.64, 0)
		label.Size = UDim2.new(1, -20, 0.13, 0)
		label.Font = Enum.Font.GothamBold
		label.Text = prettyName(model.Name)
		label.TextColor3 = Color3.new(1, 1, 1)
		label.TextScaled = true
		label.Parent = card
		local equip = button(card, "EQUIP", Color3.fromRGB(60, 190, 120))
		equip.Position = UDim2.new(0, 12, 0.8, 0)
		equip.Size = UDim2.new(1, -24, 0.15, 0)
		equipButtons[model.Name] = equip
		equip.Activated:Connect(function()
			Effects.play(click)
			local on = player:GetAttribute("EquippedBoard") == model.Name
			remote:FireServer(if on then "Unequip" else "Equip", model.Name)
			if not on then
				Effects.play(equipSound)
			end
		end)
	end

	for _, m in folder:GetChildren() do
		if m:IsA("Model") then
			addCard(m)
		end
	end
	folder.ChildAdded:Connect(function(m)
		if m:IsA("Model") then
			addCard(m)
			refresh()
		end
	end)
	player:GetAttributeChangedSignal("EquippedBoard"):Connect(refresh)
	refresh()

	local function setOpen(v: boolean)
		Effects.play(click)
		if v then
			panel.Visible = true
			panelScale.Scale = 0.85
			TweenService:Create(panelScale, TweenInfo.new(0.25, Enum.EasingStyle.Back), { Scale = 1 }):Play()
		else
			panel.Visible = false
		end
	end
	open.Activated:Connect(function()
		setOpen(not panel.Visible)
	end)
	close.Activated:Connect(function()
		setOpen(false)
	end)

	local angle = 0
	RunService.RenderStepped:Connect(function(dt: number)
		if not panel.Visible then
			return
		end
		angle += dt * 0.8
		for _, m in spinning do
			m:PivotTo(CFrame.Angles(0, angle, 0))
		end
	end)
end

return BoardPicker
