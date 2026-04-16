import os
import enum
import json
from checkers.constant import MAX_MAN, MAX_KING, MAX_DARK_CELLS

from checkers.constant import PATH_RESTORES
from datetime import datetime
from checkers.constant import DIM_CKECKERBOARD, MAX_DARK_CELLS, MAX_MAN
from checkers.engine.game.cells import Coordinates2D
from checkers.engine.game.pieces import Cells, Pieces, EnumPlayersColor
from checkers.engine.game.player_stats import PlayerStats
from checkers.engine.game.move import Move
from dataclasses import dataclass

# Class used to define the outcome of the match.
@enum.unique
class EnumResult(enum.Enum):
    R_NONE = 0
    R_LIGHT = 1
    R_DARK = 2
    R_PARITY = 3
    R_STAR = 4

@dataclass(frozen=True)
class StateMove():
    move : Move
    moved_piece : int
    captured_pieces : tuple[int, ...]
    promoted_king : bool
    old_parity : int

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
        # number_move is used in restore 'view' or as statistics
        self.number_move : int = 1
        self.parity_move : int = 0
        self.data_player_light : PlayerStats = PlayerStats()
        self.data_player_dark  : PlayerStats = PlayerStats()
        self.data_players : dict[EnumPlayersColor, PlayerStats] = { 
            EnumPlayersColor.P_LIGHT : self.data_player_light, 
            EnumPlayersColor.P_DARK  : self.data_player_dark 
        }    
        # pk_game and database are used for database management in 'view' or active history
        self.pk_game : str = ""
        self.database : str = ""
        self.pdn_game : str = ""
        self.pdn : str = ""
        self.exit : bool = False
        self.game_over : bool = False
        self.result : EnumResult = EnumResult.R_NONE
        self.in_viewer : bool = False
        self.last_state_move : StateMove | None = None
        self.undo_state : list[StateMove] = []
        self.undo_index : int = -1
        self.reverse_turn : bool = False

    # Initial position of pieces on the checkerboard
    def reset(self, pk_players:tuple[str,str]):
        self.pieces.clear()

        for light_man_index in range(MAX_MAN):
            id_dark_cell = MAX_DARK_CELLS - light_man_index - 1
            self.pieces.add_pieces(id_dark_cell,  light_man_index + 1)
        for dark_man_index in range(MAX_MAN):
            self.pieces.add_pieces(dark_man_index, -dark_man_index - 1)

        self.player_turn = EnumPlayersColor.P_LIGHT
        self.number_move = 1
        self.parity_move = 0
        self.game_over = False
        self.result = EnumResult.R_NONE
        self.undo_state.clear()
        self.undo_index = -1
        self.reverse_turn = False

        self.set_players(pk_players)

    # restoration of positioning pieces on the ckeckerboard from a previously saved state
    def restore(self, filename: str):
        path_file = PATH_RESTORES + filename
        if not os.path.exists(path_file):
            raise FileNotFoundError(f"File {path_file} not found !")
        
        self.pieces.clear()
        self.undo_state.clear()

        with open(path_file,"r") as file_restore:
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

            # Verify key 'player_light'
            if "player_light" not in state_dict:
                raise ValueError(f"Missing 'player_light' key !")
            _pk_light : str = state_dict["player_light"]

            # Verify key 'player_dark'
            if "player_dark" not in state_dict:
                raise ValueError(f"Missing 'player_dark' key !")
            _pk_dark : str = state_dict["player_dark"]

            # Verify key 'database'
            if "database" not in state_dict:
                raise ValueError(f"Missing 'database' key !")
            # Database history o view
            self.database = state_dict["database"]

            # Verify key 'pk_game'
            if "pk_game" not in state_dict:
                raise ValueError(f"Missing 'pk_game' key !")
            # Non empty string only in 'play' with history active, or in 'view'
            self.pk_game = state_dict["pk_game"]

            # Verify key 'pdn'
            if "pdn" not in state_dict:
                raise ValueError(f"Missing 'pdn' key !")
            # Import PDN o view
            self.pdn = state_dict["pdn"]

            # Verify key 'pdn_game'
            if "pdn_game" not in state_dict:
                raise ValueError(f"Missing 'pdn_game' key !")
            # Non empty string only in 'view' with 'import_pdn_name'
            self.pdn_game = state_dict["pdn_game"]

            self.set_players((_pk_light, _pk_dark))

    def _add_piece(self, row_index: int, col_index: int, value: int):
        id_dark_cell = Cells.coord2index(Coordinates2D(col_index, row_index))
        self.pieces.add_pieces(id_dark_cell, value)

    def save(self):
        path_file : str = PATH_RESTORES + "state_" + self.generate_datetime() + ".json"
        if os.path.exists(path_file):
            print(f"Warning: File {path_file} will be overwritten !")

        state_dict = {}

        # Generate the matrix checkerboard
        state_dict["checkerboard"] = self.generate_checkerboard()
        
        # Save the player's turn
        state_dict["player_turn"] = self.player_turn.value

        # Save number of move
        state_dict["number_move"] = self.number_move

        # Save counter of parity move
        state_dict["parity_move"] = self.parity_move

        # Save players with color
        state_dict["player_light"] = self.build_pk_player(self.data_player_light.engine, self.data_player_light.name)
        state_dict["player_dark"]  = self.build_pk_player(self.data_player_dark.engine , self.data_player_dark.name)

        # Save database "history_database" with 'play/view'
        state_dict["database"] = self.database

        # Save primary key of game
        state_dict["pk_game"] = self.pk_game

        # Save pdn "import_pdn_name" with 'view'
        state_dict["pdn"] = self.pdn

        # Save counter pdn game
        state_dict["pdn_game"] = self.pdn_game

        # Writes to JSON files with error handling
        try:
            with open(path_file, "w") as file_restore:
                json.dump(state_dict, file_restore, indent=4)

        except IOError as e:
            print(f"Error writing to file {path_file}: {e}")
        except ValueError as e:
            print(f"Error serializing JSON: {e}")

    def generate_checkerboard(self)->list[list[int]]:
        return [
            [self.pieces.get_id_piece(Cells.coord2index(Coordinates2D(col_index, row_index)))
            for col_index in range(DIM_CKECKERBOARD)] 
            for row_index in range(DIM_CKECKERBOARD)
        ]

    def get_dark_cells_state(self)->list[int]:
        return [
            self.pieces.get_id_piece(dark_cell) for dark_cell in range(MAX_DARK_CELLS)
        ]

    def build_pk_player(self, engine:str, name:str)->str:
        if not engine:
            engine = "player"
        return engine + ": " + name

    def pk_players_as_tuple(self)->tuple[str,str,str,str]:
        return (
            self.data_players[EnumPlayersColor.P_LIGHT].engine,
            self.data_players[EnumPlayersColor.P_LIGHT].name,
            self.data_players[EnumPlayersColor.P_DARK].engine,
            self.data_players[EnumPlayersColor.P_DARK].name,
        )

    def split_pk_player(self, pk_player:str)->tuple[str,str]:
        engine, player = pk_player.split(":")
        # without space
        # engine, player = [part.strip() for part in pk_player.split(":")]
        return (engine.strip(), player.strip())

    def get_pk_player(self, player:EnumPlayersColor)->str:
        return self.build_pk_player(self.data_players[player].engine, self.data_players[player].name)

    def get_engine(self)->str:
        return self.data_players[self.player_turn].engine

    def set_players(self, pk_players:tuple[str,str]):
        self.data_player_light.engine, self.data_player_light.name = self.split_pk_player(pk_players[0])
        self.data_player_dark.engine , self.data_player_dark.name  = self.split_pk_player(pk_players[1])

        # If database I also merge the historical data from "history_database" 
        # into the Players
        if self.database:
            self.data_player_light.load_history_data()
            self.data_player_dark.load_history_data()
        self.data_player_light.reset()
        self.data_player_dark.reset()

        self.data_player_light.set_counter_man_king(*self.pieces.counter_man_king(EnumPlayersColor.P_LIGHT))
        self.data_player_dark.set_counter_man_king(*self.pieces.counter_man_king(EnumPlayersColor.P_DARK))

    def print_match(self):        
        print(f"Pdn = {self.pdn_game}") if self.pdn_game else print(f"Pk = {self.pk_game}")
        print(f"Light = {self.get_pk_player(EnumPlayersColor.P_LIGHT)}")
        print(f"Dark  = {self.get_pk_player(EnumPlayersColor.P_DARK )}")

    def set_counter_captured(self, id_dark_cell:int, player:EnumPlayersColor, step:int):
        if self.pieces.is_man(id_dark_cell):
            self.data_players[player].counter_man  -= step
        else:
            self.data_players[player].counter_king -= step
        str_player : str = "Light" if player == EnumPlayersColor.P_LIGHT else "Dark"
        print(
            f"Piece " + str_player + " : "
            f"man={self.data_players[player].counter_man}, "
            f"king={self.data_players[player].counter_king}"
        )

    def set_counter_promoted(self, player:EnumPlayersColor, step:int):
        self.data_players[player].counter_king += step
        self.data_players[player].counter_man  -= step
        str_player : str = "Light" if player == EnumPlayersColor.P_LIGHT else "Dark"
        print(
            f"Piece " + str_player + " : "
            f"man={self.data_players[player].counter_man}, "
            f"king={self.data_players[player].counter_king}"
        )

    def get_least_one_king(self)->bool:
        return (
            self.data_players[self.player_turn].counter_king > 0 and
            self.data_players[self.get_next_turn()].counter_king > 0
        )

    def generate_datetime(self)->str:
        # Generate datetime for primary key game (unique with microseconds).
        # Hint: only returned, not assigned to self.pk_game !        
        return datetime.now().strftime("%Y%m%d%H%M%S%f")

    def get_next_turn(self)->EnumPlayersColor:
        return (
            EnumPlayersColor.P_DARK
            if self.player_turn == EnumPlayersColor.P_LIGHT
            else EnumPlayersColor.P_LIGHT
        )

    def set_turn(self):
        if self.player_turn == EnumPlayersColor.P_LIGHT:
            self.player_turn = EnumPlayersColor.P_DARK
            if self.reverse_turn:
                self.reverse_turn = False
                self.number_move -= 1
        else:
            self.player_turn = EnumPlayersColor.P_LIGHT
            if not self.reverse_turn:
                self.number_move += 1
            else:
                self.reverse_turn = False

    def set_in_viewer(self, status:bool):
        self.in_viewer = status

    def update(self, move:Move)->bool:
        # The game is declared a draw when, with both players having at least one king,
        # 40 moves have occurred on each side (reducible to 10) without any pieces 
        # being captured and without any mans having moved (kings only).      
        old_parity : int = self.parity_move
        if self.get_least_one_king() and len(move.captures) == 0 and self.pieces.is_king(move.origin):
            self.parity_move += 1
            print(f"Parity move = {self.parity_move}")
        else:
            self.parity_move = 0

        # Board status update
        list_captured : list[int] = []
        destination : int = move.destinations[-1]
        self.pieces.update_position(move.origin, destination)
        for id_dark_cell in move.captures:
            list_captured.append(self.pieces.get_id_piece(id_dark_cell))
            self.set_counter_captured(id_dark_cell, self.get_next_turn(), 1)
            self.pieces.remove_pieces(id_dark_cell)

        # A man can only be promoted to a king once a move has been completed.
        piece_move = self.pieces.get_id_piece(destination)
        _is_promoted_king = self.pieces.check_promotion_king(destination)
        if _is_promoted_king:
            self.set_counter_promoted(self.player_turn, 1)

        self.last_state_move = StateMove(
            move,
            piece_move,
            tuple(list_captured),
            _is_promoted_king,
            old_parity
        )

        # undo states
        if self.in_viewer:
            if not self.is_undo():
                self.undo_state.append(self.last_state_move)
            self.undo_index += 1

        return _is_promoted_king
    
    def is_undo(self)->bool:
        return self.undo_index < (len(self.undo_state) - 1)
    
    def get_undo_move(self)->tuple[int, ...]:
        move = self.undo_state[self.undo_index + 1].move
        return move.as_tuple()

    def restore_undo_move(self)->StateMove | None:
        if self.undo_index >= 0:
            # restore state
            state_move : StateMove = self.undo_state[self.undo_index]
            self.pieces.update_position(state_move.move.destinations[-1], state_move.move.origin)
            if state_move.promoted_king:
                self.pieces.demotion_man(state_move.move.origin)
                self.set_counter_promoted(self.get_next_turn(), -1)
            for index_cell, id_dark_cell in enumerate(state_move.move.captures):
                self.pieces.add_pieces(id_dark_cell, state_move.captured_pieces[index_cell])
                self.set_counter_captured(id_dark_cell, self.player_turn, -1)
            self.parity_move = state_move.old_parity
            self.undo_index -= 1
            self.reverse_turn = True
            return state_move
        else:
            return None

    # Test end of game:
    # - no possible move or no piece
    # - parity_move >= MAX_PARITY
    def check_game_over(self, number_moves:int, max_parity:int)->bool:
        if number_moves <= 0 or self.parity_move >= max_parity:
            if number_moves <= 0:
                self.result = (                
                    EnumResult.R_LIGHT if self.get_next_turn() == EnumPlayersColor.P_LIGHT
                    else
                    EnumResult.R_DARK
                )
            else:
                self.result = EnumResult.R_PARITY

        results : dict[EnumResult, str] = {
            EnumResult.R_LIGHT : "*** Winner player LIGHT ! ***",
            EnumResult.R_DARK : "*** Winner player DARK ! ***", 
            EnumResult.R_PARITY : "*** Match parity ! ***",
            EnumResult.R_STAR : "Result not specified !"
        }

        if self.result != EnumResult.R_NONE:
            self.game_over = True
            self.last_state_move = None
            print(results[self.result])

        return self.game_over

    def force_result(self, result:EnumResult):
        self.result = result
        if result == EnumResult.R_NONE:
            print(f"Absense of further moves and result. Game not conclused !")
