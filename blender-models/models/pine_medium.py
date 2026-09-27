# Snow-covered low-poly pine, about 15 studs tall.
import _nature

NAME = "pine_medium"
CATEGORY = "Nature"


def build(rbx):
    _nature.pine(rbx, height=15, tiers=4, radius=4.0, seed=7, snow=0.45, lean=0)
