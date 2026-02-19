import enum
from typing import Optional
from checkers.types import DestCellsType
from checkers.constant import DIM_CKECKERBOARD, MAX_CELL_MOVE, CELL_WIDTH
from checkers.engine.game.cells import Coordinates2D, Cells
from checkers.engine.game.move import Move
from checkers.graph.pygame.pygame_elements import EnumStateCell, PygameCell, EnumStatePiece, PygamePiece
from checkers.graph.pygame.pygame_layers import PygameLayers
from checkers.graph.pygame.pygame_constrain import EnumPygameMoving, Constrain
from checkers.engine.game.pieces import Pieces
check_valid_piece = Pieces.check_valid_piece

class PygameState(PygameLayers, Constrain):   # MovingState
    """
    """

    def __init__(self):
        super().__init__()
        self.state_checkerboard : dict[int, PygameCell] = {}
        # Per la gestione dello stato scacchiera si usano le sole celle scure
        for row in range(DIM_CKECKERBOARD):
            for col in range(DIM_CKECKERBOARD):
                if not (row + col) % 2:
                    _id_dark_cell : int = Cells.coord2index(Coordinates2D(col, row))
                    Cells.check_valid_cell(_id_dark_cell)
                    self.state_checkerboard[_id_dark_cell] = PygameCell(_id_dark_cell)
        self.active_cell_timers : list[int] = []

    def reset(self):
        for (_, _cell) in self.state_checkerboard.items():
            _cell.reset()
        self.clear_layers()

    def get_cell(self, id_dark_cell:int)->PygameCell:
        if id_dark_cell not in self.state_checkerboard:
            raise KeyError(f"Specified id cell {id_dark_cell} is out of bounds !")        
        return self.state_checkerboard[id_dark_cell]

    def get_piece(self, id_dark_cell:int)->Optional[PygamePiece]:
        _cell : PygameCell = self.get_cell(id_dark_cell)       
        return _cell.piece

    def add_piece(self, id_dark_cell:int, id_piece:int):
        if self.get_piece(id_dark_cell) != None:
            raise KeyError(f"Specified id cell {id_dark_cell} already contains a piece !")
        
        _cell : PygameCell = self.state_checkerboard[id_dark_cell]
        _cell.piece = PygamePiece(id_piece)
        self.draw_piece_fix(_cell)

    def del_piece(self, id_dark_cell:int)->int:
        if self.get_piece(id_dark_cell) == None:
            raise KeyError(f"Specified id cell {id_dark_cell} is empty !")
        
        _id_piece = self.state_checkerboard[id_dark_cell].piece.id_piece
        # del self.state_checkerboard[id_dark_cell].piece
        self.state_checkerboard[id_dark_cell].piece = None
        return _id_piece

    def set_selection_cells(self, cells:tuple[int, ...]):
        self.selection_cells = cells
        for _id_dark_cell in self.selection_cells:
            _cell = self.get_cell(_id_dark_cell)
            _cell.set_state(EnumStateCell.C_SELECTION) #, True)
            #self.initialize_cell_timer(_cell)
            self.draw_cell(_cell)
        self.state_moving = EnumPygameMoving.M_SELECTION

    def delete_selection_cells(self):
        for _id_dark_cell in self.selection_cells:
            _cell : PygameCell = self.get_cell(_id_dark_cell)
            _cell.set_state(EnumStateCell.C_NORMAL)
            self.draw_cell(_cell)
        self.selection_cells = ()

    def set_selected_cell(self, id_dark_cell:int):
        if id_dark_cell != self.selected_cell:
            # Deselezione
            if Cells.is_valid_cell(self.selected_cell):
                _cell : PygameCell = self.get_cell(self.selected_cell)
                # N.B.: una cella già selezionata contiene sicuramente un pezzo !
                _cell.piece.set_state(EnumStatePiece.P_NORMAL)
                self.draw_piece_fix(_cell)
                self.selected_cell = -1        
            # Selezione
            if Cells.is_valid_cell(id_dark_cell):
                _cell : PygameCell = self.get_cell(id_dark_cell)
                # E' possibile selezionare solo pezzi in celle in EnumStateCell.C_SELECTION
                if _cell.state is EnumStateCell.C_SELECTION:
                    _cell.piece.set_state(EnumStatePiece.P_SELECTED)
                    self.draw_piece_fix(_cell)
                    self.selected_cell = id_dark_cell
            self.actual_cell = self.selected_cell

    def get_next_selected_cell(self)->int:
        # next_value = self.selection_cells[(self.selection_cells.index(self.selected_cell) + 1) % len(self.selection_cells)] if self.selected_cell in self.selection_cells else self.selection_cells[0]
        
        try:
            i = self.selection_cells.index(self.selected_cell)
            next_value = self.selection_cells[(i + 1) % len(self.selection_cells)]
        except ValueError:
            next_value = self.selection_cells[0]
        
        return next_value
    
    def start_moving(self, id_dark_cell:int)->bool:
        if Cells.is_valid_cell(id_dark_cell):
            _cell : PygameCell = self.get_cell(id_dark_cell)
            if _cell.state is EnumStateCell.C_SELECTION:
                if _cell.piece.state == EnumStatePiece.P_SELECTED and self.selected_cell == id_dark_cell:
                    # Se cella selezionabile con pezzo selezionato, il pezzo viene spostato dal layer dei
                    # pezzi statici a quello muovibile
                    self.delete_selection_cells()
                    self.init_coordinates(_cell.get_center())
                    self.piece_moving = _cell.piece
                    _cell.piece = None
                    self.initialize_move(_cell)
                    self.state_moving = EnumPygameMoving.M_SELECTED
                    print(f"EnumPygameMoving.M_SELECTED")
                    return True
        return False

    def stop_moving(self)->Optional[Move]:
        _move : Move = None
        _is_completed : bool = False
        if self.destination_cells.count(-1) == MAX_CELL_MOVE - 1 and self.previous_index != -1:
            _is_completed = True

        self.finalize_move()

        if _is_completed:
            # validazione mossa
            _move = Move(self.selected_cell, tuple(self.move_destinations), tuple(self.move_captures))
            self.finalize_selected_cell(self.actual_cell)
            self.finalize_captured_cell(False)
        else:
            # mossa abortita
            self.finalize_selected_cell(self.selected_cell)
            self.finalize_captured_cell(True)
            
        self.move_captures.clear()
        self.move_destinations.clear()
        self.delete_destination_cells()
        self.previous_index = -1
        self.state_moving = EnumPygameMoving.M_IDLE
        print(f"EnumPygameMoving.M_IDLE")        
        return _move

    def set_destination_cells(self, dest_cells:DestCellsType, previous_index:int):
        # N.B.: potrei perdere la selezione in attesa delle celle destinazione !
        if not Cells.is_valid_cell(self.actual_cell):            
            return
        
        self.destination_cells = dest_cells
        self.previous_index = previous_index
        
        _dest_center : list[Optional[Coordinates2D]] = []
        for _index, _id_dark_cell in enumerate(self.destination_cells):
            if Cells.is_valid_cell(_id_dark_cell):
                _cell = self.get_cell(_id_dark_cell)
                _cell.set_state(
                    EnumStateCell.C_MOVEMENT_FW 
                    if _index != self.previous_index 
                    else EnumStateCell.C_MOVEMENT_RV
                    # True
                )
                #self.initialize_cell_timer(_cell)
                self.draw_cell(_cell)

                _dest_center.append(_cell.get_center())
            else:
                _dest_center.append(None)

        self.set_destination_centers(tuple(_dest_center))
        _cell = self.get_cell(self.actual_cell)
        self.set_actual_center(_cell.get_center())

        self.state_moving = EnumPygameMoving.M_DESTINATION               

    def delete_destination_cells(self):
        for _id_dark_cell in self.destination_cells:
            if Cells.is_valid_cell(_id_dark_cell):
                _cell : PygameCell = self.get_cell(_id_dark_cell)
                _cell.set_state(EnumStateCell.C_NORMAL)
                self.draw_cell(_cell)
        self.destination_cells = (-1, -1, -1, -1)

    def inside_destinations(self, pixel:Coordinates2D)->int:
        self.draw_piece_move(pixel)
        _id_dark_cell = self.get_cell_from_pos(pixel)
        if Cells.is_valid_cell(_id_dark_cell):
            try:
                _index = self.destination_cells.index(_id_dark_cell)
                _cell = self.get_cell(_id_dark_cell)
                _center = _cell.get_center()
                _distance_2 = (pixel.x - _center.x)**2 + (pixel.y - _center.y)**2
                _norm_2 = _distance_2 * 100 // (CELL_WIDTH * CELL_WIDTH)
                # Controllo se interno ad una cella destinazione
                if _norm_2 < 4:
                    return _index
            except ValueError:
                pass
        return -1

    def check_capture_cells(self, actual_cell:int, destination_cell:int)->int:
        _actual_coor : Coordinates2D = Cells.index2coord(actual_cell)
        destination_coor : Coordinates2D = Cells.index2coord(destination_cell)
        if (
            abs(_actual_coor.col - destination_coor.col) == 2 and
            abs(_actual_coor.row - destination_coor.row) == 2
        ):
            _capture_coor : Coordinates2D = Coordinates2D(
                ((_actual_coor.col + destination_coor.col) // 2),
                ((_actual_coor.row + destination_coor.row) // 2)
            )            
            return Cells.coord2index(_capture_coor)
        return -1

    def finalize_selected_cell(self, id_dark_cell:int):
        _cell = self.get_cell(id_dark_cell)
        _cell.piece = self.piece_moving
        self.piece_moving = None
        _cell.piece.set_state(EnumStatePiece.P_NORMAL)
        self.selected_cell = -1
        self.actual_cell = -1
        self.draw_piece_fix(_cell)

    def finalize_captured_cell(self, capture:bool):
        for _id_dark_cell in self.move_captures:
            _cell = self.get_cell(_id_dark_cell)
            if capture:
                _cell.piece.set_state(EnumStatePiece.P_NORMAL)
            else:
                _cell.piece = None
            self.draw_piece_fix(_cell)        

    def set_captured_cell(self, id_dark_cell:int, is_forward:bool):
        if Cells.is_valid_cell(id_dark_cell):
            _cell : PygameCell = self.get_cell(id_dark_cell)
            if _cell.piece == None:
                raise KeyError(f"Class PygameState, set_captured_cell(): specified id cell {id_dark_cell} is empty !")

            _cell.piece.set_state(EnumStatePiece.P_CAPTURED if is_forward else EnumStatePiece.P_NORMAL, True)
            #self.draw_piece_fix(_cell)
            self.initialize_cell_timer(_cell)

    def set_destinated_cell(self, index:int):
        _captured_cell : int = self.check_capture_cells(self.actual_cell, self.destination_cells[index])
        _is_forward : bool = index != self.previous_index

        self.actual_cell = self.destination_cells[index]
        self.delete_destination_cells()
            
        if _is_forward:
            self.move_destinations.append(self.actual_cell)
            if _captured_cell != -1:
                self.move_captures.append(_captured_cell)
        else:
            self.move_destinations = self.move_destinations[:-1]
            if len(self.move_captures) > 0:
                self.move_captures = self.move_captures[:-1]

        self.set_captured_cell(_captured_cell, _is_forward)

        self.state_moving = EnumPygameMoving.M_DESTINATED

    def set_position_keyboard(self, index:int):
        if (0 <= index < MAX_CELL_MOVE):
            _id_dark_cell = self.destination_cells[index]
            if Cells.is_valid_cell(_id_dark_cell):
                _cell = self.get_cell(_id_dark_cell)  
                self.set_coor_constrained(_cell.get_center())
    
    def promoted_king(self, id_dark_cell:int):
        if Cells.is_valid_cell(id_dark_cell):
            _cell : PygameCell = self.get_cell(id_dark_cell)
            if _cell.piece == None:
                raise KeyError(f"Class PygameState, promoted_king(): specified id cell {id_dark_cell} is empty !")
            _cell.piece.promotion_king()
            self.draw_piece_fix(_cell)

    def initialize_cell_timer(self, cell:PygameCell):
        _id : int = cell.id
        if _id not in self.active_cell_timers:
            self.active_cell_timers.append(_id)

    def scan_cell_timer(self):
        for _id_dark_cell in self.active_cell_timers:
            _cell : PygameCell = self.get_cell(_id_dark_cell)
            if _cell.timer == None and (_cell.piece == None or _cell.piece.timer == None):
                self.active_cell_timers.remove(_id_dark_cell)
            else:
                if _cell.timer != None:
                    self.draw_cell(_cell)              
                if _cell.piece != None:
                    if _cell.piece.timer != None:
                        self.draw_piece_fix(_cell) 

    def moving_timer(self, elapsed:int)->Optional[int]:
        _index : Optional[int] = None

        if self.piece_moving != None:
            # self.constrain_filtered(self.get_coor_constrained())
            # self.smoothing_filtered(self.get_coor_constrained())
            self.critically_damped_spring(self.get_coor_constrained(), elapsed)
            # self.easing_filtered(self.get_coor_constrained(), self.get_coef_constrained())

            _index = self.inside_destinations(self.get_coor_filtered())
        
        return _index
