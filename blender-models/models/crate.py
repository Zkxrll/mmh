# Wooden crate with a cut-out hand hole - shows boolean cuts and bevels. 4x4x4 studs.
NAME = "crate"
CATEGORY = "Props"


def build(rbx):
    body = rbx.box((3.6, 3.6, 3.6), loc=(0, 0, 2), col="light_wood", bevel=0.05)

    # hand holes on two sides (boolean difference)
    for x in (-1.8, 1.8):
        cutter = rbx.box((0.5, 1.2, 0.4), loc=(x, 0, 3.1), col=None, bevel=0.15, segments=3)
        rbx.boolean(body, cutter, "DIFFERENCE")

    # frame planks on every edge
    for x in (-1, 1):
        for y in (-1, 1):
            rbx.box((0.5, 0.5, 4), loc=(x * 1.8, y * 1.8, 2), col="wood", bevel=0.06)
    for z in (0.25, 3.75):
        for x in (-1, 1):
            rbx.box((0.5, 4, 0.5), loc=(x * 1.8, 0, z), col="wood", bevel=0.06)
        for y in (-1, 1):
            rbx.box((4, 0.5, 0.5), loc=(0, y * 1.8, z), col="wood", bevel=0.06)

    # diagonal brace on front and back
    for y in (-1.86, 1.86):
        rbx.box((0.4, 0.15, 4.4), loc=(0, y, 2), rot=(0, 45, 0), col="wood", bevel=0.03)

    # metal corner plates
    for x in (-1, 1):
        for y in (-1, 1):
            for z in (0.25, 3.75):
                rbx.box((0.62, 0.62, 0.62), loc=(x * 1.8, y * 1.8, z), col="dark_metal", bevel=0.08)
