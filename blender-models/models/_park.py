"""Terrain-park features: kickers, rails, boxes, gates."""

import math


def kicker(rbx, length=12, height=3.5, width=8, lip_col="banner_blue", segments=14):
    # side profile in XZ: curved transition up to the lip, steep back down
    pts = [(0.0, 0.0)]
    for k in range(1, segments + 1):
        x = length * k / segments
        pts.append((x, height * (x / length) ** 2))
    back = height * 0.9
    pts += [(length + 0.6, height), (length + 0.6 + back, 0.0)]
    body = rbx.extrude_profile(pts, depth=width, col="snow", name="kicker")
    rbx.paint_faces(body, "snow_shadow", lambda c, n: abs(n.y) > 0.9)  # side walls
    # dyed lip line + start line (thin strips just above the surface)
    lip_w = 0.5
    rbx.box((lip_w, width + 0.02, 0.08), loc=(length + 0.3, 0, height + 0.02), col=lip_col)
    rbx.box((0.6, width + 0.02, 0.06), loc=(0.8, 0, 0.03 + height * (0.8 / length) ** 2), col=lip_col)
    # marker poles either side of the lip
    for y in (-width / 2 - 0.6, width / 2 + 0.6):
        rbx.cylinder(0.12, 5, loc=(length, y, 2.5), col="bark", sides=6)
        rbx.cylinder(0.14, 1.2, loc=(length, y, 4.6), col=lip_col, sides=6)


def rail(rbx, points, radius=0.28, post_col="safety_orange", base_col="dark_metal", posts=None):
    rbx.tube(points, radius=radius, col="metal", sides=12, name="rail")
    for (x, y, z) in (posts or [points[0], points[-1]]):
        rbx.cylinder(0.18, z, loc=(x, y, z / 2), col=post_col, sides=8)
        rbx.box((1.4, 1.4, 0.3), loc=(x, y, 0.15), col=base_col, bevel=0.08)
    # end caps
    rbx.sphere(radius * 1.05, loc=points[0], col="dark_metal", detail=2)
    rbx.sphere(radius * 1.05, loc=points[-1], col="dark_metal", detail=2)


def gate(rbx, name, text, bg, width=24, height=14, flag_col="red"):
    import _signs
    pillar_w = 1.6
    for x in (-width / 2, width / 2):
        rbx.box((pillar_w, pillar_w, height), loc=(x, 0, height / 2), col="dark_metal", bevel=0.12)
        rbx.box((pillar_w + 0.6, pillar_w + 0.6, 0.6), loc=(x, 0, 0.3), col="carbon", bevel=0.1)
        rbx.box((pillar_w + 0.3, pillar_w + 0.3, 0.3), loc=(x, 0, height + 0.15), col="carbon", bevel=0.08)
        # flag on top
        rbx.cylinder(0.1, 4, loc=(x, 0, height + 2.2), col="metal", sides=6)
        flag = rbx.extrude_profile([(0, 0), (2.4, 0.8), (0, 1.6)], depth=0.06, col=flag_col, name="flag")
        flag.location = (x, 0, height + 2.4)
        # lights on the pillars
        for z in (3, 6, 9):
            rbx.glow(rbx.box((0.3, pillar_w + 0.04, 0.3), loc=(x, 0, z)), "glow_cyan")
    bw, bh = width - pillar_w, height * 0.28
    z0 = height - bh - 0.6
    tex = _signs.banner(name + "_banner", text, bg=bg)
    panel = rbx.box((bw, 0.4, bh), loc=(0, 0, z0 + bh / 2), col="white")
    rbx.textured(panel, tex, _signs.planar_uv(-bw / 2, bw / 2, z0, z0 + bh))
