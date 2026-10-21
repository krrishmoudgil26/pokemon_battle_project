"""
Procedural Retro Chiptune Audio Synthesizer
Generates authentic 8-bit / 16-bit sound effects and looping battle music.
"""

import os
import wave
import struct
import math
import random

SAMPLE_RATE = 44100

def ensure_dirs():
    os.makedirs("assets/audio/music", exist_ok=True)
    os.makedirs("assets/audio/sfx", exist_ok=True)

def write_wav(filename, samples, sample_rate=SAMPLE_RATE, num_channels=1):
    """Write float samples (-1.0 to 1.0) to 16-bit PCM WAV."""
    with wave.open(filename, "w") as w:
        w.setnchannels(num_channels)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        raw_data = bytearray()
        for s in samples:
            # Clamp and convert to 16-bit integer
            s = max(-1.0, min(1.0, s))
            val = int(s * 32767.0)
            if num_channels == 1:
                raw_data.extend(struct.pack("<h", val))
            else:
                raw_data.extend(struct.pack("<hh", val, val))
        w.writeframes(raw_data)

# ----------------- Waveform Generators -----------------

def square_wave(freq, t, duty=0.5):
    """Square wave with pulse-width control."""
    phase = (t * freq) % 1.0
    return 1.0 if phase < duty else -1.0

def triangle_wave(freq, t):
    """Triangle wave (warm classic bass)."""
    phase = (t * freq) % 1.0
    return 4.0 * abs(phase - 0.5) - 1.0

def saw_wave(freq, t):
    """Sawtooth wave."""
    phase = (t * freq) % 1.0
    return 2.0 * phase - 1.0

def noise_sample():
    """White noise sample."""
    return random.uniform(-1.0, 1.0)

# ----------------- SFX Synthesizers -----------------

def gen_select_sfx():
    """Short UI cursor blip."""
    dur = 0.05
    n = int(SAMPLE_RATE * dur)
    samples = []
    freq = 660.0
    for i in range(n):
        t = i / SAMPLE_RATE
        env = (1.0 - t / dur) ** 2
        s = square_wave(freq, t, duty=0.25) * env * 0.4
        samples.append(s)
    return samples

def gen_confirm_sfx():
    """Positive 2-tone chime."""
    dur = 0.16
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 523.25 if t < 0.08 else 783.99  # C5 -> G5
        env = (1.0 - (t % 0.08) / 0.08) ** 1.5
        s = square_wave(freq, t, duty=0.5) * env * 0.45
        samples.append(s)
    return samples

def gen_charge_grass_sfx():
    """Green leaf energy gather: rising pitch with rapid vibrato and rustling noise."""
    dur = 0.85
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Pitch rises from 280 Hz to 820 Hz
        base_f = 280.0 + 540.0 * (t / dur) ** 1.3
        vibrato = math.sin(2.0 * math.pi * 24.0 * t) * 35.0
        f = base_f + vibrato
        env = math.sin(math.pi * (t / dur) ** 0.8)
        tonal = square_wave(f, t, duty=0.3) * 0.4
        # Rustling leaf noise burst
        rustle = noise_sample() * (0.2 + 0.15 * math.sin(2.0 * math.pi * 32.0 * t))
        s = (tonal * 0.65 + rustle * 0.35) * env * 0.6
        samples.append(s)
    return samples

def gen_leaf_whoosh_sfx():
    """High-speed leaf projectile stream whoosh."""
    dur = 0.45
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Noise band modulated by rising and falling sweep
        env = math.sin(math.pi * t / dur) ** 2
        f = 1200.0 - 600.0 * (t / dur)
        s = (noise_sample() * 0.6 + square_wave(f, t, duty=0.2) * 0.4) * env * 0.55
        samples.append(s)
    return samples

def gen_hit_grass_sfx():
    """Punchy multi-hit arcade slash impact (sharp cuts + low punch)."""
    dur = 0.55
    n = int(SAMPLE_RATE * dur)
    samples = []
    # 3 hits spaced at 0ms, 90ms, 180ms
    hits = [0.0, 0.09, 0.18]
    for i in range(n):
        t = i / SAMPLE_RATE
        val = 0.0
        for h_idx, hit_t in enumerate(hits):
            dt = t - hit_t
            if 0 <= dt < 0.14:
                decay = math.exp(-dt * 38.0)
                # Sharp high noise crack
                crack = noise_sample() * decay * 0.55
                # Punchy low triangle pitch drop
                f = max(60.0, 320.0 - dt * 1800.0)
                punch = triangle_wave(f, dt) * decay * 0.65
                # Accent on final hit
                mult = 1.3 if h_idx == 2 else 0.85
                val += (crack + punch) * mult
        samples.append(val * 0.5)
    return samples

def gen_fire_charge_sfx():
    """Rising fire charge: deep rumbling flame roar and rising harmonic tone."""
    dur = 1.1
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = (t / dur) ** 1.5
        # Low frequency rumble
        f_sub = 80.0 + 120.0 * (t / dur)
        sub = triangle_wave(f_sub, t) * 0.4
        # Rising saw roar
        f_saw = 140.0 + 380.0 * (t / dur) ** 1.4
        saw = saw_wave(f_saw, t) * 0.35
        # Crackling flame noise
        crackle = noise_sample() * (0.2 + 0.15 * math.sin(2.0 * math.pi * 18.0 * t))
        s = (sub + saw + crackle) * env * 0.7
        samples.append(s)
    return samples

def gen_fire_blast_sfx():
    """Massive fire wave whoosh."""
    dur = 0.8
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * t / dur) ** 1.2
        # Modulated roaring noise
        low_mod = 0.5 + 0.5 * math.sin(2.0 * math.pi * 12.0 * t)
        noise = noise_sample() * low_mod * 0.7
        f = max(90.0, 360.0 - 240.0 * (t / dur))
        sub = triangle_wave(f, t) * 0.4
        s = (noise + sub) * env * 0.75
        samples.append(s)
    return samples

def gen_explosion_sfx():
    """Heavy punchy low-end explosion with initial blast crack and decaying rumble."""
    dur = 0.95
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Initial sharp crack (0-0.08s)
        crack_env = math.exp(-t * 45.0)
        crack = noise_sample() * crack_env * 0.85
        # Sub boom drop (180 Hz -> 35 Hz)
        boom_env = math.exp(-t * 4.5)
        f_boom = max(35.0, 180.0 * math.exp(-t * 9.0))
        boom = triangle_wave(f_boom, t) * boom_env * 0.9
        # Decaying rumble noise with low-pass style simulation
        rumble_env = math.exp(-t * 3.8)
        rumble = noise_sample() * rumble_env * 0.4
        s = (crack * 0.4 + boom * 0.5 + rumble * 0.3)
        samples.append(s * 0.8)
    return samples

def gen_damage_sfx():
    """Creature recoil hurt grunt / retro impact thud."""
    dur = 0.28
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 18.0)
        f = max(70.0, 240.0 - t * 900.0)
        s = (square_wave(f, t, duty=0.25) * 0.4 + noise_sample() * 0.35) * env * 0.7
        samples.append(s)
    return samples

def gen_physical_hit_sfx():
    """Punchy physical hit (Tackle / Stomp / Gore)."""
    dur = 0.22
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 22.0)
        f = max(55.0, 380.0 - t * 1800.0)
        s = (triangle_wave(f, t) * 0.6 + noise_sample() * 0.5) * env * 0.75
        samples.append(s)
    return samples

def gen_ice_charge_sfx():
    """Shivering icy frost crystal charge."""
    dur = 0.8
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = (t / dur) ** 1.2
        f = 700.0 + 600.0 * (t / dur)
        shimmer = math.sin(2.0 * math.pi * 30.0 * t) * 50.0
        s = square_wave(f + shimmer, t, duty=0.15) * env * 0.45
        samples.append(s)
    return samples

def gen_ice_hit_sfx():
    """Glassy ice shatter / freezing impact."""
    dur = 0.4
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 12.0)
        # High pitched resonant ringing + noise
        ring = (math.sin(2.0 * math.pi * 1480.0 * t) + math.sin(2.0 * math.pi * 2100.0 * t)) * 0.35
        shatter = noise_sample() * 0.45
        s = (ring + shatter) * env * 0.6
        samples.append(s)
    return samples

def gen_potion_sfx():
    """Magical sparkling potion heal chime."""
    dur = 0.5
    n = int(SAMPLE_RATE * dur)
    samples = []
    notes = [440.0, 554.37, 659.25, 880.0, 1108.73]  # A Major arpeggio
    for i in range(n):
        t = i / SAMPLE_RATE
        idx = min(len(notes) - 1, int(t / (dur / len(notes))))
        f = notes[idx]
        note_t = t % (dur / len(notes))
        env = math.exp(-note_t * 15.0)
        s = (triangle_wave(f, t) * 0.5 + square_wave(f * 2.0, t, duty=0.2) * 0.25) * env * 0.55
        samples.append(s)
    return samples

def gen_faint_sfx():
    """Creature fainting descending pitch."""
    dur = 0.6
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = (1.0 - t / dur) ** 1.2
        f = max(50.0, 340.0 - 280.0 * (t / dur) ** 0.8)
        s = square_wave(f, t, duty=0.4) * env * 0.5
        samples.append(s)
    return samples

def gen_victory_jingle():
    """Triumphant retro Pokémon-style victory fanfare."""
    # Sequence of notes: (freq, duration in seconds)
    notes = [
        (523.25, 0.12),  # C5
        (523.25, 0.12),  # C5
        (523.25, 0.12),  # C5
        (523.25, 0.28),  # C5 long
        (415.30, 0.24),  # Ab4
        (466.16, 0.24),  # Bb4
        (523.25, 0.20),  # C5
        (466.16, 0.14),  # Bb4
        (523.25, 0.60),  # C5 held
    ]
    total_dur = sum(d for _, d in notes)
    n = int(SAMPLE_RATE * total_dur)
    samples = []
    curr_t = 0.0
    for f, d in notes:
        n_note = int(SAMPLE_RATE * d)
        for i in range(n_note):
            t = i / SAMPLE_RATE
            env = math.exp(-t * (1.5 if d > 0.3 else 3.5))
            # Harmony with third
            lead = square_wave(f, t, duty=0.5) * 0.45
            harm = triangle_wave(f * 0.5, t) * 0.35
            samples.append((lead + harm) * env * 0.65)
    return samples

def gen_defeat_jingle():
    """Melancholic retro defeat jingle."""
    notes = [
        (440.0, 0.25),   # A4
        (415.30, 0.25),  # Ab4
        (392.00, 0.25),  # G4
        (349.23, 0.65),  # F4 long
    ]
    samples = []
    for f, d in notes:
        n_note = int(SAMPLE_RATE * d)
        for i in range(n_note):
            t = i / SAMPLE_RATE
            env = (1.0 - t / d) ** 1.3
            lead = square_wave(f, t, duty=0.3) * 0.4
            bass = triangle_wave(f * 0.5, t) * 0.35
            samples.append((lead + bass) * env * 0.6)
    return samples

# ----------------- Looping Battle Music -----------------

def gen_battle_theme():
    """
    Full 8-bar looping retro battle theme in 4/4 time at 144 BPM.
    Channels:
    - Lead melody (pulse wave 50%)
    - Harmony / Arpeggio (pulse wave 25%)
    - Bassline (driving triangle wave)
    - Drums (noise snare + kick sub)
    """
    bpm = 144.0
    beat_dur = 60.0 / bpm          # ~0.4167s per beat
    step_dur = beat_dur / 4.0      # 16th note (~0.1042s)
    total_steps = 128              # 8 bars * 16 steps = 128 steps (~13.33s)
    total_dur = total_steps * step_dur
    total_samples = int(SAMPLE_RATE * total_dur)

    # Note frequencies
    C3, D3, Eb3, F3, G3, Ab3, Bb3, B3 = 130.81, 146.83, 155.56, 174.61, 196.00, 207.65, 233.08, 246.94
    C4, D4, Eb4, F4, G4, Ab4, Bb4, B4 = 261.63, 293.66, 311.13, 349.23, 392.00, 415.30, 466.16, 493.88
    C5, D5, Eb5, F5, G5, Ab5, Bb5, B5 = 523.25, 587.33, 622.25, 698.46, 783.99, 830.61, 932.33, 987.77
    C6, D6, Eb6 = 1046.50, 1174.66, 1244.51

    # Bassline pattern (C minor driving rhythm: C - Eb - F - G - Ab - Bb)
    bass_notes = [
        # Bar 1: C
        C3, C3, Eb3, C3,  G3, C3, Eb3, G3,  C3, C3, Eb3, C3,  Bb3, G3, F3, Eb3,
        # Bar 2: C
        C3, C3, Eb3, C3,  G3, C3, Eb3, G3,  C3, C3, Eb3, C3,  D3, Eb3, F3, G3,
        # Bar 3: Ab
        Ab3, Ab3, C4, Ab3, Eb3, Ab3, C4, Eb3, Ab3, Ab3, C4, Ab3, G3, F3, Eb3, D3,
        # Bar 4: Bb -> G
        Bb3, Bb3, D4, Bb3, F3, Bb3, D4, F3,  G3, G3, B3, G3,    D3, G3, B3, D4,
        # Bar 5: C (heroic rise)
        C3, C3, Eb3, C3,  G3, C3, Eb3, G3,  C3, C3, Eb3, C3,  Bb3, G3, F3, Eb3,
        # Bar 6: F -> G
        F3, F3, Ab3, F3,  C3, F3, Ab3, C4,  G3, G3, Bb3, G3,  D3, G3, Bb3, D4,
        # Bar 7: Ab -> Bb
        Ab3, Ab3, C4, Ab3, Eb3, Ab3, C4, Eb3, Bb3, Bb3, D4, Bb3, F3, Bb3, D4, F3,
        # Bar 8: C cadence
        C3, C3, G3, C3,   C3, C3, G3, C3,   C3, Eb3, G3, C4,  Bb3, G3, F3, D3,
    ]

    # Lead melody (None = rest/sustain)
    melody_notes = [
        # Bar 1
        C5, None, C5, D5,  Eb5, None, G5, None,  F5, None, Eb5, None,  D5, None, Bb4, None,
        # Bar 2
        C5, None, Eb5, None, G5, None, C6, None,  Bb5, None, G5, None, F5, G5, Eb5, D5,
        # Bar 3
        C5, None, Ab5, None, G5, None, Eb5, None, F5, None, G5, None,  Eb5, None, D5, None,
        # Bar 4
        Bb4, None, D5, None, F5, None, Bb5, None, G5, None, F5, None,  D5, None, Eb5, D5,
        # Bar 5 (High heroic phase)
        C5, None, G5, None,  C6, None, Bb5, None, G5, None, F5, None,  G5, None, Eb5, None,
        # Bar 6
        F5, None, Ab5, None, C6, None, None, None, G5, None, Bb5, None, D6, None, None, None,
        # Bar 7
        C6, None, Bb5, None, Ab5, None, G5, None, F5, None, G5, None,  Ab5, None, Bb5, None,
        # Bar 8 (Turnaround)
        C6, None, G5, None,  Eb5, None, C5, None, G5, F5, Eb5, D5,    C5, None, None, None,
    ]

    samples = [0.0] * total_samples

    for step in range(total_steps):
        step_start_t = step * step_dur
        start_idx = int(step_start_t * SAMPLE_RATE)
        end_idx = int((step_start_t + step_dur) * SAMPLE_RATE)

        # 1. Bass Channel (triangle wave)
        bf = bass_notes[step % len(bass_notes)]
        for i in range(start_idx, min(end_idx, total_samples)):
            t = i / SAMPLE_RATE
            dt = t - step_start_t
            env = math.exp(-dt * 6.0)
            bass_val = triangle_wave(bf, t) * env * 0.35
            samples[i] += bass_val

        # 2. Melody Channel (square wave 50%)
        mf = melody_notes[step % len(melody_notes)]
        if mf is not None:
            # Sustain across steps if next is None
            sustain_len = step_dur
            lookahead = step + 1
            while lookahead < total_steps and melody_notes[lookahead] is None:
                sustain_len += step_dur
                lookahead += 1
            m_end_idx = min(int((step_start_t + sustain_len) * SAMPLE_RATE), total_samples)

            for i in range(start_idx, m_end_idx):
                t = i / SAMPLE_RATE
                dt = t - step_start_t
                env = math.exp(-dt * (1.2 if sustain_len > step_dur * 2 else 3.5))
                # subtle vibrato
                vibrato = math.sin(2.0 * math.pi * 6.0 * dt) * 4.0 if dt > 0.1 else 0.0
                lead_val = square_wave(mf + vibrato, t, duty=0.5) * env * 0.28
                samples[i] += lead_val

        # 3. Arpeggio Channel (rapid pulse wave 25%)
        # 16th note arp on root chord
        arp_root = bass_notes[step % len(bass_notes)]
        arp_f = arp_root * 2.0
        for i in range(start_idx, min(end_idx, total_samples)):
            t = i / SAMPLE_RATE
            dt = t - step_start_t
            env = math.exp(-dt * 12.0)
            arp_val = square_wave(arp_f, t, duty=0.25) * env * 0.12
            samples[i] += arp_val

        # 4. Drum Channel
        # Kick on beat 0 and 2 (steps 0, 8, 16, etc.)
        # Snare on beat 1 and 3 (steps 4, 12, 20, etc.)
        # Hi-hat on every odd 16th note
        step_in_bar = step % 16
        is_kick = step_in_bar in (0, 8)
        is_snare = step_in_bar in (4, 12)
        is_hat = step_in_bar % 2 == 1

        for i in range(start_idx, min(end_idx, total_samples)):
            t = i / SAMPLE_RATE
            dt = t - step_start_t

            if is_kick:
                kf = max(40.0, 160.0 * math.exp(-dt * 25.0))
                kick_env = math.exp(-dt * 14.0)
                samples[i] += triangle_wave(kf, dt) * kick_env * 0.32

            if is_snare:
                snare_env = math.exp(-dt * 16.0)
                snare_tone = triangle_wave(180.0, dt) * snare_env * 0.18
                snare_noise = noise_sample() * snare_env * 0.25
                samples[i] += (snare_tone + snare_noise)

            if is_hat:
                hat_env = math.exp(-dt * 45.0)
                samples[i] += noise_sample() * hat_env * 0.08

    # Apply gentle master limiter / normalization
    peak = max(abs(s) for s in samples) if samples else 1.0
    scale = 0.85 / peak if peak > 0.85 else 1.0
    samples = [s * scale for s in samples]

    return samples

# ----------------- Main Generation Routine -----------------

def generate_all_audio():
    print("Generating audio assets...")
    ensure_dirs()

    sfx_map = {
        "assets/audio/sfx/select.wav": gen_select_sfx(),
        "assets/audio/sfx/confirm.wav": gen_confirm_sfx(),
        "assets/audio/sfx/charge_grass.wav": gen_charge_grass_sfx(),
        "assets/audio/sfx/leaf_whoosh.wav": gen_leaf_whoosh_sfx(),
        "assets/audio/sfx/hit_grass.wav": gen_hit_grass_sfx(),
        "assets/audio/sfx/fire_charge.wav": gen_fire_charge_sfx(),
        "assets/audio/sfx/fire_blast.wav": gen_fire_blast_sfx(),
        "assets/audio/sfx/explosion.wav": gen_explosion_sfx(),
        "assets/audio/sfx/damage.wav": gen_damage_sfx(),
        "assets/audio/sfx/physical_hit.wav": gen_physical_hit_sfx(),
        "assets/audio/sfx/ice_charge.wav": gen_ice_charge_sfx(),
        "assets/audio/sfx/ice_hit.wav": gen_ice_hit_sfx(),
        "assets/audio/sfx/potion.wav": gen_potion_sfx(),
        "assets/audio/sfx/faint.wav": gen_faint_sfx(),
        "assets/audio/sfx/victory.wav": gen_victory_jingle(),
        "assets/audio/sfx/defeat.wav": gen_defeat_jingle(),
    }

    for path, data in sfx_map.items():
        write_wav(path, data, num_channels=2)
        print(f"Generated {path}")

    # Battle music
    theme_data = gen_battle_theme()
    theme_path = "assets/audio/music/battle_theme.wav"
    write_wav(theme_path, theme_data, num_channels=2)
    print(f"Generated {theme_path}")
    print("All audio assets generated successfully!")

if __name__ == "__main__":
    generate_all_audio()
