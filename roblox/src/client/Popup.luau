--!strict
-- Big stylised trick text ("360!", "BIG AIR!") that pops, wobbles and fades.

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local Popup = {}

local gui: ScreenGui? = nil
local stack = 0

local COLORS = {
	default = { Color3.fromRGB(255, 255, 255), Color3.fromRGB(140, 220, 255) },
	spin = { Color3.fromRGB(255, 240, 120), Color3.fromRGB(255, 140, 40) },
	air = { Color3.fromRGB(160, 255, 200), Color3.fromRGB(40, 200, 255) },
	grind = { Color3.fromRGB(255, 200, 255), Color3.fromRGB(190, 90, 255) },
	finish = { Color3.fromRGB(255, 255, 255), Color3.fromRGB(255, 90, 120) },
}

local function getGui(): ScreenGui
	if gui and gui.Parent then
		return gui
	end
	local g = Instance.new("ScreenGui")
	g.Name = "TrickPopups"
	g.ResetOnSpawn = false
	g.IgnoreGuiInset = true
	g.DisplayOrder = 10
	g.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
	gui = g
	return g
end

function Popup.show(text: string, style: string?, subtitle: string?)
	local colors = COLORS[style or "default"] or COLORS.default
	local g = getGui()
	stack += 1
	local slot = stack
	local label = Instance.new("TextLabel")
	label.AnchorPoint = Vector2.new(0.5, 0.5)
	label.Position = UDim2.fromScale(0.5, 0.3 + ((slot - 1) % 3) * 0.08)
	label.Size = UDim2.fromScale(0.6, 0.11)
	label.BackgroundTransparency = 1
	label.Font = Enum.Font.FredokaOne
	label.Text = text
	label.TextScaled = true
	label.TextColor3 = Color3.new(1, 1, 1)
	label.Rotation = math.random(-6, 6)
	label.Parent = g

	local grad = Instance.new("UIGradient")
	grad.Color = ColorSequence.new(colors[1], colors[2])
	grad.Rotation = 90
	grad.Parent = label
	local stroke = Instance.new("UIStroke")
	stroke.Thickness = 4
	stroke.Color = Color3.fromRGB(20, 25, 45)
	stroke.Parent = label
	local scale = Instance.new("UIScale")
	scale.Scale = 0.2
	scale.Parent = label

	if subtitle then
		local sub = Instance.new("TextLabel")
		sub.AnchorPoint = Vector2.new(0.5, 0)
		sub.Position = UDim2.fromScale(0.5, 1)
		sub.Size = UDim2.fromScale(0.8, 0.4)
		sub.BackgroundTransparency = 1
		sub.Font = Enum.Font.GothamBold
		sub.Text = subtitle
		sub.TextScaled = true
		sub.TextColor3 = Color3.fromRGB(230, 240, 255)
		sub.Parent = label
		local s2 = Instance.new("UIStroke")
		s2.Thickness = 2
		s2.Color = Color3.fromRGB(20, 25, 45)
		s2.Parent = sub
	end

	TweenService:Create(scale, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 })
		:Play()
	task.delay(1.1, function()
		TweenService:Create(label, TweenInfo.new(0.45), {
			TextTransparency = 1,
			Position = label.Position - UDim2.fromScale(0, 0.06),
		}):Play()
		TweenService:Create(stroke, TweenInfo.new(0.45), { Transparency = 1 }):Play()
		task.wait(0.5)
		label:Destroy()
		stack -= 1
	end)
end

return Popup
