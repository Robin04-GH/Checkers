from typing import Optional
from datetime import datetime
from checkers.data.data_interface import DataInterface
from checkers.engine.game.move import Move
from checkers.engine.game.pieces import EnumPlayersColor
#from checkers.engine.inference_interface import InferenceInterface

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

    def __init__(self):
        self._database : str = ""
        self._pk_game : str = ""
        self._is_open : bool = False

        self._number_move : int = 1
        self._player_turn : EnumPlayersColor = EnumPlayersColor.P_LIGHT        

    def open_data(self, filename:str)->bool:
        self._database = filename
        # self._pk_game = id_game
        # self._is_open = True
        # self.history_db_name (open database files)
        # self.pk_game (if zero starts from the first game)
        # After opening I have access to the methods that return player IDs 
        # with colors, move pointers...

        # TODO : open db connessione
        return True

    def close_data(self):
        # self._database
        # self._is_open = False
        pass

    def is_open(self)->bool:
        return self._is_open
    
    def game_data(self, id_game:str):
        self._pk_game = id_game

        # if '_pk_game' is present (read from db or write after restore) 
        # only checks the presence of the match identifier, otherwise adds the 
        # new match row generating the unique '_pk_game' with '_generate_datetime()' !
        pass

    def get_id_game(self)->str:
        return self._pk_game

    def next_game(self)->str:
        return self._pk_game

    def get_players(self)->tuple[str, str]:
        # check '_pk_game' presence
        # returns the player names (in P_LIGHT, P_DARK order)
        pass

    def set_turn(self, number_move:int, player_turn:EnumPlayersColor):
        self._number_move = number_move
        self._player_turn = player_turn

    def get_move(self)->Optional[tuple[int, ...]]:
        pass

    def set_move(self, move:Move):
        pass

    def set_result(self, result:int):
        # When the game is over set '_pk_game' to the next game (cyclic)
        pass

    def _generate_datetime(self)->str:
        # Generate datetime for primary key game (unique with microseconds).
        # Hint: only returned, not assigned to self.pk_game !        
        return datetime.now().strftime("%Y%m%d%H%M%S%f")
