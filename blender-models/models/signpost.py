# Wooden direction sign with three arrow boards (one texture atlas).
import _signs

NAME = "signpost"
CATEGORY = "Props"


def build(rbx):
    rbx.cylinder(0.3, 9, loc=(0, 0, 4.5), col="dark_timber", sides=8)
    rbx.cone(0.34, 0.5, loc=(0, 0, 9.2), col="snow", sides=8)
    rows = ["LODGE", "SLOPES", "SKI LIFT"]
    tex = _signs.sign_rows("signpost_arrows", rows)
    n = len(rows)
    for k, (z, direction, yaw) in enumerate([(7.6, 1, 8), (6.2, -1, -10), (4.8, 1, -18)]):
        L, H = 4.6, 1.1
        # arrow outline pointing +X, drawn from the post outward
        pts = [(0, 0), (L - 0.8, 0), (L, H / 2), (L - 0.8, H), (0, H)]
        if direction < 0:
            pts = [(-x, zz) for x, zz in pts][::-1]
        arrow = rbx.extrude_profile(pts, depth=0.2, col="timber", name="arrow")
        x0, x1 = (0, L) if direction > 0 else (-L, 0)
        v1 = 1 - k / n
        v0 = 1 - (k + 1) / n
        rbx.textured(arrow, tex, _signs.planar_uv(x0, x1, 0, H, v0 + 0.01, v1 - 0.01, side=(0.02, v0 + 0.02)))
        rbx.group(arrow, "Signs")
        arrow.location = (0, 0, z - H / 2)
        arrow.rotation_euler = (0, 0, __import__("math").radians(yaw))
        # thin snow line on the top edge of each board
        s = rbx.box((L - 0.4, 0.24, 0.1), loc=((L / 2 - 0.2) * direction, 0, z + H / 2 + 0.03), col="snow")
        rbx.apply_transform(s, location=True)  # rotate around the post, like the board
        s.rotation_euler = (0, 0, __import__("math").radians(yaw))
