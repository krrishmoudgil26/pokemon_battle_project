import tkinter as tk
import random
from .config import *
from .sprites import SPRITE_DATA
from .background import build_background

class BattleGame:

    def __init__(self, root):

        self.root = root

        root.title("Pixel Monsters — Battle Arena")

        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=INK, highlightthickness=0)

        self.canvas.pack()

        self.bg = build_background()

        self.load_sprites()

        self.player = self.new_monster()

        self.enemy = self.new_monster(exclude=self.player["name"])

        self.player_hp = self.player["hp"]

        self.enemy_hp = self.enemy["hp"]

        self.potions = 3

        self.busy = False

        self.cursor = 0

        self.message = None

        root.bind("<Escape>", lambda event: self.root.destroy())

        root.bind("<Key>", self.on_key)

        self.say("A wild " + self.enemy["name"] + " appeared!", 1200, self.show_menu)

    # ------------------------------------------------------------------ data

    def new_monster(self, exclude=None):

        options = [m for m in MONSTERS if m["name"] != exclude]

        mon = random.choice(options).copy()

        mon["moves"] = list(mon["moves"])

        mon["max_pp"] = [max(8, 40 - dmg) for _, dmg in mon["moves"]]

        mon["pp"] = list(mon["max_pp"])

        return mon

    # --------------------------------------------------------------- drawing

    def load_sprites(self):

        """Decode the embedded PNGs once; keep references so Tk doesn't garbage-collect them."""

        self.sprites, self.icons = {}, {}

        zoom = {m["name"]: m["zoom"] for m in MONSTERS}

        for name, d in SPRITE_DATA.items():

            left = tk.PhotoImage(data=d["left"])

            right = tk.PhotoImage(data=d["right"])

            self.sprites[name] = {"left": left.zoom(zoom[name]), "right": right.zoom(zoom[name])}

            k = 2 if max(left.width(), left.height()) > 66 else 1      # fit the small HUD icon box

            self.icons[name] = {"left": left.subsample(k) if k > 1 else left,

                                "right": right.subsample(k) if k > 1 else right}

    def draw_monster(self, cx, bottom, monster, facing):

        self.canvas.create_image(cx, bottom, image=self.sprites[monster["name"]][facing], anchor="s")

    def draw_icon(self, cx, cy, monster, facing):

        self.canvas.create_image(cx, cy, image=self.icons[monster["name"]][facing], anchor="center")

    def health_bar(self, x, y, width, height, hp, maximum):

        c = self.canvas

        c.create_rectangle(x, y, x + width, y + height, fill=INK, outline=INK)

        ratio = max(0, hp / maximum)

        color = "#6fd44a" if ratio > .5 else "#f3d34a" if ratio > .2 else "#e85b4b"

        if ratio > 0:

            c.create_rectangle(x + 2, y + 2, x + 2 + (width - 4) * ratio, y + height - 2, fill=color, outline="")

    def hp_badge(self, x, y):

        c = self.canvas

        c.create_rectangle(x, y, x + 46, y + 20, fill=PURPLE, outline=INK, width=2)

        c.create_text(x + 23, y + 10, text="HP", font=(FONT, 11, "bold"), fill=LAV)

    def hud_enemy(self):

        c = self.canvas

        # angled panel with a little dark tail, top-left

        c.create_polygon(8, 10, 412, 10, 412, 62, 436, 98, 8, 98, fill=LAV, outline=INK, width=3)

        c.create_polygon(396, 78, 436, 98, 396, 98, fill=INK, outline=INK)

        c.create_line(10, 14, 410, 14, fill=LAV_D, width=2)

        c.create_line(330, 12, 330, 97, fill=INK, width=3)

        c.create_text(20, 30, text=self.enemy["name"].upper(), anchor="w", font=(FONT, 18, "bold"), fill=INK)

        c.create_text(318, 30, text="L12", anchor="e", font=(FONT, 13, "bold"), fill="#5a4a78")

        self.hp_badge(44, 46)

        self.health_bar(98, 46, 220, 18, self.enemy_hp, self.enemy["hp"])

        c.create_text(318, 80, text=f"{self.enemy_hp}/{self.enemy['hp']}", anchor="e",

                      font=(FONT, 14, "bold"), fill=INK)

        self.draw_icon(371, 55, self.enemy, "left")

    def hud_player(self):

        c = self.canvas

        # mirrored angled panel, bottom-right

        c.create_polygon(542, 308, 948, 308, 948, 398, 522, 398, 542, 360, fill=LAV, outline=INK, width=3)

        c.create_polygon(524, 378, 560, 398, 524, 398, fill=INK, outline=INK)

        c.create_line(546, 312, 944, 312, fill=LAV_D, width=2)

        c.create_line(632, 310, 632, 396, fill=INK, width=3)

        c.create_text(644, 328, text=self.player["name"].upper(), anchor="w", font=(FONT, 18, "bold"), fill=INK)

        c.create_text(938, 328, text="L15", anchor="e", font=(FONT, 13, "bold"), fill="#5a4a78")

        self.hp_badge(668, 346)

        self.health_bar(722, 346, 216, 18, self.player_hp, self.player["hp"])

        # thin XP bar under the HP bar

        c.create_rectangle(722, 368, 938, 374, fill=INK, outline=INK)

        c.create_rectangle(722, 369, 812, 373, fill="#4a90e8", outline="")

        c.create_text(938, 386, text=f"{self.player_hp}/{self.player['hp']}", anchor="e",

                      font=(FONT, 14, "bold"), fill=INK)

        self.draw_icon(587, 353, self.player, "right")

    def info_box(self):

        """Right-hand box: USES counter + power / type badges for the highlighted move."""

        c = self.canvas

        i = self.cursor

        name, power = self.player["moves"][i]

        uses, max_uses = self.player["pp"][i], self.player["max_pp"][i]

        c.create_rectangle(712, 420, 946, 532, fill="#3b3052", outline="#8a7bb0", width=4)

        c.create_rectangle(719, 427, 939, 525, fill="#3b3052", outline=LAV_D, width=2)

        c.create_text(829, 452, text=f"USES: {uses}/{max_uses}", font=(FONT, 16, "bold"), fill=LAV)

        c.create_rectangle(726, 474, 816, 512, fill="#f0a830", outline="#ffe08a", width=3)

        c.create_text(771, 493, text=f"POW {power}", font=(FONT, 12, "bold"), fill=INK)

        mtype = self.player["type"]

        txt_col = INK if mtype in DARK_TEXT_TYPES else "#ffffff"

        c.create_rectangle(824, 474, 934, 512, fill=TYPE_COLORS[mtype], outline="#ffffff", width=3)

        c.create_text(879, 493, text=mtype.upper(), font=(FONT, 14, "bold"), fill=txt_col)

    def menu(self):

        """Move list (2x2 with a triangle cursor) + small command row."""

        c = self.canvas

        cols = [78, 392]

        rows = [440, 480]

        for i, (name, _) in enumerate(self.player["moves"]):

            x, y = cols[i % 2], rows[i // 2]

            tag = f"mv{i}"

            c.create_rectangle(x - 30, y - 18, x + 270, y + 18, fill=INK, outline=INK, tags=(tag,))

            empty = self.player["pp"][i] <= 0

            c.create_text(x, y, text=name, anchor="w", font=(FONT, 20, "bold"),

                          fill="#6f6485" if empty else LAV, tags=(tag,))

            if i == self.cursor:

                c.create_polygon(x - 26, y - 11, x - 26, y + 11, x - 11, y, fill=LAV, outline=LAV, tags=(tag,))

            c.tag_bind(tag, "<Button-1>", lambda e, idx=i: self.choose_move(idx))

            c.tag_bind(tag, "<Enter>", lambda e, idx=i: self.hover(idx))

        cmds = [

            ("B: BAG x%d" % self.potions, 78, self.use_potion),

            ("S: SWITCH", 250, self.switch_monster),

            ("R: RUN", 392, self.run_away),

        ]

        for n, (label, x, action) in enumerate(cmds):

            tag = f"cmd{n}"

            c.create_rectangle(x - 6, 506, x + 150, 534, fill=INK, outline=INK, tags=(tag,))

            c.create_text(x, 520, text=label, anchor="w", font=(FONT, 12, "bold"), fill=LAV_D, tags=(tag,))

            c.tag_bind(tag, "<Button-1>", lambda e, a=action: a())

    def draw_scene(self, message=None):

        self.message = message

        c = self.canvas

        c.delete("all")

        c.create_image(0, 0, image=self.bg, anchor="nw")

        # enemy (top-right, faces left) and player (bottom-left, faces right)

        c.create_oval(630, 250, 860, 278, fill=INDIGO_D, outline="")

        self.draw_monster(745, 268, self.enemy, "left")

        c.create_oval(165, 366, 415, 402, fill=INDIGO_D, outline="")

        self.draw_monster(290, 388, self.player, "right")

        self.hud_enemy()

        self.hud_player()

        # bottom menu panel

        c.create_rectangle(0, UI_TOP, WIDTH, HEIGHT, fill=INK, outline=INK)

        c.create_line(0, UI_TOP + 2, WIDTH, UI_TOP + 2, fill="#3b3052", width=2)

        if message is None:

            self.menu()

        else:

            c.create_text(60, 430, text=message, anchor="nw", font=(FONT, 20, "bold"), fill=LAV, width=610)

        self.info_box()

    # -------------------------------------------------------------- controls

    def hover(self, idx):

        if self.busy or idx == self.cursor:

            return

        self.cursor = idx

        self.root.after_idle(self.draw_scene)

    def on_key(self, event):

        if self.busy:

            return

        k = event.keysym.lower()

        i = self.cursor

        new = i

        if k == "left" and i % 2 == 1:

            new = i - 1

        elif k == "right" and i % 2 == 0:

            new = i + 1

        elif k == "up" and i >= 2:

            new = i - 2

        elif k == "down" and i < 2:

            new = i + 2

        elif k in ("return", "space", "z"):

            self.choose_move(i)

            return

        elif k == "b":

            self.use_potion()

            return

        elif k == "s":

            self.switch_monster()

            return

        elif k == "r":

            self.run_away()

            return

        if new != i:

            self.cursor = new

            self.draw_scene()

    # ------------------------------------------------------------ game flow

    def say(self, text, delay, next_step):

        """Show a message in the dark panel, then continue after `delay` ms."""

        self.busy = True

        self.draw_scene(text)

        self.root.after(delay, next_step)

    def show_menu(self):

        self.busy = False

        self.draw_scene()

    def choose_move(self, idx):

        if self.busy:

            return

        pp = self.player["pp"]

        if any(pp):

            if pp[idx] <= 0:

                self.say("No uses left for that move!", 800, self.show_menu)

                return

            pp[idx] -= 1

            move, base = self.player["moves"][idx]

        else:

            move, base = "Struggle", 10

        damage = random.randint(max(5, base - 5), base + 4)

        self.enemy_hp = max(0, self.enemy_hp - damage)

        if self.enemy_hp <= 0:

            self.say(f"{self.player['name']} used {move}! {self.enemy['name']} fainted!", 1300, self.next_enemy)

        else:

            self.say(f"{self.player['name']} used {move}! It dealt {damage} damage!", 1000, self.enemy_turn)

    def enemy_turn(self):

        damage = random.randint(7, 18)

        self.player_hp = max(0, self.player_hp - damage)

        if self.player_hp <= 0:

            self.say(f"{self.player['name']} fainted! New partner incoming!", 1400, self.revive_player)

        else:

            self.say(f"{self.enemy['name']} attacks randomly! -{damage} HP", 1000, self.show_menu)

    def use_potion(self):

        if self.busy:

            return

        if self.potions <= 0:

            self.say("Your bag is empty! Choose another action.", 800, self.show_menu)

            return

        if self.player_hp == self.player["hp"]:

            self.say("HP is already full. Save that potion!", 800, self.show_menu)

            return

        self.potions -= 1

        healed = min(30, self.player["hp"] - self.player_hp)

        self.player_hp += healed

        self.say(f"Used a potion! Restored {healed} HP. Potions left: {self.potions}", 900, self.enemy_turn)

    def switch_monster(self):

        if self.busy:

            return

        old_name = self.player["name"]

        self.player = self.new_monster(exclude=self.enemy["name"])

        self.player_hp = self.player["hp"]

        self.cursor = 0

        self.say(f"{old_name} switched out! {self.player['name']} joins the battle!", 900, self.enemy_turn)

    def run_away(self):

        if self.busy:

            return

        if random.random() < .65:

            self.say("You escaped safely! A new wild monster appears.", 1100, self.next_enemy)

        else:

            self.say("Couldn't escape! The wild monster gets a turn.", 700, self.enemy_turn)

    def next_enemy(self):

        self.enemy = self.new_monster(exclude=self.player["name"])

        self.enemy_hp = self.enemy["hp"]

        self.say(f"A new wild {self.enemy['name']} appeared!", 1100, self.show_menu)

    def revive_player(self):

        self.player = self.new_monster(exclude=self.enemy["name"])

        self.player_hp = self.player["hp"]

        self.cursor = 0

        self.say(f"Go, {self.player['name']}! The battle continues!", 1100, self.show_menu)
