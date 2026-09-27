# Snow-covered low-poly pine, about 8 studs tall.
import _nature

NAME = "pine_small"
CATEGORY = "Nature"


def build(rbx):
    _nature.pine(rbx, height=8, tiers=3, radius=2.6, seed=11, snow=0.5, lean=0)
