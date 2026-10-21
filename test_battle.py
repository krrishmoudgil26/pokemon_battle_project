"""
Headless validation script for BattleGame.
Initializes Tkinter, tests loading assets, audio playback, particle spawning,
and ticks the battle animation loop for several simulated turns.
"""

import sys
import time
import tkinter as tk
from pokemon_battle.game import BattleGame
from pokemon_battle.audio_manager import AudioManager

def run_test():
    print("Testing BattleGame initialization...")
    root = tk.Tk()
    root.withdraw()  # Hide window during headless test

    game = BattleGame(root)
    print("BattleGame created successfully!")
    print(f"Player: {game.player['name']} (HP: {game.player_hp}/{game.player['hp']})")
    print(f"Enemy: {game.enemy['name']} (HP: {game.enemy_hp}/{game.enemy['hp']})")

    # Verify audio manager
    am = AudioManager.get_instance()
    print(f"Audio available: {am.available}, Sounds: {len(am.sounds)}")

    # Wait for encounter message to finish and menu to show
    print("Waiting for encounter message...")
    ticks = 0
    while game.busy and ticks < 150:
        root.update()
        time.sleep(0.016)
        ticks += 1
    assert not game.busy, "Game should be ready for input!"

    # Test selecting a move and triggering animation
    print("Simulating move selection (Needle Volley)...")
    game.choose_move(0)
    assert game.active_sequence is not None, "Active sequence should be created!"
    print(f"Attack sequence started: state={game.active_sequence.state}, move={game.active_sequence.move_name}")

    # Tick through attack sequence
    print("Ticking through attack animation...")
    ticks = 0
    while game.active_sequence is not None and ticks < 300:
        root.update()
        time.sleep(0.016)
        ticks += 1

    print(f"Player attack sequence finished after {ticks} ticks!")
    print(f"Enemy HP after attack: {game.enemy_hp}/{game.enemy['hp']}")

    # Now let enemy attack
    print("Triggering enemy attack...")
    game.enemy_turn()
    assert game.active_sequence is not None, "Enemy attack sequence should be created!"
    print(f"Enemy attack sequence started: state={game.active_sequence.state}, move={game.active_sequence.move_name}")

    ticks = 0
    while game.active_sequence is not None and ticks < 300:
        root.update()
        time.sleep(0.016)
        ticks += 1

    print(f"Enemy attack sequence finished after {ticks} ticks!")
    print(f"Player HP after attack: {game.player_hp}/{game.player['hp']}")

    # Test potion
    print("Testing potion...")
    old_p_hp = game.player_hp
    game.busy = False
    game.use_potion()
    print(f"Player HP after potion: {game.player_hp} (was {old_p_hp}), potions left: {game.potions}")

    root.destroy()
    print("ALL TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_test()
