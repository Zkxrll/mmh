# Straight 16-stud grind rail at knee height.
import _park

NAME = "rail_flat"
CATEGORY = "Park"


def build(rbx):
    _park.rail(rbx, [(-8, 0, 2.4), (8, 0, 2.4)], posts=[(-6, 0, 2.4), (6, 0, 2.4)])
