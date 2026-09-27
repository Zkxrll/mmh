# Big snow-capped boulder, ~9 x 6 x 7 studs.
import _nature

NAME = "rock_boulder"
CATEGORY = "Nature"


def build(rbx):
    _nature.rock(rbx, size=(5, 4, 3.6), seed=4)
