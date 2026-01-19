from checkers.graph.graphics_interface import GraphicsInterface
from checkers.graph.pygame.pygameGraphics import PygameGraphics
from checkers.graph.console.console import Console

class GraphicsFactory:
    """
    Factory class to create the dependency to the graphical module 
    without directly exposing the constructor.
    The instance of the graphics class is returned and not the type of the class.
    If the configured graphics module is not implemented, the console is used.
    """

    @staticmethod
    def create_graphics(graphApproach : str) -> GraphicsInterface:
        if graphApproach == "pygame":
            return PygameGraphics()
        #elif graphApproach == "tkinter":
        #   return TkinterGraphics()
        #elif graphApproach == "pyOpenGL":
        #   return OpenGLGraphics()
        #elif graphApproach == "webapp":
        #   return WebGraphics()
        else :
           return Console()
