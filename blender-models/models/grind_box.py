# Wide grind box with metal coping, 18 long.
NAME = "grind_box"
CATEGORY = "Park"
COLLISION = "PreciseConvexDecomposition"


def build(rbx):
    L, W, H = 18, 1.8, 1.6
    rbx.box((L, W, H), loc=(0, 0, H / 2), col="banner_blue", bevel=0.06)
    rbx.box((L + 0.04, W + 0.04, 0.3), loc=(0, 0, H * 0.45), col="white")      # stripe
    rbx.box((L, W + 0.1, 0.12), loc=(0, 0, H + 0.06), col="metal", bevel=0.03)  # top slide
    for y in (-(W / 2 + 0.05), W / 2 + 0.05):                                      # coping edges
        rbx.box((L, 0.14, 0.2), loc=(0, y, H), col="metal", bevel=0.04)
    for x in (-L / 2, L / 2):                                                      # end ramps
        s = -1 if x < 0 else 1
        rbx.extrude_profile([(0, 0), (2.2, 0), (0, H)], depth=W, col="dark_metal", name="ramp",
                            loc=(x, 0, 0), rot=(0, 0, 0 if s > 0 else 180))
