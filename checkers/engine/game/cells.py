# To avoid using quotes ("") in the type hints on the 'other' parameter, 
# just add this directive (Python >=3.10)
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from checkers.checkers_types import DestCellsType
from checkers.constant import MAX_DARK_CELLS, DIM_CKECKERBOARD
import enum

# To make the class formally immutable, use @dataclass(frozen=True).
# This way, attributes cannot be modified and hashing can be used.
@dataclass(frozen=True)
class Coordinates2D:
    col: int
    row: int
    """
    Class type for 2D cell checkerboard coordinates.
    Parameters defined directly as class attributes in 
    @dataclass declaration without custom constructor :
        attribute with interface game logical :
        @param col: Column of coordinates.
        @param row: Row of coordinates.
    """

    # Property for interface graphical
    @property
    def x(self)->int:
        return self.col

    @property
    def y(self)->int:
        return self.row

    def __add__(self, other: Coordinates2D)->Coordinates2D:
        """
        Override + operator.
        @param other: Other coordinates that we are summed.
        """

        if other != None:
            return Coordinates2D(self.col + other.col, self.row + other.row)

    def __iadd__(self, other: Coordinates2D)->Coordinates2D:
        """
        Override += operator.
        @param other: Other coordinates that we are summed.
        """

        if other != None:
            return Coordinates2D(self.col + other.col, self.row + other.row)

    def __sub__(self, other: Coordinates2D)->Coordinates2D:
        """
        Override - operator.
        @param other: Other coordinates that we are subtracted.
        """

        if other != None:
            return Coordinates2D(self.col - other.col, self.row - other.row)

    def __eq__(self, other: Coordinates2D)->bool:
        """
        Define == operator.

        @param other: Other coordinates that we are comparing with.
        """

        if other != None:
            if self.col == other.col and self.row == other.row:
                return True
            else:
                return False

    # Python requires that if two objects are considered equal via the 
    # __eq__ method, then their hash value (__hash__) must be the same.
    def __hash__(self)->int:
        return hash((self.col, self.row))

    def __str__(self)->str:
        return f"({self.col}, {self.row})"

    def __repr__(self)->str:
        return f"(col={self.col}, row={self.row})"
    
    def as_tuple(self)->tuple[int, int]:
        return (self.col, self.row)

# Class used to define the type of movement of the pieces 
# between the dark cells
@enum.unique
class EnumMove(enum.Enum):
    M_NONE = 0
    M_SIMPLE = 1
    M_CAPTURE = 2

class Cells:
    _simple_moves = None
    _capture_moves = None

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

    @classmethod
    def initialize(cls):
        cls._simple_moves = tuple(
            cls.find_move_cells(i, EnumMove.M_SIMPLE.value)
            for i in range(MAX_DARK_CELLS)
        )
        cls._capture_moves = tuple(
            cls.find_move_cells(i, EnumMove.M_CAPTURE.value)
            for i in range(MAX_DARK_CELLS)
        )

    @staticmethod
    def is_valid_cell(id_dark_cell:int)->bool:
        if (0 <= id_dark_cell < MAX_DARK_CELLS):
            return True
        else:
            return False

    # N.B.: with the exception you don't need to return a bool !
    @staticmethod
    def check_valid_cell(id_dark_cell:int):
        if not (0 <= id_dark_cell < MAX_DARK_CELLS):
            raise KeyError(f"Specified cell ID {id_dark_cell} is out of bounds !")
        
    # returns the tuple of simple movements given the index 
    # of the original dark cell
    @staticmethod
    def get_simple_moves(index_dark_cell:int, mask:Optional[tuple[bool, bool, bool, bool]]=None)->DestCellsType:
        if not Cells.is_valid_cell(index_dark_cell):
            return (-1, -1, -1, -1)
        
        if mask == None:
            return Cells._simple_moves[index_dark_cell]
        else:
            #m = self._simple_moves[index_dark_cell]
            #return (
            #    -1 if not mask[0] else m[0],
            #    -1 if not mask[1] else m[1],
            #    -1 if not mask[2] else m[2],
            #    -1 if not mask[3] else m[3],
            #)
            return tuple(-1 if not filter else cell for filter, cell in zip(mask, Cells._simple_moves[index_dark_cell]))

    # returns the tuple of capture movements given the index 
    # of the original dark cell
    @staticmethod
    def get_capture_moves(index_dark_cell:int, mask:Optional[tuple[bool, bool, bool, bool]]=None)->DestCellsType:
        if not Cells.is_valid_cell(index_dark_cell):
            return (-1, -1, -1, -1)

        if mask == None:
            return Cells._capture_moves[index_dark_cell]
        else:
            #m = self._capture_moves[index_dark_cell]
            #return (
            #    -1 if not mask[0] else m[0],
            #    -1 if not mask[1] else m[1],
            #    -1 if not mask[2] else m[2],
            #    -1 if not mask[3] else m[3],
            #)
            return tuple(-1 if not filter else cell for filter, cell in zip(mask, Cells._capture_moves[index_dark_cell]))

    @staticmethod
    def get_moves(index_dark_cell:int, type:EnumMove, mask:Optional[tuple[bool, bool, bool, bool]]=None)->DestCellsType:
        if not Cells.is_valid_cell(index_dark_cell) or type == EnumMove.M_NONE:
            return (-1, -1, -1, -1)

        return (
            Cells.get_simple_moves(index_dark_cell, mask)
            if type == EnumMove.M_SIMPLE
            else Cells.get_capture_moves(index_dark_cell, mask)
        )

    # transforms the dark cell index [0..31] into 8x8 checkerboard 
    # coordinates [0..7][0..7]
    @staticmethod
    def index2coord(index_dark_cell:int)->Coordinates2D:
        if not Cells.is_valid_cell(index_dark_cell):
            return Coordinates2D(-1, -1)
        
        index_checkerboard = index_dark_cell * 2
        row = index_checkerboard // DIM_CKECKERBOARD
        col = index_checkerboard % DIM_CKECKERBOARD + row % 2
        return Coordinates2D(col, row)

    # transforms the 8x8 checkerboard coordinates [0..7][0..7] 
    # into the dark cell index [0..31]
    @staticmethod
    def coord2index(coord:Coordinates2D)->int:
        col = coord.col
        row = coord.row

        if not (0 <= col < DIM_CKECKERBOARD and 0 <= row < DIM_CKECKERBOARD):
            return -1
        
        index_cells = row * DIM_CKECKERBOARD + col

        # check light cells
        if (row % 2 != col % 2):
            return -1
        
        return index_cells // 2

    # returns the tuple of dark cells with simple/capture movements 
    # starting from the dark cell ID
    @staticmethod
    def find_move_cells(index_dark_cell:int, d:EnumMove)->DestCellsType:
        if not Cells.is_valid_cell(index_dark_cell):
            return (-1,-1,-1,-1)
        
        coord : Coordinates2D = Cells.index2coord(index_dark_cell)
        moves = []

        # tuple sorted for cartesian dials (1:up-rt,..., 4:dn-rt)
        for dcol, drow in [( d, -d), (-d, -d), (-d, d), (d, d)]:
            ncol, nrow = coord.col + dcol, coord.row + drow

            if not (0 <= ncol < DIM_CKECKERBOARD and 0 <= nrow < DIM_CKECKERBOARD):
                moves.append(-1)
            else:
                moves.append((nrow * 4) + (ncol // 2))

        return tuple(moves)
    
Cells.initialize()
