# Snowboard shop: log cabin with a big display window, BOARD SHOP sign and a rack of boards.
import _house as H
import _signs

NAME = "board_shop"
JOIN = False
COLLISION = "PreciseConvexDecomposition"
CATEGORY = "Buildings"


def build(rbx):
    wx, dy = 18, 16
    zb, g = 1.6, 9.5
    H.stone_base(rbx, wx + 1.0, dy + 1.0, zb, seed=12)
    H.log_walls(rbx, wx, dy, zb, g)
    H.gable_roof(rbx, wx, dy, zb + g, pitch=38, overhang=2.4, seed=13)
    fy = -dy / 2 - 0.55
    H.door(rbx, (5.2, fy, zb), 0, w=3.2, h=6.2)
    H.window(rbx, (-3.2, fy, zb + 4.4), 0, w=7.5, h=4.2, shutters=None)   # display window
    H.lantern(rbx, (7.6, fy, zb + 5.4), 0)
    H.porch(rbx, 6, 3.2, -dy / 2 - 0.5, zb, 6.8, x=5.2)
    # sign board on the gable
    tex = _signs.banner("board_shop_sign", "BOARD SHOP", bg=(20, 60, 140), fg=(255, 230, 90),
                        stroke=(10, 20, 50), checker=False)
    # sign above the display window, on the log wall
    sw, sh, sx = 8.4, 2.1, -3.2
    z0 = zb + 7.0
    sign = rbx.box((sw, 0.3, sh), loc=(sx, -dy / 2 - 0.95, z0 + sh / 2))
    rbx.textured(sign, tex, _signs.planar_uv(sx - sw / 2, sx + sw / 2, z0, z0 + sh))
    rbx.group(sign, "Sign")
    frame = rbx.box((sw + 0.5, 0.3, sh + 0.5), loc=(sx, -dy / 2 - 0.7, z0 + sh / 2), col="dark_timber")
    rbx.group(frame, "Structure")
    # rack of boards leaning on the side wall
    rack = [rbx.box((0.4, 7, 0.4), loc=(wx / 2 + 2.2, -1, 3.8), col="dark_timber"),
            rbx.box((0.4, 7, 0.4), loc=(wx / 2 + 2.2, -1, 0.8), col="dark_timber")]
    for y in (-4.3, 2.3):
        rack.append(rbx.box((0.4, 0.4, 4.2), loc=(wx / 2 + 2.2, y, 2.1), col="dark_timber"))
    for k, col in enumerate(["red", "cyan", "neon_green", "hot_pink", "flame_yellow"]):
        b = rbx.box((0.18, 1.1, 5.0), loc=(wx / 2 + 1.5, -3.6 + k * 1.3, 2.6), rot=(0, -14, 0), col=col,
                    bevel=0.35, segments=3)
        rack.append(b)
    rbx.group(rbx.join(rack), "Structure")
    for side, yaw in ((1, 90), (-1, -90)):
        H.window(rbx, (side * (wx / 2 + 0.55), 3.5, zb + 4.6), yaw, w=2.2, h=2.8, shutters="red")
