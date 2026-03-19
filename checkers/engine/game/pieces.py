import enum
from checkers.constant import MAX_MAN, MAX_KING, MAX_DARK_CELLS
from checkers.engine.game.cells import Cells
from collections.abc import Generator

# Class, used to define the color that indicate the player 
# whose turn it is to make the move.
@enum.unique
class EnumPlayersColor(enum.Enum):
    P_LIGHT = 0
    P_DARK = 1

class Pieces:

    """
    Class containing the game pieces of both players as a reverse 
    dictionary : 
    - keys   = ID dark cells
    - values = ID piece 'man/king' [1..12/13..24]
    When a 'man' is promoted to a 'king', 12 is added to the ID.
    Player 'light' has positive IDs, player 'dark' has negative IDs.
    """

    def __init__(self):
        """
        Constructor defines the reverse dictionary leaving it empty. 
        The loading of the pieces depends on whether a reset or a restore 
        from a configurable initial state is performed.

        @param -: .
        """

        self._reverse_dict : dict[int, int] = {}

    def clear(self):
        self._reverse_dict.clear()

    @staticmethod
    def is_valid_piece(id_piece:int)->bool:
        if (1 <= abs(id_piece) <= MAX_KING):
            return True
        else:
            return False

    # N.B.: with the exception you don't need to return a bool !
    @staticmethod
    def check_valid_piece(id_piece:int):
        if not (1 <= abs(id_piece) <= MAX_KING):
            raise ValueError(f"Specified piece ID {id_piece} is out of bounds !")

    # N.B.: with the exception you don't need to return a bool !
    def check_busy_cell(self, id_dark_cell:int):
        if id_dark_cell not in self._reverse_dict:
            raise KeyError(f"Cell {id_dark_cell} is empty !")

    # N.B.: with the exception you don't need to return a bool !
    def check_empty_cell(self, id_dark_cell:int):
        if id_dark_cell in self._reverse_dict:
            raise KeyError(f"Cell {id_dark_cell} already contains a piece !")

    def add_pieces(self, id_dark_cell:int, id_piece:int):
        Cells.check_valid_cell(id_dark_cell)
        Pieces.check_valid_piece(id_piece)
        self.check_empty_cell(id_dark_cell)

        self._reverse_dict[id_dark_cell] = id_piece

    def remove_pieces(self, id_dark_cell:int):
        Cells.check_valid_cell(id_dark_cell)
        self.check_busy_cell(id_dark_cell)

        del self._reverse_dict[id_dark_cell]

    def update_position(self, origin_cell:int, target_cell:int):
        Cells.check_valid_cell(origin_cell)
        Cells.check_valid_cell(target_cell)
        # check for the presence of a piece on the original cell
        self.check_busy_cell(origin_cell)        
        # check for absence of a piece on the target cell
        self.check_empty_cell(target_cell)
        
        self.add_pieces(target_cell, self._reverse_dict[origin_cell])
        self.remove_pieces(origin_cell)

    def get_id_piece(self, id_dark_cell:int)->int:
        # avoid id_dark_cell validity test to return zero anyway
        # Cells.check_valid_cell(id_dark_cell)

        # if the cell contains no pieces it returns zero
        return self._reverse_dict.get(id_dark_cell, 0)
        
    def check_promotion_king(self, id_dark_cell:int)->bool:
        # check base cell
        player = self.get_player(id_dark_cell)
        if not (
            (player == EnumPlayersColor.P_DARK and id_dark_cell >= MAX_DARK_CELLS - 4) or
            (player == EnumPlayersColor.P_LIGHT and id_dark_cell < 4)
        ):
            return False

        id_piece = self.get_id_piece(id_dark_cell)
        Pieces.check_valid_piece(id_piece)

        # promotion to King
        if abs(id_piece) > MAX_MAN:
            return False

        if 0 < id_piece <= MAX_MAN: 
            id_piece += MAX_MAN
        elif 0 > id_piece >= -MAX_MAN:
            id_piece -= MAX_MAN
        self._reverse_dict[id_dark_cell] = id_piece  
        return True
    
    def demotion_man(self, id_dark_cell:int)->bool:
        # check for the presence of a piece on the specified cell
        self.check_busy_cell(id_dark_cell)

        id_piece = self.get_id_piece(id_dark_cell)
        Pieces.check_valid_piece(id_piece)

        # demotion to Man
        if abs(id_piece) <= MAX_MAN:
            return False
        
        if MAX_MAN < id_piece <= MAX_KING: 
            id_piece -= MAX_MAN
        elif -MAX_MAN > id_piece >= -MAX_KING:
            id_piece += MAX_MAN
        self._reverse_dict[id_dark_cell] = id_piece  
        return True

    # funcion generating a player's pieces 
    def iter_player_cells(self, player:EnumPlayersColor)->Generator[int, None, None]:
        for (cell, piece) in self._reverse_dict.items():
            if player == EnumPlayersColor.P_LIGHT:
                if piece > 0:
                    yield cell
            else:
                if piece < 0:
                    yield cell
    
    def iter_players_pieces(self)->Generator[tuple[int, int], None, None]:
        for (cell, piece) in self._reverse_dict.items():
            yield (cell, piece)

    def counter_man_king(self, player:EnumPlayersColor)->tuple[int, int]:
        _man : int = 0
        _king : int = 0
        for (_, piece) in self._reverse_dict.items():
            if player == EnumPlayersColor.P_LIGHT:
                if piece > 0:
                    if 0 < piece <= MAX_MAN:
                        _man += 1
                    else:
                        _king += 1
            else:
                if piece < 0:
                    if 0 < -piece <= MAX_MAN:
                        _man += 1
                    else:
                        _king += 1
        return (_man, _king)

    def is_man(self, id_dark_cell:int)->bool:
        Cells.check_valid_cell(id_dark_cell)
        self.check_busy_cell(id_dark_cell)
        if 0 < abs(self.get_id_piece(id_dark_cell)) <= MAX_MAN:
            return True
        else:
            return False
        
    def is_king(self, id_dark_cell:int)->bool:
        Cells.check_valid_cell(id_dark_cell)
        self.check_busy_cell(id_dark_cell)
        if MAX_MAN < abs(self.get_id_piece(id_dark_cell)) <= MAX_KING:
            return True
        else:
            return False
    
    def get_player(self, id_dark_cell:int)->EnumPlayersColor:
        Cells.check_valid_cell(id_dark_cell)
        self.check_busy_cell(id_dark_cell)
        if self.get_id_piece(id_dark_cell) > 0:
            return EnumPlayersColor.P_LIGHT
        else:
            return EnumPlayersColor.P_DARK
