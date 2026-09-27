# Slalom gate: two striped poles with a panel between them (blue).
NAME = "slalom_blue"
CATEGORY = "Park"


def build(rbx):
    for x in (-2.2, 2.2):
        pole = rbx.lathe([(0.12, k * 0.8) for k in range(9)] + [(0.0, 6.6)], loc=(x, 0, 0), col="white", sides=8)
        # add height rings so it can be striped
        rbx.paint_faces(pole, "banner_blue", lambda c, n: int(c.z / 0.8) % 2 == 0)
    panel = rbx.box((4.2, 0.06, 1.8), loc=(0, 0, 5.2), col="banner_blue")
    rbx.box((4.2, 0.08, 0.3), loc=(0, 0, 4.6), col="white")
