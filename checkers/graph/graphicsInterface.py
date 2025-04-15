from abc import ABC, abstractmethod

class GraphicsInterface(ABC):
    """
    Abstract class to allow the game engine to interface with the 
    graphics module without knowing which graphics library was used
    """

    @abstractmethod
    def render(self):
        """
        Function
        
        @param 
        """
        
        pass

    @abstractmethod
    def draw_board(self, board_state):
        """
        Function
        
        @param 
        """
        
        pass

