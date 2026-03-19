import enum
from typing import Optional
from checkers.types import DestCellsType
from checkers.constant import DIM_CKECKERBOARD, MAX_CELL_MOVE, CELL_WIDTH
from checkers.engine.game.cells import Coordinates2D, Cells
from checkers.engine.game.move import Move
from checkers.engine.game.pieces import Pieces
from checkers.engine.game.state import StateMove
from checkers.graph.pygame.pygame_elements import EnumStateCell, PygameCell, EnumStatePiece, PygamePiece
from checkers.graph.pygame.pygame_layers import PygameLayers
from checkers.graph.pygame.pygame_constrain import EnumPygameMoving, Constrain
from dataclasses import dataclass
check_valid_piece = Pieces.check_valid_piece

@enum.unique
class EnumEventMoves(enum.Enum):
    E_NONE = 0
    E_SELECTED = 1
    E_DESTINATED = 2
    E_VALIDATED = 3

@dataclass
class ViewerData:
    mode : bool = False
    timer : int = 0
    type : EnumEventMoves = EnumEventMoves.E_NONE
    target : int = -1

class PygameState(PygameLayers, Constrain):
    """
    Class for managing the state of pieces and cells on the board.
    The state is transmitted by the engine, this class stores it in the graphics thread
    and orchestrates the drawing of objects.
    """

    def __init__(self):
        super().__init__()
        self.state_checkerboard : dict[int, PygameCell] = {}
        # Only dark cells are used to manage the board state.
        for row in range(DIM_CKECKERBOARD):
            for col in range(DIM_CKECKERBOARD):
                if not (row + col) % 2:
                    id_dark_cell : int = Cells.coord2index(Coordinates2D(col, row))
                    Cells.check_valid_cell(id_dark_cell)
                    self.state_checkerboard[id_dark_cell] = PygameCell(id_dark_cell)
        self.active_cell_timers : list[int] = []
        self._viewer : ViewerData = ViewerData()
        self._timeouts : tuple[int, int, int] = (0, 0, 0)
        self._pause : bool = False
        self._lock : bool = False
        self._game_over : bool = False

    def reset(self):
        for (_, cell) in self.state_checkerboard.items():
            cell.reset()
        self.clear_layers()

    def get_cell(self, id_dark_cell:int)->PygameCell:
        if id_dark_cell not in self.state_checkerboard:
            raise KeyError(f"Specified id cell {id_dark_cell} is out of bounds !")        
        return self.state_checkerboard[id_dark_cell]

    def get_piece(self, id_dark_cell:int)->Optional[PygamePiece]:
        cell : PygameCell = self.get_cell(id_dark_cell)       
        return cell.piece

    def add_piece(self, id_dark_cell:int, id_piece:int):
        if self.get_piece(id_dark_cell) != None:
            raise KeyError(f"Specified id cell {id_dark_cell} already contains a piece !")
        
        cell : PygameCell = self.state_checkerboard[id_dark_cell]
        cell.piece = PygamePiece(id_piece)
        self.draw_piece_fix(cell)

    def del_piece(self, id_dark_cell:int)->int:
        if self.get_piece(id_dark_cell) == None:
            raise KeyError(f"Specified id cell {id_dark_cell} is empty !")
        
        cell : PygameCell = self.state_checkerboard[id_dark_cell]
        id_piece = cell.piece.id_piece
        # del self.state_checkerboard[id_dark_cell].piece
        cell.piece = None
        self.draw_piece_fix(cell)
        return id_piece

    def set_selection_cells(self, cells:tuple[int, ...]):
        self.selection_cells = cells
        for id_dark_cell in self.selection_cells:
            cell = self.get_cell(id_dark_cell)
            cell.set_state(EnumStateCell.C_SELECTION, True)
            self.initialize_cell_timer(cell)
            #self.draw_cell(cell)
        self.state_moving = EnumPygameMoving.M_SELECTION

    def delete_selection_cells(self):
        for id_dark_cell in self.selection_cells:
            cell : PygameCell = self.get_cell(id_dark_cell)
            cell.set_state(EnumStateCell.C_NORMAL)
            self.draw_cell(cell)
        self.selection_cells = ()

    def set_selected_cell(self, id_dark_cell:int):
        if id_dark_cell != self.selected_cell:
            # Deselection
            if Cells.is_valid_cell(self.selected_cell):
                cell : PygameCell = self.get_cell(self.selected_cell)
                # Hint: a cell already selected certainly contains a piece !
                cell.piece.set_state(EnumStatePiece.P_NORMAL)
                self.draw_piece_fix(cell)
                self.selected_cell = -1        
            # Selezione
            if Cells.is_valid_cell(id_dark_cell):
                cell : PygameCell = self.get_cell(id_dark_cell)
                # You can only select pieces in cells in EnumStateCell.C_SELECTION
                if cell.state == EnumStateCell.C_SELECTION:
                    cell.piece.set_state(EnumStatePiece.P_SELECTED)
                    self.draw_piece_fix(cell)
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
            cell : PygameCell = self.get_cell(id_dark_cell)
            if cell.state == EnumStateCell.C_SELECTION:
                if cell.piece.state == EnumStatePiece.P_SELECTED and self.selected_cell == id_dark_cell:
                    # If the cell is selectable with the piece selected, the piece 
                    # is moved from the static pieces layer to the movable one.
                    self.delete_selection_cells()
                    self.init_coordinates(cell.get_center())
                    self.piece_moving = cell.piece
                    cell.piece = None
                    self.initialize_move(cell)
                    self.state_moving = EnumPygameMoving.M_SELECTED
                    # print(f"EnumPygameMoving.M_SELECTED")
                    return True
        return False

    def stop_moving(self, abort:bool = False)->Optional[Move]:
        move : Move = None
        is_completed : bool = False
        if not abort:
            if self.destination_cells.count(-1) == MAX_CELL_MOVE - 1 and self.previous_index != -1:
                is_completed = True

        self.finalize_move()

        if is_completed:
            # move validation
            move = Move(self.selected_cell, tuple(self.move_destinations), tuple(self.move_captures))
            self.finalize_selected_cell(self.actual_cell)
            self.finalize_captured_cell(False)
        else:
            # aborted move
            self.finalize_selected_cell(self.selected_cell)
            self.finalize_captured_cell(True)
            
        self.clear_moving()
        return move

    def clear_moving(self):
        self.move_captures.clear()
        self.move_destinations.clear()
        self.delete_destination_cells()
        self.previous_index = -1
        self.state_moving = EnumPygameMoving.M_IDLE
        # print(f"EnumPygameMoving.M_IDLE")        

    def set_destination_cells(self, dest_cells:DestCellsType, previous_index:int):
        # Hint: I may lose the selection while waiting for the destination cells !
        if not Cells.is_valid_cell(self.actual_cell):            
            return
        
        self.destination_cells = dest_cells
        self.previous_index = previous_index
        
        dest_center : list[Optional[Coordinates2D]] = []
        for index, id_dark_cell in enumerate(self.destination_cells):
            if Cells.is_valid_cell(id_dark_cell):
                cell = self.get_cell(id_dark_cell)
                cell.set_state(
                    EnumStateCell.C_MOVEMENT_FW 
                    if index != self.previous_index 
                    else EnumStateCell.C_MOVEMENT_RV,
                    True
                )
                self.initialize_cell_timer(cell)
                #self.draw_cell(cell)

                dest_center.append(cell.get_center())
            else:
                dest_center.append(None)

        self.set_destination_centers(tuple(dest_center))
        cell = self.get_cell(self.actual_cell)
        self.set_actual_center(cell.get_center())

        self.state_moving = EnumPygameMoving.M_DESTINATION               

    def delete_destination_cells(self):
        for id_dark_cell in self.destination_cells:
            if Cells.is_valid_cell(id_dark_cell):
                cell : PygameCell = self.get_cell(id_dark_cell)
                cell.set_state(EnumStateCell.C_NORMAL)
                self.draw_cell(cell)
        self.destination_cells = (-1, -1, -1, -1)

    def inside_destinations(self, pixel:Coordinates2D)->int:
        self.draw_piece_move(pixel)
        id_dark_cell = self.get_cell_from_pos(pixel)
        if Cells.is_valid_cell(id_dark_cell):
            try:
                index = self.destination_cells.index(id_dark_cell)
                cell = self.get_cell(id_dark_cell)
                center = cell.get_center()
                distance_2 = (pixel.x - center.x)**2 + (pixel.y - center.y)**2
                norm_2 = distance_2 * 100 // (CELL_WIDTH * CELL_WIDTH)
                # Check if inside a destination cell
                if norm_2 < 4:
                    return index
            except ValueError:
                pass
        return -1

    def check_capture_cells(self, actual_cell:int, destination_cell:int)->int:
        actual_coor : Coordinates2D = Cells.index2coord(actual_cell)
        destination_coor : Coordinates2D = Cells.index2coord(destination_cell)
        if (
            abs(actual_coor.col - destination_coor.col) == 2 and
            abs(actual_coor.row - destination_coor.row) == 2
        ):
            _capture_coor : Coordinates2D = Coordinates2D(
                ((actual_coor.col + destination_coor.col) // 2),
                ((actual_coor.row + destination_coor.row) // 2)
            )            
            return Cells.coord2index(_capture_coor)
        return -1

    def finalize_selected_cell(self, id_dark_cell:int):
        cell = self.get_cell(id_dark_cell)
        cell.piece = self.piece_moving
        self.piece_moving = None
        cell.piece.set_state(EnumStatePiece.P_NORMAL)
        self.selected_cell = -1
        self.actual_cell = -1
        self.draw_piece_fix(cell)

    def finalize_captured_cell(self, capture:bool):
        for id_dark_cell in self.move_captures:
            cell = self.get_cell(id_dark_cell)
            if capture:
                cell.piece.set_state(EnumStatePiece.P_NORMAL)
            else:
                cell.piece = None
            self.draw_piece_fix(cell)        

    def set_captured_cell(self, id_dark_cell:int, is_forward:bool):
        if Cells.is_valid_cell(id_dark_cell):
            cell : PygameCell = self.get_cell(id_dark_cell)
            if cell.piece == None:
                raise KeyError(f"Class PygameState, set_captured_cell(): specified id cell {id_dark_cell} is empty !")

            cell.piece.set_state(EnumStatePiece.P_CAPTURED if is_forward else EnumStatePiece.P_NORMAL, True)
            #self.draw_piece_fix(cell)
            self.initialize_cell_timer(cell)

    def set_destinated_cell(self, index:int):
        captured_cell : int = self.check_capture_cells(self.actual_cell, self.destination_cells[index])
        is_forward : bool = index != self.previous_index

        self.actual_cell = self.destination_cells[index]
        self.delete_destination_cells()
            
        if is_forward:
            self.move_destinations.append(self.actual_cell)
            if captured_cell != -1:
                self.move_captures.append(captured_cell)
        else:
            self.move_destinations = self.move_destinations[:-1]
            if len(self.move_captures) > 0:
                self.move_captures = self.move_captures[:-1]

        self.set_captured_cell(captured_cell, is_forward)

        self.state_moving = EnumPygameMoving.M_DESTINATED

    def set_position_keyboard(self, index:int):
        if (0 <= index < MAX_CELL_MOVE):
            id_dark_cell = self.destination_cells[index]
            if Cells.is_valid_cell(id_dark_cell):
                cell = self.get_cell(id_dark_cell)  
                self.set_coor_constrained(cell.get_center())
    
    def promoted_king(self, id_dark_cell:int):
        if Cells.is_valid_cell(id_dark_cell):
            cell : PygameCell = self.get_cell(id_dark_cell)
            if cell.piece == None:
                raise KeyError(f"Class PygameState, promoted_king(): specified id cell {id_dark_cell} is empty !")
            cell.piece.promotion_king()
            self.draw_piece_fix(cell)

    def initialize_cell_timer(self, cell:PygameCell):
        id : int = cell.id
        if id not in self.active_cell_timers:
            self.active_cell_timers.append(id)

    def scan_cell_timer(self):
        for id_dark_cell in self.active_cell_timers:
            cell : PygameCell = self.get_cell(id_dark_cell)
            if cell.timer == None and (cell.piece == None or cell.piece.timer == None):
                self.active_cell_timers.remove(id_dark_cell)
            else:
                if cell.timer != None:
                    self.draw_cell(cell)              
                if cell.piece != None:
                    if cell.piece.timer != None:
                        self.draw_piece_fix(cell) 

    def moving_timer(self, elapsed:int)->Optional[int]:
        index : Optional[int] = None

        if self.piece_moving != None:
            # self.constrain_filtered(self.get_coor_constrained())
            # self.smoothing_filtered(self.get_coor_constrained())
            # self.speed_clamp_filtered(self.get_coor_constrained())
            self.critically_damped_spring(self.get_coor_constrained(), elapsed)
            # self.easing_filtered(self.get_coor_constrained(), self.get_coef_constrained())

            index = self.inside_destinations(self.get_coor_filtered())

        return index
        
    def set_timeouts(self, timeouts:tuple[int, int, int]):
        self._timeouts = timeouts

    def viewer_timer(self, elapsed:int)->EnumEventMoves:            
        if self._viewer.mode:
            if self._viewer.type != EnumEventMoves.E_NONE:
                if self.get_pause():
                    elapsed = 0

                if self._viewer.timer > 0:
                    self._viewer.timer -= elapsed
                    if self._viewer.timer <= 0:
                        match self._viewer.type:
                            case EnumEventMoves.E_SELECTED:
                                self.set_selected_cell(self._viewer.target)
                                if self.start_moving(self.selected_cell):
                                    return self._viewer.type
                                
                            case EnumEventMoves.E_DESTINATED:
                                self.set_position_keyboard(self._viewer.target)
                                return self._viewer.type
                            
                            case EnumEventMoves.E_VALIDATED:
                                return self._viewer.type
        
        return EnumEventMoves.E_NONE
    
    def get_viewer_mode(self)->bool:
        return self._viewer.mode

    def set_viewer_mode(self, mode:bool):
        self._viewer.mode = mode

    def finaling_viewer_timer(self):
        if self._viewer.mode and self._viewer.type != EnumEventMoves.E_NONE:
            self._viewer.timer = 1

    def set_timer_selected(self, cell:int):
        self._viewer.timer = self._timeouts[0]
        self._viewer.type = EnumEventMoves.E_SELECTED
        self._viewer.target = cell

    def set_timer_destinated(self, index:int):
        self._viewer.timer = self._timeouts[1]
        self._viewer.type = EnumEventMoves.E_DESTINATED
        self._viewer.target = index

    def set_timer_validated(self):
        self._viewer.timer = self._timeouts[2]
        self._viewer.type = EnumEventMoves.E_VALIDATED

    def get_pause(self)->bool:
        return self._pause

    def set_pause(self, status:bool):
        if status != self._pause:
            if self._viewer.mode and not self._lock:
                print(f"Pause Enabled") if status == True else print(f"Pause Disabled")                 
                self._pause = status

    def set_lock(self, status:bool):
        if status != self._lock:
            self._lock = status

    def get_game_over(self)->bool:
        return self._game_over
    
    def set_game_over(self, status:bool):
        self._game_over = status

    def restore_state_move(self, state_move:StateMove):
        # Cancellation of any temporary move in progress
        if self.state_moving == EnumPygameMoving.M_SELECTION:
            self.delete_selection_cells()
            self.clear_moving()
        else:
            self.stop_moving(True)

        # restore previous state with state_move
        self.add_piece(state_move.move.origin, state_move.piece_move)
        self.del_piece(state_move.move.destinations[-1])
        for index_cell, id_dark_cell in enumerate(state_move.move.captures):
            self.add_piece(id_dark_cell, state_move.pieces_captured[index_cell])
        self.set_lock(False)
