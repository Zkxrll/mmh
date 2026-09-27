# Hot-rod flames on black with a glowing orange edge.
import _board

NAME = "board_inferno"
CATEGORY = "Boards"
JOIN = False  # Deck (textured), Bindings, Glow stay separate MeshParts


def build(rbx):
    _board.build_board(rbx, NAME, "inferno", base_col="carbon", accent_col="fire", glow_col='fire')
