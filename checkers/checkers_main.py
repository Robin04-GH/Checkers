import sys
from checkers.config_manager import ConfigManager
from checkers.engine.game.checkerboard import Checkerboard
from checkers.graph.graphics_factory import GraphicsFactory

def usage():
	"""
	Print help/usage message.
	"""

	# Specify the configuration file
	# N.B.: Without pyenv use python3 !
	print('python checkers_main.py', '<configuration file>')
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
	file_name: str = args[1]
	config_manager: ConfigManager = ConfigManager(file_name)

	# Graphical dependencies with the class factory method
	checkerboard: Checkerboard = Checkerboard(config = config_manager, graphics = GraphicsFactory.create_graphics(config_manager.graph_approach))	
	checkerboard.execute_mode()
