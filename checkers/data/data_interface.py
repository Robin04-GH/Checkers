from typing import Optional
from abc import ABC, abstractmethod

class DataInterface(ABC):
    """
    Abstract class to allow  interface with the 
    data manager module without knowing type data
    """

    @abstractmethod
    def open_data(self, source:str)->bool:
        """
        """        
        pass

    @abstractmethod
    def close_data(self):
        """
        """        
        pass

    @abstractmethod
    def get_players(self, pk_game:str)->tuple[str, str]:
        """
        """        
        pass

    @abstractmethod
    # Returns the move from index (0-based) if specified, 
    # otherwise the next move or None if finished.
    # The return tuple indicates the start and end cell
    # Hint: The parser uses the 'x' separator for capture moves, 
    # and '-' for simple moves!        
    def get_move(self, index:Optional[int]=None)->Optional[tuple[int, ...]]:
        """
        """        
        pass
