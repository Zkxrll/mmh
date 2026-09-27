"""
Compose the exported models into one resort scene and render a hero image.
    python3 showcase.py [out.png] [--quick]
Imports out/<name>/<name>.glb (exactly what Roblox gets), so it doubles as an export check.
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
quick = "--quick" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
target = args[0] if args else os.path.join(OUT, "_showcase.png")  # convert to .jpg for sharing
rnd = random.Random(4)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
cache = {}


def load(name):
    """Import a model once, then return linked duplicates."""
    if name not in cache:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, name, name + ".glb"))
        objs = [o for o in bpy.data.objects if o not in before]
        for o in objs:
            o.hide_render = True
            o.hide_set(True)
        cache[name] = objs
    return cache[name]


def place(name, loc, yaw=0.0, scale=1.0, tilt=(0.0, 0.0)):
    empty = bpy.data.objects.new(name + "_inst", None)
    scn.collection.objects.link(empty)
    for src in load(name):
        if src.type != "MESH":
            continue
        o = src.copy()  # shares mesh data
        scn.collection.objects.link(o)
        o.hide_render = False
        o.hide_set(False)
        o.parent = empty
        glowify(o)
    empty.location = loc
    empty.rotation_euler = (math.radians(tilt[0]), math.radians(tilt[1]), math.radians(yaw))
    empty.scale = (scale, scale, scale)
    return empty


def glowify(o):
    """Neon parts glow in Roblox; emulate it with emission here."""
    n = o.name.lower()
    if not ("neon" in n or "windows" in n or "glow" in n):
        return
    for slot in o.material_slots:
        m = slot.material
        if not m or m.get("_glow"):
            continue
        m = m.copy()
        m["_glow"] = True
        slot.material = m
        m.use_nodes = True
        bsdf = next((nd for nd in m.node_tree.nodes if nd.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            col = bsdf.inputs["Base Color"].default_value
            bsdf.inputs["Emission Color"].default_value = col
            bsdf.inputs["Emission Strength"].default_value = 6.0


# ---------------------------------------------------------------- layout ----
# ground: big snowy plane with gentle bumps
bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=120, size=1600, location=(0, 300, 0))
ground = bpy.context.active_object
from mathutils import noise  # noqa: E402
for v in ground.data.vertices:
    p = ground.matrix_world @ v.co
    d = max(0.0, (p - Vector((0, 20, 0))).length - 60) / 400
    v.co.z = 6 * noise.noise(p * 0.01) * min(1, d * 3) - 0.3
gm = bpy.data.materials.new("snow_ground")
gm.use_nodes = True
b = gm.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.84, 0.89, 0.97, 1)
b.inputs["Roughness"].default_value = 0.6
ground.data.materials.append(gm)
for p in ground.data.polygons:
    p.use_smooth = True

# backdrop mountains
place("mountain_peak", (60, 1050, -5), yaw=10, scale=2.2)
place("mountain_range", (-700, 850, -5), yaw=25, scale=1.6)
place("mountain_range", (720, 900, -5), yaw=-30, scale=1.5)
place("mountain_hill", (-300, 420, -3), yaw=40, scale=1.3)
place("mountain_hill", (330, 480, -3), yaw=-20, scale=1.5)

# village
place("lodge", (0, 70, 0), yaw=0)
place("cabin", (-52, 48, 0), yaw=22)
place("board_shop", (50, 40, 0), yaw=-24)
place("lift_tower", (95, 150, 0), yaw=-30)
place("lift_tower", (135, 280, 0), yaw=-30)
place("ice_crystals", (-78, 105, 0), yaw=30, scale=1.6)

# path with lamps, sign and start gate
for k, y in enumerate((-12, 8, 28)):
    place("lamp_post", (-9, y, 0), yaw=180)
    place("lamp_post", (9, y + 10, 0), yaw=0)
place("signpost", (14, -4, 0), yaw=-20)
place("gate_start", (0, 2, 0), yaw=0)

# terrain park on the right
place("kicker_big", (38, -30, 0), yaw=90)
place("rail_kink", (-34, -30, 0), yaw=90)
place("grind_box", (-18, -45, 0), yaw=90)
place("snow_fence", (26, -12, 0), yaw=0)
place("slalom_red", (62, -8, 0), yaw=10)
place("slalom_blue", (70, 12, 0), yaw=10)

# cosy corner
place("campfire", (-26, 14, 0))
place("bench", (-26, 21, 0), yaw=180)
place("snowman", (-38, 6, 0), yaw=25)

# hero boards stuck in the snow near the camera
for k, (name, x) in enumerate((("board_inferno", -7.6), ("board_frostbite", -3.8), ("board_cosmic", 0.0),
                              ("board_viper", 3.8), ("board_sunset", 7.6))):
    # top graphic facing the camera, leaning back a little, planted in the snow
    place(name, (x, -60 + abs(x) * 0.25, -0.9), yaw=rnd.uniform(-8, 8) - x * 1.5,
          tilt=(74 + rnd.uniform(-3, 3), rnd.uniform(-4, 4)))

# forest
trees = ["pine_tall", "pine_medium", "pine_small", "pine_leaning"]
for _ in range(140):
    ang = rnd.uniform(0, 2 * math.pi)
    rad = rnd.uniform(90, 420)
    x, y = math.cos(ang) * rad * 1.3, 70 + math.sin(ang) * rad
    if y < -20 or (abs(x) < 70 and y < 140):
        continue
    place(rnd.choice(trees), (x, y, 0), yaw=rnd.uniform(0, 360), scale=rnd.uniform(0.8, 1.5))
for x, y in ((-70, 30), (75, 70), (-95, 70), (100, 20), (-60, -20), (80, -40)):
    place(rnd.choice(trees), (x, y, 0), yaw=rnd.uniform(0, 360), scale=rnd.uniform(0.9, 1.3))
for _ in range(26):
    x, y = rnd.uniform(-150, 150), rnd.uniform(-40, 200)
    if abs(x) < 60 and -60 < y < 110:
        continue
    place(rnd.choice(["rock_boulder", "rock_flat", "rock_cluster"]), (x, y, -0.3), yaw=rnd.uniform(0, 360),
          scale=rnd.uniform(0.8, 1.8))

# ----------------------------------------------------------------- light ----
world = bpy.data.worlds.new("sky")
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
try:
    sky = nt.nodes.new("ShaderNodeTexSky")
    for t in ("NISHITA", "MULTIPLE_SCATTERING", "SINGLE_SCATTERING"):
        try:
            sky.sky_type = t
            break
        except TypeError:
            continue
    sky.sun_elevation = math.radians(11)
    sky.sun_rotation = math.radians(235)
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.25
except Exception as e:  # fall back to a flat sky
    print("sky texture unavailable:", e)
    bg.inputs["Color"].default_value = (0.55, 0.7, 0.95, 1)
scn.world = world

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(76), 0, math.radians(-55)))
sun = bpy.context.active_object
sun.data.energy = 3.2
sun.data.color = (1.0, 0.82, 0.62)
sun.data.angle = math.radians(2)

cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 26
cam_data.clip_start = 0.5
cam_data.clip_end = 6000
cam = bpy.data.objects.new("cam", cam_data)
scn.collection.objects.link(cam)
cam.location = (4, -76, 5.5)
cam.rotation_euler = (Vector((0, 60, 11)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scn.camera = cam
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 18
cam_data.dof.aperture_fstop = 16

scn.render.engine = "CYCLES"
scn.cycles.device = "CPU"
scn.cycles.samples = 16 if quick else 96
scn.cycles.use_denoising = True
scn.render.resolution_x = 960 if quick else 1920
scn.render.resolution_y = 540 if quick else 1080
scn.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in scn.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
looks = [i.identifier for i in scn.view_settings.bl_rna.properties["look"].enum_items]
for want in ("AgX - Medium High Contrast", "Medium High Contrast", "AgX - Punchy", "Punchy"):
    if want in looks:
        scn.view_settings.look = want
        break
scn.view_settings.exposure = -0.7
scn.render.filepath = target
bpy.ops.render.render(write_still=True)
print("rendered", target)
