"""Snowy low-poly mountains from ridged noise. Faces are colored by height and slope:
snow on flatter / higher faces, bands of rock on steep cliffs."""

import math

from mathutils import Vector, noise


def mountain(rbx, name, size=(600, 600), height=320, res=(90, 90), seed=1, peaks=None,
             snow_line=0.35, ridge_scale=1.0):
    sx, sy = size
    peaks = peaks or [(0.0, 0.0, 1.0, 0.45)]  # (x, y) in -0.5..0.5, height weight, radius
    off = Vector((seed * 17.3, seed * 5.1, seed * 2.7))

    def shape(x, y):
        u, v = x / sx, y / sy
        h = 0.0
        for px, py, w, r in peaks:
            d = math.hypot(u - px, v - py) / r
            h = max(h, w * max(0.0, 1 - d) ** 1.35)
        p = Vector((u * 4 * ridge_scale, v * 4 * ridge_scale, 0)) + off
        ridge = noise.ridged_multi_fractal(p, 0.9, 2.1, 5, 1.0, 2.0, noise_basis="PERLIN_ORIGINAL")
        detail = noise.noise(p * 3.0)
        return h, ridge, detail

    # sample once to normalise the ridge noise
    samples = []
    for j in range(0, res[1] + 1, 3):
        for i in range(0, res[0] + 1, 3):
            samples.append(shape((i / res[0] - 0.5) * sx, (j / res[1] - 0.5) * sy)[1])
    lo, hi = min(samples), max(samples)

    def height_fn(x, y):
        h, ridge, detail = shape(x, y)
        r = (ridge - lo) / (hi - lo or 1)
        z = h * (0.5 + 0.5 * r) + 0.03 * detail * h
        # soft edge so the base meets the ground
        edge = min(1.0, (0.5 - max(abs(x / sx), abs(y / sy))) * 12)
        return z * height * max(0.0, edge)

    # skirt goes a little below ground so the flat rim never z-fights with the base
    obj = rbx.heightfield(size=size, res=res, height=height_fn, name=name, base=-3.0)

    def is_snow(c, n):
        if n.z < -0.5:
            return False  # bottom
        t = c.z / height
        band = snow_line + 0.08 * noise.noise(Vector((c.x * 0.02, c.y * 0.02, seed)))
        return (n.z > 0.6) or (t > band and n.z > 0.42) or (t < 0.08 and n.z > 0.3)

    rbx.paint_faces(obj, "rock", lambda c, n: True)
    rbx.paint_faces(obj, "dark_rock",
                    lambda c, n: n.z < 0.62 and noise.noise(Vector((0, 0, c.z * 0.05 + seed))) > 0.1)
    rbx.paint_faces(obj, "light_rock", lambda c, n: n.z < 0.45 and (c.z / height) > 0.55)
    rbx.paint_faces(obj, "snow_shadow", lambda c, n: is_snow(c, n) and n.z < 0.7)
    rbx.paint_faces(obj, "snow", lambda c, n: is_snow(c, n) and n.z >= 0.7)
    return obj
