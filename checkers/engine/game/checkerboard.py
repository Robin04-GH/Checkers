#import time
from checkers.config_manager import ConfigManager
from checkers.graph.graphics_interface import GraphicsInterface
from checkers.engine.game.state import State
from checkers.engine.game.game_sequence import GameSequence
#from multiprocessing import Process, Manager, Event
import threading

from checkers.engine.game.moves_player import MovesPlayer

class Checkerboard:
    """
    Class for checkerboard management:
    - initialization (reset)
    - restore initial state
    - memorization of pieces (state)
    - functions for reading the position of the pieces     
    """

    def __init__(self, config: ConfigManager, graphics: GraphicsInterface):
        """
        Constructor
        - 

        @param xxx: .
        """

        # Initialization of Cells and Pieces class and reference to external config and graphical interface
        self.config = config
        self.graphics = graphics
        self.state = State()
        self.game_sequence = None

    def execute_mode(self):
        """
        Choosing the method to execute based on the configured mode

        @param mode : type of execution mode
            "play" checkers game between player 1 and player 2
            "view" view checkers game from archive
            "data" Unsupervised Learning (UL) data extraction
        """

        modes = {
            "play": lambda: self.play_mode(self.config.player_engine1, self.config.player_engine2),
            "view": lambda: self.view_mode(self.config.view_db_name, self.config.view_id),
            "data": lambda: self.data_mode()
        }

        return modes.get(self.config.execution_mode, lambda: self.play_mode(self.config.player_engine1, self.config.player_engine2))()
            
    def play_mode(self, player_engine1: str, player_engine2: str):
        """
        Function
        
        @param 
        """

        self.game_sequence = GameSequence(self.config, self.graphics, self.state)
        """
        # Manager for shared data 
        with Manager() as manager:
            terminate_event = Event()
            pieces_proxy = manager.dict()
            # create process moves
            self.process = Process(target=self.task_engine, args=(self.state, pieces_proxy, terminate_event))
            self.process.start()
        """
        # Dictionary condiviso tra i thread
        pieces_proxy = {}

        # Avvio del thread secondario
        terminate_event = threading.Event()
        self.thread = threading.Thread(target=self.task_engine, args=(self.state, pieces_proxy, terminate_event))
        self.thread.start()

        # graphics loop (games, players move)
        self.graphics.main_loop(self.game_sequence.update)

        # When invoke EXIT:
        terminate_event.set()
        #self.process.join()
        self.thread.join()

    def view_mode(self, view_db_name: str, view_id: int):
        """
        Function
        
        @param 
        """
        pass

    def data_mode(self):
        """        
        Function
        
        @param 
        """
        pass

    def task_engine(self, state:State, pieces_proxy:dict[int, int], terminate_event):
        # loop engine
        moves_player : MovesPlayer = MovesPlayer(state)

        while not terminate_event.is_set():
            # Change shared dict 
            # pieces_proxy[] ...

            # ... da evento : definito lo stato, ricavare tutte le possibili mosse del giocatore secondo le regole
            state.restore("restores/state_test01.json")   # <--- solo test !

            moves_player.all_moves_generator()
            b = 0

            # wait
            #time.sleep(0.01)

    """
    Nota :
    - concetto di Player come classe che contiene informazioni (tipo engine) e statistiche sul giocatore visto dal 
    punto di vista esterno (configurazione e grafica). Il colore cambierà ogni partita in quanto viene sorteggiato.
    Dal punto di vista engine, viene perso il concetto di player ma rimane sono il turno di mossa in base al colore,
    mentre il tipo di engine (manuale, database, inferenza) è determinato da un parametro inizializzato nella sequenza
    logica del gioco (game_sequence).
    """