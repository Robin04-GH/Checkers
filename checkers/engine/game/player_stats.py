# from checkers.engine.game.pieces import EnumPlayersColor
from dataclasses import dataclass

@dataclass
class PlayerStats:
    # N.B.: 'engine + ": " + name' rappresenta la chiave primaria nel database ! 
    # State (local)
    # Le variabili State sono caricate dal config/restore.
    engine : str = ""
    name : str = ""
    # N.B.: il colore è implicito nella dict_players = { color : Player }
    # self.color : EnumPlayersColor = EnumPlayersColor.P_LIGHT

    # Game (restore)
    # Le variabili Game dal restore (counter_man/king ricalcolate dallo stato scacchiera)
    counter_man : int = 0
    counter_king : int = 0

    # History (database)
    # Le variabili History sono caricate dal database (se presente)
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