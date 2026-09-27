# Snowboard game kit for Roblox Studio

Everything needed to drop the new boards, map assets, effects and sounds into your place.

```
blender-models/out/<model>/<model>.fbx   3D models (import these)
roblox/build/*.rbxm                      scripts, ready to drag into Studio
roblox/studio/*.luau                     one-time Studio Command Bar tools
roblox/sfx/*.ogg                         sound effects to upload
roblox/textures/*.png                    particle textures + fallback model textures
```

## Install (about 15 minutes)

### 1. Scripts
Drag each file from `roblox/build/` into the Explorer:

| File | Where it goes |
|------|---------------|
| `SnowboardKit.rbxm` | **ReplicatedStorage** |
| `SnowboardClient.rbxm` | **StarterPlayer → StarterPlayerScripts** |
| `SnowboardServer.rbxm` | **ServerScriptService** |

Alternative: open `roblox/studio/INSTALL_SCRIPTS.luau`, copy all of it, paste into the
**Command Bar** (View → Command Bar) and press Enter. Running it again updates the scripts
and keeps your `Config`.

### 2. Models
1. **File → Import 3D** (or Avatar tab → Import 3D), pick an `.fbx` from `blender-models/out/<model>/`.
2. Check the size in the importer against `info.txt` in the same folder (e.g. the lodge is
   26 × 32 × 34 studs). If it's wrong, set the importer's scale unit to **Studs**.
3. Import. Repeat for the models you want. At minimum, import the six `board_*` models.

### 3. Set up the imported models
Paste `roblox/studio/SetupImportedAssets.luau` into the Command Bar and press Enter. It:
- applies Neon glow, Glass icicles, SmoothPlastic, collision fidelity, and anchoring
- tags props for the effects (`Campfire`, `Lamp`, `Building`, `IceCrystal`, `Grindable`, `FinishGate`)
- moves the boards to **ReplicatedStorage.Snowboards**, which the board picker reads
- sorts map pieces into **Workspace.Map.<Category>** and keeps copies in **ServerStorage.MapAssets**

If a model's colors come in grey, upload `roblox/textures/palette.png` and put its id in
`PALETTE_TEXTURE` at the top of the script, then run it again. All models share this one palette.

### 4. Lighting
Paste `roblox/studio/SetupLighting.luau` into the Command Bar. Change `PRESET` to
`SunnyPowder`, `GoldenHour`, `Blizzard` or `Night`. It sets Future lighting, atmosphere haze for
the mountains, bloom, color grading, sun rays, depth of field, snow-tinted terrain colors, and
how much snow falls. Presets can also be switched in-game from a server script:
`require(ReplicatedStorage.SnowboardKit.LightingPresets).apply("Blizzard")`.

### 5. Sounds and particle textures
Upload `roblox/sfx/*.ogg` and `roblox/textures/fx_*.png` (Asset Manager → Bulk Import).
Paste the ids into `ReplicatedStorage.SnowboardKit.Config` (`Config.Sounds`, `Config.Textures`).
Until then, particles use built-in Roblox textures and the sounds stay silent.

### 6. Fill the mountain with trees (optional)
Put a Part over the area and name it `ScatterRegion`. Then paste `roblox/studio/ScatterAssets.luau`
into the Command Bar. It places pines and rocks on terrain, skipping slopes that are too steep.
Change `SEED` to re-roll the layout, and press Ctrl+Z to undo.

### 7. Play
Press Play and click **BOARDS** (bottom left). Pick a board and it snaps under your feet. Ride
and jump to see snow spray, trails, landing bursts, spins (180/360/540...), Big Air, rail grinds,
and the confetti at the finish gate.

## What the effects do

| Effect | When |
|--------|------|
| Snow spray from the tail | Riding on snow; more with speed |
| Carve spray off the edge | Turning hard (sliding sideways) |
| Track ribbon on the snow | Board on the ground |
| Neon glow trail (board's glow color) | Fast, or in the air |
| Jump pop, landing burst, powder puff, camera shake | Leaving and hitting the ground |
| Spin detection → "360!" popup + sparkle + chime | Rotating in the air |
| Grind sparks + grind sound | Riding on anything tagged `Grindable` |
| FOV boost and speed lines | High speed (local player only) |
| Falling snow + wind | Always; amount set by the lighting preset |
| Fire, smoke, embers, flickering light, crackle | Campfires |
| Warm lights | Lamp posts, lanterns, house windows |
| Confetti + "FINISH!" | Riding through the finish gate |

## Using your own snowboard system
You don't have to use the board picker. To get all the effects on your existing board:
- tag your board **Model** `Snowboard` (CollectionService)
- set its attribute `OwnerUserId` to the rider's UserId
- parent it to the character, or make its main part the model's PrimaryPart

Listen for tricks to give points (client side):
```lua
local SnowboardFX = require(game.ReplicatedStorage.SnowboardKit.SnowboardFX)
SnowboardFX.TrickLanded:Connect(function(board, trick, info)
	print(trick, info.airTime, info.spin) -- "360", 1.2, 372
end)
```
From the server you can equip boards yourself:
`require(game.ServerScriptService.SnowboardServer.BoardService).equip(player, "board_inferno")`.

## Rebuilding
```
python3 blender-models/build.py blender-models/models/*.py   # models
python3 blender-models/sfx/make_sfx.py                       # sounds
python3 roblox/tools/make_fx_textures.py                     # particle textures
python3 roblox/tools/build_roblox.py                         # setup script, installer, .rbxm, copies
```
The Luau is strict-typed and checked with luau-lsp against the Roblox API:
`rojo sourcemap default.project.json -o sourcemap.json && luau-lsp analyze --sourcemap=sourcemap.json --definitions=@roblox=globalTypes.d.luau src`
