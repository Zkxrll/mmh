# Cluster of ice crystals - glass shards with a glowing cyan core. Magical landmark.
import math
import random

NAME = "ice_crystals"
CATEGORY = "Nature"


def build(rbx):
    rnd = random.Random(5)
    specs = [(0, 0, 7.5, 0.9, 0, 0), (1.6, 0.5, 4.8, 0.6, 18, 30), (-1.4, 0.8, 5.5, 0.7, -16, -20),
             (0.6, -1.5, 3.8, 0.5, 20, -60), (-0.9, -1.2, 3.0, 0.45, -22, 70), (2.4, -0.8, 2.6, 0.4, 30, 10)]
    for x, y, h, r, tilt, yaw in specs:
        body = rbx.cylinder(r, h, loc=(0, 0, h / 2), col="ice", sides=6)
        tip = rbx.cone(r, r * 1.8, loc=(0, 0, h + r * 0.9), col="ice", sides=6)
        c = rbx.join([body, tip])
        rbx.apply_transform(c, location=True)
        c.rotation_euler = (math.radians(tilt), 0, math.radians(yaw))
        c.location = (x, y, 0)
        rbx.glow(c, "ice", material="Glass")
        core = rbx.cylinder(r * 0.35, h * 0.5, loc=(0, 0, h * 0.62), sides=6)
        core.rotation_euler = (math.radians(tilt), 0, math.radians(yaw))
        core.location = (x, y, 0)
        rbx.glow(core, "glow_cyan")
    rbx.sphere(2.6, loc=(0, 0, 0.2), col="snow", detail=2, scale=(1.3, 1.1, 0.45))
