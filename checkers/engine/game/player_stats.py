# from checkers.engine.game.pieces import EnumPlayersColor
from dataclasses import dataclass

@dataclass
class PlayerStats:
    # Hint: 'engine + ": " + name' represents the primary key in the database!
    # State (local)
    # State variables are loaded by config/restore or import resource.
    engine : str = ""
    name : str = ""
    # Hint: the color is implicit in data_players = { color : Player } of class State.
    # self.color : EnumPlayersColor = EnumPlayersColor.P_LIGHT

    # Game (restore)
    # Game variables from restore (counter_man/king recalculated from board state)
    cnt_man : int = 0
    cnt_king : int = 0

    # History (database)
    # Local history variables that can increment statistical counts in the database (when enabled)
    # Hint: in the absence of import resources, if the players are not changed,
    # these data are still incremented locally !    
    cnt_wins : int = 0
    cnt_draws : int = 0
    cnt_losses : int = 0

    cnt_game : int = 0
    perc_score : int = 0
    """
    A class for managing player data, classified as :
    - state class variables (such as player IDs)
    - game-specific variables not contained in the State class
    - variables that can be saved in a statistics database

    PlayerStats locally accumulates statistical data for each player in a match
    only within an application session, as long as each player continues
    to be present in the matches (regardless of whether light or dark).
    The counters are reset with each player change (typically during data import).
    For persistence, database export must be enabled.
    """
    
    def reset_game_data(self):
        self.cnt_man = 0
        self.cnt_king = 0

    def reset_local_history(self):
        self.cnt_wins = 0
        self.cnt_draws = 0
        self.cnt_losses = 0

        self.cnt_game = 0
        self.perc_score = 0

    def init_player(self, engine:str, name:str):
        if self.engine != engine or self.name != name:
            self.engine = engine
            self.name = name
            self.reset_local_history()

        self.reset_game_data()

    def set_counter_man_king(self, man:int, king:int):
        self.cnt_man = man
        self.cnt_king = king       

    def add_local_history(self, stats:tuple[int, int, int]):    
        add_wins, add_draws, add_losses = stats
        self.cnt_wins += add_wins
        self.cnt_draws += add_draws
        self.cnt_losses += add_losses
        self.cnt_game = self.cnt_wins + self.cnt_draws + self.cnt_losses
        self.perc_score = (
            100 * (self.cnt_wins + self.cnt_wins + self.cnt_draws) // (self.cnt_game + self.cnt_game)
            if self.cnt_game > 0
            else 0
        )

    def print_stats(self)->str:
        return f"[ game={self.cnt_game} ({self.cnt_wins}/{self.cnt_draws}/{self.cnt_losses}), perc={self.perc_score} ]"