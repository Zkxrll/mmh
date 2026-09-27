# Snow-covered low-poly pine, about 14 studs tall.
import _nature

NAME = "pine_leaning"
CATEGORY = "Nature"


def build(rbx):
    _nature.pine(rbx, height=14, tiers=4, radius=3.6, seed=15, snow=0.45, lean=8)
