from typing import Optional
from checkers.data.view_interface import ViewInterface

class PdnManager(ViewInterface):
    """
    Classe per parsing formato partite in PDN.
    Usata in modalità 'view' per importazione da PDN->DB con 'history_database' 
    o semplice visualizzazione partita.
    """

    def __init__(self):
        pass

    def open_data(self, source:str)->bool:
        pass

    def close_data(self):
        pass

    def get_players(self, pk_game:str)->tuple[str, str]:
        # check presenza pk_game
        # ritorna i nomi dei giocatori (in ordine P_LIGHT, P_DARK)
        pass

    def get_move(self, num_move:Optional[int]=None)->tuple[int, ...]:
        pass
