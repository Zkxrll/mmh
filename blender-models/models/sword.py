# Stylized sword (a Tool handle would go on the grip). About 5 studs long.
NAME = "sword"


def build(rbx):
    # blade: extruded outline with a pointed tip, then a raised center ridge
    blade = rbx.extrude_profile(
        [(-0.28, 0), (0.28, 0), (0.28, 3.3), (0, 3.9), (-0.28, 3.3)],
        depth=0.12, loc=(0, 0, 1.35), col="metal", name="blade")
    ridge = rbx.extrude_profile(
        [(-0.06, 0), (0.06, 0), (0.06, 3.3), (0, 3.75), (-0.06, 3.3)],
        depth=0.18, loc=(0, 0, 1.35), col="light_stone", name="ridge")

    # crossguard with bevelled edges and gold gem
    rbx.box((1.6, 0.3, 0.25), loc=(0, 0, 1.25), col="gold", bevel=0.06, segments=2)
    rbx.sphere(0.16, loc=(0, -0.17, 1.25), col="red", detail=1)
    rbx.sphere(0.16, loc=(0, 0.17, 1.25), col="red", detail=1)
    for x in (-0.85, 0.85):
        rbx.sphere(0.17, loc=(x, 0, 1.25), col="gold", detail=1)

    # grip wrapped in rings, pommel on the end
    rbx.cylinder(0.14, 1.0, loc=(0, 0, 0.62), col="dark_brown", sides=8)
    for i in range(5):
        rbx.torus(0.15, 0.035, loc=(0, 0, 0.25 + i * 0.18), col="brown", seg=10, minor_seg=4)
    rbx.sphere(0.22, loc=(0, 0, 0.05), col="gold", detail=2)
