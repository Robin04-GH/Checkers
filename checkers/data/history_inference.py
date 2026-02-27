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
        # self.data.get_move() ...
        pass
