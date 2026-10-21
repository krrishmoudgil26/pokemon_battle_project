"""
Visual Effects, Particle System, and Screen Shake for Pixel Monsters Battle Arena.
Provides high-performance procedural pixel-art combat effects, projectiles, and camera dynamics.
"""

import math
import random
import time

class Particle:
    def __init__(self, x, y, vx, vy, lifetime, p_type="spark", color="#ffffff", size=4, gravity=0, friction=0.98, extra=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.p_type = p_type
        self.color = color
        self.size = size
        self.gravity = gravity
        self.friction = friction
        self.extra = extra or {}
        self.angle = self.extra.get("angle", random.uniform(0, math.pi * 2))
        self.rot_speed = self.extra.get("rot_speed", random.uniform(-6, 6))

    def update(self, dt):
        self.lifetime -= dt
        self.vx *= (self.friction ** (dt * 60.0))
        self.vy *= (self.friction ** (dt * 60.0))
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.rot_speed * dt
        return self.lifetime > 0

    @property
    def progress(self):
        """0.0 at birth -> 1.0 at death."""
        return max(0.0, min(1.0, 1.0 - (self.lifetime / self.max_lifetime)))

class ScreenShake:
    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.elapsed = 0.0
        self.frequency = 32.0

    def trigger(self, intensity=8.0, duration=0.25):
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)
        self.elapsed = 0.0

    def update(self, dt):
        if self.elapsed < self.duration:
            self.elapsed += dt
        else:
            self.intensity = 0.0

    def get_offset(self):
        if self.elapsed >= self.duration or self.intensity <= 0:
            return 0, 0
        rem = 1.0 - (self.elapsed / self.duration)
        curr_int = self.intensity * (rem ** 1.5)
        t = self.elapsed * self.frequency
        dx = math.sin(t * 1.7) * curr_int
        dy = math.cos(t * 2.3) * curr_int * 0.7
        return int(round(dx)), int(round(dy))

class EffectsManager:
    def __init__(self):
        self.particles = []
        self.screen_shake = ScreenShake()
        self.projectiles = []
        self.impact_flashes = []

    def clear(self):
        self.particles.clear()
        self.projectiles.clear()
        self.impact_flashes.clear()

    def update(self, dt):
        self.screen_shake.update(dt)
        self.particles = [p for p in self.particles if p.update(dt)]
        self.projectiles = [pj for pj in self.projectiles if pj.update(dt, self)]
        self.impact_flashes = [f for f in self.impact_flashes if f.update(dt)]

    # ----------------- Particle Spawners -----------------

    def spawn_leaf_windup(self, cx, cy, count=5):
        """Green leaf swirling particles gathering around creature."""
        colors = ["#4caf50", "#86de4f", "#a4ea64", "#2f8c84", "#c8ea64"]
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(40, 90)
            x = cx + math.cos(angle) * dist
            y = cy + math.sin(angle) * dist
            # Inward swirl velocity
            speed = random.uniform(80, 160)
            vx = -math.cos(angle + 0.5) * speed
            vy = -math.sin(angle + 0.5) * speed
            life = random.uniform(0.35, 0.65)
            color = random.choice(colors)
            size = random.uniform(6, 12)
            self.particles.append(Particle(x, y, vx, vy, life, p_type="leaf", color=color, size=size, friction=0.95))

    def spawn_leaf_projectile_stream(self, x1, y1, x2, y2, duration=0.55, count=16):
        """Create a volley of green leaf projectiles travelling from (x1,y1) to (x2,y2)."""
        pj = LeafVolleyProjectile(x1, y1, x2, y2, duration, count)
        self.projectiles.append(pj)

    def spawn_starburst_impact(self, x, y, count=3):
        """Starburst hit sparks on impact point."""
        for i in range(count):
            ox = x + random.uniform(-18, 18)
            oy = y + random.uniform(-18, 18)
            life = 0.22 + i * 0.05
            size = random.uniform(28, 48)
            self.particles.append(Particle(ox, oy, 0, 0, life, p_type="starburst", color="#ffffff", size=size, extra={"star_rot": random.uniform(0, math.pi)}))
        # Add a few sharp spark debris lines
        for _ in range(12):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(140, 280)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            col = random.choice(["#ffe08a", "#ffffff", "#f0a830"])
            self.particles.append(Particle(x, y, vx, vy, 0.25, p_type="spark", color=col, size=4, friction=0.92))

    def spawn_fire_charge(self, cx, cy, count=6):
        """Rising fire embers and heat distortion particles during charge."""
        colors = ["#ff3b30", "#ff9500", "#ffcc00", "#ff2d55", "#ffe08a"]
        for _ in range(count):
            ox = cx + random.uniform(-40, 40)
            oy = cy + random.uniform(-20, 30)
            vx = random.uniform(-25, 25)
            vy = random.uniform(-90, -180)  # Float upwards
            life = random.uniform(0.4, 0.8)
            col = random.choice(colors)
            size = random.uniform(5, 11)
            self.particles.append(Particle(ox, oy, vx, vy, life, p_type="ember", color=col, size=size, gravity=-40, friction=0.96))

    def spawn_fire_blast_stream(self, x1, y1, x2, y2, duration=0.65):
        """Launch massive rolling fire wave projectile."""
        pj = FireWaveProjectile(x1, y1, x2, y2, duration)
        self.projectiles.append(pj)

    def spawn_explosion(self, cx, cy):
        """Full explosion: expanding fiery blast core, billowing smoke, flying embers."""
        # 1. Fiery core burst particles
        for _ in range(18):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(60, 220)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd * 0.75
            col = random.choice(["#ffffff", "#ffe08a", "#ff9500", "#ff3b30"])
            size = random.uniform(16, 32)
            self.particles.append(Particle(cx, cy, vx, vy, random.uniform(0.35, 0.6), p_type="fire_core", color=col, size=size, friction=0.90))

        # 2. Billowing dark smoke puffs (drift upward and expand)
        smoke_cols = ["#261e22", "#3a2a28", "#4e3b38", "#1c1518"]
        for _ in range(12):
            ox = cx + random.uniform(-25, 25)
            oy = cy + random.uniform(-20, 20)
            vx = random.uniform(-40, 40)
            vy = random.uniform(-60, -130)
            life = random.uniform(0.6, 1.1)
            col = random.choice(smoke_cols)
            size = random.uniform(20, 42)
            self.particles.append(Particle(ox, oy, vx, vy, life, p_type="smoke", color=col, size=size, friction=0.94))

        # 3. Flying burning debris / embers with gravity
        for _ in range(24):
            ang = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            spd = random.uniform(180, 420)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            col = random.choice(["#ff3b30", "#ff9500", "#ffcc00", "#261e22"])
            life = random.uniform(0.5, 0.95)
            self.particles.append(Particle(cx, cy, vx, vy, life, p_type="ember", color=col, size=random.uniform(4, 8), gravity=380, friction=0.97))

    def spawn_ice_charge(self, cx, cy, count=5):
        """Frost crystals gathering for ice attack."""
        colors = ["#ffffff", "#cbf3f9", "#7fd3f5", "#a4ea64"]
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(40, 80)
            x = cx + math.cos(angle) * dist
            y = cy + math.sin(angle) * dist
            speed = random.uniform(70, 140)
            vx = -math.cos(angle) * speed
            vy = -math.sin(angle) * speed
            life = random.uniform(0.3, 0.6)
            col = random.choice(colors)
            self.particles.append(Particle(x, y, vx, vy, life, p_type="ice_crystal", color=col, size=random.uniform(5, 10), friction=0.96))

    def spawn_ice_projectile_stream(self, x1, y1, x2, y2, duration=0.5):
        pj = IceShardProjectile(x1, y1, x2, y2, duration)
        self.projectiles.append(pj)

    def spawn_ice_shatter(self, cx, cy):
        """Glassy ice crystal explosion."""
        colors = ["#ffffff", "#e0f8ff", "#7fd3f5", "#3f8fe0"]
        for _ in range(20):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(120, 320)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            life = random.uniform(0.3, 0.65)
            col = random.choice(colors)
            self.particles.append(Particle(cx, cy, vx, vy, life, p_type="ice_crystal", color=col, size=random.uniform(6, 12), gravity=200, friction=0.95))

    def spawn_physical_impact(self, cx, cy):
        """Comical hit spark and dust cloud."""
        self.spawn_starburst_impact(cx, cy, count=2)
        # Dust puff at bottom
        for _ in range(8):
            vx = random.uniform(-60, 60)
            vy = random.uniform(-20, -60)
            self.particles.append(Particle(cx, cy + 20, vx, vy, 0.4, p_type="smoke", color="#d8cce6", size=14, friction=0.92))

    # ----------------- Rendering -----------------

    def render(self, canvas, offset_x=0, offset_y=0):
        """Draw all active projectiles and particles on canvas with camera offset."""
        # Draw projectiles first
        for pj in self.projectiles:
            pj.render(canvas, offset_x, offset_y)

        # Draw particles
        for p in self.particles:
            px = p.x + offset_x
            py = p.y + offset_y
            prog = p.progress
            inv_p = 1.0 - prog

            if p.p_type == "leaf":
                # Render rotated diamond leaf shape
                sz = p.size * (0.8 + 0.4 * inv_p)
                ang = p.angle
                cos_a, sin_a = math.cos(ang), math.sin(ang)
                # 4 vertices: tip, right, base, left
                pts = [
                    (px + cos_a * sz * 1.6, py + sin_a * sz * 1.6),
                    (px - sin_a * sz * 0.6, py + cos_a * sz * 0.6),
                    (px - cos_a * sz * 1.2, py - sin_a * sz * 1.2),
                    (px + sin_a * sz * 0.6, py - cos_a * sz * 0.6),
                ]
                poly = [coord for pt in pts for coord in pt]
                canvas.create_polygon(poly, fill=p.color, outline="#2a2233", width=1)

            elif p.p_type == "starburst":
                # Multi-point flash star
                sz = p.size * inv_p
                rot = p.extra.get("star_rot", 0.0)
                pts = []
                num_points = 8
                for k in range(num_points * 2):
                    r = sz if (k % 2 == 0) else sz * 0.32
                    a = rot + k * (math.pi / num_points)
                    pts.extend([px + math.cos(a) * r, py + math.sin(a) * r])
                canvas.create_polygon(pts, fill=p.color, outline="#ffcc00", width=2)

            elif p.p_type == "ember":
                # Glowing square/circle ember
                sz = max(1.5, p.size * inv_p)
                canvas.create_rectangle(px - sz, py - sz, px + sz, py + sz, fill=p.color, outline="")

            elif p.p_type == "fire_core":
                # Expanding fireball puff
                sz = p.size * (0.5 + 0.7 * prog)
                canvas.create_oval(px - sz, py - sz, px + sz, py + sz, fill=p.color, outline="")

            elif p.p_type == "smoke":
                # Expanding dark smoke cloud
                sz = p.size * (0.5 + 0.9 * prog)
                canvas.create_oval(px - sz, py - sz, px + sz, py + sz, fill=p.color, outline="")

            elif p.p_type == "ice_crystal":
                # Cyan/white diamond
                sz = p.size * inv_p
                canvas.create_polygon(px, py - sz * 1.4, px + sz, py, px, py + sz * 1.4, px - sz, py, fill=p.color, outline="#ffffff", width=1)

            else:  # spark
                sz = max(1, p.size * inv_p)
                canvas.create_rectangle(px - sz, py - sz, px + sz, py + sz, fill=p.color, outline="")

# ----------------- Projectile Classes -----------------

class LeafVolleyProjectile:
    """Stream of green leaf darts flying across the screen."""
    def __init__(self, x1, y1, x2, y2, duration, count):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.duration = duration
        self.elapsed = 0.0
        self.count = count
        # Individual leaf offsets and delays
        self.leaves = []
        for _ in range(count):
            delay = random.uniform(0.0, duration * 0.45)
            spread_y = random.uniform(-25, 25)
            speed_mult = random.uniform(0.85, 1.15)
            size = random.uniform(8, 14)
            color = random.choice(["#4caf50", "#86de4f", "#a4ea64", "#2f8c84", "#c8ea64"])
            self.leaves.append({
                "delay": delay,
                "spread_y": spread_y,
                "speed_mult": speed_mult,
                "size": size,
                "color": color,
                "angle": random.uniform(-0.3, 0.3)
            })

    def update(self, dt, effects_mgr):
        self.elapsed += dt
        return self.elapsed < (self.duration + 0.1)

    def render(self, canvas, ox, oy):
        for leaf in self.leaves:
            t = self.elapsed - leaf["delay"]
            if t <= 0:
                continue
            prog = min(1.0, (t / (self.duration * 0.75)) * leaf["speed_mult"])
            if prog >= 1.0:
                continue
            # Arc interpolation
            arc_y = -math.sin(prog * math.pi) * 35.0
            cur_x = self.x1 + (self.x2 - self.x1) * prog + ox
            cur_y = self.y1 + (self.y2 - self.y1) * prog + leaf["spread_y"] + arc_y + oy

            # Direction angle
            ang = math.atan2(self.y2 - self.y1, self.x2 - self.x1) + leaf["angle"]
            sz = leaf["size"]
            cos_a, sin_a = math.cos(ang), math.sin(ang)
            pts = [
                cur_x + cos_a * sz * 1.5, cur_y + sin_a * sz * 1.5,
                cur_x - sin_a * sz * 0.5, cur_y + cos_a * sz * 0.5,
                cur_x - cos_a * sz * 1.0, cur_y - sin_a * sz * 1.0,
                cur_x + sin_a * sz * 0.5, cur_y - cos_a * sz * 0.5,
            ]
            canvas.create_polygon(pts, fill=leaf["color"], outline="#2a2233", width=1)

class FireWaveProjectile:
    """Billowing, rolling fire blast stream."""
    def __init__(self, x1, y1, x2, y2, duration):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt, effects_mgr):
        self.elapsed += dt
        # Spawn trailing embers
        prog = min(1.0, self.elapsed / self.duration)
        cur_x = self.x1 + (self.x2 - self.x1) * prog
        cur_y = self.y1 + (self.y2 - self.y1) * prog
        if prog < 1.0 and random.random() < 0.8:
            effects_mgr.particles.append(Particle(
                cur_x + random.uniform(-20, 20),
                cur_y + random.uniform(-15, 15),
                random.uniform(-40, 40),
                random.uniform(-40, 40),
                random.uniform(0.2, 0.45),
                p_type="ember",
                color=random.choice(["#ffcc00", "#ff6600", "#ff2200"]),
                size=random.uniform(5, 9)
            ))
        return self.elapsed < self.duration

    def render(self, canvas, ox, oy):
        prog = min(1.0, self.elapsed / self.duration)
        cur_x = self.x1 + (self.x2 - self.x1) * prog + ox
        cur_y = self.y1 + (self.y2 - self.y1) * prog + oy

        # Draw layered fiery wave head
        head_radius = 28 + 24 * prog
        # Outer flame red
        canvas.create_oval(cur_x - head_radius, cur_y - head_radius * 0.7,
                           cur_x + head_radius, cur_y + head_radius * 0.7,
                           fill="#e8473f", outline="")
        # Middle flame orange
        canvas.create_oval(cur_x - head_radius * 0.75, cur_y - head_radius * 0.5,
                           cur_x + head_radius * 0.75, cur_y + head_radius * 0.5,
                           fill="#f0a830", outline="")
        # Inner flame yellow/white core
        canvas.create_oval(cur_x - head_radius * 0.45, cur_y - head_radius * 0.3,
                           cur_x + head_radius * 0.45, cur_y + head_radius * 0.3,
                           fill="#fffae0", outline="")

class IceShardProjectile:
    """Ice crystals shooting toward defender."""
    def __init__(self, x1, y1, x2, y2, duration):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt, effects_mgr):
        self.elapsed += dt
        return self.elapsed < self.duration

    def render(self, canvas, ox, oy):
        prog = min(1.0, self.elapsed / self.duration)
        cur_x = self.x1 + (self.x2 - self.x1) * prog + ox
        cur_y = self.y1 + (self.y2 - self.y1) * prog + oy
        sz = 14
        canvas.create_polygon(cur_x, cur_y - sz, cur_x + sz * 1.5, cur_y, cur_x, cur_y + sz, cur_x - sz * 1.5, cur_y,
                              fill="#7fd3f5", outline="#ffffff", width=2)
