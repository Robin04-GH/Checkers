from typing import Optional
from checkers.engine.inference_interface import InferenceInterface
from checkers.engine.game.move import Move
from checkers.engine.game.state import State

class Classic(InferenceInterface):
    """
    """

    def __init__(self):
        super().__init__()

    def run(self, moves:set[Move], state:State)->Move | None:
        pass
