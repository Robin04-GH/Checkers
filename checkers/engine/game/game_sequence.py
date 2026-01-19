import enum
from checkers.config_manager import ConfigManager
from checkers.graph.graphics_interface import GraphicsInterface
from checkers.engine.game.state import State

class GameSequence:
    """
    Class that defines the state sequence of the game logic
    """

    @enum.unique
    class EnumCheckerStates(enum.IntEnum):
        S_IDLE = 0
        S_INITIALIZE = 1
        S_START_MOVES = 2
        S_WAIT_MOVES = 3
        S_MESSAGE_NEW_GAME = 4

    def __init__(self, config: ConfigManager, graphics: GraphicsInterface, state: State):
        self.config = config
        self.graphics = graphics
        self.state = state
        self._step = GameSequence.EnumCheckerStates.S_IDLE

    def update(self):
        """
        Main logic of the game
        """

        steps = {
            GameSequence.EnumCheckerStates.S_IDLE : lambda: self.idle(),
            GameSequence.EnumCheckerStates.S_INITIALIZE : lambda: self.initialize(),
            GameSequence.EnumCheckerStates.S_START_MOVES : lambda: self.start_moves(),
            GameSequence.EnumCheckerStates.S_WAIT_MOVES : lambda: self.wait_moves(),
            GameSequence.EnumCheckerStates.S_MESSAGE_NEW_GAME : lambda: self.message_new_game()
        }

        return steps.get(self._step, lambda: self.idle())()

        # macchina a stati :
        # 1) inizializza play-turn (sorteggio colore) e status
        # 2) avvia processo moves_worker
        # 3) attesa fine processo moves_worker
        # 4) set is_moved, toggle play-turn
        # 5) loop state-machine fino a fine partita
        # 6) messaggio nuova partita per fine loop grafico

        # game initialization
        # self.is_moved : bool = False
        # self.player_turn = self.EnumPlayersColor.P_LIGHT
        # arrange the pieces (reset or restore)
        # ...

        # pieces_proxy.update(self.pieces._reverse_dict)
        # process.start()
        # self.is_moved:

    def idle(self):
        #self.state.reset()
        #self.state.update()
        #self.state.restore(self.config.restore_name)
        #self.state.pieces.update_position(20,16)
        #self.state.pieces.update_position(8,12)
        #self.state.save("restores/state_test01.json")
        #self.state.save("restores/state_test02.json")
        self._step = GameSequence.EnumCheckerStates.S_INITIALIZE
        pass

    def initialize(self):
        self._step = GameSequence.EnumCheckerStates.S_START_MOVES
        pass

    def start_moves(self):
        self._step = GameSequence.EnumCheckerStates.S_WAIT_MOVES
        pass

    def wait_moves(self):
        self._step = GameSequence.EnumCheckerStates.S_MESSAGE_NEW_GAME
        pass

    def message_new_game(self):
        self._step = GameSequence.EnumCheckerStates.S_IDLE
        pass
