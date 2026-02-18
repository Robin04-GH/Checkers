from abc import ABC, abstractmethod
from checkers.engine.game.move import Move

class InferenceInterface(ABC):
    """
    Abstract class to allow the game engine to interface with the 
    inference module without knowing which engine was used
    """

    @abstractmethod
    def run(self, moves:set[Move])->Move:
        """
        """        
        pass

