import math
import time
import random

def ease_in_out(t):
    return t * t * (3.0 - 2.0 * t)

def ease_out_quad(t):
    return t * (2.0 - t)

def ease_in_quad(t):
    return t * t

def ease_out_back(t, s=1.70158):
    t -= 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0

class BattleAnimationState:
    IDLE = "IDLE"
    WINDUP = "WINDUP"
    LUNGE = "LUNGE"
    PROJECTILE = "PROJECTILE"
    IMPACT = "IMPACT"
    HP_DRAIN = "HP_DRAIN"
    RECOVERY = "RECOVERY"
    FAINT = "FAINT"

class CreatureAnimation:
    """Tracks continuous idle animation and momentary pose offsets for a creature."""
    def __init__(self, name, base_x, base_y, facing="right"):
        self.name = name
        self.base_x = base_x
        self.base_y = base_y
        self.facing = facing
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.recoil_x = 0.0
        self.recoil_y = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.flash_timer = 0.0
        self.flash_color = None
        self.faint_progress = 0.0  # 0.0 = visible, 1.0 = fully sunken
        self.pose = "idle"         # "idle", "lunge", "roar", "stomp", "hurt"
        self.horn_flame_frame = 0

    def update_idle(self, elapsed_time):
        """Subtle idle breathing bob and flame animation."""
        if self.faint_progress > 0:
            return

        # Gentle breathing sine wave
        freq = 3.2 if self.name == "Thornquill" else 2.6
        amp = 2.5
        self.offset_y = math.sin(elapsed_time * freq) * amp

        # Animated horn flames (4-frame cycle, ~8 fps)
        self.horn_flame_frame = int(elapsed_time * 8.0) % 4

    def update_effects(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_color = None

        # Decay recoil smoothly back to zero
        self.recoil_x *= (0.85 ** (dt * 60.0))
        self.recoil_y *= (0.85 ** (dt * 60.0))

    def trigger_flash(self, color="#ffffff", duration=0.18):
        self.flash_color = color
        self.flash_timer = duration

    def trigger_recoil(self, dist_x=22.0, dist_y=-6.0):
        # Recoil direction depends on facing
        dir_mult = -1.0 if self.facing == "right" else 1.0
        self.recoil_x = dist_x * dir_mult
        self.recoil_y = dist_y
        self.pose = "hurt"

    @property
    def current_x(self):
        return self.base_x + self.offset_x + self.recoil_x

    @property
    def current_y(self):
        # Sinking down if fainted
        sink = self.faint_progress * 80.0
        return self.base_y + self.offset_y + self.recoil_y + sink

class AttackSequence:
    """Orchestrates the 5-phase attack sequence matching the reference video."""
    def __init__(self, attacker_anim, defender_anim, move_name, move_type, damage,
                 old_def_hp, new_def_hp, max_def_hp, audio_mgr, effects_mgr, on_complete):
        self.attacker = attacker_anim
        self.defender = defender_anim
        self.move_name = move_name
        self.move_type = move_type
        self.damage = damage
        self.old_def_hp = old_def_hp
        self.new_def_hp = new_def_hp
        self.max_def_hp = max_def_hp
        self.audio = audio_mgr
        self.effects = effects_mgr
        self.on_complete = on_complete

        self.state = BattleAnimationState.WINDUP
        self.phase_time = 0.0
        self.is_finished = False

        # Phase durations in seconds (snappy and video-matched)
        self.windup_dur = 0.75
        self.lunge_dur = 0.45
        self.impact_dur = 0.35
        self.hp_drain_dur = 0.85
        self.recovery_dur = 0.40

        # Start phase A (Windup)
        self.start_windup()

    def start_windup(self):
        self.state = BattleAnimationState.WINDUP
        self.phase_time = 0.0
        is_fire = self.move_type == "Fire" or "Flame" in self.move_name or "Ember" in self.move_name or "Lava" in self.move_name
        is_grass = self.move_type == "Grass" or "Leaf" in self.move_name or "Needle" in self.move_name or "Solar" in self.move_name
        is_ice = self.move_type == "Ice" or "Frost" in self.move_name or "Glacier" in self.move_name or "Snow" in self.move_name

        if is_fire:
            self.attacker.pose = "roar"
            self.audio.play_sfx("fire_charge", channel_name="charge")
        elif is_grass:
            self.attacker.pose = "lunge"
            self.audio.play_sfx("charge_grass", channel_name="charge")
        elif is_ice:
            self.attacker.pose = "roar"
            self.audio.play_sfx("ice_charge", channel_name="charge")
        else:
            self.attacker.pose = "lunge"
            self.audio.play_sfx("charge_grass", channel_name="charge")

    def update(self, dt):
        if self.is_finished:
            return

        self.phase_time += dt

        # ---------------- Phase A: Windup ----------------
        if self.state == BattleAnimationState.WINDUP:
            prog = min(1.0, self.phase_time / self.windup_dur)
            is_fire = self.move_type == "Fire" or "Flame" in self.move_name or "Ember" in self.move_name or "Lava" in self.move_name
            is_grass = self.move_type == "Grass" or "Leaf" in self.move_name or "Needle" in self.move_name or "Solar" in self.move_name
            is_ice = self.move_type == "Ice" or "Frost" in self.move_name

            # Spawn charging aura particles
            if is_fire:
                if random.random() < 0.6:
                    self.effects.spawn_fire_charge(self.attacker.current_x - 15, self.attacker.current_y - 70, count=2)
            elif is_grass:
                if random.random() < 0.6:
                    self.effects.spawn_leaf_windup(self.attacker.current_x, self.attacker.current_y - 50, count=2)
            elif is_ice:
                if random.random() < 0.6:
                    self.effects.spawn_ice_charge(self.attacker.current_x, self.attacker.current_y - 60, count=2)

            if prog >= 1.0:
                self.start_lunge()

        # ---------------- Phase B: Lunge & Projectile ----------------
        elif self.state == BattleAnimationState.LUNGE:
            prog = min(1.0, self.phase_time / self.lunge_dur)
            # Attacker dashes forward slightly
            lunge_dist = 40.0 if self.attacker.facing == "right" else -40.0
            lunge_offset = math.sin(prog * math.pi) * lunge_dist
            self.attacker.offset_x = lunge_offset

            if prog >= 1.0:
                self.start_impact()

        # ---------------- Phase C: Impact ----------------
        elif self.state == BattleAnimationState.IMPACT:
            prog = min(1.0, self.phase_time / self.impact_dur)
            if prog >= 1.0:
                self.start_hp_drain()

        # ---------------- Phase D: HP Drain ----------------
        elif self.state == BattleAnimationState.HP_DRAIN:
            prog = min(1.0, self.phase_time / self.hp_drain_dur)
            if prog >= 1.0:
                self.start_recovery()

        # ---------------- Phase E: Recovery ----------------
        elif self.state == BattleAnimationState.RECOVERY:
            prog = min(1.0, self.phase_time / self.recovery_dur)
            # Glide back to base
            self.attacker.offset_x *= (1.0 - prog)
            if prog >= 1.0:
                self.attacker.offset_x = 0.0
                self.attacker.pose = "idle"
                self.defender.pose = "idle"
                self.is_finished = True
                if self.on_complete:
                    self.on_complete()

    def start_lunge(self):
        self.state = BattleAnimationState.LUNGE
        self.phase_time = 0.0
        is_fire = self.move_type == "Fire" or "Flame" in self.move_name or "Ember" in self.move_name or "Lava" in self.move_name
        is_grass = self.move_type == "Grass" or "Leaf" in self.move_name or "Needle" in self.move_name or "Solar" in self.move_name
        is_ice = self.move_type == "Ice" or "Frost" in self.move_name

        if is_fire:
            self.attacker.pose = "stomp"
            self.audio.play_sfx("fire_blast", channel_name="projectile")
            self.effects.spawn_fire_blast_stream(self.attacker.current_x - 30, self.attacker.current_y - 60,
                                                 self.defender.current_x, self.defender.current_y - 45,
                                                 duration=self.lunge_dur)
        elif is_grass:
            self.attacker.pose = "lunge"
            self.audio.play_sfx("leaf_whoosh", channel_name="projectile")
            self.effects.spawn_leaf_projectile_stream(self.attacker.current_x + 30, self.attacker.current_y - 50,
                                                      self.defender.current_x - 20, self.defender.current_y - 60,
                                                      duration=self.lunge_dur, count=16)
        elif is_ice:
            self.attacker.pose = "lunge"
            self.audio.play_sfx("leaf_whoosh", channel_name="projectile")
            self.effects.spawn_ice_projectile_stream(self.attacker.current_x + 20, self.attacker.current_y - 50,
                                                     self.defender.current_x, self.defender.current_y - 60,
                                                     duration=self.lunge_dur)
        else:
            self.audio.play_sfx("leaf_whoosh", channel_name="projectile")

    def start_impact(self):
        self.state = BattleAnimationState.IMPACT
        self.phase_time = 0.0
        is_fire = self.move_type == "Fire" or "Flame" in self.move_name or "Ember" in self.move_name or "Lava" in self.move_name
        is_grass = self.move_type == "Grass" or "Leaf" in self.move_name or "Needle" in self.move_name or "Solar" in self.move_name
        is_ice = self.move_type == "Ice" or "Frost" in self.move_name

        # Recoil defender
        self.defender.trigger_recoil(dist_x=28.0, dist_y=-8.0)
        self.defender.trigger_flash(color="#ffffff", duration=0.22)

        if is_fire:
            self.effects.screen_shake.trigger(intensity=14.0, duration=0.35)
            self.effects.spawn_explosion(self.defender.current_x, self.defender.current_y - 50)
            self.audio.play_sfx("explosion", channel_name="impact")
            self.audio.play_sfx("damage", channel_name="damage", min_interval_ms=50)
        elif is_grass:
            self.effects.screen_shake.trigger(intensity=9.0, duration=0.25)
            self.effects.spawn_starburst_impact(self.defender.current_x, self.defender.current_y - 60, count=4)
            self.audio.play_sfx("hit_grass", channel_name="impact")
            self.audio.play_sfx("damage", channel_name="damage", min_interval_ms=50)
        elif is_ice:
            self.effects.screen_shake.trigger(intensity=10.0, duration=0.28)
            self.effects.spawn_ice_shatter(self.defender.current_x, self.defender.current_y - 60)
            self.audio.play_sfx("ice_hit", channel_name="impact")
            self.audio.play_sfx("damage", channel_name="damage", min_interval_ms=50)
        else:
            self.effects.screen_shake.trigger(intensity=8.0, duration=0.22)
            self.effects.spawn_physical_impact(self.defender.current_x, self.defender.current_y - 60)
            self.audio.play_sfx("physical_hit", channel_name="impact")
            self.audio.play_sfx("damage", channel_name="damage", min_interval_ms=50)

    def start_hp_drain(self):
        self.state = BattleAnimationState.HP_DRAIN
        self.phase_time = 0.0

    def start_recovery(self):
        self.state = BattleAnimationState.RECOVERY
        self.phase_time = 0.0

    def get_displayed_hp(self):
        """Returns (current_hp_float, damage_catchup_hp_float) during HP drain phase."""
        if self.state in (BattleAnimationState.WINDUP, BattleAnimationState.LUNGE, BattleAnimationState.IMPACT):
            return float(self.old_def_hp), float(self.old_def_hp)
        elif self.state == BattleAnimationState.HP_DRAIN:
            prog = min(1.0, self.phase_time / self.hp_drain_dur)
            # Foreground HP bar drops rapidly
            fg_prog = ease_out_quad(min(1.0, prog * 1.5))
            cur_hp = self.old_def_hp - (self.old_def_hp - self.new_def_hp) * fg_prog
            # Catchup damage bar starts shrinking with a slight lag
            catchup_prog = ease_in_out(max(0.0, (prog - 0.25) / 0.75))
            catchup_hp = self.old_def_hp - (self.old_def_hp - self.new_def_hp) * catchup_prog
            return cur_hp, catchup_hp
        else:
            return float(self.new_def_hp), float(self.new_def_hp)
