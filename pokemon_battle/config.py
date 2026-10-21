WIDTH, HEIGHT = 1280, 720

PIXEL = 8

COLS, ROWS = WIDTH // PIXEL, HEIGHT // PIXEL      # 160 x 90 background "pixels"

UI_TOP = 560                                      # where the battle menu panel starts

UI_ROW = UI_TOP // PIXEL                          # 70

# Palette taken from the screenshot

INK = "#2a2233"        # near-black purple (outlines, menu panel)

LAV = "#d8cce6"        # lavender (HUD panels, menu text)

LAV_D = "#a898c8"      # darker lavender

PURPLE = "#7a4fc0"     # HP badge

SKY = "#4c82ff"

SKY_DARK = "#3b5fd2"

PINK = "#f6c6dc"

WHITE = "#fdf4f8"

TEAL = "#2f8c84"

TEAL_L = "#3fa391"

INDIGO = "#4b4aa3"

INDIGO_D = "#3e3e8f"

GRASS = "#86de4f"

GRASS_D = "#4fb348"

GRASS_L = "#a4ea64"

TYPE_COLORS = {

    "Electric": "#f0b429", "Grass": "#4caf50", "Fire": "#e8473f",

    "Water": "#3f8fe0", "Normal": "#a79f8f", "Ghost": "#7a55a8", "Ice": "#7fd3f5",

}

DARK_TEXT_TYPES = ("Electric", "Normal", "Ice")

FONT = "Courier New"

MONSTERS = [

    {"name": "Emberhorn", "type": "Fire", "hp": 118, "zoom": 2,

     "moves": [("Magma Gore", 20), ("Cinder Stomp", 16), ("Ember Snort", 13), ("Lava Charge", 24)]},

    {"name": "Frostram", "type": "Ice", "hp": 104, "zoom": 2,

     "moves": [("Frost Butt", 17), ("Ice Shard", 15), ("Snow Squall", 13), ("Glacier Crash", 23)]},

    {"name": "Thornquill", "type": "Grass", "hp": 96, "zoom": 3,

     "moves": [("Needle Volley", 16), ("Leaf Dart", 13), ("Spore Spark", 12), ("Solar Quill", 22)]},

]

# Pixel-art sprites (base64 PNG). "left" faces left (used for the enemy),

# "right" is the mirrored version (used for the player).
