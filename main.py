import tkinter as tk
from pokemon_battle.game import BattleGame

if __name__ == "__main__":
    root = tk.Tk()
    BattleGame(root)
    root.mainloop()
