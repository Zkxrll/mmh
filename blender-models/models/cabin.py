# Cozy log cabin with a covered porch, chimney, snowy roof and icicles. 16 x 20 x 17 studs.
import _house as H

NAME = "cabin"
JOIN = False
COLLISION = "PreciseConvexDecomposition"
CATEGORY = "Buildings"


def build(rbx):
    wx, dy = 16, 14
    zb, g = 1.6, 9
    H.stone_base(rbx, wx + 1.0, dy + 1.0, zb, seed=7)
    H.log_walls(rbx, wx, dy, zb, g)
    H.gable_roof(rbx, wx, dy, zb + g, pitch=42, overhang=2.2, seed=9)
    H.chimney(rbx, -4.5, 3, zb, zb + g + 7.5, w=2.4)
    fy = -dy / 2 - 0.55
    H.door(rbx, (0, fy, zb), 0, w=3.0, h=6.0)
    for x in (-4.8, 4.8):
        H.window(rbx, (x, fy, zb + 4.6), 0, w=2.2, h=2.8, shutters="dark_green")
    H.porch(rbx, 8, 4, -dy / 2 - 0.5, zb, 6.6)
    H.lantern(rbx, (2.2, fy, zb + 5.2), 0)
    for side, yaw in ((1, 90), (-1, -90)):
        H.window(rbx, (side * (wx / 2 + 0.55), 0, zb + 4.6), yaw, w=2.2, h=2.8, shutters="dark_green")
    H.window(rbx, (0, dy / 2 + 0.55, zb + 4.6), 180, w=2.2, h=2.8, shutters="dark_green")
    H.window(rbx, (0, -dy / 2 - 0.2, zb + g + 3.0), 0, w=1.8, h=2.2, shutters=None, snow=False)
