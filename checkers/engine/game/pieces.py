import enum
from checkers.constant import MAX_DARK_CELLS, MAX_MAN
from checkers.engine.game.cells import Coordinates2D, Cells

class Pieces(Cells):

    # Inner class, used to define the color that indicate the player 
    # whose turn it is to make the move.
    @enum.unique
    class EnumPlayersColor(enum.Enum):
        P_LIGHT = 0
        P_DARK = 1

    """
    Class containing the game pieces of both players as a reverse 
    dictionary : 
    - keys   = ID dark cells
    - values = ID 'man' [1..12]
    When a 'man' is promoted to a 'king', 12 is added to the ID.
    Player 'light' has positive IDs, player 'dark' has negative IDs.
    """

    # class attribute
    MAX_MAN_X2 = MAX_MAN + MAX_MAN

    def __init__(self):
        """
        Constructor defines the reverse dictionary leaving it empty. 
        { Key = id_dark_cell : value = id_piece }
        The loading of the pieces depends on whether a reset or a restore 
        from a configurable initial state is performed.

        @param -: .
        """

        super().__init__()
        self._reverse_dict : dict[int, int] = {}

    def clear(self):
        self._reverse_dict.clear()

    def is_valid_piece(self, id_piece:int)->bool:
        if (1 <= abs(id_piece) <= Pieces.MAX_MAN_X2):
            return True
        else:
            return False

    # N.B.: with the exception you don't need to return a bool !
    def check_valid_piece(self, id_piece:int):
        if not (1 <= abs(id_piece) <= Pieces.MAX_MAN_X2):
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
        self.check_valid_cell(id_dark_cell)
        self.check_valid_piece(id_piece)
        self.check_empty_cell(id_dark_cell)

        self._reverse_dict[id_dark_cell] = id_piece

    def remove_pieces(self, id_dark_cell:int):
        self.check_valid_cell(id_dark_cell)
        self.check_busy_cell(id_dark_cell)

        del self._reverse_dict[id_dark_cell]

    def update_position(self, origin_cell:int, target_cell:int):
        self.check_valid_cell(origin_cell)
        self.check_valid_cell(target_cell)

        # check for the presence of a piece on the original cell
        self.check_busy_cell(origin_cell)        
        # check for absence of a piece on the target cell
        self.check_empty_cell(target_cell)
        
        self.add_pieces(target_cell, self._reverse_dict[origin_cell])
        self.remove_pieces(origin_cell)

    def get_id_piece(self, id_dark_cell:int)->int:
        # avoid id_dark_cell validity test to return zero anyway
        #self.check_valid_cell(id_dark_cell)

        # if the cell contains no pieces it returns zero
        return self._reverse_dict.get(id_dark_cell, 0)
        
    def promotion_king(self, id_dark_cell:int):
        # check for the presence of a piece on the specified cell
        self.check_busy_cell(id_dark_cell)        

        id_piece = self.get_id_piece(id_dark_cell)

        self.check_valid_piece(id_piece)
        
        # promotion to King
        if 0 < id_piece <= MAX_MAN: 
            id_piece += MAX_MAN
        elif 0 > id_piece >= -MAX_MAN:
            id_piece -= MAX_MAN
        else:
            raise ValueError(f"The piece ID {id_piece} is already a king and cannot be promoted yet !")

        self._reverse_dict[id_dark_cell] = id_piece
    
    # funcion generating a player's pieces 
    def iter_player(self, player:EnumPlayersColor):
        for (cell, piece) in self._reverse_dict.items():
            if player == Pieces.EnumPlayersColor.P_LIGHT:
                if piece > 0:
                    yield cell
            else:
                if piece < 0:
                    yield cell
    
    def is_man(self, id_dark_cell:int)->bool:
        self.check_valid_cell(id_dark_cell)
        self.check_busy_cell(id_dark_cell)
        if 0 < abs(self.get_id_piece(id_dark_cell)) <= MAX_MAN:
            return True
        else:
            return False
        
    def is_king(self, id_dark_cell:int)->bool:
        self.check_valid_cell(id_dark_cell)
        self.check_busy_cell(id_dark_cell)
        if MAX_MAN < abs(self.get_id_piece(id_dark_cell)) <= Pieces.MAX_MAN_X2:
            return True
        else:
            return False
    
    def get_player(self, id_dark_cell:int)->EnumPlayersColor:
        self.check_valid_cell(id_dark_cell)
        self.check_busy_cell(id_dark_cell)
        if self.get_id_piece(id_dark_cell) > 0:
            return Pieces.EnumPlayersColor.P_LIGHT
        else:
            return Pieces.EnumPlayersColor.P_DARK
