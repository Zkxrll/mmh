# Snow-covered low-poly pine, about 22 studs tall.
import _nature

NAME = "pine_tall"
CATEGORY = "Nature"


def build(rbx):
    _nature.pine(rbx, height=22, tiers=5, radius=5.0, seed=4, snow=0.40, lean=0)
