"""Text / banner textures drawn with PIL, and planar UV mapping for flat panels."""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(HERE, "..", "textures")
FONT = "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf"
FONT_PLAIN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def banner(name, text, bg=(30, 90, 200), fg=(255, 255, 255), stroke=(10, 30, 80), size=(1024, 256),
           checker=True, font=FONT):
    os.makedirs(TEX_DIR, exist_ok=True)
    w, h = size
    img = Image.new("RGB", (w * 2, h * 2), bg)
    d = ImageDraw.Draw(img)
    if checker:  # checkered trims top and bottom
        s = h * 2 // 8
        for row in (0, 1, 6, 7):
            for i in range(0, w * 2 // s + 1):
                if (i + row) % 2 == 0:
                    d.rectangle([i * s, row * s, i * s + s, row * s + s], fill=(20, 20, 24))
                else:
                    d.rectangle([i * s, row * s, i * s + s, row * s + s], fill=(245, 245, 245))
    f = ImageFont.truetype(font, int(h * 2 * (0.5 if checker else 0.62)))
    d.text((w, h), text, font=f, fill=fg, anchor="mm", stroke_width=h // 16, stroke_fill=stroke)
    img = img.resize(size, Image.LANCZOS)
    path = os.path.join(TEX_DIR, f"{name}.png")
    img.save(path)
    return path


def sign_rows(name, rows, bg=(120, 78, 50), fg=(250, 240, 220), size=(512, 512)):
    """One texture with several text rows (an atlas): row k covers v in [1-(k+1)/n, 1-k/n]."""
    os.makedirs(TEX_DIR, exist_ok=True)
    w, h = size
    n = len(rows)
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    rh = h // n
    for k, text in enumerate(rows):
        y0 = k * rh
        # wood grain lines
        for g in range(6):
            yy = y0 + 8 + g * (rh - 16) // 6
            d.line([(0, yy), (w, yy + 3)], fill=(100, 64, 40), width=2)
        d.rectangle([4, y0 + 4, w - 5, y0 + rh - 5], outline=(70, 45, 28), width=6)
        f = ImageFont.truetype(FONT_PLAIN, int(rh * 0.42))
        d.text((w / 2, y0 + rh / 2), text, font=f, fill=fg, anchor="mm", stroke_width=3,
               stroke_fill=(60, 38, 22))
    path = os.path.join(TEX_DIR, f"{name}.png")
    img.save(path)
    return path


def planar_uv(x0, x1, z0, z1, v0=0.0, v1=1.0, side=(0.02, 0.5)):
    """UVs for a panel facing +/-Y: u from X, v from Z. The back is mirrored so text reads
    correctly from both sides. Edge faces sample a single texel."""
    def fn(co, n):
        u = (co.x - x0) / (x1 - x0)
        v = v0 + (v1 - v0) * (co.z - z0) / (z1 - z0)
        if n.y > 0.5:
            u = 1 - u
        elif abs(n.y) < 0.5:
            return side
        return (min(1, max(0, u)), min(1, max(0, v)))
    return fn
