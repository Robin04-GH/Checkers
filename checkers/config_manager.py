import configparser
import json
from typing import Any, Optional
from enum import Enum

class EnumExecutionMode(Enum):
    PLAY = "play"
    VIEW = "view"
    SCAN = "scan"
    DATA = "data"

class ConfigManager:
    """
    Class for managing configuration parameters
    """    

    def __init__(self, file_path: str):
        # Reading the configuration file
        self.config = configparser.ConfigParser()
        self.config.read(file_path)   
        self.assign_attrib()                
        # Blocks the ability to modify the class (immutability)
        self._is_frozen = True

    def get(self, section: str, option: str, default: Any = None) -> Any:
        # Returns a simple value (str, int, float, bool)
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
        
    def get_complex(self, section: str, option: str, default: Any = None) -> Any:
        # Returns a complex value (e.g. dict, list) deserialized from JSON
        try:
            valueStr = self.config.get(section, option)
            return json.loads(valueStr)
        except (configparser.NoSectionError, configparser.NoOptionError, json.JSONDecodeError):
            return default

    # The __setattr__() method fires only when an attribute that does not yet exist 
    # is created or modified.
    # Adding 'self.__dict__' also allows you to catch attempts to modify attributes 
    # that already exist in the class (control becomes more permissive)                                 
    def __setattr__(self, key, value):
        if hasattr(self, '_is_frozen') and self._is_frozen: # and key in self.__dict__:
            raise AttributeError(f"'{self.__class__.__name__}' is immutable !")
        super().__setattr__(key, value)

    def assign_attrib(self):
		# "graphics" : graphical interface module
		#	"console" only terminal with keyboard without graphics
		#   "tkinter" with event loop ideal for static widget graphics 2D(GUI)
		#   "pygame" with loop frame ideal for animated graphics 2D
		#   "pyOpenGL" with loop frame, uses OpenGL API for 3D graphics
		#   "webapp" future extensions (Qt)
        self.graph_approach : str = self.get("Configuration", "graphics", default="console")
        
        self.graphics_disabled = False        

		# "mode" : type of execution mode
		#   "play" checkers game between player 1 and player 2
		#   "view" view checkers game from archive
        #   "scan" like view mode but without graphics refresh
		#   "data" Unsupervised Learning (UL) data extraction
        mode_str = self.get("Configuration", "mode", default="play")
        try:            
            self.execution_mode : EnumExecutionMode = EnumExecutionMode(mode_str)
            if self.execution_mode == EnumExecutionMode.SCAN:
                self.execution_mode = EnumExecutionMode.VIEW
                self.graphics_disabled = True
            elif self.execution_mode == EnumExecutionMode.DATA:
                self.graphics_disabled = True
        except ValueError:
            raise ValueError(f"Invalid execution mode '{mode_str}' in configuration")

        # "player1_name" : identification player 1
        #   "<name_player> name player for storage data
        self.player1_name : str = self.get("Configuration", "player1_name", default="name1")

		# "player1_engine" : type of decision engine for player 1
		#   Hint: valid only in 'play' mode !
		#   "player" mouse or keyboard moves
		#   "classic" MiniMax + Alpha-Beta Pruning
		#   "SL" Supervised Learning
		#   "RL" Reinforcement Learning
        self.player1_engine : str = self.get("Configuration", "player1_engine", default="player")
        
        # "player2_name" : identification player 2
        #   "<name_player> name player for storage data
        self.player2_name : str = self.get("Configuration", "player2_name", default="name2")

		# "player2_engine" : type of decision engine for player 2
		#   Hint: valid only in 'play' mode !
		#   "player" mouse or keyboard moves
		#   "classic" MiniMax + Alpha-Beta Pruning
		#   "SL" Supervised Learning
		#   "RL" Reinforcement Learning
        self.player2_engine : str = self.get("Configuration", "player2_engine", default="player")
        
        # "parity_move" : Maximum number of moves without capturing any pieces and
        # without moving any mans (counted by both players)
        self.parity_move : int = int(self.get("Configuration", "parity_move", default='80').strip())

		# "restore" : restore checkerboards state from archive /restores
		#   Hint: delete option if normal game start !
		#   "<name_checkerboard> checkerboard state name
        self.restore_name : Optional[str] = self.get("Configuration", 'restore', default=None)

		# "import_name" : resource name for data import (.db/.pdn)
        self.import_name : Optional[str] = self.get("Configuration", 'import_name', default=None)

        # "import_game" : identifier of the first game to import (default = 1)
        #   Hint: it depends on the type of resource (order number for .pdn, order number 
        #   or better pk for .db) !
        self.import_game : Optional[str] = self.get("Configuration", "import_game", default=None)
        if not self.import_game or not self.import_game.isdigit():
            self.import_game = "1"

		# "export_name" : resource name for data export (.db/.pdn)
        self.export_name : Optional[str] = self.get("Configuration", 'export_name', default=None)

        # "timeout_selected" : timeout selected in msec for moves steps in view mode. 
        # Setting it to zero will make the timeout infinite; to continue, a keyboard (space) or 
        # mouse (left-click) event is required
        #   Hint: valid only in 'view' mode !
        timeout_selected : int = int(self.get("Configuration", "timeout_selected", default='2000').strip())
        
        # "timeout_destinated" : timeout destinated in msec for moves steps in view mode. 
        # Setting it to zero will make the timeout infinite; to continue, a keyboard (space) or 
        # mouse (left-click) event is required
        #   Hint: valid only in 'view' mode !
        timeout_destinated : int = int(self.get("Configuration", "timeout_destinated", default='2000').strip())
        
        # "timeout_validated" : timeout validated in msec for moves steps in view mode. 
        # Setting it to zero will make the timeout infinite; to continue, a keyboard (space) or 
        # mouse (left-click) event is required
        #   Hint: valid only in 'view' mode !
        timeout_validated : int = int(self.get("Configuration", "timeout_validated", default='2000').strip())
        
        self.timeouts_view : tuple[int, int, int] = timeout_selected, timeout_destinated, timeout_validated

        # "seed" : use for randomization with testable determinism
        seed = self.get("Configuration", "seed", default=None)
        self.seed : Optional[int] = int(seed) if seed is not None else None
