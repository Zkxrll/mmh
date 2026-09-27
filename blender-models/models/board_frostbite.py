# Ice-blue board with frozen shards and a glowing cyan edge.
import _board

NAME = "board_frostbite"
CATEGORY = "Boards"
JOIN = False  # Deck (textured), Bindings, Glow stay separate MeshParts


def build(rbx):
    _board.build_board(rbx, NAME, "frostbite", base_col="white", accent_col="cyan", glow_col='glow_cyan')
