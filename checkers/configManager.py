import configparser
import json
from typing import Any

class ConfigManager():
    """
    Class for managing configuration parameters
    """    

    def __init__(self, filePath: str):
        # Reading the configuration file
        self.config = configparser.ConfigParser()
        self.config.read(filePath)
        # Blocks the ability to modify the class (immutability)
        self._is_frozen = True

    def get(self, section: str, option: str, default: Any = None) -> Any:
        # Returns a simple value (str, int, float, bool)
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
        
    def getComplex(self, section: str, option: str, default: Any = None) -> Any:
        # Returns a complex value (e.g. dict, list) deserialized from JSON
        try:
            valueStr = self.config.get(section, option)
            return json.loads(valueStr)
        except (configparser.NoSectionError, configparser.NoOptionError, json.JSONDecodeError):
            return default
        
    def __setAttr__(self, key, value):
        if hasattr(self, '_is_frozen') and self._is_frozen:
            raise AttributeError(f"'{self.__class__.__name__}' is immutable")
        super().__setattr__(key, value)

"""
	with open(fileName,"r") as configFile:
		# use json parser
		configDict: Dict[str, Any] = json.load(configFile)

		#
		# Assignment to variables that store the various parameters
		#

		# "graphics" : graphical interface module
		#	"console" only terminal with keyboard without graphics
		#   "tkinter" with event loop ideal for static widget graphics 2D(GUI)
		#   "pygame" with loop frame ideal for animated graphics 2D
		#   "pyOpenGL" with loop frame, uses OpenGL API for 3D graphics
		#   "webapp" future extensions (Qt)
		configGraphApproach: str = configDict['graphics']
		
		# "mode" : type of execution mode
		#   "play" checkers game between player 1 and player 2
		#   "view" view checkers game from archive
		#   "data" Unsupervised Learning (UL) data extraction
		configExecutionMode: str = configDict['mode']

		# "player1" : type of decision engine for player 1
		#   N.B.: valid only in 'play' mode !
		#   "manual" mouse or keyboard moves
		#   "classic" MiniMax + Alpha-Beta Pruning
		#   "SL" Supervised Learning
		#   "RL" Reinforcement Learning
		configPlayerEngine1: str = configDict['player1']

		# "player2" : type of decision engine for player 2
		#   N.B.: valid only in 'play' mode !
		#   "manual" mouse or keyboard moves
		#   "classic" MiniMax + Alpha-Beta Pruning
		#   "SL" Supervised Learning
		#   "RL" Reinforcement Learning
		configPlayerEngine2: str = configDict['player2']

		# "restore" : restore checkerboards state from archive /restores
		#   N.B.: delete option if normal game start !
		#   "<name_checkerboard> checkerboard state name
		configRestoreName: str = None
		if 'restore' in configDict.keys():		
			configRestoreName = configDict['restore']

		# "history_database" : activation of historical game storage on database
		# 	N.B.: if omitted, storing does not occur !
		#   "<name_database> database name for game to storage
		configHistoryDbName: str = None
		if 'history_database' in configDict.keys():		
			configHistoryDbName = configDict['history_database']

		# "view_database" : database name from which to view the game
		#   N.B.: valid only in 'view' mode !
		#   "<name_database> database name from archive /database
		configViewDbName: str = None
		if 'view_database' in configDict.keys():		
			configViewDbName = configDict['view_database']

		# "view_id" : game identifier to view
		#   N.B.: valid only in 'view' mode !
		#   "<id> game identifier in the chosen database
		configViewId: int = 0
		if 'view_id' in configDict.keys():		
			configViewId = configDict['view_id']

		# N.B.: TODO UL type option (with archive /dataset) !

		#
		# Initialize game engine object
		#
		      
		# Dependency injection through derived class constructor  
		# pygameGraphics: PygameGraphics = PygameGraphics()
		# checkerboard: Checkerboard = Checkerboard(graphics=pygameGraphics)

		# Graphical dependencies with the class factory method
		checkerboard: Checkerboard = Checkerboard(graphics=GraphicsFactory.create_graphics(configGraphApproach))
		checkerboard.executeMode(mode=configExecutionMode, config=configDict)
"""
