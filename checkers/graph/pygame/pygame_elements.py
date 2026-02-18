import enum
from typing import Optional
from checkers.types import ColorType, RectType
from checkers.constant import MAX_MAN, MAX_KING, CELL_WIDTH, CELL_HEIGHT
from checkers.graph.pygame.colors import Colors
from checkers.engine.game.cells import Coordinates2D, Cells
from checkers.engine.game.pieces import EnumPlayersColor, Pieces
check_valid_piece = Pieces.check_valid_piece

# Classe per definire lo stato dei pezzi
@enum.unique
class EnumStatePiece(enum.Enum):
    P_NORMAL = 0
    P_SELECTED = 1
    P_CAPTURED = 2

class PygamePiece:
    """
    """

    def __init__(self, id_piece:int):
        check_valid_piece(id_piece)
        self.id_piece : int = id_piece
        self.player : EnumPlayersColor = EnumPlayersColor.P_LIGHT if id_piece > 0 else EnumPlayersColor.P_DARK
        self.is_king : bool = True if MAX_MAN < abs(id_piece) <= MAX_KING else False
        self.state = EnumStatePiece.P_NORMAL

    def promotion_king(self):
        if not self.is_king:
            self.is_king = True
            # promotion to King
            if 0 < self.id_piece <= MAX_MAN: 
                self.id_piece += MAX_MAN
            elif 0 > self.id_piece >= -MAX_MAN:
                self.id_piece -= MAX_MAN
            else:
                raise ValueError(f"The piece ID {self.id_piece} is already a king and cannot be promoted yet !")

    def set_state(self, state:EnumStatePiece):
        self.state = state

    def get_color_border(self)->ColorType:
        _color = (
            Colors.PIECE_BORDER_LIGHT 
            if self.player == EnumPlayersColor.P_LIGHT 
            else Colors.PIECE_BORDER_DARK
        )
        map_border = { 
            EnumStatePiece.P_NORMAL : _color,
            EnumStatePiece.P_SELECTED : Colors.PIECE_BORDER_SELECTED,
            EnumStatePiece.P_CAPTURED : _color  # Colors.CELL_DARK
        }
        return map_border[self.state]

    def get_color_area(self)->ColorType:
        if self.state is EnumStatePiece.P_CAPTURED:
            return Colors.CELL_DARK
        return Colors.PIECE_LIGHT if self.player == EnumPlayersColor.P_LIGHT else Colors.PIECE_DARK
    
# Classe usata per definire lo stato delle celle
@enum.unique
class EnumStateCell(enum.Enum):
    C_NORMAL = 0
    C_SELECTION = 1
    C_MOVEMENT_FW = 2
    C_MOVEMENT_RV = 3

class PygameCell:
    """
    """

    def __init__(self, id_dark_cell:int):
        self.id = id_dark_cell
        self.col, self.row = Cells.index2coord(id_dark_cell).as_tuple()
        self._rect : RectType = (
                self.col * CELL_WIDTH, 
                self.row * CELL_HEIGHT, 
                CELL_WIDTH, 
                CELL_HEIGHT
        )
        self._center_pxl : Coordinates2D = Coordinates2D(
            (self.col * CELL_WIDTH) + CELL_WIDTH // 2,
            (self.row * CELL_HEIGHT) + CELL_HEIGHT // 2
        )
        self.reset()

    def reset(self):
        self.state : EnumStateCell = EnumStateCell.C_NORMAL
        self.piece : Optional[PygamePiece] = None

    def get_rect(self)->RectType:
        return self._rect

    def get_center(self)->Coordinates2D:
        return self._center_pxl

    def get_color_cell(self)->ColorType:
        map_cell = { 
            EnumStateCell.C_NORMAL : Colors.FILL_TRANSPARENT, # Colors.CELL_LIGHT if (self.row + self.col) %2 else Colors.CELL_DARK,
            EnumStateCell.C_SELECTION : Colors.CELL_SELECTION,
            EnumStateCell.C_MOVEMENT_FW : Colors.CELL_MOVEMENT_FW,
            EnumStateCell.C_MOVEMENT_RV : Colors.CELL_MOVEMENT_RV,
        }
        return map_cell[self.state]
    
    def is_highlighted(self):
        return self.state is not EnumStateCell.C_NORMAL