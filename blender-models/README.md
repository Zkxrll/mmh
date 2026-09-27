# Blender → Roblox model toolkit

Models are written as short Python scripts, built with Blender 5 (running
headless as the `bpy` module), and exported as files Roblox Studio can import.

```
./setup.sh                          # one time: installs Blender (bpy) for Python 3.11
python3 build.py models/crate.py    # build one model  -> out/crate/
python3 build.py models/*.py        # build all of them
python3 build.py models/crate.py --no-render   # skip preview images (faster)
```

## What you get in `out/<name>/`

| File | Use |
|------|-----|
| `<name>.fbx` | **Import this into Roblox** (texture is embedded) |
| `<name>.obj` + `.mtl` | Alternative mesh format |
| `<name>.glb` | glTF, also importable into Roblox and most engines |
| `palette.png` | The color texture, if you need to set `TextureID` manually |
| `<name>.blend` | Open in desktop Blender to tweak by hand |
| `preview_front.jpg`, `preview_back.jpg` | Rendered previews |
| `info.txt` | Size in studs, triangle count, Roblox limit warnings |
| `manifest.json` | Parts, materials, collision, category - read by `roblox/tools/build_roblox.py` |

## Importing into Roblox Studio

1. **Home / Avatar tab → Import 3D** (or File → Import 3D) and pick the `.fbx`.
2. Compare the size in the importer preview with `info.txt`. If it doesn't
   match, change the importer's **File Dimensions / scale unit** setting to Studs.
3. Import. The model becomes a MeshPart, or a Model of MeshParts when the
   script sets `JOIN = False`.
4. If the colors come in grey, set the MeshPart's `TextureID` to the uploaded
   `palette.png`, or add a `SurfaceAppearance` with it as the ColorMap.

All models share one `palette.png` (upload it once). Boards and signs also carry their own
image texture (embedded in the FBX, copies in `textures/`).

Roblox limits: 20,000 triangles per mesh. `info.txt` warns if you go over;
use `rbx.decimate(obj, 0.5)` or split the model.

## Writing a model

Create `models/whatever.py`:

```python
NAME = "lamp_post"   # output folder / file name
JOIN = True          # False = separate MeshParts (doors, wheels, moving parts)
CATEGORY = "Props"   # Workspace.Map folder the Roblox setup script sorts it into
COLLISION = "Default"  # or "PreciseConvexDecomposition" for ramps, arches, houses

def build(rbx):
    rbx.cylinder(0.3, 10, loc=(0, 0, 5), col="dark_metal", sides=8)
    rbx.box((1.2, 1.2, 1.2), loc=(0, 0, 10.6), col="yellow", bevel=0.1)
```

1 unit = 1 stud. Z is up while building; export converts to Roblox's Y-up.
The pivot is placed at the bottom center of the model.

### Cheat sheet (`rbx.*`)

**Shapes**: `box`, `cylinder` (with `radius_top` for tapered), `cone`, `sphere`
(low-poly icosphere), `uv_sphere`, `torus`, `extrude_profile` (2D outline → solid:
blades, signs, logos), `lathe` (spin a profile: barrels, vases, pillars),
`mesh_from_data` (raw vertices/faces).
All take `loc=(x,y,z)`, `rot=(deg,deg,deg)`, `col="name"` or `col=(r,g,b)`.

**Edit**: `add_bevel`, `subdivide`, `mirror`, `array`, `solidify`,
`boolean(obj, cutter, "DIFFERENCE"|"UNION"|"INTERSECT")`, `decimate`,
`displace_noise` (rocks/terrain), `jitter` (hand-made low-poly look), `taper`,
`bend`, `twist`, `duplicate`, `join`, `shade_smooth`, `shade_flat`.

**More shapes**: `tube(points)` (rails, frames, handles), `heightfield(size, res, height_fn)`
(terrain / mountains).

**Color**: `paint(obj, col)`, `paint_faces(obj, col, where=lambda center, normal: ...)`.
Named colors are in `rbx.COLORS`.

**Special parts**: `glow(obj, col)` makes a Neon part (or `material="Glass"`), `textured(obj, png, uv_fn)`
gives a part its own image, `group(obj, "Door")` keeps pieces together as one MeshPart.

## What's in `models/`

| Group | Models |
|-------|--------|
| Snowboards | `board_frostbite`, `board_inferno`, `board_viper`, `board_cosmic`, `board_sunset`, `board_rookie` |
| Buildings | `lodge`, `cabin`, `board_shop` |
| Mountains | `mountain_peak`, `mountain_range`, `mountain_hill` |
| Nature | `pine_tall`, `pine_medium`, `pine_small`, `pine_leaning`, `rock_boulder`, `rock_flat`, `rock_cluster`, `ice_crystals` |
| Park | `kicker_small`, `kicker_big`, `rail_flat`, `rail_kink`, `grind_box`, `gate_start`, `gate_finish`, `slalom_red`, `slalom_blue`, `snow_fence` |
| Props | `lamp_post`, `signpost`, `lift_tower`, `lift_chair`, `campfire`, `snowman`, `bench`, `crate` |

Shared builders live in `models/_*.py` (boards, houses, terrain, nature, park, signs).

Other tools:
- `python3 sheet.py out/_sheet.png out/board_*` builds a contact sheet of previews
- `python3 showcase.py` composes the exported `.glb` files into a resort scene and renders `out/_showcase.jpg`
- `python3 sfx/make_sfx.py` synthesizes the sound effects into `sfx/out/`

Roblox scripts, effects and the install guide are in `../roblox/`.
