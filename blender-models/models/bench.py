# Wooden park bench with a little snow on the seat. 6 studs wide.
NAME = "bench"
CATEGORY = "Props"


def build(rbx):
    for k in range(4):
        rbx.box((6, 0.42, 0.18), loc=(0, -0.7 + k * 0.46, 1.6), col="timber", bevel=0.04)
    for k in range(3):
        rbx.box((6, 0.14, 0.4), loc=(0, 0.95, 2.1 + k * 0.5), rot=(-10, 0, 0), col="timber", bevel=0.04)
    for x in (-2.5, 2.5):
        rbx.tube([(x, -0.7, 0), (x, -0.6, 1.5), (x, 0.8, 1.5), (x, 0.9, 0)], radius=0.09, col="carbon", sides=6)
        rbx.tube([(x, 0.8, 1.5), (x, 1.05, 3.3)], radius=0.09, col="carbon", sides=6)
    rbx.box((5.4, 1.4, 0.12), loc=(0.2, 0.0, 1.74), col="snow", bevel=0.05)
