from checkers.checkers_types import DestCellsType
from checkers.graph.pygame.pygame_state import PygameState
from checkers.engine.game.state import StateMove

class GraphInputReceiving:
    """
    """

    def __init__(self, state:PygameState):
        self.state = state

    def print_string(self, string:str, value:float)->int:
        # print(f"Msg=" + string + f" Val={value}")
        return 0

    def timeouts_view(self, timeouts:tuple[int, int, int])->int:
        self.state.set_timeouts(timeouts)
        return 0

    def reset(self)->int:
        self.state.reset()
        return 0

    def players_pieces(self, cell_piece:tuple[int, int])->int:
        # print(f"Cell={cell_piece[0]} Piece={cell_piece[1]}")
        self.state.add_piece(*cell_piece)
        return 0

    def selection_cells(self, cells:tuple[int, ...], selected_cell:int | None = None)->int:        
        # print(cells)
        viewer_mode : bool = True if selected_cell is not None else False
        self.state.set_viewer_mode(viewer_mode)

        if viewer_mode:
            self.state.set_timer_selected(selected_cell)
            
        self.state.set_selection_cells(cells)
        return 0

    def destination_cells(self, cells:DestCellsType, previous_index:int, destinated_index:int | None = None)->int:        
        # print(cells)

        if self.state.get_viewer_mode():
            if destinated_index >= 0:
                self.state.set_timer_destinated(destinated_index) 
            else:
                self.state.set_timer_validated()

        self.state.set_destination_cells(cells, previous_index)
        return 0
    
    def promoted_king(self, cell:int)->int:
        # print(cell)
        self.state.promoted_king(cell)
        return 0
    
    def game_over(self)->int:
        print(f"Press SPACE or left-click to continue ...")
        self.state.set_game_over(True)
        return 0
    
    def request_undo(self, state_move:StateMove)->int:
        if state_move is None:
            self.state.set_lock(False)
            print("Empty undo buffer !")
            return 0

        self.state.restore_state_move(state_move)
        print("Undo executed !")
        return 0
