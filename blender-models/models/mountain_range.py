# Long backdrop ridge with several peaks - place a few around the edge of the map.
import _terrain

NAME = "mountain_range"
CATEGORY = "Mountains"


def build(rbx):
    _terrain.mountain(rbx, NAME, size=(1000, 400), height=260, res=(120, 60), seed=8, snow_line=0.3,
                      peaks=[(-0.33, 0.0, 0.85, 0.3), (-0.08, 0.05, 1.0, 0.32),
                             (0.15, -0.05, 0.75, 0.28), (0.36, 0.02, 0.9, 0.3)], ridge_scale=1.4)
