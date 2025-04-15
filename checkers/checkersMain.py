import sys
from checkers.configManager import ConfigManager
from checkers.engine.game.checkerboard import Checkerboard
from checkers.graph.graphicsFactory import GraphicsFactory

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
	config: ConfigManager = ConfigManager(fileName)

	# Graphical dependencies with the class factory method
	configGraphApproach: str = config.get("Configuration", "graphics", default="console")
	checkerboard: Checkerboard = Checkerboard(graphics=GraphicsFactory.create_graphics(configGraphApproach), config=config)	
	checkerboard.executeMode()
