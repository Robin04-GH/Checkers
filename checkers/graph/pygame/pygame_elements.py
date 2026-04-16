import enum
from typing import Optional, Callable
from checkers.checkers_types import ColorType, RectType
from checkers.constant import MAX_MAN, MAX_KING, CELL_WIDTH, CELL_HEIGHT, TIMER_PRESCALER, BLENDING_DURATION
from checkers.graph.pygame.colors import Colors
from checkers.engine.game.cells import Coordinates2D, Cells
from checkers.engine.game.pieces import EnumPlayersColor, Pieces
check_valid_piece = Pieces.check_valid_piece

class PygameBlending:
    """
    Class for blending during cell and piece state transitions
    """

    def __init__(self, callback: Callable[[], ColorType]):
        self.get_color_object = callback
        self.timer : Optional[int] = None
        self.color_init : Colors = self.get_color_object()
                
    def initialize_blending(self):        
        if self.timer != None:
            t : float = self.timer / BLENDING_DURATION
            t = max(0.0, min(1.0, t))
            self.color_init = PygameBlending.interpolate_color(self.color_init, self.get_color_object(), t)
        else:
            self.color_init = self.get_color_object()
        self.timer = 0

    @staticmethod
    def interpolate_color(c0:ColorType, c1:ColorType, t:float)->ColorType:
        return (
                c0[0] + (c1[0] - c0[0]) * t,
                c0[1] + (c1[1] - c0[1]) * t,
                c0[2] + (c1[2] - c0[2]) * t,
                c0[3] + (c1[3] - c0[3]) * t
            )

    def update_blending(self)->ColorType:
        self.timer += TIMER_PRESCALER
        t : float = self.timer / BLENDING_DURATION
        t = max(0.0, min(1.0, t))
        if self.timer >= BLENDING_DURATION:
            self.timer = None
            self.color_init = self.get_color_object()
        return PygameBlending.interpolate_color(self.color_init, self.get_color_object(), t)

    def get_color_blend(self)->ColorType:
        if self.timer != None:
            return self.update_blending()
        else:
            return self.get_color_object()

# Class to define the state of the pieces
@enum.unique
class EnumStatePiece(enum.Enum):
    P_NORMAL = 0
    P_SELECTED = 1
    P_CAPTURED = 2

class PygamePiece(PygameBlending):
    """
    Class that defines the properties and state of a piece
    """

    def __init__(self, id_piece:int):
        check_valid_piece(id_piece)
        self.id_piece : int = id_piece
        self.player : EnumPlayersColor = EnumPlayersColor.P_LIGHT if id_piece > 0 else EnumPlayersColor.P_DARK
        self.is_king : bool = True if MAX_MAN < abs(id_piece) <= MAX_KING else False
        self.state = EnumStatePiece.P_NORMAL
        # Hint: after 'self.state' because it is used in 'self.get_color_area' !
        super().__init__(self.get_color_area)

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

    def set_state(self, state:EnumStatePiece, blending:bool=False):
        if self.state != state:
            if blending:
                self.initialize_blending()
            self.state = state

    def get_color_border(self)->ColorType:
        color = (
            Colors.PIECE_BORDER_LIGHT 
            if self.player == EnumPlayersColor.P_LIGHT 
            else Colors.PIECE_BORDER_DARK
        )
        map_border = { 
            EnumStatePiece.P_NORMAL : color,
            EnumStatePiece.P_SELECTED : Colors.PIECE_BORDER_SELECTED,
            EnumStatePiece.P_CAPTURED : color  # Colors.CELL_DARK
        }
        return map_border[self.state]

    def get_color_area(self)->ColorType:
        if self.state == EnumStatePiece.P_CAPTURED:
            return Colors.CELL_DARK
        return Colors.PIECE_LIGHT if self.player == EnumPlayersColor.P_LIGHT else Colors.PIECE_DARK
    
# Class used to define the state of cells
@enum.unique
class EnumStateCell(enum.Enum):
    C_NORMAL = 0
    C_SELECTION = 1
    C_MOVEMENT_FW = 2
    C_MOVEMENT_RV = 3

class PygameCell(PygameBlending):
    """
    Class that defines the ownership and state of a cell on the board
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
        self.state : EnumStateCell = EnumStateCell.C_NORMAL        
        self.piece : Optional[PygamePiece] = None
        # N.B.: dopo 'self.state' perche usata in 'self.get_color_cell' !
        super().__init__(self.get_color_cell)

    def reset(self):
        self.set_state(EnumStateCell.C_NORMAL)
        self.piece = None
        self.timer = None
        self.color_init = self.get_color_cell()

    def set_state(self, state:EnumStateCell, blending:bool=False):
        if self.state != state:
            if blending:
                self.initialize_blending()
            self.state = state
    
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
        return self.state != EnumStateCell.C_NORMAL
        