# Prompt for Claude Code on your PC (with the Roblox Studio MCP)

1. Open Roblox Studio with your snowboard place, and make sure the Studio MCP plugin shows as connected.
2. In a terminal, `git clone` the repo (or `git pull`), then `git checkout claude/nifty-einstein-ufvvay`.
3. Start `claude` inside the repo folder and paste everything below the line.

---

You're connected to my Roblox Studio through the Roblox Studio MCP. My game is a snowboarding game. This repo contains an asset and effects kit built for it in an earlier session that had no access to Studio. Your job is to install that kit into my place, fit it to my existing map and systems, and make the whole map look polished and professional.

## Read these first
- `roblox/README.md`: install guide, what every script does, and how to hook in an existing snowboard system
- `roblox/src/`: Luau source. `shared/` goes to ReplicatedStorage.SnowboardKit, `client/` to StarterPlayerScripts.SnowboardClient, `server/` to ServerScriptService.SnowboardServer
- `roblox/studio/`: Command Bar tools: `INSTALL_SCRIPTS.luau`, `SetupImportedAssets.luau`, `SetupLighting.luau`, `ScatterAssets.luau`
- `blender-models/README.md` and `blender-models/out/<model>/`: 38 models as `.fbx` files, each with `info.txt` (size in studs) and `manifest.json` (parts, glow materials, collision). Preview images are in `blender-models/out/_sheet_*.jpg` and `_showcase.jpg`.
- `blender-models/rbx.py` + `blender-models/models/*.py`: the scripts that generate the models (Blender runs as a Python module, `pip install bpy` on Python 3.11). You can change a model and rebuild it with `python3 blender-models/build.py blender-models/models/<name>.py`.

## Step 1: Look before changing anything
Use the Studio tools to explore my place and write me a short report covering:
- the map layout (terrain, main slopes, spawn, buildings; describe or list the important Models and Parts)
- the existing house or houses: where they are, their size and orientation, and what they're built from
- any existing snowboard system: how boards are attached to players, how movement works, and which scripts are involved
- the current Lighting, Atmosphere and post-processing settings
- anything that would conflict with the kit: name clashes in ReplicatedStorage or ServerScriptService, existing FOV or camera scripts, existing particle systems

Then give me a plan and wait for my OK before making big changes.

## Step 2: Install the scripts
Create the scripts in Studio with the same hierarchy as `roblox/src/`, using the file contents. The simplest way is to run `roblox/studio/INSTALL_SCRIPTS.luau` in Studio. Keep an existing `Config` if there is one.

If I already have a snowboard system, don't replace it. Integrate with it instead: tag my board model `Snowboard` and set its `OwnerUserId` attribute (see "Using your own snowboard system" in `roblox/README.md`). In that case, decide with me whether the kit's board picker and `BoardService` are still wanted. Watch for conflicts with my camera and FOV code (`CameraFX.luau`); adjust or disable in `Config.Camera` if needed.

## Step 3: Get the models in
Studio scripts probably can't run the 3D Importer. Check what your MCP tools can do. If you can't import `.fbx` files yourself, give me an exact list of the files to import through **File → Import 3D**, in priority order:
1. the six `board_*` models
2. `lodge`, `cabin`, `board_shop`
3. the mountains and pines
4. the park features and props

After I say they're imported, run `roblox/studio/SetupImportedAssets.luau`. Then check the result: materials, the Neon/Glass parts, boards in ReplicatedStorage.Snowboards, and map pieces in Workspace.Map. Fix any part-name matching problems, since the importer's naming was a guess. If colors came in grey, walk me through uploading `roblox/textures/palette.png` and set `PALETTE_TEXTURE`.

## Step 4: Make the map better
- Replace or upgrade my existing house(s) with `lodge` / `cabin` / `board_shop`, placed where the old ones were, at the same scale and orientation. Ask before deleting anything; move the originals to ServerStorage.OldMap instead.
- Place mountains as a backdrop ring around the playable area. They can be scaled up a lot.
- Put a `ScatterRegion` over the slopes, keeping the riding lines clear, and run `ScatterAssets.luau` for trees and rocks. Tune the density until it looks natural.
- Build a terrain park where it fits the slope: kickers with proper run-ins and landings, rails, the grind box, the start gate at the top and the finish gate at the bottom. Make sure every jump is actually rideable.
- Add lamp posts along paths, a signpost at junctions, and a chairlift line of `lift_tower` models going up the mountain. Put the campfire, benches and snowman near the lodge as a spawn hangout.
- Run `SetupLighting.luau` and try `SunnyPowder`, `GoldenHour` and `Night`. Pick the best one for my map and tune it.
- Improve the terrain itself: snow materials, smoother slopes, rock outcrops on steep parts, and no floating or clipping objects.

## Step 5: Test
Use play-testing (or whatever your MCP allows) and check the Output window for errors. Equip a board, ride, jump, grind and cross the finish gate, then confirm the effects and popups appear. Fix any runtime errors in the Luau. The code was type-checked but never run in Roblox. Update the matching files in `roblox/src/` too, so the repo stays in sync.

## Step 6: Sounds and textures
The sounds in `roblox/sfx/*.ogg` and the particle textures in `roblox/textures/fx_*.png` need uploading. Tell me exactly how to upload them (Asset Manager → Bulk Import). Once I give you the IDs, fill in `Config.Sounds` and `Config.Textures`.

## Rules
- Tell me what you're about to change before any big or destructive change, and keep things undoable (use ChangeHistoryService waypoints).
- Don't delete my scripts or parts. Move replaced things to ServerStorage.OldMap.
- Keep performance in mind: don't add hundreds of lights, and keep triangle counts sane.
- When done, summarize what changed, where things are, and anything left for me to do.
