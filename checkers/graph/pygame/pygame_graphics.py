# To avoid using quotes ("") in the type hints on the 'PygameGraphics' parameter, 
# just add this directive (Python >=3.10)
from __future__ import annotations
import pygame
import threading
from checkers.constant import TIMER_PRESCALER
from checkers.graph.graphics_interface import GraphicsInterface
from checkers.channels.channel import EnumChannelProtocols, Gateway
from checkers.channels.graph_input import ProtGraphInput
from checkers.channels.graph_output import ProtGraphOutput
from checkers.graph.pygame.pygame_state import PygameState
from checkers.graph.pygame.pygame_events import PygameEventManager
from checkers.graph.pygame.graph_input_receiving import GraphInputReceiving

class PygameGraphics(GraphicsInterface):
    """
    Graphics management class on a separate thread
    """
    
    def __init__(self, gateway:Gateway):
        self.gateway = gateway
        self.sender : ProtGraphOutput = gateway.channels[EnumChannelProtocols.C_PROTGRAPHOUTPUT].sender
        self.started_event : threading.Event = threading.Event()
        self.thread = threading.Thread(target=self.main_graph, args=(self.started_event,))   #, daemon=True ?

    def start(self)->threading.Thread:
        self.thread.start()
        return self.thread

    def wait_started(self):
        self.started_event.wait()

    def main_graph(self, started_event:threading.Event):
        pygame.init()    
        # States
        self.state : PygameState = PygameState()
        self.event_manager : PygameEventManager = PygameEventManager(self.state, self.sender)
        self.time : int = pygame.time.get_ticks()

        # Channel
        self.receiving : ProtGraphInput = GraphInputReceiving(self.state)
        self.gateway.channels[EnumChannelProtocols.C_PROTGRAPHINPUT].register(self.receiving)

        started_event.set()

        self.main_loop()
        pygame.quit()

    def process_events(self):
        """
        Handles input events
        """
        self.event_manager.dispatcher(pygame.event.get())
        # self.event_manager.key_pressed()
        self.event_manager.key_mods()

    def refresh_timers(self):            
        """
        Timers
        """
        now = pygame.time.get_ticks()
        elapsed : int = now - self.time
        if elapsed >= TIMER_PRESCALER:
            self.time = now
            self.event_manager.event_timer(elapsed)

    def refresh_screen(self):
        """
        Renders frames
        """
        self.state.refresh_frame()

    def main_loop(self):
        """
        Main graphic loop.
        Calls a logical update function provided by the derived class.
        """
        while self.event_manager.get_running():
            self.gateway.channels[EnumChannelProtocols.C_PROTGRAPHINPUT].receiver.dispatcher(self.receiving)

            self.process_events()
            self.refresh_timers()
            self.refresh_screen() 
