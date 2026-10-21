import math
import random
import tkinter as tk
from .config import *

def build_background():

    rng = random.Random(11)

    ridge1 = [17 + 2.5 * math.sin(x * .09 + 1) + 1.5 * math.sin(x * .23 + 3) + rng.uniform(-.8, .8) for x in range(COLS)]

    ridge2 = [24 + 2.5 * math.sin(x * .07 + 2) + 1.5 * math.sin(x * .19) + rng.uniform(-.8, .8) for x in range(COLS)]

    ridge3 = [31 + 2.0 * math.sin(x * .10 + 4) + 1.5 * math.sin(x * .31) + rng.uniform(-1.2, 1.2) for x in range(COLS)]

    pink_clouds = [(10, 9, 24, 10), (108, 8, 18, 13), (100, 17, 14, 7), (70, 18, 10, 4)]

    white_clouds = [(76, 19, 6, 3), (112, 6, 10, 7), (104, 12, 6, 3), (18, 15, 6, 3)]

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

            if y >= UI_ROW:

                row.append(INK)

                continue

            color = SKY

            # clouds

            if in_cloud(x, y, pink_clouds):

                color = PINK

            if in_cloud(x, y, white_clouds):

                color = WHITE

            # dotted haze above the hills

            if color == SKY and 24 <= x <= 105 and 12 <= y <= 19 and (x + y) % 2 == 0 \
                    and rng.random() < (y - 11) / 8:

                color = SKY_DARK

            yy = y + rng.uniform(-.7, .7)

            # layered hills

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

                # soft indigo shadow patches in the foreground

                if y > 38 and (math.sin(x * .15) + math.sin(y * .5 + x * .05)) > 1.15:

                    color = INDIGO

            row.append(color)

        grid.append(row)

    # bottom rows (hidden by the menu) already INK

    for y in range(UI_ROW, ROWS):

        grid[y] = [INK] * COLS

    img = tk.PhotoImage(width=COLS, height=ROWS)

    img.put(" ".join("{" + " ".join(r) + "}" for r in grid))

    return img.zoom(PIXEL, PIXEL)
