import numpy as np

from enum import Enum
from checkers.configManager import ConfigManager
from checkers.constant import DIM_CKECKERBOARD
from checkers.engine.game.cells import Cells
from checkers.graph.graphicsInterface import GraphicsInterface

class Checkerboard(Cells):
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
    # 'man' or 'king' in the cells of the checkerboard
    class EnumCheckerboardCells(Enum):
        C_EMPTY = 0
        C_MAN_LIGHT = 1
        C_KING_LIGHT = 2
        C_MAN_DARK = 3
        C_KING_DARK = 4

    def __init__(self, graphics: GraphicsInterface, config: ConfigManager):
        """
        Constructor.

        @param xxx: .
        """

        # Initialization of Cells base class and reference to external graphical interface
        super().__init__()
        self.graphics = graphics
        self.config = config

        # Initialize an 8x8 checkerboard with zeros
        self.checkerboard = np.zeros((DIM_CKECKERBOARD, DIM_CKECKERBOARD), dtype=int)
        self.playerTurn = self.EnumPlayersColor.P_LIGHT.value

    def executeMode(self):
        """
        Function
        
        @param 
        """
        configExecutionMode: str = self.config.get("Configuration", "mode", default="play")
        configPlayerEngine1: str = self.config.get("Configuration", "player1", default="manual")
        configPlayerEngine2: str = self.config.get("Configuration", "player2", default="manual")
        configViewDbName: str = self.config.get("Configuration", "view_database", default="None")

        # Using lamda to pass parameters without immediately executing the function
        modes = {
            "play": lambda: self.play_mode(configPlayerEngine1, configPlayerEngine2),
            "view": lambda: self.view_mode(configViewDbName),
            "data": lambda: self.data_mode()
        }
        # Get the correct action or a default mode, then perform the action
        action = modes.get(configExecutionMode, self.play_mode)
        action()
            
    def play_mode(self, playerEngine1: str, playerEngine2: str):
        """
        Function
        
        @param 
        """
        self.graphics.render()

    def view_mode(self, viewDbName: str):
        """
        Function
        
        @param 
        """
        pass

    def data_mode(self):
        """
        Function
        
        @param 
        """
        pass

    def restoreState(self, name:str):
        """
        Function
        
        @param 
        """
        pass