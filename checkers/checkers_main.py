import sys
import threading
from checkers.config_manager import ConfigManager
from checkers.channels.channel import Gateway
from checkers.engine.game.checkerboard import Checkerboard
from checkers.graph.graphics_factory import GraphicsFactory

def usage():
	"""
	Print help/usage message.
	"""

	# Specify the configuration file
	# Hint: Without pyenv use python3 !
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

	# Comunicazione tra moduli su thread diversi
	gateway: Gateway = Gateway()

	# Graphical dependencies with the class factory method
	if not config_manager.graphics_disabled:
		graphics = GraphicsFactory.create_graphics(config_manager.graph_approach, gateway)
		thread : threading.Thread = graphics.start()
		graphics.wait_started()

	checkerboard: Checkerboard = Checkerboard(config_manager, gateway)
	checkerboard.execute_mode()

	if not config_manager.graphics_disabled:
		thread.join()
