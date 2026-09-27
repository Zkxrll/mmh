# Starter board: wood veneer with a red racing stripe, no glow.
import _board

NAME = "board_rookie"
CATEGORY = "Boards"
JOIN = False  # Deck (textured), Bindings, Glow stay separate MeshParts


def build(rbx):
    _board.build_board(rbx, NAME, "rookie", base_col="carbon", accent_col="red", glow_col=None)
