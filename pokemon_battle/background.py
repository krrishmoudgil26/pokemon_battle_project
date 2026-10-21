import os
import math
import random
import tkinter as tk
from .config import *

def build_background():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bg_path = os.path.join(base_dir, "assets", "sprites", "battle_bg.png")

    if os.path.exists(bg_path):
        try:
            return tk.PhotoImage(file=bg_path)
        except Exception as e:
            print(f"[Background] Failed to load battle_bg.png: {e}. Falling back to procedural.")

    # Procedural generation fallback
    rng = random.Random(11)

    ridge1 = [17 + 2.5 * math.sin(x * .09 + 1) + 1.5 * math.sin(x * .23 + 3) + rng.uniform(-.8, .8) for x in range(COLS)]
    ridge2 = [24 + 2.5 * math.sin(x * .07 + 2) + 1.5 * math.sin(x * .19) + rng.uniform(-.8, .8) for x in range(COLS)]
    ridge3 = [31 + 2.0 * math.sin(x * .10 + 4) + 1.5 * math.sin(x * .31) + rng.uniform(-1.2, 1.2) for x in range(COLS)]

    pink_clouds = [(10, 9, 24, 10), (145, 8, 22, 13), (135, 17, 18, 7), (90, 18, 12, 4)]
    white_clouds = [(96, 19, 8, 3), (150, 6, 12, 7), (140, 12, 8, 3), (22, 15, 8, 3)]

    def in_cloud(x, y, clouds):
        for cx, cy, rx, ry in clouds:
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d + rng.uniform(-.25, .25) < 1:
                return True
        return False

    grid = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            color = SKY
            if in_cloud(x, y, pink_clouds):
                color = PINK
            if in_cloud(x, y, white_clouds):
                color = WHITE

            if color == SKY and 24 <= x <= 145 and 12 <= y <= 19 and (x + y) % 2 == 0 \
                    and rng.random() < (y - 11) / 8:
                color = SKY_DARK

            yy = y + rng.uniform(-.7, .7)
            if yy >= ridge1[x]:
                color = TEAL_L if (x * 3 + y * 5) % 11 == 0 else TEAL
            if yy >= ridge2[x]:
                color = INDIGO_D if rng.random() < .12 else INDIGO
            if yy >= ridge3[x]:
                r = rng.random()
                if r < .17:
                    color = GRASS_D
                elif r < .22:
                    color = GRASS_L
                else:
                    color = GRASS
                if y > 45 and (math.sin(x * .15) + math.sin(y * .5 + x * .05)) > 1.15:
                    color = INDIGO
            row.append(color)
        grid.append(row)

    img = tk.PhotoImage(width=COLS, height=ROWS)
    img.put(" ".join("{" + " ".join(r) + "}" for r in grid))
    return img.zoom(PIXEL, PIXEL)
