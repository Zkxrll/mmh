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
| `preview_front.png`, `preview_back.png` | Rendered previews |
| `info.txt` | Size in studs, triangle count, Roblox limit warnings |

## Importing into Roblox Studio

1. **Home / Avatar tab → Import 3D** (or File → Import 3D) and pick the `.fbx`.
2. Compare the size in the importer preview with `info.txt`. If it doesn't
   match, change the importer's **File Dimensions / scale unit** setting to Studs.
3. Import. The model becomes a MeshPart, or a Model of MeshParts when the
   script sets `JOIN = False`.
4. If the colors come in grey, set the MeshPart's `TextureID` to the uploaded
   `palette.png`, or add a `SurfaceAppearance` with it as the ColorMap.

Roblox limits: 20,000 triangles per mesh. `info.txt` warns if you go over;
use `rbx.decimate(obj, 0.5)` or split the model.

## Writing a model

Create `models/whatever.py`:

```python
NAME = "lamp_post"   # output folder / file name
JOIN = True          # False = separate MeshParts (doors, wheels, moving parts)

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

**Color**: `paint(obj, col)`, `paint_faces(obj, col, where=lambda center, normal: ...)`.
Named colors are in `rbx.COLORS`.

Examples: `models/crate.py` (bevels, boolean cut-outs), `models/sword.py`
(extruded profiles), `models/tree.py` (tapering, jittered low-poly).
