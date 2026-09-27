# Smaller rounded snowy hill for the mid-distance. ~300 x 110 x 300 studs.
import _terrain

NAME = "mountain_hill"
CATEGORY = "Mountains"


def build(rbx):
    _terrain.mountain(rbx, NAME, size=(300, 300), height=110, res=(60, 60), seed=21, snow_line=0.15,
                      peaks=[(0.0, 0.0, 1.0, 0.55), (0.2, 0.1, 0.7, 0.35)], ridge_scale=0.7)
