# Retro synthwave sun and grid, hot pink glow.
import _board

NAME = "board_sunset"
CATEGORY = "Boards"
JOIN = False  # Deck (textured), Bindings, Glow stay separate MeshParts


def build(rbx):
    _board.build_board(rbx, NAME, "sunset", base_col="white", accent_col="hot_pink", glow_col='hot_pink')
