# START arch with a checkered banner, flags and cyan lights. 24 wide, 14 tall.
import _park

NAME = "gate_start"
CATEGORY = "Park"
COLLISION = "PreciseConvexDecomposition"


def build(rbx):
    _park.gate(rbx, NAME, "START", bg=(30, 90, 200), flag_col="red")
