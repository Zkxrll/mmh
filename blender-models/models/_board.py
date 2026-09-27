"""
Shared snowboard builder + graphic designs.

A board is built along Y (nose at -Y, which becomes the model's front in Roblox)
and made of up to three MeshParts:
    <name>_Deck      textured deck (top graphic + base graphic + sidewall)
    <name>_Bindings  bindings (palette colors)
    <name>_Glow      optional Neon edge strip
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(HERE, "..", "textures")

# board dimensions (studs). A Roblox character is ~5 studs tall.
L = 4.8          # length
W = 1.26         # width at the tips
WAIST = 1.12     # width at the middle (sidecut)
T = 0.09         # thickness
LIFT = 0.34      # how far nose / tail curve up
CONTACT = 0.56   # fraction of half-length that stays flat
STATIONS = 72
COLS = 10

# texture layout (v): base 0..0.48, sidewall 0.49..0.51, top 0.52..1
TEX_W, TEX_H = 1024, 512
SS = 2  # supersampling for smooth edges

FONT_BOLD_OBLIQUE = "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ------------------------------------------------------------ geometry ----

def _half_width(t):
    a = abs(t)
    if a <= CONTACT:
        side = (W - WAIST) / 2
        return W / 2 - side * (1 - (a / CONTACT) ** 2)
    s = (a - CONTACT) / (1 - CONTACT)
    p = 2.6
    return max(0.035, W / 2 * (1 - s ** p) ** (1 / p))


def _lift(t):
    a = abs(t)
    c0 = CONTACT - 0.04
    if a <= c0:
        return 0.0
    return LIFT * ((a - c0) / (1 - c0)) ** 2


def _stations():
    # denser near the tips, where the curve is
    for k in range(STATIONS + 1):
        u = -1 + 2 * k / STATIONS
        t = math.sin(u * math.pi / 2)
        yield t


def deck_mesh(rbx, name="Deck"):
    verts, faces = [], []
    loops = []
    for t in _stations():
        y = t * L / 2
        hw = _half_width(t)
        z = _lift(t)
        ring = []
        # top surface (left -> right), slightly inset for a rounded edge
        for i in range(COLS + 1):
            x = (-1 + 2 * i / COLS) * hw * 0.97
            ring.append((x, y, z + T))
        ring.append((hw, y, z + T * 0.5))
        # base (right -> left)
        for i in range(COLS, -1, -1):
            x = (-1 + 2 * i / COLS) * hw * 0.97
            ring.append((x, y, z))
        ring.append((-hw, y, z + T * 0.5))
        loops.append(len(verts))
        verts += ring
    n = 2 * (COLS + 1) + 2
    for s in range(len(loops) - 1):
        a, b = loops[s], loops[s + 1]
        for i in range(n):
            j = (i + 1) % n
            faces.append([a + i, a + j, b + j, b + i])
    faces.append([loops[0] + i for i in range(n)])
    faces.append([loops[-1] + i for i in range(n - 1, -1, -1)])
    obj = rbx.mesh_from_data(verts, faces, col="white", name=name)
    rbx.recalc_normals(obj)
    return obj


def deck_uv(co, normal):
    u = min(1.0, max(0.0, (co.y + L / 2) / L))
    if normal.z > 0.45:       # top sheet
        v = 0.52 + 0.48 * (-co.x / W + 0.5)
    elif normal.z < -0.45:    # base (flipped so text reads correctly from below)
        v = 0.48 * (co.x / W + 0.5)
    else:                     # sidewall
        v = 0.5
    return (u, min(1.0, max(0.0, v)))


def glow_strip(rbx, col, name="Glow", height=0.035, thick=0.022):
    """Thin Neon band hugging the board's edge at mid-thickness."""
    left, right = [], []
    for t in _stations():
        y = t * L / 2
        hw = _half_width(t)
        z = _lift(t) + T * 0.5
        left.append((-hw, y, z))
        right.append((hw, y, z))
    path = left + right[::-1]
    n = len(path)
    verts, faces = [], []
    for k, (x, y, z) in enumerate(path):
        # outward direction in XY from neighbours
        px, py, _ = path[k - 1]
        nx_, ny_, _ = path[(k + 1) % n]
        dx, dy = nx_ - px, ny_ - py
        ln = math.hypot(dx, dy) or 1
        ox, oy = dy / ln, -dx / ln
        # make sure it points away from the board centre line
        if ox * x + oy * (y * 0.05) < 0:
            ox, oy = -ox, -oy
        for (o, h) in ((0.0, -height / 2), (thick, -height / 2), (thick, height / 2), (0.0, height / 2)):
            verts.append((x + ox * o, y + oy * o, z + h))
    for k in range(n):
        a, b = 4 * k, 4 * ((k + 1) % n)
        for i in range(4):
            j = (i + 1) % 4
            faces.append([a + i, a + j, b + j, b + i])
    obj = rbx.mesh_from_data(verts, faces, col=col, name=name)
    rbx.recalc_normals(obj)
    rbx.glow(obj, col)
    return obj


def _arc_shell(rbx, radius, height, thick, a0, a1, seg, col, top_scale=1.0, axis="Z", name="shell"):
    """Curved plate: arc (degrees a0..a1) around an axis, extruded by height."""
    verts, faces = [], []
    for k in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * k / seg)
        ca, sa = math.cos(a), math.sin(a)
        for (r, h) in ((radius, 0), (radius + thick, 0), (radius + thick, height), (radius, height)):
            s = 1 + (top_scale - 1) * (h / height)
            rr = r * s
            if axis == "Z":
                verts.append((rr * ca, rr * sa, h))
            else:  # arch over the foot: arc in the YZ plane, extruded along X
                verts.append((h - height / 2, rr * ca, rr * sa))
    for k in range(seg):
        a, b = 4 * k, 4 * (k + 1)
        for i in range(4):
            j = (i + 1) % 4
            faces.append([a + i, a + j, b + j, b + i])
    faces.append([0, 1, 2, 3][::-1])
    faces.append([4 * seg + i for i in range(4)])
    obj = rbx.mesh_from_data(verts, faces, col=col, name=name)
    rbx.recalc_normals(obj)
    return obj


def binding(rbx, y, angle, base_col, accent_col):
    z0 = T
    parts = [
        rbx.box((0.56, 0.62, 0.07), loc=(0, 0, z0 + 0.035), col=base_col, bevel=0.03, segments=2),
        rbx.cylinder(0.2, 0.03, loc=(0, 0, z0 + 0.085), col=accent_col, sides=16),  # disc
    ]
    # heel cup + highback, curved around the heel (heel side = -X)
    hb = _arc_shell(rbx, 0.27, 0.62, 0.05, 110, 250, 12, base_col, top_scale=0.92, name="highback")
    hb.location = (0.02, 0, z0 + 0.07)
    hb.rotation_euler = (0, math.radians(-12), 0)
    parts.append(hb)
    # ankle strap + toe strap (arches over the foot)
    ank = _arc_shell(rbx, 0.2, 0.16, 0.05, 15, 165, 10, accent_col, axis="X", name="ankle")
    ank.location = (-0.06, 0, z0 + 0.08)
    parts.append(ank)
    toe = _arc_shell(rbx, 0.14, 0.1, 0.04, 20, 160, 8, accent_col, axis="X", name="toe")
    toe.location = (0.24, 0, z0 + 0.08)
    parts.append(toe)
    for yy in (-0.19, 0.19):
        parts.append(rbx.box((0.1, 0.05, 0.08), loc=(-0.06, yy, z0 + 0.16), col="metal", bevel=0.015))
    b = rbx.join(parts, "binding")
    rbx.apply_transform(b, location=True)  # origin back to world zero before placing
    b.rotation_euler = (0, 0, math.radians(angle))
    b.location = (0, y, _lift(y / (L / 2)))
    rbx.group(b, "Bindings")
    return b


def build_board(rbx, name, design, base_col="carbon", accent_col="red", glow_col=None):
    tex = make_texture(name, design)
    deck = deck_mesh(rbx, "Deck")
    rbx.textured(deck, tex, deck_uv)
    rbx.group(deck, "Deck")
    # feet point across the board (X); duck stance +15 / -15 degrees
    binding(rbx, -0.88, 15, base_col, accent_col)
    binding(rbx, 0.88, -15, base_col, accent_col)
    if glow_col:
        g = glow_strip(rbx, glow_col)
        rbx.group(g, "Glow")


# ------------------------------------------------------------ textures ----

def _grad(draw, box, c0, c1, horizontal=True):
    x0, y0, x1, y1 = box
    n = (x1 - x0) if horizontal else (y1 - y0)
    for i in range(int(n)):
        t = i / max(1, n - 1)
        c = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
        if horizontal:
            draw.line([(x0 + i, y0), (x0 + i, y1)], fill=c)
        else:
            draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def _text(draw, xy, text, size, fill, stroke=None, font=FONT_BOLD_OBLIQUE, anchor="mm", sw=None):
    f = ImageFont.truetype(font, size)
    kw = {}
    if stroke:
        kw = {"stroke_width": sw or max(2, size // 14), "stroke_fill": stroke}
    draw.text(xy, text, font=f, fill=fill, anchor=anchor, **kw)


def _snowflake(draw, cx, cy, r, fill, width):
    for k in range(6):
        a = math.radians(60 * k)
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.line([(cx, cy), (ex, ey)], fill=fill, width=width)
        for f in (0.45, 0.72):
            bx, by = cx + r * f * math.cos(a), cy + r * f * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(45)
                draw.line([(bx, by), (bx + r * 0.25 * math.cos(b), by + r * 0.25 * math.sin(b))],
                          fill=fill, width=width)
    draw.ellipse([cx - width * 1.5, cy - width * 1.5, cx + width * 1.5, cy + width * 1.5], fill=fill)


def _flame(draw, x0, y0, length, w0, wig, phase, color, direction=1):
    pts_l, pts_r = [], []
    steps = 40
    for s in range(steps + 1):
        t = s / steps
        cx = x0 + direction * t * length
        cy = y0 + wig * math.sin(t * math.pi * 1.6 + phase) * t
        w = w0 * (1 - t) ** 0.9
        # normal of the centerline
        dt = 1 / steps
        cy2 = y0 + wig * math.sin((t + dt) * math.pi * 1.6 + phase) * (t + dt)
        dx, dy = direction * dt * length, cy2 - cy
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        pts_l.append((cx + nx * w, cy + ny * w))
        pts_r.append((cx - nx * w, cy - ny * w))
    draw.polygon(pts_l + pts_r[::-1], fill=color)


def _hexgrid(draw, w, h, r, color, width):
    dx = r * 1.5
    dy = r * math.sqrt(3)
    col = 0
    x = 0.0
    while x < w + r:
        y = (dy / 2) if col % 2 else 0.0
        while y < h + r:
            pts = [(x + r * math.cos(math.radians(60 * k)), y + r * math.sin(math.radians(60 * k)))
                   for k in range(7)]
            draw.line(pts, fill=color, width=width)
            y += dy
        x += dx
        col += 1


def _design_frostbite(top, base, rnd):
    w, h = top.size
    d = ImageDraw.Draw(top)
    _grad(d, (0, 0, w, h), (12, 24, 70), (60, 150, 215))
    # ice shards from both edges
    for _ in range(26):
        x = rnd.uniform(0, w)
        edge = rnd.choice((0, h))
        hgt = rnd.uniform(0.25, 0.7) * h
        sgn = 1 if edge == 0 else -1
        c = rnd.choice([(200, 235, 255), (150, 210, 245), (235, 248, 255)])
        d.polygon([(x - rnd.uniform(20, 60), edge), (x + rnd.uniform(20, 60), edge),
                   (x + rnd.uniform(-40, 40), edge + sgn * hgt)], fill=c)
    _snowflake(d, w * 0.18, h / 2, h * 0.3, (255, 255, 255), 10)
    _text(d, (w * 0.58, h / 2), "FROSTBITE", int(h * 0.36), (255, 255, 255), stroke=(20, 50, 110))
    b = ImageDraw.Draw(base)
    _grad(b, (0, 0, w, h), (170, 220, 250), (90, 160, 215))
    for k in range(-4, 30):
        x = k * 90
        b.polygon([(x, 0), (x + 40, 0), (x + 40 + h * 0.6, h), (x + h * 0.6, h)], fill=(235, 246, 255))
    _text(b, (w / 2, h / 2), "FROSTBITE", int(h * 0.3), (20, 50, 110))
    return (60, 150, 215)


def _design_inferno(top, base, rnd):
    w, h = top.size
    d = ImageDraw.Draw(top)
    _grad(d, (0, 0, w, h), (40, 4, 4), (10, 10, 12))
    tongues = [(h * 0.2, 0.0), (h * 0.5, 1.3), (h * 0.8, 2.4), (h * 0.35, 3.1), (h * 0.65, 4.0)]
    for layer, (col, scale) in enumerate([((200, 30, 10), 1.0), ((255, 120, 20), 0.68), ((255, 220, 60), 0.36)]):
        for y0, ph in tongues:
            _flame(d, w * 0.02, y0, w * 0.62 * (0.8 + 0.2 * math.sin(ph)), h * 0.16 * scale, h * 0.12, ph, col)
    _text(d, (w * 0.8, h / 2), "INFERNO", int(h * 0.34), (255, 210, 60), stroke=(120, 10, 0))
    b = ImageDraw.Draw(base)
    _grad(b, (0, 0, w, h), (200, 30, 10), (255, 130, 20))
    for k in range(0, 16):
        x = k * 130
        b.polygon([(x, 0), (x + 60, 0), (x + 160, h / 2), (x + 60, h), (x, h), (x + 100, h / 2)], fill=(30, 10, 8))
    _text(b, (w / 2, h / 2), "INFERNO", int(h * 0.3), (255, 220, 70), stroke=(40, 5, 0))
    return (30, 10, 8)


def _design_viper(top, base, rnd):
    w, h = top.size
    d = ImageDraw.Draw(top)
    d.rectangle([0, 0, w, h], fill=(22, 24, 28))
    _hexgrid(d, w, h, 34, (40, 70, 48), 4)
    # neon zigzag down the middle
    pts = []
    for k in range(0, 23):
        pts.append((k * w / 22, h * (0.3 if k % 2 else 0.7)))
    d.line(pts, fill=(80, 255, 120), width=26, joint="curve")
    d.line(pts, fill=(200, 255, 210), width=8, joint="curve")
    _text(d, (w * 0.5, h / 2), "VIPER", int(h * 0.42), (22, 24, 28), stroke=(80, 255, 120), sw=10)
    b = ImageDraw.Draw(base)
    b.rectangle([0, 0, w, h], fill=(70, 230, 110))
    _hexgrid(b, w, h, 40, (40, 160, 70), 6)
    _text(b, (w / 2, h / 2), "VIPER", int(h * 0.4), (22, 24, 28))
    return (22, 24, 28)


def _design_cosmic(top, base, rnd):
    w, h = top.size
    d = ImageDraw.Draw(top)
    _grad(d, (0, 0, w, h), (20, 16, 60), (170, 30, 170))
    # nebula blobs
    neb = Image.new("RGBA", top.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(neb)
    for _ in range(14):
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(h * 0.2, h * 0.5)
        c = rnd.choice([(255, 60, 200, 70), (80, 120, 255, 70), (140, 60, 255, 70)])
        nd.ellipse([x - r, y - r, x + r, y + r], fill=c)
    neb = neb.filter(ImageFilter.GaussianBlur(h * 0.12))
    top.paste(neb, (0, 0), neb)
    d = ImageDraw.Draw(top)
    for _ in range(420):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([1.5, 2, 2, 3, 4, 6])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
    # ringed planet
    px, py, pr = w * 0.2, h * 0.5, h * 0.26
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 150, 90))
    d.ellipse([px - pr * 0.8, py - pr, px + pr * 0.6, py + pr * 0.3], fill=(255, 190, 120))
    d.ellipse([px - pr * 1.9, py - pr * 0.45, px + pr * 1.9, py + pr * 0.45], outline=(255, 230, 180), width=12)
    _text(d, (w * 0.64, h / 2), "COSMIC", int(h * 0.38), (255, 255, 255), stroke=(90, 20, 140))
    b = ImageDraw.Draw(base)
    _grad(b, (0, 0, w, h), (10, 10, 40), (60, 20, 110))
    for _ in range(300):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([1.5, 2, 3])
        b.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
    _text(b, (w / 2, h / 2), "COSMIC", int(h * 0.32), (255, 80, 210))
    return (40, 20, 90)


def _design_sunset(top, base, rnd):
    w, h = top.size
    d = ImageDraw.Draw(top)
    _grad(d, (0, 0, w, h), (255, 70, 150), (255, 170, 60))
    # synthwave sun with cut-out bands
    cx, cy, r = w * 0.3, h * 0.5, h * 0.42
    sun = Image.new("RGBA", top.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    for i in range(int(2 * r)):
        t = i / (2 * r)
        c = (255, int(230 - 150 * t), int(80 + 60 * t), 255)
        half = math.sqrt(max(0.0, r * r - (i - r) ** 2))
        sd.line([(cx - r + i, cy - half), (cx - r + i, cy + half)], fill=c)
    for k in range(6):
        bx = cx + r * (0.05 + k * 0.17)
        sd.rectangle([bx, 0, bx + 10 + 5 * k, h], fill=(0, 0, 0, 0))
    top.paste(sun, (0, 0), sun)
    d = ImageDraw.Draw(top)
    # perspective grid toward the tail
    gx = w * 0.62
    for k in range(-6, 7):
        d.line([(gx, h / 2), (w, h / 2 + k * h * 0.2)], fill=(110, 30, 160), width=5)
    for k in range(1, 9):
        x = gx + (w - gx) * (k / 8) ** 1.6
        d.line([(x, 0), (x, h)], fill=(110, 30, 160), width=5)
    _text(d, (w * 0.7, h * 0.5), "SUNSET", int(h * 0.34), (255, 255, 255), stroke=(110, 30, 160))
    b = ImageDraw.Draw(base)
    _grad(b, (0, 0, w, h), (80, 20, 130), (30, 10, 60))
    for k in range(0, 30):
        b.line([(k * 70, 0), (k * 70, h)], fill=(255, 70, 150), width=4)
    for k in range(0, 6):
        b.line([(0, k * h / 5), (w, k * h / 5)], fill=(255, 70, 150), width=4)
    _text(b, (w / 2, h / 2), "SUNSET RIDER", int(h * 0.26), (255, 190, 70), stroke=(40, 10, 70))
    return (80, 20, 130)


def _design_rookie(top, base, rnd):
    w, h = top.size
    d = ImageDraw.Draw(top)
    d.rectangle([0, 0, w, h], fill=(196, 150, 100))
    for _ in range(90):  # wood grain
        y = rnd.uniform(0, h)
        amp, ph = rnd.uniform(4, 14), rnd.uniform(0, 6)
        c = rnd.choice([(170, 120, 75), (150, 105, 65), (210, 168, 118)])
        pts = [(x, y + amp * math.sin(x / rnd.uniform(90, 200) + ph)) for x in range(0, w + 20, 20)]
        d.line(pts, fill=c, width=rnd.choice([2, 3, 5]))
    d.rectangle([0, h * 0.42, w, h * 0.58], fill=(245, 245, 245))
    d.rectangle([0, h * 0.46, w, h * 0.54], fill=(210, 40, 30))
    _text(d, (w * 0.5, h / 2), "ROOKIE", int(h * 0.3), (255, 255, 255), stroke=(40, 30, 20))
    b = ImageDraw.Draw(base)
    b.rectangle([0, 0, w, h], fill=(28, 28, 32))
    b.rectangle([0, h * 0.4, w, h * 0.6], fill=(210, 40, 30))
    _text(b, (w / 2, h / 2), "ROOKIE", int(h * 0.3), (255, 255, 255))
    return (40, 30, 20)


DESIGNS = {
    "frostbite": _design_frostbite,
    "inferno": _design_inferno,
    "viper": _design_viper,
    "cosmic": _design_cosmic,
    "sunset": _design_sunset,
    "rookie": _design_rookie,
}


def make_texture(name, design):
    os.makedirs(TEX_DIR, exist_ok=True)
    rnd = random.Random(name)
    W_, H_ = TEX_W * SS, TEX_H * SS
    region_h = int(H_ * 0.48)
    top = Image.new("RGB", (W_, region_h))
    base = Image.new("RGB", (W_, region_h))
    side = DESIGNS[design](top, base, rnd)
    img = Image.new("RGB", (W_, H_), side)
    img.paste(top, (0, 0))                       # v 0.52..1 (image top)
    img.paste(base, (0, H_ - region_h))          # v 0..0.48 (image bottom)
    img = img.resize((TEX_W, TEX_H), Image.LANCZOS)
    path = os.path.join(TEX_DIR, f"{name}_deck.png")
    img.save(path)
    return path
