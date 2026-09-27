# Carbon snake-scale board with a neon green zigzag and edge.
import _board

NAME = "board_viper"
CATEGORY = "Boards"
JOIN = False  # Deck (textured), Bindings, Glow stay separate MeshParts


def build(rbx):
    _board.build_board(rbx, NAME, "viper", base_col="carbon", accent_col="neon_green", glow_col='neon_green')
