"""Particle textures for the effects (white / greyscale so ParticleEmitter.Color can tint them).
    python3 tools/make_fx_textures.py  ->  textures/fx_*.png  (upload, then paste ids in Config.Textures)"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "textures")
S = 256
rnd = random.Random(3)
os.makedirs(OUT, exist_ok=True)


def save(name, alpha, rgb=(255, 255, 255)):
    a = np.clip(alpha, 0, 1)
    img = np.zeros((S, S, 4), np.uint8)
    img[..., 0], img[..., 1], img[..., 2] = rgb
    img[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(img, "RGBA").save(os.path.join(OUT, name))


yy, xx = np.mgrid[0:S, 0:S] / (S - 1) * 2 - 1
r = np.sqrt(xx ** 2 + yy ** 2)


def value_noise(scale, seed):
    g = np.random.default_rng(seed).random((scale + 2, scale + 2))
    img = Image.fromarray((g * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC)
    return np.asarray(img) / 255.0


# soft snow puff: round blob with lumpy noise edges
n = 0.6 * value_noise(6, 1) + 0.4 * value_noise(14, 2)
save("fx_snow_puff.png", np.clip(1 - r * (1.05 + 0.5 * (n - 0.5) * 2), 0, 1) ** 1.6)

# smoke: bigger, softer, more noise
n2 = 0.5 * value_noise(5, 3) + 0.5 * value_noise(11, 4)
save("fx_smoke.png", np.clip(1 - r * 1.1, 0, 1) ** 1.2 * (0.55 + 0.45 * n2))

# sparkle: 4-point star with glow
ang = np.arctan2(yy, xx)
star = np.clip(1 - r * (1 + 7 * np.abs(np.sin(2 * ang)) ** 0.7), 0, 1) ** 2
glow = np.clip(1 - r, 0, 1) ** 4
save("fx_sparkle.png", np.maximum(star, glow * 0.8))

# spark: small hot dot (stretch it with Squash)
save("fx_spark.png", np.clip(1 - r * 1.6, 0, 1) ** 1.5 + np.clip(1 - r, 0, 1) ** 6 * 0.4)

# streak: long thin horizontal line, soft ends (speed lines)
save("fx_streak.png", np.clip(1 - np.abs(yy) * 9, 0, 1) * np.clip(1 - np.abs(xx), 0, 1) ** 0.6)

# confetti: rectangle
save("fx_confetti.png", ((np.abs(xx) < 0.55) & (np.abs(yy) < 0.28)).astype(float))

# flame: teardrop, bright core
fy = (yy + 1) / 2  # 0 top .. 1 bottom
width = 0.62 * np.sqrt(np.clip(fy, 0, 1)) * (1.15 - fy * 0.5)
flame = np.clip(1 - np.abs(xx) / (width + 1e-3), 0, 1) * np.clip((fy - 0.02) * 3, 0, 1)
flame *= np.clip((1.02 - fy) * 6, 0, 1)
save("fx_flame.png", flame ** 1.2)

# snowflake: six arms with branches, softened
img = Image.new("L", (S * 2, S * 2), 0)
d = ImageDraw.Draw(img)
c = S
for k in range(6):
    a = math.radians(60 * k + 30)
    ex, ey = c + math.cos(a) * S * 0.9, c + math.sin(a) * S * 0.9
    d.line([(c, c), (ex, ey)], fill=255, width=18)
    for f in (0.4, 0.65):
        bx, by = c + math.cos(a) * S * 0.9 * f, c + math.sin(a) * S * 0.9 * f
        for s in (-1, 1):
            b = a + s * math.radians(45)
            d.line([(bx, by), (bx + math.cos(b) * S * 0.3, by + math.sin(b) * S * 0.3)], fill=255, width=14)
img = img.filter(ImageFilter.GaussianBlur(4)).resize((S, S), Image.LANCZOS)
save("fx_snowflake.png", np.asarray(img) / 255.0)
print("wrote", sorted(f for f in os.listdir(OUT) if f.startswith("fx_")))
