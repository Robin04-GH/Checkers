# from checkers.engine.game.pieces import EnumPlayersColor
from dataclasses import dataclass

@dataclass
class PlayerStats:
    # Hint: 'engine + ": " + name' represents the primary key in the database!
    # State (local)
    # State variables are loaded by config/restore.
    engine : str = ""
    name : str = ""
    # Hint: the color is implicit in the dict_players = { color : Player }
    # self.color : EnumPlayersColor = EnumPlayersColor.P_LIGHT

    # Game (restore)
    # Game variables from restore (counter_man/king recalculated from board state)
    counter_man : int = 0
    counter_king : int = 0

    # History (database)
    # History variables are loaded from the database (if present)
    counter_game : int = 0
    counter_score : float = 0.0
    """
    Class for management data player
    """
    
    def reset(self):
        self.counter_man = 0
        self.counter_king = 0

    def set_counter_man_king(self, man:int, king:int):
        self.counter_man = man
        self.counter_king = king       

    def load_history_data(self):
        pass