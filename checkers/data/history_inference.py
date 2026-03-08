from typing import Optional
from checkers.engine.inference_interface import InferenceInterface
from checkers.data.data_interface import DataInterface
from checkers.engine.game.move import Move

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

    def run(self, moves:set[Move])->Optional[Move]:
        history_move : tuple[int, ...] | None = self.data.get_move()

        if history_move is None or len(history_move) < 2:
            raise ValueError(f"HistoryInference : move not present !")
        
        list_moves : list[Move] = []
        history_destinations = history_move[1:]
        for move in moves:
            if move.origin == history_move[0]:
                if move.destinations == history_destinations:
                    # presenti tutte le celle
                    list_moves.clear()
                    list_moves.append(move)
                    break
                elif move.destinations[-1] == history_destinations[-1]:
                    # presente la sola cella destinazione finale
                    list_moves.append(move)

        len_moves : int = len(list_moves)
        if len_moves < 1:
            raise ValueError(f"HistoryInference : mosse non corrispondenti a quelle possibili !")
        
        if len_moves > 1:
            print(f"Storico ambiguo, possibili piu mosse : scelta la prima !")
        return list_moves[0]
