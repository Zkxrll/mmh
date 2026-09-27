# Big hero mountain with a sharp snowy peak. ~600 x 330 x 600 studs (scale it up in Studio).
import _terrain

NAME = "mountain_peak"
CATEGORY = "Mountains"


def build(rbx):
    _terrain.mountain(rbx, NAME, size=(600, 600), height=330, seed=3,
                      peaks=[(0.0, 0.0, 1.0, 0.5), (0.18, -0.12, 0.6, 0.3), (-0.2, 0.15, 0.5, 0.28)])
