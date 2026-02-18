from typing import Optional
from checkers.data.view_interface import ViewInterface
from checkers.engine.inference_interface import InferenceInterface
from checkers.config_manager import ConfigManager
from checkers.engine.game.move import Move

class DatabaseManager(ViewInterface):
    """
    Classe gestione database per storico partite.

    Il flusso dati dipende dalla configurazione :
    <mode>  <history_database>  <import_pdn>  <database>    <PDN>       <Descrizione>
      P             -               -           unused      unused      Play
      P             x               -           WR          unused      Play + storico DB
      P             -               x           unused      ?           Play                (PDN non gestibile)
      P             x               x           WR          ?           Play + storico DB   (PDN non gestibile)
      V             -               -           ?           ?           View non possibile !
      V             x               -           RD          unused      View da DB    
      V             -               x           unused      RD          View da PDN
      V             x               x           WR          RD          View da PDN + storico DB (Import PDN->DB)

    Struttura database :
    - Tabella Players (dati giocatori : pk='engine: name', contatori generali)
    - Tabella Games (dati generali partite : data, giocatori, esito)
    - Tabella Moves (storico mosse partite)
    - Tabella States (storico stato scacchiera partite)
    
    """

    def __init__(self, config:ConfigManager):
        self._database : str = ""

    def open_data(self, source:str)->bool:
        self._database = source
        # self.history_db_name (apre file database)
        # self.pk_game (se zero parte dalla prima partita)
        # Dopo l'apertura ho accesso ai metodi che ritornano ID players con colori, puntatore alle mosse ...
        pass

    def close_data(self):
        # self._database
        pass

    def get_players(self, pk_game:str)->tuple[str, str]:
        # check presenza pk_game
        # ritorna i nomi dei giocatori (in ordine P_LIGHT, P_DARK)
        pass

    def get_move(self, num_move:Optional[int]=None)->tuple[int, ...]:
        # ritorna tuple con cella origine e cella finale
        # N.B.: il parser usa separatore 'x' per mosse capture, '-' per mosse simple !
        pass
