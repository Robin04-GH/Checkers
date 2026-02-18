from typing import Optional
from checkers.engine.inference_interface import InferenceInterface
from checkers.engine.game.move import Move

class Classic(InferenceInterface):
    """
    """

    def __init__(self):
        super().__init__()

    def run(self, moves:set[Move])->Optional[Move]:
        pass