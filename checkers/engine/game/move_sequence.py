import enum
from typing import Optional
from collections.abc import Generator
from checkers.channels.graph_input import ProtGraphInput
from checkers.engine.game.moves_player import MovesPlayer
from checkers.engine.game.move import Move

# Class to define the state of the MoveSequence
@enum.unique
class EnumEngineMoving(enum.IntEnum):
    MS_IDLE = 0
    MS_QST_SELECT = 1
    MS_ASW_SELECT = 2
    MS_QST_DESTINATION = 3
    MS_ASW_DESTINATION = 4
    MS_VALIDING_MOVE = 5
    MS_QST_GAME_OVER = 6
    MS_ASW_GAME_OVER = 7
    MS_END = 8

class MoveSequence:
    """
    Class that defines the state sequence of the move
    """

    def __init__(self, sender:ProtGraphInput):
        self.sender : ProtGraphInput = sender
        self.moves_player : MovesPlayer = None
        self.move : Move = None
        self._in_moving : bool = False
        self._index_destination : int = -1
        self._max_destination : int = 0
        self._step = EnumEngineMoving.MS_IDLE

    def run(
            self, 
            moves_player:MovesPlayer, 
            move:Optional[Move], 
            game_over:bool
        )->Generator[EnumEngineMoving, None, None]:
        
        steps = {
            EnumEngineMoving.MS_IDLE : self.idle,
            EnumEngineMoving.MS_QST_SELECT : self.question_select,
            # EnumEngineMoving.MS_ASW_SELECT : self.answer_select,
            EnumEngineMoving.MS_QST_DESTINATION : self.question_destination,
            # EnumEngineMoving.MS_ASW_DESTINATION : self.answer_destination,
            # EnumEngineMoving.MS_VALIDING_MOVE : self.validated_move,
            EnumEngineMoving.MS_QST_GAME_OVER : self.question_game_over,
            # EnumEngineMoving.MS_ASW_GAME_OVER : self.answer_game_over,
            EnumEngineMoving.MS_END : self.end
        }

        self.moves_player = moves_player
        self.move = move
        self._in_moving = True
        self._index_destination = -1
        self._max_destination = len(move.destinations) if move else 0
        self._step = EnumEngineMoving.MS_QST_SELECT if not game_over else EnumEngineMoving.MS_QST_GAME_OVER

        while self._in_moving: 
            handler = steps.get(self._step, self.idle)
            handler()
            yield self._step

        return

    def get_step(self)->EnumEngineMoving:
        return self._step

    def set_step(self, step:EnumEngineMoving):
        self._step = step

    def idle(self):
        pass

    def end(self):
        self._in_moving = False

    # send message to selectable cells
    def question_select(self):
        cells : tuple[int, ...] = self.moves_player.get_all_keys()
        selected_cell : int | None = self.move.origin if self.move else None
        self.sender.selection_cells(cells, selected_cell)
        self._step = EnumEngineMoving.MS_ASW_SELECT

    # waiting for selected cell response
    def answer_select(self, cell:int):
        # print(cell)
        self.moves_player.initialize_move(cell)
        self._step = EnumEngineMoving.MS_QST_DESTINATION

    def question_destination(self):
        dest_cells, previous_index = self.moves_player.get_destination_cells()

        if self.move is None:
            destinated_index = None
        else:
            self._index_destination += 1
            if self._index_destination < self._max_destination:
                try:
                    cell = self.move.destinations[self._index_destination]
                    destinated_index = dest_cells.index(cell)                
                except ValueError:
                    raise ValueError(f"Class MoveSequence, question_destination() : destination cell index error !")
            else:
                destinated_index = -1

        self.sender.destination_cells(dest_cells, previous_index, destinated_index)
        self._step = EnumEngineMoving.MS_ASW_DESTINATION

    def answer_destination(self, index:int):
        # print(index)
        self.moves_player.upgrade_move(index)
        self._step = EnumEngineMoving.MS_QST_DESTINATION

    def validated_move(self, move:Move):        
        if self.moves_player.finalize_move(move):
            self.sender.promoted_king(move.destinations[-1])
        self._step = EnumEngineMoving.MS_END

    def question_game_over(self):
        self.sender.game_over()
        self._step = EnumEngineMoving.MS_ASW_GAME_OVER

    def answer_game_over(self):
        self._step = EnumEngineMoving.MS_END
