# Friendly snowman with hat, scarf, carrot nose and stick arms. ~7 studs tall.
NAME = "snowman"
CATEGORY = "Props"


def build(rbx):
    rbx.sphere(1.8, loc=(0, 0, 1.6), col="snow", detail=3, scale=(1, 1, 0.92))
    rbx.sphere(1.3, loc=(0, 0, 4.0), col="snow", detail=3)
    rbx.sphere(0.95, loc=(0, 0, 5.85), col="snow", detail=3)
    for z in (3.6, 4.2, 4.8):   # coal buttons
        rbx.sphere(0.13, loc=(0, -1.22 - (0.05 if z == 4.2 else 0), z), col="carbon", detail=1)
    for x in (-0.33, 0.33):     # eyes
        rbx.sphere(0.12, loc=(x, -0.84, 6.1), col="carbon", detail=1)
    rbx.cone(0.16, 0.9, loc=(0, -1.25, 5.85), rot=(90, 0, 0), col="orange", sides=6)  # carrot
    for k in range(5):          # smile
        x = -0.36 + k * 0.18
        rbx.sphere(0.07, loc=(x, -0.86, 5.55 - 0.1 * (1 - abs(x) / 0.36)), col="carbon", detail=1)
    rbx.torus(0.98, 0.22, loc=(0, 0, 5.0), col="red", seg=16, minor_seg=6)  # scarf
    rbx.box((0.4, 0.14, 1.3), loc=(0.55, -0.95, 4.4), rot=(8, 0, -12), col="red")
    rbx.cylinder(1.05, 0.12, loc=(0, 0, 6.65), col="carbon", sides=16)      # hat brim
    rbx.cylinder(0.65, 1.1, loc=(0, 0, 7.25), col="carbon", sides=16)       # hat
    rbx.cylinder(0.67, 0.2, loc=(0, 0, 6.85), col="red", sides=16)          # hat band
    for s in (-1, 1):           # stick arms with twigs
        rbx.tube([(s * 1.1, 0, 4.3), (s * 2.4, -0.1, 5.1), (s * 3.0, -0.1, 5.8)], radius=0.08, col="bark", sides=5)
        rbx.tube([(s * 2.4, -0.1, 5.1), (s * 2.9, -0.2, 5.1)], radius=0.05, col="bark", sides=5)
