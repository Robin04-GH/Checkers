import os
import json
from checkers.constant import DIM_CKECKERBOARD, MAX_DARK_CELLS, MAX_MAN
from checkers.engine.game.cells import Coordinates2D
from checkers.engine.game.pieces import Pieces

class State:
    """
    Class that defines the state of the game :
    - arrangement of pieces on the checkerboard
    - turn of the player who has to make the move
    """

    """
    # Inner class, used to define constants that represent the players' 
    # 'man' or 'king' in the cells of the checkerboard
    @enum.unique
    class EnumCheckerboardCells(enum.Enum):
        C_EMPTY = 0
        C_MAN_LIGHT = 1
        C_KING_LIGHT = 2
        C_MAN_DARK = 3
        C_KING_DARK = 4
    """

    def __init__(self):
        """
        Construction instances the classes :
        - Cells = Class for managing and collecting dark cells of the checkerboard.
        - Pieces = Class containing the game pieces of both players.

        @param -: .
        """
        self.pieces = Pieces()
        self.player_turn = Pieces.EnumPlayersColor.P_LIGHT

    # Initial position of pieces on the checkerboard
    def reset(self):
        self.pieces.clear()

        for light_man_index in range(MAX_MAN):
            id_dark_cell = MAX_DARK_CELLS - light_man_index - 1
            self.pieces.add_pieces(id_dark_cell,  light_man_index + 1)
        for dark_man_index in range(MAX_MAN):
            self.pieces.add_pieces(dark_man_index, -dark_man_index - 1)

        self.player_turn = Pieces.EnumPlayersColor.P_LIGHT

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
        
            self.player_turn = Pieces.EnumPlayersColor(state_dict["player_turn"])

    def _add_piece(self, row_index: int, col_index: int, value: int):
        id_dark_cell = self.pieces.coord2index(Coordinates2D(row_index, col_index))
        self.pieces.add_pieces(id_dark_cell, value)

    def save(self, filename: str):
        if os.path.exists(filename):
            print(f"Warning: File {filename} will be overwritten !")

        state_dict = {}

        # Generate the matrix checkerboard
        state_dict["checkerboard"] = self.generate_checkerboard()
        
        # Save the player's turn
        state_dict["player_turn"] = self.player_turn.value

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
            [self.pieces.get_id_piece(self.pieces.coord2index(Coordinates2D(row_index, col_index))) 
            for col_index in range(DIM_CKECKERBOARD)] 
            for row_index in range(DIM_CKECKERBOARD)
        ]

    def next_turn(self):
        if self.player_turn == Pieces.EnumPlayersColor.P_LIGHT:
            self.player_turn = Pieces.EnumPlayersColor.P_DARK
        else:
            self.player_turn = Pieces.EnumPlayersColor.P_LIGHT

    def update(self):
        # update move ... <--- TODO !!!

        self.next_turn()
