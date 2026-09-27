# Flat-down-flat kinked rail (ride toward +X).
import _park

NAME = "rail_kink"
CATEGORY = "Park"
COLLISION = "PreciseConvexDecomposition"


def build(rbx):
    pts = [(-12, 0, 5.0), (-4, 0, 5.0), (4, 0, 2.2), (12, 0, 2.2)]
    _park.rail(rbx, pts, post_col="banner_blue",
               posts=[(-10, 0, 5.0), (-4, 0, 5.0), (4, 0, 2.2), (10, 0, 2.2)])
