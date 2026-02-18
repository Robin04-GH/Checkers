from checkers.types import DestCellsType
from checkers.graph.pygame.pygame_state import PygameState
from checkers.engine.game.cells import Cells

class GraphInputReceiving:
    """
    """

    def __init__(self, state:PygameState):
        self.state = state

    def print_string(self, string:str, value:float)->int:
        print(f"Msg=" + string + f" Val={value}")
        # self.state.
        return 0

    def reset(self)->int:
        self.state.reset()
        return 0

    def players_pieces(self, cell_piece:tuple[int, int])->int:
        # print(f"Cell={cell_piece[0]} Piece={cell_piece[1]}")
        self.state.add_piece(*cell_piece)
        return 0

    def selection_cells(self, cells:tuple[int, ...])->int:        
        # print(cells)
        self.state.set_selection_cells(cells)
        return 0

    def destination_cells(self, cells:DestCellsType, previous_index:int)->int:        
        # print(cells)
        self.state.set_destination_cells(cells, previous_index)
        return 0
    
    def promoted_king(self, cell:int)->int:
        # print(cell)
        self.state.promoted_king(cell)
        return 0
