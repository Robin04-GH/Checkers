from abc import ABC, abstractmethod
import threading

class GraphicsInterface(ABC):
    """
    Abstract class to allow the game engine to interface with the 
    graphics module without knowing which graphics library was used
    """

    @abstractmethod
    def start(self)->threading.Thread:
        """
        """        
        pass

    @abstractmethod
    def wait_started(self):
        """
        """        
        pass

    @abstractmethod
    def main_graph(self):
        """
        """        
        pass

    @abstractmethod
    def process_events(self):
        """
        Handles input events
        """        
        pass

    @abstractmethod
    def refresh_timers(self):            
        """
        Timers
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
