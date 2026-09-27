# Galaxy board: nebula, stars and a ringed planet, magenta glow.
import _board

NAME = "board_cosmic"
CATEGORY = "Boards"
JOIN = False  # Deck (textured), Bindings, Glow stay separate MeshParts


def build(rbx):
    _board.build_board(rbx, NAME, "cosmic", base_col="violet", accent_col="magenta", glow_col='magenta')
