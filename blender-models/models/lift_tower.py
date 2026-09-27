# Chairlift tower: tapered steel pole, crossarm and cable wheel assemblies. ~34 studs tall.
import math

NAME = "lift_tower"
CATEGORY = "Props"


def build(rbx):
    H = 32
    rbx.cylinder(1.1, H, loc=(0, 0, H / 2), col="flame_yellow", sides=10, radius_top=0.75)
    rbx.box((4.5, 4.5, 1.2), loc=(0, 0, 0.6), col="light_stone", bevel=0.15)  # concrete footing
    rbx.box((18, 0.9, 1.1), loc=(0, 0, H + 0.4), col="flame_yellow", bevel=0.1)  # crossarm
    for s in (-1, 1):
        rbx.box((0.4, 0.4, 3.2), loc=(s * 3.5, 0, H - 1.1), rot=(0, s * 40, 0), col="flame_yellow")  # braces
        # wheel train under each end of the arm
        x = s * 7.5
        rbx.box((0.3, 3.8, 0.35), loc=(x, 0, H - 0.5), col="dark_metal")
        for k in (-1.2, 0, 1.2):
            rbx.cylinder(0.45, 0.3, loc=(x, k, H - 0.9), rot=(0, 90, 0), col="rubber", sides=12)
            rbx.cylinder(0.2, 0.34, loc=(x, k, H - 0.9), rot=(0, 90, 0), col="metal", sides=8)
    # ladder up the pole
    rbx.box((0.1, 0.1, H - 2), loc=(0.95, -0.35, H / 2), col="dark_metal")
    rbx.box((0.1, 0.1, H - 2), loc=(0.95, 0.35, H / 2), col="dark_metal")
    for k in range(int(H - 2)):
        rbx.box((0.1, 0.7, 0.08), loc=(0.95, 0, 1.5 + k), col="dark_metal")
    # red aviation light + snow on the arm
    rbx.glow(rbx.sphere(0.25, loc=(0, 0, H + 1.2), detail=1), "bright_red")
    rbx.box((17.6, 0.95, 0.15), loc=(0, 0, H + 1.02), col="snow")
