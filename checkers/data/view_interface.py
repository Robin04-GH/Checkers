from typing import Optional
from abc import ABC, abstractmethod

class ViewInterface(ABC):
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
    def get_move(self, num_move:Optional[int]=None)->tuple[int, ...]:
        """
        """        
        pass
