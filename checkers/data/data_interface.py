from typing import Optional
from abc import ABC, abstractmethod
from checkers.engine.game.pieces import EnumPlayersColor
from checkers.engine.game.state import EnumResult, StateMove

class DataInterface(ABC):
    """
    Abstract class to allow  interface with the 
    data manager module without knowing type data
    """

    @abstractmethod
    def open_data(self, filename:str)->bool:
        """
        """        
        pass

    @abstractmethod
    def close_data(self):
        """
        """        
        pass

    @abstractmethod
    def is_open(self)->bool:
        """
        """        
        pass

    @abstractmethod
    def game_data(self, id_game:str)->bool:
        """
        """        
        pass

    @abstractmethod
    def get_id_game(self)->str:
        """
        """        
        pass

    @abstractmethod
    def next_game(self)->str:
        """
        """        
        pass

    @abstractmethod
    def get_pk_players(self)->tuple[tuple[str, str, str, str]]:
        """
        """        
        pass

    @abstractmethod
    def set_turn(self, number_move:int, player_turn:EnumPlayersColor):
        """
        """        
        pass

    @abstractmethod
    # Returns last move or None.
    def get_move(self)->Optional[tuple[int, ...]]:
        """
        """        
        pass

    @abstractmethod
    # Returns the next move or None if finished.
    # The return tuple indicates the start and end cell
    # Hint: The parser uses the 'x' separator for capture moves, and '-' for simple moves ! 
    def next_move(self)->Optional[tuple[int, ...]]:
        """
        """        
        pass

    @abstractmethod
    def get_result(self)->EnumResult:
        """
        """        
        pass

    @abstractmethod
    def write_game(self, pk_game:str, pk_players:tuple[str,str,str,str]):
        """
        """        
        pass

    @abstractmethod
    def write_move(
            self, 
            number_move:int, player_turn:EnumPlayersColor, state_move:StateMove,
            state_checkerboard:list[int] = None
        ):
        """
        """        
        pass

    @abstractmethod
    def write_result(self, result:EnumResult):
        """
        """        
        pass
