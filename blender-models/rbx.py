"""
rbx.py - small helper library for building Roblox-ready models with Blender (bpy).

Units: 1 Blender unit = 1 Roblox stud. Build models at real stud sizes
(a Roblox character is ~5 studs tall, a door ~4x7 studs).

Colors: parts are painted with named colors. Every model shares ONE palette
texture (palette.png, all COLORS in a fixed order) and faces are UV-mapped onto
their swatch - upload palette.png once and it works for every MeshPart.

Special parts: glow(obj, color) marks a part as Neon. It is exported as its own
mesh and listed in manifest.json, which the Roblox setup script reads to set
Material / Color. group(obj, "Door") keeps parts together as one MeshPart when
the model is exported with JOIN = False.
"""

import math
import os
import random

import bpy  # must come before bmesh / mathutils
import bmesh
from mathutils import Euler, Matrix, Vector, noise

# Roblox MeshPart limit (triangles per mesh).
ROBLOX_TRI_LIMIT = 20000

# A few handy colors (RGB 0-255). Roblox BrickColor-ish names.
COLORS = {
    "white": (242, 243, 243),
    "black": (27, 42, 53),
    "dark_stone": (99, 95, 98),
    "stone": (163, 162, 165),
    "light_stone": (199, 193, 183),
    "red": (196, 40, 28),
    "bright_red": (255, 60, 50),
    "orange": (218, 133, 65),
    "yellow": (245, 205, 48),
    "gold": (239, 184, 56),
    "lime": (164, 189, 71),
    "green": (75, 151, 75),
    "dark_green": (40, 110, 50),
    "leaf": (90, 170, 70),
    "teal": (18, 238, 212),
    "blue": (13, 105, 172),
    "sky": (128, 187, 219),
    "purple": (107, 50, 124),
    "pink": (255, 102, 204),
    "brown": (124, 92, 70),
    "dark_brown": (86, 60, 45),
    "wood": (160, 115, 75),
    "light_wood": (204, 160, 110),
    "sand": (215, 197, 154),
    "metal": (150, 155, 165),
    "dark_metal": (70, 75, 85),
    "glow_cyan": (60, 240, 255),
    # winter
    "snow": (236, 242, 250),
    "snow_shadow": (200, 214, 232),
    "ice": (168, 214, 240),
    "deep_ice": (90, 160, 210),
    "rock": (110, 112, 120),
    "dark_rock": (72, 72, 82),
    "light_rock": (150, 150, 158),
    "pine": (38, 84, 62),
    "dark_pine": (26, 60, 46),
    "bark": (92, 64, 48),
    "timber": (120, 78, 50),
    "dark_timber": (78, 50, 34),
    "plaster": (232, 224, 208),
    "roof": (70, 52, 48),
    "window_glow": (255, 196, 110),
    "fire": (255, 140, 40),
    "ember": (255, 90, 30),
    "hot_pink": (255, 40, 140),
    "magenta": (190, 40, 220),
    "violet": (80, 40, 160),
    "navy": (20, 30, 70),
    "cyan": (40, 200, 240),
    "neon_green": (80, 255, 120),
    "flame_yellow": (255, 210, 60),
    "carbon": (35, 36, 42),
    "rubber": (45, 45, 50),
    "safety_orange": (255, 110, 20),
    "banner_blue": (30, 90, 200),
}
PALETTE_ORDER = list(COLORS)  # fixed order -> identical palette.png for every model

_palette = []  # color names used in the current model (for the report)


# ---------------------------------------------------------------- scene ----

def reset():
    """Start from an empty scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _palette.clear()
    scn = bpy.context.scene
    scn.unit_settings.system = "METRIC"
    scn.unit_settings.scale_length = 1.0


def color(name_or_rgb, name=None):
    """Register a color (name from COLORS or an (r,g,b) tuple). Returns its key."""
    if isinstance(name_or_rgb, str):
        if name_or_rgb not in COLORS:
            raise KeyError(f"unknown color '{name_or_rgb}', add it to COLORS or pass (r,g,b)")
        key = name_or_rgb
    else:
        key = name or "c_%02x%02x%02x" % tuple(name_or_rgb)
        COLORS[key] = tuple(name_or_rgb)
    if key not in _palette:
        _palette.append(key)
    return key


def _material(key):
    mat = bpy.data.materials.get("col_" + key)
    if mat is None:
        mat = bpy.data.materials.new("col_" + key)
        r, g, b = (c / 255 for c in COLORS[key])
        mat.diffuse_color = (_srgb_to_lin(r), _srgb_to_lin(g), _srgb_to_lin(b), 1)
    return mat


def _srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def paint(obj, col):
    """Give the whole object one color."""
    key = color(col)
    obj.data.materials.clear()
    obj.data.materials.append(_material(key))
    for p in obj.data.polygons:
        p.material_index = 0
    return obj


def paint_faces(obj, col, where):
    """Paint only faces whose world-space center satisfies where(center, normal)."""
    key = color(col)
    mat = _material(key)
    mats = obj.data.materials
    if mat.name not in [m.name for m in mats if m]:
        mats.append(mat)
    idx = [m.name for m in mats].index(mat.name)
    bpy.context.view_layer.update()  # refresh matrix_world after location / rotation changes
    mw = obj.matrix_world
    for p in obj.data.polygons:
        c = mw @ p.center
        n = (mw.to_3x3() @ p.normal).normalized()
        if where(c, n):
            p.material_index = idx
    return obj


# ----------------------------------------------------------- primitives ----

def _finish(obj, name, col, loc, rot):
    obj.name = name or obj.name
    if loc is not None:
        obj.location = Vector(loc)
    if rot is not None:
        obj.rotation_euler = Euler([math.radians(a) for a in rot])
    if col is not None:
        paint(obj, col)
    return obj


def box(size=(1, 1, 1), loc=(0, 0, 0), rot=None, col="stone", name=None, bevel=0.0, segments=1):
    """Box with size (x, y, z) in studs, centered at loc. Optional rounded edges."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.scale = size
    apply_transform(obj)
    _finish(obj, name, col, loc, rot)
    if bevel > 0:
        add_bevel(obj, bevel, segments)
    return obj


def cylinder(radius=0.5, depth=1, loc=(0, 0, 0), rot=None, col="stone", name=None, sides=12,
             radius_top=None):
    """Cylinder along Z. radius_top makes it a tapered cylinder / cone."""
    if radius_top is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius, depth=depth)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=radius, radius2=radius_top, depth=depth)
    return _finish(bpy.context.active_object, name, col, loc, rot)


def cone(radius=0.5, depth=1, loc=(0, 0, 0), rot=None, col="stone", name=None, sides=12):
    bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=radius, radius2=0, depth=depth)
    return _finish(bpy.context.active_object, name, col, loc, rot)


def sphere(radius=0.5, loc=(0, 0, 0), rot=None, col="stone", name=None, detail=2, smooth=False,
           scale=None):
    """Icosphere. detail 1 = very low poly, 2-3 = rounder."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=detail, radius=radius)
    obj = bpy.context.active_object
    if scale:
        obj.scale = scale
        apply_transform(obj)
    if smooth:
        shade_smooth(obj)
    return _finish(obj, name, col, loc, rot)


def uv_sphere(radius=0.5, loc=(0, 0, 0), rot=None, col="stone", name=None, segments=16, rings=8,
              smooth=True):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=radius)
    obj = bpy.context.active_object
    if smooth:
        shade_smooth(obj)
    return _finish(obj, name, col, loc, rot)


def torus(major=1, minor=0.25, loc=(0, 0, 0), rot=None, col="stone", name=None, seg=24, minor_seg=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=seg, minor_segments=minor_seg)
    return _finish(bpy.context.active_object, name, col, loc, rot)


def tube(points, radius=0.25, col="metal", sides=12, name="tube", joints=True):
    """Round bar through a list of points - rails, pipes, handles, frames."""
    from mathutils import Quaternion
    parts = []
    pts = [Vector(p) for p in points]
    for a, b in zip(pts, pts[1:]):
        d = b - a
        c = cylinder(radius=radius, depth=d.length, loc=(a + b) / 2, col=col, sides=sides)
        c.rotation_mode = "QUATERNION"
        c.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
        parts.append(c)
    if joints:
        for p in pts[1:-1]:
            parts.append(uv_sphere(radius=radius, loc=p, col=col, segments=sides, rings=max(4, sides // 2),
                                   smooth=False))
    obj = join(parts, name) if len(parts) > 1 else parts[0]
    return obj


def mesh_from_data(verts, faces, loc=(0, 0, 0), rot=None, col="stone", name="mesh"):
    """Build a mesh from raw vertex / face lists (full control over the shape)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([Vector(v) for v in verts], [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    _select(obj)
    return _finish(obj, name, col, loc, rot)


def extrude_profile(points, depth, loc=(0, 0, 0), rot=None, col="stone", name="profile", axis="Y"):
    """Extrude a 2D outline (list of (u, v) points, counter-clockwise) into a solid.
    The outline lies in the XZ plane and is extruded along Y (centered)."""
    n = len(points)
    h = depth / 2
    verts = [(u, -h, v) for u, v in points] + [(u, h, v) for u, v in points]
    faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, n + i, n + j, j])
    obj = mesh_from_data(verts, faces, loc, rot, col, name)
    recalc_normals(obj)
    return obj


def lathe(profile, loc=(0, 0, 0), rot=None, col="stone", name="lathe", sides=16):
    """Spin a profile of (radius, height) points around Z - vases, barrels, bottles, pillars."""
    verts, faces = [], []
    n = len(profile)
    for s in range(sides):
        a = 2 * math.pi * s / sides
        for r, z in profile:
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for s in range(sides):
        t = (s + 1) % sides
        for i in range(n - 1):
            faces.append([s * n + i, t * n + i, t * n + i + 1, s * n + i + 1])
    obj = mesh_from_data(verts, faces, loc, rot, col, name)
    merge_by_distance(obj)
    # close ends that do not reach the axis
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    edges = [e for e in bm.edges if e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(obj.data)
    bm.free()
    recalc_normals(obj)
    return obj


def glow(obj, col="window_glow", material="Neon"):
    """Mark a part as glowing (Roblox Neon). Exported as its own MeshPart."""
    paint(obj, col)
    obj["rbx_material"] = material
    obj["rbx_color"] = color(col)
    return obj


def textured(obj, image_path, uv_fn, roughness=0.45):
    """Give a part its own image texture instead of the palette.
    uv_fn(co, normal) -> (u, v) is called for every face corner (world space).
    The part is exported as its own MeshPart with the image embedded."""
    img = bpy.data.images.load(os.path.abspath(image_path), check_existing=True)
    mat = bpy.data.materials.new("tex_" + os.path.basename(image_path))
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = roughness
    me = obj.data
    me.materials.clear()
    me.materials.append(mat)
    uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name="UVMap")
    uv.name = "UVMap"
    bpy.context.view_layer.update()  # refresh matrix_world after location / rotation changes
    mw = obj.matrix_world
    rot = mw.to_3x3()
    for p in me.polygons:
        p.material_index = 0
        n = (rot @ p.normal).normalized()
        for li in p.loop_indices:
            co = mw @ me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = uv_fn(co, n)
    obj["rbx_texture"] = os.path.abspath(image_path)
    return obj


def group(obj, name):
    """Keep objects with the same group name together as one MeshPart (JOIN = False)."""
    obj["rbx_group"] = name
    return obj


def heightfield(size=(100, 100), res=(60, 60), height=None, loc=(0, 0, 0), name="terrain",
                base=0.0):
    """Grid mesh whose vertex heights come from height(x, y) -> z (studs).
    The grid is closed with side skirts and a bottom so it is a solid mesh.
    Paint it afterwards with paint_faces (e.g. snow on flat tops, rock on cliffs)."""
    sx, sy = size
    nx, ny = res
    verts, faces = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = (i / nx - 0.5) * sx
            y = (j / ny - 0.5) * sy
            verts.append((x, y, max(base, height(x, y)) if height else 0.0))
    idx = lambda i, j: j * (nx + 1) + i
    for j in range(ny):
        for i in range(nx):
            # alternate the diagonal for a nicer low-poly look
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            if (i + j) % 2:
                faces += [[a, b, c], [a, c, d]]
            else:
                faces += [[a, b, d], [b, c, d]]
    # skirt: ring of boundary vertices dropped to the base
    ring = ([idx(i, 0) for i in range(nx)] + [idx(nx, j) for j in range(ny)] +
            [idx(i, ny) for i in range(nx, 0, -1)] + [idx(0, j) for j in range(ny, 0, -1)])
    start = len(verts)
    for k in ring:
        x, y, _ = verts[k]
        verts.append((x, y, base))
    n = len(ring)
    for m in range(n):
        a, b = ring[m], ring[(m + 1) % n]
        faces.append([b, a, start + m, start + (m + 1) % n])
    faces.append([start + m for m in range(n)])
    obj = mesh_from_data(verts, faces, loc=loc, col="rock", name=name)
    recalc_normals(obj)
    return obj


# ------------------------------------------------------------ modifiers ----

def _select(obj):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj, location=False, rotation=True, scale=True):
    _select(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)
    return obj


def apply_modifiers(obj):
    _select(obj)
    for m in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    return obj


def add_bevel(obj, width=0.1, segments=2, limit_angle=30):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(limit_angle)
    return apply_modifiers(obj)


def subdivide(obj, levels=1, smooth=True):
    m = obj.modifiers.new("Subsurf", "SUBSURF")
    m.levels = levels
    m.render_levels = levels
    if not smooth:
        m.subdivision_type = "SIMPLE"
    return apply_modifiers(obj)


def mirror(obj, axis="X", merge=True):
    m = obj.modifiers.new("Mirror", "MIRROR")
    m.use_axis = [axis == "X", axis == "Y", axis == "Z"]
    m.use_mirror_merge = merge
    return apply_modifiers(obj)


def array(obj, count, offset=(1, 0, 0), relative=True, merge=False):
    m = obj.modifiers.new("Array", "ARRAY")
    m.count = count
    m.use_relative_offset = relative
    m.use_constant_offset = not relative
    if relative:
        m.relative_offset_displace = offset
    else:
        m.constant_offset_displace = offset
    m.use_merge_vertices = merge
    return apply_modifiers(obj)


def solidify(obj, thickness=0.1):
    m = obj.modifiers.new("Solidify", "SOLIDIFY")
    m.thickness = thickness
    return apply_modifiers(obj)


def boolean(obj, cutter, op="DIFFERENCE", keep_cutter=False):
    """op: DIFFERENCE (cut a hole), UNION (merge), INTERSECT."""
    m = obj.modifiers.new("Bool", "BOOLEAN")
    m.object = cutter
    m.operation = op
    m.solver = "EXACT"
    apply_modifiers(obj)
    if not keep_cutter:
        bpy.data.objects.remove(cutter, do_unlink=True)
    return obj


def decimate(obj, ratio=0.5):
    """Reduce triangle count (ratio 0-1)."""
    m = obj.modifiers.new("Decimate", "DECIMATE")
    m.ratio = ratio
    return apply_modifiers(obj)


def displace_noise(obj, strength=0.2, scale=1.0, seed=0):
    """Push vertices in/out with noise - makes rocks, terrain, crumbly shapes."""
    offs = Vector((seed * 13.1, seed * 7.7, seed * 3.3))
    for v in obj.data.vertices:
        d = noise.noise(v.co * scale + offs)
        v.co += v.normal * d * strength
    obj.data.update()
    return obj


def jitter(obj, amount=0.05, seed=0):
    """Randomly nudge vertices - hand-made low-poly look."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    for v in bm.verts:
        v.co += Vector((rnd.uniform(-amount, amount) for _ in range(3)))
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def taper(obj, top_scale=0.5, axis=2):
    """Scale vertices linearly along an axis (1 at bottom -> top_scale at top)."""
    zs = [v.co[axis] for v in obj.data.vertices]
    lo, hi = min(zs), max(zs)
    for v in obj.data.vertices:
        t = (v.co[axis] - lo) / (hi - lo or 1)
        s = 1 + (top_scale - 1) * t
        for a in range(3):
            if a != axis:
                v.co[a] *= s
    obj.data.update()
    return obj


def bend(obj, angle=30, axis="Z"):
    m = obj.modifiers.new("Bend", "SIMPLE_DEFORM")
    m.deform_method = "BEND"
    m.angle = math.radians(angle)
    m.deform_axis = axis
    return apply_modifiers(obj)


def twist(obj, angle=90, axis="Z"):
    m = obj.modifiers.new("Twist", "SIMPLE_DEFORM")
    m.deform_method = "TWIST"
    m.angle = math.radians(angle)
    m.deform_axis = axis
    return apply_modifiers(obj)


def merge_by_distance(obj, dist=1e-4):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def recalc_normals(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def shade_smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def shade_flat(obj):
    for p in obj.data.polygons:
        p.use_smooth = False
    return obj


def duplicate(obj, loc=None, rot=None, scale=None, name=None):
    new = obj.copy()
    new.data = obj.data.copy()
    bpy.context.collection.objects.link(new)
    if name:
        new.name = name
    if loc is not None:
        new.location = Vector(loc)
    if rot is not None:
        new.rotation_euler = Euler([math.radians(a) for a in rot])
    if scale is not None:
        new.scale = scale
    return new


def join(objs, name=None):
    """Join several objects into one mesh."""
    objs = [o for o in objs if o is not None]
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    if name:
        obj.name = name
    return obj


def mesh_objects():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


# ------------------------------------------------------------- palette ----

SWATCH = 16  # pixels per swatch


def _bake_palette(outdir):
    """Make palette.png, UV every face onto its color swatch, swap to one material."""
    keys = list(COLORS)  # global palette (custom colors get appended at the end)
    cols = 8
    rows = max(1, math.ceil(len(keys) / cols))
    w, h = cols * SWATCH, rows * SWATCH
    img = bpy.data.images.new("palette", w, h, alpha=False)
    px = [0.0] * (w * h * 4)
    uv_of = {}
    for i, k in enumerate(keys):
        cx, cy = i % cols, rows - 1 - i // cols
        r, g, b = (c / 255 for c in COLORS[k])
        for y in range(cy * SWATCH, (cy + 1) * SWATCH):
            for x in range(cx * SWATCH, (cx + 1) * SWATCH):
                o = (y * w + x) * 4
                px[o:o + 4] = [r, g, b, 1.0]
        uv_of[k] = ((cx + 0.5) / cols, (cy + 0.5) / rows)
    img.pixels = px
    path = os.path.join(outdir, "palette.png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()

    pal = bpy.data.materials.new("Palette")
    pal.use_nodes = True
    nt = pal.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8

    # tiny square inside the swatch so filtering never bleeds into neighbours
    du, dv = 0.2 / cols, 0.2 / rows
    for obj in mesh_objects():
        if obj.get("rbx_texture"):
            continue
        me = obj.data
        names = [m.name[4:] if m and m.name.startswith("col_") else "stone" for m in me.materials] or ["stone"]
        uv = me.uv_layers.new(name="UVMap") if not me.uv_layers else me.uv_layers[0]
        for p in me.polygons:
            k = names[p.material_index] if p.material_index < len(names) else names[0]
            u, v = uv_of.get(k, uv_of[keys[0]])
            n = len(p.loop_indices)
            for j, li in enumerate(p.loop_indices):
                a = 2 * math.pi * j / n
                uv.data[li].uv = (u + du * math.cos(a), v + dv * math.sin(a))
        me.materials.clear()
        me.materials.append(pal)
    return path


# ---------------------------------------------------------------- export ----

def _bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def _triangulate(obj):
    """Triangulate here (handles concave n-gons correctly) so importers never guess."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()


def _tri_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def export(name, outdir, join_all=True, render=True, fmt=("fbx", "obj", "glb"), meta=None):
    """Finish the model and write Roblox-ready files into outdir.

    join_all=True  -> one mesh (one MeshPart in Roblox)
    join_all=False -> keep objects separate (the importer makes a Model with one
                      MeshPart per object - use this for moving parts, doors, wheels)
    """
    os.makedirs(outdir, exist_ok=True)
    objs = mesh_objects()
    if not objs:
        raise RuntimeError("nothing to export - the scene has no meshes")
    for o in objs:
        apply_modifiers(o)
        apply_transform(o, location=False)

    # group objects into the meshes that will become MeshParts
    groups = {}
    for o in objs:
        if o.get("rbx_texture"):
            key = o.get("rbx_group") or os.path.splitext(os.path.basename(o["rbx_texture"]))[0]
        elif o.get("rbx_material"):
            key = o.get("rbx_group") or "%s_%s" % (o["rbx_material"], o["rbx_color"])
        elif join_all:
            key = "Main"
        else:
            key = o.get("rbx_group") or o.name
        groups.setdefault(key, []).append(o)
    specials = {}
    for key, members in groups.items():
        props = {k: members[0][k] for k in ("rbx_material", "rbx_color", "rbx_texture") if k in members[0]}
        o = join(members) if len(members) > 1 else members[0]
        o.name = name if (key == "Main" and len(groups) == 1) else f"{name}_{key}"
        for k, v in props.items():
            o[k] = v
        if props.get("rbx_material"):
            specials[o.name] = props
    objs = mesh_objects()

    # put the model on the ground, centered: pivot at bottom center
    lo, hi = _bounds(objs)
    shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for o in objs:
        o.location -= shift
    for o in objs:
        apply_transform(o, location=True)
        merge_by_distance(o)
        recalc_normals(o)
        _triangulate(o)
        o.data.name = o.name  # importers may use either the object or the mesh name

    palette = _bake_palette(outdir)
    lo, hi = _bounds(objs)
    size = hi - lo

    report = [f"Model: {name}",
              f"Size (studs): X {size.x:.2f}  Y(depth) {size.y:.2f}  Z(height) {size.z:.2f}",
              f"  -> in Roblox (Y is up): {size.x:.2f} x {size.z:.2f} x {size.y:.2f}",
              f"Colors in palette: {len(_palette)}"]
    total = 0
    for o in objs:
        t = _tri_count(o)
        total += t
        warn = "  <-- OVER ROBLOX LIMIT, decimate() it or split it" if t > ROBLOX_TRI_LIMIT else ""
        report.append(f"  mesh '{o.name}': {t} triangles{warn}")
    report.append(f"Total triangles: {total}")
    if specials:
        report.append("Special parts (applied by the Roblox setup script):")
        for pn, pr in specials.items():
            report.append(f"  {pn}: Material {pr['rbx_material']}, Color {pr['rbx_color']}")
    manifest = {
        "name": name,
        "size_studs": [round(size.x, 3), round(size.z, 3), round(size.y, 3)],
        "triangles": total,
        **(meta or {}),
        "parts": {o.name: {"triangles": _tri_count(o),
                           **({"material": o["rbx_material"],
                               "color": list(COLORS[o["rbx_color"]])} if o.get("rbx_material") else {}),
                           **({"texture": os.path.basename(o["rbx_texture"])} if o.get("rbx_texture") else
                              {"texture": "palette.png"} if not o.get("rbx_material") else {})}
                  for o in objs},
    }
    import shutil
    for o in objs:
        if o.get("rbx_texture"):
            dst = os.path.join(outdir, os.path.basename(o["rbx_texture"]))
            if os.path.abspath(o["rbx_texture"]) != os.path.abspath(dst):
                shutil.copy(o["rbx_texture"], dst)
    import json
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    for o in bpy.context.view_layer.objects:
        o.select_set(o in objs)

    files = [palette]
    if "fbx" in fmt:
        p = os.path.join(outdir, name + ".fbx")
        bpy.ops.export_scene.fbx(filepath=p, use_selection=True, apply_scale_options="FBX_SCALE_ALL",
                                 axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True,
                                 mesh_smooth_type="FACE", use_mesh_modifiers=True, bake_anim=False)
        files.append(p)
    if "obj" in fmt:
        p = os.path.join(outdir, name + ".obj")
        bpy.ops.wm.obj_export(filepath=p, export_selected_objects=True, forward_axis="NEGATIVE_Z",
                              up_axis="Y", path_mode="RELATIVE", export_materials=True)
        files.append(p)
    if "glb" in fmt:
        p = os.path.join(outdir, name + ".glb")
        bpy.ops.export_scene.gltf(filepath=p, export_format="GLB", use_selection=True, export_yup=True)
        files.append(p)

    blend = os.path.join(outdir, name + ".blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, check_existing=False, copy=True)
    files.append(blend)

    if render:
        files += render_previews(name, outdir, objs)

    report.append("Files:")
    report += ["  " + os.path.relpath(f, outdir) for f in files]
    text = "\n".join(report)
    with open(os.path.join(outdir, "info.txt"), "w") as f:
        f.write(text + "\n")
    print(text)
    return files


# --------------------------------------------------------------- render ----

def render_previews(name, outdir, objs=None, res=720, samples=32):
    """Render two 3/4 views (front and back) with Cycles on the CPU."""
    objs = objs or mesh_objects()
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.samples = samples
    try:
        scn.cycles.use_denoising = True
    except Exception:
        pass
    scn.render.resolution_x = scn.render.resolution_y = res
    scn.render.film_transparent = False
    scn.view_settings.view_transform = "Standard"

    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.68, 0.85, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    scn.world = world

    lo, hi = _bounds(objs)
    center = (lo + hi) / 2
    radius = max((hi - lo).length / 2, 0.5)

    # ground
    bpy.ops.mesh.primitive_plane_add(size=radius * 20, location=(center.x, center.y, lo.z + 0.002 * radius))
    ground = bpy.context.active_object
    gm = bpy.data.materials.new("ground")
    gm.use_nodes = True
    gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.62, 0.68, 0.76, 1)
    ground.data.materials.append(gm)

    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), math.radians(10), math.radians(35)))
    sun = bpy.context.active_object
    sun.data.energy = 3.5
    sun.data.angle = math.radians(8)

    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("cam", cam_data)
    scn.collection.objects.link(cam)
    scn.camera = cam
    dist = radius / math.tan(cam_data.angle / 2) * 0.98
    cam_data.clip_start = max(0.01, dist * 0.01)
    cam_data.clip_end = dist * 10

    out = []
    for label, yaw in (("front", -35), ("back", 145)):
        a = math.radians(yaw)
        el = math.radians(22)
        cam.location = center + Vector((math.sin(a) * math.cos(el), -math.cos(a) * math.cos(el),
                                        math.sin(el))) * dist
        direction = center - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        p = os.path.join(outdir, f"preview_{label}.jpg")
        scn.render.image_settings.file_format = "JPEG"
        scn.render.image_settings.quality = 90
        scn.render.filepath = p
        bpy.ops.render.render(write_still=True)
        out.append(p)

    for o in (ground, sun, cam):
        bpy.data.objects.remove(o, do_unlink=True)
    return out
