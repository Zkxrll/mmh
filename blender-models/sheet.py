"""Combine preview images into one contact sheet:  python3 sheet.py out.png out/board_*"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

out, dirs = sys.argv[1], sys.argv[2:]
cols = min(3, len(dirs))
rows = (len(dirs) + cols - 1) // cols
cell = 400
sheet = Image.new("RGB", (cols * cell, rows * cell), (30, 32, 38))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
for i, d in enumerate(dirs):
    p = os.path.join(d, "preview_front.jpg")
    if not os.path.exists(p):
        p = p[:-4] + ".png"
    img = Image.open(p).convert("RGB").resize((cell, cell), Image.LANCZOS)
    x, y = (i % cols) * cell, (i // cols) * cell
    sheet.paste(img, (x, y))
    ImageDraw.Draw(sheet).text((x + 10, y + 8), os.path.basename(d.rstrip("/")), font=font, fill=(20, 20, 30))
sheet.save(out)
print(out)
