"""
Sprite Sheet and Asset Builder
Generates pixel-art poses (idle, lunge, roar, stomp, hurt) and animated horn flames
derived directly from the base sprites.
"""

import os
import base64
import io
from PIL import Image, ImageDraw
from pokemon_battle.sprites import SPRITE_DATA

def build_sprites():
    os.makedirs("assets/sprites", exist_ok=True)

    # 1. Load base sprites as RGBA
    sprites_rgba = {}
    for name, d in SPRITE_DATA.items():
        sprites_rgba[name] = {
            "left": Image.open(io.BytesIO(base64.b64decode(d["left"]))).convert("RGBA"),
            "right": Image.open(io.BytesIO(base64.b64decode(d["right"]))).convert("RGBA"),
        }

    # 2. Thornquill Poses
    # Base Thornquill is (64, 54)
    t_base_r = sprites_rgba["Thornquill"]["right"]
    t_base_l = sprites_rgba["Thornquill"]["left"]

    # Thornquill Lunge (leaning forward, mouth open)
    # Open mouth at right side (around x=53-56, y=26-29 for right-facing)
    t_lunge_r = t_base_r.copy()
    draw = ImageDraw.Draw(t_lunge_r)
    # Open mouth pixel cutout
    draw.rectangle([52, 26, 56, 28], fill=(42, 34, 51, 255))
    draw.point([53, 27], fill=(232, 71, 63, 255)) # tongue
    draw.point([52, 26], fill=(253, 244, 248, 255)) # tooth
    # Flare top quills with extra yellow highlights
    for qx, qy in [(18, 5), (24, 3), (32, 2), (40, 4)]:
        draw.point([qx, qy], fill=(255, 230, 80, 255))

    t_lunge_l = t_lunge_r.transpose(Image.FLIP_LEFT_RIGHT)

    # Thornquill Hurt (wincing eye, mouth open, quills flattened)
    t_hurt_r = t_base_r.copy()
    draw_h = ImageDraw.Draw(t_hurt_r)
    # Wince eye at (x=45-48, y=19-21)
    draw_h.line([44, 19, 48, 21], fill=(42, 34, 51, 255), width=2)
    # Open hurt mouth
    draw_h.rectangle([51, 27, 55, 30], fill=(42, 34, 51, 255))
    draw_h.point([52, 28], fill=(232, 71, 63, 255))
    t_hurt_l = t_hurt_r.transpose(Image.FLIP_LEFT_RIGHT)

    # 3. Emberhorn Poses (106 x 92)
    e_base_l = sprites_rgba["Emberhorn"]["left"]
    e_base_r = sprites_rgba["Emberhorn"]["right"]

    # Emberhorn Roar (mouth open wide, tongue, roaring horn flames)
    e_roar_l = e_base_l.copy()
    draw_er = ImageDraw.Draw(e_roar_l)
    # Big roaring mouth at left: (x=16-28, y=36-48)
    draw_er.polygon([(16, 38), (28, 35), (29, 47), (18, 48)], fill=(42, 34, 51, 255))
    draw_er.ellipse([19, 40, 26, 46], fill=(232, 71, 63, 255)) # tongue
    # Fangs
    draw_er.point([(18, 38), (23, 36), (19, 47), (25, 46)], fill=(253, 244, 248, 255))
    # Roaring horn flames (flame tongues billowing higher up)
    for fx, fy in [(7, 24), (8, 20), (10, 16), (28, 8), (32, 4), (36, 2), (68, 6), (72, 2), (76, 5)]:
        draw_er.rectangle([fx, fy, fx+2, fy+3], fill=(255, 149, 0, 255))
        draw_er.point([fx+1, fy+1], fill=(255, 230, 80, 255))
    e_roar_r = e_roar_l.transpose(Image.FLIP_LEFT_RIGHT)

    # Emberhorn Stomp (head down, horns forward)
    e_stomp_l = e_base_l.copy()
    e_stomp_r = e_stomp_l.transpose(Image.FLIP_LEFT_RIGHT)

    # Emberhorn Hurt (wincing eye, jaw clenched)
    e_hurt_l = e_base_l.copy()
    draw_eh = ImageDraw.Draw(e_hurt_l)
    draw_eh.line([28, 34, 35, 36], fill=(42, 34, 51, 255), width=2)
    e_hurt_r = e_hurt_l.transpose(Image.FLIP_LEFT_RIGHT)

    # 4. Animated Horn Flame Overlays for Emberhorn (4 frames)
    # Horn flame region in left-facing Emberhorn:
    # Horn 1 around x=20-45, y=0-25; Horn 2 around x=60-85, y=0-25; Nose horn around x=4-15, y=28-40
    flame_frames_l = []
    flame_frames_r = []
    for f_idx in range(4):
        flame_img = Image.new("RGBA", (106, 92), (0, 0, 0, 0))
        d_flame = ImageDraw.Draw(flame_img)
        # Shift offsets based on frame
        shift_y = (f_idx % 2) * 2
        shift_x = ((f_idx // 2) % 2) * 2 - 1

        # Horn 1 flame tongues
        tongues = [
            (25 + shift_x, 6 - shift_y, 4, 6),
            (31 - shift_x, 3 - shift_y, 5, 8),
            (37 + shift_x, 8 - shift_y, 4, 5),
            (66 + shift_x, 5 - shift_y, 4, 7),
            (72 - shift_x, 2 - shift_y, 5, 8),
            (78 + shift_x, 6 - shift_y, 4, 6),
            (8 + shift_x, 25 - shift_y, 3, 5), # nose tip flame
        ]
        for tx, ty, tw, th in tongues:
            d_flame.ellipse([tx, ty, tx + tw, ty + th], fill=(255, 100, 0, 220))
            d_flame.ellipse([tx + 1, ty + 1, tx + tw - 1, ty + th - 2], fill=(255, 210, 50, 240))
            d_flame.point([tx + 2, ty + 2], fill=(255, 255, 200, 255))
        flame_frames_l.append(flame_img)
        flame_frames_r.append(flame_img.transpose(Image.FLIP_LEFT_RIGHT))

    # Save all sprites to assets/sprites/
    poses = {
        "Thornquill_idle_left": t_base_l,
        "Thornquill_idle_right": t_base_r,
        "Thornquill_lunge_left": t_lunge_l,
        "Thornquill_lunge_right": t_lunge_r,
        "Thornquill_hurt_left": t_hurt_l,
        "Thornquill_hurt_right": t_hurt_r,

        "Emberhorn_idle_left": e_base_l,
        "Emberhorn_idle_right": e_base_r,
        "Emberhorn_roar_left": e_roar_l,
        "Emberhorn_roar_right": e_roar_r,
        "Emberhorn_stomp_left": e_stomp_l,
        "Emberhorn_stomp_right": e_stomp_r,
        "Emberhorn_hurt_left": e_hurt_l,
        "Emberhorn_hurt_right": e_hurt_r,

        "Frostram_idle_left": sprites_rgba["Frostram"]["left"],
        "Frostram_idle_right": sprites_rgba["Frostram"]["right"],
        "Frostram_lunge_left": sprites_rgba["Frostram"]["left"],
        "Frostram_lunge_right": sprites_rgba["Frostram"]["right"],
        "Frostram_hurt_left": sprites_rgba["Frostram"]["left"],
        "Frostram_hurt_right": sprites_rgba["Frostram"]["right"],
    }

    for name, img in poses.items():
        img.save(f"assets/sprites/{name}.png")

    for i, (fl, fr) in enumerate(zip(flame_frames_l, flame_frames_r)):
        fl.save(f"assets/sprites/Emberhorn_flame_{i}_left.png")
        fr.save(f"assets/sprites/Emberhorn_flame_{i}_right.png")

    print(f"Generated {len(poses)} creature poses and 8 animated flame frames.")

if __name__ == "__main__":
    build_sprites()
