import os
import json
from datetime import datetime
from checkers.constant import DIM_CKECKERBOARD, MAX_DARK_CELLS, MAX_MAN
from checkers.engine.game.cells import Coordinates2D
from checkers.engine.game.pieces import Cells, Pieces, EnumPlayersColor
from checkers.engine.game.player_stats import PlayerStats
from checkers.engine.game.move import Move

class State:
    """
    Class that defines the state of the game :
    - arrangement of pieces on the checkerboard
    - turn of the player who has to make the move
    """

    def __init__(self):
        """
        Construction instances the classes :
        - Cells = Class for managing and collecting dark cells of the checkerboard.
        - Pieces = Class containing the game pieces of both players.

        @param -: .
        """
        self.pieces : Pieces = Pieces()
        self.player_turn = EnumPlayersColor.P_LIGHT
        # number_move serve in restore 'view' o come statistica
        self.number_move : int = 0
        self.parity_move : int = 0
        # pk_game e database servono per gestione database in 'view' o history attivo
        self.pk_game : str = ""
        self.database : str = ""
        self.pdn : str = ""
        self.data_player_light : PlayerStats = PlayerStats()
        self.data_player_dark  : PlayerStats = PlayerStats()
        self.data_players : dict[EnumPlayersColor, PlayerStats] = { 
            EnumPlayersColor.P_LIGHT : self.data_player_light, 
            EnumPlayersColor.P_DARK  : self.data_player_dark 
        }    
        self.exit : bool = False
        self.game_over : bool = False

    # Initial position of pieces on the checkerboard
    def reset(self, pk_game:str, pk_players:tuple[str,str]):
        self.pieces.clear()

        for light_man_index in range(MAX_MAN):
            id_dark_cell = MAX_DARK_CELLS - light_man_index - 1
            self.pieces.add_pieces(id_dark_cell,  light_man_index + 1)
        for dark_man_index in range(MAX_MAN):
            self.pieces.add_pieces(dark_man_index, -dark_man_index - 1)

        self.player_turn = EnumPlayersColor.P_LIGHT
        self.number_move = 0
        self.parity_move = 0
        self.game_over = False

        self.pk_game = pk_game
        self.set_players(pk_players)

    # restoration of positioning pieces on the ckeckerboard from a previously saved state
    def restore(self, filename: str):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} not found !")
        
        self.pieces.clear()

        with open(filename,"r") as file_restore:
            state_dict = json.load(file_restore)

            # Verify key 'checkerboard'
            if "checkerboard" not in state_dict:
                raise ValueError(f"Missing 'checkerboard' key !")        
            # Check matrix size
            num_cells = [len(row_cells) for row_cells in state_dict["checkerboard"]]
            if len(num_cells) == DIM_CKECKERBOARD and all(len(row_cells) == DIM_CKECKERBOARD for row_cells in state_dict["checkerboard"]):
            # if len(num_cells) == DIM_CKECKERBOARD and all(p == DIM_CKECKERBOARD for p in num_cells):    # method all()
            # if len(num_cells) == DIM_CKECKERBOARD and num_cells.count(DIM_CKECKERBOARD) == DIM_CKECKERBOARD: # len(num_cells) == DIM_CKECKERBOARD ! # method count()
                for row_index, row_cell in enumerate(state_dict["checkerboard"]):
                    for col_index, col_cell in enumerate(row_cell):
                        if col_cell != 0:
                            self._add_piece(row_index, col_index, col_cell)
            else:
                raise ValueError(f"Matrix size 'checkerboard' other than 8x8 !")  

            # Verify key 'player_turn'
            if "player_turn" not in state_dict:
                raise ValueError(f"Missing 'player_turn' key !")
            self.player_turn = EnumPlayersColor(state_dict["player_turn"])

            # Verify key 'number_move'
            if "number_move" not in state_dict:
                raise ValueError(f"Missing 'number_move' key !")
            self.number_move = state_dict["number_move"]

            # Verify key 'parity_move'
            if "parity_move" not in state_dict:
                raise ValueError(f"Missing 'parity_move' key !")
            self.parity_move = state_dict["parity_move"]

            # Verify key 'pk_game'
            if "pk_game" not in state_dict:
                raise ValueError(f"Missing 'pk_game' key !")
            # Stringa non vuota solo in 'play' con history attiva, oppure in 'view'
            self.pk_game = state_dict["pk_game"]

            # Verify key 'database'
            if "database" not in state_dict:
                raise ValueError(f"Missing 'database' key !")
            # Database history o view
            self.database = state_dict["database"]

            # Verify key 'pdn'
            if "pdn" not in state_dict:
                raise ValueError(f"Missing 'pdn' key !")
            # Import PDN o view
            self.pdn = state_dict["pdn"]

            # Verify key 'player_light'
            if "player_light" not in state_dict:
                raise ValueError(f"Missing 'player_light' key !")
            _pk_light : str = state_dict["player_light"]

            # Verify key 'player_dark'
            if "player_dark" not in state_dict:
                raise ValueError(f"Missing 'player_dark' key !")
            _pk_dark : str = state_dict["player_dark"]

            self.set_players((_pk_light, _pk_dark))
            self.data_player_light.set_counter_man_king(*self.pieces.counter_man_king(EnumPlayersColor.P_LIGHT))
            self.data_player_dark.set_counter_man_king(*self.pieces.counter_man_king(EnumPlayersColor.P_DARK))

    def _add_piece(self, row_index: int, col_index: int, value: int):
        id_dark_cell = Cells.coord2index(Coordinates2D(col_index, row_index))
        self.pieces.add_pieces(id_dark_cell, value)

    def save(self, filename: str):
        if os.path.exists(filename):
            print(f"Warning: File {filename} will be overwritten !")

        state_dict = {}

        # Generate the matrix checkerboard
        state_dict["checkerboard"] = self.generate_checkerboard()
        
        # Save the player's turn
        state_dict["player_turn"] = self.player_turn.value

        # Save number of move
        state_dict["number_move"] = self.number_move

        # Save counter of parity move
        state_dict["parity_move"] = self.parity_move

        # Save primary key of game
        state_dict["pk_game"] = self.pk_game

        # Save database "history_database" with 'play/view'
        state_dict["database"] = self.database

        # Save pdn "import_pdn_name" with 'view'
        state_dict["pdn"] = self.pdn

        # Save players with color
        state_dict["player_light"] = self.build_pk_player(self.data_player_light.engine, self.data_player_light.name)
        state_dict["player_dark"]  = self.build_pk_player(self.data_player_dark.engine , self.data_player_dark.name)

        # Writes to JSON files with error handling
        try:
            with open(filename, "w") as file_restore:
                json.dump(state_dict, file_restore, indent=4)

        except IOError as e:
            print(f"Error writing to file {filename}: {e}")
        except ValueError as e:
            print(f"Error serializing JSON: {e}")

    def generate_checkerboard(self):
        return [
            [self.pieces.get_id_piece(Cells.coord2index(Coordinates2D(col_index, row_index)))
            for col_index in range(DIM_CKECKERBOARD)] 
            for row_index in range(DIM_CKECKERBOARD)
        ]

    def build_pk_player(self, engine:str, name:str)->str:
        return engine + ": " + name

    def split_pk_player(self, pk_player:str)->tuple[str,str]:
        engine, player = pk_player.split(":")
        # without space
        # engine, player = [part.strip() for part in pk_player.split(":")]
        return (engine, player)

    def set_players(self, pk_players:tuple[str,str]):
        self.data_player_light.engine, self.data_player_light.name = self.split_pk_player(pk_players[0])
        self.data_player_dark.engine , self.data_player_dark.name  = self.split_pk_player(pk_players[1])
        # Se database unisco nei Player anche i dati storici di "history_database"
        if len(self.database) > 0:
            self.data_player_light.load_history_data()
            self.data_player_dark.load_history_data()
        self.data_player_light.reset()
        self.data_player_dark.reset()

    def set_counter_captured(self, id_dark_cell:int):
        _next_turn : EnumPlayersColor = self.get_next_turn()
        if self.pieces.is_man(id_dark_cell):
            self.data_players[_next_turn].counter_man  -= 1
        else:
            self.data_players[_next_turn].counter_king -= 1
        print(
            f"Player {_next_turn} : "
            f"man={self.data_players[_next_turn].counter_man}, "
            f"king={self.data_players[_next_turn].counter_king}"
        )

    def set_counter_promoted(self):
        self.data_players[self.player_turn].counter_king += 1
        self.data_players[self.player_turn].counter_man  -= 1
        print(
            f"Player {self.player_turn} : "
            f"man={self.data_players[self.player_turn].counter_man}, "
            f"king={self.data_players[self.player_turn].counter_king}"
        )

    def get_least_one_king(self)->bool:
        return (
            self.data_players[self.player_turn].counter_king > 0 and
            self.data_players[self.get_next_turn()].counter_king > 0
        )

    def get_engine(self)->str:
        return self.data_players[self.player_turn].engine

    def generate_pk_game(self)->str:
        # Generazione datetime per chiave primaria game (univoca con microsecondi). 
        # N.B.: solo restituita non assegnata a self.pk_game !
        return datetime.now().strftime("%Y%m%d%H%M%S%f")

    def get_next_turn(self)->EnumPlayersColor:
        return (
            EnumPlayersColor.P_DARK
            if self.player_turn == EnumPlayersColor.P_LIGHT
            else EnumPlayersColor.P_LIGHT
        )

    def set_next_turn(self):
        if self.player_turn == EnumPlayersColor.P_LIGHT:
            self.player_turn = EnumPlayersColor.P_DARK
        else:
            self.player_turn = EnumPlayersColor.P_LIGHT
    
    def update(self, move:Move)->bool:
        # La partita è dichiarata patta quando, avendo entrambi i giocatori almeno una dama, 
        # si verificano 40 mosse per parte (riducibili a 10) senza che venga catturato alcun pezzo e 
        # senza che nessuna pedina si sia mossa (solo dame).
        if self.get_least_one_king() and len(move.captures) == 0 and self.pieces.is_king(move.origin):
            self.parity_move += 1
            print(f"Parity move = {self.parity_move}")
        else:
            self.parity_move = 0

        # Aggiornamento stato scacchiera
        _destination : int = move.destinations[-1]
        self.pieces.update_position(move.origin, _destination)
        for _id_dark_cell in move.captures:
            self.set_counter_captured(_id_dark_cell)
            self.pieces.remove_pieces(_id_dark_cell)

        # La promozione a dama di una pedina avviene solo a mossa conclusa.
        _is_promoted_king = self.pieces.check_promotion_king(_destination, self.player_turn)
        if _is_promoted_king:
            self.set_counter_promoted()

        self.set_next_turn()
        return _is_promoted_king
    
    # Test fine partita :
    # - nessuna mossa possibile o nessun pezzo
    # - parity_move >= MAX_PARITY
    def check_game_over(self, number_moves:int, max_parity:int)->bool:
        if number_moves <= 0 or self.parity_move >= max_parity:
            self.game_over = True
            if number_moves <= 0:
                print(f"*** Winner {self.get_next_turn()} ! ***")
            else:
                print(f"*** Match parity ! *** ")
        return self.game_over
