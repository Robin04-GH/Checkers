from typing import Optional
from checkers.config_manager import EnumExecutionMode, ConfigManager
from checkers.channels.channel import EnumChannelProtocols, Channel, Gateway
from checkers.channels.graph_input import ProtGraphInput
from checkers.channels.graph_output import ProtGraphOutput
from checkers.engine.game.graph_output_receiving import GraphOutputReceiving
from checkers.engine.game.state import State
from checkers.engine.game.move_sequence import MoveSequence
from checkers.engine.game.resources import Resources

from checkers.engine.game.moves_player import MovesPlayer
from checkers.engine.game.move import Move

class Checkerboard():
    """
    Class for checkerboard management:
    - execution mode management
    - external resource initialization (database, PDN)
    - board initialization (restore if necessary)
    - game loop with context for move sequence and inference
    """

    def __init__(self, config:ConfigManager, gateway:Gateway):
        """
        Constructor
        - 

        @param xxx: .
        """

        self.config = config
        self.gateway = gateway
        self.sender : ProtGraphInput = gateway.channels[EnumChannelProtocols.C_PROTGRAPHINPUT].sender

        self.state = State()   
        self.resources = Resources(self.config, self.state)    
        self.move_sequence : MoveSequence = MoveSequence(self.sender)

        # Channel
        self.receiving : ProtGraphOutput = GraphOutputReceiving(self.state, self.move_sequence)
        self.graph_output_channel : Channel = self.gateway.channels[EnumChannelProtocols.C_PROTGRAPHOUTPUT]
        self.graph_output_channel.register(self.receiving)

    def execute_mode(self):
        """
        Choosing the method to execute based on the configured mode

        @param mode : type of execution mode
            "play" checkers game between player 1 and player 2
            "view" view checkers game from archive
            "data" Unsupervised Learning (UL) data extraction
        """

        modes = {
            EnumExecutionMode.PLAY: self.play_mode,
            EnumExecutionMode.VIEW: self.play_mode,
            EnumExecutionMode.DATA: self.data_mode,
        }

        return modes.get(self.config.execution_mode, self.play_mode)()
    
    # The "history_datase" is optional and must be enabled to archive game data or
    # retrieve data in 'view' mode.
    # The "restore" option can be applied to "play" and "view" modes. It also works without
    # enabling archives through .json files saved in /restores.
    # Using "view" mode requires the availability of a database for reading
    # games, which can be created by playing a game with "history_datase"
    # enabled, or by importing PDN (Portable Drafts Notation) formats.

    # Relational database with:
    # - Players table (player data: pk='engine: name', general counters)
    # - Games table (general game data: date, players, outcome)
    # - Moves table (game move history)
    # - States table (game board state history)        

    # Possible configurations : 
    # <play/view>   <restore>   <history>
    #       P           -           -
    #       V           -           -       Not possible !    
    #       P           X           -
    #       V           X           -       Not possible !
    #       P           -           X
    #       V           -           X
    #       P           X           X
    #       V           X           X

    # - resources.initialize()
    #   1) if restore is enabled, acquire data in State from /restores, otherwise only the
    #      database/pdn name, then save it in State
    #   2) open database/pdn if present
    #
    # - jump 1 :
    # - resources.assign_player_and_color()
    #   if restore has not been performed:
    #   1) rebuild pk_game from database if 'view' or generated with datetime if 'play'.
    #   2) rebuild pk_players from database if 'view' or from config (randomized) if 'play'.
    #   3) reset state with pk_game and pk_players
    #   Hint: player (engine/name) and pk_game can be changed at the end of each game!        
    #
    # - jump 2 :
    # - calculate possible moves based on the rules
    # - inference (dispatcher) if 'classic' or 'ML', but traceable even if 'view'
    # - move sequence (scheduler), graphics refresh
    # - update status in memory
    # - end-of-game test and save data to database:    
    #    if NO)
    #     - change player turn and jump 2
    #    if YES)
    #     - possible dialog for new player and/or pk_game selection
    #     - recalculate pk_players with color and pk_game with jump 1    
    #
    # - resources.finalize() 
    #   database closure when exiting loops with EXIT

    def play_mode(self):
        self.resources.initialize()
        try:
            self.run_match_loop()
        finally:
            self.resources.finalize()

    def run_match_loop(self):
        while not self.state.exit:          
            self.resources.reset_inference_cache()
            self.resources.assign_player_and_color()
            
            # Game start
            self.sender.reset()
            self.sender_pieces()

            while not self.state.game_over and not self.state.exit:
                self.run_turn()

    def sender_pieces(self):
        for cell_piece in self.state.pieces.iter_players_pieces():
            self.sender.players_pieces(cell_piece)

    def run_turn(self):
        # calculation of possible moves based on the rules
        with MovesPlayer(self.state) as moves_player:     
            all_moves : set[Move] = moves_player.get_all_moves()

            # end-of-game test        
            if self._is_game_over(all_moves):          
                return
            
            move : Optional[Move] = self._compute_move(all_moves)
            self._execute_move(moves_player, move)
            # saving data to database
            self._persist_turn(move)

            self.state.set_next_turn()

    def _is_game_over(self, all_moves:set[Move])->bool:
        return self.state.check_game_over(len(all_moves), self.config.parity_move)

    def _compute_move(self, all_moves:set[Move])->Optional[Move]:
        inference = self.resources.get_inference_source()
        return inference.run(all_moves) if inference else None

    def _execute_move(self, moves_player:MovesPlayer, move:Optional[Move]):
        # sequence move (scheduler), graphics refresh
        gen = self.move_sequence.run(moves_player, move)
        for step in gen:
            if self.state.exit:
                break
            self.graph_output_channel.receiver.dispatcher(self.receiving)

    def _persist_turn(self, move:Move):
        # TODO save to .db
        pass

    def data_mode(self):
        print(f"Data Mode")
