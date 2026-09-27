# Snow kicker (jump), 8 wide. Ride toward +X; the lip is at the high end.
import _park

NAME = "kicker_small"
CATEGORY = "Park"
COLLISION = "PreciseConvexDecomposition"


def build(rbx):
    _park.kicker(rbx, length=12, height=3.5, width=8, lip_col="banner_blue")
