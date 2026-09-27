# Campfire: stone ring, crossed logs and glowing flames (the FX script adds fire + light).
import math
import _nature

NAME = "campfire"
CATEGORY = "Props"


def build(rbx):
    for k in range(9):
        a = 2 * math.pi * k / 9
        s = _nature.rock(rbx, size=(0.55, 0.45, 0.4), seed=30 + k, snow=(k % 3 == 0), detail=2)
        s.location = (2.0 * math.cos(a), 2.0 * math.sin(a), 0.1)
    for k in range(4):
        a = math.degrees(math.pi * k / 4)
        log = rbx.cylinder(0.22, 2.8, loc=(0, 0, 0.45), rot=(0, 72, a), col="bark", sides=7)
    rbx.glow(rbx.cone(0.8, 1.8, loc=(0, 0, 1.0), col="fire", sides=6), "fire")
    rbx.glow(rbx.cone(0.45, 1.3, loc=(0.15, 0.1, 0.95), sides=5, rot=(0, 0, 30)), "flame_yellow")
    rbx.glow(rbx.sphere(0.9, loc=(0, 0, 0.3), detail=1, scale=(1, 1, 0.35)), "ember")
