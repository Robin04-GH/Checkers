import configparser
import json
from typing import Any, Optional

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
        
		# "mode" : type of execution mode
		#   "play" checkers game between player 1 and player 2
		#   "view" view checkers game from archive
		#   "data" Unsupervised Learning (UL) data extraction
        self.execution_mode : str = self.get("Configuration", "mode", default="play")

        # "player1_name" : identification player 1
        #   "<name_player> name player for storage data
        self.player1_name : str = self.get("Configuration", "player1_name", default="name1")

		# "player1_engine" : type of decision engine for player 1
		#   N.B.: valid only in 'play' mode !
		#   "player" mouse or keyboard moves
		#   "classic" MiniMax + Alpha-Beta Pruning
		#   "SL" Supervised Learning
		#   "RL" Reinforcement Learning
        self.player1_engine : str = self.get("Configuration", "player1_engine", default="player")
        
        # "player2_name" : identification player 2
        #   "<name_player> name player for storage data
        self.player2_name : str = self.get("Configuration", "player2_name", default="name2")

		# "player2_engine" : type of decision engine for player 2
		#   N.B.: valid only in 'play' mode !
		#   "player" mouse or keyboard moves
		#   "classic" MiniMax + Alpha-Beta Pruning
		#   "SL" Supervised Learning
		#   "RL" Reinforcement Learning
        self.player2_engine : str = self.get("Configuration", "player2_engine", default="player")
        
        # "parity_move" : massimo numero di mosse senza che venga catturato alcun pezzo e 
        # senza che nessuna pedina si sia mossa (conteggio su entrambi i giocatori)
        self.parity_move : int = int(self.get("Configuration", "parity_move", default=80).strip())

		# "restore" : restore checkerboards state from archive /restores
		#   N.B.: delete option if normal game start !
		#   "<name_checkerboard> checkerboard state name
        self.restore_name : Optional[str] = self.get("Configuration", 'restore', default=None)
        
		# "history_database" : activation of historical game storage on database
		# 	N.B.: if omitted, storing does not occur !
		#   "<name_database> database name for game to storage
        self.history_db_name : Optional[str] = self.get("Configuration", 'history_database', default=None)
        
        # "import_pdn" : PDN name from which to view the game
        #   N.B.: valid only in 'view' mode !
        #   "<name_pdn> PDN name for import/view
        self.import_pdn_name : Optional[str] = self.get("Configuration", "import_pdn", default=None)
        
        # "pk_game" : game identifier to view
        #   N.B.: valid only in 'view' mode !
        #   "<pk_game> game identifier in the chosen database (primary key=datetime)
        #   N.B.: se PDN il time determina il numero della partita con stessa data !
        self.pk_game : Optional[str] = self.get("Configuration", 'pk_game', default=None)
        