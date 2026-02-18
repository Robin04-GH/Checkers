from checkers.graph.graphics_interface import GraphicsInterface
from checkers.graph.pygame.pygame_graphics import PygameGraphics
from checkers.channels.channel import Gateway
from checkers.graph.console.console import Console

class GraphicsFactory:
    """
    Factory class to create the dependency to the graphical module 
    without directly exposing the constructor.
    The instance of the graphics class is returned and not the type of the class.
    If the configured graphics module is not implemented, the console is used.
    """

    @staticmethod
    def create_graphics(graphApproach:str, gateway:Gateway)->GraphicsInterface:
        
        match graphApproach:
            case "pygame":
                return PygameGraphics(gateway)
            #case "tkinter":
            #    return TkinterGraphics()
            #case "pyOpenGL":
            #    return OpenGLGraphics()
            #case"webapp":
            #    return WebGraphics()
            case _:
                return Console()
