"""
Audio Manager for Pixel Monsters Battle Arena.
Handles background music, sound effects, volume control, and graceful fallback.
"""

import os
import sys

class AudioManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AudioManager()
        return cls._instance

    def __init__(self):
        self.available = False
        self.mixer = None
        self.sounds = {}
        self.music_loaded = False
        self.current_music = None

        # Volume levels (0.0 to 1.0)
        self.master_volume = 0.8
        self.music_volume = 0.65
        self.sfx_volume = 0.85

        # Dedicated sound channels
        self.channels = {}

        # Debounce tracking to prevent repeated spam in the same animation tick
        self.last_played = {}

        self.init_audio()

    def init_audio(self):
        """Initialize pygame.mixer safely without crashing if unavailable."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                # 44.1kHz, 16-bit signed, stereo, 512 sample buffer for low latency
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init()
            self.mixer = pygame.mixer
            self.available = True
            self.mixer.set_num_channels(16)

            # Assign dedicated channel IDs for organized mixing
            self.channels = {
                "ui": self.mixer.Channel(0),
                "charge": self.mixer.Channel(1),
                "projectile": self.mixer.Channel(2),
                "impact": self.mixer.Channel(3),
                "damage": self.mixer.Channel(4),
                "voice": self.mixer.Channel(5),
                "jingle": self.mixer.Channel(6),
            }

            self.load_all_sounds()
        except Exception as e:
            print(f"[AudioManager] Audio initialization warning: {e}. Running in silent fallback mode.")
            self.available = False

    def load_all_sounds(self):
        """Pre-load all sound effects into memory once."""
        if not self.available or not self.mixer:
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sfx_dir = os.path.join(base_dir, "assets", "audio", "sfx")

        sound_files = {
            "select": "select.wav",
            "confirm": "confirm.wav",
            "charge_grass": "charge_grass.wav",
            "leaf_whoosh": "leaf_whoosh.wav",
            "hit_grass": "hit_grass.wav",
            "fire_charge": "fire_charge.wav",
            "fire_blast": "fire_blast.wav",
            "explosion": "explosion.wav",
            "damage": "damage.wav",
            "physical_hit": "physical_hit.wav",
            "ice_charge": "ice_charge.wav",
            "ice_hit": "ice_hit.wav",
            "potion": "potion.wav",
            "faint": "faint.wav",
            "victory": "victory.wav",
            "defeat": "defeat.wav",
        }

        for name, filename in sound_files.items():
            path = os.path.join(sfx_dir, filename)
            if os.path.exists(path):
                try:
                    snd = self.mixer.Sound(path)
                    effective_vol = self.master_volume * self.sfx_volume
                    snd.set_volume(effective_vol)
                    self.sounds[name] = snd
                except Exception as ex:
                    print(f"[AudioManager] Failed to load sound {name} from {path}: {ex}")
            else:
                print(f"[AudioManager] Sound file missing: {path}")

    def play_music(self, track_name="battle_theme", loop=True, fade_ms=500):
        """Play looping background music track."""
        if not self.available or not self.mixer:
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        music_path = os.path.join(base_dir, "assets", "audio", "music", f"{track_name}.wav")

        if not os.path.exists(music_path):
            print(f"[AudioManager] Music track not found: {music_path}")
            return

        if self.current_music == track_name and self.mixer.music.get_busy():
            return  # Already playing this track

        try:
            self.mixer.music.load(music_path)
            self.mixer.music.set_volume(self.master_volume * self.music_volume)
            loops = -1 if loop else 0
            if fade_ms > 0:
                self.mixer.music.play(loops=loops, fade_ms=fade_ms)
            else:
                self.mixer.music.play(loops=loops)
            self.current_music = track_name
            self.music_loaded = True
        except Exception as e:
            print(f"[AudioManager] Error playing music: {e}")

    def stop_music(self, fade_ms=400):
        """Stop background music."""
        if not self.available or not self.mixer:
            return
        try:
            if fade_ms > 0:
                self.mixer.music.fadeout(fade_ms)
            else:
                self.mixer.music.stop()
            self.current_music = None
        except Exception as e:
            print(f"[AudioManager] Error stopping music: {e}")

    def pause_music(self):
        if self.available and self.mixer:
            try:
                self.mixer.music.pause()
            except Exception:
                pass

    def unpause_music(self):
        if self.available and self.mixer:
            try:
                self.mixer.music.unpause()
            except Exception:
                pass

    def play_sfx(self, name, channel_name=None, min_interval_ms=100):
        """
        Play a sound effect on an optional dedicated channel.
        Prevents repeated sound spam within min_interval_ms.
        """
        if not self.available or not self.mixer or name not in self.sounds:
            return

        import time
        now = time.time() * 1000.0
        last = self.last_played.get(name, 0.0)
        if now - last < min_interval_ms:
            return
        self.last_played[name] = now

        sound = self.sounds[name]
        effective_vol = self.master_volume * self.sfx_volume
        sound.set_volume(effective_vol)

        try:
            if channel_name and channel_name in self.channels:
                ch = self.channels[channel_name]
                ch.play(sound)
            else:
                sound.play()
        except Exception as e:
            print(f"[AudioManager] Error playing SFX {name}: {e}")

    def set_master_volume(self, vol):
        self.master_volume = max(0.0, min(1.0, vol))
        self.update_volumes()

    def set_music_volume(self, vol):
        self.music_volume = max(0.0, min(1.0, vol))
        self.update_volumes()

    def set_sfx_volume(self, vol):
        self.sfx_volume = max(0.0, min(1.0, vol))
        self.update_volumes()

    def update_volumes(self):
        if self.available and self.mixer:
            try:
                self.mixer.music.set_volume(self.master_volume * self.music_volume)
            except Exception:
                pass
            eff_sfx = self.master_volume * self.sfx_volume
            for snd in self.sounds.values():
                try:
                    snd.set_volume(eff_sfx)
                except Exception:
                    pass
