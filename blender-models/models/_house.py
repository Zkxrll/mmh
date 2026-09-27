"""
Alpine house builder: log ground floor, half-timbered upper floor, steep snowy
gable roof with icicles, balcony, porch, chimney, framed glowing windows.

Parts (JOIN = False):
    <name>_Structure  everything solid (palette texture)
    <name>_Windows    glowing window panes (Neon, warm light)
    <name>_Icicles    icicles along the eaves (Glass)
"""

import math
import random


def _place(rbx, objs, loc, yaw):
    """Move pieces built around the origin (facing -Y) to loc, turned by yaw degrees."""
    for o in objs:
        rbx.apply_transform(o, location=True)
        o.rotation_euler = (0, 0, math.radians(yaw))
        o.location = loc
        rbx.apply_transform(o, location=True)


def window(rbx, loc, yaw, w=2.6, h=3.2, shutters="red", snow=True):
    t = 0.3
    parts = [
        rbx.box((w + 0.5, 0.4, t), loc=(0, -0.1, h / 2 + t / 2), col="dark_timber", bevel=0.04),  # head
        rbx.box((w + 0.8, 0.6, t), loc=(0, -0.2, -h / 2 - t / 2), col="dark_timber", bevel=0.04),  # sill
        rbx.box((t, 0.4, h), loc=(-w / 2 - t / 2, -0.1, 0), col="dark_timber"),
        rbx.box((t, 0.4, h), loc=(w / 2 + t / 2, -0.1, 0), col="dark_timber"),
        rbx.box((0.12, 0.2, h), loc=(0, -0.2, 0), col="dark_timber"),                  # mullions
        rbx.box((w, 0.2, 0.12), loc=(0, -0.2, 0), col="dark_timber"),
    ]
    if shutters:
        for s in (-1, 1):
            sh = rbx.box((w * 0.5, 0.14, h + 0.2), loc=(s * (w * 0.75 + t + 0.1), -0.05, 0), col=shutters,
                         bevel=0.03)
            parts.append(sh)
            for z in (-h * 0.3, h * 0.3):  # cross boards on the shutters
                parts.append(rbx.box((w * 0.46, 0.18, 0.18), loc=(s * (w * 0.75 + t + 0.1), -0.1, z),
                                     col="dark_timber"))
    if snow:
        parts.append(rbx.box((w + 0.7, 0.55, 0.14), loc=(0, -0.2, -h / 2 + 0.07), col="snow", bevel=0.05))
        parts.append(rbx.box((w + 0.4, 0.35, 0.12), loc=(0, -0.1, h / 2 + t + 0.06), col="snow", bevel=0.04))
    pane = rbx.box((w, 0.1, h), loc=(0, 0.02, 0))
    rbx.glow(pane, "window_glow")
    rbx.group(pane, "Windows")
    frame = rbx.join(parts)
    rbx.group(frame, "Structure")
    _place(rbx, [frame, pane], loc, yaw)


def door(rbx, loc, yaw, w=3.4, h=6.4):
    parts = [rbx.box((w, 0.3, h), loc=(0, 0, h / 2), col="timber", bevel=0.04)]
    for k in range(5):  # planks
        parts.append(rbx.box((0.08, 0.36, h - 0.4), loc=(-w / 2 + (k + 1) * w / 6, -0.02, h / 2),
                             col="dark_timber"))
    parts += [
        rbx.box((w + 0.8, 0.5, 0.45), loc=(0, -0.1, h + 0.2), col="dark_timber", bevel=0.04),
        rbx.box((0.4, 0.5, h), loc=(-w / 2 - 0.2, -0.1, h / 2), col="dark_timber"),
        rbx.box((0.4, 0.5, h), loc=(w / 2 + 0.2, -0.1, h / 2), col="dark_timber"),
        rbx.sphere(0.14, loc=(w * 0.32, -0.25, h * 0.47), col="gold", detail=1),
    ]
    pane = rbx.box((1.0, 0.1, 1.2), loc=(0, -0.12, h * 0.75))
    rbx.glow(pane, "window_glow")
    rbx.group(pane, "Windows")
    frame = rbx.join(parts)
    rbx.group(frame, "Structure")
    _place(rbx, [frame, pane], loc, yaw)


def lantern(rbx, loc, yaw):
    parts = [rbx.box((0.1, 0.5, 0.1), loc=(0, -0.25, 0.6), col="carbon"),
             rbx.box((0.5, 0.5, 0.1), loc=(0, -0.55, -0.05), col="carbon"),
             rbx.cone(0.45, 0.35, loc=(0, -0.55, 0.62), col="carbon", sides=4, rot=(0, 0, 45))]
    glass = rbx.box((0.4, 0.4, 0.6), loc=(0, -0.55, 0.27))
    rbx.glow(glass, "window_glow")
    rbx.group(glass, "Windows")
    f = rbx.join(parts)
    rbx.group(f, "Structure")
    _place(rbx, [f, glass], loc, yaw)


def log_walls(rbx, wx, dy, z0, height, r=0.5):
    """Interlocking log walls; logs stick out past the corners."""
    parts = [rbx.box((wx - 0.5, dy - 0.5, height), loc=(0, 0, z0 + height / 2), col="timber")]
    n = int(height / (2 * r))
    for k in range(n):
        zf = z0 + r + 2 * r * k
        zs = zf + r
        for y in (-dy / 2, dy / 2):
            parts.append(rbx.cylinder(r, wx + 2.2, loc=(0, y, zf), rot=(0, 90, 0), col="timber", sides=7))
        if zs + r <= z0 + height + 0.01:
            for x in (-wx / 2, wx / 2):
                parts.append(rbx.cylinder(r, dy + 2.2, loc=(x, 0, zs), rot=(90, 0, 0), col="timber", sides=7))
    walls = rbx.join(parts)
    # darker log ends
    rbx.paint_faces(walls, "dark_timber", lambda c, nn: (abs(nn.x) > 0.9 and abs(c.x) > wx / 2 + 0.9) or
                    (abs(nn.y) > 0.9 and abs(c.y) > dy / 2 + 0.9))
    rbx.group(walls, "Structure")
    return walls


def timber_frame_walls(rbx, wx, dy, z0, height):
    parts = [rbx.box((wx, dy, height), loc=(0, 0, z0 + height / 2), col="plaster")]
    b = 0.45
    for z in (z0 + b / 2, z0 + height - b / 2, z0 + height * 0.5):
        parts.append(rbx.box((wx + 0.3, dy + 0.3, b), loc=(0, 0, z), col="dark_timber"))
    # vertical posts on every face
    for x in [(-wx / 2) + i * wx / 6 for i in range(7)]:
        for y in (-dy / 2 - 0.1, dy / 2 + 0.1):
            parts.append(rbx.box((b, 0.3, height), loc=(x, y, z0 + height / 2), col="dark_timber"))
    for y in [(-dy / 2) + i * dy / 6 for i in range(7)]:
        for x in (-wx / 2 - 0.1, wx / 2 + 0.1):
            parts.append(rbx.box((0.3, b, height), loc=(x, y, z0 + height / 2), col="dark_timber"))
    # diagonal braces at the corners of the front and back
    for sx in (-1, 1):
        for y in (-dy / 2 - 0.12, dy / 2 + 0.12):
            x = sx * (wx / 2 - wx / 12)
            parts.append(rbx.box((b * 0.8, 0.3, height * 0.62), loc=(x, y, z0 + height * 0.27),
                                 rot=(0, sx * 38, 0), col="dark_timber"))
    walls = rbx.join(parts)
    rbx.group(walls, "Structure")
    return walls


def gable_roof(rbx, wx, dy, z_eave, pitch=38, overhang=2.4, thick=0.8, seed=1, icicles=True):
    """Gable roof with the ridge along Y. Returns ridge height."""
    rnd = random.Random(seed)
    p = math.radians(pitch)
    half = wx / 2
    rise = half * math.tan(p)
    z_ridge = z_eave + rise
    # attic / gable prism (plaster) with trim
    gable = rbx.extrude_profile([(-half, 0), (half, 0), (0, rise)], depth=dy, col="plaster", name="gable")
    # extrude_profile: triangle in XZ, extruded along Y -> ridge along Y, gable ends face +/-Y
    gable.location = (0, 0, z_eave)
    rbx.apply_transform(gable, location=True)
    rbx.group(gable, "Structure")
    parts = []
    run = half + overhang
    slope_len = run / math.cos(p)
    L = dy + 2 * overhang
    for s in (-1, 1):
        cx = s * run / 2
        cz = z_ridge - (run / 2) * math.tan(p)
        slab = rbx.box((slope_len, L, thick), loc=(cx, 0, cz + thick / 2 / math.cos(p)), col="roof",
                       rot=(0, s * pitch, 0))
        snow = rbx.box((slope_len - 0.6, L - 0.4, 0.7), col="snow", bevel=0.25, segments=2,
                       loc=(cx - s * 0.2, 0, cz + (thick + 0.35) / math.cos(p)), rot=(0, s * pitch, 0))
        parts += [slab, snow]
        # bargeboards (front + back edges)
        for y in (-L / 2 - 0.05, L / 2 + 0.05):
            parts.append(rbx.box((slope_len + 0.3, 0.35, 1.0), loc=(cx, y, cz), rot=(0, s * pitch, 0),
                                 col="dark_timber"))
        if icicles:
            ez = z_eave - overhang * math.tan(p)
            x = s * run
            y = -L / 2 + 0.6
            while y < L / 2 - 0.6:
                ln = rnd.uniform(0.5, 2.0)
                ic = rbx.cone(0.18, ln, loc=(x - s * 0.1, y, ez - ln / 2 + 0.05), rot=(180, 0, 0), sides=5)
                rbx.glow(ic, "ice", material="Glass")
                rbx.group(ic, "Icicles")
                y += rnd.uniform(0.7, 1.6)
    parts.append(rbx.box((0.9, L + 0.2, 0.9), loc=(0, 0, z_ridge + thick * 0.9), rot=(0, 45, 0), col="snow"))
    roof = rbx.join(parts)
    rbx.group(roof, "Structure")
    # gable trim: king post + collar beam on both gable ends
    for y in (-dy / 2 - 0.12, dy / 2 + 0.12):
        rbx.group(rbx.box((0.45, 0.3, rise), loc=(0, y, z_eave + rise / 2), col="dark_timber"), "Structure")
        rbx.group(rbx.box((wx * 0.55, 0.3, 0.45), loc=(0, y, z_eave + rise * 0.42), col="dark_timber"),
                  "Structure")
    return z_ridge


def chimney(rbx, x, y, z0, top, w=3.0):
    parts = [rbx.box((w, w, top - z0), loc=(x, y, (z0 + top) / 2), col="light_stone")]
    rnd = random.Random(int(x * 10 + y))
    z = z0 + 0.6
    while z < top - 0.5:  # stone bands
        parts.append(rbx.box((w + 0.12, w + 0.12, 0.35), loc=(x, y, z),
                             col=rnd.choice(["rock", "light_rock", "stone"])))
        z += rnd.uniform(0.9, 1.4)
    parts.append(rbx.box((w + 0.5, w + 0.5, 0.4), loc=(x, y, top + 0.2), col="dark_rock", bevel=0.08))
    parts.append(rbx.box((w + 0.3, w + 0.3, 0.35), loc=(x, y, top + 0.55), col="snow", bevel=0.12))
    parts.append(rbx.box((w * 0.5, w * 0.5, 0.4), loc=(x, y, top + 0.75), col="carbon"))
    c = rbx.join(parts)
    rbx.group(c, "Structure")
    return c


def stone_base(rbx, wx, dy, h, seed=3):
    rnd = random.Random(seed)
    parts = [rbx.box((wx, dy, h), loc=(0, 0, h / 2), col="rock", bevel=0.15)]
    for (axis, fixed, span) in (("y", -dy / 2, wx), ("y", dy / 2, wx), ("x", -wx / 2, dy), ("x", wx / 2, dy)):
        for row in range(int(h / 0.9)):
            t = -span / 2 + rnd.uniform(0, 0.8)
            while t < span / 2 - 0.8:
                sw = rnd.uniform(1.0, 2.2)
                sh = rnd.uniform(0.55, 0.8)
                z = 0.45 + row * 0.9
                c = rnd.choice(["light_rock", "stone", "rock", "light_stone"])
                if axis == "y":
                    s = rbx.box((sw, 0.3, sh), loc=(t + sw / 2, fixed, z), col=c, bevel=0.1)
                else:
                    s = rbx.box((0.3, sw, sh), loc=(fixed, t + sw / 2, z), col=c, bevel=0.1)
                rbx.jitter(s, 0.05, seed=rnd.randint(0, 999))
                parts.append(s)
                t += sw + 0.12
    base = rbx.join(parts)
    rbx.group(base, "Structure")
    return base


def balcony(rbx, width, depth, y_front, z, rail_col="dark_timber"):
    y = y_front - depth / 2
    parts = [rbx.box((width, depth, 0.5), loc=(0, y, z), col="timber", bevel=0.05),
             rbx.box((width - 0.2, depth - 0.2, 0.2), loc=(0, y, z + 0.35), col="snow", bevel=0.08)]
    yf = y_front - depth + 0.2
    parts.append(rbx.box((width, 0.3, 0.3), loc=(0, yf, z + 3.0), col=rail_col, bevel=0.04))   # top rail
    parts.append(rbx.box((width, 0.35, 0.18), loc=(0, yf, z + 3.2), col="snow"))
    parts.append(rbx.box((width, 0.25, 0.25), loc=(0, yf, z + 0.6), col=rail_col))
    for sx in (-1, 1):
        parts.append(rbx.box((0.3, depth, 0.3), loc=(sx * (width / 2 - 0.15), y, z + 3.0), col=rail_col))
    x = -width / 2 + 0.4
    while x < width / 2 - 0.3:   # carved balusters
        parts.append(rbx.box((0.35, 0.12, 2.4), loc=(x, yf, z + 1.8), col="timber"))
        x += 0.75
    for sx in (-1, 1):
        for xx in (sx * (width / 2 - 1), sx * width / 6):   # brackets
            parts.append(rbx.box((0.4, 0.4, depth * 1.35), loc=(xx, y + depth * 0.1, z - depth * 0.45),
                                 rot=(-50, 0, 0), col="dark_timber"))
    b = rbx.join(parts)
    rbx.group(b, "Structure")


def steps(rbx, parts, width, y_edge, z_floor, n=3, x=0.0):
    """Stone steps going out (-Y) from y_edge, down from z_floor to the ground."""
    for k in range(n):
        hk = z_floor * (n - k) / (n + 1)
        parts.append(rbx.box((width, 1.2, hk), loc=(x, y_edge - 0.6 - k * 1.2, hk / 2), col="light_rock",
                             bevel=0.08))


def porch(rbx, width, depth, y_front, z_floor, height, x=0.0):
    y = y_front - depth / 2
    parts = []
    for sx in (-1, 1):
        parts.append(rbx.box((0.6, 0.6, height), loc=(sx * (width / 2 - 0.4), y_front - depth + 0.4,
                                                        z_floor + height / 2), col="dark_timber", bevel=0.05))
    p = math.radians(35)
    run = width / 2 + 0.6
    zt = z_floor + height
    for s in (-1, 1):
        parts.append(rbx.box((run / math.cos(p), depth + 0.8, 0.4), loc=(s * run / 2, y, zt + run / 2 * math.tan(p)),
                             rot=(0, s * 35, 0), col="roof"))
        parts.append(rbx.box((run / math.cos(p) - 0.3, depth + 0.4, 0.4),
                             loc=(s * run / 2, y, zt + run / 2 * math.tan(p) + 0.38), rot=(0, s * 35, 0),
                             col="snow", bevel=0.12))
    tri = rbx.extrude_profile([(-width / 2, 0), (width / 2, 0), (0, (width / 2) * math.tan(p))],
                              depth=0.3, col="dark_timber", name="porchgable")
    tri.location = (0, y_front - depth + 0.2, zt)
    parts.append(tri)
    parts.append(rbx.box((width, 0.4, 0.5), loc=(0, y_front - depth + 0.4, zt), col="dark_timber"))
    parts.append(rbx.box((width, depth, z_floor), loc=(0, y, z_floor / 2), col="timber", bevel=0.05))  # deck
    steps(rbx, parts, width - 1.4, y_front - depth, z_floor)
    pr = rbx.join(parts)
    rbx.apply_transform(pr, location=True)
    pr.location.x += x
    rbx.group(pr, "Structure")
