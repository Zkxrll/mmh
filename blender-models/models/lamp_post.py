# Rustic wooden lamp post with a hanging lantern (glass glows - Neon). ~11 studs tall.
NAME = "lamp_post"
CATEGORY = "Props"


def build(rbx):
    rbx.box((0.7, 0.7, 10), loc=(0, 0, 5), col="dark_timber", bevel=0.08)
    rbx.box((1.4, 1.4, 0.6), loc=(0, 0, 0.3), col="dark_rock", bevel=0.12)
    rbx.box((2.6, 0.45, 0.45), loc=(1.0, 0, 9.4), col="dark_timber", bevel=0.05)   # arm
    rbx.box((0.3, 0.3, 1.6), loc=(0.6, 0, 8.6), rot=(0, 45, 0), col="dark_timber")  # brace
    rbx.cylinder(0.04, 0.6, loc=(2.0, 0, 8.95), col="dark_metal", sides=6)         # hook
    # lantern: frame + glowing glass + roof
    cx, cz = 2.0, 7.95
    rbx.glow(rbx.box((0.62, 0.62, 0.9), loc=(cx, 0, cz)), "window_glow")
    for dx in (-0.33, 0.33):
        for dy in (-0.33, 0.33):
            rbx.box((0.08, 0.08, 1.0), loc=(cx + dx, dy, cz), col="carbon")
    rbx.box((0.8, 0.8, 0.1), loc=(cx, 0, cz - 0.5), col="carbon")
    rbx.cone(0.62, 0.45, loc=(cx, 0, cz + 0.7), col="carbon", sides=4, rot=(0, 0, 45))
    rbx.cone(0.66, 0.22, loc=(cx, 0, cz + 0.62), col="snow", sides=4, rot=(0, 0, 45))
    # snow on top of the post and arm
    rbx.box((0.75, 0.75, 0.18), loc=(0, 0, 10.08), col="snow", bevel=0.06)
    rbx.box((2.4, 0.5, 0.12), loc=(1.1, 0, 9.68), col="snow", bevel=0.04)
