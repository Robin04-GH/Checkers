from abc import ABC, abstractmethod

class GraphicsInterface(ABC):
    """
    Abstract class to allow the game engine to interface with the 
    graphics module without knowing which graphics library was used
    """

    @abstractmethod
    def process_events(self):
        """
        Handles input events
        """        
        pass

    @abstractmethod
    def refresh_screen(self):
        """
        Renders frames
        """
        pass

    @abstractmethod
    def main_loop(self, update_logic):
        """
        Main graphic loop.
        """
        pass

    @abstractmethod
    def message_new_game(self) -> bool:
        """
        Modal message new game.
        """
        pass
