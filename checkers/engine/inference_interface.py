from abc import ABC, abstractmethod
from checkers.engine.game.move import Move
from checkers.engine.game.state import EnumResult, State

class InferenceInterface(ABC):
    """
    Abstract class to allow the game engine to interface with the 
    inference module without knowing which engine was used
    """

    @abstractmethod
    def run(self, moves:set[Move], state:State)->Move | None:
        """
        """        
        pass
