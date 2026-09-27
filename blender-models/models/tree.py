# Low-poly tree: tapered, slightly bent trunk + three stacked leaf blobs.
import math

NAME = "tree"


def build(rbx):
    trunk = rbx.cylinder(radius=0.9, depth=8, loc=(0, 0, 4), col="wood", sides=8)
    rbx.taper(trunk, top_scale=0.55)
    rbx.jitter(trunk, 0.08, seed=1)

    for i, (r, z, x) in enumerate([(3.6, 9.0, 0.0), (3.0, 11.5, 0.8), (2.2, 13.6, -0.3)]):
        leaves = rbx.sphere(radius=r, loc=(x, 0.3 * i, z), col="leaf" if i % 2 == 0 else "green",
                            detail=2, scale=(1, 1, 0.8))
        rbx.jitter(leaves, 0.3, seed=10 + i)

    # a few roots
    for a in (0, 120, 240):
        # cone tip points outward and slightly down, base tucked into the trunk
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        rbx.cone(radius=0.5, depth=2.0, loc=(1.0 * c, 1.0 * s, 0.35), rot=(0, 100, a),
                 col="dark_brown", sides=5)
