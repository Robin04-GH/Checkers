#import time
import random
from typing import Optional
from checkers.config_manager import ConfigManager
from checkers.channels.channel import Gateway
from checkers.channels.graph_input import ProtGraphInput
from checkers.channels.graph_output import ProtGraphOutput
from checkers.engine.game.graph_output_receiving import GraphOutputReceiving
from checkers.engine.game.state import State
from checkers.engine.game.move_sequence import EnumEngineMoving, MoveSequence
from checkers.data.db_manager import DatabaseManager
from checkers.data.pdn_manager import PdnManager

from checkers.engine.game.moves_player import MovesPlayer
from checkers.engine.inference_factory import InferenceFactory
from checkers.engine.game.move import Move

class Checkerboard():
    """
    Class for checkerboard management:
    - initialization (reset)
    - restore initial state
    - memorization of pieces (state)
    - functions for reading the position of the pieces     
    """

    def __init__(self, config:ConfigManager, gateway:Gateway):
        """
        Constructor
        - 

        @param xxx: .
        """

        # Initialization of Cells and Pieces class and reference to external config and graphical interface
        self.config = config
        self.gateway = gateway
        self.sender : ProtGraphInput = gateway.graph_input.sender

        self.counter_message : int = 0
        self.await_id : int = 0

        self.state = State()       
        self.db_manager : DatabaseManager = None
        self.pdn_manager : PdnManager = None
        self.move_sequence : MoveSequence = MoveSequence(self.sender)

        # Channel
        self.receiving : ProtGraphOutput = GraphOutputReceiving(self.state, self.move_sequence)
        self.gateway.graph_output.register(self.receiving)

        self.restore : Optional[str] = self.config.restore_name
        self.player_light : str = self.state.build_pk_player(self.config.player1_engine, self.config.player1_name)
        self.player_dark  : str = self.state.build_pk_player(self.config.player2_engine, self.config.player2_name)
        self.pk_game : Optional[str] = self.config.pk_game

    def execute_mode(self):
        """
        Choosing the method to execute based on the configured mode

        @param mode : type of execution mode
            "play" checkers game between player 1 and player 2
            "view" view checkers game from archive
            "data" Unsupervised Learning (UL) data extraction
        """

        modes = {
            "play": self.play_mode,
            "view": self.play_mode,
            "data": self.data_mode,
        }

        return modes.get(self.config.execution_mode, self.play_mode)()

    """
    def execute_mode(self):

        modes = {
            "play": lambda: self.play_mode(),
            "view": lambda: self.play_mode(),
            "data": lambda: self.data_mode()
        }

        return modes.get(self.config.execution_mode, lambda: self.play_mode())()
    """     
      
    def initialize_resource(self):
        # N.B.: diverso da stringa vuota solo in 'play' con history attiva o in 'view' !
        _database : str = ""
        _pdn : str = ""

        # Se restore attivato, la ripartenza avviene acquisendo i dati salvati in /restores,
        # che sovrascrivono in parte quelli del file di configurazione
        if self.restore != None:
            self.state.restore(self.restore)
        else:                
            # Acquisizione nome database all'avvio senza restore
            if self.config.execution_mode != "play" and self.config.execution_mode != "view":
                raise ValueError(f"Mode error !")
            if (
                self.config.execution_mode == "view" and 
                self.config.history_db_name != None and
                len(self.config.history_db_name) == 0 and 
                self.config.import_pdn_name != None and
                len(self.config.import_pdn_name) == 0
            ):
                raise ValueError(f"Mode 'view' without resource : 'history_database'/'import_pdn' !")

            if self.config.history_db_name != None and len(self.config.history_db_name):
                _database = self.config.history_db_name
            if self.config.import_pdn_name != None and len(self.config.import_pdn_name):
                _pdn = self.config.import_pdn_name
            # La variabile col nome del database/pdn è mantenuto salvata in State
            self.state.database = _database
            self.state.pdn = _pdn
                
        # Apertura eventuale database all'avvio.
        if len(self.state.database) > 0:
            self.db_manager = DatabaseManager(self.config) 
            if self.db_manager.open_data(self.state.database):
                raise ValueError(f"Open {self.state.database} error !")
        # Apertura eventuale pdn all'avvio.
        if len(self.state.pdn) > 0:
            self.pdn_manager = PdnManager(self.config) 
            if self.pdn_manager.open_data(self.state.pdn):
                raise ValueError(f"Open {self.state.pdn} error !")
            
    def finalize_resource(self):
        # Chiusura database
        if len(self.state.database) > 0:
            self.db_manager.close_data()
        # Chiusura pdn
        if len(self.state.pdn) > 0:
            self.pdn_manager.close_data()

    # N.B.: metodo gestito ogni nuova partita nel loop checkerboard.
    # Possono essere cambiate solo player1/2_engine/name e pk_game. 
    def assign_player_and_color(self):
        if self.restore == None:
            if self.config.execution_mode == "view":
                _pk_players : tuple[str,str] = self.db_manager.get_players(self.pk_game)
            elif self.config.execution_mode == "play":
                self.pk_game = self.state.generate_pk_game()
                # Attribuzione del colore ai players in modo random
                _pk_players : tuple[str,str] = (self.player_light, self.player_dark)
                # random.sample restituisce una nuova sequenza con gli elementi mescolati.
                _pk_players = tuple(random.sample(_pk_players, k=2))
            else:
                raise ValueError(f"Mode error")        
            self.state.reset(self.pk_game, _pk_players)
        else:
            self.restore = None
        
    def play_mode(self):
        """
        Function
        
        @param 
        """        

        # L' "history_datase" è opzionale, da attivare per archiviare i dati delle partite o
        # per prelevare dati in modalità 'view'.
        # Il "restore" può essere applicato alle modalità "play" e "view". Funziona anche senza
        # attivazione degli archivi attraverso file .json salvati in /restores.
        # L'uso della modalità "view" implica la disponibilità di un database per la lettura
        # delle partite, che può essere stato creato avendo giocato una partita con "history_datase"
        # attivo, oppure attraverso l'import di formati PDN (Portable Draughts Notation).

        # Database relazionale con :
        # - Tabella Players (dati giocatori : pk='engine: name', contatori generali)
        # - Tabella Games (dati generali partite : data, giocatori, esito)
        # - Tabella Moves (storico mosse partite)
        # - Tabella States (storico stato scacchiera partite)

        # Configurazioni possibili : 
        # <play/view>   <restore>   <history>
        #       P           -           -
        #       V           -           -       Non possibile !    
        #       P           X           -
        #       V           X           -       Non possibile !
        #       P           -           X
        #       V           -           X
        #       P           X           X
        #       V           X           X

        # - initialize_resource() 
        #   1) Se restore attivato acquisizione dati in State da /restores, altrimenti del solo 
        #      nome database/pdn poi salvato in State
        #   2) Apertura database/pdn se presente
        #
        # - jump 1 :
        # - assign_player_and_color()
        #   Se non è stato eseguito restore :
        #   1) Ricostruzione pk_game da database se 'view' o generato con datetime se 'play'.
        #   2) Ricostruzione pk_players da database se 'view' o da config (randomizzato) se 'play'.
        #   3) Reset State con pk_game e pk_players
        #   N.B.: player (engine/name) e pk_game possono essere cambiati ad ogni fine partita !
        #
        # - jump 2 :
        # - calcolo delle possibili mosse in base alle regole
        # - inferenza (dispatcher) se 'classic' o 'ML', ma riconducibile anche se 'view'
        # - sequenza mossa (scheduler), refresh grafica
        # - aggiornamento stato in memoria
        # - test fine partita e salvataggio dati su database :
        #    se NO)
        #     - cambio turno player e jump 2
        #    se SI)
        #     - eventuale dialog per nuova scelta player e/o pk_game 
        #     - ricalcolo pk_players con color e pk_game con jump 1
        #
        # - finalize_resource() 
        #   chiusura database all'uscita dei loop con EXIT
    
        self.initialize_resource()

        while not self.state.exit:          
            self.assign_player_and_color()
            
            # Avvio partita
            self.sender.reset()
            self.sender_pieces()

            # inferenza (dispatcher) se 'classic' o 'ML', ma riconducibile anche se 'view'
            _inference = InferenceFactory.create_inference(
                self.config, 
                self.state.get_engine(), 
                self.db_manager, 
                self.pdn_manager
            )

            while not self.state.game_over and not self.state.exit:          
                # calcolo delle possibili mosse in base alle regole
                with MovesPlayer(self.state) as moves_player:     
                    _move : Optional[Move] = None 
                    _all_moves : set[Move] = moves_player.get_all_moves()

                    # test fine partita :                    
                    if not self.state.check_game_over(len(_all_moves), self.config.parity_move):
                        if _inference != None:
                            _move = _inference.run(_all_moves)

                        # sequenza mossa (scheduler), refresh grafica
                        _gen = self.move_sequence.run(moves_player,_move)
                        for _step in _gen:
                            if _step == EnumEngineMoving.MS_END or self.state.exit:
                                break
                            self.gateway.graph_output.receiver.dispatcher(self.receiving)

                        # salvataggio dati su database
                        # TODO

        self.finalize_resource()

    def sender_pieces(self):
        for cell_piece in self.state.pieces.iter_players_pieces():
            self.sender.players_pieces(cell_piece)

    def data_mode(self):
        print(f"Data Mode")

    """
    def process_senders(self):          
        if self.await_id == 0 or self.sender.await_sended(self.await_id):
            self.counter_message += 1
            msg = Message(EnumIdGraph.GRH_STRING, tuple(f"Message Checker {self.counter_message}"))
            self.await_id = self.sender.send_message_awaitable(msg, self)

    def process_receivers(self):
        msg = self.receiver.receive_message(self)
        if msg != None:
            print(f"Checker received {msg.id} : {msg.data[0]}")
            if msg.data[0] == "QUIT":
                self.running = False
    """    
