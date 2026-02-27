from typing import Optional
from checkers.data.data_interface import DataInterface
from checkers.engine.inference_interface import InferenceInterface
from checkers.config_manager import ConfigManager
from checkers.engine.game.move import Move

class DatabaseManager(DataInterface):
    """
    Database management class for match history.

    The data flow depends on the configuration :
    <mode>  <history_database>  <import_pdn>  <database>    <PDN>       <Description>
      P             -               -           unused      unused      Play
      P             x               -           WR          unused      Play + history DB
      P             -               x           unused      ?           Play                (unmanageable PDN)
      P             x               x           WR          ?           Play + history DB   (unmanageable PDN)
      V             -               -           ?           ?           View not possible !
      V             x               -           RD          unused      View from DB    
      V             -               x           unused      RD          View from PDN
      V             x               x           WR          RD          View from PDN + history DB (Import PDN->DB)

    Database structure:
    - Players table (player data: pk='engine:name', general counters)
    - Games table (general game data: date, players, outcome)
    - Moves table (game move history)
    - States table (game board state history)
    """

    def __init__(self, config:ConfigManager):
        self._config = config
        self._database: str | None = None

    def open_data(self, source:str)->bool:
        self._database = source
        # self.history_db_name (open database files)
        # self.pk_game (if zero starts from the first game)
        # After opening I have access to the methods that return player IDs 
        # with colors, move pointers...
        pass

    def close_data(self):
        # self._database
        pass

    def get_players(self, pk_game:str)->tuple[str, str]:
        # check pk_game presence
        # returns the player names (in P_LIGHT, P_DARK order)
        pass

    def get_move(self, index:Optional[int]=None)->Optional[tuple[int, ...]]:
        pass
