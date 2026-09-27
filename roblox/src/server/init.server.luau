--!strict
--[[
	SnowboardServer - lets players equip the board models in ReplicatedStorage.Snowboards.

	The board is welded under the character's feet (cosmetic, massless, no collision)
	and tagged "Snowboard" so every client plays its effects. The character is lifted
	a little so the feet sit on the bindings. Re-equipped automatically on respawn.

	From your own server code:
	  local BoardService = require(game.ServerScriptService.SnowboardServer.BoardService)
	  BoardService.equip(player, "board_inferno")
	  BoardService.unequip(player)
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Kit = ReplicatedStorage:WaitForChild("SnowboardKit")
local BoardService = require(script:WaitForChild("BoardService"))

local remote = Instance.new("RemoteEvent")
remote.Name = "BoardRemote"
remote.Parent = Kit

local lastRequest: { [Player]: number } = {}

remote.OnServerEvent:Connect(function(player, action, name)
	-- validate everything coming from the client
	if typeof(action) ~= "string" then
		return
	end
	local now = os.clock()
	if now - (lastRequest[player] or 0) < 0.4 then
		return
	end
	lastRequest[player] = now
	if action == "Equip" and typeof(name) == "string" and #name < 64 then
		BoardService.equip(player, name)
	elseif action == "Unequip" then
		BoardService.unequip(player)
	end
end)

game:GetService("Players").PlayerRemoving:Connect(function(player)
	lastRequest[player] = nil
end)

BoardService.start()
