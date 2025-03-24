import sys
import json

from engine.game.checkerboard import Checkerboard

def usage():
	"""
	Print help/usage message.
	"""

	# Specify the configuration file
	# N.B.: Without pyenv use python3 !
	print('python checkers.py', '<configuration file>')
	sys.exit(1)


#
# Main function, when the python script is executed, we execute this.
#
if __name__ == '__main__':
	# Fetch the command line arguments
	args = sys.argv

	if len(args) != 2:
		print('Incorrect number of arguments.')
		usage()

	# open configuration file		
	fileName: str = args[1]
	with open(fileName,"r") as configFile:
		# use json parser
		configDict = json.load(configFile)

		#
		# Assignment to variables that store the various parameters
		#

		# "graphics" : graphical interface module
		#   "pygame" with loop frame ideal for animated graphics 2D
		#   "tkinter" with event loop ideal for static widget graphics 2D(GUI)
		#   "pyOpenGL" with loop frame, uses OpenGL API for 3D graphics
		#   "webapp" future extensions
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
		configRestoreName: str = configDict['restore']

		# "history_database" : activation of historical game storage on database
		# 	N.B.: if omitted, storing does not occur !
		#   "<name_database> database name for game to storage
		configHistoryDbName: str = configDict['history_database']

		# "view_database" : database name from which to view the game
		#   N.B.: valid only in 'view' mode !
		#   "<name_database> database name from archive /database
		configViewDbName: str = configDict['view_database']

		# "view_id" : game identifier to view
		#   N.B.: valid only in 'view' mode !
		#   "<id> game identifier in the chosen database
		configViewId: int = configDict['view_id']

		# N.B.: TODO UL type option (with archive /dataset) !

		#
		# Initialize game engine object
		#        
		checkerboard: Checkerboard = Checkerboard()