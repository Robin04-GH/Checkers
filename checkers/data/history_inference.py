from checkers.engine.inference_interface import InferenceInterface
from checkers.data.data_interface import DataInterface
from checkers.engine.game.move import Move
from checkers.engine.game.state import EnumResult, State

class HistoryInference(InferenceInterface):
    """
    """

    def __init__(self, data:DataInterface):
        super().__init__()
        self.data = data
        if self.data == None:
            raise ValueError(
                f"Class HistoryInference, __init__(): data acquisition class not specified"
            )
        self.last_history_move : tuple[int, ...] | None = None

    def run(self, moves:set[Move], state:State)->Move | None:
        history_move : tuple[int, ...] | None = None
        if not state.is_undo():
            if self.last_history_move is None:
                history_move = self.data.next_move()
            else:
                history_move = self.last_history_move
                self.last_history_move = None        
        else:
            if self.last_history_move is None:
                self.last_history_move = self.data.get_move()
            history_move = state.get_undo_move()        
        
        if history_move is None:
            return None
        
        if len(history_move) < 2:
            raise ValueError(f"HistoryInference : move not present !")            

        list_moves : list[Move] = []
        history_destinations = history_move[1:]
        for move in moves:
            if move.origin == history_move[0]:
                if move.destinations == history_destinations:
                    # all cells present
                    list_moves.clear()
                    list_moves.append(move)
                    break
                elif move.destinations[-1] == history_destinations[-1]:
                    # only the final destination cell is present
                    list_moves.append(move)

        len_moves : int = len(list_moves)
        if len_moves < 1:
            raise ValueError(f"HistoryInference : moves that do not correspond to the possible ones !")
        
        if len_moves > 1:
            print(f"Ambiguous history, several moves possible : first one chosen !")
        return list_moves[0]

    def get_result(self)->EnumResult:
        return self.data.get_result()
    