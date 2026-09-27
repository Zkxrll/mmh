# Two-seat chairlift chair on its hanger (attach the grip to your cable). ~7 studs tall.
NAME = "lift_chair"
CATEGORY = "Props"
JOIN = False


def build(rbx):
    # hanger: grip at the top, bar down, bend to the back of the seat
    grip = rbx.box((0.8, 0.5, 0.5), loc=(0, 0, 7.6), col="dark_metal", bevel=0.08)
    rbx.group(grip, "Chair")
    pts = [(0, 0, 7.4), (0, 0, 3.6), (0, 0.9, 2.9), (0, 0.9, 1.9)]
    rbx.group(rbx.tube(pts, radius=0.12, col="metal", sides=8), "Chair")
    seat = rbx.box((3.4, 1.3, 0.25), loc=(0, 0.2, 1.7), col="banner_blue", bevel=0.08)
    back = rbx.box((3.4, 0.2, 1.4), loc=(0, 0.85, 2.5), rot=(-12, 0, 0), col="banner_blue", bevel=0.06)
    frame = rbx.tube([(-1.8, 0.9, 1.6), (-1.8, 0.9, 3.2), (1.8, 0.9, 3.2), (1.8, 0.9, 1.6)],
                     radius=0.08, col="metal", sides=8)
    arms = rbx.tube([(-1.8, 0.9, 2.4), (-1.8, -0.3, 2.4), (-1.8, -0.3, 1.8)], radius=0.07, col="metal", sides=8)
    arms2 = rbx.tube([(1.8, 0.9, 2.4), (1.8, -0.3, 2.4), (1.8, -0.3, 1.8)], radius=0.07, col="metal", sides=8)
    for o in (seat, back, frame, arms, arms2):
        rbx.group(o, "Chair")
    # safety bar with footrest (separate part so a script can swing it down)
    bar = rbx.tube([(-1.7, 0.8, 3.3), (-1.7, -0.8, 3.0), (1.7, -0.8, 3.0), (1.7, 0.8, 3.3)],
                   radius=0.07, col="dark_metal", sides=8)
    foot = rbx.tube([(-0.6, -0.8, 3.0), (-0.6, -1.2, 0.8), (0.6, -1.2, 0.8), (0.6, -0.8, 3.0)],
                    radius=0.06, col="dark_metal", sides=8)
    rbx.group(bar, "SafetyBar")
    rbx.group(foot, "SafetyBar")
