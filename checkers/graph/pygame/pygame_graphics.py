# To avoid using quotes ("") in the type hints on the 'PygameGraphics' parameter, 
# just add this directive (Python >=3.10)
from __future__ import annotations
import pygame
import threading
from checkers.graph.graphics_interface import GraphicsInterface
from checkers.channels.channel import Gateway
from checkers.channels.graph_input import ProtGraphInput
from checkers.channels.graph_output import ProtGraphOutput
from checkers.graph.pygame.pygame_state import PygameState
from checkers.graph.pygame.pygame_events import PygameEventManager
from checkers.graph.pygame.graph_input_receiving import GraphInputReceiving

class PygameGraphics(GraphicsInterface):
    """
    """
    
    def __init__(self, gateway:Gateway):
        self.gateway = gateway
        self.sender : ProtGraphOutput = gateway.graph_output.sender
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
        self.gateway.graph_input.register(self.receiving)
        started_event.set()

        self.main_loop()
        pygame.quit()

    def process_events(self):
        """
        Handles input events
        """
        self.event_manager.dispatcher(pygame.event.get())
        self.event_manager.key_pressed()

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
            self.gateway.graph_input.receiver.dispatcher(self.receiving)
            self.process_events()
            self.refresh_screen() 
            
            # Refresh timer
            _now = pygame.time.get_ticks()
            _elapsed = _now - self.time
            if _elapsed >= 50:
                self.time = _now
                self.state.refresh_timer()


# L'immagine è composta da 2 superfici, scacchiera e pedine entrambe ridisegnabili :
#  1) Ogni cella della scacchiera ha uno stato contrassegnato da un colore : 
#  - normale, selezionabile avanti, selezionabile indietro, selezionata.
#  2) Ogni pedina oltre al colore del player ha anch'essa uno stato che ne altera il colore : 
#  - normale (player), selezionata (bordo), catturata (trasparenza). 
# Inoltre lo stato di pedina o dama viene evidenziato con un secondo cerchio all'interno.
#
# Gli stati effettivi sono mantenuti in memoria pygame con delle liste.
# Lo stato transitorio durante la sequenza della mossa, ripristinabile quando la mossa viene abortita, 
# altera :
#  - offset pedina selezionata (che si aggiunge alla posizione originaria che rimane inalterata fino
#    alla validazione della mossa), stato delle pedine catturate.
#
# La schermata è componibile con la sequente sequenza di comandi : 
#  - 'pedine_surface.fill((0, 0, 0, 0))' per pulire la superficie nel buffer della memoria video
#  - 'pygame.draw.circle(...)' per disegnare lo stato in memoria nel buffer della memoria video
#  - 'schermo.blit(scacchiera_surface, (0, 0))' per scrittura superficie nel buffer della memoria video
#  - 'pygame.display.flip()' per refresh video
#
# Come sentire i tasti ?

