# Low flat rock slab with snow on top.
import _nature

NAME = "rock_flat"
CATEGORY = "Nature"


def build(rbx):
    _nature.rock(rbx, size=(7, 5, 1.8), seed=9)
