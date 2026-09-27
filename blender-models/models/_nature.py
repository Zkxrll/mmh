"""Snowy pines and rocks."""

import math
import random

from mathutils import Vector


def pine(rbx, height=16, tiers=4, radius=4.2, seed=1, snow=0.45, lean=0.0):
    """Stacked, jittered cone tiers with snow on the upper part of each tier."""
    rnd = random.Random(seed)
    trunk_h = height * 0.22
    trunk = rbx.cylinder(radius=radius * 0.13, depth=trunk_h + 1, loc=(0, 0, (trunk_h + 1) / 2 - 0.5),
                         col="bark", sides=7, radius_top=radius * 0.09)
    rbx.jitter(trunk, 0.05, seed=seed)
    parts = [trunk]
    z = trunk_h * 0.75
    tier_h = (height - z) / tiers * 1.5
    for k in range(tiers):
        t = k / max(1, tiers - 1)
        r = radius * (1 - 0.62 * t) * rnd.uniform(0.92, 1.05)
        h = tier_h * (1 - 0.25 * t)
        # profile (radius, height): droopy rim, concave cone to a point
        prof = [(0.0, h * 0.12), (r, 0.0), (r * 0.78, h * 0.18), (r * 0.52, h * 0.42),
                (r * 0.28, h * 0.68), (0.0, h)]
        tier = rbx.lathe(prof, loc=(0, 0, z), col="pine", sides=rnd.choice((7, 8, 9)))
        tier.rotation_euler = (0, 0, rnd.uniform(0, math.pi))
        rbx.jitter(tier, r * 0.06, seed=seed * 10 + k)
        rbx.apply_transform(tier, location=True)
        top_z = z + h
        snow_z = z + h * (1 - snow) + rnd.uniform(-0.2, 0.2) * h * 0.2
        rbx.paint_faces(tier, "dark_pine", lambda c, n: n.z < -0.2)
        rbx.paint_faces(tier, "snow", lambda c, n, s=snow_z: n.z > 0.15 and c.z > s)
        rbx.paint_faces(tier, "snow", lambda c, n, zz=z, hh=h: n.z > 0.5 and c.z < zz + hh * 0.2)  # rim
        parts.append(tier)
        z += h * 0.55
    tree = rbx.join(parts)
    if lean:
        rbx.bend(tree, lean, "X")
    return tree


def rock(rbx, size=(6, 5, 3.5), seed=1, snow=True, detail=3, loc=(0, 0, 0)):
    r = rbx.sphere(radius=1, detail=detail, scale=size, loc=loc, col="rock")
    rbx.apply_transform(r, location=True)
    rbx.displace_noise(r, strength=min(size) * 0.28, scale=0.45, seed=seed)
    rbx.jitter(r, min(size) * 0.04, seed=seed)
    rbx.paint_faces(r, "dark_rock", lambda c, n: n.z < -0.1)
    rbx.paint_faces(r, "light_rock", lambda c, n: 0.1 < n.z < 0.45)
    if snow:
        rbx.paint_faces(r, "snow", lambda c, n: n.z > 0.62)
    # sink the bottom a little so it sits into the ground
    r.location.z = -size[2] * 0.25
    return r
