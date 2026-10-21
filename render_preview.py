"""
Direct PIL Renderer for Battle Scene Snapshot.
Uses the exact same coordinates, sprites, particles, and HUD logic
to verify the visual output.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

WIDTH, HEIGHT = 1280, 720
INK = (42, 34, 51)
LAV = (216, 204, 230)
LAV_D = (168, 152, 200)
PURPLE = (122, 79, 192)

bg = Image.open("assets/sprites/battle_bg.png").convert("RGBA")
canvas = bg.copy()
draw = ImageDraw.Draw(canvas)

# 1. Ground Shadows
# Enemy ground shadow
draw.ellipse([950 - 145, 435 - 32, 950 + 145, 435 + 32], fill=(58, 56, 117, 255))
# Player ground shadow
draw.ellipse([370 - 140, 595 - 30, 370 + 140, 595 + 30], fill=(58, 56, 117, 255))

# 2. Creatures
e_idle = Image.open("assets/sprites/Emberhorn_idle_left.png").convert("RGBA").resize((212, 184), Image.NEAREST)
canvas.alpha_composite(e_idle, (950 - 106, 430 - 184))

e_flame = Image.open("assets/sprites/Emberhorn_flame_0_left.png").convert("RGBA").resize((212, 184), Image.NEAREST)
canvas.alpha_composite(e_flame, (950 - 106, 430 - 184))

t_idle = Image.open("assets/sprites/Thornquill_idle_right.png").convert("RGBA").resize((192, 162), Image.NEAREST)
canvas.alpha_composite(t_idle, (370 - 96, 590 - 162))

# 3. Enemy HUD Top-Left
x1, y1, x2, y2 = 16, 16, 452, 132
pts = [(x1, y1), (x2 - 24, y1), (x2, y1 + 36), (x2, y2), (x1, y2)]
draw.polygon(pts, fill=LAV, outline=INK, width=3)
draw.line([(x1 + 4, y1 + 4), (x2 - 24, y1 + 4)], fill=LAV_D, width=2)
draw.line([(356, y1 + 2), (356, y2 - 2)], fill=INK, width=2)

try:
    font_bold = ImageFont.truetype("arialbd.ttf", 20)
    font_sm = ImageFont.truetype("arialbd.ttf", 14)
except Exception:
    font_bold = ImageFont.load_default()
    font_sm = ImageFont.load_default()

draw.text((32, 28), "EMBERHORN", fill=INK, font=font_bold)
draw.text((300, 32), "L12", fill=(90, 74, 120), font=font_sm)

# HP badge
draw.rectangle([46, 64, 46 + 44, 64 + 20], fill=PURPLE, outline=INK, width=2)
draw.text((58, 66), "HP", fill=LAV, font=font_sm)

# Health bar (118/118)
draw.rectangle([100, 64, 100 + 244, 64 + 20], fill=(32, 26, 44), outline=(32, 26, 44), width=2)
draw.rectangle([102, 66, 102 + 240, 66 + 16], fill=(94, 204, 70))
draw.text((276, 96), "118/118", fill=INK, font=font_bold)

# Enemy icon
e_ico = Image.open("assets/sprites/Emberhorn_idle_left.png").convert("RGBA").resize((53, 46), Image.NEAREST)
canvas.alpha_composite(e_ico, (380, 50))

# 4. Player HUD Bottom-Right
x1, y1, x2, y2 = 800, 442, 1264, 564
pts = [(x1 + 30, y1), (x2, y1), (x2, y2), (x1, y2), (x1 + 30, y1 + 55)]
draw.polygon(pts, fill=LAV, outline=INK, width=3)
draw.line([(x1 + 34, y1 + 4), (x2 - 4, y1 + 4)], fill=LAV_D, width=2)
draw.line([(900, y1 + 2), (900, y2 - 2)], fill=INK, width=2)

draw.text((916, 452), "THORNQUILL", fill=INK, font=font_bold)
draw.text((1200, 456), "L15", fill=(90, 74, 120), font=font_sm)

draw.rectangle([940, 488, 940 + 44, 488 + 20], fill=PURPLE, outline=INK, width=2)
draw.text((952, 490), "HP", fill=LAV, font=font_sm)

draw.rectangle([994, 488, 994 + 254, 488 + 20], fill=(32, 26, 44), outline=(32, 26, 44), width=2)
draw.rectangle([996, 490, 996 + 250, 490 + 16], fill=(94, 204, 70))

# Blue EXP bar
draw.rectangle([994, 513, 1248, 518], fill=INK, outline=INK)
draw.rectangle([994, 514, 1150, 517], fill=(74, 144, 232))

draw.text((1180, 526), "96/96", fill=INK, font=font_bold)

t_ico = Image.open("assets/sprites/Thornquill_idle_right.png").convert("RGBA").resize((48, 40), Image.NEAREST)
canvas.alpha_composite(t_ico, (828, 480))

# 5. Move Menu at bottom
draw.rectangle([24, 576, 880, 708], fill=INK, outline=(59, 48, 82), width=3)
draw.rectangle([28, 580, 876, 704], fill=(35, 28, 43), outline=LAV_D, width=2)

# Cursor & Move choices
draw.polygon([(48, 602), (48, 622), (62, 612)], fill=(240, 168, 48))
draw.text((74, 600), "Needle Volley", fill=(255, 255, 255), font=font_bold)
draw.text((460, 600), "Leaf Dart", fill=LAV, font=font_bold)
draw.text((74, 644), "Spore Spark", fill=LAV, font=font_bold)
draw.text((460, 644), "Solar Quill", fill=LAV, font=font_bold)

draw.text((74, 680), "[B] BAG x3     [S] SWITCH     [R] RUN", fill=LAV_D, font=font_sm)

# Info box
draw.rectangle([896, 576, 1256, 708], fill=INK, outline=(59, 48, 82), width=3)
draw.rectangle([900, 580, 1252, 704], fill=(35, 28, 43), outline=LAV_D, width=2)
draw.text((1030, 596), "USES: 16/16", fill=LAV, font=font_bold)

# Power badge
draw.rectangle([920, 636, 1056, 680], fill=(240, 168, 48), outline=(255, 224, 138), width=2)
draw.text((950, 646), "POW 16", fill=INK, font=font_bold)

# Type badge
draw.rectangle([1076, 636, 1232, 680], fill=(76, 175, 80), outline=(255, 255, 255), width=2)
draw.text((1115, 646), "GRASS", fill=(255, 255, 255), font=font_bold)

canvas.convert("RGB").save("battle_scene_preview.png")
print("battle_scene_preview.png rendered successfully!")
