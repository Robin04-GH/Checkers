from enum import IntFlag, auto, unique
from  typing import Optional
import pygame
from checkers.types import ColorType, RectType
from checkers.constant import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_WIDTH, CELL_HEIGHT, DIM_CKECKERBOARD
from checkers.graph.pygame.colors import Colors
from checkers.engine.game.cells import Coordinates2D, Cells
from checkers.graph.pygame.pygame_elements import PygameCell, PygamePiece

# Classe per definire lo stato dei pezzi
@unique
class EnumLayerMask(IntFlag):
    L_MASK_BOARD = auto()
    L_MASK_HIGHLIGHT = auto()
    L_MASK_PIECES = auto()
    L_MASK_DRAG = auto()

    L_MASK_HIGHLIGHT_ON = L_MASK_HIGHLIGHT | L_MASK_PIECES
    L_MASK_HIGHLIGHT_OFF = L_MASK_BOARD | L_MASK_PIECES | L_MASK_DRAG
    L_MASK_MOVING = L_MASK_BOARD | L_MASK_HIGHLIGHT | L_MASK_PIECES | L_MASK_DRAG

class PygameLayers:
    """
    """

    def __init__(self):
        super().__init__()
        self._screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self._screen = pygame.display.set_mode(self._screen_size)
        pygame.display.set_caption("Checkers")
        
        self._board_layer : pygame.Surface = pygame.Surface(self._screen_size)
        self._highlight_layer : pygame.Surface = pygame.Surface(self._screen_size, pygame.SRCALPHA)
        self._pieces_layer : pygame.Surface = pygame.Surface(self._screen_size, pygame.SRCALPHA)
        self._drag_layer : pygame.Surface = pygame.Surface(self._screen_size, pygame.SRCALPHA)
        self._dirty_rects : list[tuple[RectType, EnumLayerMask]] = []
        self._clock = pygame.time.Clock()

        self.piece_moving : Optional[PygamePiece] = None
        self.piece_pos : Optional[Coordinates2D] = None

        # draw static checkerboard
        self.draw_checkerboard()

    def validate_rect(self, rect:RectType, mask:EnumLayerMask):
        self._dirty_rects.append((rect, mask))

    def clear_layers(self):
        self._highlight_layer.fill(Colors.FILL_TRANSPARENT)
        self._pieces_layer.fill(Colors.FILL_TRANSPARENT)
        self._drag_layer.fill(Colors.FILL_TRANSPARENT)
        # Validate total refresh
        self.validate_rect(self._board_layer.get_rect(), EnumLayerMask.L_MASK_BOARD)

    def refresh_frame(self):
        if self._dirty_rects:
            for rect, mask in self._dirty_rects:
                # Composer layers
                if mask & EnumLayerMask.L_MASK_BOARD:
                    self._screen.blit(self._board_layer, rect, rect)
                if mask & EnumLayerMask.L_MASK_HIGHLIGHT:
                    self._screen.blit(self._highlight_layer, rect, rect)
                if mask & EnumLayerMask.L_MASK_PIECES:
                    self._screen.blit(self._pieces_layer, rect, rect)
                if mask & EnumLayerMask.L_MASK_DRAG:
                    self._screen.blit(self._drag_layer, rect, rect)

            pygame.display.update([rect for rect, _ in self._dirty_rects])
            self._dirty_rects.clear()
        else:       
            pygame.display.flip()   
            # In assenza di dirty comunque refresh temporizzato,
            # update() non garantisce che l’intera finestra sia sincronizzata con il backbuffer.
            self._clock.tick(6)            

    # Draw static checkerboard
    def draw_checkerboard(self):
        for row in range(DIM_CKECKERBOARD):
            for col in range(DIM_CKECKERBOARD):
                _color : ColorType = Colors.CELL_LIGHT if (row + col) % 2 else Colors.CELL_DARK
                _rect : RectType = (col * CELL_WIDTH, row * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
                self._raw_draw_cell(self._board_layer, _color, _rect)
        self.validate_rect(self._board_layer.get_rect(), EnumLayerMask.L_MASK_BOARD)

    def draw_cell(self, cell:PygameCell):
        self._raw_draw_cell(self._highlight_layer, cell.get_color_cell(), cell.get_rect())
        self.validate_rect(
            cell.get_rect(), 
            EnumLayerMask.L_MASK_HIGHLIGHT_ON if cell.is_highlighted() else EnumLayerMask.L_MASK_HIGHLIGHT_OFF
        )

    def draw_piece_fix(self, cell:PygameCell):
        if cell.piece != None:
            self._raw_draw_piece(
                self._pieces_layer, 
                cell.piece.get_color_area(), 
                cell.piece.get_color_border(), 
                cell.get_center(),
                cell.piece.is_king
            )
            self.validate_rect(cell.get_rect(), EnumLayerMask.L_MASK_PIECES)
        else:
            self._pieces_layer.fill(Colors.FILL_TRANSPARENT, cell.get_rect())
            self.validate_rect(cell.get_rect(), EnumLayerMask.L_MASK_BOARD)

    def initialize_move(self, cell:PygameCell):
        self.draw_piece_fix(cell)
        self.draw_piece_move(cell.get_center())

    def finalize_move(self):
        self.clear_piece_move()
        self.piece_pos = None

    def get_rect_move(self, pixel:Coordinates2D)->RectType:
        _rect : RectType = (
            pixel.x - CELL_WIDTH // 2, 
            pixel.y - CELL_HEIGHT // 2, 
            CELL_WIDTH, 
            CELL_HEIGHT
        )
        # print(f"Rect : {_rect}")
        return _rect

    def clear_piece_move(self):
        if self.piece_pos != None:
            self._drag_layer.fill(Colors.FILL_TRANSPARENT, self.get_rect_move(self.piece_pos))
            self.validate_rect(self.get_rect_move(self.piece_pos), EnumLayerMask.L_MASK_MOVING)

    def draw_piece_move(self, pixel:Coordinates2D):             
        if pixel != self.piece_pos:  
            # Cancellazione vecchia posizione pezzo
            self.clear_piece_move()
            # Disegno nuova posizione pezzo
            self._raw_draw_piece(
                    self._drag_layer, 
                    self.piece_moving.get_color_area(), 
                    self.piece_moving.get_color_border(), 
                    pixel,
                    self.piece_moving.is_king
            )             
            self.piece_pos = pixel   
            self.validate_rect(self.get_rect_move(pixel), EnumLayerMask.L_MASK_MOVING)

    def get_cell_from_pos(self, pixel:Coordinates2D)->int:
        _col = pixel.x // CELL_WIDTH 
        _row = pixel.y // CELL_HEIGHT
        
        if not (0 <= _row < DIM_CKECKERBOARD and 0 <= _col < DIM_CKECKERBOARD):
            return -1
        
        # N.B.: ritorna solo l'id delle celle dark, se la cella è light ritorna -1 !
        return Cells.coord2index(Coordinates2D(_col, _row))

    # Raw draw cell
    def _raw_draw_cell(self, layer:pygame.Surface, color:ColorType, rect:RectType):
        pygame.draw.rect(layer, color, rect)
    
    # Raw draw piece      
    def _raw_draw_piece(
            self, 
            layer:pygame.Surface, 
            color_area:ColorType, 
            color_border:ColorType, 
            pixel:Coordinates2D,
            is_king:bool):
        for reduce in range(0, 5 if is_king else 1, 4):
            # Border
            pygame.draw.circle(
                layer, 
                color_border, 
                (pixel.x, pixel.y), 
                CELL_WIDTH//2 - 8 - reduce
            )
            # Area
            pygame.draw.circle(
                layer, 
                color_area, 
                (pixel.x, pixel.y), 
                CELL_WIDTH//2 - 10 - reduce
            )
    