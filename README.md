# Pixel Monsters — Battle Arena

A modular retro pixel-art monster battle game inspired by classic turn-based RPGs, featuring video-matched combat animations, procedural particle effects, screen shake, and authentic chiptune audio.

## Requirements
- Python 3.9 or newer (tested on Python 3.9, 3.12, and 3.14)
- Tkinter (standard with Python on Windows)
- `pygame` (used for audio mixing; installed via `pip install pygame`)

## How to Run
Open a terminal in this folder and run:

```bash
python main.py
```
*(Or `py main.py` / `python3 main.py`)*

To run the automated battle system validation test:
```bash
python test_battle.py
```

## Features & Visual Matching
- **16:9 Retro Viewport (1280x720)**: Pixel-art sky, dithered mountain ridges, lush grassy arena, corner bushes, and ground shadows under each creature.
- **Continuous Idle Animations**: Breathing body bobbing, flickering animated horn flames for Emberhorn, and quill shimmers for Thornquill.
- **Video-Matched Attack Animations**:
  - **Phase A (Windup)**: Anticipation crouch, charging sound, swirling green leaf / fire aura particles.
  - **Phase B (Projectile Flight)**: Rapid stream of rotating green leaf darts or billowing fire wave.
  - **Phase C (Impact & Recoil)**: Starburst hit sparks, creature wince & flash tint, screen shake, multi-hit impact sounds.
  - **Phase D (Counterattack Windup)**: Emberhorn roaring pose, horn flames expanding 2x, rising fire charge sound, glowing ember storm.
  - **Phase E (Fire Wave & Explosion)**: Billowing flame wave, massive impact explosion with expanding fiery core, rolling dark smoke clouds, flying burning debris, and heavy impact sound.
  - **Phase F (HP Drain & Idle Return)**: Dual-layer health bars with trailing red damage catchup bars, real-time numeric HP countdown, and smooth recovery to base stance.
- **Audio System**:
  - Dedicated `AudioManager` with separate channels for BGM, attack charge, projectiles, impact, damage grunt, and UI blips.
  - High-energy looping retro battle theme (`assets/audio/music/battle_theme.wav`).
  - 16 custom chiptune SFX in `assets/audio/sfx/`.
  - Graceful silent fallback if sound hardware is absent.
- **Preserved Combat & AI Mechanics**:
  - Full player vs. AI turn-based mechanics with type effectiveness, move power, PP depletion, bag potions, switching, and running.
  - Real HP synchronization (damage applied exactly once per hit).

## Project Structure
- `main.py` — application entry point
- `pokemon_battle/config.py` — 1280x720 window dimensions, palette, and monster definitions
- `pokemon_battle/audio_manager.py` — sound engine, music looping, volume control, and debounced channels
- `pokemon_battle/animation_manager.py` — 60 FPS non-blocking animation states, easing curves, and HP drain
- `pokemon_battle/effects.py` — reusable particle system (leaves, flames, smoke, embers, starbursts) and screen shake
- `pokemon_battle/sprites.py` — embedded base pixel-art sprites
- `pokemon_battle/background.py` — pixel-art battle arena background loading & procedural generator
- `pokemon_battle/game.py` — main battle loop, controls, HUD, and turn orchestration
- `assets/audio/` — background music and sound effects (WAV)
- `assets/sprites/` — creature pose sprites, animated horn flame frames, and arena background
- `test_battle.py` — automated headless test script

## Controls
- **Arrow Keys**: Navigate the move menu
- **Enter / Space / Z**: Select move
- **B**: Use healing potion from bag
- **S**: Switch monster
- **R**: Run away
- **Esc**: Quit game
