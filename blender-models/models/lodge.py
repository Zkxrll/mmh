# Big alpine lodge: stone base, log ground floor, half-timbered upper floor, balcony over a
# covered entrance, steep snowy roof with icicles, chimney, warm glowing windows. 26 x 34 x 32 studs.
import _house as H

NAME = "lodge"
JOIN = False
COLLISION = "PreciseConvexDecomposition"
CATEGORY = "Buildings"


def build(rbx):
    wx, dy = 26, 32
    zb, g, u = 2.5, 10, 9
    H.stone_base(rbx, wx + 1.2, dy + 1.2, zb)
    H.log_walls(rbx, wx, dy, zb, g)
    H.timber_frame_walls(rbx, wx, dy, zb + g, u)
    z_eave = zb + g + u
    H.gable_roof(rbx, wx, dy, z_eave, pitch=40, overhang=2.6, seed=4)
    H.chimney(rbx, 8, 6, zb, 29.5)
    fy = -dy / 2 - 0.55
    # front, ground floor
    H.door(rbx, (0, fy, zb), 0)
    for x in (-7.5, 7.5):
        H.window(rbx, (x, fy, zb + 5), 0)
    H.lantern(rbx, (-2.6, fy, zb + 5.6), 0)
    H.lantern(rbx, (2.6, fy, zb + 5.6), 0)
    # front, upper floor + balcony over the entrance
    uy = -dy / 2 - 0.25
    H.window(rbx, (0, uy, zb + g + 3.3), 0, w=3.0, h=5.2, shutters=None)
    for x in (-7.5, 7.5):
        H.window(rbx, (x, uy, zb + g + 4.6), 0)
    H.balcony(rbx, 16, 4, -dy / 2, zb + g)
    parts = []
    for x in (-7.6, 7.6):   # posts holding the balcony
        parts.append(rbx.box((0.7, 0.7, g), loc=(x, -dy / 2 - 3.6, zb + g / 2 - 0.25), col="dark_timber",
                             bevel=0.05))
    H.steps(rbx, parts, 10, -dy / 2 - 0.6, zb)
    rbx.group(rbx.join(parts), "Structure")
    # gable window
    H.window(rbx, (0, uy, z_eave + 4.2), 0, w=2.4, h=2.8, shutters=None, snow=False)
    # sides and back
    for side, yaw in ((1, 90), (-1, -90)):
        for y in (-8, 0, 8):
            H.window(rbx, (side * (wx / 2 + 0.55), y, zb + 5), yaw)
            H.window(rbx, (side * (wx / 2 + 0.25), y, zb + g + 4.6), yaw)
    for x in (-6, 6):
        H.window(rbx, (x, dy / 2 + 0.55, zb + 5), 180)
        H.window(rbx, (x, dy / 2 + 0.25, zb + g + 4.6), 180)
