import enum
from typing import Optional
from collections.abc import Generator
from checkers.types import DestCellsType
from checkers.channels.graph_input import ProtGraphInput
from checkers.engine.game.moves_player import MovesPlayer
from checkers.engine.game.move import Move

# Classe per definire lo stato della MoveSequence
@enum.unique
class EnumEngineMoving(enum.IntEnum):
    MS_IDLE = 0
    MS_QST_SELECT = 1,
    MS_ASW_SELECT = 2,
    MS_QST_DESTINATION = 3,
    MS_ASW_DESTINATION = 4,
    MS_VALIDATED_MOVE = 5,
    MS_END = 7

class MoveSequence:
    """
    Class that defines the state sequence of the move
    """

    def __init__(self, sender:ProtGraphInput):
        self.sender : ProtGraphInput = sender
        self.moves_player : MovesPlayer = None
        self.move : Move = None
        self._in_moving = False
        self._step = EnumEngineMoving.MS_IDLE

    def run(self, moves_player:MovesPlayer, move:Optional[Move])->Generator[EnumEngineMoving, None, None]:
        
        steps = {
            EnumEngineMoving.MS_IDLE : lambda: self.idle(),
            EnumEngineMoving.MS_QST_SELECT : lambda: self.question_select(),
            # EnumEngineMoving.MS_ASW_SELECT : lambda: self.answer_select(),
            EnumEngineMoving.MS_QST_DESTINATION : lambda: self.question_destination(),
            # EnumEngineMoving.MS_ASW_DESTINATION : lambda: self.answer_destination(),
            # EnumEngineMoving.MS_VALIDATED_MOVE : lambda: self.validated_move(),
            EnumEngineMoving.MS_END : lambda: self.end()
        }

        self.moves_player = moves_player
        self.move = move
        self._in_moving = True
        self._step = EnumEngineMoving.MS_QST_SELECT

        while self._in_moving: 
            steps.get(self._step, lambda: self.idle())()
            yield self._step

    def get_step(self)->EnumEngineMoving:
        return self._step

    def set_step(self, step:EnumEngineMoving):
        self._step = step

    def idle(self):
        pass

    def end(self):
        self._in_moving = False

    # invio msg celle selezionabili
    def question_select(self):
        cells : tuple[int, ...] = self.moves_player.get_all_keys()
        self.sender.selection_cells(cells)
        self._step = EnumEngineMoving.MS_ASW_SELECT

    # attesa risposta cella selezionata
    def answer_select(self, cell:int):
        print(cell)
        self.moves_player.initialize_move(cell)
        self._step = EnumEngineMoving.MS_QST_DESTINATION

    def question_destination(self):
        dest_cells, previous_index = self.moves_player.get_destination_cells()
        self.sender.destination_cells(dest_cells, previous_index)
        self._step = EnumEngineMoving.MS_ASW_DESTINATION

    def answer_destination(self, index:int):
        print(index)
        self.moves_player.upgrade_move(index)
        self._step = EnumEngineMoving.MS_QST_DESTINATION

    def validated_move(self, move:Move):        
        if self.moves_player.finalize_move(move):
            self.sender.promoted_king(move.destinations[-1])
        self._step = EnumEngineMoving.MS_END

    # N.B.: se durante la sequenza viene rilasciato il mouse dopo la selezione, le fasi transitorie 
    # della mossa vengono abortite e si torna alle celle selezionabili originarie