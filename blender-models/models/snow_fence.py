# 16-stud section of orange safety fence on wooden posts (line them up along the course).
NAME = "snow_fence"
CATEGORY = "Park"


def build(rbx):
    for x in (-8, -4, 0, 4, 8):
        rbx.cylinder(0.14, 4.6, loc=(x, 0, 2.1), col="bark", sides=6)
        rbx.cone(0.18, 0.3, loc=(x, 0, 4.5), col="snow", sides=6)
    for z in (1.2, 2.0, 2.8, 3.6):
        rbx.box((16.2, 0.06, 0.34), loc=(0, -0.16, z), col="safety_orange")
    for x in range(-8, 9):
        rbx.box((0.1, 0.06, 2.7), loc=(x, -0.16, 2.4), col="safety_orange")
    rbx.box((16.4, 0.5, 0.35), loc=(0, 0, 0.1), col="snow", bevel=0.1)
