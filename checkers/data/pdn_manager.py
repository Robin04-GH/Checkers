from typing import Optional
from checkers.data.data_interface import DataInterface

class PdnManager(DataInterface):
    """
    Class for parsing game formats in PDN.
    Used in 'view' mode for importing from PDN->DB with 'history_database'
    or simply viewing games.    
    """

    def __init__(self):
        pass

    def open_data(self, source:str)->bool:
        pass

    def close_data(self):
        pass

    def get_players(self, pk_game:str)->tuple[str, str]:
        # check pk_game presence
        # returns the player names (in P_LIGHT, P_DARK order)        
        pass

    def get_move(self, index:Optional[int]=None)->Optional[tuple[int, ...]]:
        pass
