import os
import time
import math
import random
import tkinter as tk
from .config import *
from .sprites import SPRITE_DATA
from .background import build_background
from .audio_manager import AudioManager
from .effects import EffectsManager
from .animation_manager import CreatureAnimation, AttackSequence, BattleAnimationState

class BattleGame:
    def __init__(self, root):
        self.root = root
        root.title("Pixel Monsters — Battle Arena")
        root.resizable(False, False)

        # 16:9 Viewport matching reference video
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=INK, highlightthickness=0)
        self.canvas.pack()

        # Audio Manager
        self.audio = AudioManager.get_instance()
        self.effects = EffectsManager()

        # Load background and sprites once
        self.bg = build_background()
        self.load_sprites()

        # Battle state
        self.player = self.new_monster(name_pref="Thornquill")
        self.enemy = self.new_monster(exclude=self.player["name"], name_pref="Emberhorn")
        self.player_hp = self.player["hp"]
        self.enemy_hp = self.enemy["hp"]
        self.potions = 3

        # Creature animation controllers
        # Player (Thornquill) at lower-left facing right
        self.anim_player = CreatureAnimation(self.player["name"], base_x=370, base_y=590, facing="right")
        # Enemy (Emberhorn) at upper-right facing left
        self.anim_enemy = CreatureAnimation(self.enemy["name"], base_x=950, base_y=430, facing="left")

        self.active_sequence = None
        self.busy = False
        self.cursor = 0
        self.message = None

        # Time tracking for 60 FPS update loop
        self.last_time = time.time()
        self.start_time = time.time()

        # Bindings
        root.bind("<Escape>", lambda event: self.root.destroy())
        root.bind("<Key>", self.on_key)

        # Start background music
        self.audio.play_music("battle_theme", loop=True, fade_ms=600)

        # Initial encounter message
        self.say(f"A wild {self.enemy['name']} appeared!", 1400, self.show_menu)

        # Start continuous animation and render loop
        self.update_loop()

    # ------------------------------------------------------------------ data

    def new_monster(self, exclude=None, name_pref=None):
        options = [m for m in MONSTERS if m["name"] != exclude]
        if name_pref and any(m["name"] == name_pref for m in options):
            mon = next(m for m in options if m["name"] == name_pref).copy()
        else:
            mon = random.choice(options).copy()

        mon["moves"] = list(mon["moves"])
        mon["max_pp"] = [max(8, 40 - dmg) for _, dmg in mon["moves"]]
        mon["pp"] = list(mon["max_pp"])
        return mon

    # --------------------------------------------------------------- sprites

    def load_sprites(self):
        """Load base sprites and pose variations once into PhotoImages."""
        self.sprites = {}
        self.icons = {}
        self.flames = []
        zoom_map = {m["name"]: m["zoom"] for m in MONSTERS}

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sprites_dir = os.path.join(base_dir, "assets", "sprites")

        for m in MONSTERS:
            name = m["name"]
            zm = zoom_map[name]
            self.sprites[name] = {}

            # Load pose variations if available on disk
            poses = ["idle", "lunge", "roar", "stomp", "hurt"]
            for pose in poses:
                self.sprites[name][pose] = {}
                for facing in ("left", "right"):
                    img_path = os.path.join(sprites_dir, f"{name}_{pose}_{facing}.png")
                    if os.path.exists(img_path):
                        try:
                            raw = tk.PhotoImage(file=img_path)
                            self.sprites[name][pose][facing] = raw.zoom(zm, zm)
                        except Exception:
                            self.sprites[name][pose][facing] = None

            # Fallback to base SPRITE_DATA for any missing pose
            base_l = tk.PhotoImage(data=SPRITE_DATA[name]["left"])
            base_r = tk.PhotoImage(data=SPRITE_DATA[name]["right"])
            base_l_zoomed = base_l.zoom(zm, zm)
            base_r_zoomed = base_r.zoom(zm, zm)

            for pose in poses:
                if facing not in self.sprites[name][pose] or not self.sprites[name][pose].get("left"):
                    self.sprites[name][pose]["left"] = base_l_zoomed
                if facing not in self.sprites[name][pose] or not self.sprites[name][pose].get("right"):
                    self.sprites[name][pose]["right"] = base_r_zoomed

            # HUD icons (subsampled)
            k = 2 if max(base_l.width(), base_l.height()) > 66 else 1
            self.icons[name] = {
                "left": base_l.subsample(k) if k > 1 else base_l,
                "right": base_r.subsample(k) if k > 1 else base_r,
            }

        # Animated horn flames for Emberhorn
        for i in range(4):
            fl_left_path = os.path.join(sprites_dir, f"Emberhorn_flame_{i}_left.png")
            fl_right_path = os.path.join(sprites_dir, f"Emberhorn_flame_{i}_right.png")
            if os.path.exists(fl_left_path) and os.path.exists(fl_right_path):
                try:
                    f_l = tk.PhotoImage(file=fl_left_path).zoom(2, 2)
                    f_r = tk.PhotoImage(file=fl_right_path).zoom(2, 2)
                    self.flames.append({"left": f_l, "right": f_r})
                except Exception:
                    pass

    # ------------------------------------------------------------- 60 FPS loop

    def update_loop(self):
        """Continuous non-blocking frame update and rendering loop (~60 FPS)."""
        now = time.time()
        dt = min(0.05, now - self.last_time)
        self.last_time = now
        elapsed = now - self.start_time

        # Update idle bobbing and effects
        self.anim_player.update_idle(elapsed)
        self.anim_player.update_effects(dt)
        self.anim_enemy.update_idle(elapsed)
        self.anim_enemy.update_effects(dt)

        # Update visual effects and particles
        self.effects.update(dt)

        # Update combat animation sequence if active
        if self.active_sequence:
            self.active_sequence.update(dt)
            if self.active_sequence.is_finished:
                self.active_sequence = None

        # Render frame
        self.render()

        # Schedule next tick (~16ms)
        self.root.after(16, self.update_loop)

    # -------------------------------------------------------------- rendering

    def render(self):
        c = self.canvas
        c.delete("all")

        # 1. Screen shake camera offset
        ox, oy = self.effects.screen_shake.get_offset()

        # 2. Background
        c.create_image(ox, oy, image=self.bg, anchor="nw")

        # 3. Ground Shadows
        # Enemy ground shadow
        es_scale = 1.0 - abs(self.anim_enemy.recoil_y) * 0.02
        c.create_oval(ox + 950 - 145 * es_scale, oy + 435 - 32 * es_scale,
                      ox + 950 + 145 * es_scale, oy + 435 + 32 * es_scale,
                      fill="#3a3875", outline="")

        # Player ground shadow
        ps_scale = 1.0 - abs(self.anim_player.recoil_y) * 0.02
        c.create_oval(ox + 370 - 140 * ps_scale, oy + 595 - 30 * ps_scale,
                      ox + 370 + 140 * ps_scale, oy + 595 + 30 * ps_scale,
                      fill="#3a3875", outline="")

        # 4. Draw Creatures with active poses
        self.draw_creature(self.anim_enemy, self.enemy, ox, oy)
        self.draw_creature(self.anim_player, self.player, ox, oy)

        # 5. Visual particles, projectiles, explosions, starbursts
        self.effects.render(c, ox, oy)

        # 6. HUD Panels (fixed UI, unaffected by screen shake)
        self.hud_enemy()
        self.hud_player()

        # 7. Action Ribbon / Battle Menu
        if self.message is not None:
            self.draw_message_box(self.message)
        else:
            self.draw_menu()

    def draw_creature(self, anim, monster, ox, oy):
        c = self.canvas
        name = monster["name"]
        facing = anim.facing
        pose = anim.pose

        # Get appropriate pose sprite with fallback
        sprite_dict = self.sprites.get(name, {})
        pose_dict = sprite_dict.get(pose, sprite_dict.get("idle", {}))
        img = pose_dict.get(facing, sprite_dict.get("idle", {}).get(facing))

        cx = anim.current_x + ox
        cy = anim.current_y + oy

        # Draw main creature sprite
        if img:
            c.create_image(cx, cy, image=img, anchor="s")

        # If Emberhorn, draw animated horn flame layer on top
        if name == "Emberhorn" and self.flames and anim.faint_progress <= 0:
            fl_idx = anim.horn_flame_frame % len(self.flames)
            fl_img = self.flames[fl_idx].get(facing)
            if fl_img:
                c.create_image(cx, cy, image=fl_img, anchor="s")

        # Hit flash tint overlay
        if anim.flash_color and anim.flash_timer > 0:
            # White / red flash box silhouette
            c.create_oval(cx - 70, cy - 120, cx + 70, cy - 10, outline=anim.flash_color, width=3)

    def health_bar(self, x, y, width, height, current_hp, damage_hp, maximum):
        c = self.canvas
        # Frame
        c.create_rectangle(x, y, x + width, y + height, fill="#201a2c", outline="#201a2c", width=2)

        cur_ratio = max(0.0, min(1.0, current_hp / maximum))
        dmg_ratio = max(0.0, min(1.0, damage_hp / maximum))

        # Red/orange catchup bar (damage section)
        if dmg_ratio > cur_ratio:
            c.create_rectangle(x + 2 + (width - 4) * cur_ratio, y + 2,
                               x + 2 + (width - 4) * dmg_ratio, y + height - 2,
                               fill="#e8473f", outline="")

        # Foreground HP bar color
        color = "#5ecc46" if cur_ratio > 0.5 else "#f3d34a" if cur_ratio > 0.2 else "#e8473f"

        if cur_ratio > 0:
            c.create_rectangle(x + 2, y + 2, x + 2 + (width - 4) * cur_ratio, y + height - 2,
                               fill=color, outline="")

    def hp_badge(self, x, y):
        c = self.canvas
        c.create_rectangle(x, y, x + 44, y + 20, fill=PURPLE, outline=INK, width=2)
        c.create_text(x + 22, y + 10, text="HP", font=(FONT, 11, "bold"), fill=LAV)

    def hud_enemy(self):
        c = self.canvas
        # Top-left card
        x1, y1, x2, y2 = 16, 16, 452, 132
        c.create_polygon(x1, y1, x2 - 24, y1, x2, y1 + 36, x2, y2, x1, y2,
                         fill=LAV, outline=INK, width=3)
        c.create_line(x1 + 4, y1 + 4, x2 - 24, y1 + 4, fill=LAV_D, width=2)
        c.create_line(356, y1 + 2, 356, y2 - 2, fill=INK, width=2)

        # Creature Name & Level
        c.create_text(32, 42, text=self.enemy["name"].upper(), anchor="w",
                      font=(FONT, 18, "bold"), fill=INK)
        c.create_text(344, 42, text="L12", anchor="e",
                      font=(FONT, 14, "bold"), fill="#5a4a78")

        # Health display
        cur_hp = self.enemy_hp
        dmg_hp = self.enemy_hp
        if self.active_sequence and self.active_sequence.defender == self.anim_enemy:
            cur_hp, dmg_hp = self.active_sequence.get_displayed_hp()

        self.hp_badge(46, 64)
        self.health_bar(100, 64, 244, 20, cur_hp, dmg_hp, self.enemy["hp"])

        # Numbers
        disp_num = int(round(cur_hp))
        c.create_text(344, 106, text=f"{disp_num}/{self.enemy['hp']}", anchor="e",
                      font=(FONT, 14, "bold"), fill=INK)

        # Enemy icon
        c.create_image(404, 74, image=self.icons[self.enemy["name"]]["left"], anchor="center")

    def hud_player(self):
        c = self.canvas
        # Mirrored card with angled arrow on left
        x1, y1, x2, y2 = 800, 442, 1264, 564
        c.create_polygon(x1 + 30, y1, x2, y1, x2, y2, x1, y2, x1 + 30, y1 + 55,
                         fill=LAV, outline=INK, width=3)
        c.create_line(x1 + 34, y1 + 4, x2 - 4, y1 + 4, fill=LAV_D, width=2)
        c.create_line(900, y1 + 2, 900, y2 - 2, fill=INK, width=2)

        # Player icon
        c.create_image(852, 503, image=self.icons[self.player["name"]]["right"], anchor="center")

        # Creature Name & Level
        c.create_text(916, 468, text=self.player["name"].upper(), anchor="w",
                      font=(FONT, 18, "bold"), fill=INK)
        c.create_text(1248, 468, text="L15", anchor="e",
                      font=(FONT, 14, "bold"), fill="#5a4a78")

        # Health display
        cur_hp = self.player_hp
        dmg_hp = self.player_hp
        if self.active_sequence and self.active_sequence.defender == self.anim_player:
            cur_hp, dmg_hp = self.active_sequence.get_displayed_hp()

        self.hp_badge(940, 488)
        self.health_bar(994, 488, 254, 20, cur_hp, dmg_hp, self.player["hp"])

        # Thin blue EXP bar
        c.create_rectangle(994, 513, 1248, 518, fill=INK, outline=INK)
        c.create_rectangle(994, 514, 1150, 517, fill="#4a90e8", outline="")

        # Numbers
        disp_num = int(round(cur_hp))
        c.create_text(1248, 538, text=f"{disp_num}/{self.player['hp']}", anchor="e",
                      font=(FONT, 14, "bold"), fill=INK)

    # ------------------------------------------------------------- battle menu

    def draw_message_box(self, text):
        """Clean cinematic message ribbon at the bottom during combat actions."""
        c = self.canvas
        # Ribbon background
        c.create_rectangle(24, 584, 1256, 704, fill=INK, outline="#3b3052", width=3)
        c.create_rectangle(28, 588, 1252, 700, fill="#231c2b", outline=LAV_D, width=2)
        c.create_text(56, 644, text=text, anchor="w", font=(FONT, 22, "bold"), fill=LAV, width=1160)

    def draw_menu(self):
        """2x2 Move Grid + Actions + Move Info Box."""
        c = self.canvas
        # Left command panel
        c.create_rectangle(24, 576, 880, 708, fill=INK, outline="#3b3052", width=3)
        c.create_rectangle(28, 580, 876, 704, fill="#231c2b", outline=LAV_D, width=2)

        # 2x2 Move choices
        cols = [74, 460]
        rows = [612, 656]

        for i, (name, _) in enumerate(self.player["moves"]):
            x, y = cols[i % 2], rows[i // 2]
            tag = f"mv{i}"
            empty = self.player["pp"][i] <= 0

            # Selection cursor
            if i == self.cursor:
                c.create_polygon(x - 26, y - 10, x - 26, y + 10, x - 12, y,
                                 fill="#f0a830", outline="#ffe08a", tags=(tag,))
                c.create_text(x, y, text=name, anchor="w", font=(FONT, 20, "bold"),
                              fill="#ffffff", tags=(tag,))
            else:
                c.create_text(x, y, text=name, anchor="w", font=(FONT, 20, "bold"),
                              fill="#6f6485" if empty else LAV, tags=(tag,))

            c.tag_bind(tag, "<Button-1>", lambda e, idx=i: self.choose_move(idx))
            c.tag_bind(tag, "<Enter>", lambda e, idx=i: self.hover(idx))

        # Command shortcuts row at bottom
        cmds = [
            ("[B] BAG x%d" % self.potions, 74, self.use_potion),
            ("[S] SWITCH", 340, self.switch_monster),
            ("[R] RUN", 580, self.run_away),
        ]
        for n, (label, x, action) in enumerate(cmds):
            tag = f"cmd{n}"
            c.create_text(x, 690, text=label, anchor="w", font=(FONT, 12, "bold"),
                          fill=LAV_D, tags=(tag,))
            c.tag_bind(tag, "<Button-1>", lambda e, a=action: a())

        # Right move info panel
        self.draw_info_box()

    def draw_info_box(self):
        c = self.canvas
        i = self.cursor
        name, power = self.player["moves"][i]
        uses, max_uses = self.player["pp"][i], self.player["max_pp"][i]

        # Info Box Card
        x1, y1, x2, y2 = 896, 576, 1256, 708
        c.create_rectangle(x1, y1, x2, y2, fill=INK, outline="#3b3052", width=3)
        c.create_rectangle(x1 + 4, y1 + 4, x2 - 4, y2 - 4, fill="#231c2b", outline=LAV_D, width=2)

        c.create_text(x1 + 176, y1 + 32, text=f"USES: {uses}/{max_uses}",
                      font=(FONT, 16, "bold"), fill=LAV)

        # Power badge
        c.create_rectangle(x1 + 24, y1 + 60, x1 + 160, y1 + 104,
                           fill="#f0a830", outline="#ffe08a", width=2)
        c.create_text(x1 + 92, y1 + 82, text=f"POW {power}",
                      font=(FONT, 14, "bold"), fill=INK)

        # Type badge
        mtype = self.player["type"]
        txt_col = INK if mtype in DARK_TEXT_TYPES else "#ffffff"
        c.create_rectangle(x1 + 180, y1 + 60, x1 + 336, y1 + 104,
                           fill=TYPE_COLORS.get(mtype, "#4caf50"), outline="#ffffff", width=2)
        c.create_text(x1 + 258, y1 + 82, text=mtype.upper(),
                      font=(FONT, 14, "bold"), fill=txt_col)

    # -------------------------------------------------------------- controls

    def hover(self, idx):
        if self.busy or idx == self.cursor:
            return
        self.cursor = idx
        self.audio.play_sfx("select", channel_name="ui")

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
            self.audio.play_sfx("confirm", channel_name="ui")
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
            self.audio.play_sfx("select", channel_name="ui")

    # ------------------------------------------------------------ game flow

    def say(self, text, delay, next_step):
        self.busy = True
        self.message = text
        if delay > 0 and next_step:
            self.root.after(delay, next_step)

    def show_menu(self):
        self.busy = False
        self.message = None

    def choose_move(self, idx):
        if self.busy:
            return

        pp = self.player["pp"]
        if any(pp):
            if pp[idx] <= 0:
                self.say("No uses left for that move!", 900, self.show_menu)
                return
            pp[idx] -= 1
            move_name, base_pwr = self.player["moves"][idx]
        else:
            move_name, base_pwr = "Struggle", 10

        self.busy = True
        damage = random.randint(max(5, base_pwr - 5), base_pwr + 4)
        old_hp = self.enemy_hp
        self.enemy_hp = max(0, self.enemy_hp - damage)

        # Set battle message
        self.message = f"{self.player['name']} used {move_name}!"

        # Launch video-matched attack animation sequence
        self.active_sequence = AttackSequence(
            attacker_anim=self.anim_player,
            defender_anim=self.anim_enemy,
            move_name=move_name,
            move_type=self.player["type"],
            damage=damage,
            old_def_hp=old_hp,
            new_def_hp=self.enemy_hp,
            max_def_hp=self.enemy["hp"],
            audio_mgr=self.audio,
            effects_mgr=self.effects,
            on_complete=self.after_player_attack
        )

    def after_player_attack(self):
        if self.enemy_hp <= 0:
            self.audio.play_sfx("faint", channel_name="damage")
            self.audio.play_sfx("victory", channel_name="jingle")
            self.say(f"{self.enemy['name']} fainted! Victory!", 1600, self.next_enemy)
        else:
            self.say(f"It dealt {self.enemy_hp} damage!", 600, self.enemy_turn)

    def enemy_turn(self):
        # Choose AI move
        move_name, base_pwr = random.choice(self.enemy["moves"])
        damage = random.randint(max(6, base_pwr - 6), base_pwr + 3)
        old_hp = self.player_hp
        self.player_hp = max(0, self.player_hp - damage)

        self.message = f"Wild {self.enemy['name']} used {move_name}!"

        # Launch video-matched enemy attack sequence (e.g. fire roar + wave + explosion)
        self.active_sequence = AttackSequence(
            attacker_anim=self.anim_enemy,
            defender_anim=self.anim_player,
            move_name=move_name,
            move_type=self.enemy["type"],
            damage=damage,
            old_def_hp=old_hp,
            new_def_hp=self.player_hp,
            max_def_hp=self.player["hp"],
            audio_mgr=self.audio,
            effects_mgr=self.effects,
            on_complete=self.after_enemy_attack
        )

    def after_enemy_attack(self):
        if self.player_hp <= 0:
            self.audio.play_sfx("faint", channel_name="damage")
            self.audio.play_sfx("defeat", channel_name="jingle")
            self.say(f"{self.player['name']} fainted! Partner incoming!", 1600, self.revive_player)
        else:
            self.show_menu()

    def use_potion(self):
        if self.busy:
            return
        if self.potions <= 0:
            self.say("Your bag is empty!", 800, self.show_menu)
            return
        if self.player_hp >= self.player["hp"]:
            self.say("HP is already full!", 800, self.show_menu)
            return

        self.potions -= 1
        healed = min(30, self.player["hp"] - self.player_hp)
        self.player_hp += healed
        self.audio.play_sfx("potion", channel_name="ui")
        # Sparkle effect on player
        self.effects.spawn_starburst_impact(self.anim_player.current_x, self.anim_player.current_y - 60, count=2)
        self.say(f"Used a potion! Restored {healed} HP. Potions left: {self.potions}", 1000, self.enemy_turn)

    def switch_monster(self):
        if self.busy:
            return
        old_name = self.player["name"]
        self.player = self.new_monster(exclude=self.enemy["name"])
        self.player_hp = self.player["hp"]
        self.anim_player = CreatureAnimation(self.player["name"], base_x=370, base_y=590, facing="right")
        self.cursor = 0
        self.audio.play_sfx("confirm", channel_name="ui")
        self.say(f"{old_name} switched out! {self.player['name']} joins the battle!", 1100, self.enemy_turn)

    def run_away(self):
        if self.busy:
            return
        if random.random() < 0.65:
            self.audio.play_sfx("confirm", channel_name="ui")
            self.say("Got away safely! A new wild monster appears.", 1200, self.next_enemy)
        else:
            self.say("Couldn't escape! Wild monster attacks!", 900, self.enemy_turn)

    def next_enemy(self):
        self.enemy = self.new_monster(exclude=self.player["name"])
        self.enemy_hp = self.enemy["hp"]
        self.anim_enemy = CreatureAnimation(self.enemy["name"], base_x=950, base_y=430, facing="left")
        self.say(f"A new wild {self.enemy['name']} appeared!", 1200, self.show_menu)

    def revive_player(self):
        self.player = self.new_monster(exclude=self.enemy["name"])
        self.player_hp = self.player["hp"]
        self.anim_player = CreatureAnimation(self.player["name"], base_x=370, base_y=590, facing="right")
        self.cursor = 0
        self.say(f"Go, {self.player['name']}! The battle continues!", 1200, self.show_menu)
