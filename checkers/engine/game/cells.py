# To avoid using quotes ("") in the type hints on the 'other' parameter, 
# just add this directive (Python >=3.10)
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from checkers.constant import MAX_DARK_CELLS, DIM_CKECKERBOARD

# To make the class formally immutable, use @dataclass(frozen=True).
# This way, attributes cannot be modified and hashing can be used.
@dataclass(frozen=True)
class Coordinates2D:
    row: int
    col: int
    """
    Class type for 2D cell checkerboard coordinates.
    Parameters defined directly as class attributes in 
    @dataclass declaration without custom constructor :
        @param row: Row of coordinates.
        @param col: Column of coordinates.
    """

    def __add__(self, other: Coordinates2D)->Coordinates2D:
        """
        Override + operator.
        @param other: Other coordinates that we are adding.
        """

        if other != None:
            return Coordinates2D(self.row + other.row, self.col + other.col)

    def __eq__(self, other: Coordinates2D)->bool:
        """
        Define == operator.

        @param other: Other coordinates that we are comparing with.
        """

        if other != None:
            if self.row == other.row and self.col == other.col:
                return True
            else:
                return False

    # Python requires that if two objects are considered equal via the 
    # __eq__ method, then their hash value (__hash__) must be the same.
    def __hash__(self)->int:
        return hash((self.row, self.col))

    def __str__(self)->str:
        return f"({self.row}, {self.col})"

    def __repr__(self)->str:
        return f"(row={self.row}, col={self.col})"



class Cells():
    """
    Class for managing and collecting dark cells of the checkerboard.

    The checkerboard must be arranged so that each player has the dark 
    cell (called "canton") to his right. The cells are conventionally 
    numbered from n.1 (the "canton" of the deployment with the black 
    pieces) to n. 32 (the "canton" of the deployment with the white pieces).

    The unrotated checkerboard view has the dark pieces at the top 
    and the light pieces at the bottom.    
    
    Each of the 32 dark cells has a tuple containing the cell IDs for 
    simple moves, and a tuple with the cell IDs for capturing moves of 
    opponent pieces. 
    """

    # Inner class used to define the type of movement of the pieces 
    # between the dark cells
    class EnumMove(Enum):
        M_SIMPLE = 1
        M_CAPTURE = 2

    def __init__(self):
        """
        Construction of cell tuples for simple moves and captures through 
        the compressed checkerboard indices to the dark cells only.

        @param -: .
        """

        self.simpleMoves = tuple(self.findMoveCells(i, self.EnumMove.M_SIMPLE.value) for i in range(MAX_DARK_CELLS))
        self.captureMoves = tuple(self.findMoveCells(i, self.EnumMove.M_CAPTURE.value) for i in range(MAX_DARK_CELLS))

    # returns the tuple of simple movements given the index 
    # of the original dark cell
    def getSimpleMoves(self, indexDarkCell:int)->tuple[int, int, int, int]:
        if not (0 <= indexDarkCell < len(self.simpleMoves)):
            return (-1, -1, -1, -1)
        
        return self.simpleMoves[indexDarkCell]

    # returns the tuple of capture movements given the index 
    # of the original dark cell
    def getCaptureMoves(self, indexDarkCell:int)->tuple[int, int, int, int]:
        if not (0 <= indexDarkCell < len(self.captureMoves)):
            return (-1, -1, -1, -1)
        
        return self.captureMoves[indexDarkCell]

    # transforms the dark cell index [0..31] into 8x8 checkerboard 
    # coordinates [0..7][0..7]
    def index2coord(self, indexDarkCell:int)->Coordinates2D:
        if not (0 <= indexDarkCell < MAX_DARK_CELLS):
            return Coordinates2D(-1, -1)
        
        indexCheckerboard = indexDarkCell * 2
        row = indexCheckerboard // DIM_CKECKERBOARD
        col = indexCheckerboard % DIM_CKECKERBOARD
        return Coordinates2D(row, col)

    # transforms the 8x8 checkerboard coordinates [0..7][0..7] 
    # into the dark cell index [0..31]
    def coord2index(self, coord:Coordinates2D)->int:
        row = coord.row
        col = coord.col

        if not (0 <= row < DIM_CKECKERBOARD and 0 <= col < DIM_CKECKERBOARD):
            return -1
        
        indexCells = row * DIM_CKECKERBOARD + col

        # check light cells
        if (indexCells % 2 != 0):
            return -1
        
        return indexCells // 2

    # returns the tuple of dark cells with simple/capture movements 
    # starting from the dark cell ID
    def findMoveCells(self, indexDarkCell:int, d:EnumMove)->tuple[int, int, int, int]:
        if not (0 <= indexDarkCell < MAX_DARK_CELLS):
            return (-1,-1,-1,-1)
        
        coord : Coordinates2D = self.index2coord(indexDarkCell)
        moves = []

        for dcol, drow in [( d, -d), (-d, -d), (-d, d), (d, d)]:
            ncol, nrow = coord.col + dcol, coord.row + drow

            if not (0 <= ncol < DIM_CKECKERBOARD and 0 <= nrow < DIM_CKECKERBOARD):
                moves.append(-1)
            else:
                moves.append((nrow * 4) + (ncol // 2))

        return tuple(moves)
