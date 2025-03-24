import numpy as np

from enum import Enum
from checkers.graph.graphicsInterface import GraphicsInterface

class Checkerboard():
    """
    Class for checkerboard management:
    - initialization (reset)
    - restore initial state
    - memorization of pieces (state)
    - functions for reading the position of the pieces     
    """

    # Inner class, used to define the color that indicate the player 
    # whose turn it is to make the move.
    class EnumPlayersColor(Enum):
        P_LIGHT = 0
        P_DARK = 1

    # Inner class, used to define constants that represent the players' 
    # pawns or checkers in the cells of the checkerboard
    class EnumCheckerboardCells(Enum):
        C_EMPTY = 0
        C_PAWN_LIGHT = 1
        C_CHECKER_LIGHT = 2
        C_PAWN_DARK = 3
        C_CHECKER_DARK = 4

    def __init__(self, graphics: GraphicsInterface):
        """
        Constructor.

        @param xxx: .
        """

        self.graphics = graphics
        # Initialize an 8x8 checkerboard with zeros
        self.checkerboard = np.zeros((8, 8), dtype=int)
        self.playerTurn = self.EnumPlayersColor.P_LIGHT.value

    def restoreState(self, name:str):
        """
        Function
        
        @param 
        """
        pass