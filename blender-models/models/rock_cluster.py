# A group of three rocks - good for breaking up flat snow.
import _nature

NAME = "rock_cluster"
CATEGORY = "Nature"


def build(rbx):
    _nature.rock(rbx, size=(4, 3.4, 3.2), seed=2, loc=(0, 0, 0))
    b = _nature.rock(rbx, size=(2.4, 2.2, 1.8), seed=5, loc=(4.6, 1.2, 0))
    c = _nature.rock(rbx, size=(1.6, 1.4, 1.2), seed=7, loc=(-3.4, 2.4, 0))
    b.location.x, b.location.y = 4.6, 1.2
    c.location.x, c.location.y = -3.4, 2.4
