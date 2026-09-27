# FINISH arch - same build as the start gate, red banner.
import _park

NAME = "gate_finish"
CATEGORY = "Park"
COLLISION = "PreciseConvexDecomposition"


def build(rbx):
    _park.gate(rbx, NAME, "FINISH", bg=(200, 30, 40), flag_col="banner_blue")
