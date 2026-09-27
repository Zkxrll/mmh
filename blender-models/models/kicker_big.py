# Big snow kicker for tricks, 12 wide and 6 high.
import _park

NAME = "kicker_big"
CATEGORY = "Park"
COLLISION = "PreciseConvexDecomposition"


def build(rbx):
    _park.kicker(rbx, length=20, height=6, width=12, lip_col="safety_orange")
